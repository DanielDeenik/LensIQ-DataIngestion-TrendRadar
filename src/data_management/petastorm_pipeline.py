"""
ML-Optimized ESG Data Pipeline with Petastorm for LensIQ

This module provides a production-grade, ML-optimized data pipeline for ESG intelligence
using Petastorm and PyArrow. Designed for enterprise scale with comprehensive validation,
multi-source ingestion, and ML-ready dataset generation.
"""

import os
import logging
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple, Iterator
from dataclasses import dataclass, field
from pathlib import Path
import json
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import hashlib

# Petastorm imports with fallback
try:
    from petastorm import make_reader, make_batch_reader
    from petastorm.codecs import ScalarCodec, CompressedImageCodec
    from petastorm.etl.dataset_metadata import materialize_dataset
    from petastorm.unischema import Unischema, UnischemaField, dict_to_spark_row
    from petastorm.predicates import in_lambda
    from pyspark.sql import SparkSession
    from pyspark.sql.types import *
    PETASTORM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Petastorm not available: {e}. Using fallback mode.")
    PETASTORM_AVAILABLE = False

from ..config.production_config import get_config
from ..validation.production_validator import get_validator, validate_esg_data
from .premium_data_connectors import get_premium_data_connector

logger = logging.getLogger(__name__)


@dataclass
class ESGDataPoint:
    """Structured ESG data point for ML processing."""
    company_id: str
    timestamp: datetime
    data_source: str
    environmental_score: float
    social_score: float
    governance_score: float
    combined_score: float
    carbon_intensity: Optional[float] = None
    water_intensity: Optional[float] = None
    waste_intensity: Optional[float] = None
    energy_efficiency: Optional[float] = None
    employee_satisfaction: Optional[float] = None
    board_diversity: Optional[float] = None
    revenue: Optional[float] = None
    market_cap: Optional[float] = None
    sector: Optional[str] = None
    region: Optional[str] = None
    data_quality_score: float = 1.0
    confidence_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'company_id': self.company_id,
            'timestamp': self.timestamp.isoformat(),
            'data_source': self.data_source,
            'environmental_score': self.environmental_score,
            'social_score': self.social_score,
            'governance_score': self.governance_score,
            'combined_score': self.combined_score,
            'carbon_intensity': self.carbon_intensity,
            'water_intensity': self.water_intensity,
            'waste_intensity': self.waste_intensity,
            'energy_efficiency': self.energy_efficiency,
            'employee_satisfaction': self.employee_satisfaction,
            'board_diversity': self.board_diversity,
            'revenue': self.revenue,
            'market_cap': self.market_cap,
            'sector': self.sector,
            'region': self.region,
            'data_quality_score': self.data_quality_score,
            'confidence_score': self.confidence_score
        }


# Petastorm Unischema for ESG data
if PETASTORM_AVAILABLE:
    ESGUnischema = Unischema('ESGSchema', [
        UnischemaField('company_id', np.str_, (), ScalarCodec(StringType()), False),
        UnischemaField('timestamp', np.datetime64, (), ScalarCodec(TimestampType()), False),
        UnischemaField('data_source', np.str_, (), ScalarCodec(StringType()), False),
        UnischemaField('environmental_score', np.float32, (), ScalarCodec(FloatType()), False),
        UnischemaField('social_score', np.float32, (), ScalarCodec(FloatType()), False),
        UnischemaField('governance_score', np.float32, (), ScalarCodec(FloatType()), False),
        UnischemaField('combined_score', np.float32, (), ScalarCodec(FloatType()), False),
        UnischemaField('carbon_intensity', np.float32, (), ScalarCodec(FloatType()), True),
        UnischemaField('water_intensity', np.float32, (), ScalarCodec(FloatType()), True),
        UnischemaField('waste_intensity', np.float32, (), ScalarCodec(FloatType()), True),
        UnischemaField('energy_efficiency', np.float32, (), ScalarCodec(FloatType()), True),
        UnischemaField('employee_satisfaction', np.float32, (), ScalarCodec(FloatType()), True),
        UnischemaField('board_diversity', np.float32, (), ScalarCodec(FloatType()), True),
        UnischemaField('revenue', np.float64, (), ScalarCodec(DoubleType()), True),
        UnischemaField('market_cap', np.float64, (), ScalarCodec(DoubleType()), True),
        UnischemaField('sector', np.str_, (), ScalarCodec(StringType()), True),
        UnischemaField('region', np.str_, (), ScalarCodec(StringType()), True),
        UnischemaField('data_quality_score', np.float32, (), ScalarCodec(FloatType()), False),
        UnischemaField('confidence_score', np.float32, (), ScalarCodec(FloatType()), False),
    ])
else:
    ESGUnischema = None


class DataIngestionAdapter:
    """Abstract base class for data source adapters."""
    
    def __init__(self, source_name: str, config: Dict[str, Any]):
        """Initialize data ingestion adapter."""
        self.source_name = source_name
        self.config = config
        self.rate_limiter = self._create_rate_limiter()
        
    def _create_rate_limiter(self):
        """Create rate limiter for this data source."""
        # Simple token bucket rate limiter
        return {
            'tokens': self.config.get('rate_limit', 100),
            'max_tokens': self.config.get('rate_limit', 100),
            'last_refill': time.time(),
            'refill_rate': self.config.get('rate_limit', 100) / 60.0  # per second
        }
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits."""
        now = time.time()
        time_passed = now - self.rate_limiter['last_refill']
        
        # Refill tokens
        tokens_to_add = time_passed * self.rate_limiter['refill_rate']
        self.rate_limiter['tokens'] = min(
            self.rate_limiter['max_tokens'],
            self.rate_limiter['tokens'] + tokens_to_add
        )
        self.rate_limiter['last_refill'] = now
        
        # Check if we have tokens
        if self.rate_limiter['tokens'] >= 1:
            self.rate_limiter['tokens'] -= 1
            return True
        return False
    
    async def ingest_data(self, company_ids: List[str], 
                         start_date: datetime, 
                         end_date: datetime) -> List[ESGDataPoint]:
        """Ingest data from source. To be implemented by subclasses."""
        raise NotImplementedError
    
    def validate_data(self, data: List[ESGDataPoint]) -> List[ESGDataPoint]:
        """Validate ingested data."""
        validator = get_validator()
        validated_data = []
        
        for data_point in data:
            # Convert to dict for validation
            data_dict = data_point.to_dict()
            
            # Validate data quality
            quality_report = validate_esg_data(data_dict, self.source_name)
            
            # Update quality scores
            data_point.data_quality_score = quality_report.overall_score
            
            # Only include data that meets quality threshold
            if quality_report.overall_score >= 0.7:  # 70% quality threshold
                validated_data.append(data_point)
            else:
                logger.warning(
                    f"Data point for {data_point.company_id} failed quality check: "
                    f"{quality_report.overall_score:.2f}"
                )
        
        return validated_data


class RefinitivAdapter(DataIngestionAdapter):
    """Refinitiv data source adapter."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Refinitiv adapter."""
        super().__init__("refinitiv", config)
        self.connector = get_premium_data_connector("refinitiv")
    
    async def ingest_data(self, company_ids: List[str], 
                         start_date: datetime, 
                         end_date: datetime) -> List[ESGDataPoint]:
        """Ingest ESG data from Refinitiv."""
        data_points = []
        
        for company_id in company_ids:
            if not self._check_rate_limit():
                await asyncio.sleep(1)  # Wait if rate limited
                continue
            
            try:
                # Get ESG data from Refinitiv
                esg_data = self.connector.get_esg_data(company_id)
                
                # Convert to ESGDataPoint
                data_point = ESGDataPoint(
                    company_id=company_id,
                    timestamp=datetime.now(),
                    data_source="refinitiv",
                    environmental_score=esg_data['esg_scores']['environmental'],
                    social_score=esg_data['esg_scores']['social'],
                    governance_score=esg_data['esg_scores']['governance'],
                    combined_score=esg_data['esg_scores']['combined'],
                    carbon_intensity=esg_data['metrics'].get('carbon_intensity'),
                    water_intensity=esg_data['metrics'].get('water_intensity'),
                    waste_intensity=esg_data['metrics'].get('waste_intensity'),
                    energy_efficiency=esg_data['metrics'].get('energy_efficiency'),
                    employee_satisfaction=esg_data['metrics'].get('employee_satisfaction'),
                    board_diversity=esg_data['metrics'].get('board_diversity'),
                    confidence_score=esg_data['data_quality'].get('confidence_score', 100) / 100.0
                )
                
                data_points.append(data_point)
                
            except Exception as e:
                logger.error(f"Error ingesting data for {company_id} from Refinitiv: {e}")
                continue
        
        return self.validate_data(data_points)


class BloombergAdapter(DataIngestionAdapter):
    """Bloomberg data source adapter."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Bloomberg adapter."""
        super().__init__("bloomberg", config)
        self.connector = get_premium_data_connector("bloomberg")
    
    async def ingest_data(self, company_ids: List[str], 
                         start_date: datetime, 
                         end_date: datetime) -> List[ESGDataPoint]:
        """Ingest ESG data from Bloomberg."""
        data_points = []
        
        for company_id in company_ids:
            if not self._check_rate_limit():
                await asyncio.sleep(1)
                continue
            
            try:
                esg_data = self.connector.get_esg_data(company_id)
                
                data_point = ESGDataPoint(
                    company_id=company_id,
                    timestamp=datetime.now(),
                    data_source="bloomberg",
                    environmental_score=esg_data['esg_scores']['environmental'],
                    social_score=esg_data['esg_scores']['social'],
                    governance_score=esg_data['esg_scores']['governance'],
                    combined_score=esg_data['esg_scores']['combined'],
                    carbon_intensity=esg_data['metrics'].get('carbon_intensity'),
                    water_intensity=esg_data['metrics'].get('water_intensity'),
                    waste_intensity=esg_data['metrics'].get('waste_intensity'),
                    energy_efficiency=esg_data['metrics'].get('energy_efficiency'),
                    employee_satisfaction=esg_data['metrics'].get('employee_satisfaction'),
                    board_diversity=esg_data['metrics'].get('board_diversity'),
                    confidence_score=esg_data['data_quality'].get('confidence_score', 100) / 100.0
                )
                
                data_points.append(data_point)
                
            except Exception as e:
                logger.error(f"Error ingesting data for {company_id} from Bloomberg: {e}")
                continue
        
        return self.validate_data(data_points)


class PetastormMLPipeline:
    """ML-optimized ESG data pipeline using Petastorm."""
    
    def __init__(self):
        """Initialize Petastorm ML pipeline."""
        self.config = get_config()
        self.storage_path = Path(self.config.storage.data_path) / "petastorm"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize data source adapters
        self.adapters = self._initialize_adapters()
        
        # Initialize Spark session if Petastorm is available
        self.spark = None
        if PETASTORM_AVAILABLE:
            self.spark = self._initialize_spark()
        
        logger.info(f"Petastorm pipeline initialized. Storage: {self.storage_path}")
    
    def _initialize_adapters(self) -> Dict[str, DataIngestionAdapter]:
        """Initialize data source adapters."""
        adapters = {}
        
        # Refinitiv adapter
        refinitiv_config = self.config.get_data_source("refinitiv")
        if refinitiv_config and refinitiv_config.enabled:
            adapters["refinitiv"] = RefinitivAdapter(refinitiv_config.__dict__)
        
        # Bloomberg adapter
        bloomberg_config = self.config.get_data_source("bloomberg")
        if bloomberg_config and bloomberg_config.enabled:
            adapters["bloomberg"] = BloombergAdapter(bloomberg_config.__dict__)
        
        logger.info(f"Initialized {len(adapters)} data source adapters")
        return adapters
    
    def _initialize_spark(self):
        """Initialize Spark session for Petastorm."""
        try:
            spark = SparkSession.builder \
                .appName("LensIQ-ESG-Pipeline") \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                .getOrCreate()
            
            logger.info("Spark session initialized for Petastorm")
            return spark
        except Exception as e:
            logger.error(f"Failed to initialize Spark session: {e}")
            return None
    
    async def ingest_multi_source_data(self, 
                                     company_ids: List[str],
                                     start_date: datetime,
                                     end_date: datetime,
                                     sources: Optional[List[str]] = None) -> List[ESGDataPoint]:
        """Ingest data from multiple sources concurrently."""
        if sources is None:
            sources = list(self.adapters.keys())
        
        all_data = []
        
        # Create tasks for concurrent ingestion
        tasks = []
        for source_name in sources:
            if source_name in self.adapters:
                adapter = self.adapters[source_name]
                task = adapter.ingest_data(company_ids, start_date, end_date)
                tasks.append((source_name, task))
        
        # Execute tasks concurrently
        for source_name, task in tasks:
            try:
                source_data = await task
                all_data.extend(source_data)
                logger.info(f"Ingested {len(source_data)} data points from {source_name}")
            except Exception as e:
                logger.error(f"Failed to ingest data from {source_name}: {e}")
        
        # Deduplicate data (prefer higher quality scores)
        deduplicated_data = self._deduplicate_data(all_data)
        
        logger.info(f"Total ingested data points: {len(deduplicated_data)}")
        return deduplicated_data
    
    def _deduplicate_data(self, data: List[ESGDataPoint]) -> List[ESGDataPoint]:
        """Deduplicate data points, keeping highest quality."""
        # Group by company_id and timestamp (rounded to day)
        grouped_data = {}
        
        for data_point in data:
            key = (data_point.company_id, data_point.timestamp.date())
            
            if key not in grouped_data:
                grouped_data[key] = data_point
            else:
                # Keep data point with higher quality score
                if data_point.data_quality_score > grouped_data[key].data_quality_score:
                    grouped_data[key] = data_point
        
        return list(grouped_data.values())
    
    def create_petastorm_dataset(self, 
                                data: List[ESGDataPoint],
                                dataset_name: str,
                                partition_cols: Optional[List[str]] = None) -> str:
        """Create Petastorm dataset from ESG data."""
        if not PETASTORM_AVAILABLE or not self.spark:
            return self._create_parquet_fallback(data, dataset_name, partition_cols)
        
        try:
            # Convert data to DataFrame
            df_data = [data_point.to_dict() for data_point in data]
            df = pd.DataFrame(df_data)
            
            # Convert to Spark DataFrame
            spark_df = self.spark.createDataFrame(df)
            
            # Create dataset path
            dataset_path = self.storage_path / dataset_name
            dataset_path.mkdir(parents=True, exist_ok=True)
            
            # Write Petastorm dataset
            with materialize_dataset(self.spark, str(dataset_path), ESGUnischema):
                # Convert DataFrame to Petastorm format
                petastorm_df = spark_df.select(*[field.name for field in ESGUnischema.fields])
                
                # Write partitioned data
                if partition_cols:
                    petastorm_df.write.partitionBy(*partition_cols).parquet(str(dataset_path))
                else:
                    petastorm_df.write.parquet(str(dataset_path))
            
            logger.info(f"Created Petastorm dataset: {dataset_path}")
            return str(dataset_path)
            
        except Exception as e:
            logger.error(f"Failed to create Petastorm dataset: {e}")
            return self._create_parquet_fallback(data, dataset_name, partition_cols)
    
    def _create_parquet_fallback(self, 
                                data: List[ESGDataPoint],
                                dataset_name: str,
                                partition_cols: Optional[List[str]] = None) -> str:
        """Create Parquet dataset as fallback when Petastorm is unavailable."""
        logger.info("Using Parquet fallback for dataset creation")
        
        # Convert data to DataFrame
        df_data = [data_point.to_dict() for data_point in data]
        df = pd.DataFrame(df_data)
        
        # Create dataset path
        dataset_path = self.storage_path / f"{dataset_name}_parquet"
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create PyArrow table
        table = pa.Table.from_pandas(df)
        
        # Write partitioned Parquet
        if partition_cols:
            pq.write_to_dataset(
                table,
                root_path=str(dataset_path),
                partition_cols=partition_cols,
                compression='snappy'
            )
        else:
            pq.write_table(table, str(dataset_path / "data.parquet"), compression='snappy')
        
        logger.info(f"Created Parquet dataset: {dataset_path}")
        return str(dataset_path)
    
    def create_ml_reader(self, 
                        dataset_path: str,
                        batch_size: int = 32,
                        shuffle: bool = True,
                        num_epochs: int = 1) -> Iterator:
        """Create ML-ready data reader."""
        if not PETASTORM_AVAILABLE:
            return self._create_parquet_reader(dataset_path, batch_size, shuffle, num_epochs)
        
        try:
            # Create Petastorm reader
            reader = make_batch_reader(
                f"file://{dataset_path}",
                schema_fields=ESGUnischema.fields,
                shuffle_row_groups=shuffle,
                num_epochs=num_epochs
            )
            
            logger.info(f"Created Petastorm reader for {dataset_path}")
            return reader
            
        except Exception as e:
            logger.error(f"Failed to create Petastorm reader: {e}")
            return self._create_parquet_reader(dataset_path, batch_size, shuffle, num_epochs)
    
    def _create_parquet_reader(self, 
                              dataset_path: str,
                              batch_size: int,
                              shuffle: bool,
                              num_epochs: int) -> Iterator:
        """Create Parquet reader as fallback."""
        logger.info("Using Parquet fallback for data reading")
        
        def parquet_generator():
            for epoch in range(num_epochs):
                # Read Parquet files
                if os.path.isdir(dataset_path):
                    df = pd.read_parquet(dataset_path)
                else:
                    df = pd.read_parquet(dataset_path)
                
                if shuffle:
                    df = df.sample(frac=1).reset_index(drop=True)
                
                # Yield batches
                for i in range(0, len(df), batch_size):
                    batch = df.iloc[i:i + batch_size]
                    yield batch.to_dict('records')
        
        return parquet_generator()
    
    def get_dataset_statistics(self, dataset_path: str) -> Dict[str, Any]:
        """Get statistics for a dataset."""
        try:
            if os.path.isdir(dataset_path):
                df = pd.read_parquet(dataset_path)
            else:
                df = pd.read_parquet(dataset_path)
            
            stats = {
                'total_records': len(df),
                'unique_companies': df['company_id'].nunique(),
                'date_range': {
                    'start': df['timestamp'].min().isoformat(),
                    'end': df['timestamp'].max().isoformat()
                },
                'data_sources': df['data_source'].value_counts().to_dict(),
                'quality_scores': {
                    'mean': float(df['data_quality_score'].mean()),
                    'min': float(df['data_quality_score'].min()),
                    'max': float(df['data_quality_score'].max()),
                    'std': float(df['data_quality_score'].std())
                },
                'esg_scores': {
                    'environmental': {
                        'mean': float(df['environmental_score'].mean()),
                        'std': float(df['environmental_score'].std())
                    },
                    'social': {
                        'mean': float(df['social_score'].mean()),
                        'std': float(df['social_score'].std())
                    },
                    'governance': {
                        'mean': float(df['governance_score'].mean()),
                        'std': float(df['governance_score'].std())
                    }
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get dataset statistics: {e}")
            return {}
    
    def create_training_dataset(self, 
                               company_ids: List[str],
                               start_date: datetime,
                               end_date: datetime,
                               validation_split: float = 0.2,
                               test_split: float = 0.1) -> Dict[str, str]:
        """Create training, validation, and test datasets."""
        # Generate unique dataset ID
        dataset_id = hashlib.md5(
            f"{'-'.join(company_ids)}_{start_date}_{end_date}".encode()
        ).hexdigest()[:8]
        
        # Ingest data
        logger.info("Ingesting data for training dataset creation...")
        data = asyncio.run(self.ingest_multi_source_data(company_ids, start_date, end_date))
        
        if not data:
            raise ValueError("No data ingested for training dataset")
        
        # Split data
        total_size = len(data)
        test_size = int(total_size * test_split)
        val_size = int(total_size * validation_split)
        train_size = total_size - test_size - val_size
        
        # Shuffle data
        import random
        random.shuffle(data)
        
        # Split datasets
        train_data = data[:train_size]
        val_data = data[train_size:train_size + val_size]
        test_data = data[train_size + val_size:]
        
        # Create datasets
        datasets = {}
        
        # Training dataset
        train_path = self.create_petastorm_dataset(
            train_data, 
            f"train_{dataset_id}",
            partition_cols=['data_source']
        )
        datasets['train'] = train_path
        
        # Validation dataset
        val_path = self.create_petastorm_dataset(
            val_data, 
            f"val_{dataset_id}",
            partition_cols=['data_source']
        )
        datasets['validation'] = val_path
        
        # Test dataset
        test_path = self.create_petastorm_dataset(
            test_data, 
            f"test_{dataset_id}",
            partition_cols=['data_source']
        )
        datasets['test'] = test_path
        
        logger.info(f"Created training datasets: {len(datasets)} splits")
        logger.info(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
        
        return datasets
    
    def cleanup_old_datasets(self, days_old: int = 7) -> None:
        """Clean up old datasets to save storage space."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for dataset_dir in self.storage_path.iterdir():
            if dataset_dir.is_dir():
                # Check creation time
                creation_time = datetime.fromtimestamp(dataset_dir.stat().st_ctime)
                
                if creation_time < cutoff_date:
                    try:
                        import shutil
                        shutil.rmtree(dataset_dir)
                        logger.info(f"Cleaned up old dataset: {dataset_dir}")
                    except Exception as e:
                        logger.error(f"Failed to clean up dataset {dataset_dir}: {e}")


# Global pipeline instance
_pipeline_instance: Optional[PetastormMLPipeline] = None


def get_ml_pipeline() -> PetastormMLPipeline:
    """Get global ML pipeline instance."""
    global _pipeline_instance
    
    if _pipeline_instance is None:
        _pipeline_instance = PetastormMLPipeline()
    
    return _pipeline_instance


# Convenience functions
async def ingest_esg_data(company_ids: List[str], 
                         start_date: datetime, 
                         end_date: datetime,
                         sources: Optional[List[str]] = None) -> List[ESGDataPoint]:
    """Convenience function to ingest ESG data."""
    pipeline = get_ml_pipeline()
    return await pipeline.ingest_multi_source_data(company_ids, start_date, end_date, sources)


def create_ml_dataset(data: List[ESGDataPoint], 
                     dataset_name: str,
                     partition_cols: Optional[List[str]] = None) -> str:
    """Convenience function to create ML dataset."""
    pipeline = get_ml_pipeline()
    return pipeline.create_petastorm_dataset(data, dataset_name, partition_cols)


def get_ml_reader(dataset_path: str, 
                 batch_size: int = 32,
                 shuffle: bool = True,
                 num_epochs: int = 1) -> Iterator:
    """Convenience function to get ML data reader."""
    pipeline = get_ml_pipeline()
    return pipeline.create_ml_reader(dataset_path, batch_size, shuffle, num_epochs)

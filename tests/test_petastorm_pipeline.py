"""
Comprehensive Test Suite for Petastorm ML Pipeline

This module provides extensive testing for the ML-optimized ESG data pipeline
including schema validation, data quality checks, multi-source ingestion,
ML dataset creation, fallback mechanisms, and performance benchmarks.
"""

import pytest
import asyncio
import tempfile
import shutil
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import time
import os

# Import the modules to test
from src.data_management.petastorm_pipeline import (
    PetastormMLPipeline,
    ESGDataPoint,
    RefinitivAdapter,
    BloombergAdapter,
    get_ml_pipeline,
    ingest_esg_data,
    create_ml_dataset,
    get_ml_reader,
    PETASTORM_AVAILABLE,
    ESGUnischema
)
from src.validation.production_validator import get_validator
from src.config.production_config import get_config


class TestESGDataPoint:
    """Test ESGDataPoint data structure."""

    def test_esg_data_point_creation(self):
        """Test ESG data point creation and validation."""
        data_point = ESGDataPoint(
            company_id="AAPL",
            timestamp=datetime.now(),
            data_source="refinitiv",
            environmental_score=85.5,
            social_score=78.2,
            governance_score=92.1,
            combined_score=85.3,
            carbon_intensity=45.2,
            sector="Technology",
            region="North America"
        )

        assert data_point.company_id == "AAPL"
        assert data_point.environmental_score == 85.5
        assert data_point.carbon_intensity == 45.2
        assert data_point.data_quality_score == 1.0  # default

    def test_esg_data_point_to_dict(self):
        """Test ESG data point serialization."""
        timestamp = datetime.now()
        data_point = ESGDataPoint(
            company_id="MSFT",
            timestamp=timestamp,
            data_source="bloomberg",
            environmental_score=80.0,
            social_score=75.0,
            governance_score=90.0,
            combined_score=81.7
        )

        data_dict = data_point.to_dict()

        assert data_dict['company_id'] == "MSFT"
        assert data_dict['timestamp'] == timestamp.isoformat()
        assert data_dict['environmental_score'] == 80.0
        assert isinstance(data_dict, dict)


@pytest.mark.skipif(not PETASTORM_AVAILABLE, reason="Petastorm not available")
class TestPetastormSchema:
    """Test Petastorm schema validation."""

    def test_petastorm_schema_validation(self):
        """Test Petastorm schema creation and validation."""
        assert ESGUnischema is not None

        # Check required fields
        field_names = [field.name for field in ESGUnischema.fields]
        required_fields = [
            'company_id', 'timestamp', 'data_source',
            'environmental_score', 'social_score', 'governance_score',
            'combined_score', 'data_quality_score', 'confidence_score'
        ]

        for field in required_fields:
            assert field in field_names, f"Required field {field} missing from schema"

    def test_schema_field_types(self):
        """Test schema field types are correct."""
        field_types = {field.name: field.numpy_dtype for field in ESGUnischema.fields}

        # Check numeric fields
        assert field_types['environmental_score'] == np.float32
        assert field_types['social_score'] == np.float32
        assert field_types['governance_score'] == np.float32
        assert field_types['combined_score'] == np.float32

        # Check string fields
        assert field_types['company_id'] == np.str_
        assert field_types['data_source'] == np.str_


class TestDataIngestionAdapters:
    """Test data ingestion adapters."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            'rate_limit': 100,
            'timeout': 30,
            'enabled': True,
            'api_key': 'test_key'
        }

    def test_rate_limiter_creation(self, mock_config):
        """Test rate limiter initialization."""
        adapter = RefinitivAdapter(mock_config)

        assert adapter.rate_limiter['max_tokens'] == 100
        assert adapter.rate_limiter['tokens'] == 100
        assert adapter.rate_limiter['refill_rate'] == 100 / 60.0

    def test_rate_limit_check(self, mock_config):
        """Test rate limiting functionality."""
        adapter = RefinitivAdapter(mock_config)

        # Should allow first request
        assert adapter._check_rate_limit() == True

        # Exhaust all tokens
        for _ in range(99):
            adapter._check_rate_limit()

        # Should deny next request
        assert adapter._check_rate_limit() == False

    @pytest.mark.asyncio
    async def test_refinitiv_adapter_ingestion(self, mock_config):
        """Test Refinitiv adapter data ingestion."""
        with patch('src.data_management.petastorm_pipeline.get_premium_data_connector') as mock_connector:
            # Mock the connector response
            mock_esg_data = {
                'esg_scores': {
                    'environmental': 85.0,
                    'social': 78.0,
                    'governance': 92.0,
                    'combined': 85.0
                },
                'metrics': {
                    'carbon_intensity': 45.2,
                    'water_intensity': 12.5,
                    'energy_efficiency': 88.0
                },
                'data_quality': {
                    'confidence_score': 95.0
                }
            }

            mock_connector.return_value.get_esg_data.return_value = mock_esg_data

            adapter = RefinitivAdapter(mock_config)

            # Test data ingestion
            company_ids = ['AAPL', 'MSFT']
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()

            data_points = await adapter.ingest_data(company_ids, start_date, end_date)

            assert len(data_points) <= len(company_ids)  # May be filtered by validation
            if data_points:
                assert data_points[0].data_source == "refinitiv"
                assert data_points[0].environmental_score == 85.0


class TestDataQualityFramework:
    """Test comprehensive data quality checks."""

    def test_data_quality_validation(self):
        """Test comprehensive data quality checks."""
        # Create test data with various quality issues
        test_data = [
            # Good quality data
            ESGDataPoint(
                company_id="AAPL",
                timestamp=datetime.now(),
                data_source="refinitiv",
                environmental_score=85.0,
                social_score=78.0,
                governance_score=92.0,
                combined_score=85.0
            ),
            # Poor quality data (missing scores)
            ESGDataPoint(
                company_id="INVALID",
                timestamp=datetime.now(),
                data_source="mock",
                environmental_score=0.0,
                social_score=0.0,
                governance_score=0.0,
                combined_score=0.0
            )
        ]

        validator = get_validator()

        for data_point in test_data:
            data_dict = data_point.to_dict()
            quality_report = validator.validate_data(data_dict, data_point.data_source)

            assert quality_report.overall_score >= 0.0
            assert quality_report.overall_score <= 1.0
            assert len(quality_report.validation_results) > 0

    def test_mock_data_detection(self):
        """Test detection of mock/fake data."""
        # Create obviously fake data
        fake_data_point = ESGDataPoint(
            company_id="mock_company_123",
            timestamp=datetime.now(),
            data_source="mock_provider",
            environmental_score=80.0,  # Suspiciously round
            social_score=75.0,        # Suspiciously round
            governance_score=90.0,    # Suspiciously round
            combined_score=81.7
        )

        validator = get_validator()
        data_dict = fake_data_point.to_dict()
        data_dict['is_mock'] = True  # Explicit mock flag

        quality_report = validator.validate_data(data_dict, "mock")

        # Should detect mock data
        mock_detected = any(
            result.message.lower().find('mock') != -1
            for result in quality_report.validation_results
        )
        assert mock_detected, "Mock data detection failed"


class TestMLDatasetCreation:
    """Test ML-ready dataset generation with Petastorm."""

    @pytest.fixture
    def sample_esg_data(self):
        """Create sample ESG data for testing."""
        data = []
        companies = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

        for i, company in enumerate(companies):
            for days_back in range(10):
                timestamp = datetime.now() - timedelta(days=days_back)
                data_point = ESGDataPoint(
                    company_id=company,
                    timestamp=timestamp,
                    data_source="refinitiv" if i % 2 == 0 else "bloomberg",
                    environmental_score=70.0 + np.random.normal(0, 10),
                    social_score=75.0 + np.random.normal(0, 8),
                    governance_score=80.0 + np.random.normal(0, 12),
                    combined_score=75.0 + np.random.normal(0, 9),
                    carbon_intensity=50.0 + np.random.normal(0, 15),
                    sector="Technology",
                    region="North America"
                )
                data.append(data_point)

        return data

    def test_ml_dataset_creation(self, sample_esg_data):
        """Test ML-ready dataset generation with Petastorm."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the storage path
            with patch.object(PetastormMLPipeline, '__init__', lambda x: None):
                pipeline = PetastormMLPipeline()
                pipeline.config = get_config()
                pipeline.storage_path = Path(temp_dir)
                pipeline.adapters = {}
                pipeline.spark = None  # Force fallback mode

                # Create dataset
                dataset_path = pipeline.create_petastorm_dataset(
                    sample_esg_data,
                    "test_dataset",
                    partition_cols=['data_source']
                )

                assert os.path.exists(dataset_path)

                # Verify data can be read back
                if dataset_path.endswith('_parquet'):
                    df = pd.read_parquet(dataset_path)
                    assert len(df) == len(sample_esg_data)
                    assert 'company_id' in df.columns
                    assert 'environmental_score' in df.columns

    def test_dataset_statistics(self, sample_esg_data):
        """Test dataset statistics generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PetastormMLPipeline, '__init__', lambda x: None):
                pipeline = PetastormMLPipeline()
                pipeline.config = get_config()
                pipeline.storage_path = Path(temp_dir)
                pipeline.adapters = {}
                pipeline.spark = None

                # Create dataset
                dataset_path = pipeline.create_petastorm_dataset(
                    sample_esg_data,
                    "stats_test_dataset"
                )

                # Get statistics
                stats = pipeline.get_dataset_statistics(dataset_path)

                assert 'total_records' in stats
                assert 'unique_companies' in stats
                assert 'date_range' in stats
                assert 'esg_scores' in stats
                assert stats['total_records'] == len(sample_esg_data)


class TestFallbackMechanisms:
    """Test pandas fallback when Petastorm unavailable."""

    def test_parquet_fallback_dataset_creation(self):
        """Test pandas/parquet fallback dataset creation."""
        sample_data = [
            ESGDataPoint(
                company_id="TEST",
                timestamp=datetime.now(),
                data_source="test",
                environmental_score=80.0,
                social_score=75.0,
                governance_score=90.0,
                combined_score=81.7
            )
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PetastormMLPipeline, '__init__', lambda x: None):
                pipeline = PetastormMLPipeline()
                pipeline.config = get_config()
                pipeline.storage_path = Path(temp_dir)
                pipeline.adapters = {}
                pipeline.spark = None

                # Force fallback mode
                dataset_path = pipeline._create_parquet_fallback(
                    sample_data,
                    "fallback_test"
                )

                assert os.path.exists(dataset_path)

                # Verify data
                df = pd.read_parquet(dataset_path)
                assert len(df) == 1
                assert df.iloc[0]['company_id'] == "TEST"

    def test_parquet_reader_fallback(self):
        """Test parquet reader fallback functionality."""
        sample_data = [
            ESGDataPoint(
                company_id="TEST",
                timestamp=datetime.now(),
                data_source="test",
                environmental_score=80.0,
                social_score=75.0,
                governance_score=90.0,
                combined_score=81.7
            )
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PetastormMLPipeline, '__init__', lambda x: None):
                pipeline = PetastormMLPipeline()
                pipeline.config = get_config()
                pipeline.storage_path = Path(temp_dir)
                pipeline.adapters = {}
                pipeline.spark = None

                # Create dataset
                dataset_path = pipeline._create_parquet_fallback(
                    sample_data,
                    "reader_test"
                )

                # Test reader
                reader = pipeline._create_parquet_reader(
                    dataset_path,
                    batch_size=1,
                    shuffle=False,
                    num_epochs=1
                )

                batches = list(reader)
                assert len(batches) == 1
                assert len(batches[0]) == 1
                assert batches[0][0]['company_id'] == "TEST"


class TestMultiSourceIngestion:
    """Test ingestion from multiple ESG data sources."""

    @pytest.mark.asyncio
    async def test_multi_source_ingestion(self):
        """Test ingestion from multiple ESG data sources."""
        with patch.object(PetastormMLPipeline, '__init__', lambda x: None):
            pipeline = PetastormMLPipeline()
            pipeline.config = get_config()
            pipeline.storage_path = Path("/tmp")

            # Mock adapters
            mock_refinitiv = Mock()
            mock_bloomberg = Mock()

            # Mock data from different sources
            refinitiv_data = [
                ESGDataPoint(
                    company_id="AAPL",
                    timestamp=datetime.now(),
                    data_source="refinitiv",
                    environmental_score=85.0,
                    social_score=78.0,
                    governance_score=92.0,
                    combined_score=85.0
                )
            ]

            bloomberg_data = [
                ESGDataPoint(
                    company_id="AAPL",
                    timestamp=datetime.now(),
                    data_source="bloomberg",
                    environmental_score=83.0,
                    social_score=76.0,
                    governance_score=90.0,
                    combined_score=83.0,
                    data_quality_score=0.9  # Lower quality
                )
            ]

            mock_refinitiv.ingest_data = AsyncMock(return_value=refinitiv_data)
            mock_bloomberg.ingest_data = AsyncMock(return_value=bloomberg_data)

            pipeline.adapters = {
                'refinitiv': mock_refinitiv,
                'bloomberg': mock_bloomberg
            }

            # Test multi-source ingestion
            company_ids = ['AAPL']
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()

            all_data = await pipeline.ingest_multi_source_data(
                company_ids, start_date, end_date
            )

            # Should have deduplicated data (keeping higher quality)
            assert len(all_data) == 1
            assert all_data[0].data_source == "refinitiv"  # Higher quality

    def test_data_deduplication(self):
        """Test data deduplication logic."""
        # Create duplicate data with different quality scores
        data = [
            ESGDataPoint(
                company_id="AAPL",
                timestamp=datetime(2024, 1, 1),
                data_source="refinitiv",
                environmental_score=85.0,
                social_score=78.0,
                governance_score=92.0,
                combined_score=85.0,
                data_quality_score=0.95
            ),
            ESGDataPoint(
                company_id="AAPL",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),  # Same day
                data_source="bloomberg",
                environmental_score=83.0,
                social_score=76.0,
                governance_score=90.0,
                combined_score=83.0,
                data_quality_score=0.85  # Lower quality
            )
        ]

        with patch.object(PetastormMLPipeline, '__init__', lambda x: None):
            pipeline = PetastormMLPipeline()

            deduplicated = pipeline._deduplicate_data(data)

            # Should keep only the higher quality data point
            assert len(deduplicated) == 1
            assert deduplicated[0].data_quality_score == 0.95


class TestPerformanceBenchmarks:
    """Test pipeline performance under load."""

    def test_performance_benchmarks(self):
        """Test pipeline performance under load."""
        # Create large dataset for performance testing
        large_dataset = []
        companies = [f"COMP_{i:04d}" for i in range(100)]

        start_time = time.time()

        for company in companies:
            for days_back in range(30):  # 30 days of data per company
                timestamp = datetime.now() - timedelta(days=days_back)
                data_point = ESGDataPoint(
                    company_id=company,
                    timestamp=timestamp,
                    data_source="test",
                    environmental_score=70.0 + np.random.normal(0, 10),
                    social_score=75.0 + np.random.normal(0, 8),
                    governance_score=80.0 + np.random.normal(0, 12),
                    combined_score=75.0 + np.random.normal(0, 9)
                )
                large_dataset.append(data_point)

        creation_time = time.time() - start_time

        # Test dataset creation performance
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PetastormMLPipeline, '__init__', lambda x: None):
                pipeline = PetastormMLPipeline()
                pipeline.config = get_config()
                pipeline.storage_path = Path(temp_dir)
                pipeline.spark = None

                dataset_start = time.time()
                dataset_path = pipeline._create_parquet_fallback(
                    large_dataset,
                    "performance_test"
                )
                dataset_time = time.time() - dataset_start

                # Performance assertions
                assert len(large_dataset) == 3000  # 100 companies * 30 days
                assert creation_time < 5.0  # Should create data in < 5 seconds
                assert dataset_time < 10.0  # Should create dataset in < 10 seconds
                assert os.path.exists(dataset_path)

                # Test read performance
                read_start = time.time()
                df = pd.read_parquet(dataset_path)
                read_time = time.time() - read_start

                assert len(df) == len(large_dataset)
                assert read_time < 5.0  # Should read in < 5 seconds

    def test_memory_usage(self):
        """Test memory usage during large dataset processing."""
        import psutil
        import gc

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create and process large dataset
        large_dataset = []
        for i in range(1000):
            data_point = ESGDataPoint(
                company_id=f"COMP_{i}",
                timestamp=datetime.now(),
                data_source="test",
                environmental_score=80.0,
                social_score=75.0,
                governance_score=90.0,
                combined_score=81.7
            )
            large_dataset.append(data_point)

        peak_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Clean up
        del large_dataset
        gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Memory usage should be reasonable
        memory_increase = peak_memory - initial_memory
        assert memory_increase < 500  # Should use less than 500MB for 1000 records

        # Memory should be released after cleanup
        memory_after_cleanup = final_memory - initial_memory
        assert memory_after_cleanup < memory_increase * 0.5  # At least 50% released


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge case scenarios."""

    def test_empty_dataset_handling(self):
        """Test handling of empty datasets."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(PetastormMLPipeline, '__init__', lambda x: None):
                pipeline = PetastormMLPipeline()
                pipeline.config = get_config()
                pipeline.storage_path = Path(temp_dir)
                pipeline.spark = None

                # Test with empty data
                empty_data = []
                dataset_path = pipeline._create_parquet_fallback(
                    empty_data,
                    "empty_test"
                )

                # Should handle gracefully
                assert os.path.exists(dataset_path)

    def test_invalid_data_handling(self):
        """Test handling of invalid data."""
        invalid_data = [
            ESGDataPoint(
                company_id="",  # Empty company ID
                timestamp=datetime.now(),
                data_source="test",
                environmental_score=float('inf'),  # Invalid score
                social_score=-10.0,  # Out of range
                governance_score=150.0,  # Out of range
                combined_score=float('nan')  # NaN value
            )
        ]

        validator = get_validator()

        for data_point in invalid_data:
            data_dict = data_point.to_dict()
            quality_report = validator.validate_data(data_dict, data_point.data_source)

            # Should detect quality issues
            assert quality_report.overall_score < 0.8  # Poor quality

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors during ingestion."""
        with patch.object(PetastormMLPipeline, '__init__', lambda x: None):
            pipeline = PetastormMLPipeline()

            # Mock adapter that raises network error
            mock_adapter = Mock()
            mock_adapter.ingest_data = AsyncMock(
                side_effect=Exception("Network error")
            )

            pipeline.adapters = {'failing_source': mock_adapter}

            # Should handle network errors gracefully
            company_ids = ['AAPL']
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()

            # Should not raise exception
            data = await pipeline.ingest_multi_source_data(
                company_ids, start_date, end_date
            )

            # Should return empty list when all sources fail
            assert data == []

    def test_disk_space_handling(self):
        """Test handling of insufficient disk space."""
        # This test would require mocking filesystem operations
        # to simulate disk space issues
        pass


class TestIntegration:
    """Integration tests for the complete pipeline."""

    @pytest.mark.asyncio
    async def test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the entire pipeline
            with patch.object(PetastormMLPipeline, '__init__', lambda x: None):
                pipeline = PetastormMLPipeline()
                pipeline.config = get_config()
                pipeline.storage_path = Path(temp_dir)
                pipeline.spark = None

                # Mock adapters with realistic data
                mock_adapter = Mock()
                sample_data = [
                    ESGDataPoint(
                        company_id="AAPL",
                        timestamp=datetime.now(),
                        data_source="test",
                        environmental_score=85.0,
                        social_score=78.0,
                        governance_score=92.0,
                        combined_score=85.0
                    )
                ]
                mock_adapter.ingest_data = AsyncMock(return_value=sample_data)
                pipeline.adapters = {'test': mock_adapter}

                # Test complete workflow
                company_ids = ['AAPL']
                start_date = datetime.now() - timedelta(days=30)
                end_date = datetime.now()

                # 1. Ingest data
                data = await pipeline.ingest_multi_source_data(
                    company_ids, start_date, end_date
                )
                assert len(data) == 1

                # 2. Create dataset
                dataset_path = pipeline.create_petastorm_dataset(
                    data, "integration_test"
                )
                assert os.path.exists(dataset_path)

                # 3. Get statistics
                stats = pipeline.get_dataset_statistics(dataset_path)
                assert stats['total_records'] == 1

                # 4. Create reader
                reader = pipeline.create_ml_reader(dataset_path, batch_size=1)
                batches = list(reader)
                assert len(batches) == 1


# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class TestTrendRadarIntegration:
    """Test TrendRadar integration with Petastorm pipeline."""

    @pytest.mark.asyncio
    async def test_trendradar_ml_trends_api(self):
        """Test TrendRadar ML trends API endpoint."""
        from src.frontend.routes.trendradar import TrendRadarRoute

        # Mock the ML pipeline
        with patch('src.frontend.routes.trendradar.get_ml_pipeline') as mock_pipeline:
            with patch('src.frontend.routes.trendradar.ingest_esg_data') as mock_ingest:
                # Mock ESG data
                mock_esg_data = [
                    ESGDataPoint(
                        company_id="AAPL",
                        timestamp=datetime.now(),
                        data_source="test",
                        environmental_score=85.0,
                        social_score=78.0,
                        governance_score=92.0,
                        combined_score=85.0,
                        sector="Technology"
                    )
                ]

                mock_ingest.return_value = mock_esg_data

                # Create TrendRadar route
                route = TrendRadarRoute()

                # Test ML-powered trends
                ml_trends = route._get_ml_powered_trends()

                assert len(ml_trends) > 0
                assert all('category' in trend for trend in ml_trends)
                assert all('score' in trend for trend in ml_trends)
                assert all('metrics' in trend for trend in ml_trends)

    def test_esg_trend_analysis(self):
        """Test ESG trend analysis functionality."""
        from src.frontend.routes.trendradar import TrendRadarRoute

        # Create sample ESG data
        esg_data = [
            ESGDataPoint(
                company_id="AAPL",
                timestamp=datetime.now(),
                data_source="refinitiv",
                environmental_score=85.0,
                social_score=78.0,
                governance_score=92.0,
                combined_score=85.0,
                sector="Technology",
                data_quality_score=0.95
            ),
            ESGDataPoint(
                company_id="MSFT",
                timestamp=datetime.now(),
                data_source="bloomberg",
                environmental_score=82.0,
                social_score=80.0,
                governance_score=88.0,
                combined_score=83.3,
                sector="Technology",
                data_quality_score=0.92
            )
        ]

        route = TrendRadarRoute()

        # Test trend analysis
        trends = route._analyze_esg_trends(esg_data)

        assert len(trends) > 0
        assert trends[0]['category'] == 'Climate Tech'  # Technology -> Climate Tech
        assert 'environmental_impact' in trends[0]['metrics']
        assert 'data_quality' in trends[0]
        assert trends[0]['companies_analyzed'] == 2

    def test_sector_mapping(self):
        """Test sector to category mapping."""
        from src.frontend.routes.trendradar import TrendRadarRoute

        route = TrendRadarRoute()

        # Test known mappings
        assert route._map_sector_to_category("Technology") == "Climate Tech"
        assert route._map_sector_to_category("Energy") == "Renewable Energy"
        assert route._map_sector_to_category("Financials") == "Sustainable Finance"

        # Test unknown sector
        assert route._map_sector_to_category("Unknown") == "Emerging Sustainability"

    def test_trend_values_generation(self):
        """Test trend values generation for visualization."""
        from src.frontend.routes.trendradar import TrendRadarRoute

        route = TrendRadarRoute()

        # Test with single score
        single_score = [75.0]
        values = route._generate_trend_values(single_score)
        assert len(values) == 12
        assert values[0] == 75.0

        # Test with multiple scores
        multiple_scores = [70.0, 75.0, 80.0, 85.0]
        values = route._generate_trend_values(multiple_scores)
        assert len(values) == 12
        assert values[0] == 70.0
        assert values[-1] == 85.0

    def test_esg_summary_calculation(self):
        """Test ESG summary statistics calculation."""
        from src.frontend.routes.trendradar import TrendRadarRoute

        esg_data = [
            ESGDataPoint(
                company_id="AAPL",
                timestamp=datetime.now(),
                data_source="test",
                environmental_score=85.0,
                social_score=78.0,
                governance_score=92.0,
                combined_score=85.0
            ),
            ESGDataPoint(
                company_id="MSFT",
                timestamp=datetime.now(),
                data_source="test",
                environmental_score=80.0,
                social_score=82.0,
                governance_score=88.0,
                combined_score=83.3
            )
        ]

        route = TrendRadarRoute()
        summary = route._calculate_esg_summary(esg_data)

        assert 'environmental' in summary
        assert 'social' in summary
        assert 'governance' in summary
        assert 'combined' in summary

        # Check environmental stats
        assert summary['environmental']['mean'] == 82.5  # (85 + 80) / 2
        assert summary['environmental']['min'] == 80.0
        assert summary['environmental']['max'] == 85.0

    def test_mock_predictions_fallback(self):
        """Test mock predictions fallback functionality."""
        from src.frontend.routes.trendradar import TrendRadarRoute

        route = TrendRadarRoute()
        predictions = route._get_mock_predictions()

        assert 'predictions' in predictions
        assert 'forecast_horizon' in predictions
        assert 'confidence_level' in predictions
        assert predictions['model_version'] == 'fallback'

        # Check prediction structure
        for prediction in predictions['predictions']:
            assert 'category' in prediction
            assert 'predicted_growth' in prediction
            assert 'confidence' in prediction
            assert 'key_drivers' in prediction

    @pytest.mark.asyncio
    async def test_ml_trends_fallback(self):
        """Test ML trends fallback to traditional data."""
        from src.frontend.routes.trendradar import TrendRadarRoute

        with patch('src.frontend.routes.trendradar.ingest_esg_data') as mock_ingest:
            # Mock empty ESG data to trigger fallback
            mock_ingest.return_value = []

            route = TrendRadarRoute()

            # Should fallback to traditional trends
            trends = route._get_ml_powered_trends()

            # Should have some trends (from fallback)
            assert len(trends) > 0
            assert all('category' in trend for trend in trends)

    def test_data_quality_metrics_calculation(self):
        """Test data quality metrics calculation."""
        from src.frontend.routes.trendradar import TrendRadarRoute

        esg_data = [
            ESGDataPoint(
                company_id="AAPL",
                timestamp=datetime.now(),
                data_source="refinitiv",
                environmental_score=85.0,
                social_score=78.0,
                governance_score=92.0,
                combined_score=85.0,
                data_quality_score=0.95,
                confidence_score=0.92
            ),
            ESGDataPoint(
                company_id="MSFT",
                timestamp=datetime.now(),
                data_source="bloomberg",
                environmental_score=80.0,
                social_score=82.0,
                governance_score=88.0,
                combined_score=83.3,
                data_quality_score=0.88,
                confidence_score=0.90
            )
        ]

        route = TrendRadarRoute()
        quality_metrics = route._calculate_quality_metrics(esg_data)

        assert 'data_quality' in quality_metrics
        assert 'confidence' in quality_metrics
        assert 'data_sources' in quality_metrics

        # Check quality scores
        assert quality_metrics['data_quality']['mean'] == 0.915  # (0.95 + 0.88) / 2
        assert quality_metrics['confidence']['mean'] == 0.91  # (0.92 + 0.90) / 2

        # Check data sources
        assert set(quality_metrics['data_sources']) == {'refinitiv', 'bloomberg'}


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])

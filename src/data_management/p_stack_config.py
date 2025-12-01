"""
Configuration Management System for LensIQ ML-Optimized ESG Data Pipeline

This module provides a comprehensive configuration management system following
enterprise best practices with environment-based settings, validation, and
dynamic configuration loading.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from pathlib import Path
import yaml
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ESGDataSourceConfig:
    """Configuration for ESG data sources."""
    name: str
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    timeout: int = 30  # seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0  # seconds
    enabled: bool = True
    data_types: List[str] = field(default_factory=lambda: ["environmental", "social", "governance"])
    quality_threshold: float = 0.8  # minimum quality score


@dataclass
class PetastormConfig:
    """Configuration for Petastorm ML pipeline."""
    storage_path: str = "./data/petastorm"
    parquet_row_group_size: int = 50000
    compression: str = "snappy"
    schema_version: str = "1.0"
    enable_cache: bool = True
    cache_size_mb: int = 1024
    workers: int = 4
    batch_size: int = 1000
    shuffle_buffer_size: int = 10000
    prefetch_buffer_size: int = 2


@dataclass
class DataQualityConfig:
    """Configuration for data quality validation."""
    completeness_threshold: float = 0.95
    validity_threshold: float = 0.90
    consistency_threshold: float = 0.85
    timeliness_threshold_hours: int = 24
    enable_profiling: bool = True
    enable_anomaly_detection: bool = True
    anomaly_threshold: float = 2.0  # standard deviations
    quality_report_frequency: str = "daily"  # daily, weekly, monthly


@dataclass
class MLConfig:
    """Configuration for ML training and serving."""
    model_storage_path: str = "./models"
    feature_store_path: str = "./features"
    training_data_path: str = "./data/training"
    validation_split: float = 0.2
    test_split: float = 0.1
    random_seed: int = 42
    enable_distributed_training: bool = False
    max_epochs: int = 100
    early_stopping_patience: int = 10
    learning_rate: float = 0.001
    batch_size: int = 32


@dataclass
class SecurityConfig:
    """Configuration for security and compliance."""
    enable_encryption: bool = True
    encryption_key_path: Optional[str] = None
    enable_audit_logging: bool = True
    audit_log_path: str = "./logs/audit"
    data_retention_days: int = 365
    enable_pii_detection: bool = True
    enable_data_masking: bool = True
    compliance_frameworks: List[str] = field(default_factory=lambda: ["GDPR", "CCPA"])


class PStackConfig:
    """
    Comprehensive configuration management for LensIQ ESG Data Pipeline.
    
    Supports environment-based configuration, validation, and dynamic loading.
    """
    
    def __init__(self, config_path: Optional[str] = None, environment: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
            environment: Environment name (development, staging, production)
        """
        self.environment = environment or os.getenv("LENSIQ_ENV", "development")
        self.config_path = config_path or self._get_default_config_path()
        
        # Initialize configuration sections
        self.data_sources: Dict[str, ESGDataSourceConfig] = {}
        self.petastorm: PetastormConfig = PetastormConfig()
        self.data_quality: DataQualityConfig = DataQualityConfig()
        self.ml: MLConfig = MLConfig()
        self.security: SecurityConfig = SecurityConfig()
        
        # Load configuration
        self._load_configuration()
        self._validate_configuration()
        
        logger.info(f"Configuration loaded for environment: {self.environment}")
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        base_path = Path(__file__).parent.parent.parent
        return str(base_path / "config" / f"lensiq_{self.environment}.yaml")
    
    def _load_configuration(self) -> None:
        """Load configuration from file and environment variables."""
        # Load from file if exists
        if os.path.exists(self.config_path):
            self._load_from_file()
        else:
            logger.warning(f"Configuration file not found: {self.config_path}")
        
        # Override with environment variables
        self._load_from_environment()
        
        # Load data source configurations
        self._load_data_source_configs()
    
    def _load_from_file(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Update configurations
            if 'petastorm' in config_data:
                self._update_petastorm_config(config_data['petastorm'])
            
            if 'data_quality' in config_data:
                self._update_data_quality_config(config_data['data_quality'])
            
            if 'ml' in config_data:
                self._update_ml_config(config_data['ml'])
            
            if 'security' in config_data:
                self._update_security_config(config_data['security'])
            
            logger.info(f"Configuration loaded from file: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error loading configuration file: {str(e)}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # Petastorm configuration
        if os.getenv("LENSIQ_PETASTORM_STORAGE_PATH"):
            self.petastorm.storage_path = os.getenv("LENSIQ_PETASTORM_STORAGE_PATH")
        
        if os.getenv("LENSIQ_PETASTORM_WORKERS"):
            self.petastorm.workers = int(os.getenv("LENSIQ_PETASTORM_WORKERS"))
        
        if os.getenv("LENSIQ_PETASTORM_BATCH_SIZE"):
            self.petastorm.batch_size = int(os.getenv("LENSIQ_PETASTORM_BATCH_SIZE"))
        
        # Data quality configuration
        if os.getenv("LENSIQ_QUALITY_COMPLETENESS_THRESHOLD"):
            self.data_quality.completeness_threshold = float(os.getenv("LENSIQ_QUALITY_COMPLETENESS_THRESHOLD"))
        
        if os.getenv("LENSIQ_QUALITY_VALIDITY_THRESHOLD"):
            self.data_quality.validity_threshold = float(os.getenv("LENSIQ_QUALITY_VALIDITY_THRESHOLD"))
        
        # ML configuration
        if os.getenv("LENSIQ_ML_MODEL_STORAGE_PATH"):
            self.ml.model_storage_path = os.getenv("LENSIQ_ML_MODEL_STORAGE_PATH")
        
        if os.getenv("LENSIQ_ML_BATCH_SIZE"):
            self.ml.batch_size = int(os.getenv("LENSIQ_ML_BATCH_SIZE"))
        
        # Security configuration
        if os.getenv("LENSIQ_ENABLE_ENCRYPTION"):
            self.security.enable_encryption = os.getenv("LENSIQ_ENABLE_ENCRYPTION").lower() == "true"
        
        if os.getenv("LENSIQ_ENCRYPTION_KEY_PATH"):
            self.security.encryption_key_path = os.getenv("LENSIQ_ENCRYPTION_KEY_PATH")
    
    def _load_data_source_configs(self) -> None:
        """Load ESG data source configurations."""
        # Refinitiv
        if os.getenv("REFINITIV_API_KEY"):
            self.data_sources["refinitiv"] = ESGDataSourceConfig(
                name="refinitiv",
                provider="Refinitiv",
                api_key=os.getenv("REFINITIV_API_KEY"),
                base_url=os.getenv("REFINITIV_BASE_URL", "https://api.refinitiv.com"),
                rate_limit=int(os.getenv("REFINITIV_RATE_LIMIT", "100")),
                timeout=int(os.getenv("REFINITIV_TIMEOUT", "30"))
            )
        
        # Bloomberg
        if os.getenv("BLOOMBERG_API_KEY"):
            self.data_sources["bloomberg"] = ESGDataSourceConfig(
                name="bloomberg",
                provider="Bloomberg",
                api_key=os.getenv("BLOOMBERG_API_KEY"),
                base_url=os.getenv("BLOOMBERG_BASE_URL", "https://api.bloomberg.com"),
                rate_limit=int(os.getenv("BLOOMBERG_RATE_LIMIT", "50")),
                timeout=int(os.getenv("BLOOMBERG_TIMEOUT", "30"))
            )
        
        # MSCI
        if os.getenv("MSCI_API_KEY"):
            self.data_sources["msci"] = ESGDataSourceConfig(
                name="msci",
                provider="MSCI",
                api_key=os.getenv("MSCI_API_KEY"),
                base_url=os.getenv("MSCI_BASE_URL", "https://api.msci.com"),
                rate_limit=int(os.getenv("MSCI_RATE_LIMIT", "75")),
                timeout=int(os.getenv("MSCI_TIMEOUT", "30"))
            )
        
        # Sustainalytics
        if os.getenv("SUSTAINALYTICS_API_KEY"):
            self.data_sources["sustainalytics"] = ESGDataSourceConfig(
                name="sustainalytics",
                provider="Sustainalytics",
                api_key=os.getenv("SUSTAINALYTICS_API_KEY"),
                base_url=os.getenv("SUSTAINALYTICS_BASE_URL", "https://api.sustainalytics.com"),
                rate_limit=int(os.getenv("SUSTAINALYTICS_RATE_LIMIT", "60")),
                timeout=int(os.getenv("SUSTAINALYTICS_TIMEOUT", "30"))
            )
        
        # SEC EDGAR (public data)
        self.data_sources["sec_edgar"] = ESGDataSourceConfig(
            name="sec_edgar",
            provider="SEC EDGAR",
            base_url="https://www.sec.gov/Archives/edgar",
            rate_limit=10,  # SEC has strict rate limits
            timeout=60,
            enabled=True
        )
        
        # News feeds
        if os.getenv("NEWS_API_KEY"):
            self.data_sources["news_api"] = ESGDataSourceConfig(
                name="news_api",
                provider="NewsAPI",
                api_key=os.getenv("NEWS_API_KEY"),
                base_url="https://newsapi.org/v2",
                rate_limit=int(os.getenv("NEWS_API_RATE_LIMIT", "1000")),
                timeout=int(os.getenv("NEWS_API_TIMEOUT", "30"))
            )
    
    def _update_petastorm_config(self, config_data: Dict[str, Any]) -> None:
        """Update Petastorm configuration from data."""
        for key, value in config_data.items():
            if hasattr(self.petastorm, key):
                setattr(self.petastorm, key, value)
    
    def _update_data_quality_config(self, config_data: Dict[str, Any]) -> None:
        """Update data quality configuration from data."""
        for key, value in config_data.items():
            if hasattr(self.data_quality, key):
                setattr(self.data_quality, key, value)
    
    def _update_ml_config(self, config_data: Dict[str, Any]) -> None:
        """Update ML configuration from data."""
        for key, value in config_data.items():
            if hasattr(self.ml, key):
                setattr(self.ml, key, value)
    
    def _update_security_config(self, config_data: Dict[str, Any]) -> None:
        """Update security configuration from data."""
        for key, value in config_data.items():
            if hasattr(self.security, key):
                setattr(self.security, key, value)
    
    def _validate_configuration(self) -> None:
        """Validate configuration settings."""
        errors = []
        
        # Validate Petastorm configuration
        if self.petastorm.workers <= 0:
            errors.append("Petastorm workers must be greater than 0")
        
        if self.petastorm.batch_size <= 0:
            errors.append("Petastorm batch size must be greater than 0")
        
        # Validate data quality thresholds
        if not (0 <= self.data_quality.completeness_threshold <= 1):
            errors.append("Completeness threshold must be between 0 and 1")
        
        if not (0 <= self.data_quality.validity_threshold <= 1):
            errors.append("Validity threshold must be between 0 and 1")
        
        # Validate ML configuration
        if not (0 < self.ml.validation_split < 1):
            errors.append("Validation split must be between 0 and 1")
        
        if not (0 < self.ml.test_split < 1):
            errors.append("Test split must be between 0 and 1")
        
        if (self.ml.validation_split + self.ml.test_split) >= 1:
            errors.append("Validation and test splits combined must be less than 1")
        
        # Validate data source configurations
        for name, config in self.data_sources.items():
            if config.enabled and config.api_key is None and name not in ["sec_edgar"]:
                errors.append(f"API key required for enabled data source: {name}")
        
        if errors:
            error_msg = "Configuration validation errors:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validation passed")
    
    def get_data_source_config(self, source_name: str) -> Optional[ESGDataSourceConfig]:
        """
        Get configuration for a specific data source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Data source configuration or None if not found
        """
        return self.data_sources.get(source_name)
    
    def get_enabled_data_sources(self) -> List[ESGDataSourceConfig]:
        """
        Get list of enabled data sources.
        
        Returns:
            List of enabled data source configurations
        """
        return [config for config in self.data_sources.values() if config.enabled]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        return {
            "environment": self.environment,
            "data_sources": {name: config.__dict__ for name, config in self.data_sources.items()},
            "petastorm": self.petastorm.__dict__,
            "data_quality": self.data_quality.__dict__,
            "ml": self.ml.__dict__,
            "security": self.security.__dict__,
            "loaded_at": datetime.now().isoformat()
        }
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save configuration
        """
        try:
            config_dict = self.to_dict()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, default=str)
            
            logger.info(f"Configuration saved to: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            raise


# Global configuration instance
_config_instance: Optional[PStackConfig] = None


def get_config(config_path: Optional[str] = None, environment: Optional[str] = None) -> PStackConfig:
    """
    Get global configuration instance (singleton pattern).
    
    Args:
        config_path: Path to configuration file
        environment: Environment name
        
    Returns:
        Configuration instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = PStackConfig(config_path, environment)
    
    return _config_instance


def reload_config(config_path: Optional[str] = None, environment: Optional[str] = None) -> PStackConfig:
    """
    Reload configuration (force new instance).
    
    Args:
        config_path: Path to configuration file
        environment: Environment name
        
    Returns:
        New configuration instance
    """
    global _config_instance
    _config_instance = PStackConfig(config_path, environment)
    return _config_instance


# Configuration validation utilities
def validate_environment_variables() -> List[str]:
    """
    Validate required environment variables.
    
    Returns:
        List of missing environment variables
    """
    required_vars = [
        "LENSIQ_ENV",
        "LENSIQ_PETASTORM_STORAGE_PATH",
    ]
    
    optional_vars = [
        "REFINITIV_API_KEY",
        "BLOOMBERG_API_KEY",
        "MSCI_API_KEY",
        "SUSTAINALYTICS_API_KEY",
        "NEWS_API_KEY",
        "LENSIQ_ENCRYPTION_KEY_PATH"
    ]
    
    missing_required = [var for var in required_vars if not os.getenv(var)]
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    
    if missing_optional:
        logger.warning(f"Optional environment variables not set: {missing_optional}")
    
    return missing_required


def create_default_config_file(file_path: str, environment: str = "development") -> None:
    """
    Create a default configuration file.
    
    Args:
        file_path: Path to create configuration file
        environment: Environment name
    """
    default_config = {
        "environment": environment,
        "petastorm": {
            "storage_path": "./data/petastorm",
            "workers": 4,
            "batch_size": 1000,
            "enable_cache": True,
            "cache_size_mb": 1024
        },
        "data_quality": {
            "completeness_threshold": 0.95,
            "validity_threshold": 0.90,
            "consistency_threshold": 0.85,
            "enable_profiling": True,
            "enable_anomaly_detection": True
        },
        "ml": {
            "model_storage_path": "./models",
            "validation_split": 0.2,
            "test_split": 0.1,
            "batch_size": 32,
            "learning_rate": 0.001
        },
        "security": {
            "enable_encryption": True,
            "enable_audit_logging": True,
            "data_retention_days": 365,
            "compliance_frameworks": ["GDPR", "CCPA"]
        }
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False, indent=2)
    
    logger.info(f"Default configuration file created: {file_path}")

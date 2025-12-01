"""
Production Configuration Management for LensIQ

This module provides enterprise-grade configuration management with:
- Environment-based settings
- Security validation
- No hardcoded values
- Production deployment ready
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import secrets

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration for LensIQ."""
    adapter: str
    name: str
    uri: str
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_enabled: bool = True
    connection_timeout: int = 30
    pool_size: int = 10
    
    def __post_init__(self):
        """Validate database configuration."""
        if not self.adapter:
            raise ValueError("Database adapter must be specified")
        if not self.name:
            raise ValueError("Database name must be specified")
        if not self.uri:
            raise ValueError("Database URI must be specified")


@dataclass
class SecurityConfig:
    """Security configuration for LensIQ."""
    secret_key: str
    encryption_key: str
    jwt_secret: str
    api_key_header: str = "X-LensIQ-API-Key"
    session_timeout: int = 3600  # 1 hour
    max_login_attempts: int = 5
    password_min_length: int = 12
    enable_2fa: bool = True
    cors_origins: List[str] = None
    
    def __post_init__(self):
        """Validate security configuration."""
        if not self.secret_key or len(self.secret_key) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        if not self.encryption_key or len(self.encryption_key) < 32:
            raise ValueError("Encryption key must be at least 32 characters")
        if not self.jwt_secret or len(self.jwt_secret) < 32:
            raise ValueError("JWT secret must be at least 32 characters")
        
        if self.cors_origins is None:
            self.cors_origins = []


@dataclass
class StorageConfig:
    """Storage configuration for LensIQ."""
    base_path: str
    data_path: str
    model_path: str
    log_path: str
    cache_path: str
    backup_path: str
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    retention_days: int = 365
    enable_encryption: bool = True
    
    def __post_init__(self):
        """Validate and create storage paths."""
        for path_name, path_value in [
            ("base_path", self.base_path),
            ("data_path", self.data_path),
            ("model_path", self.model_path),
            ("log_path", self.log_path),
            ("cache_path", self.cache_path),
            ("backup_path", self.backup_path)
        ]:
            if not path_value:
                raise ValueError(f"{path_name} must be specified")
            
            # Create directory if it doesn't exist
            Path(path_value).mkdir(parents=True, exist_ok=True)


@dataclass
class APIConfig:
    """API configuration for LensIQ."""
    base_url: str
    version: str = "v1"
    rate_limit_per_minute: int = 1000
    rate_limit_per_hour: int = 10000
    timeout: int = 30
    max_retries: int = 3
    enable_swagger: bool = False  # Disable in production
    enable_metrics: bool = True
    
    def __post_init__(self):
        """Validate API configuration."""
        if not self.base_url:
            raise ValueError("API base URL must be specified")
        if not self.base_url.startswith(('http://', 'https://')):
            raise ValueError("API base URL must include protocol")


@dataclass
class DataSourceConfig:
    """Data source configuration for LensIQ."""
    name: str
    provider: str
    base_url: str
    api_key: str
    rate_limit: int = 100
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enabled: bool = True
    health_check_endpoint: Optional[str] = None
    
    def __post_init__(self):
        """Validate data source configuration."""
        if not self.name:
            raise ValueError("Data source name must be specified")
        if not self.provider:
            raise ValueError("Data source provider must be specified")
        if not self.base_url:
            raise ValueError("Data source base URL must be specified")
        if self.enabled and not self.api_key:
            raise ValueError(f"API key required for enabled data source: {self.name}")


@dataclass
class MLConfig:
    """Machine Learning configuration for LensIQ."""
    model_storage_path: str
    feature_store_path: str
    training_data_path: str
    batch_size: int = 32
    max_epochs: int = 100
    learning_rate: float = 0.001
    validation_split: float = 0.2
    test_split: float = 0.1
    random_seed: int = 42
    enable_gpu: bool = False
    distributed_training: bool = False
    
    def __post_init__(self):
        """Validate ML configuration."""
        if not (0 < self.validation_split < 1):
            raise ValueError("Validation split must be between 0 and 1")
        if not (0 < self.test_split < 1):
            raise ValueError("Test split must be between 0 and 1")
        if (self.validation_split + self.test_split) >= 1:
            raise ValueError("Validation and test splits combined must be less than 1")


class ProductionConfig:
    """
    Production configuration manager for LensIQ.
    
    Provides enterprise-grade configuration management with:
    - Environment-based settings
    - Security validation
    - No hardcoded values
    - Production deployment ready
    """
    
    def __init__(self, environment: str = None):
        """
        Initialize production configuration.
        
        Args:
            environment: Environment name (development, staging, production)
        """
        self.environment = environment or os.getenv("LENSIQ_ENV", "production")
        
        # Load all configuration sections
        self.database = self._load_database_config()
        self.security = self._load_security_config()
        self.storage = self._load_storage_config()
        self.api = self._load_api_config()
        self.ml = self._load_ml_config()
        self.data_sources = self._load_data_sources_config()
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info(f"Production configuration loaded for environment: {self.environment}")
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment."""
        return DatabaseConfig(
            adapter=self._get_required_env("LENSIQ_DATABASE_ADAPTER"),
            name=self._get_required_env("LENSIQ_DATABASE_NAME"),
            uri=self._get_required_env("LENSIQ_DATABASE_URI"),
            username=os.getenv("LENSIQ_DATABASE_USERNAME"),
            password=os.getenv("LENSIQ_DATABASE_PASSWORD"),
            ssl_enabled=os.getenv("LENSIQ_DATABASE_SSL", "true").lower() == "true",
            connection_timeout=int(os.getenv("LENSIQ_DATABASE_TIMEOUT", "30")),
            pool_size=int(os.getenv("LENSIQ_DATABASE_POOL_SIZE", "10"))
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration from environment."""
        # Generate secure defaults if not provided (for development only)
        default_secret = secrets.token_urlsafe(32) if self.environment == "development" else None
        
        return SecurityConfig(
            secret_key=self._get_required_env("LENSIQ_SECRET_KEY", default_secret),
            encryption_key=self._get_required_env("LENSIQ_ENCRYPTION_KEY"),
            jwt_secret=self._get_required_env("LENSIQ_JWT_SECRET"),
            api_key_header=os.getenv("LENSIQ_API_KEY_HEADER", "X-LensIQ-API-Key"),
            session_timeout=int(os.getenv("LENSIQ_SESSION_TIMEOUT", "3600")),
            max_login_attempts=int(os.getenv("LENSIQ_MAX_LOGIN_ATTEMPTS", "5")),
            password_min_length=int(os.getenv("LENSIQ_PASSWORD_MIN_LENGTH", "12")),
            enable_2fa=os.getenv("LENSIQ_ENABLE_2FA", "true").lower() == "true",
            cors_origins=self._parse_list(os.getenv("LENSIQ_CORS_ORIGINS", ""))
        )
    
    def _load_storage_config(self) -> StorageConfig:
        """Load storage configuration from environment."""
        base_path = self._get_required_env("LENSIQ_STORAGE_BASE_PATH")
        
        return StorageConfig(
            base_path=base_path,
            data_path=os.getenv("LENSIQ_DATA_PATH", f"{base_path}/data"),
            model_path=os.getenv("LENSIQ_MODEL_PATH", f"{base_path}/models"),
            log_path=os.getenv("LENSIQ_LOG_PATH", f"{base_path}/logs"),
            cache_path=os.getenv("LENSIQ_CACHE_PATH", f"{base_path}/cache"),
            backup_path=os.getenv("LENSIQ_BACKUP_PATH", f"{base_path}/backups"),
            max_file_size=int(os.getenv("LENSIQ_MAX_FILE_SIZE", str(100 * 1024 * 1024))),
            retention_days=int(os.getenv("LENSIQ_RETENTION_DAYS", "365")),
            enable_encryption=os.getenv("LENSIQ_STORAGE_ENCRYPTION", "true").lower() == "true"
        )
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration from environment."""
        return APIConfig(
            base_url=self._get_required_env("LENSIQ_API_BASE_URL"),
            version=os.getenv("LENSIQ_API_VERSION", "v1"),
            rate_limit_per_minute=int(os.getenv("LENSIQ_RATE_LIMIT_MINUTE", "1000")),
            rate_limit_per_hour=int(os.getenv("LENSIQ_RATE_LIMIT_HOUR", "10000")),
            timeout=int(os.getenv("LENSIQ_API_TIMEOUT", "30")),
            max_retries=int(os.getenv("LENSIQ_API_MAX_RETRIES", "3")),
            enable_swagger=os.getenv("LENSIQ_ENABLE_SWAGGER", "false").lower() == "true",
            enable_metrics=os.getenv("LENSIQ_ENABLE_METRICS", "true").lower() == "true"
        )
    
    def _load_ml_config(self) -> MLConfig:
        """Load ML configuration from environment."""
        return MLConfig(
            model_storage_path=self._get_required_env("LENSIQ_ML_MODEL_PATH"),
            feature_store_path=self._get_required_env("LENSIQ_ML_FEATURE_PATH"),
            training_data_path=self._get_required_env("LENSIQ_ML_TRAINING_PATH"),
            batch_size=int(os.getenv("LENSIQ_ML_BATCH_SIZE", "32")),
            max_epochs=int(os.getenv("LENSIQ_ML_MAX_EPOCHS", "100")),
            learning_rate=float(os.getenv("LENSIQ_ML_LEARNING_RATE", "0.001")),
            validation_split=float(os.getenv("LENSIQ_ML_VALIDATION_SPLIT", "0.2")),
            test_split=float(os.getenv("LENSIQ_ML_TEST_SPLIT", "0.1")),
            random_seed=int(os.getenv("LENSIQ_ML_RANDOM_SEED", "42")),
            enable_gpu=os.getenv("LENSIQ_ML_ENABLE_GPU", "false").lower() == "true",
            distributed_training=os.getenv("LENSIQ_ML_DISTRIBUTED", "false").lower() == "true"
        )
    
    def _load_data_sources_config(self) -> Dict[str, DataSourceConfig]:
        """Load data sources configuration from environment."""
        data_sources = {}
        
        # Refinitiv
        if os.getenv("REFINITIV_API_KEY"):
            data_sources["refinitiv"] = DataSourceConfig(
                name="refinitiv",
                provider="Refinitiv",
                base_url=self._get_required_env("REFINITIV_BASE_URL"),
                api_key=os.getenv("REFINITIV_API_KEY"),
                rate_limit=int(os.getenv("REFINITIV_RATE_LIMIT", "100")),
                timeout=int(os.getenv("REFINITIV_TIMEOUT", "30")),
                health_check_endpoint="/health"
            )
        
        # Bloomberg
        if os.getenv("BLOOMBERG_API_KEY"):
            data_sources["bloomberg"] = DataSourceConfig(
                name="bloomberg",
                provider="Bloomberg",
                base_url=self._get_required_env("BLOOMBERG_BASE_URL"),
                api_key=os.getenv("BLOOMBERG_API_KEY"),
                rate_limit=int(os.getenv("BLOOMBERG_RATE_LIMIT", "50")),
                timeout=int(os.getenv("BLOOMBERG_TIMEOUT", "30")),
                health_check_endpoint="/status"
            )
        
        # MSCI
        if os.getenv("MSCI_API_KEY"):
            data_sources["msci"] = DataSourceConfig(
                name="msci",
                provider="MSCI",
                base_url=self._get_required_env("MSCI_BASE_URL"),
                api_key=os.getenv("MSCI_API_KEY"),
                rate_limit=int(os.getenv("MSCI_RATE_LIMIT", "75")),
                timeout=int(os.getenv("MSCI_TIMEOUT", "30")),
                health_check_endpoint="/ping"
            )
        
        # Sustainalytics
        if os.getenv("SUSTAINALYTICS_API_KEY"):
            data_sources["sustainalytics"] = DataSourceConfig(
                name="sustainalytics",
                provider="Sustainalytics",
                base_url=self._get_required_env("SUSTAINALYTICS_BASE_URL"),
                api_key=os.getenv("SUSTAINALYTICS_API_KEY"),
                rate_limit=int(os.getenv("SUSTAINALYTICS_RATE_LIMIT", "60")),
                timeout=int(os.getenv("SUSTAINALYTICS_TIMEOUT", "30")),
                health_check_endpoint="/health"
            )
        
        return data_sources
    
    def _get_required_env(self, key: str, default: str = None) -> str:
        """
        Get required environment variable.
        
        Args:
            key: Environment variable key
            default: Default value (only for development)
            
        Returns:
            Environment variable value
            
        Raises:
            ValueError: If required variable is missing in production
        """
        value = os.getenv(key, default)
        
        if not value:
            if self.environment == "production":
                raise ValueError(f"Required environment variable missing: {key}")
            elif default is None:
                raise ValueError(f"Required environment variable missing: {key}")
        
        return value
    
    def _parse_list(self, value: str) -> List[str]:
        """Parse comma-separated list from environment variable."""
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]
    
    def _validate_configuration(self) -> None:
        """Validate complete configuration."""
        errors = []
        
        # Production-specific validations
        if self.environment == "production":
            # Ensure no default values in production
            if "development" in self.security.secret_key.lower():
                errors.append("Production secret key cannot contain 'development'")
            
            # Ensure HTTPS in production
            if not self.api.base_url.startswith("https://"):
                errors.append("Production API must use HTTPS")
            
            # Ensure data sources are configured
            if not self.data_sources:
                errors.append("At least one data source must be configured in production")
        
        if errors:
            error_msg = f"Configuration validation errors:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validation passed")
    
    def get_data_source(self, name: str) -> Optional[DataSourceConfig]:
        """Get data source configuration by name."""
        return self.data_sources.get(name)
    
    def get_enabled_data_sources(self) -> List[DataSourceConfig]:
        """Get list of enabled data sources."""
        return [config for config in self.data_sources.values() if config.enabled]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            "environment": self.environment,
            "database": {
                "adapter": self.database.adapter,
                "name": self.database.name,
                "ssl_enabled": self.database.ssl_enabled,
                "connection_timeout": self.database.connection_timeout,
                "pool_size": self.database.pool_size
            },
            "api": {
                "version": self.api.version,
                "rate_limit_per_minute": self.api.rate_limit_per_minute,
                "rate_limit_per_hour": self.api.rate_limit_per_hour,
                "timeout": self.api.timeout,
                "enable_swagger": self.api.enable_swagger,
                "enable_metrics": self.api.enable_metrics
            },
            "storage": {
                "retention_days": self.storage.retention_days,
                "max_file_size": self.storage.max_file_size,
                "enable_encryption": self.storage.enable_encryption
            },
            "ml": {
                "batch_size": self.ml.batch_size,
                "max_epochs": self.ml.max_epochs,
                "validation_split": self.ml.validation_split,
                "test_split": self.ml.test_split,
                "enable_gpu": self.ml.enable_gpu,
                "distributed_training": self.ml.distributed_training
            },
            "data_sources": {
                name: {
                    "provider": config.provider,
                    "enabled": config.enabled,
                    "rate_limit": config.rate_limit,
                    "timeout": config.timeout
                }
                for name, config in self.data_sources.items()
            }
        }


# Global configuration instance
_config_instance: Optional[ProductionConfig] = None


def get_config(environment: str = None) -> ProductionConfig:
    """
    Get global configuration instance (singleton pattern).
    
    Args:
        environment: Environment name
        
    Returns:
        Configuration instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ProductionConfig(environment)
    
    return _config_instance


def reload_config(environment: str = None) -> ProductionConfig:
    """
    Reload configuration (force new instance).
    
    Args:
        environment: Environment name
        
    Returns:
        New configuration instance
    """
    global _config_instance
    _config_instance = ProductionConfig(environment)
    return _config_instance

"""
Unified Configuration System for LensIQ

This module provides a simplified configuration system that eliminates
redundancy and over-engineering from the previous multi-config approach.
"""

import os
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    type: str  # 'mongodb' or 'mock'
    name: str = 'lensiq'


@dataclass
class APIConfig:
    """API keys configuration."""
    openai: Optional[str] = None
    refinitiv: Optional[str] = None
    bloomberg: Optional[str] = None
    msci: Optional[str] = None
    perplexity: Optional[str] = None


@dataclass
class AppConfig:
    """Application configuration."""
    debug: bool = False
    secret_key: str = 'dev-key-change-in-production'
    host: str = '0.0.0.0'
    port: int = 5000


class UnifiedConfig:
    """
    Simplified configuration system that eliminates redundancy.

    Features:
    - Single source of truth for all configuration
    - Automatic environment variable detection
    - Built-in validation and defaults
    - No over-engineered config classes
    """

    def __init__(self):
        """Initialize the unified configuration."""
        self.database = self._load_database_config()
        self.api = self._load_api_config()
        self.app = self._load_app_config()

        # Log configuration status
        self._log_config_status()

    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration with automatic detection."""

        # Try MongoDB first
        mongodb_uri = os.getenv('MONGODB_URI')
        if mongodb_uri:
            return DatabaseConfig(
                url=mongodb_uri,
                type='mongodb',
                name=os.getenv('MONGODB_DB', 'lensiq')
            )

        # Try MongoDB Atlas
        username = os.getenv('MONGODB_USERNAME')
        password = os.getenv('MONGODB_PASSWORD')
        if username and password:
            atlas_uri = (f"mongodb+srv://{username}:{password}@"
                        f"trendsense.m0vdz.mongodb.net/lensiq?"
                        f"retryWrites=true&w=majority")
            return DatabaseConfig(
                url=atlas_uri,
                type='mongodb',
                name='lensiq'
            )

        # Fall back to mock
        logger.warning("No database configuration found, using mock database")
        return DatabaseConfig(
            url='mock://localhost',
            type='mock'
        )

    def _load_api_config(self) -> APIConfig:
        """Load API configuration from environment."""
        return APIConfig(
            openai=os.getenv('OPENAI_API_KEY'),
            refinitiv=os.getenv('REFINITIV_API_KEY'),
            bloomberg=os.getenv('BLOOMBERG_API_KEY'),
            msci=os.getenv('MSCI_API_KEY'),
            perplexity=os.getenv('PERPLEXITY_API_KEY')
        )

    def _load_app_config(self) -> AppConfig:
        """Load application configuration."""
        return AppConfig(
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            secret_key=os.getenv('SECRET_KEY', 'dev-key-change-in-production'),
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', 5000))
        )

    def _log_config_status(self):
        """Log configuration status for debugging."""
        logger.info(f"Database: {self.database.type} ({self.database.url[:20]}...)")

        api_keys_configured = [
            name for name, key in {
                'OpenAI': self.api.openai,
                'Refinitiv': self.api.refinitiv,
                'Bloomberg': self.api.bloomberg,
                'MSCI': self.api.msci,
                'Perplexity': self.api.perplexity
            }.items() if key
        ]

        logger.info(f"API Keys configured: {', '.join(api_keys_configured) or 'None'}")
        logger.info(f"App mode: {'Debug' if self.app.debug else 'Production'}")

    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a service.

        Args:
            service: Service name ('openai', 'refinitiv', etc.)

        Returns:
            API key or None if not configured
        """
        return getattr(self.api, service.lower(), None)

    def is_api_configured(self, service: str) -> bool:
        """Check if an API service is configured."""
        return self.get_api_key(service) is not None

    def get_database_url(self) -> str:
        """Get database connection URL."""
        return self.database.url

    def get_database_type(self) -> str:
        """Get database type."""
        return self.database.type

    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.app.debug

    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask configuration dictionary."""
        return {
            'DEBUG': self.app.debug,
            'SECRET_KEY': self.app.secret_key,
            'HOST': self.app.host,
            'PORT': self.app.port
        }

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate configuration and return status.

        Returns:
            Dict with validation results
        """
        issues = []
        warnings = []

        # Check database configuration
        if self.database.type == 'mock':
            warnings.append("Using mock database - not suitable for production")

        # Check API keys
        if not any([self.api.openai, self.api.refinitiv, self.api.bloomberg]):
            warnings.append("No ESG data API keys configured - limited functionality")

        # Check secret key
        if self.app.secret_key == 'dev-key-change-in-production':
            if not self.app.debug:
                issues.append("Default secret key used in production mode")
            else:
                warnings.append("Using default secret key in debug mode")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'database_type': self.database.type,
            'api_keys_configured': len([k for k in [
                self.api.openai, self.api.refinitiv, self.api.bloomberg,
                self.api.msci, self.api.perplexity
            ] if k]),
            'debug_mode': self.app.debug
        }


# Global configuration instance
_config_instance: Optional[UnifiedConfig] = None


def get_config() -> UnifiedConfig:
    """Get the global configuration instance."""
    global _config_instance

    if _config_instance is None:
        _config_instance = UnifiedConfig()

    return _config_instance


def reload_config() -> UnifiedConfig:
    """Reload configuration from environment."""
    global _config_instance
    _config_instance = None
    return get_config()


# Convenience functions for backward compatibility
def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return get_config().database


def get_api_config() -> APIConfig:
    """Get API configuration."""
    return get_config().api


def get_app_config() -> AppConfig:
    """Get application configuration."""
    return get_config().app


# Environment detection helpers
def is_production() -> bool:
    """Check if running in production environment."""
    return not get_config().is_debug()


def is_development() -> bool:
    """Check if running in development environment."""
    return get_config().is_debug()


def has_real_database() -> bool:
    """Check if using a real database (not mock)."""
    return get_config().database.type != 'mock'


def has_api_keys() -> bool:
    """Check if any API keys are configured."""
    config = get_config()
    return any([
        config.api.openai,
        config.api.refinitiv,
        config.api.bloomberg,
        config.api.msci,
        config.api.perplexity
    ])

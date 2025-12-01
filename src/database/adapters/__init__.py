"""
Database Adapters Package

This package provides database adapters for LensIQ.
"""

import os
import logging

from .base_adapter import DatabaseAdapter
from .mongodb_adapter import MongoDBAdapter
from .dual_adapter import DualDatabaseAdapter

logger = logging.getLogger(__name__)

__all__ = [
    'DatabaseAdapter',
    'MongoDBAdapter',
    'DualDatabaseAdapter',
    'get_database_adapter'
]


def get_database_adapter(adapter_type: str = None,
                         **kwargs) -> DatabaseAdapter:
    """
    Get a database adapter based on configuration.

    Args:
        adapter_type: Type of adapter to use ('mongodb' or 'dual')
        **kwargs: Additional arguments for adapter initialization

    Returns:
        DatabaseAdapter instance
    """
    # Get adapter type from environment if not provided
    if adapter_type is None:
        adapter_type = os.getenv('DATABASE_ADAPTER', 'mongodb').lower()

    # Create and return the appropriate adapter
    if adapter_type == 'mongodb':
        logger.info("Using MongoDB adapter")
        return MongoDBAdapter(**kwargs)

    if adapter_type == 'dual':
        # Get primary adapter type from environment
        primary_type = os.getenv('PRIMARY_DATABASE_ADAPTER',
                                 'mongodb').lower()
        secondary_type = os.getenv('SECONDARY_DATABASE_ADAPTER',
                                   'mongodb').lower()
        logger.info("Using dual database adapter "
                    "(primary: %s, secondary: %s)",
                    primary_type, secondary_type)
        return DualDatabaseAdapter(primary_type, secondary_type)

    logger.warning("Unknown adapter type: %s, falling back to MongoDB",
                   adapter_type)
    return MongoDBAdapter(**kwargs)

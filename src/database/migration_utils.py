"""
Database Migration Utilities

This module provides utilities for exporting MongoDB data.
"""

import os
import json
import logging
from typing import List

from .adapters import MongoDBAdapter

# Configure logging
logger = logging.getLogger(__name__)


def export_mongodb_to_json(collections: List[str] = None, 
                          output_dir: str = 'data_export') -> bool:
    """
    Export MongoDB collections to JSON files.

    Args:
        collections: List of collection names to export (None for all)
        output_dir: Directory to save JSON files

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create MongoDB adapter
        mongodb = MongoDBAdapter()
        if not mongodb.connect():
            logger.error("Failed to connect to MongoDB")
            return False

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Get all collections if not specified
        if collections is None:
            # This is a simplified approach - in a real application, you would
            # get the list of collections from MongoDB
            collections = [
                'users',
                'trends',
                'companies',
                'products',
                'resources',
                'metrics',
                'timeseries_data',
                'graph_data',
                'vector_data'
            ]

        # Export each collection
        for collection_name in collections:
            logger.info(f"Exporting collection: {collection_name}")

            # Get documents from collection
            documents = mongodb.find(collection_name)
            if not documents:
                logger.warning(f"No documents found in collection: "
                              f"{collection_name}")
                continue

            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])

            # Write to JSON file
            output_file = os.path.join(output_dir, f"{collection_name}.json")
            with open(output_file, 'w') as f:
                json.dump(documents, f, default=str, indent=2)

            logger.info(f"Exported {len(documents)} documents from "
                       f"{collection_name} to {output_file}")

        mongodb.disconnect()
        return True

    except Exception as e:
        logger.error(f"Error exporting MongoDB to JSON: {str(e)}")
        return False

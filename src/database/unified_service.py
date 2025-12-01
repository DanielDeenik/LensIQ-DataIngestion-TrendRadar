"""
Unified Database Service for LensIQ

This module provides a simplified, single-responsibility database service
that eliminates redundancy and over-engineering from the previous multi-adapter system.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Try to import database libraries
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

logger = logging.getLogger(__name__)


class UnifiedDatabaseService:
    """
    Simplified database service that eliminates redundancy and
    over-engineering.

    Features:
    - Single connection pattern for all database operations
    - Automatic fallback from MongoDB to Mock
    - Simplified CRUD operations without unnecessary abstraction
    - Built-in error handling and logging
    """

    def __init__(self, connection_string: str = None):
        """Initialize the unified database service."""
        self.db = None
        self.db_type = None
        self.connected = False

        # Try to connect in order of preference: MongoDB -> Mock
        self._connect(connection_string)

    def _connect(self, connection_string: str = None) -> bool:
        """Connect to database with automatic fallback."""

        # Try MongoDB first
        if self._try_mongodb(connection_string):
            return True

        # Fall back to mock database
        self._use_mock_database()
        return True

    def _try_mongodb(self, connection_string: str = None) -> bool:
        """Try to connect to MongoDB."""
        if not MONGODB_AVAILABLE:
            logger.info("MongoDB not available, skipping")
            return False

        try:
            # Get connection string
            if not connection_string:
                connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/lensiq')

            # Try MongoDB Atlas if credentials are provided
            username = os.getenv('MONGODB_USERNAME')
            password = os.getenv('MONGODB_PASSWORD')

            if username and password:
                connection_string = f"mongodb+srv://{username}:{password}@trendsense.m0vdz.mongodb.net/lensiq?retryWrites=true&w=majority"

            # Connect to MongoDB
            client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')  # Test connection

            self.db = client.get_database()
            self.db_type = 'mongodb'
            self.connected = True
            logger.info(f"Connected to MongoDB: {connection_string}")
            return True

        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}")
            return False

    def _use_mock_database(self):
        """Use mock database as fallback."""
        self.db = MockDatabase()
        self.db_type = 'mock'
        self.connected = True
        logger.info("Using mock database")

    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self.connected

    def find(self, collection: str, query: Dict = None,
             sort: List = None, limit: int = 0, skip: int = 0) -> List[Dict]:
        """
        Find documents in a collection.

        Args:
            collection: Collection name
            query: Query filter (default: {})
            sort: Sort specification (default: None)
            limit: Maximum documents to return (default: 0 = no limit)
            skip: Number of documents to skip (default: 0)

        Returns:
            List of documents
        """
        if not self.connected:
            return []

        try:
            if self.db_type == 'mongodb':
                return self._mongodb_find(collection, query, sort, limit, skip)
            else:  # mock
                return self.db.find(collection, query, sort, limit, skip)
        except Exception as e:
            logger.error(f"Error finding documents in {collection}: {e}")
            return []

    def find_one(self, collection: str, query: Dict = None) -> Optional[Dict]:
        """
        Find a single document.

        Args:
            collection: Collection name
            query: Query filter

        Returns:
            Document or None
        """
        results = self.find(collection, query, limit=1)
        return results[0] if results else None

    def insert(self, collection: str, document: Dict) -> Optional[str]:
        """
        Insert a document.

        Args:
            collection: Collection name
            document: Document to insert

        Returns:
            Document ID or None
        """
        if not self.connected:
            return None

        try:
            # Add timestamp if not present
            if 'created_at' not in document:
                document['created_at'] = datetime.now().isoformat()

            if self.db_type == 'mongodb':
                result = self.db[collection].insert_one(document)
                return str(result.inserted_id)
            else:  # mock
                return self.db.insert(collection, document)
        except Exception as e:
            logger.error(f"Error inserting document into {collection}: {e}")
            return None

    def insert_many(self, collection: str, documents: List[Dict]) -> List[str]:
        """
        Insert multiple documents.

        Args:
            collection: Collection name
            documents: List of documents to insert

        Returns:
            List of document IDs
        """
        if not self.connected or not documents:
            return []

        try:
            # Add timestamps
            for doc in documents:
                if 'created_at' not in doc:
                    doc['created_at'] = datetime.now().isoformat()

            if self.db_type == 'mongodb':
                result = self.db[collection].insert_many(documents)
                return [str(id) for id in result.inserted_ids]
            else:  # mock
                return self.db.insert_many(collection, documents)
        except Exception as e:
            logger.error(f"Error inserting documents into {collection}: {e}")
            return []

    def update(self, collection: str, query: Dict, update: Dict) -> bool:
        """
        Update documents.

        Args:
            collection: Collection name
            query: Query filter
            update: Update operations

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            # Add timestamp
            update['updated_at'] = datetime.now().isoformat()

            if self.db_type == 'mongodb':
                result = self.db[collection].update_many(query,
                                                        {'$set': update})
                return result.modified_count > 0
            else:  # mock
                return self.db.update(collection, query, update)
        except Exception as e:
            logger.error(f"Error updating documents in {collection}: {e}")
            return False

    def delete(self, collection: str, query: Dict) -> bool:
        """
        Delete documents.

        Args:
            collection: Collection name
            query: Query filter

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            if self.db_type == 'mongodb':
                result = self.db[collection].delete_many(query)
                return result.deleted_count > 0
            else:  # mock
                return self.db.delete(collection, query)
        except Exception as e:
            logger.error(f"Error deleting documents from {collection}: {e}")
            return False

    def delete_many(self, collection: str, query: Dict) -> int:
        """
        Delete multiple documents and return count.

        Args:
            collection: Collection name
            query: Query filter

        Returns:
            Number of deleted documents
        """
        if not self.connected:
            return 0

        try:
            if self.db_type == 'mongodb':
                result = self.db[collection].delete_many(query)
                return result.deleted_count
            else:  # mock
                return self.db.delete_many(collection, query)
        except Exception as e:
            logger.error(f"Error deleting documents from {collection}: {e}")
            return 0

    def _mongodb_find(self, collection: str, query: Dict = None,
                      sort: List = None, limit: int = 0,
                      skip: int = 0) -> List[Dict]:
        """MongoDB-specific find implementation."""
        query = query or {}

        cursor = self.db[collection].find(query)

        if sort:
            cursor = cursor.sort(sort)
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)

        results = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            results.append(doc)

        return results


class MockDatabase:
    """Mock database for testing and fallback."""

    def __init__(self):
        self.collections = {}

    def find(self, collection: str, query: Dict = None,
             sort: List = None, limit: int = 0, skip: int = 0) -> List[Dict]:
        """Mock find implementation."""
        if collection not in self.collections:
            return []

        results = list(self.collections[collection].values())

        # Apply simple filtering
        if query:
            filtered = []
            for doc in results:
                match = True
                for key, value in query.items():
                    if key not in doc or doc[key] != value:
                        match = False
                        break
                if match:
                    filtered.append(doc)
            results = filtered

        # Apply sorting (simple)
        if sort:
            for field, direction in reversed(sort):
                results.sort(key=lambda x: x.get(field, ''), reverse=(direction == -1))

        # Apply skip and limit
        if skip > 0:
            results = results[skip:]
        if limit > 0:
            results = results[:limit]

        return results

    def insert(self, collection: str, document: Dict) -> str:
        """Mock insert implementation."""
        if collection not in self.collections:
            self.collections[collection] = {}

        doc_id = f"mock_{len(self.collections[collection])}"
        document['_id'] = doc_id
        self.collections[collection][doc_id] = document.copy()
        return doc_id

    def insert_many(self, collection: str, documents: List[Dict]) -> List[str]:
        """Mock insert many implementation."""
        ids = []
        for doc in documents:
            doc_id = self.insert(collection, doc)
            ids.append(doc_id)
        return ids

    def update(self, collection: str, query: Dict, update: Dict) -> bool:
        """Mock update implementation."""
        if collection not in self.collections:
            return False

        updated = False
        for doc in self.collections[collection].values():
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                doc.update(update)
                updated = True

        return updated

    def delete(self, collection: str, query: Dict) -> bool:
        """Mock delete implementation."""
        if collection not in self.collections:
            return False

        to_delete = []
        for doc_id, doc in self.collections[collection].items():
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                to_delete.append(doc_id)

        for doc_id in to_delete:
            del self.collections[collection][doc_id]

        return len(to_delete) > 0

    def delete_many(self, collection: str, query: Dict) -> int:
        """Mock delete many implementation."""
        if collection not in self.collections:
            return 0

        to_delete = []
        for doc_id, doc in self.collections[collection].items():
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                to_delete.append(doc_id)

        for doc_id in to_delete:
            del self.collections[collection][doc_id]

        return len(to_delete)


# Global service instance
_service_instance: Optional[UnifiedDatabaseService] = None


def get_database_service(connection_string: str = None) -> UnifiedDatabaseService:
    """Get the global database service instance."""
    global _service_instance

    if _service_instance is None:
        _service_instance = UnifiedDatabaseService(connection_string)

    return _service_instance


# Backward compatibility alias
database_service = get_database_service()

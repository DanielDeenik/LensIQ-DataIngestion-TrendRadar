"""
Database Command-Line Interface

This module provides a command-line interface for database operations.
"""

import argparse
import logging

from .adapters import MongoDBAdapter
from .migration_utils import export_mongodb_to_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection() -> bool:
    """
    Test connection to MongoDB database.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        logger.info("Testing MongoDB connection...")
        
        adapter = MongoDBAdapter()
        
        if adapter.connect():
            logger.info("Successfully connected to MongoDB")
            adapter.disconnect()
            return True
        else:
            logger.error("Failed to connect to MongoDB")
            return False
    except Exception as e:
        logger.error(f"Error testing MongoDB connection: {str(e)}")
        return False


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='Database CLI for LensIQ')
    subparsers = parser.add_subparsers(dest='command', 
                                      help='Available commands')
    
    # Test command
    test_parser = subparsers.add_parser('test', 
                                       help='Test database connection')
    
    # Export command
    export_parser = subparsers.add_parser('export', 
                                         help='Export MongoDB to JSON')
    export_parser.add_argument('--collections', nargs='+', 
                              help='Collections to export (default: all)')
    export_parser.add_argument('--output-dir', default='data_export', 
                              help='Output directory')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'test':
        test_connection()
    elif args.command == 'export':
        export_mongodb_to_json(args.collections, args.output_dir)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

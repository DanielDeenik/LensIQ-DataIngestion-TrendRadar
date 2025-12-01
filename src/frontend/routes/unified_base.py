"""
Unified Base Route Handler for LensIQ

This module provides a simplified, unified base class that eliminates
redundancy across route handlers and standardizes common patterns.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from flask import Blueprint, render_template, jsonify, request
from functools import wraps

from src.database.unified_service import get_database_service

logger = logging.getLogger(__name__)


class UnifiedRouteHandler:
    """
    Simplified base route handler that eliminates redundancy.
    
    Features:
    - Factory methods for standard CRUD routes
    - Unified error handling and logging
    - Automatic database connection checking
    - Standardized API response formats
    - Built-in template context management
    """
    
    def __init__(self, name: str, url_prefix: str = None):
        """Initialize the unified route handler."""
        self.name = name
        self.blueprint = Blueprint(name, __name__, url_prefix=url_prefix)
        self.database_service = get_database_service()
        
        # Standard template context that's always available
        self.base_context = {
            'active_nav': name,
            'database_available': self.database_service.is_connected()
        }
    
    def handle_errors(self, func):
        """Unified error handling decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                
                # Return JSON error for API endpoints
                if request.path.startswith('/api/'):
                    return jsonify({
                        'error': str(e),
                        'status': 'error'
                    }), 500
                
                # Return error page for regular routes
                return render_template('errors/500.html', error=str(e)), 500
        
        return wrapper
    
    def create_index_route(self, template: str, data_getters: Dict[str, Callable] = None,
                          page_title: str = None) -> Callable:
        """
        Factory method to create standard index routes.
        
        Args:
            template: Template file to render
            data_getters: Dict of data getter functions {key: function}
            page_title: Page title for the template
            
        Returns:
            Route function
        """
        data_getters = data_getters or {}
        
        @self.blueprint.route('/')
        @self.handle_errors
        def index():
            # Build context with base data
            context = self.base_context.copy()
            context['page_title'] = page_title or f"{self.name.title()} - LensIQ"
            
            # Add data from getters
            for key, getter in data_getters.items():
                try:
                    context[key] = getter()
                    logger.info(f"Retrieved {len(context[key]) if isinstance(context[key], list) else 1} {key}")
                except Exception as e:
                    logger.warning(f"Failed to get {key}: {e}")
                    context[key] = [] if 'list' in str(type(getter)).lower() else {}
            
            return render_template(template, **context)
        
        return index
    
    def create_api_route(self, endpoint: str, data_getter: Callable,
                        methods: List[str] = None) -> Callable:
        """
        Factory method to create standard API routes.
        
        Args:
            endpoint: API endpoint path (e.g., 'data', 'metrics')
            data_getter: Function to get the data
            methods: HTTP methods (default: ['GET'])
            
        Returns:
            Route function
        """
        methods = methods or ['GET']
        
        @self.blueprint.route(f'/api/{endpoint}', methods=methods)
        @self.handle_errors
        def api_endpoint():
            try:
                data = data_getter()
                return jsonify({
                    'data': data,
                    'status': 'success',
                    'count': len(data) if isinstance(data, list) else 1
                })
            except Exception as e:
                return jsonify({
                    'error': str(e),
                    'status': 'error'
                }), 500
        
        return api_endpoint
    
    def create_crud_routes(self, collection: str, template_dir: str,
                          page_title: str = None) -> Dict[str, Callable]:
        """
        Factory method to create standard CRUD routes.
        
        Args:
            collection: Database collection name
            template_dir: Template directory (e.g., 'lensiq', 'trends')
            page_title: Base page title
            
        Returns:
            Dict of route functions
        """
        routes = {}
        
        # Index route
        routes['index'] = self.create_index_route(
            template=f'{template_dir}/index.html',
            data_getters={
                'items': lambda: self.database_service.find(collection, limit=10),
                'total_count': lambda: len(self.database_service.find(collection))
            },
            page_title=page_title or f"{collection.title()} - LensIQ"
        )
        
        # API routes
        routes['api_list'] = self.create_api_route(
            endpoint=collection,
            data_getter=lambda: self.database_service.find(collection)
        )
        
        routes['api_create'] = self.create_api_create_route(collection)
        routes['api_update'] = self.create_api_update_route(collection)
        routes['api_delete'] = self.create_api_delete_route(collection)
        
        return routes
    
    def create_api_create_route(self, collection: str) -> Callable:
        """Create API route for creating items."""
        @self.blueprint.route(f'/api/{collection}', methods=['POST'])
        @self.handle_errors
        def api_create():
            data = request.json or {}
            
            if not data:
                return jsonify({
                    'error': 'No data provided',
                    'status': 'error'
                }), 400
            
            item_id = self.database_service.insert(collection, data)
            
            if item_id:
                return jsonify({
                    'id': item_id,
                    'status': 'success',
                    'message': f'{collection.rstrip("s").title()} created successfully'
                })
            else:
                return jsonify({
                    'error': f'Failed to create {collection.rstrip("s")}',
                    'status': 'error'
                }), 500
        
        return api_create
    
    def create_api_update_route(self, collection: str) -> Callable:
        """Create API route for updating items."""
        @self.blueprint.route(f'/api/{collection}/<item_id>', methods=['PUT'])
        @self.handle_errors
        def api_update(item_id: str):
            data = request.json or {}
            
            if not data:
                return jsonify({
                    'error': 'No data provided',
                    'status': 'error'
                }), 400
            
            success = self.database_service.update(
                collection, 
                {'_id': item_id}, 
                data
            )
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'{collection.rstrip("s").title()} updated successfully'
                })
            else:
                return jsonify({
                    'error': f'Failed to update {collection.rstrip("s")}',
                    'status': 'error'
                }), 500
        
        return api_update
    
    def create_api_delete_route(self, collection: str) -> Callable:
        """Create API route for deleting items."""
        @self.blueprint.route(f'/api/{collection}/<item_id>', methods=['DELETE'])
        @self.handle_errors
        def api_delete(item_id: str):
            success = self.database_service.delete(
                collection,
                {'_id': item_id}
            )
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'{collection.rstrip("s").title()} deleted successfully'
                })
            else:
                return jsonify({
                    'error': f'Failed to delete {collection.rstrip("s")}',
                    'status': 'error'
                }), 404
        
        return api_delete
    
    def create_health_check_route(self) -> Callable:
        """Create health check route for the service."""
        @self.blueprint.route('/api/health')
        @self.handle_errors
        def health_check():
            return jsonify({
                'service': self.name,
                'status': 'healthy',
                'database_connected': self.database_service.is_connected(),
                'database_type': self.database_service.db_type
            })
        
        return health_check
    
    def register_standard_routes(self, collection: str, template_dir: str,
                                page_title: str = None) -> None:
        """
        Register all standard routes for a service.
        
        Args:
            collection: Database collection name
            template_dir: Template directory
            page_title: Page title
        """
        # Create and register CRUD routes
        routes = self.create_crud_routes(collection, template_dir, page_title)
        
        # Routes are automatically registered when created
        # due to the blueprint decorators
        
        # Register health check
        self.create_health_check_route()
        
        logger.info(f"Registered standard routes for {self.name}")


class DataService:
    """
    Simplified data service for common operations.
    
    This eliminates the need for separate data getter methods
    in each route handler.
    """
    
    def __init__(self, database_service):
        self.db = database_service
    
    def get_stories(self, limit: int = 10) -> List[Dict]:
        """Get stories from database."""
        return self.db.find('stories', sort=[('created_at', -1)], limit=limit)
    
    def get_insights(self, limit: int = 10) -> List[Dict]:
        """Get insights from database."""
        return self.db.find('insights', sort=[('created_at', -1)], limit=limit)
    
    def get_trends(self, limit: int = 10) -> List[Dict]:
        """Get trends from database."""
        return self.db.find('trends', sort=[('score', -1)], limit=limit)
    
    def get_companies(self, limit: int = 10) -> List[Dict]:
        """Get companies from database."""
        return self.db.find('companies', sort=[('name', 1)], limit=limit)
    
    def get_funds(self, limit: int = 10) -> List[Dict]:
        """Get funds from database."""
        return self.db.find('funds', sort=[('aum', -1)], limit=limit)
    
    def get_metrics(self) -> Dict:
        """Get metrics from database."""
        metrics = self.db.find_one('metrics')
        return metrics or {}
    
    def create_story(self, story_data: Dict) -> Optional[str]:
        """Create a new story."""
        return self.db.insert('stories', story_data)
    
    def create_insight(self, insight_data: Dict) -> Optional[str]:
        """Create a new insight."""
        return self.db.insert('insights', insight_data)


# Global data service instance
_data_service_instance: Optional[DataService] = None


def get_data_service() -> DataService:
    """Get the global data service instance."""
    global _data_service_instance
    
    if _data_service_instance is None:
        _data_service_instance = DataService(get_database_service())
    
    return _data_service_instance

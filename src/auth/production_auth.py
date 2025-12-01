"""
Production Authentication System for LensIQ

This module provides enterprise-grade authentication and authorization with:
- API key authentication
- JWT token management
- Rate limiting
- Audit logging
- Security validation
"""

import os
import jwt
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from flask import request, jsonify, g, current_app
import redis
from dataclasses import dataclass

from ..config.production_config import get_config

logger = logging.getLogger(__name__)


@dataclass
class AuthUser:
    """Authenticated user information."""
    user_id: str
    api_key: str
    permissions: List[str]
    rate_limit: int
    organization: str
    tier: str = "standard"
    is_active: bool = True


class RateLimiter:
    """Redis-based rate limiter for API requests."""
    
    def __init__(self, redis_client=None):
        """Initialize rate limiter."""
        self.redis_client = redis_client
        if not self.redis_client:
            config = get_config()
            if hasattr(config, 'redis_url'):
                try:
                    self.redis_client = redis.from_url(config.redis_url)
                except Exception as e:
                    logger.warning(f"Redis connection failed: {e}")
                    self.redis_client = None
    
    def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """
        Check if request is allowed within rate limit.
        
        Args:
            key: Unique identifier for rate limiting
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        if not self.redis_client:
            # Fallback: allow all requests if Redis is not available
            return True
        
        try:
            current_time = int(time.time())
            window_start = current_time - window
            
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_requests = self.redis_client.zcard(key)
            
            if current_requests >= limit:
                return False
            
            # Add current request
            self.redis_client.zadd(key, {str(current_time): current_time})
            self.redis_client.expire(key, window)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Fallback: allow request if rate limiter fails
            return True


class ProductionAuth:
    """Production authentication system for LensIQ."""
    
    def __init__(self):
        """Initialize authentication system."""
        self.config = get_config()
        self.rate_limiter = RateLimiter()
        self._api_keys = self._load_api_keys()
        
    def _load_api_keys(self) -> Dict[str, AuthUser]:
        """Load API keys from secure storage."""
        # In production, this would load from a secure database
        # For now, we'll use environment variables
        api_keys = {}
        
        # Load from environment variables (format: LENSIQ_API_KEY_<USER_ID>)
        for key, value in os.environ.items():
            if key.startswith("LENSIQ_API_KEY_"):
                user_id = key.replace("LENSIQ_API_KEY_", "").lower()
                
                # Parse API key configuration
                # Format: api_key:permissions:rate_limit:organization:tier
                parts = value.split(":")
                if len(parts) >= 4:
                    api_key = parts[0]
                    permissions = parts[1].split(",") if parts[1] else []
                    rate_limit = int(parts[2]) if parts[2].isdigit() else 1000
                    organization = parts[3]
                    tier = parts[4] if len(parts) > 4 else "standard"
                    
                    api_keys[api_key] = AuthUser(
                        user_id=user_id,
                        api_key=api_key,
                        permissions=permissions,
                        rate_limit=rate_limit,
                        organization=organization,
                        tier=tier
                    )
        
        logger.info(f"Loaded {len(api_keys)} API keys")
        return api_keys
    
    def validate_api_key(self, api_key: str) -> Optional[AuthUser]:
        """
        Validate API key and return user information.
        
        Args:
            api_key: API key to validate
            
        Returns:
            AuthUser if valid, None otherwise
        """
        if not api_key:
            return None
        
        # Hash the API key for lookup (in production, store hashed keys)
        user = self._api_keys.get(api_key)
        
        if user and user.is_active:
            return user
        
        return None
    
    def generate_jwt_token(self, user: AuthUser, expires_in: int = None) -> str:
        """
        Generate JWT token for authenticated user.
        
        Args:
            user: Authenticated user
            expires_in: Token expiration in seconds
            
        Returns:
            JWT token string
        """
        if expires_in is None:
            expires_in = self.config.security.session_timeout
        
        payload = {
            'user_id': user.user_id,
            'organization': user.organization,
            'tier': user.tier,
            'permissions': user.permissions,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        
        return jwt.encode(
            payload,
            self.config.security.jwt_secret,
            algorithm='HS256'
        )
    
    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return payload.
        
        Args:
            token: JWT token to validate
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.config.security.jwt_secret,
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    def check_rate_limit(self, user: AuthUser, endpoint: str = None) -> bool:
        """
        Check if user is within rate limits.
        
        Args:
            user: Authenticated user
            endpoint: Specific endpoint (optional)
            
        Returns:
            True if within limits, False otherwise
        """
        # Create rate limit key
        key_parts = [f"rate_limit:{user.user_id}"]
        if endpoint:
            key_parts.append(f"endpoint:{endpoint}")
        
        rate_limit_key = ":".join(key_parts)
        
        # Check per-minute rate limit
        minute_allowed = self.rate_limiter.is_allowed(
            f"{rate_limit_key}:minute",
            user.rate_limit,
            60
        )
        
        # Check per-hour rate limit (10x the per-minute limit)
        hour_allowed = self.rate_limiter.is_allowed(
            f"{rate_limit_key}:hour",
            user.rate_limit * 10,
            3600
        )
        
        return minute_allowed and hour_allowed
    
    def check_permission(self, user: AuthUser, required_permission: str) -> bool:
        """
        Check if user has required permission.
        
        Args:
            user: Authenticated user
            required_permission: Required permission
            
        Returns:
            True if user has permission, False otherwise
        """
        if not required_permission:
            return True
        
        # Admin users have all permissions
        if "admin" in user.permissions:
            return True
        
        # Check specific permission
        return required_permission in user.permissions
    
    def log_auth_event(self, event_type: str, user_id: str = None, 
                      details: Dict[str, Any] = None) -> None:
        """
        Log authentication event for audit purposes.
        
        Args:
            event_type: Type of authentication event
            user_id: User ID (if applicable)
            details: Additional event details
        """
        if not self.config.security.enable_audit_logging:
            return
        
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'details': details or {}
        }
        
        # In production, this would write to a secure audit log
        logger.info(f"AUTH_AUDIT: {audit_entry}")


# Global authentication instance
_auth_instance: Optional[ProductionAuth] = None


def get_auth() -> ProductionAuth:
    """Get global authentication instance."""
    global _auth_instance
    
    if _auth_instance is None:
        _auth_instance = ProductionAuth()
    
    return _auth_instance


def require_api_key(f: Callable) -> Callable:
    """
    Decorator to require API key authentication.
    
    Usage:
        @require_api_key
        def protected_endpoint():
            # Access authenticated user via g.current_user
            return jsonify({'user': g.current_user.user_id})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = get_auth()
        config = get_config()
        
        # Get API key from header
        api_key = request.headers.get(config.security.api_key_header)
        
        if not api_key:
            auth.log_auth_event('api_key_missing')
            return jsonify({
                'error': 'API key required',
                'message': f'Please provide API key in {config.security.api_key_header} header'
            }), 401
        
        # Validate API key
        user = auth.validate_api_key(api_key)
        if not user:
            auth.log_auth_event('api_key_invalid', details={'api_key_prefix': api_key[:8]})
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 401
        
        # Check rate limits
        if not auth.check_rate_limit(user, request.endpoint):
            auth.log_auth_event('rate_limit_exceeded', user.user_id)
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }), 429
        
        # Store user in request context
        g.current_user = user
        
        # Log successful authentication
        auth.log_auth_event('api_key_authenticated', user.user_id)
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_permission(permission: str) -> Callable:
    """
    Decorator to require specific permission.
    
    Usage:
        @require_api_key
        @require_permission('esg_data_access')
        def protected_endpoint():
            return jsonify({'data': 'sensitive_data'})
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth = get_auth()
            
            # Check if user is authenticated
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Please authenticate first'
                }), 401
            
            # Check permission
            if not auth.check_permission(g.current_user, permission):
                auth.log_auth_event(
                    'permission_denied',
                    g.current_user.user_id,
                    {'required_permission': permission}
                )
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'Permission required: {permission}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_tier(min_tier: str) -> Callable:
    """
    Decorator to require minimum subscription tier.
    
    Usage:
        @require_api_key
        @require_tier('premium')
        def premium_endpoint():
            return jsonify({'data': 'premium_data'})
    """
    tier_hierarchy = {
        'basic': 1,
        'standard': 2,
        'premium': 3,
        'enterprise': 4
    }
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth = get_auth()
            
            # Check if user is authenticated
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Please authenticate first'
                }), 401
            
            # Check tier
            user_tier_level = tier_hierarchy.get(g.current_user.tier, 0)
            required_tier_level = tier_hierarchy.get(min_tier, 999)
            
            if user_tier_level < required_tier_level:
                auth.log_auth_event(
                    'tier_insufficient',
                    g.current_user.user_id,
                    {
                        'user_tier': g.current_user.tier,
                        'required_tier': min_tier
                    }
                )
                return jsonify({
                    'error': 'Insufficient subscription tier',
                    'message': f'Minimum tier required: {min_tier}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def get_current_user() -> Optional[AuthUser]:
    """Get current authenticated user from request context."""
    return getattr(g, 'current_user', None)


def create_api_key_hash(api_key: str) -> str:
    """Create secure hash of API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_secure_api_key(length: int = 32) -> str:
    """Generate cryptographically secure API key."""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

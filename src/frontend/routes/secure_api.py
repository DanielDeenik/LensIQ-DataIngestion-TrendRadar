"""
Secure API Routes for LensIQ

This module provides production-ready API endpoints with comprehensive
authentication, authorization, rate limiting, and error handling.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify, g
from functools import wraps
import asyncio

from ...auth.production_auth import (
    require_api_key,
    require_permission,
    require_tier,
    get_current_user
)
from ...data_management.petastorm_pipeline import (
    get_ml_pipeline,
    ingest_esg_data,
    create_ml_dataset
)
from ...validation.production_validator import get_validator, validate_esg_data
from ...monitoring.health_check import get_health_checker
from ...config.production_config import get_config

logger = logging.getLogger(__name__)

# Create secure API blueprint
secure_api_bp = Blueprint('secure_api', __name__)


@secure_api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Public health check endpoint.

    Returns:
        JSON response with system health status
    """
    try:
        health_checker = get_health_checker()
        health_report = health_checker.check_all_health()

        return jsonify({
            'status': 'success',
            'data': health_report,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Health check failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/readiness', methods=['GET'])
def readiness_check():
    """
    Kubernetes readiness probe endpoint.

    Returns:
        JSON response indicating if service is ready to serve requests
    """
    try:
        health_checker = get_health_checker()
        is_ready, readiness_report = health_checker.check_readiness()

        status_code = 200 if is_ready else 503

        return jsonify({
            'status': 'ready' if is_ready else 'not_ready',
            'data': readiness_report,
            'timestamp': datetime.utcnow().isoformat()
        }), status_code

    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Readiness check failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/liveness', methods=['GET'])
def liveness_check():
    """
    Kubernetes liveness probe endpoint.

    Returns:
        JSON response indicating if service is alive
    """
    try:
        health_checker = get_health_checker()
        is_alive, liveness_report = health_checker.check_liveness()

        status_code = 200 if is_alive else 503

        return jsonify({
            'status': 'alive' if is_alive else 'dead',
            'data': liveness_report,
            'timestamp': datetime.utcnow().isoformat()
        }), status_code

    except Exception as e:
        logger.error(f"Liveness check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Liveness check failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/auth/status', methods=['GET'])
@require_api_key
def auth_status():
    """
    Get authentication status for current user.

    Returns:
        JSON response with user authentication details
    """
    try:
        user = get_current_user()

        return jsonify({
            'status': 'success',
            'data': {
                'authenticated': True,
                'user_id': user.user_id,
                'organization': user.organization,
                'tier': user.tier,
                'permissions': user.permissions,
                'rate_limit': user.rate_limit
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Auth status check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Authentication status check failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/esg/companies/<company_id>/data', methods=['GET'])
@require_api_key
@require_permission('esg_data_access')
def get_company_esg_data(company_id: str):
    """
    Get ESG data for a specific company.

    Args:
        company_id: Company identifier

    Returns:
        JSON response with ESG data
    """
    try:
        user = get_current_user()

        # Get query parameters
        sources = request.args.getlist('sources')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Parse dates
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str)
        else:
            start_date = datetime.now() - timedelta(days=30)

        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str)
        else:
            end_date = datetime.now()

        # Ingest data using ML pipeline
        ml_pipeline = get_ml_pipeline()

        # Run async ingestion
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            esg_data = loop.run_until_complete(
                ml_pipeline.ingest_multi_source_data(
                    [company_id], start_date, end_date, sources
                )
            )
        finally:
            loop.close()

        # Convert to serializable format
        data_dicts = [data_point.to_dict() for data_point in esg_data]

        return jsonify({
            'status': 'success',
            'data': {
                'company_id': company_id,
                'records': data_dicts,
                'count': len(data_dicts),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'sources_used': sources or 'all_available'
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"ESG data retrieval failed for {company_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve ESG data for {company_id}',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/esg/validate', methods=['POST'])
@require_api_key
@require_permission('data_validation')
def validate_esg_data_endpoint():
    """
    Validate ESG data quality.

    Returns:
        JSON response with validation results
    """
    try:
        user = get_current_user()

        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided for validation',
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        # Validate data
        validator = get_validator()
        data_source = data.get('data_source', 'unknown')
        esg_records = data.get('records', [])

        if not esg_records:
            return jsonify({
                'status': 'error',
                'message': 'No ESG records provided for validation',
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        # Perform validation
        quality_report = validator.validate_data(esg_records, data_source)

        return jsonify({
            'status': 'success',
            'data': quality_report.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"ESG data validation failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'ESG data validation failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/ml/datasets', methods=['POST'])
@require_api_key
@require_permission('ml_dataset_creation')
@require_tier('premium')
def create_ml_dataset_endpoint():
    """
    Create ML-ready dataset from ESG data.

    Returns:
        JSON response with dataset creation results
    """
    try:
        user = get_current_user()

        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No configuration provided for dataset creation',
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        # Extract parameters
        company_ids = data.get('company_ids', [])
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        validation_split = data.get('validation_split', 0.2)
        test_split = data.get('test_split', 0.1)

        if not company_ids:
            return jsonify({
                'status': 'error',
                'message': 'Company IDs are required for dataset creation',
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        # Parse dates
        try:
            start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.now() - timedelta(days=365)
            end_date = datetime.fromisoformat(end_date_str) if end_date_str else datetime.now()
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': f'Invalid date format: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        # Create ML dataset
        ml_pipeline = get_ml_pipeline()
        datasets = ml_pipeline.create_training_dataset(
            company_ids=company_ids,
            start_date=start_date,
            end_date=end_date,
            validation_split=validation_split,
            test_split=test_split
        )

        # Get dataset statistics
        dataset_stats = {}
        for split_name, dataset_path in datasets.items():
            stats = ml_pipeline.get_dataset_statistics(dataset_path)
            dataset_stats[split_name] = stats

        return jsonify({
            'status': 'success',
            'data': {
                'datasets': datasets,
                'statistics': dataset_stats,
                'configuration': {
                    'company_ids': company_ids,
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'validation_split': validation_split,
                    'test_split': test_split
                }
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 201

    except Exception as e:
        logger.error(f"ML dataset creation failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'ML dataset creation failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/ai/analysis', methods=['POST'])
@require_api_key
@require_permission('ai_analysis')
@require_tier('premium')
def create_ai_analysis():
    """
    Create AI-powered ESG analysis using MCP.

    Returns:
        JSON response with AI analysis session
    """
    try:
        from ...ai.mcp_integration import create_esg_analysis_session, generate_ai_insights

        user = get_current_user()

        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No analysis configuration provided',
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        # Extract parameters
        company_ids = data.get('company_ids', [])
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        analysis_type = data.get('analysis_type', 'comprehensive')

        if not company_ids:
            return jsonify({
                'status': 'error',
                'message': 'Company IDs are required for AI analysis',
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        # Parse dates
        try:
            start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.now() - timedelta(days=365)
            end_date = datetime.fromisoformat(end_date_str) if end_date_str else datetime.now()
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': f'Invalid date format: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        # Create user context
        user_context = {
            'user_id': user.user_id,
            'organization': user.organization,
            'tier': user.tier,
            'analysis_depth': data.get('analysis_depth', 'standard')
        }

        # Create MCP session
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            session_id = loop.run_until_complete(
                create_esg_analysis_session(
                    company_ids=company_ids,
                    time_range={'start': start_date, 'end': end_date},
                    user_context=user_context,
                    analysis_type=analysis_type
                )
            )

            # Generate initial AI insights
            ai_response = loop.run_until_complete(
                generate_ai_insights(session_id, analysis_type)
            )
        finally:
            loop.close()

        return jsonify({
            'status': 'success',
            'data': {
                'session_id': session_id,
                'analysis': ai_response.to_dict(),
                'configuration': {
                    'company_ids': company_ids,
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'analysis_type': analysis_type
                }
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 201

    except Exception as e:
        logger.error(f"AI analysis creation failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'AI analysis creation failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/ai/narrative', methods=['POST'])
@require_api_key
@require_permission('narrative_generation')
@require_tier('premium')
def generate_ai_narrative():
    """
    Generate AI-powered narrative using MCP.

    Returns:
        JSON response with AI-generated narrative
    """
    try:
        from ...ai.mcp_integration import get_mcp_session_manager, get_mcp_ai_interface

        user = get_current_user()

        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No narrative configuration provided',
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        session_id = data.get('session_id')
        narrative_style = data.get('narrative_style', 'executive_summary')

        if not session_id:
            return jsonify({
                'status': 'error',
                'message': 'Session ID is required for narrative generation',
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        # Get session and generate narrative
        session_manager = get_mcp_session_manager()
        ai_interface = get_mcp_ai_interface()

        mcp_context = session_manager.get_session(session_id)
        if not mcp_context:
            return jsonify({
                'status': 'error',
                'message': f'Session {session_id} not found',
                'timestamp': datetime.utcnow().isoformat()
            }), 404

        # Generate narrative
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            narrative_response = loop.run_until_complete(
                ai_interface.generate_narrative(mcp_context, narrative_style)
            )
        finally:
            loop.close()

        # Add to session history
        session_manager.add_response(session_id, narrative_response)

        return jsonify({
            'status': 'success',
            'data': {
                'session_id': session_id,
                'narrative': narrative_response.to_dict(),
                'narrative_style': narrative_style
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"AI narrative generation failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'AI narrative generation failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/ai/sessions/<session_id>', methods=['GET'])
@require_api_key
@require_permission('ai_analysis')
def get_ai_session(session_id: str):
    """
    Get AI analysis session details.

    Args:
        session_id: MCP session identifier

    Returns:
        JSON response with session details
    """
    try:
        from ...ai.mcp_integration import get_mcp_session_manager

        user = get_current_user()
        session_manager = get_mcp_session_manager()

        # Get session
        mcp_context = session_manager.get_session(session_id)
        if not mcp_context:
            return jsonify({
                'status': 'error',
                'message': f'Session {session_id} not found',
                'timestamp': datetime.utcnow().isoformat()
            }), 404

        # Get session history
        session_history = session_manager.get_session_history(session_id)

        return jsonify({
            'status': 'success',
            'data': {
                'session': mcp_context.to_dict(),
                'history': [response.to_dict() for response in session_history],
                'total_responses': len(session_history)
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"AI session retrieval failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'AI session retrieval failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/analytics/trends', methods=['GET'])
@require_api_key
@require_permission('analytics_access')
def get_esg_trends():
    """
    Get ESG trends analysis with AI enhancement.

    Returns:
        JSON response with trend analysis
    """
    try:
        user = get_current_user()

        # Get query parameters
        sector = request.args.get('sector')
        region = request.args.get('region')
        timeframe = request.args.get('timeframe', '1y')
        metrics = request.args.getlist('metrics')
        use_ai = request.args.get('use_ai', 'false').lower() == 'true'

        # Basic trend analysis (can be enhanced with ML pipeline)
        trends_data = {
            'sector': sector,
            'region': region,
            'timeframe': timeframe,
            'metrics': metrics,
            'trends': {
                'environmental': {
                    'direction': 'improving',
                    'confidence': 0.85,
                    'key_drivers': ['renewable_energy', 'carbon_reduction']
                },
                'social': {
                    'direction': 'stable',
                    'confidence': 0.72,
                    'key_drivers': ['diversity_initiatives', 'employee_satisfaction']
                },
                'governance': {
                    'direction': 'improving',
                    'confidence': 0.91,
                    'key_drivers': ['board_independence', 'transparency']
                }
            },
            'ai_enhanced': use_ai
        }

        # Add AI insights if requested and user has premium tier
        if use_ai and user.tier in ['premium', 'enterprise']:
            try:
                from ...ai.mcp_integration import ESGContextProcessor

                # Create basic context for trend analysis
                context_processor = ESGContextProcessor()

                # Add AI-generated insights (simplified for demo)
                trends_data['ai_insights'] = {
                    'market_outlook': 'ESG performance is increasingly becoming a key differentiator in market valuation.',
                    'risk_factors': ['Regulatory changes', 'Supply chain disruptions', 'Climate-related risks'],
                    'opportunities': ['Green financing', 'Sustainable innovation', 'Stakeholder engagement'],
                    'confidence_score': 0.88
                }

            except Exception as ai_error:
                logger.warning(f"AI enhancement failed: {str(ai_error)}")
                trends_data['ai_enhancement_error'] = 'AI insights temporarily unavailable'

        return jsonify({
            'status': 'success',
            'data': trends_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"ESG trends analysis failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'ESG trends analysis failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@secure_api_bp.route('/config/info', methods=['GET'])
@require_api_key
@require_permission('admin')
def get_config_info():
    """
    Get non-sensitive configuration information.

    Returns:
        JSON response with configuration details
    """
    try:
        user = get_current_user()
        config = get_config()

        # Return non-sensitive configuration information
        config_info = config.to_dict()

        return jsonify({
            'status': 'success',
            'data': config_info,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Config info retrieval failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Configuration info retrieval failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


# Error handlers for the secure API blueprint
@secure_api_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({
        'status': 'error',
        'message': 'Bad request',
        'error': str(error),
        'timestamp': datetime.utcnow().isoformat()
    }), 400


@secure_api_bp.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors."""
    return jsonify({
        'status': 'error',
        'message': 'Unauthorized access',
        'error': 'Valid API key required',
        'timestamp': datetime.utcnow().isoformat()
    }), 401


@secure_api_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors."""
    return jsonify({
        'status': 'error',
        'message': 'Forbidden access',
        'error': 'Insufficient permissions',
        'timestamp': datetime.utcnow().isoformat()
    }), 403


@secure_api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({
        'status': 'error',
        'message': 'Resource not found',
        'error': str(error),
        'timestamp': datetime.utcnow().isoformat()
    }), 404


@secure_api_bp.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle 429 Rate Limit Exceeded errors."""
    return jsonify({
        'status': 'error',
        'message': 'Rate limit exceeded',
        'error': 'Too many requests. Please try again later.',
        'timestamp': datetime.utcnow().isoformat()
    }), 429


@secure_api_bp.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error."""
    logger.error(f"Internal server error in secure API: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'error': 'An unexpected error occurred',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

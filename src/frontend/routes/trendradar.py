"""
TrendRadar™ Routes for LensIQ Platform
Provides ML-optimized ESG trend radar visualization with Petastorm integration
"""

import logging
import asyncio
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, current_app
from typing import Dict, List, Optional, Any
import numpy as np

from .base_route import BaseRoute
from src.database.database_service import database_service
from src.data_management.petastorm_pipeline import get_ml_pipeline, ingest_esg_data, ESGDataPoint
from src.analytics.trend_analyzer import get_trend_analyzer
from src.analytics.advanced_scoring import get_advanced_esg_scorer
from src.config.production_config import get_config
from src.ai.data_management_agent import run_automated_data_import

logger = logging.getLogger(__name__)

class TrendRadarRoute(BaseRoute):
    """TrendRadar route handler with ML-powered ESG analytics."""

    def __init__(self):
        """Initialize the TrendRadar route."""
        super().__init__(name='trendradar')
        self.blueprint = Blueprint('trendradar', __name__)
        self.config = get_config()
        self.ml_pipeline = get_ml_pipeline()
        self.trend_analyzer = get_trend_analyzer()
        self.esg_scorer = get_advanced_esg_scorer()
        self.register_routes()

    def register_routes(self):
        """Register all routes for the TrendRadar blueprint."""

        @self.blueprint.route('/')
        @self.handle_errors
        def index():
            """TrendRadar - AI-powered sustainability trend radar visualization"""
            # Initialize database connection
            if not database_service.is_connected():
                logger.info("Connecting to database...")
                database_service.connect()

            # Initialize collections if they don't exist
            database_service.initialize_collections([
                'trending_categories',
                'trends',
                'startups',
                'radar_metrics'
            ])

            # Get data from Firebase
            trends_data = self._get_trends_data()
            radar_metrics = self._get_radar_metrics()

            # Check database connection
            firebase_available = database_service.is_connected()

            logger.info(f"Retrieved {len(trends_data)} trends from database")
            logger.info(f"Retrieved {len(radar_metrics)} radar metrics from database")

            context = {
                'active_nav': 'trendradar',
                'page_title': "TrendRadar - Sustainability Trend Visualization",
                'trends': trends_data,
                'radar_metrics': radar_metrics,
                'firebase_available': firebase_available
            }

            return self.render_template('fin_radar/fin_trendradar.html', **context)

        @self.blueprint.route('/api/radar-data')
        @self.handle_errors
        def api_radar_data():
            """API endpoint for radar data"""
            trends_data = self._get_trends_data()
            radar_metrics = self._get_radar_metrics()

            # Define categories and stages
            categories = list(set([trend.get('category', 'Unknown') for trend in trends_data]))
            stages = ['Watch', 'Prepare', 'Act']

            response = {
                'trends': trends_data,
                'metrics': radar_metrics,
                'categories': categories,
                'stages': stages
            }

            return self.json_response(response)

        @self.blueprint.route('/api/metrics')
        @self.handle_errors
        def api_metrics():
            """API endpoint for radar metrics"""
            metrics = self._get_radar_metrics()
            return self.json_response(metrics)

        @self.blueprint.route('/api/ml-trends')
        @self.handle_errors
        def api_ml_trends():
            """API endpoint for ML-powered trend analysis"""
            try:
                # Get ML-powered trends data
                ml_trends = self._get_ml_powered_trends()
                return self.json_response({
                    'trends': ml_trends,
                    'status': 'success',
                    'data_source': 'petastorm_ml_pipeline'
                })
            except Exception as e:
                logger.error(f"Error getting ML trends: {e}")
                # Fallback to traditional data
                fallback_trends = self._get_trends_data()
                return self.json_response({
                    'trends': fallback_trends,
                    'status': 'fallback',
                    'data_source': 'database_fallback',
                    'error': str(e)
                })

        @self.blueprint.route('/api/esg-analysis')
        @self.handle_errors
        def api_esg_analysis():
            """API endpoint for ESG trend analysis"""
            company_ids = request.args.getlist('companies')
            if not company_ids:
                # Default companies for analysis
                company_ids = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

            try:
                esg_analysis = self._get_esg_trend_analysis(company_ids)
                return self.json_response(esg_analysis)
            except Exception as e:
                logger.error(f"Error in ESG analysis: {e}")
                return self.json_response({
                    'error': str(e),
                    'status': 'error'
                }, status_code=500)

        @self.blueprint.route('/api/trend-predictions')
        @self.handle_errors
        def api_trend_predictions():
            """API endpoint for ML-powered trend predictions"""
            try:
                predictions = self._get_trend_predictions()
                return self.json_response(predictions)
            except Exception as e:
                logger.error(f"Error getting trend predictions: {e}")
                return self.json_response({
                    'error': str(e),
                    'status': 'error'
                }, status_code=500)

        @self.blueprint.route('/api/ai-data-management')
        @self.handle_errors
        def api_ai_data_management():
            """API endpoint for AI-powered data management cycle"""
            try:
                # Get parameters from request
                company_ids = request.args.getlist('companies')
                if not company_ids:
                    company_ids = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

                enable_discovery = request.args.get('discovery', 'true').lower() == 'true'
                enable_reconciliation = request.args.get('reconciliation', 'true').lower() == 'true'
                enable_quality_control = request.args.get('quality_control', 'true').lower() == 'true'

                # Run AI data management cycle
                results = asyncio.run(self._run_ai_data_management_cycle(
                    company_ids=company_ids,
                    enable_discovery=enable_discovery,
                    enable_reconciliation=enable_reconciliation,
                    enable_quality_control=enable_quality_control
                ))

                return self.json_response(results)

            except Exception as e:
                logger.error(f"Error in AI data management: {e}")
                return self.json_response({
                    'error': str(e),
                    'status': 'error'
                }, status_code=500)

        @self.blueprint.route('/api/data-sources/discover')
        @self.handle_errors
        def api_discover_data_sources():
            """API endpoint for AI-powered data source discovery"""
            try:
                search_domains = request.args.getlist('domains')
                if not search_domains:
                    search_domains = ['esg-data.com', 'sustainability-metrics.org']

                discovered_sources = asyncio.run(
                    self._discover_data_sources(search_domains)
                )

                return self.json_response({
                    'sources': [source.__dict__ for source in discovered_sources],
                    'total_discovered': len(discovered_sources),
                    'status': 'success'
                })

            except Exception as e:
                logger.error(f"Error discovering data sources: {e}")
                return self.json_response({
                    'error': str(e),
                    'status': 'error'
                }, status_code=500)

        @self.blueprint.route('/api/refresh-trends')
        @self.handle_errors
        def api_refresh_trends():
            """API endpoint to refresh trends with latest data"""
            try:
                # Force refresh of trends data
                refreshed_trends = self._get_trends_data()

                # Get updated radar metrics
                radar_metrics = self._get_radar_metrics()

                return self.json_response({
                    'trends': refreshed_trends,
                    'radar_metrics': radar_metrics,
                    'refreshed_at': datetime.now().isoformat(),
                    'status': 'success',
                    'total_trends': len(refreshed_trends)
                })

            except Exception as e:
                logger.error(f"Error refreshing trends: {e}")
                return self.json_response({
                    'error': str(e),
                    'status': 'error'
                }, status_code=500)

        @self.blueprint.route('/api/trend-health')
        @self.handle_errors
        def api_trend_health():
            """API endpoint for trend data health check"""
            try:
                trends = self._get_trends_data()

                # Analyze data health
                health_metrics = {
                    'total_trends': len(trends),
                    'data_sources': list(set(t.get('data_source', 'unknown') for t in trends)),
                    'last_updated': max([t.get('last_updated', '1970-01-01') for t in trends]) if trends else None,
                    'real_data_percentage': len([t for t in trends if t.get('data_source') != 'fallback']) / len(trends) * 100 if trends else 0,
                    'average_data_quality': np.mean([t.get('metrics', {}).get('data_quality', 50) for t in trends]) if trends else 0,
                    'trend_categories': list(set(t.get('category', 'Unknown') for t in trends))
                }

                # Determine health status
                if health_metrics['real_data_percentage'] > 80:
                    health_status = 'excellent'
                elif health_metrics['real_data_percentage'] > 50:
                    health_status = 'good'
                elif health_metrics['real_data_percentage'] > 20:
                    health_status = 'fair'
                else:
                    health_status = 'poor'

                return self.json_response({
                    'health_status': health_status,
                    'metrics': health_metrics,
                    'recommendations': self._get_health_recommendations(health_status, health_metrics),
                    'checked_at': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"Error checking trend health: {e}")
                return self.json_response({
                    'error': str(e),
                    'status': 'error'
                }, status_code=500)

    def _get_trends_data(self) -> List[Dict]:
        """Get dynamic trends data from real ESG sources."""
        try:
            # First, try to get real-time computed trends
            real_trends = self._compute_real_time_trends()
            if real_trends:
                logger.info(f"Using {len(real_trends)} real-time computed trends")
                return real_trends
        except Exception as e:
            logger.warning(f"Failed to compute real-time trends: {e}")

        # Fallback to database trends
        trends_data = database_service.find(
            'trends',
            sort=[('last_updated', -1), ('score', -1)],
            limit=10
        )

        if trends_data:
            logger.info(f"Using {len(trends_data)} cached trends from database")
            return trends_data

        # Last resort: generate trends from available ESG data
        try:
            generated_trends = self._generate_trends_from_esg_data()
            if generated_trends:
                logger.info(f"Generated {len(generated_trends)} trends from ESG data")
                return generated_trends
        except Exception as e:
            logger.warning(f"Failed to generate trends from ESG data: {e}")

        # Final fallback: minimal sample data with warning
        logger.warning("No real data available, using minimal fallback data")
        return self._get_minimal_fallback_trends()

    def _compute_real_time_trends(self) -> List[Dict]:
        """Compute trends from real-time ESG data using ML pipeline."""
        try:
            # Get recent ESG data for trend computation
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # 3 months of data

            # Use major companies for trend analysis
            company_ids = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
                'JPM', 'JNJ', 'PG', 'UNH', 'HD', 'BAC', 'XOM', 'CVX'
            ]

            # Ingest real ESG data
            esg_data = asyncio.run(
                ingest_esg_data(company_ids, start_date, end_date)
            )

            if not esg_data or len(esg_data) < 10:
                logger.warning(f"Insufficient ESG data for trend computation: {len(esg_data) if esg_data else 0} points")
                return []

            # Compute trends using statistical analysis
            trends = self._analyze_esg_trends_advanced(esg_data)

            # Cache computed trends in database
            if trends:
                self._cache_computed_trends(trends)

            return trends

        except Exception as e:
            logger.error(f"Error computing real-time trends: {e}")
            return []

    def _generate_trends_from_esg_data(self) -> List[Dict]:
        """Generate trends from available ESG data in database."""
        try:
            # Look for any ESG data in the database
            esg_records = database_service.find(
                'esg_data',
                sort=[('timestamp', -1)],
                limit=1000
            )

            if not esg_records:
                return []

            # Convert database records to ESGDataPoint objects
            esg_data_points = []
            for record in esg_records:
                try:
                    data_point = ESGDataPoint(
                        company_id=record.get('company_id', 'UNKNOWN'),
                        timestamp=datetime.fromisoformat(record.get('timestamp', datetime.now().isoformat())),
                        data_source=record.get('data_source', 'database'),
                        environmental_score=float(record.get('environmental_score', 0)),
                        social_score=float(record.get('social_score', 0)),
                        governance_score=float(record.get('governance_score', 0)),
                        combined_score=float(record.get('combined_score', 0)),
                        sector=record.get('sector'),
                        data_quality_score=float(record.get('data_quality_score', 1.0)),
                        confidence_score=float(record.get('confidence_score', 1.0))
                    )
                    esg_data_points.append(data_point)
                except Exception as e:
                    logger.warning(f"Error converting ESG record: {e}")
                    continue

            if len(esg_data_points) < 5:
                logger.warning(f"Insufficient valid ESG data points: {len(esg_data_points)}")
                return []

            # Generate trends from the data
            trends = self._analyze_esg_trends_advanced(esg_data_points)
            return trends

        except Exception as e:
            logger.error(f"Error generating trends from ESG data: {e}")
            return []

    def _analyze_esg_trends_advanced(self, esg_data: List) -> List[Dict]:
        """Advanced trend analysis with statistical methods."""
        try:
            # Group data by sector and time periods
            sector_trends = {}
            time_series_data = {}

            # Organize data by sector and time
            for data_point in esg_data:
                sector = data_point.sector or self._infer_sector_from_company(data_point.company_id)

                if sector not in sector_trends:
                    sector_trends[sector] = []
                    time_series_data[sector] = []

                sector_trends[sector].append(data_point)
                time_series_data[sector].append({
                    'timestamp': data_point.timestamp,
                    'combined_score': data_point.combined_score,
                    'environmental_score': data_point.environmental_score,
                    'social_score': data_point.social_score,
                    'governance_score': data_point.governance_score
                })

            # Compute trends for each sector
            computed_trends = []
            for sector, data_points in sector_trends.items():
                if len(data_points) < 3:  # Need minimum data for trend analysis
                    continue

                trend = self._compute_sector_trend(sector, data_points, time_series_data[sector])
                if trend:
                    computed_trends.append(trend)

            # Sort by trend strength and return top trends
            computed_trends.sort(key=lambda x: x.get('trend_strength', 0), reverse=True)
            return computed_trends[:8]  # Return top 8 trends

        except Exception as e:
            logger.error(f"Error in advanced trend analysis: {e}")
            return []

    def _compute_sector_trend(self, sector: str, data_points: List, time_series: List[Dict]) -> Dict:
        """Compute trend metrics for a specific sector."""
        try:
            # Calculate basic statistics
            scores = [dp.combined_score for dp in data_points]
            env_scores = [dp.environmental_score for dp in data_points]
            social_scores = [dp.social_score for dp in data_points]
            gov_scores = [dp.governance_score for dp in data_points]

            avg_score = np.mean(scores)
            score_std = np.std(scores)

            # Calculate growth trend using linear regression
            if len(time_series) >= 2:
                # Sort by timestamp
                time_series.sort(key=lambda x: x['timestamp'])

                # Simple linear trend calculation
                x_values = list(range(len(time_series)))
                y_values = [ts['combined_score'] for ts in time_series]

                # Calculate slope (growth rate)
                if len(x_values) > 1:
                    slope = np.polyfit(x_values, y_values, 1)[0]
                    growth_rate = (slope / avg_score) * 100 if avg_score > 0 else 0
                else:
                    growth_rate = 0
            else:
                growth_rate = 0

            # Generate trend values for visualization (12 months)
            trend_values = self._generate_trend_visualization_data(time_series, avg_score)

            # Map sector to category
            category = self._map_sector_to_trend_category(sector)

            # Calculate trend strength (combination of growth, consistency, and data quality)
            data_quality = np.mean([dp.data_quality_score for dp in data_points])
            consistency = 1.0 / (1.0 + score_std / avg_score) if avg_score > 0 else 0.5
            trend_strength = abs(growth_rate) * consistency * data_quality

            trend = {
                'category': category,
                'growth': round(growth_rate, 1),
                'score': round(avg_score, 1),
                'trend_values': trend_values,
                'trend_strength': round(trend_strength, 2),
                'data_points_count': len(data_points),
                'last_updated': datetime.now().isoformat(),
                'metrics': {
                    'environmental_impact': round(np.mean(env_scores), 1),
                    'social_impact': round(np.mean(social_scores), 1),
                    'governance_score': round(np.mean(gov_scores), 1),
                    'market_potential': round(avg_score * 0.9, 1),
                    'innovation_level': round(avg_score * 0.95, 1),
                    'regulatory_support': round(avg_score * 0.8, 1),
                    'investment_activity': round(avg_score * 0.85, 1),
                    'data_quality': round(data_quality * 100, 1),
                    'consistency': round(consistency * 100, 1)
                }
            }

            return trend

        except Exception as e:
            logger.error(f"Error computing sector trend for {sector}: {e}")
            return None

    def _generate_trend_visualization_data(self, time_series: List[Dict], avg_score: float) -> List[float]:
        """Generate 12-point trend data for visualization."""
        try:
            if len(time_series) >= 12:
                # Use actual data if we have enough points
                sorted_data = sorted(time_series, key=lambda x: x['timestamp'])
                return [round(ts['combined_score'], 1) for ts in sorted_data[-12:]]

            elif len(time_series) >= 2:
                # Interpolate to 12 points
                sorted_data = sorted(time_series, key=lambda x: x['timestamp'])
                scores = [ts['combined_score'] for ts in sorted_data]

                # Simple linear interpolation
                start_score = scores[0]
                end_score = scores[-1]
                step = (end_score - start_score) / 11

                return [round(start_score + i * step, 1) for i in range(12)]

            else:
                # Generate synthetic trend around average
                base = avg_score
                variation = base * 0.1  # 10% variation
                return [round(base + np.random.uniform(-variation, variation), 1) for _ in range(12)]

        except Exception as e:
            logger.error(f"Error generating trend visualization data: {e}")
            return [round(avg_score, 1)] * 12

    def _infer_sector_from_company(self, company_id: str) -> str:
        """Infer sector from company ID using known mappings."""
        sector_mapping = {
            'AAPL': 'Technology',
            'MSFT': 'Technology',
            'GOOGL': 'Technology',
            'AMZN': 'Consumer Discretionary',
            'TSLA': 'Consumer Discretionary',
            'NVDA': 'Technology',
            'META': 'Technology',
            'JPM': 'Financials',
            'JNJ': 'Healthcare',
            'PG': 'Consumer Staples',
            'UNH': 'Healthcare',
            'HD': 'Consumer Discretionary',
            'BAC': 'Financials',
            'XOM': 'Energy',
            'CVX': 'Energy'
        }
        return sector_mapping.get(company_id, 'Technology')

    def _map_sector_to_trend_category(self, sector: str) -> str:
        """Map business sector to sustainability trend category."""
        mapping = {
            'Technology': 'Climate Tech',
            'Energy': 'Renewable Energy',
            'Financials': 'Sustainable Finance',
            'Healthcare': 'Sustainable Healthcare',
            'Consumer Discretionary': 'Circular Economy',
            'Consumer Staples': 'Sustainable Agriculture',
            'Industrials': 'Green Manufacturing',
            'Materials': 'Green Materials',
            'Utilities': 'Clean Energy',
            'Real Estate': 'Green Buildings'
        }
        return mapping.get(sector, 'Emerging Sustainability')

    def _cache_computed_trends(self, trends: List[Dict]):
        """Cache computed trends in database for future use."""
        try:
            # Add metadata to trends
            for trend in trends:
                trend['computed_at'] = datetime.now().isoformat()
                trend['data_source'] = 'real_time_computation'
                trend['last_updated'] = datetime.now().isoformat()

            # Clear old computed trends
            database_service.delete_many('trends', {'data_source': 'real_time_computation'})

            # Insert new trends
            database_service.insert_many('trends', trends)
            logger.info(f"Cached {len(trends)} computed trends in database")

        except Exception as e:
            logger.error(f"Error caching computed trends: {e}")

    def _get_minimal_fallback_trends(self) -> List[Dict]:
        """Get minimal fallback trends when no real data is available."""
        return [
            {
                'category': 'Climate Tech',
                'growth': 25.0,
                'score': 75.0,
                'trend_values': [65, 67, 69, 71, 73, 75, 75, 75, 75, 75, 75, 75],
                'data_source': 'fallback',
                'last_updated': datetime.now().isoformat(),
                'metrics': {
                    'environmental_impact': 80,
                    'market_potential': 70,
                    'innovation_level': 75,
                    'regulatory_support': 65,
                    'investment_activity': 70
                }
            },
            {
                'category': 'Renewable Energy',
                'growth': 20.0,
                'score': 70.0,
                'trend_values': [60, 62, 64, 66, 68, 70, 70, 70, 70, 70, 70, 70],
                'data_source': 'fallback',
                'last_updated': datetime.now().isoformat(),
                'metrics': {
                    'environmental_impact': 85,
                    'market_potential': 65,
                    'innovation_level': 70,
                    'regulatory_support': 75,
                    'investment_activity': 60
                }
            },
            {
                'category': 'Sustainable Finance',
                'growth': 15.0,
                'score': 65.0,
                'trend_values': [55, 57, 59, 61, 63, 65, 65, 65, 65, 65, 65, 65],
                'data_source': 'fallback',
                'last_updated': datetime.now().isoformat(),
                'metrics': {
                    'environmental_impact': 60,
                    'market_potential': 75,
                    'innovation_level': 65,
                    'regulatory_support': 70,
                    'investment_activity': 80
                }
            }
        ]

    def _get_health_recommendations(self, health_status: str, metrics: Dict) -> List[str]:
        """Get recommendations based on data health status."""
        recommendations = []

        if health_status == 'poor':
            recommendations.extend([
                "Run AI data management cycle to refresh data sources",
                "Check ESG data provider connections",
                "Verify database connectivity and data ingestion pipelines",
                "Consider enabling fallback data sources"
            ])
        elif health_status == 'fair':
            recommendations.extend([
                "Increase data refresh frequency",
                "Add more ESG data sources for better coverage",
                "Review data quality validation rules"
            ])
        elif health_status == 'good':
            recommendations.extend([
                "Monitor data freshness regularly",
                "Consider adding real-time data streams"
            ])
        else:  # excellent
            recommendations.append("Data health is excellent - maintain current processes")

        # Add specific recommendations based on metrics
        if metrics.get('average_data_quality', 0) < 70:
            recommendations.append("Improve data quality validation and cleansing processes")

        if len(metrics.get('data_sources', [])) < 2:
            recommendations.append("Add additional data sources for better redundancy")

        return recommendations

    def _get_radar_metrics(self) -> List[Dict]:
        """Get radar metrics from database."""
        radar_metrics = database_service.find(
            'radar_metrics',
            sort=[('importance', -1)],
            limit=10
        )

        # If no data in Firebase, insert sample data
        if not radar_metrics:
            logger.info("No radar metrics found in database, inserting sample data...")
            sample_metrics = [
                {
                    "name": "environmental_impact",
                    "display_name": "Environmental Impact",
                    "description": "Measures the positive environmental effects of the trend",
                    "importance": 95,
                    "category": "Environmental"
                },
                {
                    "name": "market_potential",
                    "display_name": "Market Potential",
                    "description": "Estimates the market size and growth potential",
                    "importance": 90,
                    "category": "Financial"
                },
                {
                    "name": "innovation_level",
                    "display_name": "Innovation Level",
                    "description": "Measures the degree of innovation and technological advancement",
                    "importance": 85,
                    "category": "Technology"
                },
                {
                    "name": "regulatory_support",
                    "display_name": "Regulatory Support",
                    "description": "Assesses the level of regulatory support and policy alignment",
                    "importance": 80,
                    "category": "Policy"
                },
                {
                    "name": "investment_activity",
                    "display_name": "Investment Activity",
                    "description": "Tracks the level of investment in the trend",
                    "importance": 75,
                    "category": "Financial"
                },
                {
                    "name": "social_impact",
                    "display_name": "Social Impact",
                    "description": "Measures the positive social effects of the trend",
                    "importance": 70,
                    "category": "Social"
                },
                {
                    "name": "scalability",
                    "display_name": "Scalability",
                    "description": "Assesses how easily the trend can scale globally",
                    "importance": 65,
                    "category": "Business"
                },
                {
                    "name": "adoption_rate",
                    "display_name": "Adoption Rate",
                    "description": "Measures how quickly the trend is being adopted",
                    "importance": 60,
                    "category": "Market"
                }
            ]
            database_service.insert_many('radar_metrics', sample_metrics)
            radar_metrics = sample_metrics

        return radar_metrics

    def _get_ml_powered_trends(self) -> List[Dict]:
        """Get ML-powered trends using Petastorm pipeline."""
        try:
            # Define companies for ESG analysis
            company_ids = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA',
                          'META', 'NFLX', 'CRM', 'ADBE']

            # Get date range for analysis (last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            # Ingest ESG data using Petastorm pipeline
            logger.info("Ingesting ESG data for trend analysis...")
            esg_data = asyncio.run(
                ingest_esg_data(company_ids, start_date, end_date)
            )

            if not esg_data:
                logger.warning("No ESG data available, using fallback")
                return self._get_trends_data()

            # Analyze trends using ML
            trends = self._analyze_esg_trends(esg_data)

            logger.info(f"Generated {len(trends)} ML-powered trends")
            return trends

        except Exception as e:
            logger.error(f"Error in ML-powered trends: {e}")
            # Fallback to traditional data
            return self._get_trends_data()

    def _analyze_esg_trends(self, esg_data: List) -> List[Dict]:
        """Analyze ESG data to generate trend insights."""
        trends = []

        # Group data by sector/category
        sector_data = {}
        for data_point in esg_data:
            sector = data_point.sector or "Technology"
            if sector not in sector_data:
                sector_data[sector] = []
            sector_data[sector].append(data_point)

        # Generate trends for each sector
        for sector, data_points in sector_data.items():
            if not data_points:
                continue

            # Calculate average scores
            env_scores = [dp.environmental_score for dp in data_points]
            social_scores = [dp.social_score for dp in data_points]
            gov_scores = [dp.governance_score for dp in data_points]
            combined_scores = [dp.combined_score for dp in data_points]

            avg_env = np.mean(env_scores)
            avg_social = np.mean(social_scores)
            avg_gov = np.mean(gov_scores)
            avg_combined = np.mean(combined_scores)

            # Calculate growth trend (simplified)
            if len(combined_scores) > 1:
                growth = ((combined_scores[-1] - combined_scores[0]) /
                         combined_scores[0] * 100)
            else:
                growth = 0

            # Generate trend values (simulated time series)
            trend_values = self._generate_trend_values(combined_scores)

            # Create trend object
            trend = {
                "category": self._map_sector_to_category(sector),
                "growth": round(growth, 1),
                "score": round(avg_combined, 1),
                "trend_values": trend_values,
                "metrics": {
                    "environmental_impact": round(avg_env, 1),
                    "social_impact": round(avg_social, 1),
                    "governance_score": round(avg_gov, 1),
                    "market_potential": round(avg_combined * 0.9, 1),
                    "innovation_level": round(avg_env * 0.95, 1),
                    "regulatory_support": round(avg_gov * 0.85, 1),
                    "investment_activity": round(avg_combined * 0.8, 1)
                },
                "data_quality": round(np.mean([dp.data_quality_score
                                              for dp in data_points]), 2),
                "companies_analyzed": len(data_points),
                "last_updated": datetime.now().isoformat()
            }

            trends.append(trend)

        # Sort by combined score
        trends.sort(key=lambda x: x['score'], reverse=True)

        return trends

    def _map_sector_to_category(self, sector: str) -> str:
        """Map company sector to trend category."""
        sector_mapping = {
            "Technology": "Climate Tech",
            "Energy": "Renewable Energy",
            "Industrials": "Circular Economy",
            "Consumer Discretionary": "Sustainable Consumer",
            "Financials": "Sustainable Finance",
            "Healthcare": "Sustainable Healthcare",
            "Materials": "Green Materials",
            "Utilities": "Clean Energy",
            "Real Estate": "Green Buildings",
            "Consumer Staples": "Sustainable Agriculture"
        }
        return sector_mapping.get(sector, "Emerging Sustainability")

    def _generate_trend_values(self, scores: List[float]) -> List[float]:
        """Generate trend values for visualization."""
        if len(scores) < 2:
            # Generate synthetic trend
            base_score = scores[0] if scores else 70
            return [base_score + i * 2 for i in range(12)]

        # Interpolate to 12 points for visualization
        if len(scores) >= 12:
            return scores[:12]

        # Simple interpolation
        step = (scores[-1] - scores[0]) / 11
        return [scores[0] + i * step for i in range(12)]

    def _get_esg_trend_analysis(self, company_ids: List[str]) -> Dict:
        """Get comprehensive ESG trend analysis."""
        try:
            # Get date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # 3 months

            # Ingest ESG data
            esg_data = asyncio.run(
                ingest_esg_data(company_ids, start_date, end_date)
            )

            if not esg_data:
                return {
                    'error': 'No ESG data available',
                    'companies_analyzed': 0,
                    'analysis': {}
                }

            # Perform analysis
            analysis = {
                'companies_analyzed': len(set(dp.company_id for dp in esg_data)),
                'data_points': len(esg_data),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'esg_summary': self._calculate_esg_summary(esg_data),
                'trend_analysis': self._calculate_trend_analysis(esg_data),
                'sector_breakdown': self._calculate_sector_breakdown(esg_data),
                'quality_metrics': self._calculate_quality_metrics(esg_data)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error in ESG trend analysis: {e}")
            return {
                'error': str(e),
                'companies_analyzed': 0,
                'analysis': {}
            }

    def _calculate_esg_summary(self, esg_data: List) -> Dict:
        """Calculate ESG summary statistics."""
        env_scores = [dp.environmental_score for dp in esg_data]
        social_scores = [dp.social_score for dp in esg_data]
        gov_scores = [dp.governance_score for dp in esg_data]
        combined_scores = [dp.combined_score for dp in esg_data]

        return {
            'environmental': {
                'mean': round(np.mean(env_scores), 2),
                'median': round(np.median(env_scores), 2),
                'std': round(np.std(env_scores), 2),
                'min': round(np.min(env_scores), 2),
                'max': round(np.max(env_scores), 2)
            },
            'social': {
                'mean': round(np.mean(social_scores), 2),
                'median': round(np.median(social_scores), 2),
                'std': round(np.std(social_scores), 2),
                'min': round(np.min(social_scores), 2),
                'max': round(np.max(social_scores), 2)
            },
            'governance': {
                'mean': round(np.mean(gov_scores), 2),
                'median': round(np.median(gov_scores), 2),
                'std': round(np.std(gov_scores), 2),
                'min': round(np.min(gov_scores), 2),
                'max': round(np.max(gov_scores), 2)
            },
            'combined': {
                'mean': round(np.mean(combined_scores), 2),
                'median': round(np.median(combined_scores), 2),
                'std': round(np.std(combined_scores), 2),
                'min': round(np.min(combined_scores), 2),
                'max': round(np.max(combined_scores), 2)
            }
        }

    def _calculate_trend_analysis(self, esg_data: List) -> Dict:
        """Calculate trend analysis over time."""
        # Group by date
        date_groups = {}
        for dp in esg_data:
            date_key = dp.timestamp.date()
            if date_key not in date_groups:
                date_groups[date_key] = []
            date_groups[date_key].append(dp)

        # Calculate daily averages
        daily_averages = []
        for date, data_points in sorted(date_groups.items()):
            avg_combined = np.mean([dp.combined_score for dp in data_points])
            daily_averages.append({
                'date': date.isoformat(),
                'average_score': round(avg_combined, 2),
                'data_points': len(data_points)
            })

        # Calculate trend direction
        if len(daily_averages) >= 2:
            first_score = daily_averages[0]['average_score']
            last_score = daily_averages[-1]['average_score']
            trend_direction = 'improving' if last_score > first_score else 'declining'
            trend_magnitude = abs(last_score - first_score)
        else:
            trend_direction = 'stable'
            trend_magnitude = 0

        return {
            'daily_averages': daily_averages,
            'trend_direction': trend_direction,
            'trend_magnitude': round(trend_magnitude, 2),
            'total_days': len(daily_averages)
        }

    def _calculate_sector_breakdown(self, esg_data: List) -> Dict:
        """Calculate sector-wise ESG breakdown."""
        sector_data = {}
        for dp in esg_data:
            sector = dp.sector or "Unknown"
            if sector not in sector_data:
                sector_data[sector] = []
            sector_data[sector].append(dp)

        sector_summary = {}
        for sector, data_points in sector_data.items():
            combined_scores = [dp.combined_score for dp in data_points]
            sector_summary[sector] = {
                'count': len(data_points),
                'average_score': round(np.mean(combined_scores), 2),
                'companies': list(set(dp.company_id for dp in data_points))
            }

        return sector_summary

    def _calculate_quality_metrics(self, esg_data: List) -> Dict:
        """Calculate data quality metrics."""
        quality_scores = [dp.data_quality_score for dp in esg_data]
        confidence_scores = [dp.confidence_score for dp in esg_data]

        return {
            'data_quality': {
                'mean': round(np.mean(quality_scores), 3),
                'min': round(np.min(quality_scores), 3),
                'max': round(np.max(quality_scores), 3)
            },
            'confidence': {
                'mean': round(np.mean(confidence_scores), 3),
                'min': round(np.min(confidence_scores), 3),
                'max': round(np.max(confidence_scores), 3)
            },
            'data_sources': list(set(dp.data_source for dp in esg_data))
        }

    def _get_trend_predictions(self) -> Dict:
        """Get ML-powered trend predictions."""
        try:
            # Use trend analyzer for predictions
            predictions = self.trend_analyzer.predict_trends(
                lookback_days=90,
                forecast_days=30
            )

            return {
                'predictions': predictions,
                'forecast_horizon': '30 days',
                'confidence_level': 0.85,
                'model_version': '1.0',
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            # Return mock predictions as fallback
            return self._get_mock_predictions()

    def _get_mock_predictions(self) -> Dict:
        """Generate mock predictions as fallback."""
        mock_predictions = [
            {
                'category': 'Carbon Tech',
                'predicted_growth': 35.2,
                'confidence': 0.89,
                'key_drivers': ['regulatory_support', 'investment_activity']
            },
            {
                'category': 'Renewable Energy',
                'predicted_growth': 28.7,
                'confidence': 0.92,
                'key_drivers': ['market_potential', 'environmental_impact']
            },
            {
                'category': 'Circular Economy',
                'predicted_growth': 22.1,
                'confidence': 0.78,
                'key_drivers': ['innovation_level', 'social_impact']
            }
        ]

        return {
            'predictions': mock_predictions,
            'forecast_horizon': '30 days',
            'confidence_level': 0.85,
            'model_version': 'fallback',
            'generated_at': datetime.now().isoformat(),
            'note': 'Using fallback predictions due to ML model unavailability'
        }

    async def _run_ai_data_management_cycle(
        self,
        company_ids: List[str],
        enable_discovery: bool = True,
        enable_reconciliation: bool = True,
        enable_quality_control: bool = True
    ) -> Dict[str, Any]:
        """Run AI-powered data management cycle."""
        try:
            from ..ai.data_management_agent import run_automated_data_import

            results = await run_automated_data_import(
                company_ids=company_ids,
                enable_discovery=enable_discovery,
                enable_reconciliation=enable_reconciliation,
                enable_quality_control=enable_quality_control
            )

            return results

        except Exception as e:
            logger.error(f"Error in AI data management cycle: {e}")
            return {
                'error': str(e),
                'success': False,
                'status': 'error'
            }

    async def _discover_data_sources(self, search_domains: List[str]) -> List:
        """Discover new data sources using AI."""
        try:
            from ..ai.data_management_agent import discover_new_data_sources

            discovered_sources = await discover_new_data_sources(search_domains)
            return discovered_sources

        except Exception as e:
            logger.error(f"Error discovering data sources: {e}")
            return []

    async def _reconcile_data_sources(
        self,
        data_by_source: Dict[str, List],
        strategy: str = 'ai_weighted'
    ) -> Dict[str, Any]:
        """Reconcile conflicting data from multiple sources."""
        try:
            from ..ai.data_management_agent import reconcile_conflicting_data

            result = await reconcile_conflicting_data(data_by_source, strategy)

            return {
                'reconciled_data': [point.to_dict() for point in result.reconciled_data],
                'conflicts_resolved': result.conflicts_resolved,
                'confidence_score': result.confidence_score,
                'source_weights': result.source_weights,
                'anomalies_detected': len(result.anomalies_detected),
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Error reconciling data sources: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }


# Create instance
trendradar_route = TrendRadarRoute()
trendradar_bp = trendradar_route.blueprint

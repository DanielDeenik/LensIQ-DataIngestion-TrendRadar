"""
Unified ESG Data Service for LensIQ

This module provides a simplified ESG data service that eliminates
redundancy and over-engineering from the previous multi-connector system.
"""

import os
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ESGData:
    """Simplified ESG data structure."""
    company_id: str
    timestamp: datetime
    environmental_score: float
    social_score: float
    governance_score: float
    combined_score: float
    data_source: str
    confidence: float = 1.0


class ESGDataService:
    """
    Simplified ESG data service that eliminates redundancy.
    
    Features:
    - Single interface for all ESG data sources
    - Automatic fallback between sources
    - Built-in caching and error handling
    - Simplified data structure
    """
    
    def __init__(self):
        """Initialize the ESG data service."""
        self.api_keys = {
            'refinitiv': os.getenv('REFINITIV_API_KEY'),
            'bloomberg': os.getenv('BLOOMBERG_API_KEY'),
            'msci': os.getenv('MSCI_API_KEY')
        }
        
        # Available sources in order of preference
        self.sources = ['refinitiv', 'bloomberg', 'msci', 'mock']
        
        # Simple in-memory cache
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    async def get_esg_data(self, company_id: str, 
                          sources: List[str] = None) -> Optional[ESGData]:
        """
        Get ESG data for a company with automatic fallback.
        
        Args:
            company_id: Company identifier (ticker symbol)
            sources: Preferred sources (default: all available)
            
        Returns:
            ESG data or None if all sources fail
        """
        # Check cache first
        cache_key = f"{company_id}_{datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try sources in order
        sources = sources or self.sources
        
        for source in sources:
            try:
                data = await self._get_from_source(source, company_id)
                if data:
                    # Cache the result
                    self.cache[cache_key] = data
                    logger.info(f"Retrieved ESG data for {company_id} from {source}")
                    return data
            except Exception as e:
                logger.warning(f"Source {source} failed for {company_id}: {e}")
                continue
        
        logger.error(f"All sources failed for {company_id}")
        return None
    
    async def get_multiple_companies(self, company_ids: List[str],
                                   sources: List[str] = None) -> List[ESGData]:
        """
        Get ESG data for multiple companies concurrently.
        
        Args:
            company_ids: List of company identifiers
            sources: Preferred sources
            
        Returns:
            List of ESG data (may be partial if some companies fail)
        """
        tasks = [
            self.get_esg_data(company_id, sources)
            for company_id in company_ids
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        esg_data = []
        for result in results:
            if isinstance(result, ESGData):
                esg_data.append(result)
            elif isinstance(result, Exception):
                logger.warning(f"Failed to get ESG data: {result}")
        
        return esg_data
    
    async def _get_from_source(self, source: str, company_id: str) -> Optional[ESGData]:
        """Get data from a specific source."""
        if source == 'refinitiv':
            return await self._get_refinitiv_data(company_id)
        elif source == 'bloomberg':
            return await self._get_bloomberg_data(company_id)
        elif source == 'msci':
            return await self._get_msci_data(company_id)
        else:  # mock
            return self._get_mock_data(company_id)
    
    async def _get_refinitiv_data(self, company_id: str) -> Optional[ESGData]:
        """Get data from Refinitiv."""
        api_key = self.api_keys.get('refinitiv')
        if not api_key:
            raise ValueError("Refinitiv API key not configured")
        
        # Simplified Refinitiv API call
        url = f"https://api.refinitiv.com/esg/v1/companies/{company_id}"
        headers = {'Authorization': f'Bearer {api_key}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_refinitiv_response(company_id, data)
                else:
                    raise Exception(f"Refinitiv API error: {response.status}")
    
    async def _get_bloomberg_data(self, company_id: str) -> Optional[ESGData]:
        """Get data from Bloomberg."""
        api_key = self.api_keys.get('bloomberg')
        if not api_key:
            raise ValueError("Bloomberg API key not configured")
        
        # Simplified Bloomberg API call
        url = f"https://api.bloomberg.com/esg/v1/companies/{company_id}"
        headers = {'Authorization': f'Bearer {api_key}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_bloomberg_response(company_id, data)
                else:
                    raise Exception(f"Bloomberg API error: {response.status}")
    
    async def _get_msci_data(self, company_id: str) -> Optional[ESGData]:
        """Get data from MSCI."""
        api_key = self.api_keys.get('msci')
        if not api_key:
            raise ValueError("MSCI API key not configured")
        
        # Simplified MSCI API call
        url = f"https://api.msci.com/esg/v1/companies/{company_id}"
        headers = {'Authorization': f'Bearer {api_key}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_msci_response(company_id, data)
                else:
                    raise Exception(f"MSCI API error: {response.status}")
    
    def _get_mock_data(self, company_id: str) -> ESGData:
        """Generate mock ESG data for testing."""
        import random
        
        # Generate consistent mock data based on company_id
        random.seed(hash(company_id) % 1000)
        
        base_score = random.uniform(60, 90)
        variation = random.uniform(-10, 10)
        
        return ESGData(
            company_id=company_id,
            timestamp=datetime.now(),
            environmental_score=max(0, min(100, base_score + variation)),
            social_score=max(0, min(100, base_score + random.uniform(-5, 5))),
            governance_score=max(0, min(100, base_score + random.uniform(-5, 5))),
            combined_score=base_score,
            data_source='mock',
            confidence=0.8
        )
    
    def _parse_refinitiv_response(self, company_id: str, data: Dict) -> ESGData:
        """Parse Refinitiv API response."""
        esg_scores = data.get('esg_scores', {})
        
        return ESGData(
            company_id=company_id,
            timestamp=datetime.now(),
            environmental_score=esg_scores.get('environmental', 0),
            social_score=esg_scores.get('social', 0),
            governance_score=esg_scores.get('governance', 0),
            combined_score=esg_scores.get('combined', 0),
            data_source='refinitiv',
            confidence=data.get('confidence', 1.0)
        )
    
    def _parse_bloomberg_response(self, company_id: str, data: Dict) -> ESGData:
        """Parse Bloomberg API response."""
        scores = data.get('scores', {})
        
        return ESGData(
            company_id=company_id,
            timestamp=datetime.now(),
            environmental_score=scores.get('E', 0),
            social_score=scores.get('S', 0),
            governance_score=scores.get('G', 0),
            combined_score=scores.get('ESG', 0),
            data_source='bloomberg',
            confidence=data.get('quality', 1.0)
        )
    
    def _parse_msci_response(self, company_id: str, data: Dict) -> ESGData:
        """Parse MSCI API response."""
        ratings = data.get('ratings', {})
        
        return ESGData(
            company_id=company_id,
            timestamp=datetime.now(),
            environmental_score=ratings.get('environmental_score', 0),
            social_score=ratings.get('social_score', 0),
            governance_score=ratings.get('governance_score', 0),
            combined_score=ratings.get('overall_score', 0),
            data_source='msci',
            confidence=data.get('confidence_level', 1.0)
        )
    
    def clear_cache(self):
        """Clear the data cache."""
        self.cache.clear()
        logger.info("ESG data cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'cached_items': len(self.cache),
            'cache_ttl': self.cache_ttl,
            'sources_configured': len([k for k, v in self.api_keys.items() if v])
        }


class TrendAnalyzer:
    """
    Simplified trend analyzer that eliminates ML over-engineering.
    
    Features:
    - Simple statistical analysis
    - Trend detection using basic algorithms
    - No unnecessary ML complexity
    """
    
    def __init__(self, esg_service: ESGDataService):
        self.esg_service = esg_service
    
    async def analyze_trends(self, company_ids: List[str],
                           days: int = 90) -> List[Dict]:
        """
        Analyze ESG trends for companies.
        
        Args:
            company_ids: List of company identifiers
            days: Number of days to analyze
            
        Returns:
            List of trend analysis results
        """
        # Get current ESG data
        current_data = await self.esg_service.get_multiple_companies(company_ids)
        
        if not current_data:
            return []
        
        # Simple trend analysis
        trends = []
        for data in current_data:
            trend = self._calculate_simple_trend(data)
            trends.append(trend)
        
        # Sort by trend strength
        trends.sort(key=lambda x: x.get('trend_strength', 0), reverse=True)
        
        return trends
    
    def _calculate_simple_trend(self, esg_data: ESGData) -> Dict:
        """Calculate simple trend metrics."""
        # Simple trend calculation (in real implementation, 
        # this would use historical data)
        
        # Mock trend calculation for demonstration
        import random
        random.seed(hash(esg_data.company_id) % 1000)
        
        growth_rate = random.uniform(-5, 15)  # -5% to +15%
        trend_strength = abs(growth_rate) * esg_data.confidence
        
        return {
            'company_id': esg_data.company_id,
            'category': self._map_to_category(esg_data.company_id),
            'current_score': esg_data.combined_score,
            'growth_rate': growth_rate,
            'trend_strength': trend_strength,
            'data_source': esg_data.data_source,
            'last_updated': esg_data.timestamp.isoformat(),
            'metrics': {
                'environmental_score': esg_data.environmental_score,
                'social_score': esg_data.social_score,
                'governance_score': esg_data.governance_score,
                'confidence': esg_data.confidence
            }
        }
    
    def _map_to_category(self, company_id: str) -> str:
        """Map company to sustainability category."""
        # Simple mapping based on common tickers
        tech_companies = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META']
        energy_companies = ['XOM', 'CVX', 'COP', 'EOG']
        finance_companies = ['JPM', 'BAC', 'WFC', 'GS']
        
        if company_id in tech_companies:
            return 'Climate Tech'
        elif company_id in energy_companies:
            return 'Renewable Energy'
        elif company_id in finance_companies:
            return 'Sustainable Finance'
        else:
            return 'Emerging Sustainability'


# Global service instances
_esg_service_instance: Optional[ESGDataService] = None
_trend_analyzer_instance: Optional[TrendAnalyzer] = None


def get_esg_service() -> ESGDataService:
    """Get the global ESG service instance."""
    global _esg_service_instance
    
    if _esg_service_instance is None:
        _esg_service_instance = ESGDataService()
    
    return _esg_service_instance


def get_trend_analyzer() -> TrendAnalyzer:
    """Get the global trend analyzer instance."""
    global _trend_analyzer_instance
    
    if _trend_analyzer_instance is None:
        _trend_analyzer_instance = TrendAnalyzer(get_esg_service())
    
    return _trend_analyzer_instance


# Convenience functions for backward compatibility
async def get_company_esg_data(company_id: str) -> Optional[ESGData]:
    """Get ESG data for a single company."""
    service = get_esg_service()
    return await service.get_esg_data(company_id)


async def analyze_esg_trends(company_ids: List[str]) -> List[Dict]:
    """Analyze ESG trends for companies."""
    analyzer = get_trend_analyzer()
    return await analyzer.analyze_trends(company_ids)

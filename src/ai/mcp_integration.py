"""
Model Context Protocol (MCP) Integration for LensIQ

This module integrates MCP to provide enhanced AI capabilities for ESG analysis,
including context-aware data processing, intelligent insights generation,
and seamless AI model interactions.
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass, field
from pathlib import Path
import aiohttp
import openai

from ..config.production_config import get_config
from ..data_management.petastorm_pipeline import get_ml_pipeline, ESGDataPoint
from ..validation.production_validator import get_validator

logger = logging.getLogger(__name__)


@dataclass
class MCPContext:
    """MCP context for AI model interactions."""
    session_id: str
    user_id: str
    organization: str
    context_type: str  # 'esg_analysis', 'trend_detection', 'narrative_generation'
    data_sources: List[str] = field(default_factory=list)
    time_range: Dict[str, datetime] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'organization': self.organization,
            'context_type': self.context_type,
            'data_sources': self.data_sources,
            'time_range': {
                k: v.isoformat() if isinstance(v, datetime) else v
                for k, v in self.time_range.items()
            },
            'parameters': self.parameters,
            'metadata': self.metadata
        }


@dataclass
class MCPResponse:
    """MCP response from AI model."""
    session_id: str
    response_type: str  # 'analysis', 'insight', 'narrative', 'recommendation'
    content: Dict[str, Any]
    confidence_score: float
    sources_used: List[str]
    processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'response_type': self.response_type,
            'content': self.content,
            'confidence_score': self.confidence_score,
            'sources_used': self.sources_used,
            'processing_time_ms': self.processing_time_ms,
            'timestamp': self.timestamp.isoformat()
        }


class ESGContextProcessor:
    """Process ESG data to create rich context for AI models."""
    
    def __init__(self):
        """Initialize ESG context processor."""
        self.config = get_config()
        self.ml_pipeline = get_ml_pipeline()
        self.validator = get_validator()
    
    async def create_esg_context(self, 
                               company_ids: List[str],
                               context_type: str,
                               time_range: Dict[str, datetime],
                               user_context: Dict[str, Any]) -> MCPContext:
        """
        Create rich ESG context for AI model interactions.
        
        Args:
            company_ids: List of company identifiers
            context_type: Type of analysis context
            time_range: Time range for data
            user_context: User-specific context
            
        Returns:
            MCP context object
        """
        # Generate session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Ingest relevant ESG data
        start_date = time_range.get('start', datetime.now() - timedelta(days=365))
        end_date = time_range.get('end', datetime.now())
        
        esg_data = await self.ml_pipeline.ingest_multi_source_data(
            company_ids, start_date, end_date
        )
        
        # Process data for context
        context_data = self._process_esg_data_for_context(esg_data, context_type)
        
        # Create MCP context
        mcp_context = MCPContext(
            session_id=session_id,
            user_id=user_context.get('user_id', 'unknown'),
            organization=user_context.get('organization', 'unknown'),
            context_type=context_type,
            data_sources=list(set(data.data_source for data in esg_data)),
            time_range=time_range,
            parameters={
                'company_ids': company_ids,
                'data_quality_threshold': 0.8,
                'analysis_depth': user_context.get('analysis_depth', 'standard')
            },
            metadata={
                'total_records': len(esg_data),
                'data_quality_avg': sum(d.data_quality_score for d in esg_data) / len(esg_data) if esg_data else 0,
                'context_data': context_data
            }
        )
        
        return mcp_context
    
    def _process_esg_data_for_context(self, 
                                    esg_data: List[ESGDataPoint], 
                                    context_type: str) -> Dict[str, Any]:
        """Process ESG data to create context-specific information."""
        if not esg_data:
            return {}
        
        # Basic statistics
        env_scores = [d.environmental_score for d in esg_data if d.environmental_score is not None]
        social_scores = [d.social_score for d in esg_data if d.social_score is not None]
        gov_scores = [d.governance_score for d in esg_data if d.governance_score is not None]
        
        context_data = {
            'score_statistics': {
                'environmental': {
                    'mean': sum(env_scores) / len(env_scores) if env_scores else 0,
                    'min': min(env_scores) if env_scores else 0,
                    'max': max(env_scores) if env_scores else 0,
                    'count': len(env_scores)
                },
                'social': {
                    'mean': sum(social_scores) / len(social_scores) if social_scores else 0,
                    'min': min(social_scores) if social_scores else 0,
                    'max': max(social_scores) if social_scores else 0,
                    'count': len(social_scores)
                },
                'governance': {
                    'mean': sum(gov_scores) / len(gov_scores) if gov_scores else 0,
                    'min': min(gov_scores) if gov_scores else 0,
                    'max': max(gov_scores) if gov_scores else 0,
                    'count': len(gov_scores)
                }
            },
            'data_coverage': {
                'companies': len(set(d.company_id for d in esg_data)),
                'sources': len(set(d.data_source for d in esg_data)),
                'time_span_days': (max(d.timestamp for d in esg_data) - min(d.timestamp for d in esg_data)).days if len(esg_data) > 1 else 0
            }
        }
        
        # Context-specific processing
        if context_type == 'trend_detection':
            context_data['trend_indicators'] = self._extract_trend_indicators(esg_data)
        elif context_type == 'narrative_generation':
            context_data['narrative_elements'] = self._extract_narrative_elements(esg_data)
        elif context_type == 'risk_assessment':
            context_data['risk_factors'] = self._extract_risk_factors(esg_data)
        
        return context_data
    
    def _extract_trend_indicators(self, esg_data: List[ESGDataPoint]) -> Dict[str, Any]:
        """Extract trend indicators from ESG data."""
        # Sort data by timestamp
        sorted_data = sorted(esg_data, key=lambda x: x.timestamp)
        
        if len(sorted_data) < 2:
            return {'insufficient_data': True}
        
        # Calculate trends for each ESG pillar
        trends = {}
        
        for pillar in ['environmental', 'social', 'governance']:
            scores = []
            timestamps = []
            
            for data_point in sorted_data:
                score = getattr(data_point, f'{pillar}_score', None)
                if score is not None:
                    scores.append(score)
                    timestamps.append(data_point.timestamp)
            
            if len(scores) >= 2:
                # Simple trend calculation
                first_half = scores[:len(scores)//2]
                second_half = scores[len(scores)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                trend_direction = 'improving' if second_avg > first_avg else 'declining' if second_avg < first_avg else 'stable'
                trend_magnitude = abs(second_avg - first_avg)
                
                trends[pillar] = {
                    'direction': trend_direction,
                    'magnitude': trend_magnitude,
                    'confidence': min(1.0, len(scores) / 10.0)  # Higher confidence with more data points
                }
        
        return trends
    
    def _extract_narrative_elements(self, esg_data: List[ESGDataPoint]) -> Dict[str, Any]:
        """Extract elements for narrative generation."""
        elements = {
            'key_strengths': [],
            'areas_for_improvement': [],
            'notable_changes': [],
            'data_quality_notes': []
        }
        
        # Analyze scores to identify strengths and weaknesses
        for data_point in esg_data:
            scores = {
                'environmental': data_point.environmental_score,
                'social': data_point.social_score,
                'governance': data_point.governance_score
            }
            
            for pillar, score in scores.items():
                if score is not None:
                    if score >= 80:
                        elements['key_strengths'].append(f"Strong {pillar} performance ({score:.1f})")
                    elif score <= 50:
                        elements['areas_for_improvement'].append(f"{pillar.title()} needs attention ({score:.1f})")
            
            # Data quality notes
            if data_point.data_quality_score < 0.8:
                elements['data_quality_notes'].append(f"Lower quality data from {data_point.data_source}")
        
        # Remove duplicates
        for key in elements:
            elements[key] = list(set(elements[key]))
        
        return elements
    
    def _extract_risk_factors(self, esg_data: List[ESGDataPoint]) -> Dict[str, Any]:
        """Extract risk factors from ESG data."""
        risk_factors = {
            'high_risk_areas': [],
            'data_reliability_risks': [],
            'trend_risks': []
        }
        
        for data_point in esg_data:
            # Identify high-risk scores
            if data_point.environmental_score and data_point.environmental_score < 40:
                risk_factors['high_risk_areas'].append('Environmental performance below acceptable threshold')
            
            if data_point.social_score and data_point.social_score < 40:
                risk_factors['high_risk_areas'].append('Social performance below acceptable threshold')
            
            if data_point.governance_score and data_point.governance_score < 40:
                risk_factors['high_risk_areas'].append('Governance performance below acceptable threshold')
            
            # Data reliability risks
            if data_point.data_quality_score < 0.7:
                risk_factors['data_reliability_risks'].append(f'Low quality data from {data_point.data_source}')
        
        # Remove duplicates
        for key in risk_factors:
            risk_factors[key] = list(set(risk_factors[key]))
        
        return risk_factors


class MCPAIInterface:
    """Interface for AI model interactions using MCP."""
    
    def __init__(self):
        """Initialize MCP AI interface."""
        self.config = get_config()
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.context_processor = ESGContextProcessor()
    
    async def generate_esg_analysis(self, 
                                  mcp_context: MCPContext,
                                  analysis_type: str = 'comprehensive') -> MCPResponse:
        """
        Generate ESG analysis using AI with MCP context.
        
        Args:
            mcp_context: MCP context object
            analysis_type: Type of analysis to generate
            
        Returns:
            MCP response with analysis
        """
        start_time = datetime.utcnow()
        
        try:
            # Prepare context for AI model
            context_prompt = self._create_analysis_prompt(mcp_context, analysis_type)
            
            # Call OpenAI API
            response = await self._call_openai_api(context_prompt, analysis_type)
            
            # Process response
            analysis_content = self._process_ai_response(response, analysis_type)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return MCPResponse(
                session_id=mcp_context.session_id,
                response_type='analysis',
                content=analysis_content,
                confidence_score=analysis_content.get('confidence_score', 0.8),
                sources_used=mcp_context.data_sources,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"ESG analysis generation failed: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return MCPResponse(
                session_id=mcp_context.session_id,
                response_type='error',
                content={'error': str(e), 'message': 'Analysis generation failed'},
                confidence_score=0.0,
                sources_used=[],
                processing_time_ms=processing_time
            )
    
    async def generate_narrative(self, 
                               mcp_context: MCPContext,
                               narrative_style: str = 'executive_summary') -> MCPResponse:
        """
        Generate narrative content using AI with MCP context.
        
        Args:
            mcp_context: MCP context object
            narrative_style: Style of narrative to generate
            
        Returns:
            MCP response with narrative content
        """
        start_time = datetime.utcnow()
        
        try:
            # Prepare narrative prompt
            narrative_prompt = self._create_narrative_prompt(mcp_context, narrative_style)
            
            # Call OpenAI API
            response = await self._call_openai_api(narrative_prompt, 'narrative')
            
            # Process response
            narrative_content = self._process_narrative_response(response, narrative_style)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return MCPResponse(
                session_id=mcp_context.session_id,
                response_type='narrative',
                content=narrative_content,
                confidence_score=narrative_content.get('confidence_score', 0.85),
                sources_used=mcp_context.data_sources,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Narrative generation failed: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return MCPResponse(
                session_id=mcp_context.session_id,
                response_type='error',
                content={'error': str(e), 'message': 'Narrative generation failed'},
                confidence_score=0.0,
                sources_used=[],
                processing_time_ms=processing_time
            )
    
    def _create_analysis_prompt(self, mcp_context: MCPContext, analysis_type: str) -> str:
        """Create analysis prompt for AI model."""
        context_data = mcp_context.metadata.get('context_data', {})
        score_stats = context_data.get('score_statistics', {})
        
        prompt = f"""
        You are an expert ESG (Environmental, Social, Governance) analyst. Analyze the following ESG data and provide insights.

        Context:
        - Analysis Type: {analysis_type}
        - Companies: {', '.join(mcp_context.parameters.get('company_ids', []))}
        - Time Range: {mcp_context.time_range.get('start', 'N/A')} to {mcp_context.time_range.get('end', 'N/A')}
        - Data Sources: {', '.join(mcp_context.data_sources)}
        - Total Records: {mcp_context.metadata.get('total_records', 0)}
        - Average Data Quality: {mcp_context.metadata.get('data_quality_avg', 0):.2f}

        ESG Score Statistics:
        Environmental: Mean {score_stats.get('environmental', {}).get('mean', 0):.1f}, Range {score_stats.get('environmental', {}).get('min', 0):.1f}-{score_stats.get('environmental', {}).get('max', 0):.1f}
        Social: Mean {score_stats.get('social', {}).get('mean', 0):.1f}, Range {score_stats.get('social', {}).get('min', 0):.1f}-{score_stats.get('social', {}).get('max', 0):.1f}
        Governance: Mean {score_stats.get('governance', {}).get('mean', 0):.1f}, Range {score_stats.get('governance', {}).get('min', 0):.1f}-{score_stats.get('governance', {}).get('max', 0):.1f}

        Please provide:
        1. Key insights and findings
        2. Risk assessment
        3. Opportunities for improvement
        4. Confidence level in the analysis (0-100%)
        5. Recommendations for stakeholders

        Format your response as JSON with the following structure:
        {{
            "key_insights": ["insight1", "insight2", ...],
            "risk_assessment": {{
                "high_risks": ["risk1", "risk2", ...],
                "medium_risks": ["risk1", "risk2", ...],
                "risk_score": 0-100
            }},
            "opportunities": ["opportunity1", "opportunity2", ...],
            "recommendations": ["rec1", "rec2", ...],
            "confidence_score": 0.0-1.0,
            "summary": "Brief executive summary"
        }}
        """
        
        return prompt
    
    def _create_narrative_prompt(self, mcp_context: MCPContext, narrative_style: str) -> str:
        """Create narrative prompt for AI model."""
        context_data = mcp_context.metadata.get('context_data', {})
        narrative_elements = context_data.get('narrative_elements', {})
        
        prompt = f"""
        You are an expert ESG storyteller. Create a compelling narrative about ESG performance based on the provided data.

        Context:
        - Narrative Style: {narrative_style}
        - Companies: {', '.join(mcp_context.parameters.get('company_ids', []))}
        - Organization: {mcp_context.organization}
        - Data Sources: {', '.join(mcp_context.data_sources)}

        Narrative Elements:
        - Key Strengths: {', '.join(narrative_elements.get('key_strengths', []))}
        - Areas for Improvement: {', '.join(narrative_elements.get('areas_for_improvement', []))}
        - Notable Changes: {', '.join(narrative_elements.get('notable_changes', []))}

        Create a narrative that:
        1. Tells a compelling story about ESG performance
        2. Highlights key achievements and challenges
        3. Provides context for stakeholders
        4. Includes actionable insights
        5. Maintains professional tone appropriate for {narrative_style}

        Format your response as JSON:
        {{
            "title": "Compelling title for the narrative",
            "executive_summary": "Brief summary (2-3 sentences)",
            "main_narrative": "Full narrative content (3-5 paragraphs)",
            "key_messages": ["message1", "message2", ...],
            "call_to_action": "Recommended next steps",
            "confidence_score": 0.0-1.0
        }}
        """
        
        return prompt
    
    async def _call_openai_api(self, prompt: str, response_type: str) -> Dict[str, Any]:
        """Call OpenAI API with the given prompt."""
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert ESG analyst and storyteller."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return {
                'content': response.choices[0].message.content,
                'usage': response.usage.dict() if response.usage else {},
                'model': response.model
            }
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise
    
    def _process_ai_response(self, response: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Process AI response for analysis."""
        try:
            content = response['content']
            
            # Try to parse as JSON
            if content.strip().startswith('{'):
                analysis_data = json.loads(content)
            else:
                # Fallback: create structured response from text
                analysis_data = {
                    'summary': content,
                    'confidence_score': 0.7,
                    'key_insights': [content[:200] + '...'],
                    'recommendations': ['Review detailed analysis for specific recommendations']
                }
            
            # Add metadata
            analysis_data['analysis_type'] = analysis_type
            analysis_data['model_used'] = response.get('model', 'gpt-4')
            analysis_data['token_usage'] = response.get('usage', {})
            
            return analysis_data
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI response as JSON, using fallback")
            return {
                'summary': response['content'],
                'confidence_score': 0.6,
                'analysis_type': analysis_type,
                'parsing_error': True
            }
    
    def _process_narrative_response(self, response: Dict[str, Any], narrative_style: str) -> Dict[str, Any]:
        """Process AI response for narrative."""
        try:
            content = response['content']
            
            # Try to parse as JSON
            if content.strip().startswith('{'):
                narrative_data = json.loads(content)
            else:
                # Fallback: create structured response from text
                narrative_data = {
                    'title': f'ESG Performance Narrative - {narrative_style.title()}',
                    'main_narrative': content,
                    'confidence_score': 0.7,
                    'executive_summary': content[:200] + '...'
                }
            
            # Add metadata
            narrative_data['narrative_style'] = narrative_style
            narrative_data['model_used'] = response.get('model', 'gpt-4')
            narrative_data['token_usage'] = response.get('usage', {})
            
            return narrative_data
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse narrative response as JSON, using fallback")
            return {
                'title': f'ESG Narrative - {narrative_style.title()}',
                'main_narrative': response['content'],
                'confidence_score': 0.6,
                'narrative_style': narrative_style,
                'parsing_error': True
            }


class MCPSessionManager:
    """Manage MCP sessions and context."""
    
    def __init__(self):
        """Initialize MCP session manager."""
        self.active_sessions: Dict[str, MCPContext] = {}
        self.session_history: Dict[str, List[MCPResponse]] = {}
    
    def create_session(self, mcp_context: MCPContext) -> str:
        """Create new MCP session."""
        self.active_sessions[mcp_context.session_id] = mcp_context
        self.session_history[mcp_context.session_id] = []
        
        logger.info(f"Created MCP session: {mcp_context.session_id}")
        return mcp_context.session_id
    
    def get_session(self, session_id: str) -> Optional[MCPContext]:
        """Get MCP session by ID."""
        return self.active_sessions.get(session_id)
    
    def add_response(self, session_id: str, response: MCPResponse) -> None:
        """Add response to session history."""
        if session_id in self.session_history:
            self.session_history[session_id].append(response)
    
    def get_session_history(self, session_id: str) -> List[MCPResponse]:
        """Get session history."""
        return self.session_history.get(session_id, [])
    
    def close_session(self, session_id: str) -> None:
        """Close MCP session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        # Keep history for a while (could be moved to persistent storage)
        logger.info(f"Closed MCP session: {session_id}")


# Global instances
_mcp_ai_interface: Optional[MCPAIInterface] = None
_mcp_session_manager: Optional[MCPSessionManager] = None


def get_mcp_ai_interface() -> MCPAIInterface:
    """Get global MCP AI interface instance."""
    global _mcp_ai_interface
    
    if _mcp_ai_interface is None:
        _mcp_ai_interface = MCPAIInterface()
    
    return _mcp_ai_interface


def get_mcp_session_manager() -> MCPSessionManager:
    """Get global MCP session manager instance."""
    global _mcp_session_manager
    
    if _mcp_session_manager is None:
        _mcp_session_manager = MCPSessionManager()
    
    return _mcp_session_manager


# Convenience functions
async def create_esg_analysis_session(company_ids: List[str],
                                    time_range: Dict[str, datetime],
                                    user_context: Dict[str, Any],
                                    analysis_type: str = 'comprehensive') -> str:
    """Create ESG analysis session with MCP."""
    context_processor = ESGContextProcessor()
    session_manager = get_mcp_session_manager()
    
    # Create MCP context
    mcp_context = await context_processor.create_esg_context(
        company_ids, 'esg_analysis', time_range, user_context
    )
    
    # Create session
    session_id = session_manager.create_session(mcp_context)
    
    return session_id


async def generate_ai_insights(session_id: str, 
                             analysis_type: str = 'comprehensive') -> MCPResponse:
    """Generate AI insights for a session."""
    session_manager = get_mcp_session_manager()
    ai_interface = get_mcp_ai_interface()
    
    # Get session context
    mcp_context = session_manager.get_session(session_id)
    if not mcp_context:
        raise ValueError(f"Session {session_id} not found")
    
    # Generate analysis
    response = await ai_interface.generate_esg_analysis(mcp_context, analysis_type)
    
    # Add to session history
    session_manager.add_response(session_id, response)
    
    return response

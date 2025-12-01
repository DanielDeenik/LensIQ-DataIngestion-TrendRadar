"""
LensIQ MCP (Model Context Protocol) Usage Examples

This module demonstrates how to use LensIQ's MCP integration for
AI-powered ESG analysis, narrative generation, and insights.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import LensIQ MCP components
from src.ai.mcp_integration import (
    create_esg_analysis_session,
    generate_ai_insights,
    get_mcp_session_manager,
    get_mcp_ai_interface,
    ESGContextProcessor,
    MCPContext,
    MCPResponse
)
from src.data_management.petastorm_pipeline import get_ml_pipeline


class LensIQMCPExamples:
    """Examples demonstrating LensIQ MCP capabilities."""
    
    def __init__(self):
        """Initialize MCP examples."""
        self.session_manager = get_mcp_session_manager()
        self.ai_interface = get_mcp_ai_interface()
        self.context_processor = ESGContextProcessor()
        self.ml_pipeline = get_ml_pipeline()
    
    async def example_1_basic_esg_analysis(self):
        """
        Example 1: Basic ESG Analysis with AI Insights
        
        This example shows how to:
        1. Create an MCP session for ESG analysis
        2. Generate AI-powered insights
        3. Retrieve session results
        """
        print("🔍 Example 1: Basic ESG Analysis with AI Insights")
        print("=" * 60)
        
        # Define companies to analyze
        company_ids = ["AAPL", "MSFT", "GOOGL"]
        
        # Set time range for analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # Last year
        
        # User context
        user_context = {
            'user_id': 'analyst_001',
            'organization': 'investment_firm',
            'tier': 'premium',
            'analysis_depth': 'detailed'
        }
        
        try:
            # Step 1: Create MCP session
            print("📊 Creating ESG analysis session...")
            session_id = await create_esg_analysis_session(
                company_ids=company_ids,
                time_range={'start': start_date, 'end': end_date},
                user_context=user_context,
                analysis_type='comprehensive'
            )
            print(f"✅ Session created: {session_id}")
            
            # Step 2: Generate AI insights
            print("🤖 Generating AI insights...")
            ai_response = await generate_ai_insights(session_id, 'comprehensive')
            
            # Step 3: Display results
            print("📋 Analysis Results:")
            print(f"   Confidence Score: {ai_response.confidence_score:.2%}")
            print(f"   Processing Time: {ai_response.processing_time_ms:.0f}ms")
            print(f"   Sources Used: {', '.join(ai_response.sources_used)}")
            
            # Display key insights
            content = ai_response.content
            if 'key_insights' in content:
                print("💡 Key Insights:")
                for insight in content['key_insights'][:3]:  # Show top 3
                    print(f"   • {insight}")
            
            # Display risk assessment
            if 'risk_assessment' in content:
                risk_data = content['risk_assessment']
                print(f"⚠️  Risk Score: {risk_data.get('risk_score', 'N/A')}/100")
                if 'high_risks' in risk_data:
                    print("   High Risks:")
                    for risk in risk_data['high_risks'][:2]:  # Show top 2
                        print(f"   • {risk}")
            
            return session_id, ai_response
            
        except Exception as e:
            print(f"❌ Error in basic ESG analysis: {str(e)}")
            return None, None
    
    async def example_2_narrative_generation(self, session_id: str):
        """
        Example 2: AI-Powered Narrative Generation
        
        This example shows how to:
        1. Use an existing MCP session
        2. Generate different narrative styles
        3. Extract key messages for stakeholders
        """
        print("\n📝 Example 2: AI-Powered Narrative Generation")
        print("=" * 60)
        
        if not session_id:
            print("❌ No session ID provided. Run Example 1 first.")
            return
        
        # Get session context
        mcp_context = self.session_manager.get_session(session_id)
        if not mcp_context:
            print(f"❌ Session {session_id} not found")
            return
        
        # Generate different narrative styles
        narrative_styles = [
            'executive_summary',
            'investor_report',
            'board_presentation'
        ]
        
        narratives = {}
        
        for style in narrative_styles:
            try:
                print(f"✍️  Generating {style.replace('_', ' ').title()}...")
                
                narrative_response = await self.ai_interface.generate_narrative(
                    mcp_context, style
                )
                
                narratives[style] = narrative_response
                
                # Display narrative preview
                content = narrative_response.content
                print(f"   Title: {content.get('title', 'N/A')}")
                print(f"   Confidence: {narrative_response.confidence_score:.2%}")
                
                # Show executive summary
                if 'executive_summary' in content:
                    summary = content['executive_summary']
                    preview = summary[:100] + "..." if len(summary) > 100 else summary
                    print(f"   Preview: {preview}")
                
                # Show key messages
                if 'key_messages' in content:
                    print("   Key Messages:")
                    for msg in content['key_messages'][:2]:  # Show top 2
                        print(f"   • {msg}")
                
                print()
                
            except Exception as e:
                print(f"❌ Error generating {style}: {str(e)}")
        
        return narratives
    
    async def example_3_trend_analysis_with_context(self):
        """
        Example 3: Advanced Trend Analysis with Rich Context
        
        This example shows how to:
        1. Create rich context for trend analysis
        2. Use MCP for trend detection
        3. Generate actionable insights
        """
        print("📈 Example 3: Advanced Trend Analysis with Rich Context")
        print("=" * 60)
        
        # Define analysis parameters
        company_ids = ["TSLA", "NIO", "RIVN"]  # EV companies
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years
        
        user_context = {
            'user_id': 'portfolio_manager',
            'organization': 'green_fund',
            'tier': 'enterprise',
            'analysis_depth': 'comprehensive'
        }
        
        try:
            # Create context for trend analysis
            print("🔄 Creating trend analysis context...")
            mcp_context = await self.context_processor.create_esg_context(
                company_ids=company_ids,
                context_type='trend_detection',
                time_range={'start': start_date, 'end': end_date},
                user_context=user_context
            )
            
            # Create session
            session_id = self.session_manager.create_session(mcp_context)
            print(f"✅ Trend analysis session: {session_id}")
            
            # Generate trend analysis
            print("📊 Analyzing ESG trends...")
            trend_response = await self.ai_interface.generate_esg_analysis(
                mcp_context, 'trend_analysis'
            )
            
            # Display trend results
            print("📋 Trend Analysis Results:")
            content = trend_response.content
            
            # Show trend indicators from context
            context_data = mcp_context.metadata.get('context_data', {})
            trend_indicators = context_data.get('trend_indicators', {})
            
            if trend_indicators:
                print("📈 Trend Indicators:")
                for pillar, trend_data in trend_indicators.items():
                    if isinstance(trend_data, dict):
                        direction = trend_data.get('direction', 'unknown')
                        confidence = trend_data.get('confidence', 0)
                        print(f"   {pillar.title()}: {direction} (confidence: {confidence:.2%})")
            
            # Show AI insights
            if 'key_insights' in content:
                print("💡 AI-Generated Insights:")
                for insight in content['key_insights'][:3]:
                    print(f"   • {insight}")
            
            # Show opportunities
            if 'opportunities' in content:
                print("🎯 Opportunities:")
                for opp in content['opportunities'][:2]:
                    print(f"   • {opp}")
            
            return session_id, trend_response
            
        except Exception as e:
            print(f"❌ Error in trend analysis: {str(e)}")
            return None, None
    
    async def example_4_risk_assessment_workflow(self):
        """
        Example 4: Comprehensive Risk Assessment Workflow
        
        This example shows how to:
        1. Create risk-focused context
        2. Generate risk assessment
        3. Provide actionable recommendations
        """
        print("\n⚠️  Example 4: Comprehensive Risk Assessment Workflow")
        print("=" * 60)
        
        # High-risk portfolio for demonstration
        company_ids = ["XOM", "CVX", "COP"]  # Oil & gas companies
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        user_context = {
            'user_id': 'risk_manager',
            'organization': 'pension_fund',
            'tier': 'enterprise',
            'analysis_depth': 'risk_focused'
        }
        
        try:
            # Create risk assessment context
            print("🔍 Creating risk assessment context...")
            mcp_context = await self.context_processor.create_esg_context(
                company_ids=company_ids,
                context_type='risk_assessment',
                time_range={'start': start_date, 'end': end_date},
                user_context=user_context
            )
            
            session_id = self.session_manager.create_session(mcp_context)
            print(f"✅ Risk assessment session: {session_id}")
            
            # Generate risk analysis
            print("⚠️  Analyzing ESG risks...")
            risk_response = await self.ai_interface.generate_esg_analysis(
                mcp_context, 'risk_assessment'
            )
            
            # Display risk results
            print("📋 Risk Assessment Results:")
            content = risk_response.content
            
            # Show risk factors from context
            context_data = mcp_context.metadata.get('context_data', {})
            risk_factors = context_data.get('risk_factors', {})
            
            if risk_factors:
                print("🚨 Identified Risk Factors:")
                for risk_type, risks in risk_factors.items():
                    if risks:
                        print(f"   {risk_type.replace('_', ' ').title()}:")
                        for risk in risks[:2]:  # Show top 2
                            print(f"   • {risk}")
            
            # Show AI risk assessment
            if 'risk_assessment' in content:
                risk_data = content['risk_assessment']
                print(f"📊 Overall Risk Score: {risk_data.get('risk_score', 'N/A')}/100")
                
                if 'high_risks' in risk_data:
                    print("🔴 High Priority Risks:")
                    for risk in risk_data['high_risks'][:3]:
                        print(f"   • {risk}")
            
            # Show recommendations
            if 'recommendations' in content:
                print("💡 Risk Mitigation Recommendations:")
                for rec in content['recommendations'][:3]:
                    print(f"   • {rec}")
            
            return session_id, risk_response
            
        except Exception as e:
            print(f"❌ Error in risk assessment: {str(e)}")
            return None, None
    
    async def example_5_session_management(self):
        """
        Example 5: Advanced Session Management
        
        This example shows how to:
        1. Manage multiple MCP sessions
        2. Track session history
        3. Compare results across sessions
        """
        print("\n🔧 Example 5: Advanced Session Management")
        print("=" * 60)
        
        # Create multiple sessions for comparison
        sessions = {}
        
        # Session 1: Tech companies
        tech_companies = ["AAPL", "MSFT", "GOOGL"]
        tech_session = await self._create_comparison_session(
            "tech_analysis", tech_companies, "Technology Sector"
        )
        if tech_session:
            sessions['tech'] = tech_session
        
        # Session 2: Energy companies
        energy_companies = ["XOM", "CVX", "COP"]
        energy_session = await self._create_comparison_session(
            "energy_analysis", energy_companies, "Energy Sector"
        )
        if energy_session:
            sessions['energy'] = energy_session
        
        # Compare sessions
        if len(sessions) >= 2:
            print("📊 Session Comparison:")
            for sector, (session_id, response) in sessions.items():
                print(f"\n{sector.title()} Sector:")
                print(f"   Session ID: {session_id}")
                print(f"   Confidence: {response.confidence_score:.2%}")
                print(f"   Processing Time: {response.processing_time_ms:.0f}ms")
                
                # Show session history
                history = self.session_manager.get_session_history(session_id)
                print(f"   History Length: {len(history)} responses")
        
        return sessions
    
    async def _create_comparison_session(self, analysis_type: str, 
                                       company_ids: List[str], 
                                       description: str):
        """Helper method to create comparison sessions."""
        try:
            print(f"🔄 Creating {description} session...")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            user_context = {
                'user_id': 'sector_analyst',
                'organization': 'research_firm',
                'tier': 'premium',
                'analysis_depth': 'standard'
            }
            
            session_id = await create_esg_analysis_session(
                company_ids=company_ids,
                time_range={'start': start_date, 'end': end_date},
                user_context=user_context,
                analysis_type=analysis_type
            )
            
            response = await generate_ai_insights(session_id, 'sector_analysis')
            
            print(f"✅ {description} session created: {session_id}")
            return session_id, response
            
        except Exception as e:
            print(f"❌ Error creating {description} session: {str(e)}")
            return None
    
    def display_session_summary(self, session_id: str):
        """Display comprehensive session summary."""
        print(f"\n📋 Session Summary: {session_id}")
        print("=" * 50)
        
        # Get session context
        mcp_context = self.session_manager.get_session(session_id)
        if not mcp_context:
            print("❌ Session not found")
            return
        
        # Display context information
        print("🔍 Session Context:")
        print(f"   Type: {mcp_context.context_type}")
        print(f"   User: {mcp_context.user_id}")
        print(f"   Organization: {mcp_context.organization}")
        print(f"   Companies: {', '.join(mcp_context.parameters.get('company_ids', []))}")
        print(f"   Data Sources: {', '.join(mcp_context.data_sources)}")
        
        # Display metadata
        metadata = mcp_context.metadata
        print(f"   Total Records: {metadata.get('total_records', 0)}")
        print(f"   Avg Quality: {metadata.get('data_quality_avg', 0):.2%}")
        
        # Display session history
        history = self.session_manager.get_session_history(session_id)
        print(f"\n📊 Session History ({len(history)} responses):")
        
        for i, response in enumerate(history, 1):
            print(f"   {i}. {response.response_type.title()}")
            print(f"      Confidence: {response.confidence_score:.2%}")
            print(f"      Time: {response.processing_time_ms:.0f}ms")
            print(f"      Timestamp: {response.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")


async def run_all_examples():
    """Run all MCP examples in sequence."""
    print("🚀 LensIQ MCP Integration Examples")
    print("=" * 80)
    print("This demo showcases AI-powered ESG analysis using Model Context Protocol")
    print()
    
    examples = LensIQMCPExamples()
    
    try:
        # Example 1: Basic ESG Analysis
        session_id, analysis_response = await examples.example_1_basic_esg_analysis()
        
        if session_id:
            # Example 2: Narrative Generation
            narratives = await examples.example_2_narrative_generation(session_id)
            
            # Display session summary
            examples.display_session_summary(session_id)
        
        # Example 3: Trend Analysis
        trend_session, trend_response = await examples.example_3_trend_analysis_with_context()
        
        # Example 4: Risk Assessment
        risk_session, risk_response = await examples.example_4_risk_assessment_workflow()
        
        # Example 5: Session Management
        sessions = await examples.example_5_session_management()
        
        print("\n🎉 All examples completed successfully!")
        print("=" * 80)
        
        # Summary of created sessions
        all_sessions = [session_id, trend_session, risk_session]
        all_sessions.extend([s[0] for s in sessions.values() if s])
        active_sessions = [s for s in all_sessions if s]
        
        print(f"📊 Created {len(active_sessions)} MCP sessions:")
        for i, sid in enumerate(active_sessions, 1):
            print(f"   {i}. {sid}")
        
        print("\n💡 Next Steps:")
        print("   • Explore session details using display_session_summary()")
        print("   • Generate additional narratives with different styles")
        print("   • Create custom analysis workflows")
        print("   • Integrate with your existing ESG data pipeline")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")


# Standalone example functions for specific use cases
async def quick_company_analysis(company_id: str):
    """Quick analysis for a single company."""
    print(f"🔍 Quick Analysis: {company_id}")
    
    examples = LensIQMCPExamples()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # Last quarter
    
    user_context = {
        'user_id': 'quick_user',
        'organization': 'demo',
        'tier': 'standard'
    }
    
    session_id = await create_esg_analysis_session(
        company_ids=[company_id],
        time_range={'start': start_date, 'end': end_date},
        user_context=user_context,
        analysis_type='quick'
    )
    
    response = await generate_ai_insights(session_id, 'quick')
    
    print(f"✅ Analysis complete for {company_id}")
    print(f"   Confidence: {response.confidence_score:.2%}")
    
    return session_id, response


async def sector_comparison(sector_companies: Dict[str, List[str]]):
    """Compare ESG performance across sectors."""
    print("📊 Sector Comparison Analysis")
    
    results = {}
    
    for sector, companies in sector_companies.items():
        print(f"🔄 Analyzing {sector}...")
        
        session_id = await create_esg_analysis_session(
            company_ids=companies,
            time_range={
                'start': datetime.now() - timedelta(days=365),
                'end': datetime.now()
            },
            user_context={
                'user_id': 'sector_analyst',
                'organization': 'research',
                'tier': 'premium'
            },
            analysis_type='sector_comparison'
        )
        
        response = await generate_ai_insights(session_id, 'sector_analysis')
        results[sector] = (session_id, response)
        
        print(f"✅ {sector} analysis complete")
    
    return results


if __name__ == "__main__":
    # Run all examples
    asyncio.run(run_all_examples())
    
    # Uncomment to run specific examples:
    # asyncio.run(quick_company_analysis("AAPL"))
    # 
    # sectors = {
    #     "Technology": ["AAPL", "MSFT", "GOOGL"],
    #     "Energy": ["XOM", "CVX", "COP"],
    #     "Finance": ["JPM", "BAC", "WFC"]
    # }
    # asyncio.run(sector_comparison(sectors))

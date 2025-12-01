# LensIQ Platform - Complete Overview

![LensIQ Logo](images/lensiq-logo.png)

## Table of Contents
- [Introduction](#introduction)
- [Platform Architecture](#platform-architecture)
- [Core Features](#core-features)
  - [1. Storytelling (LensIQ)](#1-storytelling-lensiq)
  - [2. Strategy Hub](#2-strategy-hub)
  - [3. Trends (TrendRadar)](#3-trends-trendradar)
  - [4. VC Lens](#4-vc-lens)
  - [5. Graph Analytics](#5-graph-analytics)
  - [6. Data Management](#6-data-management)
  - [7. Lookthrough](#7-lookthrough)
  - [8. Lifecycle Management](#8-lifecycle-management)
  - [9. AI Copilot](#9-ai-copilot)
- [Technical Stack](#technical-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)

---

## Introduction

**LensIQ** is an enterprise-grade AI-powered platform designed for ESG (Environmental, Social, and Governance) analysis, sustainability trend monitoring, and strategic investment intelligence. The platform combines advanced data analytics, machine learning, and intuitive visualization to help organizations make data-driven decisions in the sustainability space.

### Key Capabilities
- 🎯 **AI-Powered Storytelling** - Transform data into compelling narratives
- 📊 **Strategic Planning** - Multiple strategic frameworks (Porter's Five Forces, SWOT, BCG Matrix, etc.)
- 📡 **Real-Time Trend Monitoring** - Dynamic trend radar with ML-powered insights
- 💼 **Investment Intelligence** - VC-focused analytics and portfolio management
- 🔍 **Deep Analytics** - Graph-based network analysis and relationship mapping
- 🤖 **AI Assistant** - Intelligent copilot for data exploration and insights

---

## Platform Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LensIQ Platform                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Storytelling │  │   Strategy   │  │    Trends    │      │
│  │   (LensIQ)   │  │     Hub      │  │ (TrendRadar) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   VC Lens    │  │    Graph     │  │     Data     │      │
│  │              │  │  Analytics   │  │  Management  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Lookthrough  │  │  Lifecycle   │  │ AI Copilot   │      │
│  │              │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│              Core Services & Infrastructure                   │
│  • MongoDB Database  • Vector Store  • AI Services           │
│  • RESTful APIs     • Authentication  • Real-time Updates    │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Features

### 1. Storytelling (LensIQ)

**Purpose:** Transform complex ESG data into compelling narratives that resonate with investors, clients, and stakeholders.

![LensIQ Storytelling Dashboard](images/lensiq-storytelling-dashboard.png)

#### Key Features:
- **AI-Generated Stories** - Automatically create data-driven narratives from trends and insights
- **Insight Generation** - Extract key insights from sustainability data
- **Trend Narratives** - Connect trends to create cohesive storylines
- **Custom Story Builder** - Interactive interface for crafting custom narratives

#### Use Cases:
- 📝 Investor pitch decks and presentations
- 📊 Quarterly sustainability reports
- 🎯 Marketing and communications materials
- 💡 Executive briefings and board presentations

#### Screenshots:

**Main Storytelling Interface**
![Storytelling Interface](images/storytelling-main.png)
*Create and manage sustainability stories with AI assistance*

**AI Insights Panel**
![AI Insights](images/storytelling-insights.png)
*View AI-generated insights from your data*

**Narrative Builder**
![Narrative Builder](images/storytelling-narratives.png)
*Build compelling narratives from trend data*

#### API Endpoints:
```
GET  /storytelling/api/stories       - Retrieve all stories
GET  /storytelling/api/insights      - Get AI-generated insights
POST /storytelling/api/generate-story - Generate new story
GET  /storytelling/api/trend-insights - Get trend-based insights
```

---

### 2. Strategy Hub

**Purpose:** Comprehensive strategic planning tools using industry-standard frameworks for sustainability initiatives.

![Strategy Hub Dashboard](images/strategy-hub-dashboard.png)

#### Available Frameworks:

##### Porter's Five Forces
Assess competitive sustainability positioning across five dimensions:
- Supplier Power
- Buyer Power
- Competitive Rivalry
- Threat of Substitution
- Threat of New Entry

![Porter's Five Forces](images/strategy-porters.png)

##### SWOT Analysis
Evaluate sustainability initiatives through:
- **Strengths** - Internal advantages
- **Weaknesses** - Internal limitations
- **Opportunities** - External possibilities
- **Threats** - External challenges

![SWOT Analysis](images/strategy-swot.png)

##### BCG Growth-Share Matrix
Prioritize green investments based on:
- Market Growth Rate
- Relative Market Share

![BCG Matrix](images/strategy-bcg.png)

##### McKinsey 9-Box Matrix
Rank assets on two dimensions:
- Market Attractiveness
- Competitive Position

![McKinsey Matrix](images/strategy-mckinsey.png)

##### Strategy Pyramid
Define hierarchical strategy:
- Mission
- Objectives
- Strategies
- Tactics

![Strategy Pyramid](images/strategy-pyramid.png)

#### Features:
- **Framework Selection** - Choose from 5+ strategic frameworks
- **Interactive Analysis** - Visual, interactive framework tools
- **Strategy Execution** - Track and monitor strategy implementation
- **Collaborative Planning** - Share and collaborate on strategies
- **Progress Tracking** - Monitor KPIs and milestones

#### Screenshots:

**Framework Selection**
![Framework Selection](images/strategy-frameworks.png)
*Choose the right strategic framework for your analysis*

**Strategy Execution Dashboard**
![Strategy Execution](images/strategy-execution.png)
*Track progress and monitor strategy implementation*

#### API Endpoints:
```
GET  /strategy/api/frameworks        - List available frameworks
GET  /strategy/api/strategies        - Get all strategies
POST /strategy/api/analyze           - Analyze using framework
GET  /strategy/framework/<name>      - Framework details
```

---

### 3. Trends (TrendRadar)

**Purpose:** Real-time sustainability trend monitoring with dynamic visualization and ML-powered insights.

![TrendRadar Dashboard](images/trendradar-dashboard.png)

#### Key Features:
- **Dynamic Radar Visualization** - Interactive trend radar with real-time data
- **ML-Powered Analysis** - Machine learning algorithms for trend prediction
- **Category Filtering** - Filter trends by category, stage, and impact
- **Trend Stages** - Watch, Prepare, Act classification
- **Historical Tracking** - Track trend evolution over time

#### Trend Categories:
- 🌱 Environmental
- 👥 Social
- 🏛️ Governance
- 💡 Technology
- 📈 Market
- 🔬 Innovation

#### Screenshots:

**Interactive Trend Radar**
![Trend Radar](images/trendradar-main.png)
*Visualize trends across categories and stages*

**Trend Details Panel**
![Trend Details](images/trendradar-details.png)
*Deep dive into individual trend metrics and predictions*

**ML Insights**
![ML Insights](images/trendradar-ml.png)
*Machine learning-powered trend forecasting*

#### API Endpoints:
```
GET  /trends/api/radar-data          - Get radar visualization data
GET  /trends/api/metrics             - Retrieve trend metrics
GET  /trends/api/ml-trends           - ML-powered trend analysis
POST /trends/api/filter              - Filter trends by criteria
```

---

### 4. VC Lens

**Purpose:** Venture capital investment analysis focused on sustainability and ESG metrics.

![VC Lens Dashboard](images/vc-lens-dashboard.png)

#### Key Features:
- **Portfolio Analytics** - Comprehensive portfolio performance metrics
- **ESG Scoring** - Automated ESG assessment for investments
- **Deal Flow Management** - Track and analyze investment opportunities
- **Impact Measurement** - Quantify social and environmental impact
- **Comparative Analysis** - Benchmark against industry standards

#### Metrics Tracked:
- 💰 Financial Performance
- 🌍 Environmental Impact
- 👥 Social Impact
- 📊 Governance Quality
- 📈 Growth Potential
- ⚠️ Risk Assessment

#### Screenshots:

**Portfolio Overview**
![Portfolio Overview](images/vc-lens-portfolio.png)
*High-level view of portfolio performance and ESG metrics*

**Company Deep Dive**
![Company Analysis](images/vc-lens-company.png)
*Detailed analysis of individual portfolio companies*

**ESG Scorecard**
![ESG Scorecard](images/vc-lens-esg.png)
*Comprehensive ESG scoring and benchmarking*

#### API Endpoints:
```
GET  /vc-lens/api/portfolio          - Portfolio summary
GET  /vc-lens/api/companies          - List portfolio companies
GET  /vc-lens/api/esg-scores         - ESG scoring data
POST /vc-lens/api/analyze-deal       - Analyze new deal
```

---

### 5. Graph Analytics

**Purpose:** Network analysis and relationship mapping for complex ESG data.

![Graph Analytics Dashboard](images/graph-analytics-dashboard.png)

#### Available Graph Types:

##### Impact Graph
Visualize impact relationships and dependencies
![Impact Graph](images/graph-impact.png)

##### Network Graph
Map organizational and stakeholder networks
![Network Graph](images/graph-network.png)

##### Supply Chain Graph
Analyze supply chain relationships and risks
![Supply Chain Graph](images/graph-supply-chain.png)

##### Venture Signal Graph
Track investment signals and connections
![Venture Signal Graph](images/graph-venture-signal.png)

#### Features:
- **Interactive Visualization** - Zoom, pan, and explore graph data
- **Relationship Mapping** - Identify connections and dependencies
- **Centrality Analysis** - Find key nodes and influencers
- **Path Finding** - Discover relationships between entities
- **Community Detection** - Identify clusters and groups

#### API Endpoints:
```
GET  /graph-analytics/api/impact-graph       - Impact graph data
GET  /graph-analytics/api/network-graph      - Network relationships
GET  /graph-analytics/api/supply-chain       - Supply chain graph
GET  /graph-analytics/api/venture-signals    - Venture signal graph
POST /graph-analytics/api/analyze-path       - Find paths between nodes
```

---

### 6. Data Management

**Purpose:** Centralized data storage, retrieval, and management for all ESG data.

![Data Management Dashboard](images/data-management-dashboard.png)

#### Key Features:
- **Multi-Source Ingestion** - Import from JSON, CSV, Excel, APIs, databases
- **Data Transformation** - Clean, validate, and enrich data
- **RAG Integration** - Retrieval-Augmented Generation for AI insights
- **Vector Storage** - Efficient storage and retrieval of embeddings
- **Quality Validation** - Automated data quality checks
- **API Access** - RESTful APIs for programmatic access

#### Data Sources Supported:
- 📄 JSON files
- 📊 CSV/Excel spreadsheets
- 🔌 REST APIs
- 🗄️ Databases (MongoDB, SQL)
- 🌐 Web scraping
- 📡 Real-time streams

#### Screenshots:

**Data Upload Interface**
![Data Upload](images/data-management-upload.png)
*Upload and import data from multiple sources*

**Collection Browser**
![Collection Browser](images/data-management-collections.png)
*Browse and manage data collections*

**Data Quality Dashboard**
![Data Quality](images/data-management-quality.png)
*Monitor data quality metrics and validation results*

#### API Endpoints:
```
GET  /data-management/api/collections        - List all collections
POST /data-management/api/upload             - Upload new data
GET  /data-management/api/collection/<name>  - Get collection data
POST /data-management/api/transform          - Transform data
GET  /data-management/api/quality-report     - Data quality metrics
```

---

### 7. Lookthrough

**Purpose:** Entity traversal and metrics propagation for portfolio analysis.

![Lookthrough Dashboard](images/lookthrough-dashboard.png)

#### Key Features:
- **Entity Hierarchy** - Navigate fund → company → project structures
- **Metrics Propagation** - Roll up metrics from projects to funds
- **Multi-Level Analysis** - Analyze at fund, company, or project level
- **Ownership Tracking** - Track ownership percentages and stakes
- **Impact Aggregation** - Aggregate impact metrics across portfolio

#### Entity Types:
- 💼 **Funds** - Investment funds and vehicles
- 🏢 **Companies** - Portfolio companies
- 🎯 **Projects** - Individual projects and initiatives

#### Screenshots:

**Fund View**
![Fund View](images/lookthrough-fund.png)
*Overview of fund holdings and aggregated metrics*

**Company View**
![Company View](images/lookthrough-company.png)
*Detailed company analysis with project breakdown*

**Project View**
![Project View](images/lookthrough-project.png)
*Individual project metrics and impact data*

#### API Endpoints:
```
GET  /lookthrough/api/funds                  - List all funds
GET  /lookthrough/api/fund/<id>              - Fund details
GET  /lookthrough/api/company/<id>           - Company details
GET  /lookthrough/api/project/<id>           - Project details
POST /lookthrough/api/propagate-metrics      - Calculate rolled-up metrics
```

---

### 8. Lifecycle Management

**Purpose:** Track and manage the complete lifecycle of investments and initiatives.

![Lifecycle Dashboard](images/lifecycle-dashboard.png)

#### Lifecycle Stages:
1. **Discovery** - Identify opportunities
2. **Due Diligence** - Evaluate and assess
3. **Investment** - Execute transaction
4. **Growth** - Monitor and support
5. **Exit** - Realize returns

#### Key Features:
- **Stage Tracking** - Monitor progress through lifecycle stages
- **Milestone Management** - Track key milestones and deliverables
- **Document Management** - Store and organize lifecycle documents
- **Timeline Visualization** - Visual timeline of lifecycle events
- **Automated Workflows** - Trigger actions based on stage transitions

#### Screenshots:

**Lifecycle Timeline**
![Lifecycle Timeline](images/lifecycle-timeline.png)
*Visual timeline of investment lifecycle*

**Stage Details**
![Stage Details](images/lifecycle-stages.png)
*Detailed view of current stage and next steps*

#### API Endpoints:
```
GET  /lifecycle/api/investments              - List all investments
GET  /lifecycle/api/investment/<id>          - Investment details
POST /lifecycle/api/update-stage             - Update lifecycle stage
GET  /lifecycle/api/milestones               - Get milestones
POST /lifecycle/api/add-milestone            - Add new milestone
```

---

### 9. AI Copilot

**Purpose:** Intelligent AI assistant for data exploration, insights, and decision support.

![AI Copilot Interface](images/copilot-interface.png)

#### Capabilities:
- **Natural Language Queries** - Ask questions in plain English
- **Data Exploration** - Discover insights through conversation
- **Automated Analysis** - AI-powered data analysis
- **Recommendations** - Get AI-driven recommendations
- **Context-Aware** - Understands your current view and context

#### Example Queries:
- "What are the top ESG trends this quarter?"
- "Show me companies with high environmental impact scores"
- "Compare portfolio performance against benchmarks"
- "Generate a sustainability report for Q4"
- "What are the risks in my supply chain?"

#### Screenshots:

**Chat Interface**
![Copilot Chat](images/copilot-chat.png)
*Natural language interface for data queries*

**AI Insights**
![Copilot Insights](images/copilot-insights.png)
*AI-generated insights and recommendations*

#### API Endpoints:
```
POST /copilot/api/query                      - Send natural language query
GET  /copilot/api/suggestions                - Get AI suggestions
POST /copilot/api/analyze                    - Request AI analysis
GET  /copilot/api/history                    - Query history
```

---

## Technical Stack

### Backend
- **Framework:** Flask 3.0.3
- **Language:** Python 3.11+
- **Database:** MongoDB 4.8.0
- **Vector Store:** Pinecone 5.0.0
- **AI/ML:** OpenAI 1.40.0, scikit-learn 1.5.1

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **JavaScript** - Interactive UI components
- **TailwindCSS** - Utility-first CSS framework
- **Chart.js/D3.js** - Data visualization

### Data Processing
- **pandas 2.2.2** - Data manipulation
- **numpy 1.26.4** - Numerical computing
- **pyarrow 17.0.0** - Columnar data processing

### Infrastructure
- **gunicorn 22.0.0** - Production WSGI server
- **Redis 5.0.8** - Caching and session management
- **NetworkX 3.3** - Graph analysis

### Security
- **PyJWT 2.9.0** - JSON Web Tokens
- **cryptography 43.0.0** - Encryption and security

---

## Getting Started

### Prerequisites
- Python 3.11 or higher
- MongoDB 4.0 or higher
- 4GB RAM minimum (8GB recommended)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/TrendSense.git
   cd TrendSense
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Unix/MacOS
   # or
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up MongoDB**
   ```bash
   # See MONGODB_SETUP_GUIDE.md for detailed instructions
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the platform**
   ```
   Open browser to: http://localhost:5000
   ```

### Quick Start Guide

1. **Access the Dashboard** - Navigate to the home page
2. **Explore Features** - Use the navigation menu to access different modules
3. **Upload Data** - Go to Data Management to import your ESG data
4. **Create Stories** - Use LensIQ to generate narratives
5. **Analyze Trends** - Check TrendRadar for real-time insights
6. **Build Strategies** - Use Strategy Hub for planning

---

## API Documentation

### Authentication

All API endpoints require authentication using JWT tokens.

```bash
# Get access token
POST /api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}

# Use token in requests
GET /api/endpoint
Authorization: Bearer <your_token>
```

### Response Format

All API responses follow this format:

```json
{
  "status": "success|error",
  "data": { ... },
  "message": "Optional message",
  "timestamp": "2025-11-14T12:00:00Z"
}
```

### Rate Limiting

- **Free Tier:** 100 requests/hour
- **Pro Tier:** 1,000 requests/hour
- **Enterprise:** Unlimited

### Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not Found |
| 429  | Rate Limit Exceeded |
| 500  | Internal Server Error |

---

## Additional Resources

- 📚 [Full API Documentation](API-Documentation.md)
- 🎓 [User Guide](User-Guide.md)
- 🔧 [Developer Guide](Developer-Guide.md)
- 🐛 [Troubleshooting](Troubleshooting.md)
- 📊 [Data Schema Reference](Data-Schema.md)
- 🔐 [Security Best Practices](Security.md)

---

## Support

For questions, issues, or feature requests:

- 📧 Email: support@lensiq.com
- 💬 Slack: [LensIQ Community](https://lensiq.slack.com)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/TrendSense/issues)
- 📖 Documentation: [docs.lensiq.com](https://docs.lensiq.com)

---

## License

Proprietary - All rights reserved.

© 2025 LensIQ Platform. All rights reserved.

---

*Last Updated: November 14, 2025*


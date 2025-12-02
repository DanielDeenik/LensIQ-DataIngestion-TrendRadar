# LensIQ Data Ingestion & TrendRadar - Architecture Documentation

> **Comprehensive architectural overview of the LensIQ Data Ingestion & TrendRadar platform**

**Version:** 1.0.0  
**Last Updated:** 2025-12-02  
**Repository:** https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [Component Map](#component-map)
4. [Technology Stack](#technology-stack)
5. [Module Descriptions](#module-descriptions)
6. [API Endpoints](#api-endpoints)
7. [Database Schema](#database-schema)
8. [Mermaid Diagrams](#mermaid-diagrams)

---

## 🎯 System Overview

LensIQ Data Ingestion & TrendRadar is an AI-powered platform designed to:

- **Ingest data from multiple sources** (Reddit, Discord, LinkedIn, SQL, MongoDB, Files)
- **Process and analyze trends** using machine learning and AI
- **Visualize insights** through interactive TrendRadar
- **Generate narratives** using AI-powered storytelling
- **Provide strategic frameworks** for decision-making

### Key Capabilities

| Capability | Status | Description |
|------------|--------|-------------|
| **Multi-Source Ingestion** | ✅ Phase 1 | Reddit, Discord, Files |
| **Data Processing** | ✅ Phase 1 | Cleaning, validation, transformation |
| **AI Integration** | ✅ Phase 1 | OpenAI GPT-4 for narratives |
| **TrendRadar Visualization** | ✅ Phase 1 | Interactive radar charts |
| **ML Trend Detection** | 🚧 Phase 4 | Time series, anomaly detection |
| **Advanced Analytics** | 🚧 Phase 5 | Predictive forecasting |

---

## 🏗️ Architecture Layers

### Layer 1: External Data Sources
- Reddit API (Posts, Comments, Sentiment)
- Discord Bot (Messages, Channels)
- LinkedIn API (Professional Insights) - Phase 2
- SQL Databases (PostgreSQL, MySQL) - Phase 2
- File Uploads (CSV, Excel, JSON)

### Layer 2: Data Ingestion
- Reddit Connector (PRAW Integration) ✅
- Discord Connector (Async Bot) ✅
- LinkedIn Connector - Phase 2
- SQL Connector - Phase 2
- File Connectors (CSV/Excel/JSON) ✅

### Layer 3: Data Processing Pipeline
- RAG Data Manager (Orchestration)
- Data Transformer (Cleaning & Enrichment)
- Data Quality Validator (ESG Validation)

### Layer 4: AI/ML Processing
- AI Connector (OpenAI GPT-4)
- Sentiment Analysis (NLP Models)
- Trend Detection (Time Series Analysis) - Phase 4
- Anomaly Detection (Isolation Forest) - Phase 4
- Clustering (K-means, DBSCAN) - Phase 4

### Layer 5: Data Storage
- MongoDB (Primary Database)
- Vector DB (Embeddings) - Optional
- Redis Cache (Performance) - Optional

### Layer 6: Application Layer
- Flask Application (app.py)
- Database Service (Singleton Pattern)
- Database Adapter (MongoDB/Firebase)

### Layer 7: API & Routes
- API Routes (/api/*)
- LensIQ Routes (/storytelling)
- TrendRadar Routes (/trends)
- Strategy Routes (/strategy)

### Layer 8: Frontend Presentation
- Storytelling UI (AI Narratives)
- TrendRadar UI (Interactive Visualization)
- Strategy Hub UI (Frameworks & Tools)
- Dashboard (Overview & Metrics)

---

## 📦 Component Map

### Core Application
- **app.py** - Flask Application (Port 5050)

### Data Management Module (`src/data_management/`)

#### Connectors
- `reddit_connector.py` ✅ Complete (300 lines)
- `discord_connector.py` ✅ Complete (360 lines)
- `linkedin_connector.py` 🚧 Phase 2
- `sql_connector.py` 🚧 Phase 2
- File Connectors ✅ CSV/Excel/JSON

#### Core Components
- `rag_data_manager.py` - Orchestration
- `data_transformer.py` - Processing
- `data_quality_validator.py` - Validation
- `data_storage.py` - Persistence
- `data_retrieval.py` - Queries

#### AI Integration
- `ai_connector.py` - OpenAI/HuggingFace
- `premium_data_connectors.py` - ESG Providers

### Database Module (`src/database/`)

#### Adapters
- `mongodb_adapter.py` - Primary DB
- `firebase_adapter.py` - Optional
- `dual_adapter.py` - Multi-DB
- `base_adapter.py` - Interface

#### Services
- `database_service.py` - Singleton
- `mongodb_service.py` - MongoDB Ops
- `graph_manager.py` - Graph Data

#### Initialization
- `init_all_data.py` - Setup
- `init_lookthrough_data.py` - Lookthrough
- `populate_mock_data.py` - Test Data

### Frontend Module (`src/frontend/`)

#### Routes
- `lensiq.py` - /storytelling - AI Narratives
- `trendradar.py` - /trends - Radar Viz
- `strategy_direct_flask.py` - /strategy - Frameworks
- `api.py` - /api - REST API

#### Templates
- `lensiq/` - storytelling.html
- `fin_radar/` - radar.html
- `strategy/` - strategy_hub.html
- `components/` - Shared UI

#### Static Assets
- `css/` - Styles
- `js/` - Scripts
- `images/` - Assets

#### Utils
- `navigation_config.py` - Nav Structure
- `gemini_search.py` - AI Search
- `strategy_ai_consultant.py` - AI Advisor
- `cache.py` - Caching

### Lookthrough Module (`src/lookthrough/`)
- `entity_traversal.py` - Graph Navigation
- `metrics_propagator.py` - Metric Calc

---

## 🛠️ Technology Stack

### Backend
- Python 3.11+
- Flask 3.0.3
- PyMongo
- PRAW (Reddit)
- discord.py

### AI/ML
- OpenAI GPT-4
- scikit-learn
- PyTorch (planned)
- transformers (planned)
- VADER
- TextBlob

### Database
- MongoDB 8.0.5
- Redis (optional)
- Vector DB (optional)

### Frontend
- HTML5/CSS3
- JavaScript (ES6+)
- Chart.js
- Bootstrap

---

## 🔌 API Endpoints

### Health Check
```
GET /api/health
Response: {"status": "ok"}
```

### Storytelling
```
GET /storytelling/
POST /storytelling/api/generate-story
```

### TrendRadar
```
GET /trends/
GET /trends/api/radar-data
```

### Strategy
```
GET /strategy/
GET /strategy/frameworks
```

---

## 💾 Database Schema

### Collections

#### trends
```json
{
  "_id": "ObjectId",
  "title": "string",
  "description": "string",
  "category": "string",
  "score": "number",
  "sentiment": "number",
  "source": "string",
  "created_at": "datetime"
}
```

#### stories
```json
{
  "_id": "ObjectId",
  "title": "string",
  "content": "string",
  "topic": "string",
  "ai_generated": "boolean",
  "created_at": "datetime"
}
```

---

## 📊 Mermaid Diagrams

See the rendered diagrams in the repository documentation or use the following Mermaid code:

### System Architecture Diagram

\`\`\`mermaid
graph TB
    subgraph "External Data Sources"
        Reddit[Reddit API]
        Discord[Discord Bot]
        LinkedIn[LinkedIn API]
        SQL[(SQL Databases)]
        Files[File Uploads]
    end
    
    subgraph "Data Ingestion Layer"
        RedditConn[Reddit Connector]
        DiscordConn[Discord Connector]
        LinkedInConn[LinkedIn Connector]
        SQLConn[SQL Connector]
        FileConn[File Connectors]
    end
    
    subgraph "Data Processing Pipeline"
        DataManager[RAG Data Manager]
        Transformer[Data Transformer]
        Validator[Data Quality Validator]
    end
    
    subgraph "AI/ML Processing Layer"
        AIConnector[AI Connector]
        Sentiment[Sentiment Analysis]
        TrendDetect[Trend Detection]
        Anomaly[Anomaly Detection]
        Clustering[Trend Clustering]
    end
    
    subgraph "Data Storage Layer"
        MongoDB[(MongoDB)]
        VectorDB[(Vector DB)]
        Cache[Redis Cache]
    end
    
    subgraph "Application Layer"
        App[Flask Application]
        DBService[Database Service]
        DBAdapter[Database Adapter]
    end
    
    subgraph "API & Route Layer"
        API[API Routes]
        LensIQ[LensIQ Routes]
        TrendRadar[TrendRadar Routes]
        Strategy[Strategy Routes]
    end
    
    subgraph "Frontend Layer"
        StoryUI[Storytelling UI]
        RadarUI[TrendRadar UI]
        StrategyUI[Strategy Hub UI]
        Dashboard[Dashboard]
    end
    
    Reddit --> RedditConn --> DataManager
    Discord --> DiscordConn --> DataManager
    LinkedIn -.-> LinkedInConn -.-> DataManager
    SQL -.-> SQLConn -.-> DataManager
    Files --> FileConn --> DataManager
    
    DataManager --> Transformer --> Validator
    
    Validator --> AIConnector --> MongoDB
    Validator --> Sentiment --> MongoDB
    Validator --> TrendDetect -.-> MongoDB
    Validator --> Anomaly -.-> MongoDB
    Validator --> Clustering -.-> MongoDB
    
    MongoDB --> DBAdapter --> DBService --> App
    
    App --> API --> Dashboard
    App --> LensIQ --> StoryUI
    App --> TrendRadar --> RadarUI
    App --> Strategy --> StrategyUI
\`\`\`

---

## 📈 Data Flow

1. **User Request** → Flask App → Route Handler
2. **Route Handler** → Data Manager → Check Cache
3. **Cache Miss** → Data Connectors (parallel fetch)
4. **Raw Data** → Transform & Clean → Validate Quality
5. **Validated Data** → AI/ML Processing (parallel)
6. **Enriched Data** → Store in MongoDB → Update Cache
7. **Processed Data** → Route Handler → Render Template
8. **Response** → User Browser

---

## 🔐 Security

- Environment variables for API keys
- No hardcoded credentials
- Input validation and sanitization
- Session-based authentication
- HTTPS in production

---

## 📚 Additional Resources

- README.md - Quick start guide
- SPLIT_REPOSITORY_GUIDE.md - Repository setup
- docs/api_documentation.md - API docs
- docs/README.md - Development guide

---

**Last Updated:** 2025-12-02  
**Version:** 1.0.0  
**Maintained by:** LensIQ Development Team

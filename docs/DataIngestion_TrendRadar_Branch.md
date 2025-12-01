# LensIQ Data Ingestion & TrendRadar Branch

**Branch:** `LensIQ_DataIngestion_TrendRadar`  
**Focus:** Structured & unstructured data ingestion + ML-powered trend analysis  
**Created:** December 1, 2025

---

## 🎯 Branch Scope

This branch focuses exclusively on:

1. **Data Ingestion** - Ingest structured and unstructured data from multiple sources
2. **TrendRadar** - ML/AI-powered dynamic trend assessment and visualization

### What's Included ✅

- **Data Sources:**
  - Reddit (unstructured social data)
  - LinkedIn (professional network data)
  - Discord (community discussions)
  - SQL databases (structured data)
  - MongoDB (document data)
  - CSV/Excel/JSON files
  - REST APIs

- **TrendRadar Features:**
  - Machine learning trend detection
  - AI-powered trend analysis (OpenAI GPT)
  - Dynamic metric assessment
  - Real-time trend visualization
  - Client-specific metric prioritization
  - Predictive trend forecasting

### What's Excluded ❌

- Storytelling module
- Strategy Hub
- VC Lens
- Graph Analytics
- Lookthrough
- Lifecycle
- AI Copilot (except for trend analysis)

---

## 🏗️ Architecture

### Core Components

```
LensIQ_DataIngestion_TrendRadar/
├── Data Ingestion Layer
│   ├── Social Media Connectors (Reddit, LinkedIn, Discord)
│   ├── Database Connectors (SQL, MongoDB)
│   ├── File Connectors (CSV, Excel, JSON)
│   ├── API Connectors (REST, GraphQL)
│   └── Data Quality Validation
│
├── Data Processing Layer
│   ├── Structured Data Pipeline
│   ├── Unstructured Data Pipeline (NLP)
│   ├── Data Transformation & Enrichment
│   ├── ML Feature Extraction
│   └── Petastorm ML Pipeline
│
├── TrendRadar Engine
│   ├── ML Trend Detection (Scikit-learn)
│   ├── AI Trend Analysis (OpenAI GPT)
│   ├── Trend Scoring & Ranking
│   ├── Predictive Forecasting
│   └── Client Metric Prioritization
│
└── Visualization Layer
    ├── Interactive Radar Chart
    ├── Trend Timeline
    ├── Metric Dashboard
    └── Real-time Updates
```

---

## 📊 Data Sources

### 1. Reddit Connector (Unstructured)

**Purpose:** Capture community sentiment, emerging trends, discussions

**Data Points:**
- Subreddit posts and comments
- Upvotes, engagement metrics
- Sentiment analysis
- Topic extraction
- Trend momentum

**Implementation:**
- PRAW (Python Reddit API Wrapper)
- Real-time streaming
- Historical data retrieval
- Sentiment analysis with transformers

### 2. LinkedIn Connector (Structured/Unstructured)

**Purpose:** Professional insights, industry trends, thought leadership

**Data Points:**
- Company updates
- Industry news
- Professional discussions
- Job market trends
- Skill trends

**Implementation:**
- LinkedIn API
- Web scraping (where permitted)
- NLP for content analysis
- Network analysis

### 3. Discord Connector (Unstructured)

**Purpose:** Community discussions, real-time sentiment, niche trends

**Data Points:**
- Server messages
- Channel activity
- User engagement
- Topic trends
- Community sentiment

**Implementation:**
- Discord.py bot
- Real-time message streaming
- Historical message retrieval
- Sentiment and topic analysis

### 4. SQL Databases (Structured)

**Purpose:** Traditional relational data, transactional data

**Data Points:**
- Company financials
- ESG metrics
- Performance indicators
- Historical trends

**Implementation:**
- SQLAlchemy ORM
- Support for PostgreSQL, MySQL, SQL Server
- Query optimization
- Connection pooling

### 5. MongoDB (Document Data)

**Purpose:** Flexible schema data, aggregated metrics

**Data Points:**
- ESG documents
- Trend data
- Aggregated metrics
- Time-series data

**Implementation:**
- PyMongo driver
- Aggregation pipelines
- Change streams for real-time updates
- Efficient indexing

---

## 🤖 TrendRadar ML/AI Features

### 1. Machine Learning Trend Detection

**Models:**
- **Time Series Analysis:** ARIMA, Prophet for trend forecasting
- **Anomaly Detection:** Isolation Forest for unusual patterns
- **Clustering:** K-means for trend grouping
- **Classification:** Random Forest for trend categorization

**Features:**
- Automated trend identification
- Trend strength scoring
- Momentum calculation
- Seasonality detection
- Outlier identification

### 2. AI-Powered Trend Analysis

**OpenAI GPT Integration:**
- Natural language trend descriptions
- Trend impact assessment
- Competitive analysis
- Risk/opportunity identification
- Client-specific insights

**Capabilities:**
- Generate executive summaries
- Explain complex trends in simple terms
- Identify cross-trend correlations
- Recommend actions based on trends

### 3. Dynamic Metric Assessment

**Client-Specific Prioritization:**
- Industry-specific metrics
- Company size considerations
- Geographic relevance
- Regulatory requirements
- Strategic priorities

**Metric Categories:**
- Environmental (carbon, energy, water, waste)
- Social (diversity, safety, community)
- Governance (board, ethics, transparency)
- Financial (revenue, growth, profitability)
- Operational (efficiency, innovation, quality)

### 4. Real-Time Trend Visualization

**Interactive Radar Chart:**
- Multi-dimensional trend display
- Customizable axes
- Drill-down capabilities
- Time-based animation
- Export functionality

**Dashboard Features:**
- Top trending topics
- Emerging trends
- Declining trends
- Trend correlations
- Predictive forecasts

---

## 🔧 Technical Stack

### Data Ingestion
- **Reddit:** `praw` 7.7.1
- **LinkedIn:** `linkedin-api` (unofficial)
- **Discord:** `discord.py` 2.3.2
- **SQL:** `sqlalchemy` 2.0.23, `psycopg2` 2.9.9
- **MongoDB:** `pymongo` 4.8.0
- **Files:** `pandas` 2.2.2, `openpyxl` 3.1.2

### ML/AI
- **Machine Learning:** `scikit-learn` 1.5.1
- **Time Series:** `prophet` 1.1.5, `statsmodels` 0.14.1
- **NLP:** `sentence-transformers` 3.0.1, `transformers` 4.40.0
- **AI:** `openai` 1.40.0
- **ML Pipeline:** `petastorm` 0.12.1 (optional)

### Data Processing
- **Data Manipulation:** `pandas` 2.2.2, `numpy` 1.26.4
- **Async Processing:** `asyncio`, `aiohttp` 3.9.5
- **Task Queue:** `celery` 5.4.0, `redis` 5.0.4

### Visualization
- **Charts:** Chart.js 4.4.0
- **Real-time:** WebSockets
- **Export:** `matplotlib` 3.8.4, `plotly` 5.20.0

---

## 📁 File Structure

```
src/
├── data_management/
│   ├── connectors/
│   │   ├── reddit_connector.py          # NEW
│   │   ├── linkedin_connector.py        # NEW
│   │   ├── discord_connector.py         # NEW
│   │   ├── sql_connector.py             # NEW
│   │   ├── mongodb_connector.py         # Enhanced
│   │   ├── data_source_connector.py     # Existing
│   │   └── premium_data_connectors.py   # Existing
│   ├── pipelines/
│   │   ├── structured_pipeline.py       # NEW
│   │   ├── unstructured_pipeline.py     # NEW
│   │   ├── petastorm_pipeline.py        # Existing
│   │   └── data_quality_validator.py    # Existing
│   └── rag_data_manager.py              # Existing
│
├── analytics/
│   ├── trend_detection/
│   │   ├── ml_trend_detector.py         # NEW
│   │   ├── time_series_analyzer.py      # NEW
│   │   ├── anomaly_detector.py          # NEW
│   │   └── trend_scorer.py              # NEW
│   ├── ai_analysis/
│   │   ├── trend_analyzer.py            # Enhanced
│   │   ├── gpt_insights.py              # NEW
│   │   └── metric_prioritizer.py        # NEW
│   └── advanced_scoring.py              # Existing
│
├── frontend/
│   ├── routes/
│   │   └── trendradar.py                # Enhanced
│   ├── templates/
│   │   └── fin_radar/
│   │       └── fin_trendradar.html      # Enhanced
│   └── static/
│       └── js/
│           └── trend_radar.js           # Enhanced
│
└── database/
    ├── database_service.py              # Existing
    └── adapters/
        └── dual_adapter.py              # Existing
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Additional dependencies for this branch
pip install praw discord.py linkedin-api sqlalchemy psycopg2-binary prophet statsmodels
```

### 2. Configure API Keys

Create `.env` file:

```bash
# Social Media APIs
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=LensIQ/1.0

DISCORD_BOT_TOKEN=your_discord_bot_token

LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# Database Connections
MONGODB_URI=mongodb://localhost:27017/lensiq
POSTGRES_URI=postgresql://user:pass@localhost:5432/lensiq

# AI/ML
OPENAI_API_KEY=your_openai_api_key

# Premium Data (Optional)
REFINITIV_API_KEY=your_refinitiv_key
BLOOMBERG_API_KEY=your_bloomberg_key
```

### 3. Run Data Ingestion

```bash
# Start data ingestion workers
python -m src.data_management.ingestion_worker

# Or run specific connectors
python -m src.data_management.connectors.reddit_connector
python -m src.data_management.connectors.discord_connector
```

### 4. Launch TrendRadar

```bash
# Start Flask application
python app.py

# Navigate to TrendRadar
open http://localhost:5000/trends
```

---

## 📈 Roadmap

### Phase 1: Data Connectors (Week 1-2)
- [ ] Implement Reddit connector
- [ ] Implement LinkedIn connector
- [ ] Implement Discord connector
- [ ] Implement SQL connector
- [ ] Enhance MongoDB connector

### Phase 2: Data Pipelines (Week 3-4)
- [ ] Build structured data pipeline
- [ ] Build unstructured data pipeline (NLP)
- [ ] Integrate data quality validation
- [ ] Set up async processing with Celery

### Phase 3: ML Trend Detection (Week 5-6)
- [ ] Implement time series analysis
- [ ] Build anomaly detection
- [ ] Create trend scoring algorithm
- [ ] Add predictive forecasting

### Phase 4: AI Analysis (Week 7-8)
- [ ] Integrate OpenAI GPT for insights
- [ ] Build metric prioritization engine
- [ ] Create client-specific customization
- [ ] Add trend correlation analysis

### Phase 5: Enhanced Visualization (Week 9-10)
- [ ] Upgrade radar chart with real-time data
- [ ] Add interactive drill-down
- [ ] Build metric dashboard
- [ ] Implement export functionality

---

*Last Updated: December 1, 2025*


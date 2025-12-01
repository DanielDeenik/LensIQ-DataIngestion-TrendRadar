# LensIQ Data Ingestion & TrendRadar

**Branch:** `LensIQ_DataIngestion_TrendRadar`  
**Focus:** Structured & Unstructured Data Ingestion + ML-Powered Trend Analysis  
**Status:** In Development

---

## 🎯 Overview

This branch is a focused implementation of LensIQ that concentrates on two core capabilities:

1. **Multi-Source Data Ingestion** - Ingest structured and unstructured data from diverse sources
2. **TrendRadar** - ML/AI-powered dynamic trend detection and visualization

### Key Differentiators

- **Unstructured Data Support** - Reddit, LinkedIn, Discord
- **Structured Data Support** - SQL, MongoDB, CSV, Excel, JSON
- **Real-Time Processing** - Async data ingestion with Celery
- **ML-Powered Analysis** - Time series, anomaly detection, predictive forecasting
- **AI Insights** - OpenAI GPT for trend interpretation
- **Dynamic Visualization** - Interactive radar charts with real-time updates

---

## 📊 Data Sources

### Social Media (Unstructured)

| Source | Type | Data Points | Status |
|--------|------|-------------|--------|
| **Reddit** | Community discussions | Posts, comments, sentiment, engagement | ✅ Implemented |
| **LinkedIn** | Professional insights | Company updates, industry news, trends | 🚧 In Progress |
| **Discord** | Community chat | Messages, reactions, topics | ✅ Implemented |

### Databases (Structured)

| Source | Type | Use Case | Status |
|--------|------|----------|--------|
| **MongoDB** | Document DB | ESG data, trends, metrics | ✅ Implemented |
| **PostgreSQL** | Relational DB | Financial data, transactions | 🚧 In Progress |
| **MySQL** | Relational DB | Legacy data integration | 🚧 In Progress |

### Files (Structured)

| Format | Use Case | Status |
|--------|----------|--------|
| **CSV** | Bulk data import | ✅ Implemented |
| **Excel** | Spreadsheet data | ✅ Implemented |
| **JSON** | API responses, configs | ✅ Implemented |

---

## 🤖 TrendRadar Features

### Machine Learning

- **Time Series Analysis** - ARIMA, Prophet for trend forecasting
- **Anomaly Detection** - Isolation Forest for unusual patterns
- **Clustering** - K-means for trend grouping
- **Classification** - Random Forest for trend categorization

### AI-Powered Insights

- **Natural Language Descriptions** - GPT-generated trend summaries
- **Impact Assessment** - AI-evaluated business impact
- **Competitive Analysis** - Cross-trend correlation
- **Risk/Opportunity Identification** - Automated alerts

### Dynamic Metrics

- **Client-Specific Prioritization** - Industry, size, geography
- **Real-Time Scoring** - Continuous trend strength assessment
- **Predictive Forecasting** - 30-day trend predictions
- **Confidence Intervals** - Statistical confidence levels

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements-dataingestion.txt

# Or install core dependencies only
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
# Social Media APIs
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=LensIQ/1.0

DISCORD_BOT_TOKEN=your_discord_bot_token

LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# Databases
MONGODB_URI=mongodb://localhost:27017/lensiq
POSTGRES_URI=postgresql://user:pass@localhost:5432/lensiq
REDIS_URL=redis://localhost:6379/0

# AI/ML
OPENAI_API_KEY=your_openai_api_key

# Optional: Premium Data
REFINITIV_API_KEY=your_refinitiv_key
BLOOMBERG_API_KEY=your_bloomberg_key
```

### 3. Start Services

```bash
# Start MongoDB
mongod --dbpath /path/to/data

# Start Redis (for Celery)
redis-server

# Start Celery worker (for async tasks)
celery -A src.data_management.celery_app worker --loglevel=info

# Start Flask application
python app.py
```

### 4. Access TrendRadar

```bash
# Open in browser
open http://localhost:5000/trends
```

---

## 📁 Project Structure

```
LensIQ_DataIngestion_TrendRadar/
├── src/
│   ├── data_management/
│   │   ├── connectors/
│   │   │   ├── reddit_connector.py          ✅ NEW
│   │   │   ├── discord_connector.py         ✅ NEW
│   │   │   ├── linkedin_connector.py        🚧 TODO
│   │   │   ├── sql_connector.py             🚧 TODO
│   │   │   └── mongodb_connector.py         ✅ Enhanced
│   │   ├── pipelines/
│   │   │   ├── structured_pipeline.py       🚧 TODO
│   │   │   ├── unstructured_pipeline.py     🚧 TODO
│   │   │   └── petastorm_pipeline.py        ✅ Existing
│   │   └── rag_data_manager.py              ✅ Existing
│   │
│   ├── analytics/
│   │   ├── trend_detection/
│   │   │   ├── ml_trend_detector.py         🚧 TODO
│   │   │   ├── time_series_analyzer.py      🚧 TODO
│   │   │   └── anomaly_detector.py          🚧 TODO
│   │   └── advanced_scoring.py              ✅ Existing
│   │
│   └── frontend/
│       ├── routes/
│       │   └── trendradar.py                ✅ Enhanced
│       └── templates/
│           └── fin_radar/
│               └── fin_trendradar.html      ✅ Enhanced
│
├── docs/
│   └── DataIngestion_TrendRadar_Branch.md   ✅ Documentation
│
├── requirements-dataingestion.txt           ✅ Dependencies
└── README_DataIngestion_TrendRadar.md       ✅ This file
```

---

## 🔧 Usage Examples

### Ingest Reddit Data

```python
from src.data_management.connectors.reddit_connector import get_reddit_connector

# Initialize connector
reddit = get_reddit_connector()

# Get posts from subreddit
posts = reddit.get_subreddit_posts(
    subreddit_name='sustainability',
    limit=100,
    time_filter='week',
    sort_by='hot'
)

# Search for specific topics
esg_posts = reddit.search_subreddit(
    subreddit_name='investing',
    query='ESG',
    limit=50
)
```

### Ingest Discord Data

```python
from src.data_management.connectors.discord_connector import collect_discord_data

# Collect messages from channels
messages = await collect_discord_data(
    channel_ids=[123456789, 987654321],
    limit=100
)

# Process messages
for msg in messages:
    print(f"{msg.author}: {msg.content}")
```

### Run TrendRadar Analysis

```python
from src.frontend.routes.trendradar import TrendRadarRoute

# Initialize TrendRadar
radar = TrendRadarRoute()

# Get ML-powered trends
trends = radar._get_ml_powered_trends()

# Get trend predictions
predictions = radar._get_trend_predictions()
```

---

## 📈 Development Roadmap

### ✅ Phase 1: Foundation (Completed)
- [x] Create branch
- [x] Document architecture
- [x] Implement Reddit connector
- [x] Implement Discord connector
- [x] Create requirements file

### 🚧 Phase 2: Data Connectors (In Progress)
- [ ] Implement LinkedIn connector
- [ ] Implement SQL connector
- [ ] Enhance MongoDB connector
- [ ] Add data quality validation
- [ ] Create unified ingestion API

### 📅 Phase 3: Data Pipelines (Planned)
- [ ] Build structured data pipeline
- [ ] Build unstructured data pipeline (NLP)
- [ ] Integrate sentiment analysis
- [ ] Add async processing with Celery
- [ ] Implement data caching

### 📅 Phase 4: ML Trend Detection (Planned)
- [ ] Implement time series analysis (ARIMA, Prophet)
- [ ] Build anomaly detection (Isolation Forest)
- [ ] Create trend scoring algorithm
- [ ] Add predictive forecasting
- [ ] Implement trend clustering

### 📅 Phase 5: AI Analysis (Planned)
- [ ] Integrate OpenAI GPT for insights
- [ ] Build metric prioritization engine
- [ ] Create client-specific customization
- [ ] Add trend correlation analysis
- [ ] Implement automated alerts

### 📅 Phase 6: Enhanced Visualization (Planned)
- [ ] Upgrade radar chart with real-time data
- [ ] Add interactive drill-down
- [ ] Build metric dashboard
- [ ] Implement export functionality
- [ ] Add mobile responsiveness

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_reddit_connector.py

# Run with coverage
pytest --cov=src --cov-report=html
```

---

## 📚 Documentation

- **Branch Overview:** `docs/DataIngestion_TrendRadar_Branch.md`
- **API Documentation:** Coming soon
- **User Guide:** Coming soon

---

## 🤝 Contributing

This is a focused development branch. Key areas for contribution:

1. **Data Connectors** - Add new social media or database connectors
2. **ML Models** - Improve trend detection algorithms
3. **AI Insights** - Enhance GPT prompts and analysis
4. **Visualization** - Improve TrendRadar UI/UX
5. **Testing** - Add comprehensive test coverage

---

## 📝 Notes

### Design Decisions

1. **Async-First** - All data ingestion uses async/await for performance
2. **Mock Fallbacks** - Graceful degradation when APIs unavailable
3. **Modular Architecture** - Easy to add new data sources
4. **ML Pipeline** - Petastorm for large-scale ML (optional)
5. **Client-Focused** - Dynamic metric prioritization per client

### Known Limitations

- LinkedIn connector requires unofficial API (rate limits apply)
- Discord requires bot token (must be added to servers)
- Reddit API has rate limits (60 requests/minute)
- ML models require training data (using mock data initially)

---

## 🔗 Links

- **Main Repository:** https://github.com/DanielDeenik/TrendSense
- **Project Board:** https://github.com/users/DanielDeenik/projects/4
- **Issues:** https://github.com/DanielDeenik/TrendSense/issues

---

**Last Updated:** December 1, 2025  
**Branch Status:** Active Development  
**Next Milestone:** Complete Phase 2 (Data Connectors)


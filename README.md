# LensIQ Data Ingestion & TrendRadar

> **AI-Powered Data Ingestion and Trend Analysis Platform**

A focused implementation of LensIQ that specializes in multi-source data ingestion (structured and unstructured) and ML/AI-powered trend detection through the TrendRadar module.

---

## 🎯 Overview

**LensIQ Data Ingestion & TrendRadar** is an enterprise-grade platform designed to:

1. **Ingest data from multiple sources** - Reddit, Discord, LinkedIn, SQL databases, MongoDB, CSV, JSON
2. **Analyze trends using ML/AI** - Machine learning algorithms and AI-powered insights
3. **Visualize insights dynamically** - Interactive TrendRadar with client-specific metrics
4. **Provide actionable intelligence** - Help companies identify emerging trends and opportunities

---

## ✨ Key Features

### 📊 **Multi-Source Data Ingestion**

- **Social Media:** Reddit, Discord, LinkedIn
- **Databases:** MongoDB, PostgreSQL, MySQL
- **Files:** CSV, Excel, JSON
- **Real-time & Batch Processing**
- **Automated Data Quality Validation**

### 🤖 **ML/AI-Powered Analysis**

- **Time Series Analysis** - ARIMA, Prophet forecasting
- **Anomaly Detection** - Isolation Forest algorithms
- **Trend Clustering** - K-means, DBSCAN
- **Sentiment Analysis** - NLP-powered sentiment scoring
- **AI Insights** - OpenAI GPT-powered trend interpretation

### 📡 **TrendRadar Visualization**

- **Interactive Radar Chart** - Dynamic trend visualization
- **Client-Specific Metrics** - Customizable KPIs
- **Priority Categorization** - Act/Prepare/Watch zones
- **Real-time Updates** - Live data integration
- **Export Capabilities** - PDF, CSV, JSON exports

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB 8.0+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar.git
cd LensIQ-DataIngestion-TrendRadar

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and database settings

# Start MongoDB (if not running)
mongod --dbpath /usr/local/var/mongodb --fork

# Launch the application
./start_lensiq.sh
# Or manually: python3 app.py
```

### Access the Application

- **TrendRadar:** http://localhost:5050/trends
- **Main Dashboard:** http://localhost:5050/
- **API Health:** http://localhost:5050/api/health

---

## 📁 Project Structure

```
LensIQ-DataIngestion-TrendRadar/
├── app.py                          # Main Flask application
├── start_lensiq.sh                 # Startup script
├── requirements.txt                # Python dependencies
├── .env                            # Environment configuration
│
├── src/
│   ├── data_management/
│   │   ├── connectors/             # Data source connectors
│   │   │   ├── reddit_connector.py      ✅ Reddit API integration
│   │   │   ├── discord_connector.py     ✅ Discord bot integration
│   │   │   ├── linkedin_connector.py    🚧 LinkedIn (planned)
│   │   │   └── sql_connector.py         🚧 SQL databases (planned)
│   │   │
│   │   └── pipelines/              # Data processing pipelines
│   │       ├── structured_pipeline.py   🚧 Structured data (planned)
│   │       └── unstructured_pipeline.py 🚧 Unstructured data (planned)
│   │
│   ├── analytics/
│   │   ├── trend_detection/        # ML trend detection
│   │   │   ├── time_series_analyzer.py  🚧 ARIMA, Prophet (planned)
│   │   │   ├── anomaly_detector.py      🚧 Isolation Forest (planned)
│   │   │   └── trend_scorer.py          🚧 Trend scoring (planned)
│   │   │
│   │   └── ai_analysis/            # AI-powered insights
│   │       ├── gpt_insights.py          🚧 OpenAI GPT (planned)
│   │       └── metric_prioritizer.py    🚧 Metric ranking (planned)
│   │
│   ├── frontend/
│   │   ├── routes/
│   │   │   └── trendradar.py       ✅ TrendRadar routes
│   │   └── templates/
│   │       └── trendradar.html     ✅ TrendRadar UI
│   │
│   ├── database/
│   │   └── database_service.py     ✅ MongoDB integration
│   │
│   └── config/
│       └── production_config.py    ✅ Configuration management
│
├── docs/
│   ├── DataIngestion_TrendRadar_Branch.md  # Architecture documentation
│   └── API.md                              # API documentation
│
└── tests/                          # Unit and integration tests
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
LENSIQ_DATABASE_ADAPTER=mongodb
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=lensiq

# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key
PORT=5050

# Social Media APIs
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
DISCORD_BOT_TOKEN=your_discord_bot_token
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# AI Services
OPENAI_API_KEY=your_openai_api_key
```

### API Credentials Setup

- **Reddit:** https://www.reddit.com/prefs/apps
- **Discord:** https://discord.com/developers/applications
- **OpenAI:** https://platform.openai.com/api-keys

---

## 📊 Data Sources

| Source | Status | Implementation | Use Case |
|--------|--------|----------------|----------|
| **Reddit** | ✅ Complete | `reddit_connector.py` | Community discussions, sentiment |
| **Discord** | ✅ Complete | `discord_connector.py` | Real-time community chat |
| **LinkedIn** | 🚧 Planned | Phase 2 | Professional insights, B2B trends |
| **SQL** | 🚧 Planned | Phase 2 | Structured business data |
| **MongoDB** | ✅ Complete | Existing | Document storage, aggregation |
| **CSV/Excel** | ✅ Complete | Existing | File uploads, batch imports |
| **JSON** | ✅ Complete | Existing | API responses, exports |

---

## 🤖 Machine Learning Features

### Current Capabilities ✅

- Data quality validation
- Basic trend categorization
- ESG scoring algorithms
- Mock data generation for testing

### Planned Enhancements 🚧

- **Time Series Forecasting** - ARIMA, Prophet, LSTM
- **Anomaly Detection** - Isolation Forest, One-Class SVM
- **Clustering** - K-means, DBSCAN for trend grouping
- **Sentiment Analysis** - BERT, RoBERTa models
- **Predictive Analytics** - Trend forecasting
- **AI Insights** - GPT-powered trend interpretation

---

## 📈 Development Roadmap

### Phase 1: Foundation ✅ **COMPLETE**
- [x] Reddit connector
- [x] Discord connector
- [x] MongoDB integration
- [x] Basic TrendRadar UI
- [x] Documentation

### Phase 2: Data Connectors 🚧 **IN PROGRESS**
- [ ] LinkedIn connector
- [ ] SQL connector (PostgreSQL, MySQL)
- [ ] Enhanced MongoDB features
- [ ] Data quality validation
- [ ] Unified ingestion API

### Phase 3: Data Pipelines 📋 **PLANNED**
- [ ] Structured data pipeline
- [ ] Unstructured data pipeline with NLP
- [ ] Sentiment analysis integration
- [ ] Async processing with Celery
- [ ] Data caching layer

### Phase 4: ML Trend Detection 📋 **PLANNED**
- [ ] Time series analysis (ARIMA, Prophet)
- [ ] Anomaly detection (Isolation Forest)
- [ ] Trend scoring algorithm
- [ ] Predictive forecasting
- [ ] Trend clustering

### Phase 5: AI Analysis 📋 **PLANNED**
- [ ] OpenAI GPT integration
- [ ] Metric prioritization engine
- [ ] Client-specific customization
- [ ] Trend correlation analysis
- [ ] Automated alerts

### Phase 6: Enhanced Visualization 📋 **PLANNED**
- [ ] Real-time radar updates
- [ ] Interactive drill-down
- [ ] Metric dashboard
- [ ] Export functionality
- [ ] Mobile responsiveness

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_connectors.py

# Run with coverage
pytest --cov=src tests/
```

---

## 📚 Documentation

- **Architecture:** [docs/DataIngestion_TrendRadar_Branch.md](docs/DataIngestion_TrendRadar_Branch.md)
- **Quick Start:** [README_DataIngestion_TrendRadar.md](README_DataIngestion_TrendRadar.md)

---

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Related Projects

- **LensIQ Platform:** https://github.com/DanielDeenik/TrendSense
- **GitHub Projects Board:** https://github.com/users/DanielDeenik/projects/4

---

## 📧 Contact

**Daniel Deenik**
- GitHub: [@DanielDeenik](https://github.com/DanielDeenik)
- Project: [LensIQ Data Ingestion & TrendRadar](https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar)

---

## 🙏 Acknowledgments

Built with:
- Flask 3.0.3
- MongoDB 8.0.5
- PyTorch 2.2.2
- Scikit-learn 1.5.1
- OpenAI GPT-4
- And many other amazing open-source projects

---

**Made with ❤️ for data-driven decision making**

# LensIQ API Documentation

## Overview

LensIQ provides a comprehensive REST API for ESG (Environmental, Social, Governance) data analysis with AI-powered insights. The API is designed for enterprise use with robust authentication, rate limiting, and comprehensive error handling.

## Base URL

```
Production: https://api.lensiq.ai/api/v1
Development: http://localhost:5000/api/v1
```

## Authentication

All API endpoints (except health checks) require authentication using API keys.

### API Key Authentication

Include your API key in the request header:

```http
X-LensIQ-API-Key: your_api_key_here
```

### Getting an API Key

Contact your LensIQ administrator to obtain an API key with appropriate permissions.

## Rate Limiting

API requests are rate-limited based on your subscription tier:

- **Standard**: 1,000 requests/minute, 10,000 requests/hour
- **Premium**: 5,000 requests/minute, 50,000 requests/hour  
- **Enterprise**: 10,000 requests/minute, 100,000 requests/hour

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Response Format

All API responses follow a consistent JSON format:

```json
{
  "status": "success|error",
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00Z",
  "message": "Optional message"
}
```

## Error Handling

HTTP status codes indicate the result of your request:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

Error responses include details:

```json
{
  "status": "error",
  "message": "Error description",
  "error": "Detailed error information",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Endpoints

### Health & Status

#### GET /health
Public health check endpoint.

**Response:**
```json
{
  "status": "success",
  "data": {
    "overall_status": "healthy",
    "checks": [...],
    "system_metrics": {...}
  }
}
```

#### GET /readiness
Kubernetes readiness probe.

#### GET /liveness
Kubernetes liveness probe.

### Authentication

#### GET /auth/status
Get current authentication status.

**Headers:**
- `X-LensIQ-API-Key: required`

**Response:**
```json
{
  "status": "success",
  "data": {
    "authenticated": true,
    "user_id": "user123",
    "organization": "acme_corp",
    "tier": "premium",
    "permissions": ["esg_data_access", "ai_analysis"],
    "rate_limit": 5000
  }
}
```

### ESG Data

#### GET /esg/companies/{company_id}/data
Get ESG data for a specific company.

**Headers:**
- `X-LensIQ-API-Key: required`

**Permissions:** `esg_data_access`

**Parameters:**
- `company_id` (path): Company identifier
- `sources` (query): Data sources to include (optional)
- `start_date` (query): Start date (ISO format, optional)
- `end_date` (query): End date (ISO format, optional)

**Example:**
```http
GET /esg/companies/AAPL/data?sources=refinitiv,bloomberg&start_date=2024-01-01
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "company_id": "AAPL",
    "records": [
      {
        "company_id": "AAPL",
        "timestamp": "2024-01-15T10:30:00Z",
        "data_source": "refinitiv",
        "environmental_score": 85.5,
        "social_score": 78.2,
        "governance_score": 92.1,
        "combined_score": 85.3,
        "carbon_intensity": 45.2,
        "data_quality_score": 0.95
      }
    ],
    "count": 1,
    "date_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-15T23:59:59Z"
    }
  }
}
```

#### POST /esg/validate
Validate ESG data quality.

**Headers:**
- `X-LensIQ-API-Key: required`

**Permissions:** `data_validation`

**Request Body:**
```json
{
  "data_source": "refinitiv",
  "records": [
    {
      "company_id": "AAPL",
      "environmental_score": 85.5,
      "social_score": 78.2,
      "governance_score": 92.1
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "overall_score": 0.95,
    "dimension_scores": {
      "completeness": 1.0,
      "validity": 0.95,
      "consistency": 0.92
    },
    "validation_results": [...],
    "record_count": 1
  }
}
```

### Machine Learning

#### POST /ml/datasets
Create ML-ready dataset from ESG data.

**Headers:**
- `X-LensIQ-API-Key: required`

**Permissions:** `ml_dataset_creation`
**Tier:** Premium or Enterprise

**Request Body:**
```json
{
  "company_ids": ["AAPL", "MSFT", "GOOGL"],
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "validation_split": 0.2,
  "test_split": 0.1
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "datasets": {
      "train": "/path/to/train_dataset",
      "validation": "/path/to/val_dataset",
      "test": "/path/to/test_dataset"
    },
    "statistics": {
      "train": {
        "total_records": 800,
        "unique_companies": 3
      }
    }
  }
}
```

### AI-Powered Analysis

#### POST /ai/analysis
Create AI-powered ESG analysis using MCP.

**Headers:**
- `X-LensIQ-API-Key: required`

**Permissions:** `ai_analysis`
**Tier:** Premium or Enterprise

**Request Body:**
```json
{
  "company_ids": ["AAPL", "MSFT"],
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "analysis_type": "comprehensive",
  "analysis_depth": "detailed"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "session_123",
    "analysis": {
      "response_type": "analysis",
      "content": {
        "key_insights": [
          "Strong environmental performance across portfolio",
          "Governance scores show consistent improvement"
        ],
        "risk_assessment": {
          "high_risks": ["Climate transition risk"],
          "risk_score": 25
        },
        "confidence_score": 0.88
      },
      "processing_time_ms": 2500
    }
  }
}
```

#### POST /ai/narrative
Generate AI-powered narrative using MCP.

**Headers:**
- `X-LensIQ-API-Key: required`

**Permissions:** `narrative_generation`
**Tier:** Premium or Enterprise

**Request Body:**
```json
{
  "session_id": "session_123",
  "narrative_style": "executive_summary"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "session_123",
    "narrative": {
      "response_type": "narrative",
      "content": {
        "title": "ESG Performance Executive Summary",
        "executive_summary": "Portfolio demonstrates strong ESG fundamentals...",
        "main_narrative": "Detailed narrative content...",
        "key_messages": [
          "Environmental leadership position",
          "Strong governance framework"
        ],
        "confidence_score": 0.92
      }
    }
  }
}
```

#### GET /ai/sessions/{session_id}
Get AI analysis session details.

**Headers:**
- `X-LensIQ-API-Key: required`

**Permissions:** `ai_analysis`

**Response:**
```json
{
  "status": "success",
  "data": {
    "session": {
      "session_id": "session_123",
      "context_type": "esg_analysis",
      "data_sources": ["refinitiv", "bloomberg"],
      "parameters": {...}
    },
    "history": [
      {
        "response_type": "analysis",
        "timestamp": "2024-01-15T10:30:00Z"
      }
    ],
    "total_responses": 2
  }
}
```

### Analytics

#### GET /analytics/trends
Get ESG trends analysis with optional AI enhancement.

**Headers:**
- `X-LensIQ-API-Key: required`

**Permissions:** `analytics_access`

**Parameters:**
- `sector` (query): Industry sector filter
- `region` (query): Geographic region filter
- `timeframe` (query): Time period (1y, 2y, 5y)
- `metrics` (query): Specific metrics to analyze
- `use_ai` (query): Enable AI enhancement (premium/enterprise only)

**Response:**
```json
{
  "status": "success",
  "data": {
    "trends": {
      "environmental": {
        "direction": "improving",
        "confidence": 0.85,
        "key_drivers": ["renewable_energy", "carbon_reduction"]
      }
    },
    "ai_enhanced": true,
    "ai_insights": {
      "market_outlook": "ESG performance increasingly important...",
      "confidence_score": 0.88
    }
  }
}
```

### Configuration

#### GET /config/info
Get non-sensitive configuration information.

**Headers:**
- `X-LensIQ-API-Key: required`

**Permissions:** `admin`

**Response:**
```json
{
  "status": "success",
  "data": {
    "environment": "production",
    "api": {
      "version": "v1",
      "rate_limit_per_minute": 1000
    },
    "data_sources": {
      "refinitiv": {
        "enabled": true,
        "rate_limit": 100
      }
    }
  }
}
```

## SDKs and Libraries

### Python SDK

```python
from lensiq import LensIQClient

client = LensIQClient(api_key="your_api_key")

# Get ESG data
esg_data = client.get_company_esg_data("AAPL")

# Create AI analysis
analysis = client.create_ai_analysis(
    company_ids=["AAPL", "MSFT"],
    analysis_type="comprehensive"
)
```

### JavaScript SDK

```javascript
import { LensIQClient } from '@lensiq/sdk';

const client = new LensIQClient({ apiKey: 'your_api_key' });

// Get ESG data
const esgData = await client.getCompanyESGData('AAPL');

// Create AI analysis
const analysis = await client.createAIAnalysis({
  companyIds: ['AAPL', 'MSFT'],
  analysisType: 'comprehensive'
});
```

## Webhooks

LensIQ supports webhooks for real-time notifications:

### Events

- `data.updated` - New ESG data available
- `analysis.completed` - AI analysis finished
- `quality.alert` - Data quality issue detected

### Webhook Payload

```json
{
  "event": "data.updated",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "company_id": "AAPL",
    "data_source": "refinitiv",
    "quality_score": 0.95
  }
}
```

## Best Practices

### Performance

1. **Batch Requests**: Use batch endpoints when possible
2. **Caching**: Cache responses for frequently accessed data
3. **Pagination**: Use pagination for large datasets
4. **Compression**: Enable gzip compression

### Security

1. **API Key Security**: Store API keys securely, never in client-side code
2. **HTTPS**: Always use HTTPS in production
3. **Rate Limiting**: Implement client-side rate limiting
4. **Error Handling**: Handle all error responses gracefully

### Data Quality

1. **Validation**: Always validate data before processing
2. **Quality Scores**: Monitor data quality scores
3. **Source Diversity**: Use multiple data sources when available
4. **Freshness**: Check data timestamps for currency

## Support

- **Documentation**: https://docs.lensiq.ai
- **API Status**: https://status.lensiq.ai
- **Support**: support@lensiq.ai
- **GitHub**: https://github.com/lensiq/api-examples

## Changelog

### v1.0.0 (2024-01-15)
- Initial API release
- ESG data endpoints
- AI-powered analysis with MCP
- ML dataset creation
- Comprehensive authentication and rate limiting

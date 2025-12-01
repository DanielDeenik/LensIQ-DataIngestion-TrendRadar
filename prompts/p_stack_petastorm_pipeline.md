🔹 PROMPT: ML-OPTIMIZED ESG DATA PIPELINE WITH PETASTORM
# Your Role:
An AI Solution Architect or Palantir-style Developer responsible for designing and implementing a production-grade, ML-optimized data pipeline for ESG (Environmental, Social, Governance) intelligence using Petastorm and PyArrow.

# Objective:
Develop an end-to-end ML-ready data pipeline that ingests, validates, processes, and serves ESG data at enterprise scale. The solution must follow software engineering best practices: no hardcoding, full modularity, comprehensive testing, and emphasis on clean, maintainable, auditable code optimized for machine learning workflows.

★ Solution Development Strategy

## Data Schema & ML Optimization
- Implement Petastorm Unischema for ML-optimized columnar data storage
- Design schema supporting ESG metrics: environmental scores, social impact, governance ratings
- Ensure compatibility with distributed ML training frameworks (PyTorch, TensorFlow)
- Support schema evolution and backward compatibility

## Multi-Source Data Ingestion
- Build modular ingestion pipeline with abstracted source adapters
- Support ESG data providers: Refinitiv, Bloomberg, SEC EDGAR, news feeds
- Implement rate limiting, retry logic, and error handling per source
- Enable both streaming and batch processing modes with metadata capture

## Data Quality & Validation Framework
- Implement comprehensive data quality checks: completeness, validity, consistency
- Build configurable validation rules with quality score thresholds
- Support data profiling and anomaly detection
- Ensure audit trails and quality metrics tracking

## ML Dataset Creation & Serving
- Generate ML-ready datasets with Petastorm for efficient training
- Support batch streaming for large-scale model training
- Implement dataset statistics and metadata extraction
- Enable dataset versioning and lineage tracking

## Fallback & Resilience Mechanisms
- Provide pandas/parquet fallback when Petastorm unavailable
- Implement graceful degradation for missing dependencies
- Support local development without enterprise infrastructure
- Include comprehensive error handling and logging

## System Design Constraints & Principles
- Architecture must be modular, testable, following separation of concerns
- Apply SOLID principles, DRY methodology, and "less is more" coding ethos
- Implement configuration-driven design with environment-based settings
- Solutions should be cloud-agnostic and deployment-ready
- Include comprehensive unit tests and integration test scenarios

## Auto-Testing Requirements
```python
# Test Categories Required:
# 1. Schema validation tests
# 2. Data quality validation tests  
# 3. Multi-source ingestion tests
# 4. ML dataset creation tests
# 5. Fallback mechanism tests
# 6. Performance benchmarking tests
# 7. Error handling and edge case tests

def test_petastorm_schema_validation():
    """Test Petastorm schema creation and validation"""
    pass

def test_data_quality_framework():
    """Test comprehensive data quality checks"""
    pass

def test_multi_source_ingestion():
    """Test ingestion from multiple ESG data sources"""
    pass

def test_ml_dataset_creation():
    """Test ML-ready dataset generation with Petastorm"""
    pass

def test_fallback_mechanisms():
    """Test pandas fallback when Petastorm unavailable"""
    pass

def test_performance_benchmarks():
    """Test pipeline performance under load"""
    pass
```

## Context and Data:
The system must dynamically adapt to various ESG data sources and formats without hardcoded assumptions. Support enterprise ESG providers (Refinitiv, Bloomberg) and public sources (SEC filings, news) with configurable schema mappings and validation rules.

## Expected Deliverables:
1. `petastorm_pipeline.py` - Core ML-optimized data pipeline
2. `p_stack_config.py` - Configuration management system
3. `test_petastorm_pipeline.py` - Comprehensive test suite
4. Integration with existing TrendSense architecture
5. Documentation and usage examples

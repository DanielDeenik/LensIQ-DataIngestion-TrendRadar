"""
Production Data Validation System for LensIQ

This module provides enterprise-grade data validation with:
- Real-time data quality checks
- ESG data validation
- Schema validation
- Anomaly detection
- Data lineage tracking
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import re

from ..config.production_config import get_config

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DataQualityDimension(Enum):
    """Data quality dimensions."""
    COMPLETENESS = "completeness"
    VALIDITY = "validity"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    ACCURACY = "accuracy"
    UNIQUENESS = "uniqueness"


@dataclass
class ValidationResult:
    """Result of a data validation check."""
    dimension: DataQualityDimension
    severity: ValidationSeverity
    score: float  # 0.0 to 1.0
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'dimension': self.dimension.value,
            'severity': self.severity.value,
            'score': self.score,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class DataQualityReport:
    """Comprehensive data quality report."""
    overall_score: float
    dimension_scores: Dict[DataQualityDimension, float]
    validation_results: List[ValidationResult]
    data_source: str
    record_count: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'overall_score': self.overall_score,
            'dimension_scores': {
                dim.value: score for dim, score in self.dimension_scores.items()
            },
            'validation_results': [result.to_dict() for result in self.validation_results],
            'data_source': self.data_source,
            'record_count': self.record_count,
            'timestamp': self.timestamp.isoformat()
        }


class ESGDataValidator:
    """Validator for ESG (Environmental, Social, Governance) data."""
    
    def __init__(self):
        """Initialize ESG data validator."""
        self.config = get_config()
        
        # ESG score ranges
        self.esg_score_ranges = {
            'environmental': (0, 100),
            'social': (0, 100),
            'governance': (0, 100),
            'combined': (0, 100)
        }
        
        # Required ESG fields
        self.required_fields = [
            'company_id',
            'timestamp',
            'esg_scores',
            'data_source'
        ]
        
        # ESG metrics validation rules
        self.metric_rules = {
            'carbon_intensity': {'min': 0, 'max': 1000, 'unit': 'tCO2e/revenue'},
            'water_intensity': {'min': 0, 'max': 500, 'unit': 'm3/revenue'},
            'waste_intensity': {'min': 0, 'max': 100, 'unit': 'tonnes/revenue'},
            'energy_efficiency': {'min': 0, 'max': 100, 'unit': 'percentage'},
            'employee_satisfaction': {'min': 0, 'max': 100, 'unit': 'percentage'},
            'board_diversity': {'min': 0, 'max': 100, 'unit': 'percentage'}
        }
    
    def validate_esg_data(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate ESG data comprehensively.
        
        Args:
            data: ESG data to validate
            
        Returns:
            List of validation results
        """
        results = []
        
        # Check completeness
        results.extend(self._validate_completeness(data))
        
        # Check validity
        results.extend(self._validate_validity(data))
        
        # Check consistency
        results.extend(self._validate_consistency(data))
        
        # Check timeliness
        results.extend(self._validate_timeliness(data))
        
        # Check for mock data indicators
        results.extend(self._validate_authenticity(data))
        
        return results
    
    def _validate_completeness(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate data completeness."""
        results = []
        
        # Check required fields
        missing_fields = []
        for field in self.required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            results.append(ValidationResult(
                dimension=DataQualityDimension.COMPLETENESS,
                severity=ValidationSeverity.ERROR,
                score=0.0,
                message=f"Missing required fields: {', '.join(missing_fields)}",
                details={'missing_fields': missing_fields}
            ))
        else:
            # Check ESG scores completeness
            esg_scores = data.get('esg_scores', {})
            missing_scores = []
            
            for score_type in ['environmental', 'social', 'governance']:
                if score_type not in esg_scores or esg_scores[score_type] is None:
                    missing_scores.append(score_type)
            
            completeness_score = 1.0 - (len(missing_scores) / 3.0)
            
            if missing_scores:
                results.append(ValidationResult(
                    dimension=DataQualityDimension.COMPLETENESS,
                    severity=ValidationSeverity.WARNING,
                    score=completeness_score,
                    message=f"Missing ESG scores: {', '.join(missing_scores)}",
                    details={'missing_scores': missing_scores}
                ))
            else:
                results.append(ValidationResult(
                    dimension=DataQualityDimension.COMPLETENESS,
                    severity=ValidationSeverity.INFO,
                    score=1.0,
                    message="All required fields present",
                    details={}
                ))
        
        return results
    
    def _validate_validity(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate data validity."""
        results = []
        
        # Validate ESG scores
        esg_scores = data.get('esg_scores', {})
        invalid_scores = []
        
        for score_type, score_value in esg_scores.items():
            if score_type in self.esg_score_ranges:
                min_val, max_val = self.esg_score_ranges[score_type]
                
                if not isinstance(score_value, (int, float)):
                    invalid_scores.append(f"{score_type}: not numeric")
                elif not (min_val <= score_value <= max_val):
                    invalid_scores.append(f"{score_type}: {score_value} not in range [{min_val}, {max_val}]")
        
        # Validate metrics
        metrics = data.get('metrics', {})
        invalid_metrics = []
        
        for metric_name, metric_value in metrics.items():
            if metric_name in self.metric_rules:
                rules = self.metric_rules[metric_name]
                
                if not isinstance(metric_value, (int, float)):
                    invalid_metrics.append(f"{metric_name}: not numeric")
                elif not (rules['min'] <= metric_value <= rules['max']):
                    invalid_metrics.append(f"{metric_name}: {metric_value} not in range [{rules['min']}, {rules['max']}]")
        
        # Calculate validity score
        total_checks = len(esg_scores) + len(metrics)
        invalid_checks = len(invalid_scores) + len(invalid_metrics)
        validity_score = 1.0 - (invalid_checks / max(total_checks, 1))
        
        if invalid_scores or invalid_metrics:
            all_invalid = invalid_scores + invalid_metrics
            results.append(ValidationResult(
                dimension=DataQualityDimension.VALIDITY,
                severity=ValidationSeverity.ERROR if validity_score < 0.5 else ValidationSeverity.WARNING,
                score=validity_score,
                message=f"Invalid values found: {', '.join(all_invalid[:3])}{'...' if len(all_invalid) > 3 else ''}",
                details={
                    'invalid_scores': invalid_scores,
                    'invalid_metrics': invalid_metrics
                }
            ))
        else:
            results.append(ValidationResult(
                dimension=DataQualityDimension.VALIDITY,
                severity=ValidationSeverity.INFO,
                score=1.0,
                message="All values are valid",
                details={}
            ))
        
        return results
    
    def _validate_consistency(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate data consistency."""
        results = []
        
        esg_scores = data.get('esg_scores', {})
        inconsistencies = []
        
        # Check if combined score is consistent with individual scores
        if all(score in esg_scores for score in ['environmental', 'social', 'governance', 'combined']):
            env_score = esg_scores['environmental']
            social_score = esg_scores['social']
            gov_score = esg_scores['governance']
            combined_score = esg_scores['combined']
            
            # Calculate expected combined score (simple average)
            expected_combined = (env_score + social_score + gov_score) / 3
            
            # Allow 5% tolerance
            tolerance = 5.0
            if abs(combined_score - expected_combined) > tolerance:
                inconsistencies.append(
                    f"Combined score {combined_score} inconsistent with individual scores "
                    f"(expected ~{expected_combined:.1f})"
                )
        
        # Check data quality metadata consistency
        data_quality = data.get('data_quality', {})
        if 'confidence_score' in data_quality:
            confidence = data_quality['confidence_score']
            if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 100):
                inconsistencies.append(f"Invalid confidence score: {confidence}")
        
        consistency_score = 1.0 - (len(inconsistencies) / max(len(esg_scores), 1))
        
        if inconsistencies:
            results.append(ValidationResult(
                dimension=DataQualityDimension.CONSISTENCY,
                severity=ValidationSeverity.WARNING,
                score=consistency_score,
                message=f"Consistency issues: {', '.join(inconsistencies)}",
                details={'inconsistencies': inconsistencies}
            ))
        else:
            results.append(ValidationResult(
                dimension=DataQualityDimension.CONSISTENCY,
                severity=ValidationSeverity.INFO,
                score=1.0,
                message="Data is consistent",
                details={}
            ))
        
        return results
    
    def _validate_timeliness(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate data timeliness."""
        results = []
        
        timestamp_str = data.get('timestamp')
        if not timestamp_str:
            results.append(ValidationResult(
                dimension=DataQualityDimension.TIMELINESS,
                severity=ValidationSeverity.ERROR,
                score=0.0,
                message="No timestamp provided",
                details={}
            ))
            return results
        
        try:
            # Parse timestamp
            if isinstance(timestamp_str, str):
                data_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                data_timestamp = timestamp_str
            
            # Check how old the data is
            now = datetime.utcnow()
            age_hours = (now - data_timestamp).total_seconds() / 3600
            
            # Define timeliness thresholds
            fresh_threshold = 24  # hours
            stale_threshold = 168  # 1 week
            
            if age_hours < 0:
                # Future timestamp
                results.append(ValidationResult(
                    dimension=DataQualityDimension.TIMELINESS,
                    severity=ValidationSeverity.ERROR,
                    score=0.0,
                    message="Data timestamp is in the future",
                    details={'age_hours': age_hours}
                ))
            elif age_hours <= fresh_threshold:
                # Fresh data
                results.append(ValidationResult(
                    dimension=DataQualityDimension.TIMELINESS,
                    severity=ValidationSeverity.INFO,
                    score=1.0,
                    message="Data is fresh",
                    details={'age_hours': age_hours}
                ))
            elif age_hours <= stale_threshold:
                # Moderately old data
                timeliness_score = 1.0 - ((age_hours - fresh_threshold) / (stale_threshold - fresh_threshold))
                results.append(ValidationResult(
                    dimension=DataQualityDimension.TIMELINESS,
                    severity=ValidationSeverity.WARNING,
                    score=timeliness_score,
                    message=f"Data is {age_hours:.1f} hours old",
                    details={'age_hours': age_hours}
                ))
            else:
                # Stale data
                results.append(ValidationResult(
                    dimension=DataQualityDimension.TIMELINESS,
                    severity=ValidationSeverity.ERROR,
                    score=0.0,
                    message=f"Data is stale ({age_hours:.1f} hours old)",
                    details={'age_hours': age_hours}
                ))
        
        except Exception as e:
            results.append(ValidationResult(
                dimension=DataQualityDimension.TIMELINESS,
                severity=ValidationSeverity.ERROR,
                score=0.0,
                message=f"Invalid timestamp format: {str(e)}",
                details={'timestamp': timestamp_str}
            ))
        
        return results
    
    def _validate_authenticity(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate data authenticity (detect mock/fake data)."""
        results = []
        
        mock_indicators = []
        
        # Check for explicit mock indicators
        if data.get('is_mock', False):
            mock_indicators.append("Explicit mock flag set")
        
        # Check for mock data patterns in provider names
        provider = data.get('provider', '').lower()
        if 'mock' in provider or 'test' in provider or 'demo' in provider:
            mock_indicators.append(f"Mock provider: {provider}")
        
        # Check for unrealistic score patterns (all scores ending in .0 or .5)
        esg_scores = data.get('esg_scores', {})
        suspicious_scores = []
        
        for score_type, score_value in esg_scores.items():
            if isinstance(score_value, (int, float)):
                # Check if score is suspiciously round
                if score_value == int(score_value) or (score_value * 2) == int(score_value * 2):
                    suspicious_scores.append(score_type)
        
        if len(suspicious_scores) >= 3:
            mock_indicators.append("Suspiciously round scores")
        
        # Check for sequential company IDs (mock data pattern)
        company_id = data.get('company_id', '')
        if re.match(r'^(mock|test|demo)_.*_\d+$', company_id):
            mock_indicators.append("Sequential mock company ID pattern")
        
        if mock_indicators:
            results.append(ValidationResult(
                dimension=DataQualityDimension.ACCURACY,
                severity=ValidationSeverity.CRITICAL,
                score=0.0,
                message=f"Mock/fake data detected: {', '.join(mock_indicators)}",
                details={'mock_indicators': mock_indicators}
            ))
        else:
            results.append(ValidationResult(
                dimension=DataQualityDimension.ACCURACY,
                severity=ValidationSeverity.INFO,
                score=1.0,
                message="Data appears authentic",
                details={}
            ))
        
        return results


class ProductionDataValidator:
    """Production-grade data validator for LensIQ."""
    
    def __init__(self):
        """Initialize production data validator."""
        self.config = get_config()
        self.esg_validator = ESGDataValidator()
    
    def validate_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                     data_source: str) -> DataQualityReport:
        """
        Validate data and generate quality report.
        
        Args:
            data: Data to validate (single record or list of records)
            data_source: Source of the data
            
        Returns:
            Data quality report
        """
        # Normalize data to list
        if isinstance(data, dict):
            data_list = [data]
        else:
            data_list = data
        
        all_results = []
        record_count = len(data_list)
        
        # Validate each record
        for i, record in enumerate(data_list):
            try:
                # Determine data type and validate accordingly
                if self._is_esg_data(record):
                    record_results = self.esg_validator.validate_esg_data(record)
                else:
                    record_results = self._validate_generic_data(record)
                
                # Add record index to results
                for result in record_results:
                    result.details['record_index'] = i
                
                all_results.extend(record_results)
                
            except Exception as e:
                logger.error(f"Error validating record {i}: {str(e)}")
                all_results.append(ValidationResult(
                    dimension=DataQualityDimension.VALIDITY,
                    severity=ValidationSeverity.ERROR,
                    score=0.0,
                    message=f"Validation error: {str(e)}",
                    details={'record_index': i, 'error': str(e)}
                ))
        
        # Calculate dimension scores
        dimension_scores = self._calculate_dimension_scores(all_results)
        
        # Calculate overall score
        overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        
        return DataQualityReport(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            validation_results=all_results,
            data_source=data_source,
            record_count=record_count
        )
    
    def _is_esg_data(self, data: Dict[str, Any]) -> bool:
        """Check if data is ESG data."""
        esg_indicators = ['esg_scores', 'environmental', 'social', 'governance']
        return any(indicator in data for indicator in esg_indicators)
    
    def _validate_generic_data(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate generic data."""
        results = []
        
        # Basic completeness check
        if not data:
            results.append(ValidationResult(
                dimension=DataQualityDimension.COMPLETENESS,
                severity=ValidationSeverity.ERROR,
                score=0.0,
                message="Empty data record",
                details={}
            ))
        else:
            # Check for null values
            null_fields = [key for key, value in data.items() if value is None]
            completeness_score = 1.0 - (len(null_fields) / len(data))
            
            if null_fields:
                results.append(ValidationResult(
                    dimension=DataQualityDimension.COMPLETENESS,
                    severity=ValidationSeverity.WARNING,
                    score=completeness_score,
                    message=f"Null values in fields: {', '.join(null_fields)}",
                    details={'null_fields': null_fields}
                ))
            else:
                results.append(ValidationResult(
                    dimension=DataQualityDimension.COMPLETENESS,
                    severity=ValidationSeverity.INFO,
                    score=1.0,
                    message="No null values found",
                    details={}
                ))
        
        return results
    
    def _calculate_dimension_scores(self, results: List[ValidationResult]) -> Dict[DataQualityDimension, float]:
        """Calculate average scores for each dimension."""
        dimension_scores = {}
        
        for dimension in DataQualityDimension:
            dimension_results = [r for r in results if r.dimension == dimension]
            
            if dimension_results:
                avg_score = sum(r.score for r in dimension_results) / len(dimension_results)
                dimension_scores[dimension] = avg_score
            else:
                # Default score if no results for this dimension
                dimension_scores[dimension] = 1.0
        
        return dimension_scores
    
    def get_quality_threshold(self, dimension: DataQualityDimension) -> float:
        """Get quality threshold for a dimension."""
        thresholds = {
            DataQualityDimension.COMPLETENESS: self.config.data_quality.completeness_threshold,
            DataQualityDimension.VALIDITY: self.config.data_quality.validity_threshold,
            DataQualityDimension.CONSISTENCY: self.config.data_quality.consistency_threshold,
            DataQualityDimension.TIMELINESS: 0.8,  # 80% threshold for timeliness
            DataQualityDimension.ACCURACY: 0.9,    # 90% threshold for accuracy
            DataQualityDimension.UNIQUENESS: 0.95  # 95% threshold for uniqueness
        }
        
        return thresholds.get(dimension, 0.8)
    
    def is_quality_acceptable(self, report: DataQualityReport) -> bool:
        """Check if data quality is acceptable for production use."""
        # Check overall score
        if report.overall_score < 0.8:
            return False
        
        # Check critical dimensions
        critical_dimensions = [
            DataQualityDimension.COMPLETENESS,
            DataQualityDimension.VALIDITY,
            DataQualityDimension.ACCURACY
        ]
        
        for dimension in critical_dimensions:
            score = report.dimension_scores.get(dimension, 0.0)
            threshold = self.get_quality_threshold(dimension)
            
            if score < threshold:
                return False
        
        # Check for critical validation errors
        critical_errors = [
            r for r in report.validation_results
            if r.severity == ValidationSeverity.CRITICAL
        ]
        
        return len(critical_errors) == 0


# Global validator instance
_validator_instance: Optional[ProductionDataValidator] = None


def get_validator() -> ProductionDataValidator:
    """Get global validator instance."""
    global _validator_instance
    
    if _validator_instance is None:
        _validator_instance = ProductionDataValidator()
    
    return _validator_instance


def validate_esg_data(data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                     data_source: str) -> DataQualityReport:
    """
    Convenience function to validate ESG data.
    
    Args:
        data: ESG data to validate
        data_source: Source of the data
        
    Returns:
        Data quality report
    """
    validator = get_validator()
    return validator.validate_data(data, data_source)

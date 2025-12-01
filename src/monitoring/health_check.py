"""
Production Health Check System for LensIQ

This module provides comprehensive health monitoring with:
- Database connectivity checks
- Data source availability
- API endpoint health
- System resource monitoring
- Performance metrics
"""

import os
import time
import psutil
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import aiohttp

from ..config.production_config import get_config
from ..database.database_service import DatabaseService

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    component: str
    status: HealthStatus
    message: str
    response_time_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'component': self.component,
            'status': self.status.value,
            'message': self.message,
            'response_time_ms': self.response_time_ms,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    uptime_seconds: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'disk_percent': self.disk_percent,
            'network_io': self.network_io,
            'process_count': self.process_count,
            'uptime_seconds': self.uptime_seconds,
            'timestamp': self.timestamp.isoformat()
        }


class DatabaseHealthChecker:
    """Health checker for database connectivity."""
    
    def __init__(self):
        """Initialize database health checker."""
        self.db_service = DatabaseService()
    
    def check_health(self) -> HealthCheckResult:
        """Check database health."""
        start_time = time.time()
        
        try:
            # Check basic connectivity
            if not self.db_service.is_connected():
                return HealthCheckResult(
                    component="database",
                    status=HealthStatus.CRITICAL,
                    message="Database not connected",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Test basic operations
            test_collection = "health_check"
            test_doc = {
                "test": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Insert test document
            doc_id = self.db_service.insert_one(test_collection, test_doc)
            if not doc_id:
                return HealthCheckResult(
                    component="database",
                    status=HealthStatus.UNHEALTHY,
                    message="Failed to insert test document",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Read test document
            retrieved_doc = self.db_service.find_one(test_collection, {"_id": doc_id})
            if not retrieved_doc:
                return HealthCheckResult(
                    component="database",
                    status=HealthStatus.UNHEALTHY,
                    message="Failed to retrieve test document",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Delete test document
            deleted = self.db_service.delete_one(test_collection, {"_id": doc_id})
            if not deleted:
                logger.warning("Failed to delete test document")
            
            response_time = (time.time() - start_time) * 1000
            
            # Check response time
            if response_time > 5000:  # 5 seconds
                status = HealthStatus.WARNING
                message = f"Database responding slowly ({response_time:.0f}ms)"
            elif response_time > 1000:  # 1 second
                status = HealthStatus.WARNING
                message = f"Database response time elevated ({response_time:.0f}ms)"
            else:
                status = HealthStatus.HEALTHY
                message = "Database is healthy"
            
            return HealthCheckResult(
                component="database",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "adapter": self.db_service._adapter.__class__.__name__,
                    "operations_tested": ["insert", "find", "delete"]
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="database",
                status=HealthStatus.CRITICAL,
                message=f"Database health check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )


class DataSourceHealthChecker:
    """Health checker for external data sources."""
    
    def __init__(self):
        """Initialize data source health checker."""
        self.config = get_config()
        self.timeout = 10  # seconds
    
    def check_data_source_health(self, source_name: str) -> HealthCheckResult:
        """Check health of a specific data source."""
        start_time = time.time()
        
        try:
            source_config = self.config.get_data_source(source_name)
            if not source_config:
                return HealthCheckResult(
                    component=f"data_source_{source_name}",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Data source {source_name} not configured",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            if not source_config.enabled:
                return HealthCheckResult(
                    component=f"data_source_{source_name}",
                    status=HealthStatus.WARNING,
                    message=f"Data source {source_name} is disabled",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Check health endpoint if available
            health_url = None
            if source_config.health_check_endpoint:
                health_url = f"{source_config.base_url}{source_config.health_check_endpoint}"
            else:
                # Fallback to base URL
                health_url = source_config.base_url
            
            # Make health check request
            headers = {}
            if source_config.api_key:
                headers['Authorization'] = f"Bearer {source_config.api_key}"
            
            response = requests.get(
                health_url,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Evaluate response
            if response.status_code == 200:
                status = HealthStatus.HEALTHY
                message = f"Data source {source_name} is healthy"
            elif response.status_code in [401, 403]:
                status = HealthStatus.WARNING
                message = f"Data source {source_name} authentication issue"
            elif response.status_code >= 500:
                status = HealthStatus.UNHEALTHY
                message = f"Data source {source_name} server error"
            else:
                status = HealthStatus.WARNING
                message = f"Data source {source_name} unexpected response"
            
            return HealthCheckResult(
                component=f"data_source_{source_name}",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "provider": source_config.provider,
                    "status_code": response.status_code,
                    "url": health_url
                }
            )
            
        except requests.exceptions.Timeout:
            return HealthCheckResult(
                component=f"data_source_{source_name}",
                status=HealthStatus.UNHEALTHY,
                message=f"Data source {source_name} timeout",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": "timeout"}
            )
        except requests.exceptions.ConnectionError:
            return HealthCheckResult(
                component=f"data_source_{source_name}",
                status=HealthStatus.CRITICAL,
                message=f"Data source {source_name} connection failed",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": "connection_error"}
            )
        except Exception as e:
            return HealthCheckResult(
                component=f"data_source_{source_name}",
                status=HealthStatus.CRITICAL,
                message=f"Data source {source_name} health check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    def check_all_data_sources(self) -> List[HealthCheckResult]:
        """Check health of all configured data sources."""
        results = []
        
        for source_name in self.config.data_sources.keys():
            result = self.check_data_source_health(source_name)
            results.append(result)
        
        return results


class SystemHealthChecker:
    """Health checker for system resources."""
    
    def __init__(self):
        """Initialize system health checker."""
        self.start_time = time.time()
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            'bytes_sent': network.bytes_sent,
            'bytes_recv': network.bytes_recv,
            'packets_sent': network.packets_sent,
            'packets_recv': network.packets_recv
        }
        
        # Process count
        process_count = len(psutil.pids())
        
        # Uptime
        uptime_seconds = time.time() - self.start_time
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_io=network_io,
            process_count=process_count,
            uptime_seconds=uptime_seconds
        )
    
    def check_system_health(self) -> List[HealthCheckResult]:
        """Check system health."""
        results = []
        start_time = time.time()
        
        try:
            metrics = self.get_system_metrics()
            response_time = (time.time() - start_time) * 1000
            
            # Check CPU usage
            if metrics.cpu_percent > 90:
                cpu_status = HealthStatus.CRITICAL
                cpu_message = f"CPU usage critical: {metrics.cpu_percent:.1f}%"
            elif metrics.cpu_percent > 80:
                cpu_status = HealthStatus.WARNING
                cpu_message = f"CPU usage high: {metrics.cpu_percent:.1f}%"
            else:
                cpu_status = HealthStatus.HEALTHY
                cpu_message = f"CPU usage normal: {metrics.cpu_percent:.1f}%"
            
            results.append(HealthCheckResult(
                component="system_cpu",
                status=cpu_status,
                message=cpu_message,
                response_time_ms=response_time,
                details={"cpu_percent": metrics.cpu_percent}
            ))
            
            # Check memory usage
            if metrics.memory_percent > 95:
                memory_status = HealthStatus.CRITICAL
                memory_message = f"Memory usage critical: {metrics.memory_percent:.1f}%"
            elif metrics.memory_percent > 85:
                memory_status = HealthStatus.WARNING
                memory_message = f"Memory usage high: {metrics.memory_percent:.1f}%"
            else:
                memory_status = HealthStatus.HEALTHY
                memory_message = f"Memory usage normal: {metrics.memory_percent:.1f}%"
            
            results.append(HealthCheckResult(
                component="system_memory",
                status=memory_status,
                message=memory_message,
                response_time_ms=response_time,
                details={"memory_percent": metrics.memory_percent}
            ))
            
            # Check disk usage
            if metrics.disk_percent > 95:
                disk_status = HealthStatus.CRITICAL
                disk_message = f"Disk usage critical: {metrics.disk_percent:.1f}%"
            elif metrics.disk_percent > 85:
                disk_status = HealthStatus.WARNING
                disk_message = f"Disk usage high: {metrics.disk_percent:.1f}%"
            else:
                disk_status = HealthStatus.HEALTHY
                disk_message = f"Disk usage normal: {metrics.disk_percent:.1f}%"
            
            results.append(HealthCheckResult(
                component="system_disk",
                status=disk_status,
                message=disk_message,
                response_time_ms=response_time,
                details={"disk_percent": metrics.disk_percent}
            ))
            
        except Exception as e:
            results.append(HealthCheckResult(
                component="system_metrics",
                status=HealthStatus.CRITICAL,
                message=f"Failed to get system metrics: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            ))
        
        return results


class ProductionHealthChecker:
    """Comprehensive health checker for LensIQ production environment."""
    
    def __init__(self):
        """Initialize production health checker."""
        self.config = get_config()
        self.db_checker = DatabaseHealthChecker()
        self.data_source_checker = DataSourceHealthChecker()
        self.system_checker = SystemHealthChecker()
    
    def check_all_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        start_time = time.time()
        
        # Collect all health check results
        all_results = []
        
        # Database health
        db_result = self.db_checker.check_health()
        all_results.append(db_result)
        
        # Data source health
        data_source_results = self.data_source_checker.check_all_data_sources()
        all_results.extend(data_source_results)
        
        # System health
        system_results = self.system_checker.check_system_health()
        all_results.extend(system_results)
        
        # Calculate overall health
        overall_status = self._calculate_overall_status(all_results)
        
        # Get system metrics
        system_metrics = self.system_checker.get_system_metrics()
        
        total_time = (time.time() - start_time) * 1000
        
        return {
            'overall_status': overall_status.value,
            'timestamp': datetime.utcnow().isoformat(),
            'total_check_time_ms': total_time,
            'environment': self.config.environment,
            'version': '1.0.0',
            'checks': [result.to_dict() for result in all_results],
            'system_metrics': system_metrics.to_dict(),
            'summary': self._generate_summary(all_results)
        }
    
    def _calculate_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """Calculate overall health status from individual results."""
        if not results:
            return HealthStatus.UNHEALTHY
        
        # Count statuses
        status_counts = {status: 0 for status in HealthStatus}
        for result in results:
            status_counts[result.status] += 1
        
        # Determine overall status
        if status_counts[HealthStatus.CRITICAL] > 0:
            return HealthStatus.CRITICAL
        elif status_counts[HealthStatus.UNHEALTHY] > 0:
            return HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.WARNING] > 0:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def _generate_summary(self, results: List[HealthCheckResult]) -> Dict[str, Any]:
        """Generate summary of health check results."""
        total_checks = len(results)
        status_counts = {status.value: 0 for status in HealthStatus}
        
        for result in results:
            status_counts[result.status.value] += 1
        
        # Calculate average response time
        avg_response_time = sum(r.response_time_ms for r in results) / total_checks if total_checks > 0 else 0
        
        # Identify failing components
        failing_components = [
            r.component for r in results
            if r.status in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY]
        ]
        
        return {
            'total_checks': total_checks,
            'status_counts': status_counts,
            'average_response_time_ms': avg_response_time,
            'failing_components': failing_components,
            'health_score': (status_counts['healthy'] / total_checks * 100) if total_checks > 0 else 0
        }
    
    def check_readiness(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if system is ready to serve requests."""
        # Critical components that must be healthy for readiness
        critical_components = ['database']
        
        health_report = self.check_all_health()
        
        # Check if critical components are healthy
        critical_failures = []
        for check in health_report['checks']:
            component = check['component']
            status = check['status']
            
            if any(critical in component for critical in critical_components):
                if status in ['critical', 'unhealthy']:
                    critical_failures.append(component)
        
        is_ready = len(critical_failures) == 0
        
        readiness_report = {
            'ready': is_ready,
            'timestamp': datetime.utcnow().isoformat(),
            'critical_failures': critical_failures,
            'environment': self.config.environment
        }
        
        return is_ready, readiness_report
    
    def check_liveness(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if system is alive and responding."""
        start_time = time.time()
        
        try:
            # Basic liveness check - just verify we can respond
            response_time = (time.time() - start_time) * 1000
            
            liveness_report = {
                'alive': True,
                'timestamp': datetime.utcnow().isoformat(),
                'response_time_ms': response_time,
                'environment': self.config.environment,
                'uptime_seconds': self.system_checker.get_system_metrics().uptime_seconds
            }
            
            return True, liveness_report
            
        except Exception as e:
            liveness_report = {
                'alive': False,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'environment': self.config.environment
            }
            
            return False, liveness_report


# Global health checker instance
_health_checker_instance: Optional[ProductionHealthChecker] = None


def get_health_checker() -> ProductionHealthChecker:
    """Get global health checker instance."""
    global _health_checker_instance
    
    if _health_checker_instance is None:
        _health_checker_instance = ProductionHealthChecker()
    
    return _health_checker_instance

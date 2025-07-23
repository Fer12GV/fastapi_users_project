from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any
import time
import psutil
import asyncio
from app.db.database import get_db
from app.core.logging_config import logger

router = APIRouter()

class HealthChecker:
    """Health check utilities for monitoring system components"""
    
    @staticmethod
    async def check_database(db: AsyncSession) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        start_time = time.time()
        try:
            # Simple query to test connection
            result = await db.execute(text("SELECT 1"))
            result.fetchone()
            
            # Test write capability
            await db.execute(text("CREATE TEMP TABLE health_check (id INTEGER)"))
            await db.execute(text("INSERT INTO health_check (id) VALUES (1)"))
            await db.execute(text("DROP TABLE health_check"))
            
            duration = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "message": "Database connection successful"
            }
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "response_time_ms": round(duration * 1000, 2),
                "message": f"Database error: {str(e)}"
            }
    
    @staticmethod
    def check_system_resources() -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Define thresholds
            cpu_threshold = 80.0
            memory_threshold = 80.0
            disk_threshold = 90.0
            
            status = "healthy"
            issues = []
            
            if cpu_percent > cpu_threshold:
                status = "degraded"
                issues.append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > memory_threshold:
                status = "degraded"
                issues.append(f"High memory usage: {memory.percent}%")
            
            if disk.percent > disk_threshold:
                status = "unhealthy"
                issues.append(f"High disk usage: {disk.percent}%")
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "issues": issues,
                "message": "System resources checked" if not issues else "; ".join(issues)
            }
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"System check error: {str(e)}"
            }
    
    @staticmethod
    async def check_external_dependencies() -> Dict[str, Any]:
        """Check external service dependencies"""
        # This is where you would check external APIs, services, etc.
        # For now, we'll simulate some checks
        
        checks = []
        overall_status = "healthy"
        
        # Example: Check if we can resolve DNS
        try:
            import socket
            socket.gethostbyname('google.com')
            checks.append({
                "service": "DNS Resolution",
                "status": "healthy",
                "message": "DNS resolution working"
            })
        except Exception as e:
            checks.append({
                "service": "DNS Resolution",
                "status": "unhealthy",
                "message": f"DNS error: {str(e)}"
            })
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "checks": checks,
            "message": "External dependencies checked"
        }

@router.get("/health", tags=["Health"])
async def basic_health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "message": "FastAPI Users API is running",
        "timestamp": time.time()
    }

@router.get("/health/detailed", tags=["Health"])
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with all system components"""
    start_time = time.time()
    
    # Run all health checks
    db_health = await HealthChecker.check_database(db)
    system_health = HealthChecker.check_system_resources()
    external_health = await HealthChecker.check_external_dependencies()
    
    # Determine overall status
    statuses = [db_health["status"], system_health["status"], external_health["status"]]
    
    if "unhealthy" in statuses:
        overall_status = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif "degraded" in statuses:
        overall_status = "degraded"
        status_code = status.HTTP_200_OK
    else:
        overall_status = "healthy"
        status_code = status.HTTP_200_OK
    
    total_duration = time.time() - start_time
    
    health_report = {
        "status": overall_status,
        "timestamp": time.time(),
        "total_check_duration_ms": round(total_duration * 1000, 2),
        "components": {
            "database": db_health,
            "system": system_health,
            "external": external_health
        }
    }
    
    # Log health check results
    if overall_status == "unhealthy":
        logger.error(f"Health check failed: {health_report}")
    elif overall_status == "degraded":
        logger.warning(f"Health check degraded: {health_report}")
    else:
        logger.debug(f"Health check passed: {overall_status}")
    
    if status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=status_code, detail=health_report)
    
    return health_report

@router.get("/health/ready", tags=["Health"])
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe endpoint"""
    try:
        # Check if application is ready to serve traffic
        db_health = await HealthChecker.check_database(db)
        
        if db_health["status"] != "healthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Application not ready"
            )
        
        return {"status": "ready", "message": "Application is ready to serve traffic"}
    
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application not ready"
        )

@router.get("/health/live", tags=["Health"])
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    # Simple check to verify the application is alive
    # This should be lightweight and not check external dependencies
    return {"status": "alive", "message": "Application is alive"}

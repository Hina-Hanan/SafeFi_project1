"""
Real-time Monitoring API Endpoints
"""
import logging
import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.realtime_monitor import get_monitor

logger = logging.getLogger("app.api.v1.monitoring")

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Background task reference
_monitoring_task: Optional[asyncio.Task] = None


class MonitorConfigRequest(BaseModel):
    """Request to configure monitoring settings."""
    recipient_email: str = Field(..., description="Email to receive alerts")
    high_risk_threshold: float = Field(70.0, ge=0, le=100, description="High risk threshold (%)")
    medium_risk_threshold: float = Field(40.0, ge=0, le=100, description="Medium risk threshold (%)")
    check_interval_seconds: int = Field(300, ge=60, le=3600, description="Check interval (seconds)")
    notify_high_risk: bool = Field(True, description="Send alerts for high risk")
    notify_medium_risk: bool = Field(False, description="Send alerts for medium risk")


@router.post("/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """
    Start real-time protocol risk monitoring.
    
    Monitors all active protocols and sends email alerts when they exceed thresholds.
    Checks every 5 minutes by default (configurable via env vars).
    """
    global _monitoring_task
    
    monitor = get_monitor()
    
    if monitor.is_running:
        return {
            "success": False,
            "message": "Monitoring is already running",
            "status": monitor.get_status()
        }
    
    # Start monitoring in background
    async def run_monitor():
        await monitor.start_monitoring()
    
    _monitoring_task = asyncio.create_task(run_monitor())
    
    logger.info("🚀 Real-time monitoring started")
    
    return {
        "success": True,
        "message": "Real-time monitoring started",
        "status": monitor.get_status()
    }


@router.post("/stop")
async def stop_monitoring():
    """Stop real-time protocol risk monitoring."""
    global _monitoring_task
    
    monitor = get_monitor()
    
    if not monitor.is_running:
        return {
            "success": False,
            "message": "Monitoring is not running"
        }
    
    monitor.stop_monitoring()
    
    if _monitoring_task:
        _monitoring_task.cancel()
        try:
            await _monitoring_task
        except asyncio.CancelledError:
            pass
        _monitoring_task = None
    
    logger.info("⏹️ Real-time monitoring stopped")
    
    return {
        "success": True,
        "message": "Real-time monitoring stopped"
    }


@router.get("/status")
async def get_monitoring_status():
    """Get current monitoring status and configuration."""
    monitor = get_monitor()
    return {
        "status": monitor.get_status(),
        "email_configured": monitor.email_service.enabled and bool(monitor.email_service.sender_password)
    }


@router.post("/check-now")
async def check_protocols_now():
    """
    Manually trigger an immediate protocol check.
    
    Useful for testing or forcing an immediate check without waiting for the interval.
    """
    monitor = get_monitor()
    
    try:
        await monitor._check_protocols()
        return {
            "success": True,
            "message": "Manual check completed",
            "status": monitor.get_status()
        }
    except Exception as e:
        logger.exception(f"Manual check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Manual check failed: {str(e)}"
        )



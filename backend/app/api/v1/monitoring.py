"""
Monitoring and Status API Endpoints

Provides endpoints to monitor the automated scheduler and subscriber alert system.
"""
import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.automated_scheduler import get_scheduler
from app.services.subscriber_alert_service import get_subscriber_alert_service
from app.services.email_alert_service import get_email_service

logger = logging.getLogger("app.api.v1.monitoring")

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


class SchedulerStatusResponse(BaseModel):
    """Scheduler status information."""
    is_running: bool
    update_count: int
    last_update_time: str | None
    next_scheduled_run: str | None
    active_jobs: int
    status_message: str


class ForceUpdateRequest(BaseModel):
    """Request to force an immediate update."""
    run_alerts: bool = True


@router.get("/scheduler/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status():
    """
    Get the current status of the automated scheduler.
    
    Returns information about:
    - Whether the scheduler is running
    - Number of updates performed
    - Last update time
    - Next scheduled run time
    """
    try:
        scheduler = get_scheduler()
        status = scheduler.get_status()
        
        status_message = "Scheduler is running normally" if status["is_running"] else "Scheduler is stopped"
        
        return SchedulerStatusResponse(
            is_running=status["is_running"],
            update_count=status["update_count"],
            last_update_time=status["last_update_time"],
            next_scheduled_run=status["next_scheduled_run"],
            active_jobs=status["active_jobs"],
            status_message=status_message
        )
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")


@router.post("/scheduler/force-update")
async def force_immediate_update(request: ForceUpdateRequest = ForceUpdateRequest()):
    """
    Force an immediate data update and alert check.
    
    This bypasses the normal schedule and runs the update cycle immediately.
    Useful for testing or when urgent updates are needed.
    """
    try:
        scheduler = get_scheduler()
        
        if not scheduler.is_running:
            raise HTTPException(
                status_code=503,
                detail="Scheduler is not running. Cannot force update."
            )
        
        # Trigger update cycle
        import asyncio
        asyncio.create_task(scheduler._run_data_update_cycle())
    
    return {
        "success": True,
            "message": "Update cycle initiated",
            "timestamp": datetime.utcnow().isoformat(),
            "run_alerts": request.run_alerts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error forcing update: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to force update: {str(e)}")


@router.get("/alerts/statistics")
def get_alert_statistics(db: Session = Depends(get_db)):
    """
    Get comprehensive statistics about the alert system.
    
    Returns:
    - Total active subscribers
    - Protocols above thresholds
    - Recent alerts sent
    - System health
    """
    try:
        from app.database.models import EmailSubscriber, Protocol, RiskScore
        from sqlalchemy import func, desc
        
        # Get subscriber statistics
        total_subscribers = db.query(EmailSubscriber).filter(
            EmailSubscriber.is_active == True
        ).count()
        
        verified_subscribers = db.query(EmailSubscriber).filter(
            EmailSubscriber.is_active == True,
            EmailSubscriber.is_verified == True
        ).count()
        
        # Get protocol statistics
        total_protocols = db.query(Protocol).filter(Protocol.is_active == True).count()
        
        # Get recent alerts sent (within last hour)
        from datetime import timedelta
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        recent_alerts_count = db.query(EmailSubscriber).filter(
            EmailSubscriber.last_alert_sent >= one_hour_ago
        ).count()
        
        # Get risk level distribution
        risk_distribution = {
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        protocols = db.query(Protocol).filter(Protocol.is_active == True).all()
        for protocol in protocols:
            latest_risk = db.query(RiskScore).filter(
                RiskScore.protocol_id == protocol.id
            ).order_by(desc(RiskScore.timestamp)).first()
            
            if latest_risk:
                risk_distribution[latest_risk.risk_level] += 1
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "subscribers": {
                "total_active": total_subscribers,
                "verified": verified_subscribers,
                "unverified": total_subscribers - verified_subscribers
            },
            "protocols": {
                "total_active": total_protocols,
                "high_risk": risk_distribution["high"],
                "medium_risk": risk_distribution["medium"],
                "low_risk": risk_distribution["low"]
            },
            "alerts": {
                "sent_last_hour": recent_alerts_count
            },
            "system_health": {
                "scheduler_running": get_scheduler().is_running,
                "email_service_enabled": get_email_service().enabled
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting alert statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/alerts/subscriber/{email}/status")
def get_subscriber_alert_status(email: str, db: Session = Depends(get_db)):
    """
    Get detailed alert status for a specific subscriber.
    
    Shows:
    - Current thresholds
    - Protocols above thresholds
    - Time until next alert can be sent
    - Recent alert history
    """
    try:
        alert_service = get_subscriber_alert_service()
        stats = alert_service.get_subscriber_alert_stats(email, db)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscriber status for {email}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.post("/alerts/test/{email}")
def send_test_alert(email: str, db: Session = Depends(get_db)):
    """
    Send a test alert email to verify configuration.
    
    Useful for:
    - Testing SMTP settings
    - Verifying subscriber configuration
    - Debugging email delivery issues
    """
    try:
        alert_service = get_subscriber_alert_service()
        success = alert_service.send_test_alert(email, db)
        
        if success:
            return {
                "success": True,
                "message": f"Test alert sent successfully to {email}",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send test alert. Check SMTP configuration."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test alert to {email}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send test alert: {str(e)}")


@router.post("/scheduler/start")
async def start_scheduler():
    """
    Start the automated scheduler if it's stopped.
    
    This is useful after a manual stop or error recovery.
    """
    try:
        scheduler = get_scheduler()
        
        if scheduler.is_running:
    return {
        "success": True,
                "message": "Scheduler is already running",
                "status": scheduler.get_status()
    }

        await scheduler.start()

    return {
            "success": True,
            "message": "Scheduler started successfully",
            "status": scheduler.get_status()
    }
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")


@router.post("/scheduler/stop")
async def stop_scheduler():
    """
    Stop the automated scheduler.
    
    WARNING: This will stop automatic updates and alerts.
    Use this only for maintenance or debugging.
    """
    try:
        scheduler = get_scheduler()
    
        if not scheduler.is_running:
        return {
            "success": True,
                "message": "Scheduler is already stopped",
                "status": scheduler.get_status()
            }
        
        await scheduler.stop()
        
        return {
            "success": True,
            "message": "Scheduler stopped successfully",
            "status": scheduler.get_status()
        }
        
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")

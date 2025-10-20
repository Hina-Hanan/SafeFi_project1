"""
Email Alerts API Endpoints
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
import re

from app.services.email_alert_service import get_email_service

logger = logging.getLogger("app.api.v1.email_alerts")

router = APIRouter(prefix="/email-alerts", tags=["email-alerts"])


class EmailSubscriptionRequest(BaseModel):
    """Request to subscribe to email alerts."""
    email: str = Field(..., description="Email address to receive alerts")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email address format')
        return v
    high_risk_threshold: float = Field(70.0, ge=0, le=100, description="High risk threshold (%)")
    medium_risk_threshold: float = Field(40.0, ge=0, le=100, description="Medium risk threshold (%)")
    notify_on_high: bool = Field(True, description="Send alerts for high risk")
    notify_on_medium: bool = Field(True, description="Send alerts for medium risk")


class TestAlertRequest(BaseModel):
    """Request to send a test alert email."""
    email: str = Field(..., description="Email address to send test to")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email address format')
        return v


class SendAlertRequest(BaseModel):
    """Request to send an alert for a specific protocol."""
    email: str = Field(..., description="Email address to send alert to")
    protocol_name: str = Field(..., description="Protocol name")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score (%)")
    risk_level: str = Field(..., description="Risk level (low/medium/high)")
    threshold: float = Field(..., ge=0, le=100, description="Threshold that was exceeded")
    alert_type: str = Field("high", description="Alert type (high/medium)")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email address format')
        return v


class BatchAlertRequest(BaseModel):
    """Request to send multiple alerts in one email."""
    email: str = Field(..., description="Email address to send alerts to")
    alerts: List[dict] = Field(..., description="List of alert data")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email address format')
        return v


@router.post("/subscribe")
def subscribe_to_alerts(request: EmailSubscriptionRequest):
    """
    Subscribe an email address to receive risk alerts.
    
    Note: This is a placeholder. In production, you would:
    1. Store subscription in database
    2. Verify email address
    3. Set up automated monitoring
    """
    # For now, just validate the email service is configured
    service = get_email_service()
    
    if not service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email alerts are not enabled. Please configure SMTP settings."
        )
    
    # TODO: Store subscription in database
    logger.info(f"Email subscription request from {request.email}")
    
    return {
        "success": True,
        "message": f"Subscription request received for {request.email}",
        "settings": {
            "email": request.email,
            "high_risk_threshold": request.high_risk_threshold,
            "medium_risk_threshold": request.medium_risk_threshold,
            "notify_on_high": request.notify_on_high,
            "notify_on_medium": request.notify_on_medium
        }
    }


@router.post("/test")
def send_test_alert(request: TestAlertRequest):
    """Send a test alert email to verify email configuration."""
    service = get_email_service()
    
    if not service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email alerts are not enabled. Check SMTP configuration."
        )
    
    # Send test alert
    success = service.send_risk_alert(
        recipient_email=request.email,
        protocol_name="Test Protocol (Uniswap)",
        risk_score=85.5,
        risk_level="high",
        threshold=70.0,
        alert_type="high"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test email. Check server logs."
        )
    
    return {
        "success": True,
        "message": f"Test alert sent to {request.email}"
    }


@router.post("/send-alert")
def send_single_alert(request: SendAlertRequest):
    """Send a risk alert email for a specific protocol."""
    service = get_email_service()
    
    if not service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email alerts are not enabled."
        )
    
    success = service.send_risk_alert(
        recipient_email=request.email,
        protocol_name=request.protocol_name,
        risk_score=request.risk_score,
        risk_level=request.risk_level,
        threshold=request.threshold,
        alert_type=request.alert_type
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send alert email."
        )
    
    return {
        "success": True,
        "message": f"Alert sent to {request.email} for {request.protocol_name}"
    }


@router.post("/send-batch")
def send_batch_alerts(request: BatchAlertRequest):
    """Send multiple alerts in a single email."""
    service = get_email_service()
    
    if not service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email alerts are not enabled."
        )
    
    success = service.send_batch_alerts(
        recipient_email=request.email,
        alerts=request.alerts
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send batch alert email."
        )
    
    return {
        "success": True,
        "message": f"Batch alert sent to {request.email} with {len(request.alerts)} protocol(s)"
    }


@router.get("/status")
def get_email_alert_status():
    """Check if email alerts are configured and enabled."""
    service = get_email_service()
    
    return {
        "enabled": service.enabled,
        "smtp_host": service.smtp_host,
        "smtp_port": service.smtp_port,
        "sender_email": service.sender_email,
        "configured": bool(service.sender_password)
    }


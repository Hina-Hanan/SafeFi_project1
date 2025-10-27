"""
Email Alerts Subscription API Endpoints

Allows users to subscribe to email alerts for protocol risk notifications.
"""
import logging
import secrets
from typing import List
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
import re

from app.database.connection import get_db
from app.database.models import EmailSubscriber, Protocol, RiskScore
from app.services.email_alert_service import get_email_service
from app.services.subscriber_alert_service import get_subscriber_alert_service
from app.services.automated_scheduler import get_scheduler

logger = logging.getLogger("app.api.v1.email_alerts")

router = APIRouter(prefix="/email-alerts", tags=["email-alerts"])


# Request/Response Models
class EmailSubscriptionRequest(BaseModel):
    """Request to subscribe to email alerts."""
    email: str = Field(..., description="Email address to receive alerts")
    high_risk_threshold: float = Field(70.0, ge=0, le=100, description="High risk threshold (%)")
    medium_risk_threshold: float = Field(40.0, ge=0, le=100, description="Medium risk threshold (%)")
    notify_on_high: bool = Field(True, description="Send alerts for high risk")
    notify_on_medium: bool = Field(True, description="Send alerts for medium risk")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email address format')
        return v.lower().strip()


class EmailSubscriptionResponse(BaseModel):
    """Response for subscription operations."""
    success: bool
    message: str
    email: str
    subscriber_id: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class SubscriberInfo(BaseModel):
    """Subscriber information."""
    id: str
    email: str
    is_active: bool
    is_verified: bool
    high_risk_threshold: float
    medium_risk_threshold: float
    notify_on_high: bool
    notify_on_medium: bool
    created_at: datetime
    last_alert_sent: datetime | None = None


class TestAlertRequest(BaseModel):
    """Request to send a test alert email."""
    email: str = Field(..., description="Email address to send test to")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email address format')
        return v.lower().strip()


# API Endpoints
@router.post("/subscribe", response_model=EmailSubscriptionResponse)
def subscribe_to_alerts(
    request: EmailSubscriptionRequest,
    db: Session = Depends(get_db)
):
    """
    Subscribe an email address to receive risk alerts.
    
    - Creates or updates email subscription
    - Generates verification and unsubscribe tokens
    - Sends welcome email
    """
    try:
        # Check if email service is configured
        service = get_email_service()
        if not service.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Email alerts are not enabled. Please configure SMTP settings."
            )
        
        # Check if email already exists
        existing_subscriber = db.query(EmailSubscriber).filter(
            EmailSubscriber.email == request.email
        ).first()
        
        if existing_subscriber:
            # Update existing subscription
            existing_subscriber.is_active = True
            existing_subscriber.high_risk_threshold = request.high_risk_threshold
            existing_subscriber.medium_risk_threshold = request.medium_risk_threshold
            existing_subscriber.notify_on_high = request.notify_on_high
            existing_subscriber.notify_on_medium = request.notify_on_medium
            existing_subscriber.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(existing_subscriber)
            
            logger.info(f"Updated subscription for {request.email}")
            
            return EmailSubscriptionResponse(
                success=True,
                message=f"Subscription updated for {request.email}",
                email=request.email,
                subscriber_id=existing_subscriber.id,
                is_active=existing_subscriber.is_active,
                is_verified=existing_subscriber.is_verified
            )
        
        # Create new subscription
        subscriber = EmailSubscriber(
            email=request.email,
            high_risk_threshold=request.high_risk_threshold,
            medium_risk_threshold=request.medium_risk_threshold,
            notify_on_high=request.notify_on_high,
            notify_on_medium=request.notify_on_medium,
            is_active=True,
            is_verified=True,  # Auto-verify for now (add email verification later)
            verification_token=secrets.token_urlsafe(32),
            unsubscribe_token=secrets.token_urlsafe(32)
        )
        
        db.add(subscriber)
        db.commit()
        db.refresh(subscriber)
        
        logger.info(f"New subscription created for {request.email}")
        
        # Send welcome email
        try:
            service.send_risk_alert(
                recipient_email=request.email,
                protocol_name="Welcome to DeFi Risk Alerts!",
                risk_score=0.0,
                risk_level="low",
                threshold=0.0,
                alert_type="welcome"
            )
        except Exception as e:
            logger.warning(f"Failed to send welcome email to {request.email}: {e}")
        
        return EmailSubscriptionResponse(
            success=True,
            message=f"Successfully subscribed {request.email} to risk alerts",
            email=request.email,
            subscriber_id=subscriber.id,
            is_active=subscriber.is_active,
            is_verified=subscriber.is_verified
        )
        
    except Exception as e:
        logger.error(f"Subscription failed for {request.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subscription failed: {str(e)}"
        )


@router.post("/unsubscribe/{email}", response_model=EmailSubscriptionResponse)
def unsubscribe_from_alerts(email: str, db: Session = Depends(get_db)):
    """
    Unsubscribe an email address from risk alerts.
    """
    try:
        subscriber = db.query(EmailSubscriber).filter(
            EmailSubscriber.email == email.lower().strip()
        ).first()
        
        if not subscriber:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No subscription found for {email}"
            )
        
        subscriber.is_active = False
        subscriber.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Unsubscribed {email}")
        
        return EmailSubscriptionResponse(
            success=True,
            message=f"Successfully unsubscribed {email}",
            email=email,
            subscriber_id=subscriber.id,
            is_active=False,
            is_verified=subscriber.is_verified
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unsubscribe failed for {email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unsubscribe failed: {str(e)}"
        )


@router.get("/subscribers", response_model=List[SubscriberInfo])
def get_all_subscribers(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get list of all email subscribers."""
    try:
        query = db.query(EmailSubscriber)
        
        if active_only:
            query = query.filter(EmailSubscriber.is_active == True)
        
        subscribers = query.order_by(EmailSubscriber.created_at.desc()).all()
        
        return [
            SubscriberInfo(
                id=sub.id,
                email=sub.email,
                is_active=sub.is_active,
                is_verified=sub.is_verified,
                high_risk_threshold=sub.high_risk_threshold,
                medium_risk_threshold=sub.medium_risk_threshold,
                notify_on_high=sub.notify_on_high,
                notify_on_medium=sub.notify_on_medium,
                created_at=sub.created_at,
                last_alert_sent=sub.last_alert_sent
            )
            for sub in subscribers
        ]
        
    except Exception as e:
        logger.error(f"Failed to get subscribers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscribers: {str(e)}"
        )


@router.get("/subscriber/{email}", response_model=SubscriberInfo)
def get_subscriber(email: str, db: Session = Depends(get_db)):
    """Get subscription information for a specific email."""
    try:
        subscriber = db.query(EmailSubscriber).filter(
            EmailSubscriber.email == email.lower().strip()
        ).first()
        
        if not subscriber:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No subscription found for {email}"
            )
        
        return SubscriberInfo(
            id=subscriber.id,
            email=subscriber.email,
            is_active=subscriber.is_active,
            is_verified=subscriber.is_verified,
            high_risk_threshold=subscriber.high_risk_threshold,
            medium_risk_threshold=subscriber.medium_risk_threshold,
            notify_on_high=subscriber.notify_on_high,
            notify_on_medium=subscriber.notify_on_medium,
            created_at=subscriber.created_at,
            last_alert_sent=subscriber.last_alert_sent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get subscriber {email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscriber: {str(e)}"
        )


@router.post("/test", response_model=EmailSubscriptionResponse)
def send_test_alert(request: TestAlertRequest, db: Session = Depends(get_db)):
    """Send a test alert email to verify email configuration."""
    try:
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
        
        return EmailSubscriptionResponse(
            success=True,
            message=f"Test alert sent to {request.email}",
            email=request.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test alert failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test alert failed: {str(e)}"
        )


@router.post("/send-alerts-to-all")
def send_alerts_to_all_subscribers(db: Session = Depends(get_db)):
    """
    Send risk alerts to all active subscribers based on current risk levels.
    
    This endpoint checks all protocols and sends alerts to subscribers
    whose thresholds are exceeded.
    """
    try:
        service = get_email_service()
        
        if not service.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Email alerts are not enabled."
            )
        
        # Get all active subscribers
        subscribers = db.query(EmailSubscriber).filter(
            EmailSubscriber.is_active == True,
            EmailSubscriber.is_verified == True
        ).all()
        
        if not subscribers:
            return {
                "success": True,
                "message": "No active subscribers",
                "alerts_sent": 0
            }
        
        # Get latest risk scores for all protocols
        protocols_with_risk = db.query(Protocol, RiskScore).join(
            RiskScore,
            Protocol.id == RiskScore.protocol_id
        ).order_by(RiskScore.timestamp.desc()).all()
        
        # Track alerts sent
        alerts_sent = 0
        alerts_by_email = {}
        
        # Check each protocol's risk for each subscriber
        for protocol, risk_score in protocols_with_risk:
            risk_percentage = risk_score.risk_score * 100
            
            for subscriber in subscribers:
                should_alert = False
                alert_type = None
                
                # Check if subscriber should be alerted
                if (risk_score.risk_level == "high" and 
                    subscriber.notify_on_high and 
                    risk_percentage >= subscriber.high_risk_threshold):
                    should_alert = True
                    alert_type = "high"
                elif (risk_score.risk_level == "medium" and 
                      subscriber.notify_on_medium and 
                      risk_percentage >= subscriber.medium_risk_threshold):
                    should_alert = True
                    alert_type = "medium"
                
                if should_alert:
                    # Collect alerts for this email
                    if subscriber.email not in alerts_by_email:
                        alerts_by_email[subscriber.email] = []
                    
                    alerts_by_email[subscriber.email].append({
                        "protocol_name": protocol.name,
                        "risk_score": risk_percentage,
                        "risk_level": risk_score.risk_level,
                        "threshold": subscriber.high_risk_threshold if alert_type == "high" else subscriber.medium_risk_threshold,
                        "alert_type": alert_type
                    })
        
        # Send batch alerts to each subscriber
        for email, alerts in alerts_by_email.items():
            try:
                success = service.send_batch_alerts(
                    recipient_email=email,
                    alerts=alerts
                )
                
                if success:
                    alerts_sent += 1
                    
                    # Update last_alert_sent
                    subscriber = db.query(EmailSubscriber).filter(
                        EmailSubscriber.email == email
                    ).first()
                    if subscriber:
                        subscriber.last_alert_sent = datetime.utcnow()
                        db.commit()
                        
            except Exception as e:
                logger.error(f"Failed to send batch alert to {email}: {e}")
        
        return {
            "success": True,
            "message": f"Alerts processed for {len(subscribers)} subscribers",
            "alerts_sent": alerts_sent,
            "subscribers_notified": len(alerts_by_email)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send alerts to subscribers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send alerts: {str(e)}"
        )


@router.get("/status")
def get_email_alert_status(db: Session = Depends(get_db)):
    """Check if email alerts are configured and get subscriber count."""
    try:
        service = get_email_service()
        
        # Get subscriber statistics
        total_subscribers = db.query(EmailSubscriber).count()
        active_subscribers = db.query(EmailSubscriber).filter(
            EmailSubscriber.is_active == True
        ).count()
        
        return {
            "enabled": service.enabled,
            "smtp_host": service.smtp_host,
            "smtp_port": service.smtp_port,
            "sender_email": service.sender_email,
            "configured": bool(service.sender_password),
            "total_subscribers": total_subscribers,
            "active_subscribers": active_subscribers
        }
        
    except Exception as e:
        logger.error(f"Failed to get email alert status: {e}")
        return {
            "enabled": False,
            "configured": False,
            "total_subscribers": 0,
            "active_subscribers": 0,
            "error": str(e)
        }

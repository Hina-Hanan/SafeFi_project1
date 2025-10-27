"""
Subscriber-Specific Alert Service

Sends personalized email alerts to subscribers based on their
individual threshold settings and preferences.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.database.models import EmailSubscriber, Protocol, RiskScore
from app.services.email_alert_service import get_email_service
from app.database.connection import SessionLocal

logger = logging.getLogger("app.services.subscriber_alerts")


class SubscriberAlertService:
    """
    Manages personalized risk alerts for email subscribers.
    
    Features:
    - Per-subscriber threshold monitoring
    - Personalized alert preferences
    - Alert cooldown to prevent spam
    - Batch and individual alert support
    """
    
    def __init__(self):
        self.email_service = get_email_service()
        self.alert_cooldown = timedelta(hours=1)  # Don't spam same alert within 1 hour
        logger.info("SubscriberAlertService initialized")
    
    def check_and_send_alerts(self) -> Dict:
        """
        Check all protocols against all subscribers' thresholds and send alerts.
        
        Returns:
            Statistics about alerts sent
        """
        logger.info("🔍 Checking risk levels for all subscribers...")
        
        db = SessionLocal()
        try:
            # Get all active and verified subscribers
            subscribers = db.execute(
                select(EmailSubscriber)
                .where(EmailSubscriber.is_active == True)
                .where(EmailSubscriber.is_verified == True)
            ).scalars().all()
            
            if not subscribers:
                logger.info("No active subscribers found")
                return {"total_subscribers": 0, "alerts_sent": 0}
            
            # Get all active protocols with their latest risk scores
            protocols = db.execute(
                select(Protocol)
                .where(Protocol.is_active == True)
            ).scalars().all()
            
            stats = {
                "total_subscribers": len(subscribers),
                "alerts_sent": 0,
                "alerts_skipped_cooldown": 0,
                "subscribers_notified": set(),
                "timestamp": datetime.utcnow()
            }
            
            # Check each subscriber's thresholds
            for subscriber in subscribers:
                alerts_for_subscriber = []
                
                for protocol in protocols:
                    # Get latest risk score
                    latest_risk = db.execute(
                        select(RiskScore)
                        .where(RiskScore.protocol_id == protocol.id)
                        .order_by(desc(RiskScore.timestamp))
                        .limit(1)
                    ).scalar_one_or_none()
                    
                    if not latest_risk:
                        continue
                    
                    # Convert risk score to percentage
                    risk_score_pct = latest_risk.risk_score * 100
                    
                    # Check if alert should be sent based on subscriber's preferences
                    should_alert = False
                    alert_type = None
                    
                    if (risk_score_pct >= subscriber.high_risk_threshold and 
                        subscriber.notify_on_high):
                        should_alert = True
                        alert_type = "high"
                    elif (risk_score_pct >= subscriber.medium_risk_threshold and 
                          subscriber.notify_on_medium):
                        should_alert = True
                        alert_type = "medium"
                    
                    if should_alert:
                        alerts_for_subscriber.append({
                            "protocol_name": protocol.name,
                            "risk_score": risk_score_pct,
                            "risk_level": latest_risk.risk_level,
                            "threshold": (subscriber.high_risk_threshold 
                                        if alert_type == "high" 
                                        else subscriber.medium_risk_threshold),
                            "alert_type": alert_type
                        })
                
                # Send alerts if any found and not in cooldown
                if alerts_for_subscriber:
                    if self._should_send_alert(subscriber, db):
                        self._send_alerts_to_subscriber(subscriber, alerts_for_subscriber)
                        stats["alerts_sent"] += len(alerts_for_subscriber)
                        stats["subscribers_notified"].add(subscriber.email)
                        
                        # Update last_alert_sent
                        subscriber.last_alert_sent = datetime.utcnow()
                        db.commit()
                    else:
                        stats["alerts_skipped_cooldown"] += len(alerts_for_subscriber)
            
            # Convert set to count for JSON serialization
            stats["subscribers_notified"] = len(stats["subscribers_notified"])
            
            logger.info(
                f"✅ Alert check complete: {stats['alerts_sent']} alerts sent "
                f"to {stats['subscribers_notified']} subscribers"
            )
            
            return stats
            
        except Exception as e:
            logger.exception(f"Error in check_and_send_alerts: {e}")
            return {"error": str(e)}
        finally:
            db.close()
    
    def _should_send_alert(self, subscriber: EmailSubscriber, db: Session) -> bool:
        """Check if enough time has passed since last alert to this subscriber."""
        if subscriber.last_alert_sent is None:
            return True
        
        time_since_last = datetime.utcnow() - subscriber.last_alert_sent
        return time_since_last > self.alert_cooldown
    
    def _send_alerts_to_subscriber(
        self, 
        subscriber: EmailSubscriber, 
        alerts: List[Dict]
    ) -> None:
        """Send risk alerts to a single subscriber."""
        try:
            if len(alerts) == 1:
                # Send single alert
                alert = alerts[0]
                success = self.email_service.send_risk_alert(
                    recipient_email=subscriber.email,
                    protocol_name=alert["protocol_name"],
                    risk_score=alert["risk_score"],
                    risk_level=alert["risk_level"],
                    threshold=alert["threshold"],
                    alert_type=alert["alert_type"]
                )
                
                if success:
                    logger.info(
                        f"✉️  Sent alert to {subscriber.email} for "
                        f"{alert['protocol_name']} ({alert['risk_score']:.1f}%)"
                    )
                else:
                    logger.warning(f"⚠️  Failed to send alert to {subscriber.email}")
            
            else:
                # Send batch alert
                success = self.email_service.send_batch_alerts(
                    recipient_email=subscriber.email,
                    alerts=alerts
                )
                
                if success:
                    logger.info(
                        f"✉️  Sent {len(alerts)} batched alerts to {subscriber.email}"
                    )
                else:
                    logger.warning(
                        f"⚠️  Failed to send batch alerts to {subscriber.email}"
                    )
                    
        except Exception as e:
            logger.exception(f"Error sending alerts to {subscriber.email}: {e}")
    
    def send_test_alert(self, email: str, db: Session) -> bool:
        """Send a test alert to verify email configuration."""
        try:
            # Get subscriber info if exists
            subscriber = db.execute(
                select(EmailSubscriber)
                .where(EmailSubscriber.email == email)
            ).scalar_one_or_none()
            
            threshold = subscriber.high_risk_threshold if subscriber else 70.0
            
            success = self.email_service.send_risk_alert(
                recipient_email=email,
                protocol_name="Test Protocol",
                risk_score=75.5,
                risk_level="high",
                threshold=threshold,
                alert_type="high"
            )
            
            if success:
                logger.info(f"✅ Test alert sent successfully to {email}")
            else:
                logger.warning(f"⚠️  Failed to send test alert to {email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending test alert to {email}: {e}")
            return False
    
    def get_subscriber_alert_stats(self, email: str, db: Session) -> Dict:
        """Get alert statistics for a specific subscriber."""
        try:
            subscriber = db.execute(
                select(EmailSubscriber)
                .where(EmailSubscriber.email == email)
            ).scalar_one_or_none()
            
            if not subscriber:
                return {"error": "Subscriber not found"}
            
            # Get all active protocols
            protocols = db.execute(
                select(Protocol)
                .where(Protocol.is_active == True)
            ).scalars().all()
            
            protocols_above_threshold = {
                "high": [],
                "medium": [],
                "low": []
            }
            
            for protocol in protocols:
                latest_risk = db.execute(
                    select(RiskScore)
                    .where(RiskScore.protocol_id == protocol.id)
                    .order_by(desc(RiskScore.timestamp))
                    .limit(1)
                ).scalar_one_or_none()
                
                if not latest_risk:
                    continue
                
                risk_score_pct = latest_risk.risk_score * 100
                
                if risk_score_pct >= subscriber.high_risk_threshold:
                    protocols_above_threshold["high"].append({
                        "name": protocol.name,
                        "risk_score": risk_score_pct,
                        "risk_level": latest_risk.risk_level
                    })
                elif risk_score_pct >= subscriber.medium_risk_threshold:
                    protocols_above_threshold["medium"].append({
                        "name": protocol.name,
                        "risk_score": risk_score_pct,
                        "risk_level": latest_risk.risk_level
                    })
                else:
                    protocols_above_threshold["low"].append({
                        "name": protocol.name,
                        "risk_score": risk_score_pct,
                        "risk_level": latest_risk.risk_level
                    })
            
            return {
                "subscriber_email": subscriber.email,
                "high_risk_threshold": subscriber.high_risk_threshold,
                "medium_risk_threshold": subscriber.medium_risk_threshold,
                "notify_on_high": subscriber.notify_on_high,
                "notify_on_medium": subscriber.notify_on_medium,
                "last_alert_sent": subscriber.last_alert_sent.isoformat() if subscriber.last_alert_sent else None,
                "protocols_above_high_threshold": len(protocols_above_threshold["high"]),
                "protocols_above_medium_threshold": len(protocols_above_threshold["medium"]),
                "protocol_details": protocols_above_threshold,
                "time_until_next_alert": self._time_until_next_alert(subscriber)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for {email}: {e}")
            return {"error": str(e)}
    
    def _time_until_next_alert(self, subscriber: EmailSubscriber) -> str:
        """Calculate time until next alert can be sent."""
        if subscriber.last_alert_sent is None:
            return "Can send immediately"
        
        time_since_last = datetime.utcnow() - subscriber.last_alert_sent
        time_remaining = self.alert_cooldown - time_since_last
        
        if time_remaining.total_seconds() <= 0:
            return "Can send immediately"
        
        minutes = int(time_remaining.total_seconds() / 60)
        return f"{minutes} minutes"


# Singleton instance
_subscriber_alert_service: SubscriberAlertService | None = None

def get_subscriber_alert_service() -> SubscriberAlertService:
    """Get or create the subscriber alert service singleton."""
    global _subscriber_alert_service
    if _subscriber_alert_service is None:
        _subscriber_alert_service = SubscriberAlertService()
    return _subscriber_alert_service


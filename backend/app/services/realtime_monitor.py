"""
Real-time Protocol Risk Monitor
Continuously monitors protocols and sends email alerts when high risk is detected.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
import os
from dotenv import load_dotenv

from app.database.connection import SessionLocal
from app.database.models import Protocol, RiskScore
from app.services.email_alert_service import get_email_service

load_dotenv()
logger = logging.getLogger("app.services.realtime_monitor")


class RealtimeRiskMonitor:
    """Monitor protocols in real-time and send email alerts."""
    
    def __init__(self):
        self.email_service = get_email_service()
        self.recipient_email = os.getenv("ALERT_RECIPIENT_EMAIL", "hinahanan003@gmail.com")
        self.high_risk_threshold = float(os.getenv("HIGH_RISK_THRESHOLD", "70.0"))
        self.medium_risk_threshold = float(os.getenv("MEDIUM_RISK_THRESHOLD", "40.0"))
        self.check_interval = int(os.getenv("MONITOR_INTERVAL_SECONDS", "300"))  # 5 minutes default
        self.notify_high = os.getenv("NOTIFY_HIGH_RISK", "true").lower() == "true"
        self.notify_medium = os.getenv("NOTIFY_MEDIUM_RISK", "false").lower() == "true"
        
        # Track sent alerts to avoid spamming (protocol_id -> last_alert_time)
        self.last_alerts: Dict[str, datetime] = {}
        self.alert_cooldown = timedelta(hours=1)  # Don't resend same alert within 1 hour
        
        self.is_running = False
        logger.info(f"RealtimeRiskMonitor initialized - Recipient: {self.recipient_email}, "
                   f"High threshold: {self.high_risk_threshold}%, Check interval: {self.check_interval}s")
    
    async def start_monitoring(self) -> None:
        """Start continuous monitoring in background."""
        if self.is_running:
            logger.warning("Monitor is already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting real-time risk monitoring...")
        
        try:
            while self.is_running:
                await self._check_protocols()
                await asyncio.sleep(self.check_interval)
        except Exception as e:
            logger.exception(f"Monitor crashed: {e}")
            self.is_running = False
    
    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        self.is_running = False
        logger.info("⏹️ Stopping real-time risk monitoring...")
    
    async def _check_protocols(self) -> None:
        """Check all active protocols and send alerts if needed."""
        db = SessionLocal()
        try:
            # Get all active protocols with their latest risk scores
            protocols = db.query(Protocol).filter_by(is_active=True).all()
            
            high_risk_alerts = []
            medium_risk_alerts = []
            
            for protocol in protocols:
                # Get latest risk score
                latest_risk = (
                    db.query(RiskScore)
                    .filter(RiskScore.protocol_id == protocol.id)
                    .order_by(RiskScore.timestamp.desc())
                    .first()
                )
                
                if not latest_risk:
                    continue
                
                risk_score_pct = latest_risk.risk_score * 100
                
                # Check if should alert
                should_alert = False
                alert_type = None
                
                if risk_score_pct >= self.high_risk_threshold and self.notify_high:
                    should_alert = True
                    alert_type = "high"
                    high_risk_alerts.append({
                        "protocol_name": protocol.name,
                        "risk_score": risk_score_pct,
                        "risk_level": latest_risk.risk_level,
                        "protocol_id": protocol.id
                    })
                elif risk_score_pct >= self.medium_risk_threshold and self.notify_medium:
                    should_alert = True
                    alert_type = "medium"
                    medium_risk_alerts.append({
                        "protocol_name": protocol.name,
                        "risk_score": risk_score_pct,
                        "risk_level": latest_risk.risk_level,
                        "protocol_id": protocol.id
                    })
                
                # Send individual alert if needed and not in cooldown
                if should_alert and alert_type:
                    if self._should_send_alert(protocol.id):
                        self._send_individual_alert(
                            protocol_name=protocol.name,
                            risk_score=risk_score_pct,
                            risk_level=latest_risk.risk_level,
                            threshold=self.high_risk_threshold if alert_type == "high" else self.medium_risk_threshold,
                            alert_type=alert_type
                        )
                        self.last_alerts[protocol.id] = datetime.utcnow()
            
            # Log summary
            if high_risk_alerts or medium_risk_alerts:
                logger.info(f"📊 Monitor check complete - High risk: {len(high_risk_alerts)}, "
                           f"Medium risk: {len(medium_risk_alerts)}")
            
        except Exception as e:
            logger.exception(f"Error checking protocols: {e}")
        finally:
            db.close()
    
    def _should_send_alert(self, protocol_id: str) -> bool:
        """Check if we should send an alert (not in cooldown period)."""
        if protocol_id not in self.last_alerts:
            return True
        
        time_since_last = datetime.utcnow() - self.last_alerts[protocol_id]
        return time_since_last > self.alert_cooldown
    
    def _send_individual_alert(
        self,
        protocol_name: str,
        risk_score: float,
        risk_level: str,
        threshold: float,
        alert_type: str
    ) -> None:
        """Send email alert for a single protocol."""
        try:
            success = self.email_service.send_risk_alert(
                recipient_email=self.recipient_email,
                protocol_name=protocol_name,
                risk_score=risk_score,
                risk_level=risk_level,
                threshold=threshold,
                alert_type=alert_type
            )
            
            if success:
                logger.info(f"✅ Alert sent for {protocol_name} (Risk: {risk_score:.1f}%)")
            else:
                logger.warning(f"⚠️ Failed to send alert for {protocol_name}")
                
        except Exception as e:
            logger.exception(f"Error sending alert for {protocol_name}: {e}")
    
    def get_status(self) -> Dict:
        """Get monitor status."""
        return {
            "is_running": self.is_running,
            "recipient_email": self.recipient_email,
            "high_risk_threshold": self.high_risk_threshold,
            "medium_risk_threshold": self.medium_risk_threshold,
            "check_interval_seconds": self.check_interval,
            "notify_high_risk": self.notify_high,
            "notify_medium_risk": self.notify_medium,
            "alert_cooldown_hours": self.alert_cooldown.total_seconds() / 3600,
            "tracked_protocols": len(self.last_alerts),
            "last_alerts": {
                pid: last_time.isoformat() 
                for pid, last_time in list(self.last_alerts.items())[-5:]  # Show last 5
            }
        }


# Singleton instance
_monitor_instance: Optional[RealtimeRiskMonitor] = None

def get_monitor() -> RealtimeRiskMonitor:
    """Get or create the monitor singleton."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = RealtimeRiskMonitor()
    return _monitor_instance



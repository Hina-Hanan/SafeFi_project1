"""
Email Alert Service for Risk Notifications

Sends email alerts when protocols exceed risk thresholds.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("app.services.email_alert")

class EmailAlertService:
    """Service for sending email alerts about protocol risks."""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("ALERT_SENDER_EMAIL", "hinahanan2003@gmail.com")
        self.sender_password = os.getenv("ALERT_SENDER_PASSWORD", "")
        self.enabled = os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() == "true"
        
        if not self.sender_password and self.enabled:
            logger.warning("Email alerts enabled but ALERT_SENDER_PASSWORD not set")
    
    def send_risk_alert(
        self,
        recipient_email: str,
        protocol_name: str,
        risk_score: float,
        risk_level: str,
        threshold: float,
        alert_type: str = "high"
    ) -> bool:
        """
        Send a risk alert email.
        
        Args:
            recipient_email: Email address to send to
            protocol_name: Name of the protocol
            risk_score: Current risk score (0-100)
            risk_level: Risk level classification
            threshold: The threshold that was exceeded
            alert_type: Type of alert ('high' or 'medium')
        
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Email alerts disabled. Skipping email.")
            return False
        
        if not self.sender_password:
            logger.error("Cannot send email: ALERT_SENDER_PASSWORD not configured")
            return False
        
        try:
            # Create email
            subject = f"⚠️ DeFi Risk Alert: {protocol_name} - {risk_level.upper()} Risk"
            
            html_body = self._generate_html_email(
                protocol_name=protocol_name,
                risk_score=risk_score,
                risk_level=risk_level,
                threshold=threshold,
                alert_type=alert_type
            )
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"✅ Alert email sent to {recipient_email} for {protocol_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send alert email: {e}")
            return False
    
    def send_batch_alerts(
        self,
        recipient_email: str,
        alerts: List[dict]
    ) -> bool:
        """
        Send a batch of alerts in a single email.
        
        Args:
            recipient_email: Email address to send to
            alerts: List of alert dictionaries with protocol info
        
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.enabled or not alerts:
            return False
        
        try:
            subject = f"⚠️ DeFi Risk Alert: {len(alerts)} Protocol(s) Exceeded Thresholds"
            
            html_body = self._generate_batch_email(alerts)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"✅ Batch alert email sent to {recipient_email} with {len(alerts)} alerts")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send batch alert email: {e}")
            return False
    
    def _generate_html_email(
        self,
        protocol_name: str,
        risk_score: float,
        risk_level: str,
        threshold: float,
        alert_type: str
    ) -> str:
        """Generate HTML email content for a single alert."""
        
        # Color coding
        colors = {
            'high': '#ef4444',
            'medium': '#f59e0b',
            'low': '#10b981'
        }
        color = colors.get(risk_level.lower(), '#6b7280')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeFi Risk Alert</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 12px; border: 1px solid #334155; overflow: hidden;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, {color}20 0%, {color}10 100%); padding: 30px; border-bottom: 2px solid {color};">
            <h1 style="margin: 0; color: #f1f5f9; font-size: 24px; font-weight: bold;">
                ⚠️ DeFi Risk Monitor Alert
            </h1>
            <p style="margin: 10px 0 0 0; color: #94a3b8; font-size: 14px;">
                {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}
            </p>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px;">
            <div style="background: {color}15; border-left: 4px solid {color}; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="margin: 0 0 10px 0; color: {color}; font-size: 20px;">
                    {protocol_name}
                </h2>
                <p style="margin: 0; color: #cbd5e1; font-size: 16px;">
                    Risk level has exceeded your configured threshold
                </p>
            </div>
            
            <!-- Risk Metrics -->
            <div style="background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #334155;">
                            <span style="color: #94a3b8; font-size: 14px;">Current Risk Score</span>
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #334155; text-align: right;">
                            <span style="color: {color}; font-size: 18px; font-weight: bold;">{risk_score:.1f}%</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #334155;">
                            <span style="color: #94a3b8; font-size: 14px;">Risk Level</span>
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #334155; text-align: right;">
                            <span style="color: {color}; font-size: 16px; font-weight: bold; text-transform: uppercase;">{risk_level}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0;">
                            <span style="color: #94a3b8; font-size: 14px;">Your Threshold</span>
                        </td>
                        <td style="padding: 12px 0; text-align: right;">
                            <span style="color: #e2e8f0; font-size: 16px;">{threshold:.1f}%</span>
                        </td>
                    </tr>
                </table>
            </div>
            
            <!-- Action Required -->
            <div style="background: linear-gradient(135deg, #6366f115 0%, #ec489915 100%); border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <h3 style="margin: 0 0 10px 0; color: #f1f5f9; font-size: 16px;">
                    📋 Recommended Actions
                </h3>
                <ul style="margin: 0; padding-left: 20px; color: #cbd5e1; font-size: 14px; line-height: 1.8;">
                    <li>Review the protocol's recent performance and metrics</li>
                    <li>Check for any security audits or recent vulnerabilities</li>
                    <li>Consider reducing exposure if risk continues to increase</li>
                    <li>Monitor the situation closely over the next 24-48 hours</li>
                </ul>
            </div>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5173" style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: bold; font-size: 16px;">
                    View Dashboard
                </a>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #0f172a; padding: 20px 30px; border-top: 1px solid #334155; text-align: center;">
            <p style="margin: 0; color: #64748b; font-size: 12px;">
                This is an automated alert from DeFi Risk Monitor<br>
                You're receiving this because you've configured risk alerts for your protocols
            </p>
            <p style="margin: 15px 0 0 0; color: #64748b; font-size: 12px;">
                © {datetime.utcnow().year} DeFi Risk Monitor. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_batch_email(self, alerts: List[dict]) -> str:
        """Generate HTML email content for multiple alerts."""
        
        # Generate alerts table rows
        alert_rows = ""
        for alert in alerts:
            color = {
                'high': '#ef4444',
                'medium': '#f59e0b',
                'low': '#10b981'
            }.get(alert.get('risk_level', 'medium').lower(), '#6b7280')
            
            alert_rows += f"""
            <tr>
                <td style="padding: 16px; border-bottom: 1px solid #334155;">
                    <span style="color: #f1f5f9; font-weight: bold; font-size: 15px;">{alert.get('protocol_name', 'Unknown')}</span>
                </td>
                <td style="padding: 16px; border-bottom: 1px solid #334155; text-align: center;">
                    <span style="color: {color}; font-weight: bold; font-size: 16px;">{alert.get('risk_score', 0):.1f}%</span>
                </td>
                <td style="padding: 16px; border-bottom: 1px solid #334155; text-align: center;">
                    <span style="color: {color}; font-weight: bold; text-transform: uppercase; font-size: 13px;">{alert.get('risk_level', 'N/A')}</span>
                </td>
            </tr>
            """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeFi Risk Alerts</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; padding: 20px;">
    <div style="max-width: 700px; margin: 0 auto; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 12px; border: 1px solid #334155; overflow: hidden;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #ef444420 0%, #f59e0b20 100%); padding: 30px; border-bottom: 2px solid #ef4444;">
            <h1 style="margin: 0; color: #f1f5f9; font-size: 24px; font-weight: bold;">
                ⚠️ Multiple Risk Alerts Detected
            </h1>
            <p style="margin: 10px 0 0 0; color: #94a3b8; font-size: 14px;">
                {len(alerts)} protocol(s) have exceeded your risk thresholds
            </p>
            <p style="margin: 5px 0 0 0; color: #64748b; font-size: 13px;">
                {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}
            </p>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px;">
            <!-- Alerts Table -->
            <div style="background: #1e293b; border-radius: 8px; overflow: hidden; margin-bottom: 20px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #0f172a;">
                            <th style="padding: 16px; text-align: left; color: #94a3b8; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Protocol</th>
                            <th style="padding: 16px; text-align: center; color: #94a3b8; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Risk Score</th>
                            <th style="padding: 16px; text-align: center; color: #94a3b8; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Level</th>
                        </tr>
                    </thead>
                    <tbody>
                        {alert_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Summary -->
            <div style="background: linear-gradient(135deg, #6366f115 0%, #ec489915 100%); border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <h3 style="margin: 0 0 10px 0; color: #f1f5f9; font-size: 16px;">
                    📊 Summary
                </h3>
                <p style="margin: 0; color: #cbd5e1; font-size: 14px; line-height: 1.6;">
                    Multiple protocols in your watchlist have triggered risk alerts. We recommend reviewing each protocol individually and considering appropriate risk management actions.
                </p>
            </div>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5173" style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: bold; font-size: 16px;">
                    View Full Dashboard
                </a>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #0f172a; padding: 20px 30px; border-top: 1px solid #334155; text-align: center;">
            <p style="margin: 0; color: #64748b; font-size: 12px;">
                This is an automated alert from DeFi Risk Monitor<br>
                You're receiving this because you've configured risk alerts
            </p>
            <p style="margin: 15px 0 0 0; color: #64748b; font-size: 12px;">
                © {datetime.utcnow().year} DeFi Risk Monitor. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html


# Singleton instance
_email_service_instance: Optional[EmailAlertService] = None

def get_email_service() -> EmailAlertService:
    """Get or create the email service singleton."""
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailAlertService()
    return _email_service_instance



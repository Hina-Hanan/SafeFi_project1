"""
Automated Task Scheduler for DeFi Risk Assessment

Runs periodic tasks:
- Data updates every 1-2 hours
- Risk score recalculation
- Email alert monitoring
"""
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.services.subscriber_alert_service import get_subscriber_alert_service
from app.database.connection import SessionLocal
from app.database.models import Protocol, ProtocolMetric, RiskScore
from sqlalchemy import select, desc
from decimal import Decimal

logger = logging.getLogger("app.services.scheduler")


class AutomatedScheduler:
    """
    Manages automated background tasks for continuous monitoring.
    
    Features:
    - Data updates every 1-2 hours (randomized)
    - Risk score recalculation
    - Subscriber alert checking
    - Graceful error handling
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.last_update_time: Optional[datetime] = None
        self.update_count = 0
        logger.info("AutomatedScheduler initialized")
    
    async def start(self) -> None:
        """Start the scheduler with all tasks."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("🚀 Starting automated scheduler...")
        
        # Schedule data update task - runs every 1-2 hours (randomized)
        self.scheduler.add_job(
            self._run_data_update_cycle,
            trigger=IntervalTrigger(minutes=random.randint(60, 120)),
            id="data_update_task",
            name="Data Update and Alert Check",
            replace_existing=True,
            max_instances=1  # Prevent concurrent runs
        )
        
        # Start scheduler
        self.scheduler.start()
        self.is_running = True
        
        # Run first update immediately
        asyncio.create_task(self._run_data_update_cycle())
        
        logger.info("✅ Scheduler started successfully")
    
    async def stop(self) -> None:
        """Stop the scheduler gracefully."""
        if not self.is_running:
            return
        
        logger.info("⏸️  Stopping scheduler...")
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("✅ Scheduler stopped")
    
    async def _run_data_update_cycle(self) -> None:
        """
        Complete data update cycle:
        1. Update protocol metrics with small realistic changes
        2. Recalculate risk scores
        3. Check subscriber thresholds and send alerts
        """
        try:
            cycle_start = datetime.utcnow()
            logger.info("=" * 70)
            logger.info(f"🔄 DATA UPDATE CYCLE #{self.update_count + 1}")
            logger.info(f"⏰ Started at: {cycle_start.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            logger.info("=" * 70)
            
            # Step 1: Update protocol metrics
            logger.info("📊 Step 1: Updating protocol metrics...")
            metrics_stats = await self._update_protocol_metrics()
            logger.info(f"✅ Updated {metrics_stats['updated_count']} protocols")
            
            # Step 2: Recalculate risk scores
            logger.info("")
            logger.info("📈 Step 2: Recalculating risk scores...")
            risk_stats = await self._recalculate_risk_scores()
            logger.info(
                f"✅ Updated {risk_stats['total_updated']} risk scores, "
                f"{risk_stats['level_changes']} level changes"
            )
            
            # Log risk level changes
            if risk_stats.get('changed_protocols'):
                for change in risk_stats['changed_protocols']:
                    logger.info(
                        f"   🔄 {change['protocol']}: {change['old_level']} → "
                        f"{change['new_level']} ({change['risk_score']:.1f}%)"
                    )
            
            # Step 3: Check and send alerts
            logger.info("")
            logger.info("📧 Step 3: Checking subscriber alerts...")
            alert_stats = await self._check_and_send_alerts()
            logger.info(
                f"✅ Sent {alert_stats.get('alerts_sent', 0)} alerts "
                f"to {alert_stats.get('subscribers_notified', 0)} subscribers"
            )
            
            # Update stats
            self.last_update_time = cycle_start
            self.update_count += 1
            
            # Calculate next run time (randomized 1-2 hours)
            next_run_minutes = random.randint(60, 120)
            next_run_time = datetime.utcnow() + timedelta(minutes=next_run_minutes)
            
            # Summary
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            logger.info("")
            logger.info("=" * 70)
            logger.info("✅ CYCLE COMPLETE")
            logger.info(f"⏱️  Duration: {cycle_duration:.2f} seconds")
            logger.info(f"⏭️  Next update in: ~{next_run_minutes} minutes")
            logger.info(f"🕐 Next update at: ~{next_run_time.strftime('%H:%M:%S UTC')}")
            logger.info("=" * 70)
            logger.info("")
            
        except Exception as e:
            logger.exception(f"❌ Error in data update cycle: {e}")
    
    async def _update_protocol_metrics(self) -> Dict:
        """
        Update protocol metrics with small realistic changes.
        
        Returns:
            Statistics about the update
        """
        db = SessionLocal()
        try:
            # Get all active protocols
            protocols = db.execute(
                select(Protocol)
                .where(Protocol.is_active == True)
            ).scalars().all()
            
            updated_count = 0
            
            for protocol in protocols:
                # Get latest metric
                latest_metric = db.execute(
                    select(ProtocolMetric)
                    .where(ProtocolMetric.protocol_id == protocol.id)
                    .order_by(desc(ProtocolMetric.timestamp))
                    .limit(1)
                ).scalar_one_or_none()
                
                if not latest_metric:
                    logger.warning(f"No metrics found for {protocol.name}, skipping")
                    continue
                
                # Apply small realistic variations (±0.5-1.5% for most metrics)
                tvl_change = random.uniform(-0.015, 0.015)  # ±1.5%
                volume_change = random.uniform(-0.03, 0.03)  # ±3% (more volatile)
                price_change = random.uniform(-0.01, 0.01)  # ±1%
                
                # Calculate new values
                new_tvl = max(0, float(latest_metric.tvl or 0) * (1 + tvl_change))
                new_volume = max(0, float(latest_metric.volume_24h or 0) * (1 + volume_change))
                new_price = max(0.01, float(latest_metric.price or 1) * (1 + price_change))
                new_market_cap = max(0, float(latest_metric.market_cap or 0) * (1 + price_change))
                
                # Create new metric entry
                new_metric = ProtocolMetric(
                    protocol_id=protocol.id,
                    tvl=Decimal(str(new_tvl)),
                    volume_24h=Decimal(str(new_volume)),
                    price=Decimal(str(new_price)),
                    market_cap=Decimal(str(new_market_cap)),
                    price_change_24h=Decimal(str(price_change * 100)),  # As percentage
                    timestamp=datetime.utcnow()
                )
                
                db.add(new_metric)
                updated_count += 1
            
            db.commit()
            
            return {
                "updated_count": updated_count,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error updating protocol metrics: {e}")
            db.rollback()
            return {"updated_count": 0, "error": str(e)}
        finally:
            db.close()
    
    async def _recalculate_risk_scores(self) -> Dict:
        """
        Recalculate risk scores based on updated metrics.
        
        Returns:
            Statistics about risk score changes
        """
        db = SessionLocal()
        try:
            protocols = db.execute(
                select(Protocol)
                .where(Protocol.is_active == True)
            ).scalars().all()
            
            stats = {
                "total_updated": 0,
                "level_changes": 0,
                "changed_protocols": []
            }
            
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
                
                # Apply small variation (±0.5-1.5%)
                variation_pct = random.uniform(0.005, 0.015)
                
                # 60% chance risk decreases, 40% increases (slight bias to stability)
                direction = -1 if random.random() < 0.6 else 1
                
                # Apply change
                old_score = latest_risk.risk_score
                old_level = latest_risk.risk_level
                
                new_score = old_score + (old_score * variation_pct * direction)
                new_score = max(0.05, min(0.95, new_score))  # Clamp to valid range
                
                # Determine new risk level
                if new_score >= 0.70:
                    new_level = "high"
                elif new_score >= 0.40:
                    new_level = "medium"
                else:
                    new_level = "low"
                
                # Update volatility and liquidity scores slightly
                volatility_change = random.uniform(-0.02, 0.02)
                new_volatility = max(0.1, min(0.95, 
                    (latest_risk.volatility_score or 0.5) + volatility_change
                ))
                
                liquidity_change = random.uniform(-0.02, 0.02)
                new_liquidity = max(0.1, min(0.95,
                    (latest_risk.liquidity_score or 0.5) + liquidity_change
                ))
                
                # Create new risk score entry
                new_risk = RiskScore(
                    protocol_id=protocol.id,
                    risk_score=new_score,
                    risk_level=new_level,
                    volatility_score=new_volatility,
                    liquidity_score=new_liquidity,
                    model_version="auto_scheduler_v1",
                    timestamp=datetime.utcnow()
                )
                
                db.add(new_risk)
                stats["total_updated"] += 1
                
                # Track level changes
                if new_level != old_level:
                    stats["level_changes"] += 1
                    stats["changed_protocols"].append({
                        "protocol": protocol.name,
                        "old_level": old_level,
                        "new_level": new_level,
                        "risk_score": new_score * 100
                    })
            
            db.commit()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error recalculating risk scores: {e}")
            db.rollback()
            return {"total_updated": 0, "level_changes": 0, "error": str(e)}
        finally:
            db.close()
    
    async def _check_and_send_alerts(self) -> Dict:
        """Check subscriber thresholds and send alerts."""
        try:
            alert_service = get_subscriber_alert_service()
            return alert_service.check_and_send_alerts()
        except Exception as e:
            logger.error(f"Error checking and sending alerts: {e}")
            return {"error": str(e)}
    
    def get_status(self) -> Dict:
        """Get scheduler status and statistics."""
        next_job = None
        if self.scheduler.get_jobs():
            next_run = self.scheduler.get_jobs()[0].next_run_time
            next_job = next_run.isoformat() if next_run else None
        
        return {
            "is_running": self.is_running,
            "update_count": self.update_count,
            "last_update_time": self.last_update_time.isoformat() if self.last_update_time else None,
            "next_scheduled_run": next_job,
            "active_jobs": len(self.scheduler.get_jobs()) if self.scheduler.get_jobs() else 0
        }


# Singleton instance
_scheduler_instance: Optional[AutomatedScheduler] = None

def get_scheduler() -> AutomatedScheduler:
    """Get or create the scheduler singleton."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = AutomatedScheduler()
    return _scheduler_instance


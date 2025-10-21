from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def check_expired_subscriptions():
    """Check for expired subscriptions and revoke access."""
    from app.models import Subscription, SubscriptionStatus, db
    from app.plex_service import plex_service
    
    try:
        logger.info("Running expired subscription check...")
        
        # Find active subscriptions that have passed their end date
        now = datetime.utcnow()
        expired_subscriptions = Subscription.query.filter(
            Subscription.status == SubscriptionStatus.active,
            Subscription.current_period_end.isnot(None),
            Subscription.current_period_end < now,
            Subscription.grandfathered == False  # Don't expire grandfathered users
        ).all()
        
        count = 0
        for subscription in expired_subscriptions:
            try:
                # Revoke Plex access
                plex_service.revoke_access(subscription.plex_username)
                
                # Update subscription status
                subscription.status = SubscriptionStatus.expired
                subscription.updated_at = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"Revoked access for expired subscription: {subscription.email} (ID: {subscription.id})")
                count += 1
            except Exception as e:
                logger.error(f"Error processing expired subscription {subscription.id}: {str(e)}")
                db.session.rollback()
        
        logger.info(f"Expired subscription check complete. Processed {count} subscriptions.")
        return count
    
    except Exception as e:
        logger.error(f"Error in check_expired_subscriptions: {str(e)}")
        return 0

def send_expiry_warnings():
    """Log warnings for subscriptions expiring soon (3 days)."""
    from app.models import Subscription, SubscriptionStatus
    
    try:
        logger.info("Checking for subscriptions expiring soon...")
        
        # Find subscriptions expiring in 3 days
        now = datetime.utcnow()
        warning_date = now + timedelta(days=3)
        
        expiring_soon = Subscription.query.filter(
            Subscription.status == SubscriptionStatus.active,
            Subscription.current_period_end.isnot(None),
            Subscription.current_period_end <= warning_date,
            Subscription.current_period_end > now,
            Subscription.grandfathered == False
        ).all()
        
        for subscription in expiring_soon:
            days_left = (subscription.current_period_end - now).days
            logger.warning(
                f"Subscription expiring in {days_left} days: {subscription.email} "
                f"(ID: {subscription.id}, Expires: {subscription.current_period_end})"
            )
        
        logger.info(f"Found {len(expiring_soon)} subscriptions expiring within 3 days.")
        return len(expiring_soon)
    
    except Exception as e:
        logger.error(f"Error in send_expiry_warnings: {str(e)}")
        return 0

def init_scheduler(app):
    """Initialize and start the background scheduler."""
    scheduler = BackgroundScheduler()
    
    # Check for expired subscriptions daily at midnight
    scheduler.add_job(
        func=check_expired_subscriptions,
        trigger=CronTrigger(hour=0, minute=0),  # Run at midnight
        id='check_expired_subscriptions',
        name='Check for expired subscriptions',
        replace_existing=True
    )
    
    # Send expiry warnings daily at 9 AM
    scheduler.add_job(
        func=send_expiry_warnings,
        trigger=CronTrigger(hour=9, minute=0),  # Run at 9 AM
        id='send_expiry_warnings',
        name='Send expiry warnings',
        replace_existing=True
    )
    
    # Start the scheduler
    with app.app_context():
        scheduler.start()
        logger.info("Background scheduler started successfully")
    
    return scheduler


import os
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text, Enum
from sqlalchemy.pool import NullPool
from config import Config
import enum

# Initialize SQLAlchemy
db = SQLAlchemy()

class SubscriptionStatus(enum.Enum):
    """Subscription status enumeration."""
    active = "active"
    past_due = "past_due"
    cancelled = "cancelled"
    expired = "expired"

class AdminUser(UserMixin):
    """Admin user class for Flask-Login."""
    
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

def get_admin_user(user_id):
    """Get admin user by ID for Flask-Login."""
    if user_id == '1':
        return AdminUser('1', Config.ADMIN_USERNAME)
    return None

# SQLAlchemy Models
class Tier(db.Model):
    """Subscription tier model."""
    __tablename__ = 'tiers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    price_monthly = db.Column(db.Float, nullable=False)
    stripe_price_id = db.Column(db.String(255), nullable=True)
    allow_downloads = db.Column(db.Boolean, default=False, nullable=False)
    library_names = db.Column(db.JSON, nullable=True)  # List of library names
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='tier', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price_monthly': self.price_monthly,
            'stripe_price_id': self.stripe_price_id,
            'allow_downloads': self.allow_downloads,
            'library_names': self.library_names or [],
            'active': self.active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Subscription(db.Model):
    """Subscription model for tracking user access."""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    plex_username = db.Column(db.String(255), nullable=False, index=True)
    tier_id = db.Column(db.Integer, db.ForeignKey('tiers.id'), nullable=False)
    status = db.Column(Enum(SubscriptionStatus), default=SubscriptionStatus.active, nullable=False)
    stripe_customer_id = db.Column(db.String(255), nullable=True, index=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True, unique=True, index=True)
    current_period_start = db.Column(db.DateTime, nullable=True)
    current_period_end = db.Column(db.DateTime, nullable=True, index=True)
    cancel_at_period_end = db.Column(db.Boolean, default=False, nullable=False)
    grandfathered = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    invite_requests = db.relationship('InviteRequest', backref='subscription', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'plex_username': self.plex_username,
            'tier_id': self.tier_id,
            'tier_name': self.tier.name if self.tier else None,
            'status': self.status.value if isinstance(self.status, SubscriptionStatus) else self.status,
            'stripe_customer_id': self.stripe_customer_id,
            'stripe_subscription_id': self.stripe_subscription_id,
            'current_period_start': self.current_period_start.strftime('%Y-%m-%d %H:%M:%S') if self.current_period_start else None,
            'current_period_end': self.current_period_end.strftime('%Y-%m-%d %H:%M:%S') if self.current_period_end else None,
            'cancel_at_period_end': self.cancel_at_period_end,
            'grandfathered': self.grandfathered,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class InviteRequest(db.Model):
    """Invite request model for database storage."""
    __tablename__ = 'invite_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    email_or_username = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=True)
    free_tier = db.Column(db.Boolean, default=False, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'email_or_username': self.email_or_username,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'error_message': self.error_message,
            'subscription_id': self.subscription_id,
            'free_tier': self.free_tier
        }

def get_database_uri():
    """Get database URI from environment or config."""
    # Check for Azure PostgreSQL connection string
    db_connection_string = os.environ.get('DATABASE_URL') or os.environ.get('AZURE_POSTGRESQL_CONNECTIONSTRING')
    
    if db_connection_string:
        # Azure provides connection strings in different formats
        # Convert if needed (Azure sometimes uses postgres:// but SQLAlchemy needs postgresql://)
        if db_connection_string.startswith('postgres://'):
            db_connection_string = db_connection_string.replace('postgres://', 'postgresql://', 1)
        return db_connection_string
    
    # Fall back to SQLite for local development
    return f'sqlite:///{Config.DATABASE_PATH}'

def init_db():
    """Initialize the database schema."""
    try:
        db.create_all()
        print(f"✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        raise

def create_invite_request(email_or_username, status, error_message=None):
    """Create a new invite request record."""
    try:
        invite = InviteRequest(
            email_or_username=email_or_username,
            status=status,
            error_message=error_message
        )
        db.session.add(invite)
        db.session.commit()
        return invite.id
    except Exception as e:
        db.session.rollback()
        print(f"Error creating invite request: {str(e)}")
        raise

def get_recent_invites(limit=50):
    """Get recent invite requests."""
    try:
        invites = InviteRequest.query.order_by(InviteRequest.timestamp.desc()).limit(limit).all()
        return [invite.to_dict() for invite in invites]
    except Exception as e:
        print(f"Error fetching recent invites: {str(e)}")
        return []

def get_invite_stats():
    """Get invite statistics."""
    try:
        total = InviteRequest.query.count()
        successful = InviteRequest.query.filter_by(status='success').count()
        failed = InviteRequest.query.filter_by(status='failed').count()
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed
        }
    except Exception as e:
        print(f"Error fetching invite stats: {str(e)}")
        return {'total': 0, 'successful': 0, 'failed': 0}

def get_subscription_stats():
    """Get subscription statistics."""
    try:
        total = Subscription.query.count()
        active = Subscription.query.filter_by(status=SubscriptionStatus.active).count()
        grandfathered = Subscription.query.filter_by(grandfathered=True).count()
        past_due = Subscription.query.filter_by(status=SubscriptionStatus.past_due).count()
        cancelled = Subscription.query.filter_by(status=SubscriptionStatus.cancelled).count()
        expired = Subscription.query.filter_by(status=SubscriptionStatus.expired).count()
        
        # Calculate MRR (Monthly Recurring Revenue)
        active_subs = Subscription.query.filter_by(status=SubscriptionStatus.active, grandfathered=False).all()
        mrr = sum([sub.tier.price_monthly for sub in active_subs if sub.tier])
        
        return {
            'total': total,
            'active': active,
            'grandfathered': grandfathered,
            'past_due': past_due,
            'cancelled': cancelled,
            'expired': expired,
            'mrr': round(mrr, 2)
        }
    except Exception as e:
        print(f"Error fetching subscription stats: {str(e)}")
        return {'total': 0, 'active': 0, 'grandfathered': 0, 'past_due': 0, 'cancelled': 0, 'expired': 0, 'mrr': 0}

def get_active_subscriptions(limit=None):
    """Get active subscriptions."""
    try:
        query = Subscription.query.filter_by(status=SubscriptionStatus.active).order_by(Subscription.created_at.desc())
        if limit:
            query = query.limit(limit)
        subscriptions = query.all()
        return [sub.to_dict() for sub in subscriptions]
    except Exception as e:
        print(f"Error fetching active subscriptions: {str(e)}")
        return []

def get_subscriptions_by_status(status, limit=None):
    """Get subscriptions by status."""
    try:
        query = Subscription.query.filter_by(status=status).order_by(Subscription.created_at.desc())
        if limit:
            query = query.limit(limit)
        subscriptions = query.all()
        return [sub.to_dict() for sub in subscriptions]
    except Exception as e:
        print(f"Error fetching subscriptions by status: {str(e)}")
        return []

def get_subscription_by_stripe_id(stripe_subscription_id):
    """Get subscription by Stripe subscription ID."""
    try:
        subscription = Subscription.query.filter_by(stripe_subscription_id=stripe_subscription_id).first()
        return subscription
    except Exception as e:
        print(f"Error fetching subscription by Stripe ID: {str(e)}")
        return None

def create_subscription(email, plex_username, tier_id, stripe_customer_id=None, stripe_subscription_id=None, 
                       current_period_start=None, current_period_end=None, grandfathered=False):
    """Create a new subscription record."""
    try:
        subscription = Subscription(
            email=email,
            plex_username=plex_username,
            tier_id=tier_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            status=SubscriptionStatus.active,
            current_period_start=current_period_start or datetime.utcnow(),
            current_period_end=current_period_end,
            grandfathered=grandfathered
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription
    except Exception as e:
        db.session.rollback()
        print(f"Error creating subscription: {str(e)}")
        raise

def update_subscription_status(subscription_id, status, current_period_end=None, cancel_at_period_end=None):
    """Update subscription status and billing period."""
    try:
        subscription = Subscription.query.get(subscription_id)
        if subscription:
            if isinstance(status, str):
                subscription.status = SubscriptionStatus[status]
            else:
                subscription.status = status
            
            if current_period_end:
                subscription.current_period_end = current_period_end
            if cancel_at_period_end is not None:
                subscription.cancel_at_period_end = cancel_at_period_end
            
            subscription.updated_at = datetime.utcnow()
            db.session.commit()
            return subscription
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error updating subscription status: {str(e)}")
        raise

def grandfather_existing_users():
    """Create permanent subscriptions for existing successful invites."""
    try:
        # Get all successful invites that don't have a subscription
        invites = InviteRequest.query.filter_by(status='success').filter(
            InviteRequest.subscription_id.is_(None)
        ).all()
        
        # Get or create a default tier for grandfathered users
        default_tier = Tier.query.filter_by(name="Grandfathered").first()
        if not default_tier:
            default_tier = Tier(
                name="Grandfathered",
                description="Legacy users with permanent free access",
                price_monthly=0.0,
                allow_downloads=True,
                library_names=[],
                active=True
            )
            db.session.add(default_tier)
            db.session.flush()
        
        count = 0
        for invite in invites:
            subscription = Subscription(
                email=invite.email_or_username,
                plex_username=invite.email_or_username,
                tier_id=default_tier.id,
                status=SubscriptionStatus.active,
                grandfathered=True,
                current_period_start=invite.timestamp,
                current_period_end=None,  # No expiry for grandfathered users
                stripe_customer_id=None,
                stripe_subscription_id=None
            )
            db.session.add(subscription)
            
            # Link the invite to the subscription
            invite.subscription_id = subscription.id
            invite.free_tier = True
            count += 1
        
        db.session.commit()
        return count
    except Exception as e:
        db.session.rollback()
        print(f"Error grandfathering existing users: {str(e)}")
        raise

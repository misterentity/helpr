import os
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from config import Config

# Initialize SQLAlchemy
db = SQLAlchemy()

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
class InviteRequest(db.Model):
    """Invite request model for database storage."""
    __tablename__ = 'invite_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    email_or_username = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'email_or_username': self.email_or_username,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'error_message': self.error_message
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

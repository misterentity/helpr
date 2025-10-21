from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
import os

# Initialize Flask-Login
login_manager = LoginManager()

# Initialize CSRF Protection
csrf = CSRFProtect()

# Initialize Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__)
    
    # Validate configuration before proceeding
    try:
        config_class.validate_config()
    except ValueError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Configuration validation failed: {str(e)}")
        # Create a minimal app that shows setup instructions
        @app.route('/')
        def setup_required():
            return render_template('setup_required.html', error=str(e)), 500
        return app
    
    app.config.from_object(config_class)
    
    # Configure SQLAlchemy
    from app.models import get_database_uri
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Initialize SQLAlchemy
    from app.models import db
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin dashboard.'
    
    # Initialize CSRF Protection
    csrf.init_app(app)
    
    # Initialize Rate Limiter
    limiter.init_app(app)
    
    # User loader for Flask-Login
    from app.models import get_admin_user
    
    @login_manager.user_loader
    def load_user(user_id):
        return get_admin_user(user_id)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    # Initialize database tables
    with app.app_context():
        db.create_all()
    
    # Initialize background scheduler for subscription management
    from app.scheduler import init_scheduler
    try:
        scheduler = init_scheduler(app)
        app.scheduler = scheduler
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not start background scheduler: {str(e)}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app


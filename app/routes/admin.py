from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.plex_service import plex_service
from app.models import AdminUser, get_recent_invites, get_invite_stats
from app.utils import is_safe_url
from config import Config
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validate credentials
        if username == Config.ADMIN_USERNAME and check_password_hash(Config.ADMIN_PASSWORD_HASH, password):
            user = AdminUser('1', username)
            login_user(user)
            logger.info(f"Admin user {username} logged in")
            
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page, request.host_url):
                return redirect(next_page)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
            logger.warning(f"Failed login attempt for username: {username}")
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    """Admin logout."""
    logger.info(f"Admin user {current_user.username} logged out")
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.index'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard."""
    try:
        # Get Plex libraries
        libraries = plex_service.get_libraries()
        
        # Get currently configured libraries
        configured_libraries = Config.get_library_config()
        
        # Get recent invite requests
        recent_invites = get_recent_invites(limit=50)
        
        # Get statistics
        stats = get_invite_stats()
        
        # Test connection status
        connection_status = plex_service.test_connection()
        
        return render_template(
            'admin/dashboard.html',
            libraries=libraries,
            configured_libraries=configured_libraries,
            recent_invites=recent_invites,
            stats=stats,
            connection_status=connection_status
        )
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('admin/dashboard.html', 
                             libraries=[], 
                             configured_libraries=[], 
                             recent_invites=[],
                             stats={'total': 0, 'successful': 0, 'failed': 0},
                             connection_status={'success': False, 'error': str(e)})

@admin_bp.route('/settings', methods=['POST'])
@login_required
def update_settings():
    """Update library settings."""
    try:
        # Get selected libraries from form
        selected_libraries = request.form.getlist('libraries')
        
        # Update configuration
        Config.set_library_config(selected_libraries)
        
        logger.info(f"Admin updated library settings: {selected_libraries}")
        flash(f'Settings updated successfully. {len(selected_libraries)} libraries selected.', 'success')
        
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        flash(f'Error updating settings: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/test-connection')
@login_required
def test_connection():
    """Test Plex connection."""
    try:
        result = plex_service.test_connection()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Connection test failed: {str(e)}'
        })


from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.plex_service import plex_service
from app.models import create_invite_request
from app.utils import validate_email_or_username, sanitize_input
from config import Config
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# Import limiter from app package
from app import limiter

@main_bp.route('/')
def index():
    """Render the invite request form."""
    require_code = bool(Config.INVITE_CODE)
    return render_template('index.html', require_invite_code=require_code)

@main_bp.route('/request-invite', methods=['POST'])
@limiter.limit("5 per minute; 20 per hour")
def request_invite():
    """Process invite request form submission."""
    try:
        # Get form data
        email_or_username = request.form.get('email_or_username', '').strip()
        invite_code = request.form.get('invite_code', '').strip()
        
        # Validate input
        if not email_or_username:
            flash('Please provide a Plex username or email address.', 'error')
            return redirect(url_for('main.index'))
        
        # Sanitize input
        email_or_username = sanitize_input(email_or_username)
        
        # Validate format
        if not validate_email_or_username(email_or_username):
            flash('Please provide a valid email address or Plex username.', 'error')
            return redirect(url_for('main.index'))
        
        # Check invite code if required
        if Config.INVITE_CODE and invite_code != Config.INVITE_CODE:
            flash('Invalid invite code. Please contact the administrator.', 'error')
            create_invite_request(email_or_username, 'failed', 'Invalid invite code')
            return redirect(url_for('main.index'))
        
        # Get configured libraries
        library_names = Config.get_library_config()
        
        # Send the invite
        plex_service.send_invite(email_or_username, library_names)
        
        # Log success
        create_invite_request(email_or_username, 'success')
        
        logger.info(f"Successfully sent invite to {email_or_username}")
        return render_template('success.html', email_or_username=email_or_username)
        
    except ValueError as e:
        # Plex-specific errors
        error_msg = str(e)
        flash(error_msg, 'error')
        create_invite_request(email_or_username, 'failed', error_msg)
        logger.error(f"Error sending invite to {email_or_username}: {error_msg}")
        return redirect(url_for('main.index'))
        
    except Exception as e:
        # Generic errors
        error_msg = f"An unexpected error occurred: {str(e)}"
        flash('An unexpected error occurred. Please try again later.', 'error')
        create_invite_request(email_or_username, 'failed', error_msg)
        logger.error(f"Unexpected error sending invite to {email_or_username}: {str(e)}")
        return redirect(url_for('main.index'))


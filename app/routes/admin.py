from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.plex_service import plex_service
from app.models import (AdminUser, get_recent_invites, get_invite_stats,
                        get_subscription_stats, Subscription, Tier, 
                        SubscriptionStatus, grandfather_existing_users,
                        update_subscription_status, db)
from app.stripe_service import stripe_service
from app.utils import is_safe_url
from config import Config
from datetime import datetime, timedelta
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
        # Get Plex libraries (this also ensures connection)
        libraries = plex_service.get_libraries()
        
        # Get currently configured libraries
        configured_libraries = Config.get_library_config()
        
        # Get recent invite requests (reduced from 50 to 20 for better performance)
        recent_invites = get_recent_invites(limit=20)
        
        # Get statistics
        stats = get_invite_stats()
        subscription_stats = get_subscription_stats()
        
        # Build connection status from successful library fetch (no redundant API call)
        connection_status = {
            'success': True,
            'server_name': Config.PLEX_SERVER_NAME,
            'library_count': len(libraries),
            'message': f"Successfully connected to {Config.PLEX_SERVER_NAME}"
        }
        
        return render_template(
            'admin/dashboard.html',
            libraries=libraries,
            configured_libraries=configured_libraries,
            recent_invites=recent_invites,
            stats=stats,
            subscription_stats=subscription_stats,
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
                             subscription_stats={'total': 0, 'active': 0, 'grandfathered': 0, 'mrr': 0},
                             connection_status={'success': False, 'error': str(e), 'message': f'Connection failed: {str(e)}'})

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

@admin_bp.route('/subscriptions')
@login_required
def subscriptions():
    """List all subscriptions with filtering."""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    
    # Build query
    query = Subscription.query
    
    # Apply status filter
    if status_filter != 'all':
        try:
            status_enum = SubscriptionStatus[status_filter]
            query = query.filter_by(status=status_enum)
        except KeyError:
            pass
    
    # Apply search filter
    if search:
        query = query.filter(
            db.or_(
                Subscription.email.ilike(f'%{search}%'),
                Subscription.plex_username.ilike(f'%{search}%')
            )
        )
    
    # Order by most recent first
    subscriptions = query.order_by(Subscription.created_at.desc()).all()
    
    # Get subscription stats
    stats = get_subscription_stats()
    
    return render_template('admin/subscriptions.html',
                         subscriptions=[s.to_dict() for s in subscriptions],
                         stats=stats,
                         status_filter=status_filter,
                         search=search)

@admin_bp.route('/subscription/<int:subscription_id>')
@login_required
def subscription_detail(subscription_id):
    """View single subscription details."""
    subscription = Subscription.query.get_or_404(subscription_id)
    
    # Get Stripe subscription details if available
    stripe_data = None
    if subscription.stripe_subscription_id:
        try:
            stripe_sub = stripe_service.get_subscription(subscription.stripe_subscription_id)
            stripe_data = {
                'status': stripe_sub.status,
                'current_period_end': datetime.fromtimestamp(stripe_sub.current_period_end),
                'cancel_at_period_end': stripe_sub.cancel_at_period_end,
                'billing_url': None
            }
            
            # Create billing portal session
            if subscription.stripe_customer_id:
                try:
                    portal = stripe_service.create_billing_portal_session(
                        subscription.stripe_customer_id,
                        url_for('admin.subscriptions', _external=True)
                    )
                    stripe_data['billing_url'] = portal.url
                except Exception as e:
                    logger.warning(f"Could not create billing portal: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching Stripe data: {str(e)}")
    
    return render_template('admin/subscription_detail.html',
                         subscription=subscription.to_dict(),
                         stripe_data=stripe_data)

@admin_bp.route('/subscription/<int:subscription_id>/revoke', methods=['POST'])
@login_required
def revoke_subscription(subscription_id):
    """Manually revoke a subscription."""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        
        # Revoke Plex access
        plex_service.revoke_access(subscription.plex_username)
        
        # Update subscription status
        update_subscription_status(
            subscription_id,
            status=SubscriptionStatus.cancelled
        )
        
        # Cancel Stripe subscription if exists
        if subscription.stripe_subscription_id:
            try:
                stripe_service.cancel_subscription(subscription.stripe_subscription_id, at_period_end=False)
            except Exception as e:
                logger.error(f"Error cancelling Stripe subscription: {str(e)}")
        
        flash(f'Successfully revoked access for {subscription.email}', 'success')
        logger.info(f"Admin revoked subscription {subscription_id}")
    
    except Exception as e:
        flash(f'Error revoking subscription: {str(e)}', 'error')
        logger.error(f"Error revoking subscription {subscription_id}: {str(e)}")
    
    return redirect(url_for('admin.subscriptions'))

@admin_bp.route('/subscription/<int:subscription_id>/extend', methods=['POST'])
@login_required
def extend_subscription(subscription_id):
    """Manually extend a subscription period."""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        days = int(request.form.get('days', 30))
        
        # Extend the period
        if subscription.current_period_end:
            new_end = subscription.current_period_end + timedelta(days=days)
        else:
            new_end = datetime.utcnow() + timedelta(days=days)
        
        update_subscription_status(
            subscription_id,
            status=SubscriptionStatus.active,
            current_period_end=new_end
        )
        
        flash(f'Extended subscription for {subscription.email} by {days} days', 'success')
        logger.info(f"Admin extended subscription {subscription_id} by {days} days")
    
    except Exception as e:
        flash(f'Error extending subscription: {str(e)}', 'error')
        logger.error(f"Error extending subscription {subscription_id}: {str(e)}")
    
    return redirect(url_for('admin.subscription_detail', subscription_id=subscription_id))

@admin_bp.route('/tiers')
@login_required
def tiers():
    """Manage subscription tiers."""
    tiers = Tier.query.order_by(Tier.price_monthly).all()
    libraries = plex_service.get_libraries()
    
    return render_template('admin/tiers.html',
                         tiers=[t.to_dict() for t in tiers],
                         libraries=libraries)

@admin_bp.route('/tier/create', methods=['POST'])
@login_required
def create_tier():
    """Create a new subscription tier."""
    try:
        name = request.form.get('name')
        description = request.form.get('description', '')
        price_monthly = float(request.form.get('price_monthly', 0))
        stripe_price_id = request.form.get('stripe_price_id', '').strip()
        allow_downloads = request.form.get('allow_downloads') == 'on'
        library_names = request.form.getlist('libraries')
        
        tier = Tier(
            name=name,
            description=description,
            price_monthly=price_monthly,
            stripe_price_id=stripe_price_id if stripe_price_id else None,
            allow_downloads=allow_downloads,
            library_names=library_names,
            active=True
        )
        
        db.session.add(tier)
        db.session.commit()
        
        flash(f'Successfully created tier: {name}', 'success')
        logger.info(f"Admin created tier: {name}")
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating tier: {str(e)}', 'error')
        logger.error(f"Error creating tier: {str(e)}")
    
    return redirect(url_for('admin.tiers'))

@admin_bp.route('/tier/<int:tier_id>/update', methods=['POST'])
@login_required
def update_tier(tier_id):
    """Update an existing tier."""
    try:
        tier = Tier.query.get_or_404(tier_id)
        
        tier.name = request.form.get('name')
        tier.description = request.form.get('description', '')
        tier.price_monthly = float(request.form.get('price_monthly', 0))
        tier.stripe_price_id = request.form.get('stripe_price_id', '').strip() or None
        tier.allow_downloads = request.form.get('allow_downloads') == 'on'
        tier.library_names = request.form.getlist('libraries')
        tier.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Successfully updated tier: {tier.name}', 'success')
        logger.info(f"Admin updated tier {tier_id}")
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating tier: {str(e)}', 'error')
        logger.error(f"Error updating tier {tier_id}: {str(e)}")
    
    return redirect(url_for('admin.tiers'))

@admin_bp.route('/tier/<int:tier_id>/toggle', methods=['POST'])
@login_required
def toggle_tier(tier_id):
    """Toggle tier active status."""
    try:
        tier = Tier.query.get_or_404(tier_id)
        tier.active = not tier.active
        tier.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = "activated" if tier.active else "deactivated"
        flash(f'Successfully {status} tier: {tier.name}', 'success')
        logger.info(f"Admin {status} tier {tier_id}")
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error toggling tier: {str(e)}', 'error')
        logger.error(f"Error toggling tier {tier_id}: {str(e)}")
    
    return redirect(url_for('admin.tiers'))

@admin_bp.route('/grandfather-users', methods=['POST'])
@login_required
def grandfather_users():
    """Grandfather existing users (migration script)."""
    try:
        count = grandfather_existing_users()
        flash(f'Successfully grandfathered {count} existing users', 'success')
        logger.info(f"Admin grandfathered {count} users")
    
    except Exception as e:
        flash(f'Error grandfathering users: {str(e)}', 'error')
        logger.error(f"Error grandfathering users: {str(e)}")
    
    return redirect(url_for('admin.subscriptions'))


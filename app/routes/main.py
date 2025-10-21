from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.plex_service import plex_service
from app.models import (create_invite_request, Tier, create_subscription, 
                        get_subscription_by_stripe_id, update_subscription_status,
                        SubscriptionStatus, db)
from app.stripe_service import stripe_service
from app.utils import validate_email_or_username, sanitize_input
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# Import limiter and csrf from app package
from app import limiter, csrf

@main_bp.route('/')
def index():
    """Redirect to plans page or show legacy invite form."""
    # Check if we have a free tier code configured
    if Config.FREE_TIER_INVITE_CODE:
        # Redirect to plans page (subscription model active)
        return redirect(url_for('main.plans'))
    else:
        # Legacy mode: show original invite form
        require_code = bool(Config.INVITE_CODE)
        return render_template('index.html', require_invite_code=require_code)

@main_bp.route('/plans')
def plans():
    """Display subscription tier selection page."""
    # Get tiers from database
    tiers = Tier.query.filter_by(active=True).order_by(Tier.price_monthly).all()
    
    # If no tiers in database, check config.json
    if not tiers:
        tier_configs = Config.get_tiers()
        tier_dicts = tier_configs
    else:
        tier_dicts = [tier.to_dict() for tier in tiers]
    
    return render_template('plans.html', 
                         tiers=tier_dicts,
                         stripe_publishable_key=Config.STRIPE_PUBLISHABLE_KEY,
                         free_tier_enabled=bool(Config.FREE_TIER_INVITE_CODE))

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

@main_bp.route('/checkout', methods=['POST'])
@limiter.limit("10 per hour")
def checkout():
    """Create Stripe checkout session for subscription."""
    try:
        tier_id = request.form.get('tier_id')
        email = request.form.get('email', '').strip()
        plex_username = request.form.get('plex_username', '').strip()
        
        # Validate input
        if not tier_id or not email:
            flash('Please provide all required information.', 'error')
            return redirect(url_for('main.plans'))
        
        # Use email as plex_username if not provided
        if not plex_username:
            plex_username = email
        
        # Validate email format
        if not validate_email_or_username(email):
            flash('Please provide a valid email address.', 'error')
            return redirect(url_for('main.plans'))
        
        # Get tier from database or config
        tier = Tier.query.get(int(tier_id))
        if not tier:
            # Try config.json
            tier_config = Config.get_tier_by_id(int(tier_id))
            if not tier_config:
                flash('Invalid subscription tier selected.', 'error')
                return redirect(url_for('main.plans'))
            tier_dict = tier_config
        else:
            tier_dict = tier.to_dict()
        
        # Create Stripe checkout session
        success_url = url_for('main.subscription_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = url_for('main.plans', _external=True)
        
        session = stripe_service.create_checkout_session(
            tier=tier_dict,
            customer_email=email,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'tier_id': str(tier_id),
                'plex_username': plex_username
            }
        )
        
        # Redirect to Stripe checkout
        return redirect(session.url, code=303)
    
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        flash('An error occurred. Please try again later.', 'error')
        return redirect(url_for('main.plans'))

@main_bp.route('/subscription-success')
def subscription_success():
    """Subscription payment success page."""
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            # Retrieve session to get customer email
            session = stripe_service.get_checkout_session(session_id)
            email = session.customer_email or session.customer_details.email
            return render_template('subscription_success.html', email=email)
        except Exception as e:
            logger.error(f"Error retrieving checkout session: {str(e)}")
    
    return render_template('subscription_success.html', email=None)

@main_bp.route('/webhook/stripe', methods=['POST'])
@csrf.exempt  # Stripe webhooks can't include CSRF tokens
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe_service.verify_webhook_signature(payload, sig_header)
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    event_type = event['type']
    
    try:
        if event_type == 'checkout.session.completed':
            # Payment successful, create subscription
            session = event['data']['object']
            handle_checkout_completed(session)
        
        elif event_type == 'customer.subscription.updated':
            # Subscription updated (renewal, cancellation scheduled, etc.)
            subscription = event['data']['object']
            handle_subscription_updated(subscription)
        
        elif event_type == 'customer.subscription.deleted':
            # Subscription cancelled/expired
            subscription = event['data']['object']
            handle_subscription_deleted(subscription)
        
        elif event_type == 'invoice.payment_failed':
            # Payment failed
            invoice = event['data']['object']
            handle_payment_failed(invoice)
        
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        logger.error(f"Error processing webhook event {event_type}: {str(e)}")
        return jsonify({'error': str(e)}), 500

def handle_checkout_completed(session):
    """Handle successful checkout - create subscription and send Plex invite."""
    try:
        stripe_subscription_id = session.get('subscription')
        customer_email = session.get('customer_email') or session.get('customer_details', {}).get('email')
        tier_id = int(session.get('metadata', {}).get('tier_id'))
        plex_username = session.get('metadata', {}).get('plex_username') or customer_email
        
        # Get subscription details from Stripe
        stripe_sub = stripe_service.get_subscription(stripe_subscription_id)
        sub_data = stripe_service.parse_subscription_data(stripe_sub)
        
        # Create subscription in database
        subscription = create_subscription(
            email=customer_email,
            plex_username=plex_username,
            tier_id=tier_id,
            stripe_customer_id=sub_data['stripe_customer_id'],
            stripe_subscription_id=sub_data['stripe_subscription_id'],
            current_period_start=sub_data['current_period_start'],
            current_period_end=sub_data['current_period_end']
        )
        
        # Get tier to send Plex invite
        tier = Tier.query.get(tier_id)
        if tier:
            # Send Plex invite with tier settings
            plex_service.send_invite_with_tier(plex_username, tier)
            
            # Create invite request record
            invite_request = create_invite_request(
                email_or_username=plex_username,
                status='success',
                error_message=None
            )
            invite_request.subscription_id = subscription.id
            db.session.commit()
            
            logger.info(f"Successfully created subscription and sent Plex invite for {customer_email}")
        else:
            logger.error(f"Tier {tier_id} not found when processing checkout")
    
    except Exception as e:
        logger.error(f"Error handling checkout completion: {str(e)}")
        raise

def handle_subscription_updated(stripe_subscription):
    """Handle subscription updates from Stripe."""
    try:
        subscription = get_subscription_by_stripe_id(stripe_subscription['id'])
        if subscription:
            # Parse updated data
            sub_data = stripe_service.parse_subscription_data(stripe_subscription)
            
            # Determine status
            stripe_status = sub_data['status']
            if stripe_status == 'active':
                status = SubscriptionStatus.active
            elif stripe_status == 'past_due':
                status = SubscriptionStatus.past_due
            elif stripe_status == 'canceled':
                status = SubscriptionStatus.cancelled
            else:
                status = SubscriptionStatus.active
            
            # Update subscription
            update_subscription_status(
                subscription.id,
                status=status,
                current_period_end=sub_data['current_period_end'],
                cancel_at_period_end=sub_data['cancel_at_period_end']
            )
            
            logger.info(f"Updated subscription {subscription.id} status to {status.value}")
    
    except Exception as e:
        logger.error(f"Error handling subscription update: {str(e)}")
        raise

def handle_subscription_deleted(stripe_subscription):
    """Handle subscription cancellation/deletion."""
    try:
        subscription = get_subscription_by_stripe_id(stripe_subscription['id'])
        if subscription:
            # Revoke Plex access
            plex_service.revoke_access(subscription.plex_username)
            
            # Update subscription status
            update_subscription_status(
                subscription.id,
                status=SubscriptionStatus.cancelled
            )
            
            logger.info(f"Cancelled subscription {subscription.id} and revoked Plex access for {subscription.email}")
    
    except Exception as e:
        logger.error(f"Error handling subscription deletion: {str(e)}")
        raise

def handle_payment_failed(invoice):
    """Handle failed payment."""
    try:
        stripe_subscription_id = invoice.get('subscription')
        if stripe_subscription_id:
            subscription = get_subscription_by_stripe_id(stripe_subscription_id)
            if subscription:
                # Update status to past_due
                update_subscription_status(
                    subscription.id,
                    status=SubscriptionStatus.past_due
                )
                
                logger.warning(f"Payment failed for subscription {subscription.id} ({subscription.email})")
    
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}")
        raise

@main_bp.route('/free-access', methods=['POST'])
@limiter.limit("5 per hour")
def free_access():
    """Handle free tier access with invite code."""
    try:
        email_or_username = request.form.get('email_or_username', '').strip()
        invite_code = request.form.get('invite_code', '').strip()
        
        # Validate input
        if not email_or_username or not invite_code:
            flash('Please provide both email/username and invite code.', 'error')
            return redirect(url_for('main.plans'))
        
        # Validate invite code
        if invite_code != Config.FREE_TIER_INVITE_CODE:
            flash('Invalid invite code.', 'error')
            create_invite_request(email_or_username, 'failed', 'Invalid free tier invite code')
            return redirect(url_for('main.plans'))
        
        # Validate email/username format
        if not validate_email_or_username(email_or_username):
            flash('Please provide a valid email address or Plex username.', 'error')
            return redirect(url_for('main.plans'))
        
        # Get or create "Grandfathered" tier
        tier = Tier.query.filter_by(name="Grandfathered").first()
        if not tier:
            # Use default tier or create one
            tier = Tier.query.first()
            if not tier:
                flash('No subscription tiers available. Please contact administrator.', 'error')
                return redirect(url_for('main.plans'))
        
        # Create grandfathered subscription (no expiry, no Stripe)
        subscription = create_subscription(
            email=email_or_username,
            plex_username=email_or_username,
            tier_id=tier.id,
            grandfathered=True,
            current_period_start=datetime.utcnow(),
            current_period_end=None  # No expiry
        )
        
        # Send Plex invite
        library_names = Config.get_library_config()  # Use default libraries
        plex_service.send_invite(email_or_username, library_names, allow_downloads=False)
        
        # Create invite request record
        invite_req = create_invite_request(
            email_or_username=email_or_username,
            status='success',
            error_message=None
        )
        invite_req.subscription_id = subscription.id
        invite_req.free_tier = True
        db.session.commit()
        
        logger.info(f"Successfully created free tier access for {email_or_username}")
        return render_template('success.html', email_or_username=email_or_username)
    
    except ValueError as e:
        error_msg = str(e)
        flash(error_msg, 'error')
        create_invite_request(email_or_username, 'failed', error_msg)
        logger.error(f"Error granting free access to {email_or_username}: {error_msg}")
        return redirect(url_for('main.plans'))
    
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        flash('An unexpected error occurred. Please try again later.', 'error')
        create_invite_request(email_or_username, 'failed', error_msg)
        logger.error(f"Unexpected error granting free access to {email_or_username}: {str(e)}")
        return redirect(url_for('main.plans'))


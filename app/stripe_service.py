import stripe
import logging
from config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize Stripe with secret key
stripe.api_key = Config.STRIPE_SECRET_KEY

class StripeService:
    """Service class for Stripe API operations."""
    
    def __init__(self):
        self.api_key = Config.STRIPE_SECRET_KEY
        self.publishable_key = Config.STRIPE_PUBLISHABLE_KEY
        self.webhook_secret = Config.STRIPE_WEBHOOK_SECRET
    
    def create_customer(self, email, name=None, metadata=None):
        """Create a Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            logger.info(f"Created Stripe customer: {customer.id} for {email}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe customer: {str(e)}")
            raise ValueError(f"Error creating customer: {str(e)}")
    
    def create_checkout_session(self, tier, customer_email, success_url, cancel_url, metadata=None):
        """Create a Stripe checkout session for a subscription."""
        try:
            # Ensure we have the necessary tier information
            if not tier.get('stripe_price_id'):
                raise ValueError(f"Tier '{tier.get('name')}' does not have a Stripe price ID configured")
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': tier['stripe_price_id'],
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=customer_email,
                metadata=metadata or {},
                subscription_data={
                    'metadata': metadata or {}
                }
            )
            logger.info(f"Created checkout session: {session.id} for {customer_email}")
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            raise ValueError(f"Error creating checkout session: {str(e)}")
    
    def get_checkout_session(self, session_id):
        """Retrieve a checkout session by ID."""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving checkout session: {str(e)}")
            raise ValueError(f"Error retrieving checkout session: {str(e)}")
    
    def get_subscription(self, subscription_id):
        """Get subscription details from Stripe."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving subscription: {str(e)}")
            raise ValueError(f"Error retrieving subscription: {str(e)}")
    
    def cancel_subscription(self, subscription_id, at_period_end=True):
        """Cancel a subscription (default: at end of billing period)."""
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                logger.info(f"Scheduled subscription {subscription_id} for cancellation at period end")
            else:
                subscription = stripe.Subscription.delete(subscription_id)
                logger.info(f"Immediately cancelled subscription {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            raise ValueError(f"Error cancelling subscription: {str(e)}")
    
    def reactivate_subscription(self, subscription_id):
        """Reactivate a subscription that was set to cancel."""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False
            )
            logger.info(f"Reactivated subscription {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Error reactivating subscription: {str(e)}")
            raise ValueError(f"Error reactivating subscription: {str(e)}")
    
    def verify_webhook_signature(self, payload, signature):
        """Verify webhook signature from Stripe."""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {str(e)}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {str(e)}")
            raise
    
    def parse_subscription_data(self, stripe_subscription):
        """Parse Stripe subscription object into our data format."""
        return {
            'stripe_subscription_id': stripe_subscription.id,
            'stripe_customer_id': stripe_subscription.customer,
            'status': stripe_subscription.status,
            'current_period_start': datetime.fromtimestamp(stripe_subscription.current_period_start),
            'current_period_end': datetime.fromtimestamp(stripe_subscription.current_period_end),
            'cancel_at_period_end': stripe_subscription.cancel_at_period_end,
        }
    
    def get_payment_methods(self, customer_id):
        """Get customer's payment methods."""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            return payment_methods.data
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving payment methods: {str(e)}")
            return []
    
    def create_billing_portal_session(self, customer_id, return_url):
        """Create a billing portal session for customer to manage subscription."""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Error creating billing portal session: {str(e)}")
            raise ValueError(f"Error creating billing portal: {str(e)}")

# Global instance
stripe_service = StripeService()


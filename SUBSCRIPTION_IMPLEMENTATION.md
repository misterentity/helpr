# Subscription System Implementation Summary

## Overview

Helpr has been transformed from a simple Plex invite tool into a full-featured subscription management system with Stripe payment integration, tiered access levels, automatic expiry handling, and grandfathering of existing users.

## What Was Implemented

### 1. Database Models ✅

**New Tables:**
- `tiers` - Subscription tier configuration
  - Stores tier name, price, Stripe price ID, download permissions, library assignments
- `subscriptions` - User subscription tracking
  - Links users to tiers, tracks Stripe customer/subscription IDs
  - Stores billing periods, status (active/past_due/cancelled/expired)
  - Grandfathering flag for legacy users
  
**Updated Tables:**
- `invite_requests` - Added subscription_id and free_tier columns

### 2. Stripe Integration ✅

**New Service: `app/stripe_service.py`**
- Create checkout sessions for subscriptions
- Handle webhook events (checkout complete, subscription updated/deleted, payment failed)
- Verify webhook signatures for security
- Create billing portal sessions
- Manage subscription lifecycle

**Webhook Handlers:**
- `checkout.session.completed` → Create subscription, send Plex invite
- `customer.subscription.updated` → Update subscription status
- `customer.subscription.deleted` → Revoke Plex access
- `invoice.payment_failed` → Mark subscription past_due

### 3. Plex Service Extensions ✅

**New Methods in `app/plex_service.py`:**
- `send_invite_with_tier(email, tier)` - Send invite with tier-specific settings
- `revoke_access(email)` - Remove user's Plex access
- `update_user_permissions(email, libraries, allow_downloads)` - Modify existing user permissions
- Updated `send_invite()` to support `allow_downloads` parameter

### 4. Background Scheduler ✅

**New Module: `app/scheduler.py`**
- Daily job (midnight) to check for expired subscriptions and revoke access
- Daily job (9 AM) to log expiry warnings for subscriptions ending in 3 days
- Uses APScheduler for reliable background processing

### 5. Public Routes ✅

**New Routes in `app/routes/main.py`:**
- `GET /plans` - Display subscription tier selection page
- `POST /checkout` - Create Stripe checkout session
- `GET /subscription-success` - Payment success confirmation
- `POST /webhook/stripe` - Handle Stripe webhook events (CSRF-exempt)
- `POST /free-access` - Process free tier invite code

**Updated Routes:**
- `/` - Redirects to `/plans` if subscription mode is active

### 6. Admin Routes ✅

**New Routes in `app/routes/admin.py`:**
- `GET /admin/subscriptions` - List all subscriptions with filtering
- `GET /admin/subscription/<id>` - View single subscription details
- `POST /admin/subscription/<id>/revoke` - Manually revoke subscription
- `POST /admin/subscription/<id>/extend` - Extend subscription period
- `GET /admin/tiers` - Manage subscription tiers (CRUD)
- `POST /admin/tier/create` - Create new tier
- `POST /admin/tier/<id>/update` - Update existing tier
- `POST /admin/tier/<id>/toggle` - Activate/deactivate tier
- `POST /admin/grandfather-users` - Migration script for existing users

**Updated Routes:**
- `/admin/dashboard` - Now shows subscription statistics and MRR

### 7. Templates ✅

**New Templates:**
- `templates/plans.html` - Subscription tier selection with pricing cards
- `templates/subscription_success.html` - Post-payment success page
- `templates/admin/subscriptions.html` - Subscription management interface
- `templates/admin/subscription_detail.html` - Single subscription view
- `templates/admin/tiers.html` - Tier configuration interface

**Updated Templates:**
- `templates/admin/dashboard.html` - Added subscription overview widget

### 8. Configuration ✅

**New Environment Variables:**
- `STRIPE_PUBLISHABLE_KEY` - Stripe public key
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Webhook signing secret
- `FREE_TIER_INVITE_CODE` - Optional code for free access

**Updated Files:**
- `env.template` - Added Stripe configuration
- `config.py` - Added tier management methods
- `requirements.txt` - Added `stripe` and `APScheduler`

### 9. Features

**Tiered Access:**
- ✅ Two-tier system: "Without Downloads" and "With Downloads"
- ✅ Configurable per-tier library access
- ✅ Download/sync permissions controlled by tier
- ✅ Dynamic tier creation and management via admin UI

**Subscription Management:**
- ✅ Monthly recurring billing via Stripe
- ✅ Automatic Plex invite on successful payment
- ✅ Subscription status tracking (active, past_due, cancelled, expired)
- ✅ Automatic access revocation on cancellation/expiry
- ✅ Monthly Recurring Revenue (MRR) tracking

**Grandfathering:**
- ✅ Migration script to convert existing users to lifetime subscriptions
- ✅ Grandfathered users have permanent access without expiry
- ✅ Admin can manually grandfather users via invite code

**Admin Capabilities:**
- ✅ View all subscriptions with filtering and search
- ✅ Manually revoke or extend subscriptions
- ✅ Create and manage subscription tiers
- ✅ View subscription statistics and revenue
- ✅ Link to Stripe billing portal for customer management

**Security:**
- ✅ Webhook signature verification
- ✅ Rate limiting on checkout endpoint
- ✅ CSRF protection on all forms (except webhooks)
- ✅ Idempotent webhook handling

## Architecture

```
User → /plans → Stripe Checkout → Webhook → Create Subscription → Send Plex Invite
                                              ↓
                                      Background Scheduler
                                              ↓
                               Check Expiry → Revoke Access
```

## Database Schema

```sql
tiers:
  - id (PK)
  - name, description
  - price_monthly
  - stripe_price_id
  - allow_downloads (boolean)
  - library_names (JSON)
  - active (boolean)

subscriptions:
  - id (PK)
  - email, plex_username
  - tier_id (FK)
  - status (enum)
  - stripe_customer_id, stripe_subscription_id
  - current_period_start, current_period_end
  - cancel_at_period_end (boolean)
  - grandfathered (boolean)
  - created_at, updated_at

invite_requests:
  - ... existing fields ...
  - subscription_id (FK, nullable)
  - free_tier (boolean)
```

## Migration Path

1. **Deploy code** with database migrations
2. **Configure Stripe** following STRIPE_SETUP.md
3. **Create tiers** in admin panel with Stripe Price IDs
4. **Grandfather existing users** via `/admin/grandfather-users`
5. **Test subscription flow** with Stripe test mode
6. **Go live** by switching to Stripe live keys

## Testing Checklist

- [ ] Create subscription with test card → Plex invite sent
- [ ] Payment fails → Status updates to past_due
- [ ] Subscription cancelled → Access revoked
- [ ] Subscription expires → Background job revokes access
- [ ] Free tier code → Grants access without Stripe
- [ ] Grandfather migration → Existing users get lifetime access
- [ ] Admin can manually revoke/extend subscriptions
- [ ] Tier CRUD operations work correctly

## Known Limitations

1. **Plex API Limitations**: `updateFriend()` may not be available in all PlexAPI versions; falls back to remove/re-invite
2. **No Proration**: Tier changes require manual handling (not automated)
3. **Single Currency**: Currently hardcoded to USD (can be extended)
4. **No Trial Periods**: Not implemented (can be added via Stripe)

## Future Enhancements

- Add trial periods (7/14/30 days free)
- Support tier changes with proration
- Add annual billing options
- Implement usage-based billing
- Add email notifications for expiry warnings
- Support multiple currencies
- Add discount codes/coupons
- Implement referral system

## Files Created

**Backend:**
- `app/stripe_service.py`
- `app/scheduler.py`

**Templates:**
- `app/templates/plans.html`
- `app/templates/subscription_success.html`
- `app/templates/admin/subscriptions.html`
- `app/templates/admin/subscription_detail.html`
- `app/templates/admin/tiers.html`

**Documentation:**
- `STRIPE_SETUP.md`
- `SUBSCRIPTION_IMPLEMENTATION.md` (this file)

## Files Modified

**Backend:**
- `app/__init__.py` - Initialize scheduler, create tables
- `app/models.py` - Added Tier, Subscription models and helper functions
- `app/plex_service.py` - Added revoke/update methods
- `app/routes/main.py` - Added subscription routes and webhook handler
- `app/routes/admin.py` - Added subscription management routes

**Configuration:**
- `config.py` - Added Stripe config and tier management methods
- `requirements.txt` - Added stripe, APScheduler
- `env.template` - Added Stripe environment variables

**Templates:**
- `app/templates/admin/dashboard.html` - Added subscription statistics

## Deployment Notes

### Environment Variables Required

```bash
# Existing
SECRET_KEY=...
PLEX_TOKEN=...
PLEX_SERVER_NAME=...
ADMIN_USERNAME=...
ADMIN_PASSWORD_HASH=...

# New - Required for Subscriptions
STRIPE_PUBLISHABLE_KEY=pk_test_... (or pk_live_...)
STRIPE_SECRET_KEY=sk_test_... (or sk_live_...)
STRIPE_WEBHOOK_SECRET=whsec_...

# New - Optional
FREE_TIER_INVITE_CODE=special_code
```

### Stripe Webhook URL

```
https://your-domain.com/webhook/stripe
```

Must be configured in Stripe Dashboard with selected events:
- checkout.session.completed
- customer.subscription.updated
- customer.subscription.deleted
- invoice.payment_failed

### Background Scheduler

The APScheduler runs in-process and starts automatically when the app starts. For production deployments with multiple workers, consider:
- Running scheduler in a separate process/container
- Using external job queue (Celery, RQ)
- Or ensure only one worker runs the scheduler

## Support

For setup assistance, see `STRIPE_SETUP.md`.
For technical questions, review the code comments in:
- `app/stripe_service.py`
- `app/scheduler.py`
- `app/models.py` (subscription-related functions)



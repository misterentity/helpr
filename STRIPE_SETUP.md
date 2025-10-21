# Stripe Setup Guide for Helpr Subscriptions

This guide walks you through setting up Stripe for subscription payments in Helpr.

## Prerequisites

- A Stripe account (sign up at https://stripe.com)
- Helpr application deployed and running
- Admin access to your Helpr instance

## Step 1: Get Stripe API Keys

1. Log in to the [Stripe Dashboard](https://dashboard.stripe.com/)
2. Click **Developers** in the left sidebar
3. Click **API keys**
4. Copy your **Publishable key** (starts with `pk_test_` for test mode)
5. Copy your **Secret key** (starts with `sk_test_` for test mode)
6. Add both to your `.env` file:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
   STRIPE_SECRET_KEY=sk_test_xxxxx
   ```

**Important**: Start with test mode keys during development. Switch to live mode keys (`pk_live_` and `sk_live_`) only when ready for production.

## Step 2: Create Products and Prices

### Create "Without Downloads" Tier

1. In Stripe Dashboard, go to **Products** → **Add Product**
2. Enter product details:
   - Name: `Without Downloads`
   - Description: `Access to Plex libraries without download capability`
3. Under **Pricing**, click **Add pricing**:
   - Price: `$9.99` (or your desired price)
   - Billing period: `Monthly`
   - Currency: `USD`
4. Click **Save product**
5. Click on the price you just created
6. **Copy the Price ID** (starts with `price_xxxxx`) - you'll need this later

### Create "With Downloads" Tier

1. Click **Add Product** again
2. Enter product details:
   - Name: `With Downloads`
   - Description: `Access to Plex libraries with download/sync capability`
3. Under **Pricing**, click **Add pricing**:
   - Price: `$14.99` (or your desired price)
   - Billing period: `Monthly`
   - Currency: `USD`
4. Click **Save product**
5. **Copy the Price ID** (starts with `price_xxxxx`)

## Step 3: Set Up Webhooks

Webhooks allow Stripe to notify your application about subscription events.

1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Enter your endpoint URL:
   ```
   https://your-domain.com/webhook/stripe
   ```
   Replace `your-domain.com` with your actual domain.

4. Click **Select events** and choose:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
   - `invoice.payment_succeeded`

5. Click **Add endpoint**
6. Click on the endpoint you just created
7. Reveal and copy the **Signing secret** (starts with `whsec_xxxxx`)
8. Add it to your `.env` file:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_xxxxx
   ```

### Testing Webhooks Locally

For local development, use the Stripe CLI:

```bash
# Install Stripe CLI
# Download from: https://stripe.com/docs/stripe-cli

# Login to Stripe
stripe login

# Forward webhooks to your local server
stripe listen --forward-to localhost:5000/webhook/stripe

# This will output a webhook signing secret starting with whsec_
# Use this secret in your .env file for local testing
```

## Step 4: Configure Tiers in Helpr

1. Log in to your Helpr admin dashboard
2. Navigate to **Tiers** (or go to `/admin/tiers`)
3. Create the "Without Downloads" tier:
   - Name: `Without Downloads`
   - Price: `9.99`
   - Stripe Price ID: Paste the price ID from Step 2
   - Allow Downloads: **Unchecked**
   - Libraries: Select the libraries to share
   - Click **Create Tier**

4. Create the "With Downloads" tier:
   - Name: `With Downloads`
   - Price: `14.99`
   - Stripe Price ID: Paste the price ID from Step 2
   - Allow Downloads: **Checked**
   - Libraries: Select the libraries to share
   - Click **Create Tier**

## Step 5: Configure Free Tier Access (Optional)

To allow free access with an invite code:

1. Add to your `.env` file:
   ```
   FREE_TIER_INVITE_CODE=your_secret_code_here
   ```
2. Share this code with users you want to grant free access
3. They can enter it on the plans page under "Have an Invite Code?"

## Step 6: Test the Flow

### Test Mode Testing

1. Visit your `/plans` page
2. Select a subscription tier
3. Enter your email
4. Click **Subscribe Now**
5. You'll be redirected to Stripe Checkout
6. Use a [test card number](https://stripe.com/docs/testing):
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`
   - Any future expiry date (e.g., 12/34)
   - Any 3-digit CVC

7. Complete the payment
8. Check if:
   - You're redirected to the success page
   - You receive a Plex invitation email
   - The subscription appears in `/admin/subscriptions`

### Webhook Testing

Check webhook delivery in Stripe Dashboard:
1. Go to **Developers** → **Webhooks**
2. Click on your endpoint
3. View **Recent deliveries** to see events

## Step 7: Go Live

When ready for production:

1. Switch to **Live mode** in Stripe Dashboard (toggle in top-right)
2. Create products and prices again in live mode
3. Get new API keys from **Developers** → **API keys**
4. Create a new webhook endpoint with live mode
5. Update your `.env` file with live keys:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
   STRIPE_SECRET_KEY=sk_live_xxxxx
   STRIPE_WEBHOOK_SECRET=whsec_xxxxx (from live webhook)
   ```
6. Update tier Stripe Price IDs in Helpr admin with live mode price IDs
7. Restart your application

## Step 8: Monitor Subscriptions

### In Stripe Dashboard

- View customers: **Customers** tab
- View subscriptions: **Subscriptions** tab
- View revenue: **Home** → Revenue chart

### In Helpr Admin

- View active subscriptions: `/admin/subscriptions`
- View MRR and stats: Admin dashboard
- Manage individual subscriptions: Click **View** on any subscription

## Troubleshooting

### Webhook Not Receiving Events

1. Check webhook endpoint URL is correct and publicly accessible
2. Verify webhook signing secret matches your `.env`
3. Check webhook logs in Stripe Dashboard
4. For local testing, ensure Stripe CLI is running: `stripe listen --forward-to localhost:5000/webhook/stripe`

### Payment Successful but No Plex Invite

1. Check application logs for errors
2. Verify Plex credentials in `.env` are correct
3. Check subscription was created in `/admin/subscriptions`
4. Try manually sending invite from admin panel

### Price ID Not Working

1. Ensure you copied the Price ID (starts with `price_`), not Product ID
2. Verify you're using the correct mode (test vs live)
3. Check price is for "Recurring" billing, not "One-time"

## Security Best Practices

1. **Never commit** `.env` file to version control
2. **Always validate** webhook signatures (done automatically)
3. **Use HTTPS** in production (required by Stripe)
4. **Rotate keys** if compromised via Stripe Dashboard
5. **Monitor** failed payments and fraud alerts in Stripe

## Support

- Stripe Documentation: https://stripe.com/docs
- Stripe Support: https://support.stripe.com
- Helpr Issues: Contact your system administrator



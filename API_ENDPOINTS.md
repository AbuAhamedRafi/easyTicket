# EasyTicket API Endpoints Documentation

Complete list of all API endpoints available in the EasyTicket platform.

---

## Table of Contents

- [Authentication](#authentication)
- [Event Categories](#event-categories)
- [Events](#events)
- [Tickets](#tickets)
- [Ticket Tiers](#ticket-tiers)
- [Day Passes](#day-passes)
- [Day+Tier Prices](#daytier-prices)
- [My Tickets](#my-tickets)
- [Orders](#orders)
- [Payments](#payments)
- [Webhooks](#webhooks)
- [API Documentation](#api-documentation)

---

## Authentication

Base URL: `/api/auth/`

### User Registration & Verification

#### `POST /api/auth/signup/`

**Register a new user**

- **Description**: Create a new user account (consumer or organizer). Email verification required before login.
- **Authentication**: Public
- **Rate Limit**: 5 requests per hour
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword",
    "password_confirm": "securepassword",
    "user_type": "consumer", // or "organizer"
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
  }
  ```
- **Response**: User ID, email, user_type
- **User Types**:
  - `consumer`: Can browse events and purchase tickets
  - `organizer`: Can create and manage events, scan tickets

#### `POST /api/auth/verify-email/`

**Verify email address**

- **Description**: Verify user email using the token sent via email
- **Authentication**: Public
- **Request Body**:
  ```json
  {
    "token": "verification-token-from-email"
  }
  ```
- **Response**: Confirmation message

#### `POST /api/auth/resend-verification/`

**Resend verification email**

- **Description**: Resend email verification link to user
- **Authentication**: Public
- **Request Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response**: Confirmation message

### Login & Logout

#### `POST /api/auth/login/`

**User login**

- **Description**: Authenticate user and return JWT tokens. Email must be verified.
- **Authentication**: Public
- **Rate Limit**: 5 requests per hour
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password"
  }
  ```
- **Response**: JWT tokens (access & refresh) in both response body AND HTTP-only cookies, user profile
- **Cookies Set**:
  - `access_token`: HTTP-only cookie (5 minutes)
  - `refresh_token`: HTTP-only cookie (7 days)

#### `POST /api/auth/logout/`

**User logout**

- **Description**: Blacklist the refresh token to logout user
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "refresh": "refresh-token" // Optional if sent via cookie
  }
  ```
- **Response**: Confirmation message, clears authentication cookies

#### `POST /api/auth/token/refresh/`

**Refresh JWT token**

- **Description**: Get a new access token using the refresh token
- **Authentication**: Public (requires valid refresh token)
- **Request Body**:
  ```json
  {
    "refresh": "refresh-token" // Optional if sent via cookie
  }
  ```
- **Response**: New access token (also set in HTTP-only cookie)

### User Profile

#### `GET /api/auth/profile/`

**Get current user profile**

- **Description**: Retrieve the authenticated user's profile information
- **Authentication**: Required
- **Response**: User profile data including user_type, email, name, etc.

#### `PUT /api/auth/profile/`

**Update user profile**

- **Description**: Update the authenticated user's profile
- **Authentication**: Required
- **Request Body**: User fields to update
- **Response**: Updated user profile

#### `PATCH /api/auth/profile/`

**Partially update user profile**

- **Description**: Partially update the authenticated user's profile
- **Authentication**: Required
- **Request Body**: Partial user fields to update
- **Response**: Updated user profile

#### `POST /api/auth/change-password/`

**Change password**

- **Description**: Change the authenticated user's password
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "old_password": "current-password",
    "new_password": "new-password",
    "new_password_confirm": "new-password"
  }
  ```
- **Response**: Confirmation message

---

## Event Categories

Base URL: `/api/events/categories/`

#### `GET /api/events/categories/`

**List all event categories**

- **Description**: Get a list of all active event categories
- **Authentication**: Public
- **Response**: Array of categories

#### `GET /api/events/categories/{slug}/`

**Get category details**

- **Description**: Get detailed information about a specific category
- **Authentication**: Public
- **Response**: Category details

#### `POST /api/events/categories/`

**Create new category**

- **Description**: Create a new event category (Admin only)
- **Authentication**: Required (Admin)
- **Request Body**: Category data
- **Response**: Created category

#### `PUT /api/events/categories/{slug}/`

**Update category**

- **Description**: Update an existing category (Admin only)
- **Authentication**: Required (Admin)
- **Request Body**: Category data
- **Response**: Updated category

#### `PATCH /api/events/categories/{slug}/`

**Partially update category**

- **Description**: Partially update a category (Admin only)
- **Authentication**: Required (Admin)
- **Request Body**: Partial category data
- **Response**: Updated category

#### `DELETE /api/events/categories/{slug}/`

**Delete category**

- **Description**: Delete a category (Admin only)
- **Authentication**: Required (Admin)
- **Response**: 204 No Content

---

## Events

Base URL: `/api/events/`

### Event CRUD

#### `GET /api/events/`

**List all events**

- **Description**: Get a list of all published events with filtering and search
- **Authentication**: Public
- **Query Parameters**:
  - `status`: Filter by status (draft/published/ongoing/completed/cancelled)
  - `category`: Filter by category ID
  - `is_free`: Filter free events (true/false)
  - `is_featured`: Filter featured events (true/false)
  - `venue_city`: Filter by city name
  - `pricing_type`: Filter by pricing type (simple/tiered/day_based/tier_and_day)
  - `search`: Search in title, description, tags, venue
  - `ordering`: Order by (start_date, -start_date, base_price, -base_price)
- **Response**: Paginated array of events

#### `GET /api/events/{slug}/`

**Get event details**

- **Description**: Get detailed information about a specific event
- **Authentication**: Public
- **Response**: Event details with tickets, categories, and pricing information

#### `POST /api/events/`

**Create new event**

- **Description**: Create a new event (Organizers only)
- **Authentication**: Required (Organizer)
- **Request Body**: Event data including pricing_type
  ```json
  {
    "title": "Amazing Music Festival",
    "description": "...",
    "category": "category-uuid",
    "pricing_type": "tier_and_day", // simple/tiered/day_based/tier_and_day
    "venue_name": "Central Park",
    "venue_city": "New York",
    "start_date": "2025-12-01T18:00:00Z",
    "end_date": "2025-12-03T23:00:00Z",
    "total_capacity": 5000,
    "is_free": false
  }
  ```
- **Response**: Created event
- **Note**: The `pricing_type` determines what ticket structures are allowed

#### `PUT /api/events/{slug}/`

**Update event**

- **Description**: Update an existing event (Owner only)
- **Authentication**: Required (Event Owner or Admin)
- **Request Body**: Event data
- **Response**: Updated event

#### `PATCH /api/events/{slug}/`

**Partially update event**

- **Description**: Partially update an event (Owner only)
- **Authentication**: Required (Event Owner or Admin)
- **Request Body**: Partial event data
- **Response**: Updated event

#### `DELETE /api/events/{slug}/`

**Delete event**

- **Description**: Delete an event (Owner only)
- **Authentication**: Required (Event Owner or Admin)
- **Response**: 204 No Content

### Event Custom Actions

#### `GET /api/events/my_events/`

**Get organizer's events**

- **Description**: Get all events created by the authenticated organizer
- **Authentication**: Required (Organizer only)
- **Access Control**: Explicit validation - consumers cannot access this endpoint
- **Response**: Array of organizer's events

#### `GET /api/events/upcoming/`

**Get upcoming events**

- **Description**: Get all upcoming published events
- **Authentication**: Public
- **Response**: Array of upcoming events

#### `GET /api/events/featured/`

**Get featured events**

- **Description**: Get all featured published events
- **Authentication**: Public
- **Response**: Array of featured events

#### `GET /api/events/search/`

**Search events**

- **Description**: Search events by various criteria
- **Authentication**: Public
- **Query Parameters**: Same as list endpoint
- **Response**: Array of matching events

#### `POST /api/events/{slug}/publish/`

**Publish event**

- **Description**: Change event status to published (Owner only)
- **Authentication**: Required (Event Owner or Admin)
- **Access Control**: Explicit validation ensures only event owner can publish
- **Response**: Published event details

#### `POST /api/events/{slug}/cancel/`

**Cancel event**

- **Description**: Cancel an event (Owner only)
- **Authentication**: Required (Event Owner or Admin)
- **Access Control**: Explicit validation ensures only event owner can cancel
- **Response**: Cancelled event details

---

## Tickets

Base URL: `/api/tickets/types/`

### Ticket Type CRUD

#### `GET /api/tickets/types/`

**List all ticket types**

- **Description**: Get a list of all ticket types with filtering
- **Authentication**: Public
- **Query Parameters**:
  - `event`: Filter by event ID
  - `pricing_type`: Filter by pricing type (simple/tiered/day_based/tier_and_day)
  - `is_active`: Filter active tickets (true/false)
  - `is_on_sale`: Filter tickets currently on sale (true/false)
  - `search`: Search in name, description, benefits
  - `ordering`: Order by (created_at, price, total_quantity)
- **Response**: Array of ticket types

#### `GET /api/tickets/types/{id}/`

**Get ticket type details**

- **Description**: Get detailed information about a specific ticket type including tiers, day passes, and day+tier prices
- **Authentication**: Public
- **Response**: Ticket type details with all pricing variations

#### `POST /api/tickets/types/`

**Create new ticket type**

- **Description**: Create a new ticket type for an event (Event organizer only)
- **Authentication**: Required (Organizer)
- **Request Body**: Ticket type data matching event's pricing_type
  ```json
  {
    "event": "event-uuid",
    "name": "VIP Pass",
    "pricing_type": "simple", // Must match event.pricing_type
    "price": 150.00, // For simple pricing only
    "total_quantity": 100,
    "sales_start": "2025-11-01T00:00:00Z",
    "sales_end": "2025-12-01T00:00:00Z",
    "min_purchase": 1,
    "max_purchase": 10,
    "benefits": "VIP lounge access, Meet & Greet"
  }
  ```
- **Response**: Created ticket type

#### `PUT /api/tickets/types/{id}/`

**Update ticket type**

- **Description**: Update an existing ticket type (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**: Ticket type data
- **Response**: Updated ticket type

#### `PATCH /api/tickets/types/{id}/`

**Partially update ticket type**

- **Description**: Partially update a ticket type (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**: Partial ticket type data
- **Response**: Updated ticket type

#### `DELETE /api/tickets/types/{id}/`

**Delete ticket type**

- **Description**: Delete a ticket type (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Response**: 204 No Content

### Ticket Type Custom Actions

#### `GET /api/tickets/types/by_event/`

**Get tickets for an event**

- **Description**: Get all ticket types for a specific event
- **Authentication**: Public
- **Query Parameters**:
  - `event_id`: Event UUID (required)
- **Response**: Array of ticket types for the event

#### `GET /api/tickets/types/available/`

**Get available tickets**

- **Description**: Get all currently available tickets (on sale and not sold out)
- **Authentication**: Public
- **Response**: Array of available ticket types

---

## Ticket Tiers

Base URL: `/api/tickets/tiers/`

**Used for**: `tiered` and `tier_and_day` pricing types

#### `GET /api/tickets/tiers/`

**List all ticket tiers**

- **Description**: Get a list of all ticket tiers
- **Authentication**: Public
- **Query Parameters**:
  - `ticket_type`: Filter by ticket type ID
  - `ordering`: Order by (tier_number, price)
- **Response**: Array of ticket tiers

#### `GET /api/tickets/tiers/{id}/`

**Get tier details**

- **Description**: Get detailed information about a specific tier
- **Authentication**: Public
- **Response**: Tier details

#### `POST /api/tickets/tiers/`

**Create new tier**

- **Description**: Create a new ticket tier (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**:
  ```json
  {
    "ticket_type": "ticket-type-uuid",
    "tier_number": 1,
    "name": "VIP",
    "price": 150.00,
    "quantity": 50,
    "sales_start": "2025-11-01T00:00:00Z",
    "sales_end": "2025-12-01T00:00:00Z"
  }
  ```
- **Response**: Created tier
- **Note**: Only for ticket types with pricing_type = "tiered"

#### `PUT /api/tickets/tiers/{id}/`

**Update tier**

- **Description**: Update an existing tier (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**: Tier data
- **Response**: Updated tier

#### `PATCH /api/tickets/tiers/{id}/`

**Partially update tier**

- **Description**: Partially update a tier (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**: Partial tier data
- **Response**: Updated tier

#### `DELETE /api/tickets/tiers/{id}/`

**Delete tier**

- **Description**: Delete a tier (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Response**: 204 No Content

---

## Day Passes

Base URL: `/api/tickets/day-passes/`

**Used for**: `day_based` pricing type ONLY (not for `tier_and_day`)

#### `GET /api/tickets/day-passes/`

**List all day passes**

- **Description**: Get a list of all day passes
- **Authentication**: Public
- **Query Parameters**:
  - `ticket_type`: Filter by ticket type ID
  - `is_all_days`: Filter all-days passes (true/false)
  - `ordering`: Order by (day_number, price, date)
- **Response**: Array of day passes

#### `GET /api/tickets/day-passes/{id}/`

**Get day pass details**

- **Description**: Get detailed information about a specific day pass
- **Authentication**: Public
- **Response**: Day pass details

#### `POST /api/tickets/day-passes/`

**Create new day pass**

- **Description**: Create a new day pass (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**:
  ```json
  {
    "ticket_type": "ticket-type-uuid",
    "day_number": 1,
    "name": "Day 1",
    "date": "2025-12-01",
    "price": 75.00,
    "quantity": 500,
    "is_all_days": false
  }
  ```
- **Response**: Created day pass
- **Note**: Only for ticket types with pricing_type = "day_based"

#### `PUT /api/tickets/day-passes/{id}/`

**Update day pass**

- **Description**: Update an existing day pass (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**: Day pass data
- **Response**: Updated day pass

#### `PATCH /api/tickets/day-passes/{id}/`

**Partially update day pass**

- **Description**: Partially update a day pass (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**: Partial day pass data
- **Response**: Updated day pass

#### `DELETE /api/tickets/day-passes/{id}/`

**Delete day pass**

- **Description**: Delete a day pass (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Response**: 204 No Content

---

## Day+Tier Prices

Base URL: `/api/tickets/day-tier-prices/`

**Used for**: `tier_and_day` pricing type ONLY

This creates a pricing matrix where each day has multiple tier options.

#### `GET /api/tickets/day-tier-prices/`

**List all day+tier prices**

- **Description**: Get a list of all day and tier price combinations
- **Authentication**: Public
- **Query Parameters**:
  - `ticket_type`: Filter by ticket type ID
  - `day_number`: Filter by specific day
  - `tier_number`: Filter by specific tier
  - `is_active`: Filter active combinations
  - `ordering`: Order by (day_number, tier_number, price, date)
- **Response**: Array of day+tier price combinations

#### `GET /api/tickets/day-tier-prices/{id}/`

**Get day+tier price details**

- **Description**: Get detailed information about a specific day+tier price combination
- **Authentication**: Public
- **Response**: Day+tier price details

#### `POST /api/tickets/day-tier-prices/`

**Create new day+tier price**

- **Description**: Create a new day+tier price combination (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**:
  ```json
  {
    "ticket_type": "ticket-type-uuid",
    "day_number": 1,
    "day_name": "Day 1",
    "date": "2025-12-01",
    "tier_number": 1,
    "tier_name": "VIP",
    "price": 200.00,
    "quantity": 50,
    "is_active": true
  }
  ```
- **Response**: Created day+tier price
- **Note**: Only for ticket types with pricing_type = "tier_and_day"
- **Example Matrix**:
  - Day 1 + VIP = $200
  - Day 1 + General = $100
  - Day 2 + VIP = $200
  - Day 2 + General = $100

#### `PUT /api/tickets/day-tier-prices/{id}/`

**Update day+tier price**

- **Description**: Update an existing day+tier price (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**: Day+tier price data
- **Response**: Updated day+tier price

#### `PATCH /api/tickets/day-tier-prices/{id}/`

**Partially update day+tier price**

- **Description**: Partially update a day+tier price (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Request Body**: Partial day+tier price data
- **Response**: Updated day+tier price

#### `DELETE /api/tickets/day-tier-prices/{id}/`

**Delete day+tier price**

- **Description**: Delete a day+tier price (Event organizer only)
- **Authentication**: Required (Event Organizer)
- **Response**: 204 No Content

#### `GET /api/tickets/day-tier-prices/matrix/`

**Get pricing matrix**

- **Description**: Get the full Day×Tier pricing matrix for a ticket type, organized by days and tiers
- **Authentication**: Public
- **Query Parameters**:
  - `ticket_type`: Ticket type UUID (required)
- **Response**:
  ```json
  {
    "ticket_type": "uuid",
    "days": [
      {"number": 1, "name": "Day 1"},
      {"number": 2, "name": "Day 2"}
    ],
    "tiers": [
      {"number": 1, "name": "VIP"},
      {"number": 2, "name": "General"}
    ],
    "matrix": {
      "1": {
        "1": {"id": "uuid", "price": "200.00", ...},
        "2": {"id": "uuid", "price": "100.00", ...}
      },
      "2": {
        "1": {"id": "uuid", "price": "200.00", ...},
        "2": {"id": "uuid", "price": "100.00", ...}
      }
    }
  }
  ```

---

## My Tickets

Base URL: `/api/tickets/my-tickets/`

Individual tickets purchased by users (generated after payment confirmation)

#### `GET /api/tickets/my-tickets/`

**List user's tickets**

- **Description**: Get all tickets for the authenticated user
- **Authentication**: Required
- **Query Parameters**:
  - `status`: Filter by status (active/used/cancelled/expired)
  - `is_used`: Filter used tickets (true/false)
  - `event`: Filter by event ID
  - `ordering`: Order by (created_at, event__start_date)
- **Response**: Array of user's tickets with QR codes and PDF download links

#### `GET /api/tickets/my-tickets/{id}/`

**Get ticket details**

- **Description**: Get detailed information about a specific ticket
- **Authentication**: Required (Ticket Owner)
- **Response**: Ticket details with QR code and PDF download link

#### `POST /api/tickets/my-tickets/verify/`

**Verify and scan ticket**

- **Description**: Verify a ticket's QR code and mark it as used. Staff/Organizer only.
- **Authentication**: Required (Staff or Organizer)
- **Access Control**: Explicit validation - only staff and organizers can scan tickets
- **Request Body**:
  ```json
  {
    "qr_code_data": "sha256-hash-from-qr-code"
  }
  ```
- **Response**: Ticket details and verification status
- **Use Case**: For entry/gate scanning at events

#### `GET /api/tickets/my-tickets/stats/`

**Get ticket statistics**

- **Description**: Get statistics about user's tickets
- **Authentication**: Required
- **Response**:
  ```json
  {
    "total_tickets": 10,
    "active_tickets": 5,
    "used_tickets": 3,
    "cancelled_tickets": 2,
    "upcoming_events": 2
  }
  ```

#### `GET /api/tickets/my-tickets/{id}/download/`

**Download ticket PDF**

- **Description**: Download ticket as PDF with QR code
- **Authentication**: Required (Ticket Owner)
- **Response**: PDF file

---

## Orders

Base URL: `/api/orders/`

### Order CRUD

#### `GET /api/orders/`

**List user's orders**

- **Description**: Get all orders for the authenticated user (admins see all orders)
- **Authentication**: Required
- **Response**: Paginated array of orders

#### `GET /api/orders/{id}/`

**Get order details**

- **Description**: Get detailed information about a specific order
- **Authentication**: Required (Order Owner or Admin)
- **Response**: Order details with items, tickets, payment info

#### `POST /api/orders/`

**Create new order**

- **Description**: Create a new order with ticket items. Inventory is locked within transaction to prevent overselling.
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "event": "event-uuid",
    "buyer_email": "buyer@example.com",
    "buyer_phone": "+1234567890",
    "buyer_name": "John Doe",
    "notes": "Optional notes",
    "items": [
      {
        "ticket_type_id": "ticket-type-uuid",
        "ticket_tier_id": "tier-uuid", // For tiered pricing
        "day_pass_id": "day-pass-uuid", // For day_based pricing
        "day_tier_price_id": "day-tier-price-uuid", // For tier_and_day pricing
        "quantity": 2
      }
    ]
  }
  ```
- **Response**: Created order with payment details
- **Note**: Include appropriate IDs based on event's pricing_type:
  - `simple`: Only `ticket_type_id` and `quantity`
  - `tiered`: `ticket_type_id`, `ticket_tier_id`, `quantity`
  - `day_based`: `ticket_type_id`, `day_pass_id`, `quantity`
  - `tier_and_day`: `ticket_type_id`, `day_tier_price_id`, `quantity`

### Order Custom Actions

#### `GET /api/orders/pending/`

**Get pending orders**

- **Description**: Get all pending orders for the authenticated user
- **Authentication**: Required
- **Response**: Array of pending orders

#### `GET /api/orders/confirmed/`

**Get confirmed orders**

- **Description**: Get all confirmed (paid) orders for the authenticated user
- **Authentication**: Required
- **Response**: Array of confirmed orders

#### `POST /api/orders/{id}/cancel/`

**Cancel order**

- **Description**: Cancel a pending order (restores ticket inventory)
- **Authentication**: Required (Order Owner or Admin)
- **Request Body**:
  ```json
  {
    "reason": "Changed my mind" // Optional
  }
  ```
- **Response**: Cancelled order details

#### `POST /api/orders/{id}/confirm_payment/`

**⚠️ Confirm payment (DEPRECATED - Testing Only)**

- **Description**: Manual payment confirmation for testing. Use Stripe webhooks in production.
- **Authentication**: Required (Order Owner)
- **Request Body**:
  ```json
  {
    "payment_id": "test-payment-id",
    "payment_method": "stripe"
  }
  ```
- **Response**: Confirmed order details
- **Warning**: This endpoint is for development/testing only. Production should use Stripe webhooks.

#### `GET /api/orders/stats/`

**Get order statistics**

- **Description**: Get statistics about user's orders
- **Authentication**: Required
- **Response**:
  ```json
  {
    "total_orders": 5,
    "pending_orders": 1,
    "confirmed_orders": 3,
    "cancelled_orders": 1,
    "total_spent": "250.00",
    "total_tickets": 10
  }
  ```

#### `GET /api/orders/my_tickets/`

**Get user's tickets**

- **Description**: Get all tickets purchased by the user across all confirmed orders
- **Authentication**: Required
- **Response**: Array of order items (tickets) from confirmed orders

#### `POST /api/orders/cleanup_expired/`

**Check for expired orders**

- **Description**: Check and update expired pending orders (Admin only)
- **Authentication**: Required (Admin)
- **Access Control**: Explicit validation - only administrators can trigger system cleanup
- **Response**: Count of expired orders marked as failed
- **Note**: Orders expire after 15 minutes if not paid

---

## Payments

Payment endpoints are part of the Orders API

Base URL: `/api/orders/{order_id}/`

#### `POST /api/orders/{id}/create-payment-intent/`

**Create Stripe Payment Intent**

- **Description**: Create a payment intent for order checkout. Generates client_secret for Stripe.js.
- **Authentication**: Required (Order Owner)
- **Rate Limit**: 10 requests per hour
- **Response**:
  ```json
  {
    "success": true,
    "payment_intent": {
      "client_secret": "pi_xxx_secret_xxx",
      "payment_intent_id": "pi_xxx",
      "amount": 10000, // in cents
      "currency": "usd",
      "status": "requires_payment_method"
    }
  }
  ```
- **Notes**:
  - Calculates service fee (5% of subtotal by default)
  - Updates order status to "processing"
  - Amount includes subtotal + service_fee - discount_amount

#### `GET /api/orders/{id}/payment-status/`

**Get Payment Status**

- **Description**: Check the current status of a payment from Stripe
- **Authentication**: Required (Order Owner or Admin)
- **Response**:
  ```json
  {
    "order_id": "uuid",
    "order_number": "OE-20251119-0001",
    "order_status": "confirmed",
    "payment_status": "succeeded",
    "amount": 100.0,
    "currency": "usd"
  }
  ```

#### `POST /api/orders/{id}/refund/`

**Refund Order**

- **Description**: Process a full or partial refund for a confirmed order
- **Authentication**: Required (Order Owner or Admin)
- **Request Body**:
  ```json
  {
    "amount": 50.0, // optional for partial refund, omit for full refund
    "reason": "requested_by_customer" // optional
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "refund_id": "re_xxx",
    "amount": 50.0,
    "currency": "usd",
    "status": "succeeded"
  }
  ```
- **Notes**:
  - Only confirmed orders can be refunded
  - Sends refund notification email
  - Updates order status to "refunded"

---

## Webhooks

Base URL: `/api/webhooks/`

#### `POST /api/webhooks/stripe/`

**Stripe Webhook Handler**

- **Description**: Handle Stripe webhook events (payment confirmations, refunds, etc.)
- **Authentication**: Stripe signature verification
- **Events Handled**:
  - `payment_intent.succeeded`: Confirm order, generate tickets, send confirmation email
  - `payment_intent.payment_failed`: Mark order as failed
  - `charge.refunded`: Handle refunds, update order status
- **Response**: 200 OK or appropriate error status
- **Security**: Verifies webhook signature using Stripe webhook secret
- **Side Effects**:
  - Creates individual Ticket records for confirmed orders
  - Sends ticket PDFs via email
  - Updates inventory (quantity_sold)

---

## API Documentation

Interactive API documentation powered by drf-spectacular

#### `GET /api/schema/`

**OpenAPI Schema**

- **Description**: Get the OpenAPI 3.0 schema for the API
- **Authentication**: Public
- **Format**: JSON
- **Use**: For generating client SDKs or importing into API tools

#### `GET /api/docs/`

**Swagger UI**

- **Description**: Interactive API documentation with Swagger UI
- **Authentication**: Public
- **URL**: `http://localhost:8001/api/docs/`
- **Features**: 
  - Try out API endpoints directly from browser
  - View request/response schemas
  - See example requests
  - Test with authentication

#### `GET /api/redoc/`

**ReDoc Documentation**

- **Description**: Beautiful API documentation with ReDoc
- **Authentication**: Public
- **URL**: `http://localhost:8001/api/redoc/`
- **Features**: 
  - Clean, organized documentation
  - Search functionality
  - Easy navigation
  - Code samples

---

## Response Status Codes

### Success Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Resource deleted successfully

### Client Error Codes

- `400 Bad Request`: Invalid request data or validation error
- `401 Unauthorized`: Authentication required or invalid credentials
- `403 Forbidden`: Permission denied (e.g., consumer accessing organizer endpoint)
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded

### Server Error Codes

- `500 Internal Server Error`: Server error

---

## Authentication

Most endpoints require authentication using JWT (JSON Web Tokens).

### How to Authenticate:

#### Option 1: HTTP-only Cookies (Recommended)
1. Login via `/api/auth/login/` 
2. Tokens are automatically set as HTTP-only cookies
3. Browser automatically includes cookies in subsequent requests
4. More secure (XSS protection)

#### Option 2: Authorization Header
1. Login via `/api/auth/login/` to get access and refresh tokens
2. Include the access token in the Authorization header:
   ```
   Authorization: Bearer <access_token>
   ```
3. Refresh the access token using `/api/auth/token/refresh/` when it expires

### Token Expiration:

- Access Token: 5 minutes (default)
- Refresh Token: 7 days (default)

### Custom Authentication Backend:

The system uses a custom authentication backend that checks both:
1. Authorization header (`Bearer token`)
2. HTTP-only cookies (`access_token`)

---

## Rate Limiting

Some endpoints have rate limiting to prevent abuse:

- **Authentication endpoints** (signup, login): 5 requests per hour
- **Payment endpoints**: 10 requests per hour
- **General authenticated endpoints**: 1000 requests per hour
- **Anonymous endpoints**: 100 requests per hour

Rate limit headers are included in responses:

- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets

---

## Access Control & User Types

The system enforces strict access control based on user types:

### Consumer (`user_type = "consumer"`)
- ✅ Browse events and view details
- ✅ Purchase tickets and view own orders
- ✅ View own ticket collection
- ✅ Manage own profile
- ❌ Cannot create or manage events
- ❌ Cannot scan/verify tickets
- ❌ Cannot access organizer endpoints

### Organizer (`user_type = "organizer"`)
- ✅ All consumer permissions
- ✅ Create and manage own events
- ✅ Create ticket types for own events
- ✅ Publish/cancel own events
- ✅ Scan tickets for own events
- ✅ View statistics for own events
- ❌ Cannot access other organizers' events
- ❌ Cannot modify events they don't own

### Admin/Staff (`is_staff = True`)
- ✅ Full access to all resources
- ✅ Manage all events, orders, and users
- ✅ Trigger system operations (cleanup, bulk actions)
- ✅ Process refunds for any order
- ✅ Access admin panel

### Permission Enforcement:

The system uses **explicit validation** in endpoint handlers to ensure proper access control:

```python
# Example: Organizer-only endpoint
if not request.user.is_authenticated:
    return 401 Unauthorized
if request.user.user_type != "organizer":
    return 403 Forbidden
```

This prevents permission bypasses and ensures security.

---

## Pricing Types Explained

Events support 4 different pricing structures:

### 1. Simple Pricing (`pricing_type = "simple"`)
- Single ticket type with one fixed price
- Example: "$50 per ticket"
- Use Case: Simple events with uniform pricing

### 2. Tiered Pricing (`pricing_type = "tiered"`)
- Multiple price tiers (VIP, General, Student, etc.)
- Each tier has different price and benefits
- Example: "VIP: $150, General: $75, Student: $40"
- Use Case: Events with different access levels

### 3. Day-Based Pricing (`pricing_type = "day_based"`)
- Different prices for different days
- Example: "Day 1: $50, Day 2: $60, All Days: $100"
- Use Case: Multi-day conferences or festivals

### 4. Tiered + Day-Based (`pricing_type = "tier_and_day"`)
- Combination of both - pricing matrix
- Each day has multiple tier options
- Example:
  - Day 1 VIP: $150
  - Day 1 General: $75
  - Day 2 VIP: $150
  - Day 2 General: $75
- Use Case: Multi-day events with VIP/General options per day
- **Uses DayTierPrice model** for the pricing matrix

### Ticket Structure by Pricing Type:

| Pricing Type | Models Used | Example |
|--------------|-------------|---------|
| `simple` | TicketType only | "$50 General Admission" |
| `tiered` | TicketType + TicketTier | "VIP ($150), General ($75), Student ($40)" |
| `day_based` | TicketType + DayPass | "Day 1 ($50), Day 2 ($60), All Days ($100)" |
| `tier_and_day` | TicketType + DayTierPrice | "Day 1 VIP ($150), Day 1 General ($75), Day 2 VIP ($150)..." |

---

## Filtering, Searching, and Ordering

Many list endpoints support filtering, searching, and ordering:

### Filtering

Use query parameters to filter results:

```
GET /api/events/?status=published&is_featured=true&pricing_type=tier_and_day
```

### Searching

Use the `search` parameter:

```
GET /api/events/?search=music
```

Search fields vary by endpoint:
- Events: title, description, tags, venue
- Tickets: name, description, benefits

### Ordering

Use the `ordering` parameter (prefix with `-` for descending):

```
GET /api/events/?ordering=-start_date
GET /api/tickets/types/?ordering=price
```

---

## Pagination

List endpoints are paginated with the following default settings:

- **Default page size**: 20 items
- **Maximum page size**: 100 items

Pagination parameters:

- `page`: Page number (1-indexed)
- `page_size`: Items per page (max 100)

Example:

```
GET /api/events/?page=2&page_size=10
```

Response includes pagination metadata:

```json
{
  "count": 50,
  "next": "http://localhost:8001/api/events/?page=3",
  "previous": "http://localhost:8001/api/events/?page=1",
  "results": [...]
}
```

---

## Order Workflow

### 1. Create Order
```
POST /api/orders/
```
- Creates pending order
- Locks inventory (prevents overselling)
- Order expires in 15 minutes

### 2. Create Payment Intent
```
POST /api/orders/{id}/create-payment-intent/
```
- Generates Stripe client_secret
- Calculates service fee (5%)
- Order status: "processing"

### 3. Complete Payment (Frontend)
- Use Stripe.js with client_secret
- Stripe processes payment
- Stripe sends webhook to backend

### 4. Webhook Confirmation
```
POST /api/webhooks/stripe/
```
- Confirms payment
- Generates individual tickets
- Sends confirmation email with PDFs
- Order status: "confirmed"

### 5. View Tickets
```
GET /api/tickets/my-tickets/
```
- View all purchased tickets
- Download PDFs
- Show QR codes

---

## Error Responses

All error responses follow a consistent format:

```json
{
  "error": "Error message",
  "detail": "Detailed explanation",
  "field_errors": {
    "field_name": ["Error for this field"]
  }
}
```

### Common Errors:

**Authentication Errors:**
- `"Authentication credentials were not provided."` (401)
- `"Invalid email or password."` (400)
- `"Email not verified. Please check your email."` (400)

**Permission Errors:**
- `"Only organizers can access this endpoint."` (403)
- `"Only administrators can trigger order cleanup."` (403)
- `"You do not have permission to publish this event."` (403)

**Validation Errors:**
- `"Only X tickets available for 'Ticket Name'"` (400)
- `"Order must have at least one item"` (400)
- `"Ticket type not found"` (400)

---

## Best Practices

### 1. Authentication
- Use HTTP-only cookies for better security
- Refresh tokens before they expire
- Handle 401 errors by redirecting to login

### 2. Order Creation
- Validate ticket availability before showing checkout
- Handle inventory errors gracefully
- Show clear error messages to users
- Implement order expiration countdown (15 minutes)

### 3. Payment Processing
- Use Stripe.js (never send card details to your server)
- Handle webhook events reliably
- Implement retry logic for failed webhooks
- Store payment_intent_id for reference

### 4. Error Handling
- Always check response status codes
- Display user-friendly error messages
- Log errors for debugging
- Implement proper retry logic

### 5. Performance
- Use pagination for large lists
- Cache event and category data
- Prefetch related data with select_related/prefetch_related
- Implement client-side caching

---

## Support

For API support or questions:
- Email: support@easyticket.com
- GitHub Issues: [Repository URL]
- Documentation: http://localhost:8001/api/docs/

---

## Changelog

### Version 1.1 (November 19, 2025)
- Added DayTierPrice model for tier_and_day pricing
- Added pricing_type field to Event model
- Implemented explicit permission validation
- Fixed transaction management for order creation
- Added HTTP-only cookie authentication
- Enhanced security with user type validation

### Version 1.0 (November 5, 2025)
- Initial API release
- Basic CRUD operations for events, tickets, orders
- Stripe payment integration
- JWT authentication

---

**Last Updated**: November 19, 2025  
**API Version**: 1.1  
**Documentation Version**: 2.0  
**Backend**: Django 5.2.7 + Django REST Framework  
**Database**: PostgreSQL  
**Payment Gateway**: Stripe

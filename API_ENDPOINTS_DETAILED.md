# EasyTicket API Documentation - Complete Reference

**Version:** 1.1  
**Last Updated:** November 19, 2025  
**Base URL:** `http://localhost:8001`

---

## 📋 Table of Contents

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
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)

---

## 🔐 Authentication

Base URL: `/api/auth/`

### POST /api/auth/signup/

**Register a new user**

**Request:**

```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "user_type": "consumer",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}
```

**Response:** `201 Created`

```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "user": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "john.doe@example.com",
    "user_type": "consumer"
  }
}
```

---

### POST /api/auth/verify-email/

**Verify email address**

**Request:**

```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** `200 OK`

```json
{
  "message": "Email verified successfully. You can now login.",
  "user": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "john.doe@example.com"
  }
}
```

---

### POST /api/auth/login/

**User login**

**Request:**

```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`

```json
{
  "message": "Login successful",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "consumer",
    "phone_number": "+1234567890",
    "is_email_verified": true,
    "date_joined": "2025-11-01T10:30:00Z",
    "last_login": "2025-11-19T08:25:00Z"
  }
}
```

**Cookies Set:**

- `access_token` (HTTP-only, 5 min)
- `refresh_token` (HTTP-only, 7 days)

---

### POST /api/auth/logout/

**User logout**

**Request:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`

```json
{
  "message": "Logout successful"
}
```

---

### POST /api/auth/token/refresh/

**Refresh JWT token**

**Request:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### GET /api/auth/profile/

**Get current user profile**

**Response:** `200 OK`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "consumer",
  "phone_number": "+1234567890",
  "is_email_verified": true,
  "date_joined": "2025-11-01T10:30:00Z",
  "last_login": "2025-11-19T08:25:00Z"
}
```

---

### PUT /api/auth/profile/

**Update user profile**

**Request:**

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+1987654321"
}
```

**Response:** `200 OK`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "user_type": "consumer",
  "phone_number": "+1987654321",
  "is_email_verified": true,
  "date_joined": "2025-11-01T10:30:00Z",
  "last_login": "2025-11-19T08:25:00Z"
}
```

---

### POST /api/auth/change-password/

**Change password**

**Request:**

```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

**Response:** `200 OK`

```json
{
  "message": "Password changed successfully"
}
```

---

## 📂 Event Categories

Base URL: `/api/events/categories/`

### GET /api/events/categories/

**List all categories**

**Response:** `200 OK`

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "Music",
      "slug": "music",
      "description": "Music concerts and festivals",
      "icon": "🎵",
      "is_active": true,
      "events_count": 45,
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
      "name": "Sports",
      "slug": "sports",
      "description": "Sports events and tournaments",
      "icon": "⚽",
      "is_active": true,
      "events_count": 32,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### GET /api/events/categories/{slug}/

**Get category details**

**Response:** `200 OK`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Music",
  "slug": "music",
  "description": "Music concerts and festivals",
  "icon": "🎵",
  "is_active": true,
  "events_count": 45,
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

### POST /api/events/categories/

**Create new category** (Admin only)

**Request:**

```json
{
  "name": "Technology",
  "slug": "technology",
  "description": "Tech conferences and workshops",
  "icon": "💻",
  "is_active": true
}
```

**Response:** `201 Created`

```json
{
  "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "name": "Technology",
  "slug": "technology",
  "description": "Tech conferences and workshops",
  "icon": "💻",
  "is_active": true,
  "events_count": 0,
  "created_at": "2025-11-19T08:30:00Z"
}
```

---

## 🎉 Events

Base URL: `/api/events/`

### GET /api/events/

**List all events**

**Query Parameters:**

- `status` - Filter by status (draft/published/ongoing/completed/cancelled)
- `category` - Filter by category ID
- `is_free` - Filter free events (true/false)
- `is_featured` - Filter featured events (true/false)
- `venue_city` - Filter by city name
- `pricing_type` - Filter by pricing type
- `search` - Search in title, description, tags, venue
- `ordering` - Order by field (start_date, -start_date, base_price)
- `page` - Page number
- `page_size` - Items per page (max 100)

**Response:** `200 OK`

```json
{
  "count": 156,
  "next": "http://localhost:8001/api/events/?page=2",
  "previous": null,
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "Summer Music Festival 2025",
      "slug": "summer-music-festival-2025",
      "short_description": "The biggest music festival of the year featuring top artists",
      "organizer": "7fa85f64-5717-4562-b3fc-2c963f66afa9",
      "organizer_name": "EventCo Ltd",
      "organizer_email": "organizer@eventco.com",
      "category": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "category_name": "Music",
      "pricing_type": "tier_and_day",
      "venue_name": "Central Park",
      "venue_city": "New York",
      "venue_country": "United States",
      "start_date": "2025-12-15T18:00:00Z",
      "end_date": "2025-12-17T23:00:00Z",
      "thumbnail_image": "http://localhost:8001/media/events/thumbnails/festival.jpg",
      "status": "published",
      "is_free": false,
      "base_price": "75.00",
      "currency": "USD",
      "is_featured": true,
      "is_upcoming": true,
      "is_ongoing": false,
      "is_past": false,
      "duration_days": 3,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ]
}
```

---

### GET /api/events/{slug}/

**Get event details**

**Response:** `200 OK`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Summer Music Festival 2025",
  "slug": "summer-music-festival-2025",
  "description": "Join us for the biggest music festival of the year! Featuring performances from world-renowned artists across multiple genres. Three days of non-stop entertainment, food, and fun in the heart of Central Park.",
  "short_description": "The biggest music festival of the year featuring top artists",
  "organizer": "7fa85f64-5717-4562-b3fc-2c963f66afa9",
  "organizer_name": "EventCo Ltd",
  "organizer_email": "organizer@eventco.com",
  "category": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "category_details": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Music",
    "slug": "music",
    "description": "Music concerts and festivals",
    "icon": "🎵"
  },
  "pricing_type": "tier_and_day",
  "venue_name": "Central Park",
  "venue_address": "Central Park, Manhattan",
  "venue_city": "New York",
  "venue_state": "NY",
  "venue_country": "United States",
  "venue_postal_code": "10024",
  "venue_latitude": "40.785091",
  "venue_longitude": "-73.968285",
  "start_date": "2025-12-15T18:00:00Z",
  "end_date": "2025-12-17T23:00:00Z",
  "banner": "http://localhost:8001/media/events/banners/festival-banner.jpg",
  "thumbnail_image": "http://localhost:8001/media/events/thumbnails/festival.jpg",
  "status": "published",
  "published_at": "2025-11-05T14:30:00Z",
  "total_capacity": 50000,
  "tickets_sold": 12500,
  "available_capacity": 37500,
  "is_free": false,
  "base_price": "75.00",
  "currency": "USD",
  "refund_policy": "Full refund up to 7 days before the event",
  "cancellation_policy": "Tickets can be transferred but not refunded after 7 days",
  "age_restriction": "18+",
  "tags": ["music", "festival", "summer", "outdoor"],
  "is_featured": true,
  "is_trending": true,
  "is_upcoming": true,
  "is_ongoing": false,
  "is_past": false,
  "duration_days": 3,
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-15T16:45:00Z"
}
```

---

### POST /api/events/

**Create new event** (Organizer only)

**Request:**

```json
{
  "title": "Tech Conference 2026",
  "description": "Annual technology conference featuring industry leaders",
  "short_description": "Join the biggest tech conference of the year",
  "category": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "pricing_type": "tiered",
  "venue_name": "Convention Center",
  "venue_address": "123 Tech Street",
  "venue_city": "San Francisco",
  "venue_state": "CA",
  "venue_country": "United States",
  "venue_postal_code": "94102",
  "venue_latitude": "37.774929",
  "venue_longitude": "-122.419416",
  "start_date": "2026-03-15T09:00:00Z",
  "end_date": "2026-03-17T18:00:00Z",
  "total_capacity": 5000,
  "is_free": false,
  "base_price": "299.00",
  "currency": "USD",
  "refund_policy": "Full refund up to 30 days before event",
  "age_restriction": "18+",
  "tags": ["technology", "conference", "networking"],
  "is_featured": false
}
```

**Response:** `201 Created`

```json
{
  "id": "8fa85f64-5717-4562-b3fc-2c963f66afb1",
  "title": "Tech Conference 2026",
  "slug": "tech-conference-2026",
  "description": "Annual technology conference featuring industry leaders",
  "short_description": "Join the biggest tech conference of the year",
  "organizer": "7fa85f64-5717-4562-b3fc-2c963f66afa9",
  "organizer_name": "EventCo Ltd",
  "organizer_email": "organizer@eventco.com",
  "category": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "category_details": {
    "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
    "name": "Technology",
    "slug": "technology"
  },
  "pricing_type": "tiered",
  "venue_name": "Convention Center",
  "venue_city": "San Francisco",
  "start_date": "2026-03-15T09:00:00Z",
  "end_date": "2026-03-17T18:00:00Z",
  "status": "draft",
  "is_free": false,
  "base_price": "299.00",
  "currency": "USD",
  "created_at": "2025-11-19T08:45:00Z"
}
```

---

### PUT /api/events/{slug}/

**Update event** (Owner only)

**Request:** Same as POST

**Response:** `200 OK` - Same structure as GET response

---

### PATCH /api/events/{slug}/

**Partially update event** (Owner only)

**Request:**

```json
{
  "is_featured": true,
  "base_price": "249.00"
}
```

**Response:** `200 OK` - Full event object with updates

---

### DELETE /api/events/{slug}/

**Delete event** (Owner only)

**Response:** `204 No Content`

---

### GET /api/events/my_events/

**Get organizer's events** (Organizer only)

**Response:** `200 OK`

```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "Summer Music Festival 2025",
      "slug": "summer-music-festival-2025",
      "status": "published",
      "start_date": "2025-12-15T18:00:00Z",
      "tickets_sold": 12500,
      "total_capacity": 50000,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ]
}
```

---

### POST /api/events/{slug}/publish/

**Publish event** (Owner only)

**Response:** `200 OK`

```json
{
  "id": "8fa85f64-5717-4562-b3fc-2c963f66afb1",
  "title": "Tech Conference 2026",
  "slug": "tech-conference-2026",
  "status": "published",
  "published_at": "2025-11-19T08:50:00Z",
  "message": "Event published successfully"
}
```

---

### POST /api/events/{slug}/cancel/

**Cancel event** (Owner only)

**Response:** `200 OK`

```json
{
  "id": "8fa85f64-5717-4562-b3fc-2c963f66afb1",
  "title": "Tech Conference 2026",
  "slug": "tech-conference-2026",
  "status": "cancelled",
  "message": "Event cancelled successfully"
}
```

---

## 🎫 Tickets

Base URL: `/api/tickets/types/`

### GET /api/tickets/types/

**List all ticket types**

**Query Parameters:**

- `event` - Filter by event ID
- `pricing_type` - Filter by pricing type
- `is_active` - Filter active tickets
- `is_on_sale` - Filter tickets on sale
- `search` - Search in name, description
- `ordering` - Order by field
- `page` - Page number
- `page_size` - Items per page

**Response:** `200 OK`

```json
{
  "count": 45,
  "next": "http://localhost:8001/api/tickets/types/?page=2",
  "previous": null,
  "results": [
    {
      "id": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
      "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "event_title": "Summer Music Festival 2025",
      "name": "Festival Pass",
      "description": "Access to all days and stages",
      "pricing_type": "tier_and_day",
      "price": null,
      "min_price": "75.00",
      "total_quantity": 50000,
      "quantity_sold": 12500,
      "available_quantity": 37500,
      "is_sold_out": false,
      "is_on_sale": true,
      "sales_start": "2025-11-01T00:00:00Z",
      "sales_end": "2025-12-15T18:00:00Z",
      "is_active": true,
      "created_at": "2025-11-01T10:30:00Z"
    }
  ]
}
```

---

### GET /api/tickets/types/{id}/

**Get ticket type details**

**Response:** `200 OK`

```json
{
  "id": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
  "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "event_title": "Summer Music Festival 2025",
  "name": "Festival Pass",
  "description": "Access to all days and stages of the festival. Includes entry to VIP areas and backstage tours.",
  "pricing_type": "tier_and_day",
  "price": null,
  "min_price": "75.00",
  "total_quantity": 50000,
  "quantity_sold": 12500,
  "available_quantity": 37500,
  "is_sold_out": false,
  "is_on_sale": true,
  "sales_start": "2025-11-01T00:00:00Z",
  "sales_end": "2025-12-15T18:00:00Z",
  "min_purchase": 1,
  "max_purchase": 10,
  "benefits": "VIP lounge access, Priority entry, Backstage tour, Free merchandise",
  "is_active": true,
  "tiers": [],
  "day_passes": [],
  "day_tier_prices": [
    {
      "id": "1fa85f64-5717-4562-b3fc-2c963f66afb3",
      "day_number": 1,
      "day_name": "Day 1",
      "date": "2025-12-15",
      "tier_number": 1,
      "tier_name": "VIP",
      "price": "200.00",
      "quantity": 500,
      "quantity_sold": 250,
      "available_quantity": 250,
      "is_sold_out": false,
      "is_on_sale": true,
      "is_active": true
    },
    {
      "id": "2fa85f64-5717-4562-b3fc-2c963f66afb4",
      "day_number": 1,
      "day_name": "Day 1",
      "date": "2025-12-15",
      "tier_number": 2,
      "tier_name": "General",
      "price": "75.00",
      "quantity": 5000,
      "quantity_sold": 2000,
      "available_quantity": 3000,
      "is_sold_out": false,
      "is_on_sale": true,
      "is_active": true
    }
  ],
  "created_at": "2025-11-01T10:30:00Z",
  "updated_at": "2025-11-15T14:20:00Z"
}
```

---

### POST /api/tickets/types/

**Create new ticket type** (Organizer only)

**Request:**

```json
{
  "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Early Bird Special",
  "description": "Limited early bird tickets at discounted price",
  "pricing_type": "simple",
  "price": "50.00",
  "total_quantity": 1000,
  "sales_start": "2025-11-01T00:00:00Z",
  "sales_end": "2025-11-30T23:59:59Z",
  "min_purchase": 1,
  "max_purchase": 4,
  "benefits": "20% discount, Priority access",
  "is_active": true
}
```

**Response:** `201 Created`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afb5",
  "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "event_title": "Summer Music Festival 2025",
  "name": "Early Bird Special",
  "description": "Limited early bird tickets at discounted price",
  "pricing_type": "simple",
  "price": "50.00",
  "min_price": "50.00",
  "total_quantity": 1000,
  "quantity_sold": 0,
  "available_quantity": 1000,
  "is_sold_out": false,
  "is_on_sale": true,
  "sales_start": "2025-11-01T00:00:00Z",
  "sales_end": "2025-11-30T23:59:59Z",
  "min_purchase": 1,
  "max_purchase": 4,
  "benefits": "20% discount, Priority access",
  "is_active": true,
  "created_at": "2025-11-19T09:00:00Z"
}
```

---

## 🎟️ Ticket Tiers

Base URL: `/api/tickets/tiers/`

### GET /api/tickets/tiers/

**List all ticket tiers**

**Response:** `200 OK`

```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "4fa85f64-5717-4562-b3fc-2c963f66afb6",
      "tier_number": 1,
      "name": "VIP",
      "price": "299.00",
      "quantity": 200,
      "quantity_sold": 150,
      "available_quantity": 50,
      "is_sold_out": false,
      "sales_start": "2025-11-01T00:00:00Z",
      "sales_end": "2026-03-15T09:00:00Z",
      "created_at": "2025-11-01T10:45:00Z"
    },
    {
      "id": "5fa85f64-5717-4562-b3fc-2c963f66afb7",
      "tier_number": 2,
      "name": "Regular",
      "price": "199.00",
      "quantity": 1000,
      "quantity_sold": 450,
      "available_quantity": 550,
      "is_sold_out": false,
      "sales_start": "2025-11-01T00:00:00Z",
      "sales_end": "2026-03-15T09:00:00Z",
      "created_at": "2025-11-01T10:45:00Z"
    }
  ]
}
```

---

### POST /api/tickets/tiers/

**Create new tier** (Organizer only)

**Request:**

```json
{
  "ticket_type": "8fa85f64-5717-4562-b3fc-2c963f66afb1",
  "tier_number": 3,
  "name": "Student",
  "price": "99.00",
  "quantity": 500,
  "sales_start": "2025-11-01T00:00:00Z",
  "sales_end": "2026-03-15T09:00:00Z"
}
```

**Response:** `201 Created`

```json
{
  "id": "6fa85f64-5717-4562-b3fc-2c963f66afb8",
  "tier_number": 3,
  "name": "Student",
  "price": "99.00",
  "quantity": 500,
  "quantity_sold": 0,
  "available_quantity": 500,
  "is_sold_out": false,
  "sales_start": "2025-11-01T00:00:00Z",
  "sales_end": "2026-03-15T09:00:00Z",
  "created_at": "2025-11-19T09:15:00Z"
}
```

---

## 📅 Day Passes

Base URL: `/api/tickets/day-passes/`

### GET /api/tickets/day-passes/

**List all day passes**

**Response:** `200 OK`

```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "7fa85f64-5717-4562-b3fc-2c963f66afb9",
      "day_number": 1,
      "name": "Day 1 Pass",
      "date": "2025-12-15",
      "price": "75.00",
      "quantity": 10000,
      "quantity_sold": 4500,
      "available_quantity": 5500,
      "is_sold_out": false,
      "is_all_days": false,
      "created_at": "2025-11-01T11:00:00Z"
    },
    {
      "id": "8fa85f64-5717-4562-b3fc-2c963f66afc1",
      "day_number": null,
      "name": "All Days Pass",
      "date": null,
      "price": "200.00",
      "quantity": 5000,
      "quantity_sold": 1200,
      "available_quantity": 3800,
      "is_sold_out": false,
      "is_all_days": true,
      "created_at": "2025-11-01T11:00:00Z"
    }
  ]
}
```

---

### POST /api/tickets/day-passes/

**Create new day pass** (Organizer only)

**Request:**

```json
{
  "ticket_type": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
  "day_number": 2,
  "name": "Day 2 Pass",
  "date": "2025-12-16",
  "price": "85.00",
  "quantity": 10000,
  "is_all_days": false
}
```

**Response:** `201 Created`

```json
{
  "id": "9fa85f64-5717-4562-b3fc-2c963f66afc2",
  "day_number": 2,
  "name": "Day 2 Pass",
  "date": "2025-12-16",
  "price": "85.00",
  "quantity": 10000,
  "quantity_sold": 0,
  "available_quantity": 10000,
  "is_sold_out": false,
  "is_all_days": false,
  "created_at": "2025-11-19T09:30:00Z"
}
```

---

## 🎯 Day+Tier Prices

Base URL: `/api/tickets/day-tier-prices/`

### GET /api/tickets/day-tier-prices/

**List all day+tier prices**

**Response:** `200 OK`

```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "1fa85f64-5717-4562-b3fc-2c963f66afb3",
      "day_number": 1,
      "day_name": "Day 1",
      "date": "2025-12-15",
      "tier_number": 1,
      "tier_name": "VIP",
      "price": "200.00",
      "quantity": 500,
      "quantity_sold": 250,
      "available_quantity": 250,
      "is_sold_out": false,
      "is_on_sale": true,
      "is_active": true,
      "sales_start": "2025-11-01T00:00:00Z",
      "sales_end": "2025-12-15T18:00:00Z",
      "created_at": "2025-11-01T11:15:00Z"
    }
  ]
}
```

---

### POST /api/tickets/day-tier-prices/

**Create new day+tier price** (Organizer only)

**Request:**

```json
{
  "ticket_type": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
  "day_number": 3,
  "day_name": "Day 3",
  "date": "2025-12-17",
  "tier_number": 1,
  "tier_name": "VIP",
  "price": "250.00",
  "quantity": 500,
  "is_active": true,
  "sales_start": "2025-11-01T00:00:00Z",
  "sales_end": "2025-12-17T23:00:00Z"
}
```

**Response:** `201 Created`

```json
{
  "id": "2fa85f64-5717-4562-b3fc-2c963f66afc3",
  "day_number": 3,
  "day_name": "Day 3",
  "date": "2025-12-17",
  "tier_number": 1,
  "tier_name": "VIP",
  "price": "250.00",
  "quantity": 500,
  "quantity_sold": 0,
  "available_quantity": 500,
  "is_sold_out": false,
  "is_on_sale": true,
  "is_active": true,
  "sales_start": "2025-11-01T00:00:00Z",
  "sales_end": "2025-12-17T23:00:00Z",
  "created_at": "2025-11-19T09:45:00Z"
}
```

---

### GET /api/tickets/day-tier-prices/matrix/

**Get pricing matrix**

**Query:** `?ticket_type=9fa85f64-5717-4562-b3fc-2c963f66afb2`

**Response:** `200 OK`

```json
{
  "ticket_type": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
  "days": [
    { "number": 1, "name": "Day 1" },
    { "number": 2, "name": "Day 2" },
    { "number": 3, "name": "Day 3" }
  ],
  "tiers": [
    { "number": 1, "name": "VIP" },
    { "number": 2, "name": "General" }
  ],
  "matrix": {
    "1": {
      "1": {
        "id": "1fa85f64-5717-4562-b3fc-2c963f66afb3",
        "price": "200.00",
        "quantity": 500,
        "available_quantity": 250,
        "is_sold_out": false
      },
      "2": {
        "id": "2fa85f64-5717-4562-b3fc-2c963f66afb4",
        "price": "75.00",
        "quantity": 5000,
        "available_quantity": 3000,
        "is_sold_out": false
      }
    },
    "2": {
      "1": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afb5",
        "price": "200.00",
        "quantity": 500,
        "available_quantity": 300,
        "is_sold_out": false
      },
      "2": {
        "id": "4fa85f64-5717-4562-b3fc-2c963f66afb6",
        "price": "75.00",
        "quantity": 5000,
        "available_quantity": 3500,
        "is_sold_out": false
      }
    }
  }
}
```

---

## 🎫 My Tickets

Base URL: `/api/tickets/my-tickets/`

### GET /api/tickets/my-tickets/

**List user's tickets**

**Response:** `200 OK`

```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afc4",
      "order": "4fa85f64-5717-4562-b3fc-2c963f66afc5",
      "order_number": "OE-20251119-0001",
      "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "event_title": "Summer Music Festival 2025",
      "event_date": "2025-12-15T18:00:00Z",
      "event_location": "Central Park, New York",
      "ticket_type": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
      "ticket_name": "Festival Pass - Day 1 VIP",
      "tier_name": "VIP",
      "day_name": "Day 1",
      "ticket_number": "TKT-20251119-0001",
      "qr_code_data": "abc123def456...",
      "qr_code_image": "http://localhost:8001/media/tickets/qr/ticket-001.png",
      "pdf_url": "http://localhost:8001/api/tickets/my-tickets/3fa85f64-5717-4562-b3fc-2c963f66afc4/download/",
      "status": "active",
      "is_used": false,
      "used_at": null,
      "created_at": "2025-11-19T10:00:00Z"
    }
  ]
}
```

---

### GET /api/tickets/my-tickets/{id}/

**Get ticket details**

**Response:** `200 OK`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afc4",
  "order": "4fa85f64-5717-4562-b3fc-2c963f66afc5",
  "order_number": "OE-20251119-0001",
  "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "event_title": "Summer Music Festival 2025",
  "event_date": "2025-12-15T18:00:00Z",
  "event_location": "Central Park, New York",
  "event_venue": "Central Park",
  "event_address": "Central Park, Manhattan, New York, NY 10024",
  "ticket_type": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
  "ticket_name": "Festival Pass - Day 1 VIP",
  "tier_name": "VIP",
  "day_name": "Day 1",
  "ticket_number": "TKT-20251119-0001",
  "qr_code_data": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
  "qr_code_image": "http://localhost:8001/media/tickets/qr/ticket-001.png",
  "pdf_url": "http://localhost:8001/api/tickets/my-tickets/3fa85f64-5717-4562-b3fc-2c963f66afc4/download/",
  "buyer_name": "John Doe",
  "buyer_email": "john.doe@example.com",
  "status": "active",
  "is_used": false,
  "used_at": null,
  "verified_by": null,
  "created_at": "2025-11-19T10:00:00Z",
  "updated_at": "2025-11-19T10:00:00Z"
}
```

---

### POST /api/tickets/my-tickets/verify/

**Verify and scan ticket** (Staff/Organizer only)

**Request:**

```json
{
  "qr_code_data": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
}
```

**Response:** `200 OK`

```json
{
  "success": true,
  "message": "Ticket verified successfully",
  "ticket": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afc4",
    "ticket_number": "TKT-20251119-0001",
    "event_title": "Summer Music Festival 2025",
    "ticket_name": "Festival Pass - Day 1 VIP",
    "buyer_name": "John Doe",
    "status": "active",
    "is_used": true,
    "used_at": "2025-12-15T18:30:00Z",
    "verified_by": "organizer@eventco.com"
  }
}
```

**Error Response:** `400 Bad Request`

```json
{
  "error": "Ticket already used",
  "detail": "This ticket was scanned on 2025-12-15T18:30:00Z",
  "ticket": {
    "ticket_number": "TKT-20251119-0001",
    "used_at": "2025-12-15T18:30:00Z"
  }
}
```

---

### GET /api/tickets/my-tickets/stats/

**Get ticket statistics**

**Response:** `200 OK`

```json
{
  "total_tickets": 12,
  "active_tickets": 8,
  "used_tickets": 3,
  "cancelled_tickets": 1,
  "upcoming_events": 5,
  "past_events": 2
}
```

---

## 📦 Orders

Base URL: `/api/orders/`

### GET /api/orders/

**List user's orders**

**Response:** `200 OK`

```json
{
  "count": 15,
  "next": "http://localhost:8001/api/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": "4fa85f64-5717-4562-b3fc-2c963f66afc5",
      "order_number": "OE-20251119-0001",
      "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "event_name": "Summer Music Festival 2025",
      "status": "confirmed",
      "total_amount": "425.00",
      "currency": "USD",
      "total_tickets": 2,
      "is_paid": true,
      "is_expired": false,
      "created_at": "2025-11-19T09:45:00Z",
      "expires_at": null
    }
  ]
}
```

---

### GET /api/orders/{id}/

**Get order details**

**Response:** `200 OK`

```json
{
  "id": "4fa85f64-5717-4562-b3fc-2c963f66afc5",
  "order_number": "OE-20251119-0001",
  "user": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "event_name": "Summer Music Festival 2025",
  "event_image": "http://localhost:8001/media/events/banners/festival-banner.jpg",
  "event_date": "2025-12-15T18:00:00Z",
  "event_location": "New York",
  "status": "confirmed",
  "subtotal": "400.00",
  "service_fee": "20.00",
  "discount_amount": "0.00",
  "total_amount": "420.00",
  "currency": "USD",
  "payment_method": "stripe",
  "payment_id": "pi_1234567890abcdef",
  "paid_at": "2025-11-19T09:50:00Z",
  "buyer_email": "john.doe@example.com",
  "buyer_phone": "+1234567890",
  "buyer_name": "John Doe",
  "promo_code": null,
  "notes": "",
  "cancellation_reason": null,
  "cancelled_at": null,
  "items": [
    {
      "id": "5fa85f64-5717-4562-b3fc-2c963f66afc6",
      "ticket_type": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
      "ticket_tier": null,
      "day_pass": null,
      "day_tier_price": "1fa85f64-5717-4562-b3fc-2c963f66afb3",
      "quantity": 2,
      "unit_price": "200.00",
      "subtotal": "400.00",
      "ticket_name": "Festival Pass",
      "tier_name": "VIP",
      "day_name": "Day 1",
      "full_ticket_name": "Festival Pass - Day 1 VIP",
      "created_at": "2025-11-19T09:45:00Z"
    }
  ],
  "total_tickets": 2,
  "is_paid": true,
  "is_expired": false,
  "created_at": "2025-11-19T09:45:00Z",
  "updated_at": "2025-11-19T09:50:00Z",
  "expires_at": null
}
```

---

### POST /api/orders/

**Create new order**

**Request (Simple Pricing):**

```json
{
  "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "buyer_email": "john.doe@example.com",
  "buyer_phone": "+1234567890",
  "buyer_name": "John Doe",
  "notes": "Please send tickets to my email",
  "items": [
    {
      "ticket_type_id": "3fa85f64-5717-4562-b3fc-2c963f66afb5",
      "quantity": 2
    }
  ]
}
```

**Request (Tiered Pricing):**

```json
{
  "event": "8fa85f64-5717-4562-b3fc-2c963f66afb1",
  "buyer_email": "jane.smith@example.com",
  "buyer_phone": "+1987654321",
  "buyer_name": "Jane Smith",
  "items": [
    {
      "ticket_type_id": "4fa85f64-5717-4562-b3fc-2c963f66afb6",
      "ticket_tier_id": "5fa85f64-5717-4562-b3fc-2c963f66afb7",
      "quantity": 1
    }
  ]
}
```

**Request (Day-Based Pricing):**

```json
{
  "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "buyer_email": "bob.jones@example.com",
  "buyer_phone": "+1555666777",
  "buyer_name": "Bob Jones",
  "items": [
    {
      "ticket_type_id": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
      "day_pass_id": "7fa85f64-5717-4562-b3fc-2c963f66afb9",
      "quantity": 3
    }
  ]
}
```

**Request (Tier+Day Pricing):**

```json
{
  "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "buyer_email": "alice.brown@example.com",
  "buyer_phone": "+1444555666",
  "buyer_name": "Alice Brown",
  "items": [
    {
      "ticket_type_id": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
      "day_tier_price_id": "1fa85f64-5717-4562-b3fc-2c963f66afb3",
      "quantity": 2
    },
    {
      "ticket_type_id": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
      "day_tier_price_id": "2fa85f64-5717-4562-b3fc-2c963f66afb4",
      "quantity": 1
    }
  ]
}
```

**Response:** `201 Created`

```json
{
  "id": "6fa85f64-5717-4562-b3fc-2c963f66afc7",
  "order_number": "OE-20251119-0002",
  "user": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "event": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "event_name": "Summer Music Festival 2025",
  "status": "pending",
  "subtotal": "100.00",
  "service_fee": "0.00",
  "discount_amount": "0.00",
  "total_amount": "100.00",
  "currency": "USD",
  "payment_method": "pending",
  "buyer_email": "john.doe@example.com",
  "buyer_phone": "+1234567890",
  "buyer_name": "John Doe",
  "items": [
    {
      "id": "7fa85f64-5717-4562-b3fc-2c963f66afc8",
      "ticket_type": "3fa85f64-5717-4562-b3fc-2c963f66afb5",
      "quantity": 2,
      "unit_price": "50.00",
      "subtotal": "100.00",
      "ticket_name": "Early Bird Special",
      "full_ticket_name": "Early Bird Special"
    }
  ],
  "total_tickets": 2,
  "is_paid": false,
  "is_expired": false,
  "created_at": "2025-11-19T10:15:00Z",
  "expires_at": "2025-11-19T10:30:00Z"
}
```

---

### POST /api/orders/{id}/cancel/

**Cancel order**

**Request:**

```json
{
  "reason": "Changed my mind about attending"
}
```

**Response:** `200 OK`

```json
{
  "id": "6fa85f64-5717-4562-b3fc-2c963f66afc7",
  "order_number": "OE-20251119-0002",
  "status": "cancelled",
  "cancellation_reason": "Changed my mind about attending",
  "cancelled_at": "2025-11-19T10:20:00Z",
  "message": "Order cancelled successfully"
}
```

---

### GET /api/orders/stats/

**Get order statistics**

**Response:** `200 OK`

```json
{
  "total_orders": 15,
  "pending_orders": 2,
  "confirmed_orders": 11,
  "cancelled_orders": 2,
  "total_spent": "1250.00",
  "total_tickets": 28,
  "upcoming_events": 8
}
```

---

### GET /api/orders/my_tickets/

**Get user's tickets from all orders**

**Response:** `200 OK`

```json
{
  "count": 28,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "5fa85f64-5717-4562-b3fc-2c963f66afc6",
      "order": "4fa85f64-5717-4562-b3fc-2c963f66afc5",
      "ticket_type": "9fa85f64-5717-4562-b3fc-2c963f66afb2",
      "quantity": 2,
      "unit_price": "200.00",
      "ticket_name": "Festival Pass",
      "tier_name": "VIP",
      "day_name": "Day 1",
      "full_ticket_name": "Festival Pass - Day 1 VIP"
    }
  ]
}
```

---

## 💳 Payments

Base URL: `/api/orders/{order_id}/`

### POST /api/orders/{id}/create-payment-intent/

**Create Stripe Payment Intent**

**Response:** `200 OK`

```json
{
  "success": true,
  "payment_intent": {
    "client_secret": "pi_1234567890_secret_abcdefghijklmnop",
    "payment_intent_id": "pi_1234567890abcdef",
    "amount": 42000,
    "currency": "usd",
    "status": "requires_payment_method"
  }
}
```

**Error Response:** `400 Bad Request`

```json
{
  "error": "Order cannot be paid",
  "status": "confirmed",
  "detail": "This order has already been paid"
}
```

---

### GET /api/orders/{id}/payment-status/

**Get Payment Status**

**Response:** `200 OK`

```json
{
  "order_id": "4fa85f64-5717-4562-b3fc-2c963f66afc5",
  "order_number": "OE-20251119-0001",
  "order_status": "confirmed",
  "payment_status": "succeeded",
  "amount": 420.0,
  "currency": "usd"
}
```

---

### POST /api/orders/{id}/refund/

**Refund Order**

**Request (Full Refund):**

```json
{
  "reason": "requested_by_customer"
}
```

**Request (Partial Refund):**

```json
{
  "amount": 100.0,
  "reason": "duplicate_purchase"
}
```

**Response:** `200 OK`

```json
{
  "success": true,
  "refund_id": "re_1234567890abcdef",
  "amount": 420.0,
  "currency": "usd",
  "status": "succeeded"
}
```

---

## 🔔 Webhooks

Base URL: `/api/webhooks/`

### POST /api/webhooks/stripe/

**Stripe Webhook Handler**

**Request Headers:**

```
Stripe-Signature: t=1234567890,v1=abc123...
Content-Type: application/json
```

**Request Body (payment_intent.succeeded):**

```json
{
  "id": "evt_1234567890",
  "object": "event",
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_1234567890abcdef",
      "object": "payment_intent",
      "amount": 42000,
      "currency": "usd",
      "status": "succeeded",
      "metadata": {
        "order_id": "4fa85f64-5717-4562-b3fc-2c963f66afc5",
        "order_number": "OE-20251119-0001"
      }
    }
  }
}
```

**Response:** `200 OK`

```json
{
  "received": true,
  "message": "Webhook processed successfully"
}
```

---

## 📊 Response Formats

### Pagination Response

All list endpoints return paginated responses:

```json
{
  "count": 156,
  "next": "http://localhost:8001/api/endpoint/?page=2",
  "previous": null,
  "results": [
    // Array of objects
  ]
}
```

### Success Response

Standard success response structure:

```json
{
  "message": "Operation successful",
  "data": {
    // Response data
  }
}
```

### Error Response

Standard error response structure:

```json
{
  "error": "Error message",
  "detail": "Detailed explanation of the error",
  "field_errors": {
    "field_name": ["Error message for this field"],
    "another_field": ["Another error message"]
  }
}
```

---

## ❌ Error Handling

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Resource deleted successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Common Error Examples

**Authentication Error:**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Validation Error:**

```json
{
  "email": ["This field is required."],
  "password": ["This field may not be blank."]
}
```

**Permission Error:**

```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Not Found Error:**

```json
{
  "detail": "Not found."
}
```

**Custom Error:**

```json
{
  "error": "Only 5 tickets available for 'VIP Pass'",
  "available_quantity": 5,
  "requested_quantity": 10
}
```

---

## 🔒 Authentication

### Using JWT Tokens

**Authorization Header:**

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Using HTTP-only Cookies

Cookies are automatically sent with requests after login:

- `access_token` - 5 minutes expiry
- `refresh_token` - 7 days expiry

### Rate Limiting

Rate limit headers in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1700000000
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- All monetary values are strings with 2 decimal places
- UUIDs are used for all resource IDs
- File uploads use multipart/form-data
- Dates use YYYY-MM-DD format
- Currency codes follow ISO 4217 (USD, EUR, GBP, etc.)

---

**Documentation Version:** 2.0  
**API Version:** 1.1  
**Last Updated:** November 19, 2025

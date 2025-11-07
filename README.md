# EasyTicket - Event Ticketing Platform

A comprehensive Django REST API for managing events, tickets, and orders with integrated Stripe payment processing.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [API Documentation](#api-documentation)
- [Docker Commands](#docker-commands)
- [Testing](#testing)
- [Deployment](#deployment)

## 🎯 Overview

EasyTicket is a full-featured event ticketing platform that enables organizers to create and manage events, sell tickets, and process payments securely. Consumers can browse events, purchase tickets, and receive QR-coded tickets via email.

## ✨ Features

### Authentication & Authorization

- ✅ Email-based registration with verification
- ✅ JWT-based authentication with refresh tokens
- ✅ Role-based access control (Consumer, Organizer, Admin)
- ✅ Password change and reset functionality
- ✅ Profile management

### Event Management

- ✅ Create, update, and delete events
- ✅ Event categories and filtering
- ✅ Multi-day event support
- ✅ Event images and descriptions
- ✅ Venue and location management
- ✅ Event status tracking (upcoming, ongoing, completed, cancelled)

### Ticket System

- ✅ Multiple ticket types (General Admission, VIP, Early Bird, etc.)
- ✅ Ticket tiers with different pricing
- ✅ Day passes for multi-day events
- ✅ Inventory management with concurrency protection
- ✅ QR code generation for tickets
- ✅ PDF ticket generation

### Order & Payment Processing

- ✅ Shopping cart functionality
- ✅ Stripe payment integration
- ✅ Payment intent creation
- ✅ Webhook-based order confirmation
- ✅ Automatic refund processing
- ✅ Service fee calculation
- ✅ Order history and tracking
- ✅ Email notifications (confirmation, cancellation)

### Security Features

- ✅ Webhook signature verification
- ✅ Idempotent webhook processing
- ✅ Row-level locking for inventory
- ✅ CORS protection
- ✅ Environment-based configuration
- ✅ Token blacklisting on logout

## 🛠 Tech Stack

**Backend Framework:**

- Django 5.2.7
- Django REST Framework 3.16.1

**Authentication:**

- djangorestframework-simplejwt 5.5.1
- JWT access & refresh tokens

**Database:**

- PostgreSQL 16
- psycopg2-binary 2.9.11

**Payment Processing:**

- Stripe 11.1.1
- Webhook integration

**Documentation:**

- drf-spectacular 0.27.2
- Swagger UI & ReDoc

**Additional Libraries:**

- Pillow 12.0.0 (Image processing)
- reportlab 4.0.7 (PDF generation)
- qrcode 7.4.2 (QR code generation)
- django-cors-headers 4.9.0
- django-filter 24.3
- python-decouple 3.8

**DevOps:**

- Docker & Docker Compose
- PostgreSQL (containerized or external)

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- PostgreSQL 16 (local or Docker)
- Python 3.12+ (for local development)
- Stripe account (for payment testing)

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd easyTicket
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your settings:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (use 'db' for Docker PostgreSQL, 'host.docker.internal' for local)
DB_NAME=easyTicket
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=host.docker.internal
DB_PORT=5432

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SERVICE_FEE_PERCENTAGE=5.0

# Email (Gmail SMTP)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Frontend
FRONTEND_URL=http://localhost:3000
```

### 3. Start with Docker

```bash
# Build and start the backend
docker compose up --build -d

# View logs
docker logs easyticket_backend -f

# Create test users (optional)
docker exec -it easyticket_backend python manage.py create_test_users
```

**Test Users Created:**

- **Organizer**: `admin_payment@test.com` / `AdminPass123!`
- **Consumer**: `customer_payment@test.com` / `CustomerPass123!`

### 4. Access the Application

- **API Base**: http://localhost:8000/api/
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Admin Panel**: http://localhost:8000/admin/

## 💻 Development Setup

### Local Development (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run development server
python manage.py runserver
```

### Project Structure

```
easyTicket/
├── Common/                 # Shared utilities
│   ├── email_utils.py     # Email sending functions
│   ├── models.py          # Base models
│   └── permissions.py     # Custom permissions
├── Events/                # Event management
│   ├── models.py          # Event, EventCategory models
│   ├── serializers.py     # Event serializers
│   ├── views.py           # Event ViewSets
│   └── urls.py            # Event routes
├── Orders/                # Order & Payment processing
│   ├── models.py          # Order, OrderItem, WebhookEvent
│   ├── serializers.py     # Order serializers
│   ├── views.py           # Order ViewSet
│   ├── webhooks.py        # Stripe webhook handlers
│   ├── urls.py            # Order routes
│   └── webhook_urls.py    # Webhook routes
├── Tickets/               # Ticket management
│   ├── models.py          # TicketType, TicketTier, DayPass, Ticket
│   ├── serializers.py     # Ticket serializers
│   ├── views.py           # Ticket ViewSets
│   └── urls.py            # Ticket routes
├── UserAuth/              # Authentication & Users
│   ├── models.py          # Custom User model
│   ├── serializers.py     # Auth serializers
│   ├── views.py           # Auth views
│   ├── urls.py            # Auth routes
│   └── management/
│       └── commands/
│           └── create_test_users.py
├── easyTicket/            # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   └── asgi.py/wsgi.py    # ASGI/WSGI config
├── static/                # Static files
├── media/                 # User uploads
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Container orchestration
├── entrypoint.sh          # Docker startup script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (git-ignored)
└── .env.example           # Environment template
```

## 📚 API Documentation

### Base URL

```
http://localhost:8000/api/
```

### Authentication Endpoints

| Method    | Endpoint                         | Description               | Auth Required |
| --------- | -------------------------------- | ------------------------- | ------------- |
| POST      | `/api/auth/signup/`              | Register new user         | No            |
| POST      | `/api/auth/verify-email/`        | Verify email address      | No            |
| POST      | `/api/auth/resend-verification/` | Resend verification email | No            |
| POST      | `/api/auth/login/`               | Login user                | No            |
| POST      | `/api/auth/logout/`              | Logout user               | Yes           |
| POST      | `/api/auth/token/refresh/`       | Refresh access token      | No            |
| GET       | `/api/auth/profile/`             | Get current user profile  | Yes           |
| PUT/PATCH | `/api/auth/profile/`             | Update user profile       | Yes           |
| POST      | `/api/auth/change-password/`     | Change password           | Yes           |

### Event Endpoints

| Method    | Endpoint                  | Description           | Auth Required | Role              |
| --------- | ------------------------- | --------------------- | ------------- | ----------------- |
| GET       | `/api/events/`            | List all events       | No            | -                 |
| POST      | `/api/events/`            | Create event          | Yes           | Organizer         |
| GET       | `/api/events/{id}/`       | Get event details     | No            | -                 |
| PUT/PATCH | `/api/events/{id}/`       | Update event          | Yes           | Organizer (owner) |
| DELETE    | `/api/events/{id}/`       | Delete event          | Yes           | Organizer (owner) |
| GET       | `/api/events/categories/` | List event categories | No            | -                 |
| POST      | `/api/events/categories/` | Create category       | Yes           | Admin             |

**Query Parameters:**

- `?category={id}` - Filter by category
- `?status={status}` - Filter by status (upcoming, ongoing, completed, cancelled)
- `?search={query}` - Search by name or description
- `?ordering={field}` - Order by field (e.g., `-start_date`)

### Ticket Endpoints

| Method    | Endpoint                   | Description             | Auth Required | Role              |
| --------- | -------------------------- | ----------------------- | ------------- | ----------------- |
| GET       | `/api/tickets/types/`      | List ticket types       | No            | -                 |
| POST      | `/api/tickets/types/`      | Create ticket type      | Yes           | Organizer         |
| GET       | `/api/tickets/types/{id}/` | Get ticket type details | No            | -                 |
| PUT/PATCH | `/api/tickets/types/{id}/` | Update ticket type      | Yes           | Organizer (owner) |
| DELETE    | `/api/tickets/types/{id}/` | Delete ticket type      | Yes           | Organizer (owner) |
| GET       | `/api/tickets/tiers/`      | List ticket tiers       | No            | -                 |
| POST      | `/api/tickets/tiers/`      | Create ticket tier      | Yes           | Organizer         |
| GET       | `/api/tickets/day-passes/` | List day passes         | No            | -                 |
| POST      | `/api/tickets/day-passes/` | Create day pass         | Yes           | Organizer         |
| GET       | `/api/tickets/my-tickets/` | Get user's tickets      | Yes           | Consumer          |

### Order Endpoints

| Method    | Endpoint            | Description        | Auth Required | Role             |
| --------- | ------------------- | ------------------ | ------------- | ---------------- |
| GET       | `/api/orders/`      | List user's orders | Yes           | Consumer         |
| POST      | `/api/orders/`      | Create order       | Yes           | Consumer         |
| GET       | `/api/orders/{id}/` | Get order details  | Yes           | Consumer (owner) |
| PUT/PATCH | `/api/orders/{id}/` | Update order       | Yes           | Consumer (owner) |
| DELETE    | `/api/orders/{id}/` | Cancel order       | Yes           | Consumer (owner) |

**Custom Order Actions:**

| Method | Endpoint                                  | Description                  | Auth Required |
| ------ | ----------------------------------------- | ---------------------------- | ------------- |
| POST   | `/api/orders/{id}/create-payment-intent/` | Create Stripe payment intent | Yes           |
| GET    | `/api/orders/{id}/payment-status/`        | Check payment status         | Yes           |
| POST   | `/api/orders/{id}/refund/`                | Process refund               | Yes           |
| POST   | `/api/orders/{id}/confirm-payment/`       | ⚠️ DEPRECATED - Use webhooks | Yes           |

**Order Filtering:**

- GET `/api/orders/pending/` - Pending orders
- GET `/api/orders/processing/` - Processing orders
- GET `/api/orders/confirmed/` - Confirmed orders
- GET `/api/orders/cancelled/` - Cancelled orders

### Webhook Endpoints

| Method | Endpoint                | Description             | Auth Required           |
| ------ | ----------------------- | ----------------------- | ----------------------- |
| POST   | `/api/webhooks/stripe/` | Stripe webhook receiver | No (Signature verified) |

**Webhook Events Handled:**

- `payment_intent.succeeded` - Confirms order, sends ticket email
- `payment_intent.payment_failed` - Marks order as failed
- `payment_intent.canceled` - Cancels processing orders
- `charge.refunded` - Updates order to refunded status

## 🔐 Authentication Flow

### 1. User Registration

```bash
POST /api/auth/signup/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "consumer",
  "phone_number": "+1234567890"
}
```

### 2. Email Verification

```bash
POST /api/auth/verify-email/
Content-Type: application/json

{
  "token": "verification-token-from-email"
}
```

### 3. Login

```bash
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "user_type": "consumer",
    ...
  }
}
```

### 4. Authenticated Requests

```bash
GET /api/auth/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 5. Token Refresh

```bash
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 💳 Payment Flow

### 1. Create Order

```bash
POST /api/orders/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "items": [
    {
      "ticket_type": "uuid",
      "quantity": 2
    },
    {
      "ticket_tier": "uuid",
      "quantity": 1
    }
  ]
}

# Response:
{
  "id": "order-uuid",
  "order_number": "ORD-20231105-ABCD",
  "status": "pending",
  "subtotal": "150.00",
  "service_fee": "7.50",
  "total": "157.50",
  "items": [...]
}
```

### 2. Create Payment Intent

```bash
POST /api/orders/{order_id}/create-payment-intent/
Authorization: Bearer {access_token}

# Response:
{
  "client_secret": "pi_xxx_secret_yyy",
  "payment_intent_id": "pi_xxx",
  "amount": 15750,
  "currency": "usd"
}
```

### 3. Process Payment (Frontend)

```javascript
// Using Stripe.js in your frontend
const stripe = Stripe("pk_test_...");
const { error } = await stripe.confirmCardPayment(client_secret, {
  payment_method: {
    card: cardElement,
    billing_details: {
      name: "Customer Name",
      email: "customer@example.com",
    },
  },
});
```

### 4. Webhook Confirmation (Automatic)

When payment succeeds, Stripe sends a webhook to `/api/webhooks/stripe/`:

- ✅ Webhook signature verified
- ✅ Order status updated to "confirmed"
- ✅ Inventory decremented
- ✅ Tickets generated with QR codes
- ✅ Confirmation email sent
- ✅ Idempotency check prevents duplicate processing

### 5. Check Payment Status

```bash
GET /api/orders/{order_id}/payment-status/
Authorization: Bearer {access_token}

# Response:
{
  "order_id": "uuid",
  "status": "confirmed",
  "payment_status": "succeeded",
  "stripe_payment_id": "pi_xxx"
}
```

### 6. Request Refund

```bash
POST /api/orders/{order_id}/refund/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "reason": "Customer requested cancellation"
}

# Response:
{
  "message": "Refund processed successfully",
  "refund_id": "re_xxx",
  "amount": "157.50",
  "status": "succeeded"
}
```

## 🐳 Docker Commands

### Container Management

```bash
# Build and start
docker compose up --build -d

# Start without rebuilding
docker compose up -d

# Stop containers
docker compose down

# Stop and remove volumes
docker compose down -v

# Restart backend
docker compose restart backend

# View logs
docker logs easyticket_backend -f
docker logs easyticket_backend --tail 100

# Check container status
docker compose ps
```

### Django Management Commands

```bash
# Run migrations
docker exec -it easyticket_backend python manage.py migrate

# Create superuser
docker exec -it easyticket_backend python manage.py createsuperuser

# Create test users
docker exec -it easyticket_backend python manage.py create_test_users

# Collect static files
docker exec -it easyticket_backend python manage.py collectstatic --noinput

# Django shell
docker exec -it easyticket_backend python manage.py shell

# Access container bash
docker exec -it easyticket_backend bash
```

### Database Commands (if using Docker PostgreSQL)

```bash
# Access PostgreSQL
docker exec -it easyticket_db psql -U postgres -d easyTicket

# Backup database
docker exec easyticket_db pg_dump -U postgres easyTicket > backup.sql

# Restore database
cat backup.sql | docker exec -i easyticket_db psql -U postgres -d easyTicket
```

### Cleanup

```bash
# Remove containers and networks
docker compose down

# Remove containers, networks, and volumes
docker compose down -v

# Remove all unused Docker resources
docker system prune -a

# Remove specific image
docker rmi easyticket-backend
```

## 🧪 Testing

### Setting Up Stripe Webhooks for Local Testing

1. **Install Stripe CLI**

   ```bash
   # Download from: https://stripe.com/docs/stripe-cli
   ```

2. **Login to Stripe**

   ```bash
   stripe login
   ```

3. **Forward Webhooks to Local Server**

   ```bash
   stripe listen --forward-to localhost:8000/api/webhooks/stripe/

   # Copy the webhook signing secret (whsec_...)
   # Add to .env:
   STRIPE_WEBHOOK_SECRET=whsec_xxx
   ```

4. **Restart Docker Container**

   ```bash
   docker compose restart backend
   ```

5. **Trigger Test Events**
   ```bash
   stripe trigger payment_intent.succeeded
   stripe trigger payment_intent.payment_failed
   ```

### Manual Testing Workflow

1. **Create Test Users**

   ```bash
   docker exec -it easyticket_backend python manage.py create_test_users
   ```

2. **Login as Organizer** (`admin_payment@test.com`)

   - Create event via API
   - Create ticket types and tiers
   - Set pricing and inventory

3. **Login as Consumer** (`customer_payment@test.com`)
   - Browse events
   - Create order with tickets
   - Create payment intent
   - Use Stripe test card: `4242 4242 4242 4242`
   - Verify webhook confirmation
   - Check email for ticket

### Stripe Test Cards

```
Success: 4242 4242 4242 4242 (any CVC, future date)
Decline: 4000 0000 0000 0002
Insufficient Funds: 4000 0000 0000 9995
3D Secure: 4000 0027 6000 3184
```

### Running Unit Tests (When Available)

```bash
# Run all tests
docker exec -it easyticket_backend python manage.py test

# Run specific app tests
docker exec -it easyticket_backend python manage.py test Orders

# Run with coverage
docker exec -it easyticket_backend coverage run manage.py test
docker exec -it easyticket_backend coverage report
```

## 🔒 Security Best Practices

### Environment Variables

- ✅ Never commit `.env` file to version control
- ✅ Use strong `SECRET_KEY` (generate with `django-admin startproject`)
- ✅ Rotate secrets regularly
- ✅ Use different keys for dev/staging/production

### Stripe Security

- ✅ Always verify webhook signatures
- ✅ Use Stripe test keys in development
- ✅ Keep secret keys server-side only
- ✅ Log all payment transactions
- ✅ Implement idempotency for webhooks

### Database Security

- ✅ Use strong database passwords
- ✅ Enable SSL for database connections in production
- ✅ Regular database backups
- ✅ Restrict database access by IP

### API Security

- ✅ JWT token expiration (15 min access, 1 day refresh)
- ✅ Token blacklisting on logout
- ✅ Rate limiting (configure in production)
- ✅ CORS whitelist only trusted domains
- ✅ HTTPS only in production

### Code Security

- ✅ Row-level locking for inventory (prevents race conditions)
- ✅ Input validation on all endpoints
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection (Django templates)
- ✅ CSRF protection (Django middleware)

## 📊 Database Models Overview

### User Model

```python
User (AbstractBaseUser, PermissionsMixin)
├── email (unique, primary key)
├── user_type: consumer | organizer | admin
├── auth_provider: email | google | facebook
├── is_email_verified
├── phone_number
└── profile fields (first_name, last_name, bio, avatar)
```

### Event Model

```python
Event
├── organizer (FK: User)
├── category (FK: EventCategory)
├── name, description
├── venue, address, city, country
├── start_date, end_date
├── status: upcoming | ongoing | completed | cancelled
├── banner_image
├── max_attendees
└── timestamps
```

### Ticket Models

```python
TicketType
├── event (FK: Event)
├── name, description
├── base_price
├── total_quantity, available_quantity
├── sale_start_date, sale_end_date
├── max_per_order
└── is_active

TicketTier (inherits TicketType)
├── tier_level (1-5)
└── Additional pricing tiers

DayPass (inherits TicketType)
├── valid_date
└── Day-specific access

Ticket
├── order_item (FK: OrderItem)
├── ticket_type (FK: TicketType)
├── qr_code
├── is_checked_in
└── check_in_time
```

### Order Models

```python
Order
├── customer (FK: User)
├── order_number (auto-generated)
├── status: pending | processing | confirmed | failed | cancelled | refunded
├── subtotal, service_fee, total
├── payment_id (Stripe Payment Intent ID)
├── expires_at (15 min from creation)
└── timestamps

OrderItem
├── order (FK: Order)
├── ticket_type | ticket_tier | day_pass (polymorphic)
├── quantity
├── unit_price
└── total_price

WebhookEvent (for idempotency)
├── event_id (unique, from Stripe)
├── event_type
├── processed_at
└── payload (JSON)
```

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with domain
- [ ] Use production database (managed PostgreSQL)
- [ ] Set strong `SECRET_KEY`
- [ ] Configure production Stripe keys
- [ ] Set up `STRIPE_WEBHOOK_SECRET` from Stripe dashboard
- [ ] Configure email backend (SendGrid, AWS SES, etc.)
- [ ] Set up static files serving (AWS S3, Cloudinary)
- [ ] Configure media files storage (S3)
- [ ] Enable HTTPS (SSL certificate)
- [ ] Set up CDN for static assets
- [ ] Configure CORS for frontend domain
- [ ] Set up monitoring (Sentry, New Relic)
- [ ] Configure logging
- [ ] Set up automated backups
- [ ] Enable rate limiting
- [ ] Configure caching (Redis)
- [ ] Set up CI/CD pipeline
- [ ] Use production WSGI server (Gunicorn, uWSGI)
- [ ] Set up reverse proxy (Nginx)

### Environment Variables for Production

```env
# Django
SECRET_KEY=<strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Database (Managed PostgreSQL)
DB_NAME=easyticket_prod
DB_USER=easyticket_user
DB_PASSWORD=<strong-password>
DB_HOST=your-db-host.com
DB_PORT=5432

# Stripe (Production Keys)
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SERVICE_FEE_PERCENTAGE=5.0

# Email (Production SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid-api-key>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Frontend
FRONTEND_URL=https://yourdomain.com

# Static/Media Files
AWS_ACCESS_KEY_ID=<aws-key>
AWS_SECRET_ACCESS_KEY=<aws-secret>
AWS_STORAGE_BUCKET_NAME=easyticket-assets
AWS_S3_REGION_NAME=us-east-1
```

### Docker Production Setup

Update `docker-compose.yml` for production:

```yaml
services:
  backend:
    build: .
    container_name: easyticket_backend
    command: gunicorn easyTicket.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    env_file:
      - .env.production
    ports:
      - "8000:8000"
    restart: always
    networks:
      - easyticket_network

  nginx:
    image: nginx:alpine
    container_name: easyticket_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/static
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: always
    networks:
      - easyticket_network

networks:
  easyticket_network:
    driver: bridge

volumes:
  static_volume:
  media_volume:
```

### Deployment Platforms

**Recommended Platforms:**

- AWS (EC2, RDS, S3, CloudFront)
- DigitalOcean (Droplets, Managed Databases)
- Heroku (Easy deployment)
- Railway (Modern PaaS)
- Render (Automatic deployments)

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use Django naming conventions
- Write descriptive docstrings
- Keep functions focused and small
- Use type hints where applicable

### Git Workflow

```bash
# Feature development
git checkout -b feature/payment-integration
git add .
git commit -m "feat: add Stripe payment integration"
git push origin feature/payment-integration

# Create Pull Request for review
```

### Commit Message Convention

```
feat: add new feature
fix: bug fix
docs: documentation update
style: code formatting
refactor: code restructuring
test: add tests
chore: maintenance tasks
```

### API Development Best Practices

1. **Versioning**: Use `/api/v1/` for future API versions
2. **Pagination**: Implement for all list endpoints
3. **Filtering**: Use django-filter for complex queries
4. **Serialization**: Keep serializers clean and focused
5. **Validation**: Validate at serializer level
6. **Error Handling**: Return meaningful error messages
7. **Documentation**: Keep Swagger/ReDoc updated

### Database Best Practices

1. **Migrations**: Always create migrations for model changes
2. **Indexes**: Add indexes for frequently queried fields
3. **Foreign Keys**: Use `on_delete` appropriately
4. **Transactions**: Use atomic transactions for critical operations
5. **Signals**: Use sparingly, prefer explicit calls
6. **Queries**: Use `select_related` and `prefetch_related` to avoid N+1

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 👥 Team

**Developer**: Abu Ahamed Rafi  
**Email**: abuahamedrafi@gmail.com

## 📞 Support

For issues and questions:

- Create an issue in the repository
- Contact: abuahamedrafi@gmail.com

## 🔗 Useful Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [Stripe Testing](https://stripe.com/docs/testing)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

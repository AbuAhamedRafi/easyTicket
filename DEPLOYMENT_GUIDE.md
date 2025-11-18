# Production Deployment Guide - EasyTicket

This guide covers deploying the EasyTicket application to production with all security features enabled.

## Prerequisites

- Production server (Linux recommended: Ubuntu 20.04/22.04)
- PostgreSQL database
- Domain name with SSL certificate
- Stripe account (production mode)
- Email service (AWS SES, SendGrid, etc.)

---

## 1. Server Setup

### 1.1 Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3-pip postgresql-client nginx -y

# Install Docker and Docker Compose (if using containers)
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker
```

### 1.2 Create Application User

```bash
sudo useradd -m -s /bin/bash easyticket
sudo usermod -aG docker easyticket  # If using Docker
```

---

## 2. Application Deployment

### 2.1 Clone Repository

```bash
# Switch to application user
sudo su - easyticket

# Clone your repository
git clone https://github.com/yourusername/easyticket.git
cd easyticket

# Checkout production branch
git checkout main  # or your production branch
```

### 2.2 Configure Environment

```bash
# Copy production environment template
cp .env.production.example .env.production

# Edit with your production values
nano .env.production
```

**CRITICAL: Update these values:**

- `SECRET_KEY` - Generate new: `python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- `DEBUG=False`
- `ALLOWED_HOSTS` - Your domain(s)
- Database credentials
- Stripe LIVE keys
- Email configuration

### 2.3 Build and Start

**Option A: Docker Deployment (Recommended)**

```bash
# Build containers
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

**Option B: Traditional Deployment**

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn easyTicket.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 3. Nginx Configuration

### 3.1 Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/easyticket
```

```nginx
upstream easyticket_app {
    server 127.0.0.1:8000;  # Or your Docker container IP
}

server {
    listen 80;
    server_name yourapp.com www.yourapp.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourapp.com www.yourapp.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourapp.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client upload limit
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /home/easyticket/easyticket/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/easyticket/easyticket/media/;
        expires 7d;
    }

    # API endpoints
    location / {
        proxy_pass http://easyticket_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting for auth endpoints
    location ~ ^/api/auth/(login|signup)/ {
        limit_req zone=auth burst=5 nodelay;
        proxy_pass http://easyticket_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3.2 Add Rate Limiting Zones

Edit `/etc/nginx/nginx.conf` and add inside `http` block:

```nginx
http {
    # ... existing config ...

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

    # ... rest of config ...
}
```

### 3.3 Enable Site

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/easyticket /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## 4. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourapp.com -d www.yourapp.com

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## 5. Systemd Service (Non-Docker)

### 5.1 Create Service File

```bash
sudo nano /etc/systemd/system/easyticket.service
```

```ini
[Unit]
Description=EasyTicket Gunicorn Application
After=network.target

[Service]
User=easyticket
Group=easyticket
WorkingDirectory=/home/easyticket/easyticket
Environment="PATH=/home/easyticket/easyticket/venv/bin"
EnvironmentFile=/home/easyticket/easyticket/.env.production
ExecStart=/home/easyticket/easyticket/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --timeout 60 \
    --access-logfile /home/easyticket/easyticket/logs/access.log \
    --error-logfile /home/easyticket/easyticket/logs/error.log \
    easyTicket.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.2 Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable easyticket
sudo systemctl start easyticket
sudo systemctl status easyticket
```

---

## 6. Cron Jobs for Management Commands

```bash
# Edit crontab for easyticket user
crontab -e
```

Add these lines:

```bash
# Cleanup expired email verification tokens (daily at 2 AM)
0 2 * * * cd /home/easyticket/easyticket && /home/easyticket/easyticket/venv/bin/python manage.py cleanup_tokens >> /home/easyticket/easyticket/logs/cron.log 2>&1

# Cancel expired orders (every 5 minutes)
*/5 * * * * cd /home/easyticket/easyticket && /home/easyticket/easyticket/venv/bin/python manage.py cancel_expired_orders >> /home/easyticket/easyticket/logs/cron.log 2>&1
```

**For Docker:**

```bash
# Cleanup tokens
0 2 * * * cd /home/easyticket/easyticket && docker-compose exec -T web python manage.py cleanup_tokens >> /home/easyticket/easyticket/logs/cron.log 2>&1

# Cancel expired orders
*/5 * * * * cd /home/easyticket/easyticket && docker-compose exec -T web python manage.py cancel_expired_orders >> /home/easyticket/easyticket/logs/cron.log 2>&1
```

---

## 7. Stripe Webhook Configuration

### 7.1 Create Production Webhook

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter: `https://yourapp.com/api/orders/webhook/stripe/`
4. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
   - `charge.refunded`
5. Copy the webhook signing secret
6. Add to `.env.production`: `STRIPE_WEBHOOK_SECRET=whsec_...`

### 7.2 Test Webhook

```bash
# Use Stripe CLI to test
stripe listen --forward-to https://yourapp.com/api/orders/webhook/stripe/
stripe trigger payment_intent.succeeded
```

---

## 8. Database Backup

### 8.1 Create Backup Script

```bash
nano /home/easyticket/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/easyticket/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="easyticket_production"
DB_USER="postgres_prod_user"

mkdir -p $BACKUP_DIR

# Backup database
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /home/easyticket/easyticket/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x /home/easyticket/backup.sh
```

### 8.2 Schedule Daily Backup

```bash
crontab -e
```

Add:

```bash
# Daily database backup at 3 AM
0 3 * * * /home/easyticket/backup.sh >> /home/easyticket/easyticket/logs/backup.log 2>&1
```

---

## 9. Monitoring Setup

### 9.1 Install Sentry (Optional)

```bash
pip install sentry-sdk
```

Update `settings.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=config("SENTRY_DSN", default=""),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False
    )
```

### 9.2 Log Monitoring

```bash
# View application logs
tail -f /home/easyticket/easyticket/logs/django.log

# View payment logs
tail -f /home/easyticket/easyticket/logs/payments.log

# View security logs
tail -f /home/easyticket/easyticket/logs/security.log
```

---

## 10. Post-Deployment Verification

### 10.1 Security Checks

```bash
# Run Django deployment checks
python manage.py check --deploy

# Test HTTPS redirect
curl -I http://yourapp.com  # Should redirect to HTTPS

# Verify security headers
curl -I https://yourapp.com
```

### 10.2 Functional Tests

- [ ] User registration with email verification
- [ ] User login with correct credentials
- [ ] Failed login attempts (should be rate-limited after 5 tries)
- [ ] Create an event as organizer
- [ ] Purchase tickets as consumer
- [ ] Payment processing end-to-end
- [ ] Webhook delivery and order confirmation
- [ ] Email notifications received
- [ ] Refund processing
- [ ] Admin panel access

### 10.3 Performance Tests

```bash
# Test response times
time curl https://yourapp.com/api/events/

# Load test (install Apache Bench)
ab -n 1000 -c 10 https://yourapp.com/api/events/
```

---

## 11. Maintenance

### 11.1 Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild containers (Docker)
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Or restart service (non-Docker)
sudo systemctl restart easyticket
```

### 11.2 Database Migrations

```bash
# Backup database first!
./backup.sh

# Run migrations
docker-compose exec web python manage.py migrate

# Or non-Docker
python manage.py migrate
```

### 11.3 View Logs

```bash
# Application logs
docker-compose logs -f web

# Or systemd logs
sudo journalctl -u easyticket -f
```

---

## 12. Troubleshooting

### Issue: 502 Bad Gateway

```bash
# Check if application is running
sudo systemctl status easyticket  # non-Docker
docker-compose ps  # Docker

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

### Issue: Static files not loading

```bash
# Collect static files again
python manage.py collectstatic --noinput

# Check Nginx static file location
ls -la /home/easyticket/easyticket/staticfiles/
```

### Issue: Webhooks not working

```bash
# Check webhook logs
tail -f logs/payments.log

# Verify webhook secret in Stripe dashboard
# Test webhook delivery in Stripe dashboard
```

---

## 13. Rollback Plan

```bash
# Stop application
docker-compose down  # Docker
sudo systemctl stop easyticket  # non-Docker

# Restore database backup
psql -h $DB_HOST -U $DB_USER $DB_NAME < /home/easyticket/backups/db_backup_YYYYMMDD_HHMMSS.sql

# Checkout previous version
git checkout previous-stable-tag

# Rebuild and restart
docker-compose up -d --build  # Docker
sudo systemctl start easyticket  # non-Docker
```

---

## Support

For issues or questions:

- Check logs in `/home/easyticket/easyticket/logs/`
- Review `SECURITY_AUDIT.md` for security best practices
- Consult `SECURITY_IMPLEMENTATION.md` for feature details

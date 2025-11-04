# Docker Commands for EasyTicket

This folder contains all Docker-related files for the EasyTicket project.

## Quick Start

From the **docker directory** (`cd docker`), run:

```bash
# Build and start the containers
docker-compose up --build -d

# View logs
docker logs easyticket_web -f

# Stop containers
docker-compose down
```

## File Structure

```
easyTicket/
├── docker/                    # All Docker files here
│   ├── .env                   # Environment variables
│   ├── .env.example          # Environment template
│   ├── Dockerfile            # Docker image definition
│   ├── docker-compose.yml    # Container orchestration
│   ├── entrypoint.sh         # Startup script
│   └── README.md             # This file
├── .dockerignore             # Files to exclude from build (in root)
├── manage.py
├── requirements.txt
└── [other project files...]
```

## Available Commands

**Important:** All docker-compose commands must be run from the `docker/` directory.

### Build & Run

```bash
# Navigate to docker directory first
cd docker

# Build and start in detached mode
docker-compose up --build -d

# Start without rebuilding
docker-compose up -d

# Build only (no start)
docker-compose build
```

### Container Management

```bash
# Stop containers
docker-compose down

# Restart containers
docker-compose restart

# View logs
docker logs easyticket_web -f
docker logs easyticket_web --tail 100
```

### Django Commands

```bash
# Run migrations
docker exec -it easyticket_web python manage.py migrate

# Create superuser
docker exec -it easyticket_web python manage.py createsuperuser

# Create test users for payment testing
docker exec -it easyticket_web python manage.py create_test_users

# Collect static files
docker exec -it easyticket_web python manage.py collectstatic --noinput

# Django shell
docker exec -it easyticket_web python manage.py shell

# Access container bash
docker exec -it easyticket_web bash
```

### Database Commands

```bash
# Access PostgreSQL (if using Docker PostgreSQL)
docker exec -it easyticket_db psql -U postgres -d easyticket_db

# Backup database
docker exec easyticket_db pg_dump -U postgres easyticket_db > backup.sql

# Restore database
cat backup.sql | docker exec -i easyticket_db psql -U postgres -d easyticket_db
```

### Cleanup

```bash
# Remove containers and networks
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove all unused Docker resources
docker system prune -a
```

## What Happens on Build

The `entrypoint.sh` script automatically:

1. **Waits for database connection** (30 retries, 2 seconds each)
2. **Runs migrations** (`makemigrations` and `migrate`)
3. **Collects static files**
4. **Starts the Django development server**

## Environment Variables

## Environment Variables

Make sure `.env` file exists in the **docker/** directory with:

```env
# Required
DB_NAME=easyTicket
DB_USER=postgres
DB_PASSWORD=12345
DB_HOST=host.docker.internal
DB_PORT=5432

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SERVICE_FEE_PERCENTAGE=5.0

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## File Structure

```
easyTicket/
├── docker/                 # Docker documentation
│   └── README.md          # This file
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Container orchestration
├── entrypoint.sh          # Startup script (auto-migrations)
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (not in git)
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs easyticket_web

# Check if port 8000 is already in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux
```

### Database connection errors

- Make sure PostgreSQL is running locally
- Check `DB_HOST=host.docker.internal` in `.env`
- Verify database credentials

### Permission errors

```bash
# Fix permissions (Linux/Mac)
sudo chown -R $USER:$USER .
```

### Clean rebuild

```bash
# Complete cleanup and rebuild
docker-compose down -v
docker system prune -a
docker-compose up --build -d
```

## Development Workflow

**Note:** Always work from the `docker/` directory for Docker commands.

1. **Make code changes** - Files are volume-mounted, changes reflect immediately
2. **If models changed** - Run migrations:
   ```bash
   docker exec -it easyticket_web python manage.py makemigrations
   docker exec -it easyticket_web python manage.py migrate
   ```
3. **If requirements changed** - Rebuild:
   ```bash
   cd docker
   docker-compose up --build -d
   ```
4. **View changes** - No restart needed for code changes (Django auto-reloads)

## Production Deployment

For production, update:

1. `DEBUG=False` in `.env`
2. Set strong `SECRET_KEY`
3. Use production database (not host.docker.internal)
4. Use proper WSGI server (gunicorn/uwsgi)
5. Add nginx for static files
6. Use production Stripe keys
7. Set up proper email backend (not Gmail SMTP)

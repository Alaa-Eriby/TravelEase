# TravelEase – Deployment & Production Operations Guide

### 1. Docker & Docker Compose Deployment (Recommended)
TravelEase includes a complete multi-container Docker configuration:
- `db`: PostgreSQL 15 Alpine with persistent storage volume and health check.
- `web`: Python 3.10 slim running Gunicorn / Django application with auto-migration and demo data seeding on startup.

#### Quick Launch with Docker:
```bash
# 1. Clone repository
git clone https://github.com/your-username/travelease.git
cd travelease

# 2. Launch multi-container environment
docker-compose up --build -d

# 3. Check health and view logs
docker-compose ps
docker-compose logs -f web
```
The application will be live at `http://localhost:8000/`.

---

### 2. Manual Bare-Metal / Local Production Deployment

#### Step 1: Environment Setup
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

#### Step 2: Database Setup (PostgreSQL)
Configure your `.env` file:
```ini
DEBUG=False
SECRET_KEY=generate-a-strong-random-secret-key-here
ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1
DB_ENGINE=postgresql
POSTGRES_DB=travelease_db
POSTGRES_USER=travelease_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

#### Step 3: Run Database Migrations & Static Assets
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_data
```

#### Step 4: Web Server Configuration (Nginx + Gunicorn)
Sample Gunicorn systemd service:
```ini
[Unit]
Description=Gunicorn daemon for TravelEase
After=network.target

[Service]
User=travelease
Group=www-data
WorkingDirectory=/var/www/travelease
ExecStart=/var/www/travelease/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          travelease.wsgi:application

[Install]
WantedBy=multi-user.target
```
Sample Nginx server block:
```nginx
server {
    server_name travelease.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/travelease;
    }
    location /media/ {
        root /var/www/travelease;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

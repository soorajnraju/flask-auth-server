# 🐳 Docker Deployment Guide - Enterprise Flask Authorization Server

This guide provides comprehensive instructions for deploying the Enterprise Flask Authorization Server using Docker and Docker Compose.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- 5GB free disk space

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repository>
cd flask-example

# Copy environment configuration
cp .env.docker .env

# Edit environment variables (IMPORTANT!)
nano .env
```

### 2. Start with Docker Compose

```bash
# Start all services (app, database, redis)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 3. Initialize Database

The database is automatically initialized on first run, but you can manually trigger it:

```bash
# Initialize database with default admin user
docker-compose exec app python init_db.py
```

### 4. Test the Deployment

```bash
# Health check
curl http://localhost:5001/health

# Login with default admin
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "Admin123!"}'
```

## 📊 Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Nginx Proxy   │────│  Flask App      │────│   PostgreSQL    │
│   (Optional)    │    │  (Port 5001)    │    │   (Port 5432)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              │
                       ┌─────────────────┐
                       │                 │
                       │     Redis       │
                       │   (Port 6379)   │
                       │                 │
                       └─────────────────┘
```

## 🔧 Configuration Profiles

### Development Profile

```bash
# Start with development tools (includes Adminer for database management)
docker-compose --profile development up -d

# Access Adminer at http://localhost:8080
# Server: db, Username: flask_user, Password: (from .env), Database: flask_auth
```

### Production Profile

```bash
# Start with Nginx reverse proxy
docker-compose --profile production up -d

# Access via Nginx at http://localhost
```

## 🔐 Security Configuration

### 1. Update Default Passwords

Edit `.env` file and change these critical values:

```bash
# Database
POSTGRES_PASSWORD=your_secure_database_password

# Redis
REDIS_PASSWORD=your_secure_redis_password

# JWT Secrets (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your_super_secure_flask_secret_key
JWT_SECRET_KEY=your_super_secure_jwt_secret_key
```

### 2. Generate Secure Secrets

```bash
# Generate secure random secrets
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### 3. Configure CORS

Update `CORS_ORIGINS` in `.env` to include only your trusted domains:

```bash
CORS_ORIGINS=https://yourapp.com,https://admin.yourapp.com
```

## 📦 Individual Service Management

### Flask Application

```bash
# Build the Flask app image
docker build -t flask-auth-server .

# Run standalone (requires external database)
docker run -p 5001:5001 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  flask-auth-server
```

### PostgreSQL Database

```bash
# Run PostgreSQL separately
docker run -d \
  --name flask-auth-postgres \
  -e POSTGRES_DB=flask_auth \
  -e POSTGRES_USER=flask_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine
```

### Redis Cache

```bash
# Run Redis separately
docker run -d \
  --name flask-auth-redis \
  -p 6379:6379 \
  redis:7-alpine \
  redis-server --requirepass your_redis_password
```

## 🔍 Monitoring and Debugging

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f redis
```

### Execute Commands in Containers

```bash
# Access Flask app shell
docker-compose exec app bash

# Run database commands
docker-compose exec app python -c "from app.models import db; print(db)"

# Access PostgreSQL
docker-compose exec db psql -U flask_user -d flask_auth
```

### Health Checks

```bash
# Service health status
docker-compose ps

# Manual health checks
curl http://localhost:5001/health
docker-compose exec db pg_isready -U flask_user
docker-compose exec redis redis-cli ping
```

## 🏭 Production Deployment

### 1. Environment Preparation

```bash
# Create production environment file
cp .env.docker .env.production

# Update for production
FLASK_ENV=production
FLASK_DEBUG=False
BCRYPT_LOG_ROUNDS=13
```

### 2. SSL/TLS Configuration

```bash
# Create SSL directory
mkdir -p docker/ssl

# Copy your SSL certificates
cp your_cert.pem docker/ssl/cert.pem
cp your_private.key docker/ssl/private.key

# Update Nginx configuration in docker/nginx/conf.d/flask-auth.conf
```

### 3. Production Deployment

```bash
# Deploy with production profile
docker-compose --profile production --env-file .env.production up -d

# Verify deployment
curl -k https://localhost/health
```

### 4. Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 🔄 Data Management

### Database Backups

```bash
# Create backup
docker-compose exec db pg_dump -U flask_user flask_auth > backup.sql

# Restore backup
docker-compose exec -T db psql -U flask_user flask_auth < backup.sql
```

### Data Volumes

```bash
# List Docker volumes
docker volume ls

# Backup volume data
docker run --rm -v flask-example_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volume data
docker run --rm -v flask-example_postgres_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## 🚀 Scaling and Load Balancing

### Scale Application Instances

```bash
# Scale Flask app to 3 instances
docker-compose up -d --scale app=3

# Update Nginx upstream configuration accordingly
```

### External Load Balancer Integration

For cloud deployment, integrate with:
- AWS Application Load Balancer
- Google Cloud Load Balancer
- Azure Load Balancer
- Kubernetes Ingress

## 🧪 Testing Docker Deployment

```bash
# Run comprehensive tests
bash scripts/test_docker_deployment.sh

# Load testing
docker run --rm -it --network host \
  loadimpact/k6 run - <<EOF
import http from 'k6/http';
export default function() {
  http.get('http://localhost:5001/health');
}
EOF
```

## ❗ Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database status
   docker-compose logs db
   
   # Verify network connectivity
   docker-compose exec app nc -z db 5432
   ```

2. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :5001
   
   # Change port in .env
   APP_PORT=5002
   ```

3. **Permission Denied**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   chmod +x docker-entrypoint.sh
   ```

4. **Out of Memory**
   ```bash
   # Check resource usage
   docker stats
   
   # Increase available memory or add resource limits
   ```

### Getting Help

```bash
# Service status
docker-compose ps

# Detailed container information
docker-compose exec app env

# System resource usage
docker system df
docker system events
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Redis Docker Hub](https://hub.docker.com/_/redis)
- [Nginx Docker Hub](https://hub.docker.com/_/nginx)

---

🎉 **Your Enterprise Flask Authorization Server is now ready for Docker deployment!**
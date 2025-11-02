# Enterprise Authorization Server - Complete Documentation

## 📋 Table of Contents
1. [Quick Start Guide](#quick-start-guide)
2. [Project Overview](#project-overview)
3. [API Reference](#api-reference)
4. [Security Features](#security-features)
5. [Integration Guide](#integration-guide)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ (running on localhost:5432)
- Virtual environment activated

### 1. Database Setup
Ensure PostgreSQL is running with these credentials:
```bash
Username: postgres
Password: postgres
Database: flask
Host: localhost
Port: 5432
```

### 2. Install Dependencies
```bash
# Activate virtual environment
source .venv/bin/activate

# Dependencies are already installed in your project
```

### 3. Initialize Database
```bash
python init_db.py
```
**Output:** Creates 30 permissions, 4 roles, and 1 admin user

### 4. Start Server
```bash
# Recommended: Simplified server (no Redis dependency)
python simple_main.py

# Alternative: Full server (requires Redis)
python main.py
```

### 5. Test Installation
```bash
# In a new terminal
python test_working_server.py
```

### 6. Access Endpoints
- **Health Check:** http://127.0.0.1:5001/health
- **API Info:** http://127.0.0.1:5001/api/v1/info
- **Admin Login:** admin@example.com / Admin123!

---

## 🏗️ Project Overview

### Architecture
This is a **microservices-ready authorization server** built with Flask, providing centralized authentication and authorization for distributed systems.

### Core Components
```
app/
├── controllers/        # REST API endpoints
├── models/            # Database models (SQLAlchemy)
├── middleware/        # Authentication & authorization decorators
├── services/          # Business logic layer
└── schemas/          # Input validation (Marshmallow)
```

### Key Features
- ✅ **JWT Authentication** with access/refresh tokens
- ✅ **RBAC System** with fine-grained permissions
- ✅ **User Management** (registration, profiles, password changes)
- ✅ **Token Security** (blacklisting, expiration, validation)
- ✅ **API Versioning** (/api/v1/)
- ✅ **CORS Support** for web applications
- ✅ **Rate Limiting** (optional, with Redis)
- ✅ **Input Validation** and error handling
- ✅ **Production Ready** (Gunicorn, Docker, environment configs)

---

## 📡 API Reference

### Base URL
```
http://127.0.0.1:5001/api/v1
```

### Authentication Flow

#### 1. User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "user@company.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201):**
```json
{
    "success": true,
    "user": {
        "id": 2,
        "email": "user@company.com",
        "username": "johndoe",
        "roles": ["user"],
        "permissions": ["api:read"]
    }
}
```

#### 2. User Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "admin@example.com",
    "password": "Admin123!"
}
```

**Response (200):**
```json
{
    "success": true,
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "admin@example.com",
        "roles": ["admin"],
        "permissions": ["user:manage", "role:manage", "..."]
    }
}
```

#### 3. Access Protected Resources
```http
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

#### 4. Refresh Expired Tokens
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

### RBAC Management

#### List Roles (Admin/Manager)
```http
GET /api/v1/rbac/roles?page=1&per_page=10&include_permissions=true
Authorization: Bearer {admin_token}
```

#### Create Custom Role (Admin)
```http
POST /api/v1/rbac/roles
Authorization: Bearer {admin_token}
Content-Type: application/json

{
    "name": "developer",
    "description": "Software developer with code access",
    "permission_ids": [1, 2, 16, 17]  # Specific permission IDs
}
```

#### Assign Roles to User (Admin)
```http
POST /api/v1/rbac/users/2/roles
Authorization: Bearer {admin_token}
Content-Type: application/json

{
    "role_ids": [2, 3]  # manager and developer roles
}
```

### Complete Endpoint List
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Create new user | No |
| POST | `/auth/login` | Authenticate user | No |
| POST | `/auth/refresh` | Refresh access token | No |
| GET | `/auth/me` | Get current user info | Yes |
| PUT | `/auth/me` | Update profile | Yes |
| POST | `/auth/change-password` | Change password | Yes |
| POST | `/auth/logout` | Logout & blacklist token | Yes |
| GET | `/auth/users` | List all users | Admin |
| GET | `/rbac/roles` | List roles | Manager+ |
| POST | `/rbac/roles` | Create role | Admin |
| GET | `/rbac/permissions` | List permissions | Manager+ |
| POST | `/rbac/permissions` | Create permission | Admin |
| GET | `/health` | Health check | No |
| GET | `/api/v1/info` | API information | No |

---

## 🔐 Security Features

### Password Requirements
- **Minimum 8 characters**
- **At least 1 uppercase letter** (A-Z)
- **At least 1 lowercase letter** (a-z) 
- **At least 1 digit** (0-9)
- **At least 1 special character** (!@#$%^&*)

### JWT Token Security
- **Access tokens:** Expire in 1 hour
- **Refresh tokens:** Expire in 30 days
- **Token blacklisting:** Secure logout prevents reuse
- **JTI tracking:** Unique token identification
- **Claims validation:** Automatic expiration checking

### RBAC Permission System
Permissions follow the pattern: `{resource}:{action}`

**Available Actions:**
- `create` - Create new resources
- `read` - View/list resources  
- `update` - Modify existing resources
- `delete` - Remove resources
- `manage` - Full access (create + read + update + delete)

**Example Permissions:**
```
user:read        # Can view user information
orders:create    # Can create new orders
products:manage  # Full product management access
system:admin     # System administration access
```

### Default Security Roles

#### 🔴 Admin (Full Access)
```
Permissions: user:manage, role:manage, permission:manage, 
            api:manage, system:admin, orders:manage, products:manage
Use Case: System administrators, DevOps
```

#### 🟡 Manager (Limited Admin)
```
Permissions: user:read, user:update, role:read, permission:read,
            orders:manage, products:read, products:update
Use Case: Department heads, team leaders
```

#### 🟢 Employee (Operational)
```
Permissions: api:read, orders:read, orders:create, products:read
Use Case: Regular staff, customer service
```

#### 🔵 User (Basic)
```
Permissions: api:read
Use Case: External users, customers
```

---

## 🔗 Integration Guide

### Microservice Integration

#### 1. JWT Token Verification
Your other microservices should verify tokens like this:

```python
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_permissions = claims.get('permissions', [])
                
                if permission not in user_permissions:
                    return {'error': 'Insufficient permissions'}, 403
                
                return f(*args, **kwargs)
            except Exception:
                return {'error': 'Invalid token'}, 401
        return decorated_function
    return decorator

# Usage in your order service
@app.route('/orders')
@require_permission('orders:read')
def get_orders():
    return {'orders': []}
```

#### 2. Token Payload Structure
```json
{
    "sub": 1,                    # User ID
    "email": "user@company.com", # User email
    "username": "johndoe",       # Username
    "roles": ["employee"],       # User roles
    "permissions": [             # User permissions
        "api:read",
        "orders:read",
        "orders:create"
    ],
    "iat": 1699123456,          # Issued at
    "exp": 1699127056,          # Expires at
    "jti": "unique-token-id"    # JWT ID
}
```

#### 3. Service Configuration
Each microservice needs the same JWT secret:

```python
# In your microservice config
JWT_SECRET_KEY = "same-secret-as-auth-server"

# Initialize JWT in your Flask app
from flask_jwt_extended import JWTManager
jwt = JWTManager(app)
```

### Frontend Integration

#### JavaScript/React Example
```javascript
// Login and store token
const login = async (email, password) => {
    const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    if (data.success) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
    }
    return data;
};

// Make authenticated requests
const apiCall = async (endpoint) => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(endpoint, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.status === 401) {
        // Token expired, try refresh
        await refreshToken();
        // Retry request
    }
    
    return response.json();
};
```

---

## 🚀 Production Deployment

### Environment Variables
Create a production `.env` file:

```bash
# Security (CHANGE THESE!)
JWT_SECRET_KEY=your-256-bit-production-secret-key
SECRET_KEY=your-flask-production-secret-key

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/production_db

# Application
FLASK_ENV=production
BCRYPT_LOG_ROUNDS=13

# Optional: Redis for rate limiting
REDIS_URL=redis://redis-host:6379/0

# CORS (adjust for your frontend domains)
CORS_ORIGINS=https://yourapp.com,https://admin.yourapp.com
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

# Use Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "main:app"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  auth-server:
    build: .
    ports:
      - "5001:5001"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/flask
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=flask
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:alpine
    
volumes:
  postgres_data:
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name auth.yourcompany.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check if virtual environment is active
source .venv/bin/activate

# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check if database exists
psql -h localhost -U postgres -l | grep flask
```

#### Database Connection Issues
```bash
# Test database connection
python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/flask')
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

#### Token Validation Errors
- **"Token has expired"**: Use refresh token to get new access token
- **"Invalid token"**: Token may be corrupted or using wrong secret
- **"Token is required"**: Include `Authorization: Bearer {token}` header

#### Permission Denied Errors
```bash
# Check user permissions
curl -H "Authorization: Bearer {token}" \
     http://localhost:5001/api/v1/auth/me

# Check required permission for endpoint in middleware/auth.py
```

### Debug Mode
Enable detailed logging:
```bash
export FLASK_DEBUG=1
python simple_main.py
```

### Health Check
```bash
curl http://localhost:5001/health
# Should return: {"success": true, "message": "Authorization server is healthy"}
```

---

## 📚 Additional Resources

### File Structure Reference
- **`simple_main.py`** - Recommended production server (no Redis)
- **`main.py`** - Full-featured server (with Redis rate limiting)
- **`working_server.py`** - Demo server (in-memory storage)
- **`init_db.py`** - Database initialization script
- **`demo.py`** - Component verification script

### Default Admin Access
- **Email:** admin@example.com
- **Password:** Admin123!
- **⚠️ Change password immediately in production!**

### Support
For issues or questions:
1. Check this documentation
2. Review error logs in debug mode
3. Test with the provided demo scripts
4. Verify database and dependencies are properly installed

---

**🎉 Your enterprise authorization server is ready for production use!**
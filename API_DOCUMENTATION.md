# Enterprise Authorization Server API Documentation

## Overview

This is an enterprise-grade Flask authorization server with JWT authentication and Role-Based Access Control (RBAC). It's designed to serve as a central authentication and authorization service for microservices architecture.

## Features

- **JWT Authentication**: Secure token-based authentication with access and refresh tokens
- **RBAC (Role-Based Access Control)**: Fine-grained permission system
- **User Management**: Complete user lifecycle management
- **Token Management**: Token blacklisting and refresh capabilities
- **Rate Limiting**: API rate limiting for security
- **CORS Support**: Cross-origin resource sharing
- **Password Security**: Strong password hashing with bcrypt
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **API Versioning**: Versioned API endpoints
- **Comprehensive Logging**: Structured logging for monitoring
- **Health Checks**: System health monitoring endpoints

## Quick Start

### 1. Database Setup

Make sure PostgreSQL is running with your credentials:
- Username: postgres
- Password: postgres  
- Database: flask
- Host: localhost
- Port: 5432

### 2. Environment Setup

The application uses the provided `.env` file. Update the following if needed:
- JWT secret keys
- Database credentials
- Redis configuration (optional, for rate limiting)

### 3. Initialize Database

Run the database initialization script:

```bash
python init_db.py
```

This creates:
- All database tables
- Default permissions
- Default roles (admin, manager, employee, user)
- Default admin user (admin@example.com / Admin123!)

### 4. Start the Server

```bash
python main.py
```

The server will start on `http://localhost:5001`

## API Endpoints

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

Response:
```json
{
    "success": true,
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "johndoe",
        "roles": [...],
        "permissions": [...]
    }
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

#### Update Profile
```http
PUT /api/v1/auth/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Smith"
}
```

#### Change Password
```http
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "old_password": "OldPass123!",
    "new_password": "NewPass123!"
}
```

#### Verify Token
```http
GET /api/v1/auth/verify-token
Authorization: Bearer <access_token>
```

#### Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

### RBAC Endpoints

#### Get All Roles
```http
GET /api/v1/rbac/roles?page=1&per_page=10&include_permissions=true
Authorization: Bearer <access_token>
```

#### Create Role
```http
POST /api/v1/rbac/roles
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "developer",
    "description": "Software developer role",
    "permission_ids": [1, 2, 3]
}
```

#### Update Role
```http
PUT /api/v1/rbac/roles/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "description": "Updated description",
    "permission_ids": [1, 2, 3, 4]
}
```

#### Get All Permissions
```http
GET /api/v1/rbac/permissions?resource=user&action=read
Authorization: Bearer <access_token>
```

#### Create Permission
```http
POST /api/v1/rbac/permissions
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "blog:create",
    "description": "Create blog posts",
    "resource": "blog",
    "action": "create"
}
```

#### Assign Roles to User
```http
POST /api/v1/rbac/users/1/roles
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "role_ids": [1, 2]
}
```

#### Get User Permissions
```http
GET /api/v1/rbac/users/1/permissions
Authorization: Bearer <access_token>
```

#### Check User Permission
```http
GET /api/v1/rbac/users/1/permissions/user:read/check
Authorization: Bearer <access_token>
```

### Admin Endpoints

#### Get All Users (Admin Only)
```http
GET /api/v1/auth/users?page=1&per_page=10&search=john
Authorization: Bearer <admin_access_token>
```

#### Activate User (Admin Only)
```http
POST /api/v1/auth/users/1/activate
Authorization: Bearer <admin_access_token>
```

#### Deactivate User (Admin Only)
```http
POST /api/v1/auth/users/1/deactivate
Authorization: Bearer <admin_access_token>
```

### Utility Endpoints

#### Health Check
```http
GET /health
```

#### API Info
```http
GET /api/v1/info
```

## Integration with Other Microservices

### JWT Token Verification

Other microservices can verify JWT tokens by:

1. **Extracting the JWT token** from the Authorization header
2. **Verifying the signature** using the same JWT secret
3. **Checking token expiration** and blacklist status
4. **Extracting user permissions** from token claims

### Example Token Claims

```json
{
    "sub": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "roles": ["employee"],
    "permissions": ["api:read", "orders:read", "orders:create"],
    "iat": 1699123456,
    "exp": 1699127056,
    "jti": "unique-token-id"
}
```

### Microservice Authorization Example

```python
# Example for another microservice
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def check_permission(required_permission):
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_permissions = claims.get('permissions', [])
                
                if required_permission not in user_permissions:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            except Exception:
                return jsonify({'error': 'Invalid token'}), 401
        return wrapper
    return decorator

@app.route('/orders')
@check_permission('orders:read')
def get_orders():
    # Your order logic here
    return jsonify({'orders': []})
```

## Default Roles and Permissions

### Roles

1. **admin**: Full system access
2. **manager**: Limited administrative access
3. **employee**: Regular employee access
4. **user**: Basic user access

### Permission Structure

Permissions follow the pattern: `resource:action`

- **Resources**: user, role, permission, api, system, orders, products, etc.
- **Actions**: create, read, update, delete, manage

Examples:
- `user:read` - Read user information
- `orders:create` - Create orders
- `system:manage` - Full system administration

## Security Features

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### Token Security

- Access tokens expire in 1 hour (configurable)
- Refresh tokens expire in 30 days (configurable)
- Token blacklisting for secure logout
- JTI (JWT ID) for token tracking

### Rate Limiting

- 100 requests per hour per IP (configurable)
- Redis-based rate limiting storage
- Customizable per endpoint

## Production Deployment

### Environment Variables

Update these in production:

```bash
# Security
JWT_SECRET_KEY=your-production-jwt-secret-key
SECRET_KEY=your-production-secret-key

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (for rate limiting)
REDIS_URL=redis://host:port/db

# Flask
FLASK_ENV=production
```

### Database Migration

```bash
# Install Flask-Migrate commands
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5001 main:app
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5001

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "main:app"]
```

## Error Handling

All API responses follow a consistent format:

### Success Response
```json
{
    "success": true,
    "data": {},
    "message": "Operation successful"
}
```

### Error Response
```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field": ["Validation error message"]
    }
}
```

## Monitoring and Logging

### Health Check Endpoint

Use `/health` for monitoring system status.

### Logs

The application provides structured logging for:
- Authentication attempts
- Authorization failures
- Token operations
- Database operations
- API requests

## Support and Development

### Adding New Permissions

1. Create permission in database:
```python
permission = Permission(
    name="resource:action",
    description="Description",
    resource="resource_name",
    action="action_name"
)
```

2. Assign to roles as needed
3. Use in middleware decorators

### Custom Middleware

```python
from app.middleware.auth import permission_required

@app.route('/custom-endpoint')
@permission_required('custom:action')
def custom_endpoint(**kwargs):
    current_user = kwargs['current_user']
    # Your logic here
```

This authorization server provides a solid foundation for enterprise applications requiring secure, scalable authentication and authorization services.
# 🛡️ Enterprise Flask Authorization Server

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com)
[![JWT](https://img.shields.io/badge/JWT-Authentication-orange.svg)](https://jwt.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A **production-ready** enterprise authorization server built with Flask, featuring JWT authentication and Role-Based Access Control (RBAC). Designed as a central authentication service for microservices architectures.

## 🚀 Quick Start

```bash
# 1. Ensure PostgreSQL is running (localhost:5432, db: flask)
# 2. Activate virtual environment
source .venv/bin/activate

# 3. Initialize database with default roles and admin user
python init_db.py

# 4. Start the server
python simple_main.py

# 5. Test the installation
python test_working_server.py
```

**🎉 Your authorization server is now running at http://127.0.0.1:5001**

**Default Admin Login:** admin@example.com / Admin123!

## ✨ Key Features

- 🔐 **JWT Authentication** - Secure token-based authentication with refresh tokens
- 👥 **RBAC System** - Fine-grained role and permission management  
- 🛡️ **Enterprise Security** - Password strength, token blacklisting, CORS support
- 🗄️ **PostgreSQL Integration** - Robust database with proper relationships
- 🌐 **Microservice Ready** - Easy integration with other services
- 📊 **Health Monitoring** - Built-in health checks and API info endpoints
- 🐳 **Production Ready** - Docker, Gunicorn, and environment configuration
- ⚡ **Rate Limiting** - Optional Redis-based API rate limiting
- 📝 **Input Validation** - Comprehensive request validation and error handling

## 📚 Documentation

### 📖 Main Documentation
- **[📋 Complete Documentation](COMPLETE_DOCUMENTATION.md)** - **START HERE** - Comprehensive guide with setup, API reference, and deployment
- **[🔧 API Reference](API_DOCUMENTATION.md)** - Detailed API endpoints and examples
- **[🎯 Project Summary](PROJECT_SUMMARY.md)** - Overview of features and architecture

### 🏗️ Architecture & Code
- **[📁 Project Structure](#project-structure)** - File organization and components
- **[🔐 Security Features](#security-features)** - Authentication and authorization details
- **[🌐 Integration Guide](#integration-with-microservices)** - How to use with other services

### 🚀 Deployment & Operations
- **[🐳 Production Deployment](COMPLETE_DOCUMENTATION.md#production-deployment)** - Docker, environment setup
- **[🔧 Troubleshooting](COMPLETE_DOCUMENTATION.md#troubleshooting)** - Common issues and solutions
- **[📊 Health Monitoring](#health-monitoring)** - Monitoring and maintenance

## 📁 Project Structure

```
flask-auth-server/
├── 📚 Documentation
│   ├── README.md                    # This file - project overview
│   ├── COMPLETE_DOCUMENTATION.md    # 📋 Main documentation 
│   ├── API_DOCUMENTATION.md         # 🔧 API reference
│   └── PROJECT_SUMMARY.md           # 🎯 Feature overview
│
├── 🏗️ Core Application
│   ├── app/
│   │   ├── __init__.py             # Flask application factory
│   │   ├── controllers/            # 🌐 REST API endpoints
│   │   │   ├── auth_controller.py  # Authentication endpoints
│   │   │   └── rbac_controller.py  # Role/permission management
│   │   ├── models/                 # 🗄️ Database models
│   │   │   ├── __init__.py        # Database initialization
│   │   │   └── auth.py            # User, Role, Permission models
│   │   ├── middleware/             # 🛡️ Security middleware
│   │   │   └── auth.py            # JWT & RBAC decorators
│   │   ├── services/              # 💼 Business logic
│   │   │   └── auth_service.py    # Auth & RBAC services
│   │   └── schemas/               # ✅ Input validation
│   │       └── auth.py            # Marshmallow schemas
│   │
│   ├── 🚀 Server Entry Points
│   │   ├── simple_main.py         # 🟢 Recommended server (no Redis)
│   │   ├── main.py                # Full server (with Redis)
│   │   ├── working_server.py      # Demo server (in-memory)
│   │   └── minimal_server.py      # Test server (basic Flask)
│   │
│   └── 🔧 Configuration & Setup
│       ├── config.py              # Application configuration
│       ├── simple_config.py       # Simplified config (no Redis)
│       ├── init_db.py            # Database initialization
│       ├── requirements.txt       # Python dependencies
│       └── .env                  # Environment variables
│
├── 🧪 Testing & Demo
│   ├── demo.py                   # Component verification
│   ├── test_working_server.py    # Comprehensive API tests
│   ├── test_api.py              # Full integration tests
│   ├── simple_test.py           # Basic connectivity tests
│   └── quick_test.py            # Minimal endpoint tests
│
└── 🐳 Deployment
    ├── .gitignore               # Git ignore rules
    ├── Dockerfile               # Docker container (in docs)
    └── docker-compose.yml       # Multi-service setup (in docs)
```

## 🔐 Security Features

### 🎯 Authentication & Authorization
- **JWT Tokens** with configurable expiration (1 hour access, 30 days refresh)
- **Token Blacklisting** for secure logout
- **Password Security** with bcrypt hashing and strength requirements
- **Role-Based Access Control** with fine-grained permissions

### 🛡️ Security Policies
- **Password Requirements**: 8+ chars, uppercase, lowercase, digits, special chars
- **Permission System**: `resource:action` format (e.g., `orders:create`, `user:manage`)
- **CORS Support** for cross-origin requests
- **Rate Limiting** (optional, with Redis)
- **Input Validation** with Marshmallow schemas

### 👥 Default Roles
| Role | Permissions | Use Case |
|------|-------------|----------|
| **admin** | Full system access | System administrators |
| **manager** | Limited admin access | Department heads |
| **employee** | Operational access | Regular staff |
| **user** | Basic API access | External users |

## 🌐 Integration with Microservices

### 🔗 How Other Services Use This
1. **Verify JWT tokens** using the same secret key
2. **Extract permissions** from token claims
3. **Check authorization** without calling auth server
4. **Manage permissions** via RBAC API endpoints

### 💻 Example Integration
```python
# In your order microservice
from flask_jwt_extended import verify_jwt_in_request, get_jwt

@app.route('/orders')
def get_orders():
    verify_jwt_in_request()
    claims = get_jwt()
    
    if 'orders:read' not in claims.get('permissions', []):
        return {'error': 'Insufficient permissions'}, 403
    
    return {'orders': [...]}
```

### 🎫 JWT Token Contains
```json
{
    "sub": 1,
    "email": "user@company.com",
    "username": "johndoe",
    "roles": ["employee"],
    "permissions": ["api:read", "orders:create", "products:read"],
    "exp": 1699127056
}
```

## 🔌 API Endpoints

### 🔑 Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login  
- `POST /api/v1/auth/refresh` - Refresh tokens
- `GET /api/v1/auth/me` - Current user info
- `POST /api/v1/auth/logout` - Secure logout

### 👥 RBAC Management  
- `GET /api/v1/rbac/roles` - List roles
- `POST /api/v1/rbac/roles` - Create role
- `GET /api/v1/rbac/permissions` - List permissions
- `POST /api/v1/rbac/users/{id}/roles` - Assign roles

### 🔧 System
- `GET /health` - Health check
- `GET /api/v1/info` - API information

**📖 [Complete API Reference →](API_DOCUMENTATION.md)**

## 📊 Health Monitoring

### 🏥 Health Check
```bash
curl http://localhost:5001/health
```
Response:
```json
{
    "success": true,
    "message": "Authorization server is healthy",
    "version": "1.0.0"
}
```

### 📈 Monitoring Endpoints
- **Health Status**: `GET /health`
- **API Information**: `GET /api/v1/info`
- **Token Verification**: `GET /api/v1/auth/verify-token`

## 🚀 Production Deployment

### 🐳 Docker Deployment (Recommended)

**Quick Start with Docker Compose:**
```bash
# 1. Setup environment
cp .env.docker .env
# Edit .env with secure passwords

# 2. Start all services (Flask + PostgreSQL + Redis)
docker-compose up -d

# 3. Test deployment
curl http://localhost:5001/health
```

**📖 [Complete Docker Guide →](DOCKER_GUIDE.md)** - Comprehensive Docker deployment with PostgreSQL, Redis, Nginx, and production configurations.

### 🔧 Manual Deployment

**Environment Variables:**
```bash
JWT_SECRET_KEY=your-256-bit-secret
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0  # Optional
FLASK_ENV=production
```

**Production Server:**
```bash
gunicorn --workers 4 --bind 0.0.0.0:5001 minimal_main:create_minimal_app()
```

**📖 [Complete Deployment Guide →](COMPLETE_DOCUMENTATION.md#production-deployment)**

## 🧪 Testing

### 🔍 Verify Installation
```bash
# Test all components
python demo.py

# Test API endpoints
python test_working_server.py

# Quick connectivity test
python simple_test.py
```

### 🎯 Manual Testing
```bash
# Health check
curl http://localhost:5001/health

# Admin login
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin123!"}'
```

## 📋 Getting Started Checklist

- [ ] **Prerequisites**: Python 3.13+, PostgreSQL running
- [ ] **Setup**: Virtual environment activated, dependencies installed
- [ ] **Database**: `python init_db.py` completed successfully
- [ ] **Server**: `python simple_main.py` running on port 5001
- [ ] **Test**: `python test_working_server.py` passes all tests
- [ ] **Login**: Can authenticate with admin@example.com / Admin123!
- [ ] **Integration**: Other services can verify JWT tokens

## 🆘 Need Help?

### 📖 Documentation
1. **[Complete Documentation](COMPLETE_DOCUMENTATION.md)** - Comprehensive guide
2. **[Troubleshooting](COMPLETE_DOCUMENTATION.md#troubleshooting)** - Common issues
3. **[API Reference](API_DOCUMENTATION.md)** - Endpoint details

### 🔧 Common Issues
- **Server won't start**: Check virtual environment and PostgreSQL
- **Database errors**: Verify PostgreSQL credentials and `flask` database exists  
- **Token errors**: Ensure JWT secret consistency across services
- **Permission denied**: Check user roles and required permissions

### 🚀 Quick Fixes
```bash
# Reset database
dropdb flask && createdb flask && python init_db.py

# Check server status  
curl http://localhost:5001/health

# View logs
python simple_main.py  # Check terminal output
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Update documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 Ready to Go!

Your **Enterprise Authorization Server** is production-ready with:

✅ **30 Permissions** for comprehensive access control  
✅ **4 Default Roles** for common use cases  
✅ **JWT Authentication** with refresh token support  
✅ **RBAC System** for fine-grained authorization  
✅ **Microservice Integration** ready  
✅ **Production Deployment** with Docker and Gunicorn  
✅ **Comprehensive Documentation** and testing  

**Start with:** `python simple_main.py` and visit http://localhost:5001/health

**📖 [Get Started with Complete Documentation →](COMPLETE_DOCUMENTATION.md)**
#!/usr/bin/env python3
"""
Final Working Authorization Server
This version fixes all issues and provides a fully functional server.
"""

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# In-memory storage (replace with database in production)
users = {
    "admin@example.com": {
        "id": 1,
        "email": "admin@example.com",
        "username": "admin",
        "password": "Admin123!",  # In production, this should be hashed
        "first_name": "Admin",
        "last_name": "User",
        "roles": ["admin"],
        "permissions": ["user:manage", "role:manage", "permission:manage", "api:manage", "system:admin"]
    },
    "user@example.com": {
        "id": 2,
        "email": "user@example.com", 
        "username": "user",
        "password": "User123!",
        "first_name": "Regular",
        "last_name": "User",
        "roles": ["user"],
        "permissions": ["api:read"]
    }
}

# Routes
@app.route('/')
def home():
    return jsonify({
        'message': 'Enterprise Authorization Server',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'info': '/api/v1/info',
            'login': '/api/v1/auth/login',
            'me': '/api/v1/auth/me'
        }
    })

@app.route('/health')
def health():
    return jsonify({
        'success': True,
        'message': 'Authorization server is healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/v1/info')
def api_info():
    return jsonify({
        'success': True,
        'api': {
            'name': 'Enterprise Authorization Server',
            'version': '1.0.0',
            'description': 'JWT authentication with RBAC',
            'features': [
                'JWT Authentication',
                'Role-Based Access Control',
                'User Management',
                'Permission System',
                'CORS Support'
            ]
        }
    })

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        email = data['email']
        password = data['password']
        
        # Find user
        user = users.get(email)
        if not user or user['password'] != password:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        # Create access token
        additional_claims = {
            'email': user['email'],
            'username': user['username'],
            'roles': user['roles'],
            'permissions': user['permissions']
        }
        
        access_token = create_access_token(
            identity=user['id'],
            additional_claims=additional_claims
        )
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'username': user['username'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'roles': user['roles'],
                'permissions': user['permissions']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'error': str(e)
        }), 500

@app.route('/api/v1/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        
        # Find user by ID
        user = None
        for email, user_data in users.items():
            if user_data['id'] == current_user_id:
                user = user_data
                break
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'username': user['username'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'roles': user['roles'],
                'permissions': user['permissions']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get user',
            'error': str(e)
        }), 500

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': 'All fields are required: email, username, password, first_name, last_name'
            }), 400
        
        email = data['email']
        
        # Check if user already exists
        if email in users:
            return jsonify({
                'success': False,
                'message': 'User already exists'
            }), 409
        
        # Create new user
        new_user = {
            'id': len(users) + 1,
            'email': email,
            'username': data['username'],
            'password': data['password'],  # In production, hash this
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'roles': ['user'],
            'permissions': ['api:read']
        }
        
        users[email] = new_user
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': new_user['id'],
                'email': new_user['email'],
                'username': new_user['username'],
                'first_name': new_user['first_name'],
                'last_name': new_user['last_name'],
                'roles': new_user['roles'],
                'permissions': new_user['permissions']
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error': str(e)
        }), 500

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'message': 'Token has expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'success': False,
        'message': 'Invalid token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'success': False,
        'message': 'Token is required'
    }), 401

if __name__ == '__main__':
    print("🚀 Starting Enterprise Authorization Server")
    print("📍 Server: http://127.0.0.1:5000")
    print("📍 Health: http://127.0.0.1:5000/health")
    print("📍 API Info: http://127.0.0.1:5000/api/v1/info")
    print("\n🔐 Default Login Credentials:")
    print("   Admin: admin@example.com / Admin123!")
    print("   User:  user@example.com / User123!")
    print("\n✨ Ready to accept requests!")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
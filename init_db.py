#!/usr/bin/env python3
"""
Database initialization script for the authorization server.
Creates default roles, permissions, and admin user.
"""

import os
import sys
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.auth import User, Role, Permission

def create_default_permissions():
    """Create default permissions for the system."""
    permissions_data = [
        # User management permissions
        {'name': 'user:create', 'description': 'Create new users', 'resource': 'user', 'action': 'create'},
        {'name': 'user:read', 'description': 'View user information', 'resource': 'user', 'action': 'read'},
        {'name': 'user:update', 'description': 'Update user information', 'resource': 'user', 'action': 'update'},
        {'name': 'user:delete', 'description': 'Delete users', 'resource': 'user', 'action': 'delete'},
        {'name': 'user:manage', 'description': 'Full user management access', 'resource': 'user', 'action': 'manage'},
        
        # Role management permissions
        {'name': 'role:create', 'description': 'Create new roles', 'resource': 'role', 'action': 'create'},
        {'name': 'role:read', 'description': 'View role information', 'resource': 'role', 'action': 'read'},
        {'name': 'role:update', 'description': 'Update role information', 'resource': 'role', 'action': 'update'},
        {'name': 'role:delete', 'description': 'Delete roles', 'resource': 'role', 'action': 'delete'},
        {'name': 'role:manage', 'description': 'Full role management access', 'resource': 'role', 'action': 'manage'},
        
        # Permission management permissions
        {'name': 'permission:create', 'description': 'Create new permissions', 'resource': 'permission', 'action': 'create'},
        {'name': 'permission:read', 'description': 'View permission information', 'resource': 'permission', 'action': 'read'},
        {'name': 'permission:update', 'description': 'Update permission information', 'resource': 'permission', 'action': 'update'},
        {'name': 'permission:delete', 'description': 'Delete permissions', 'resource': 'permission', 'action': 'delete'},
        {'name': 'permission:manage', 'description': 'Full permission management access', 'resource': 'permission', 'action': 'manage'},
        
        # API access permissions
        {'name': 'api:read', 'description': 'Read access to API resources', 'resource': 'api', 'action': 'read'},
        {'name': 'api:write', 'description': 'Write access to API resources', 'resource': 'api', 'action': 'create'},
        {'name': 'api:manage', 'description': 'Full API management access', 'resource': 'api', 'action': 'manage'},
        
        # System administration permissions
        {'name': 'system:admin', 'description': 'System administration access', 'resource': 'system', 'action': 'manage'},
        {'name': 'system:monitor', 'description': 'System monitoring access', 'resource': 'system', 'action': 'read'},
        
        # Microservice permissions (examples for other services)
        {'name': 'orders:create', 'description': 'Create orders', 'resource': 'orders', 'action': 'create'},
        {'name': 'orders:read', 'description': 'View orders', 'resource': 'orders', 'action': 'read'},
        {'name': 'orders:update', 'description': 'Update orders', 'resource': 'orders', 'action': 'update'},
        {'name': 'orders:delete', 'description': 'Delete orders', 'resource': 'orders', 'action': 'delete'},
        {'name': 'orders:manage', 'description': 'Full order management', 'resource': 'orders', 'action': 'manage'},
        
        {'name': 'products:create', 'description': 'Create products', 'resource': 'products', 'action': 'create'},
        {'name': 'products:read', 'description': 'View products', 'resource': 'products', 'action': 'read'},
        {'name': 'products:update', 'description': 'Update products', 'resource': 'products', 'action': 'update'},
        {'name': 'products:delete', 'description': 'Delete products', 'resource': 'products', 'action': 'delete'},
        {'name': 'products:manage', 'description': 'Full product management', 'resource': 'products', 'action': 'manage'},
    ]
    
    created_permissions = []
    
    for perm_data in permissions_data:
        permission = Permission.query.filter_by(name=perm_data['name']).first()
        if not permission:
            permission = Permission(**perm_data)
            db.session.add(permission)
            created_permissions.append(permission)
            print(f"Created permission: {perm_data['name']}")
        else:
            print(f"Permission already exists: {perm_data['name']}")
    
    return created_permissions

def create_default_roles():
    """Create default roles for the system."""
    roles_data = [
        {
            'name': 'admin',
            'description': 'System administrator with full access',
            'permissions': [
                'user:manage', 'role:manage', 'permission:manage', 
                'api:manage', 'system:admin', 'system:monitor',
                'orders:manage', 'products:manage'
            ]
        },
        {
            'name': 'manager',
            'description': 'Manager with limited administrative access',
            'permissions': [
                'user:read', 'user:update', 'role:read', 'permission:read',
                'api:read', 'api:write', 'system:monitor',
                'orders:manage', 'products:read', 'products:update'
            ]
        },
        {
            'name': 'employee',
            'description': 'Regular employee with basic access',
            'permissions': [
                'api:read', 'orders:read', 'orders:create', 'products:read'
            ]
        },
        {
            'name': 'user',
            'description': 'Basic user with minimal access',
            'permissions': [
                'api:read'
            ]
        }
    ]
    
    created_roles = []
    
    for role_data in roles_data:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(
                name=role_data['name'],
                description=role_data['description']
            )
            
            # Assign permissions to role
            for perm_name in role_data['permissions']:
                permission = Permission.query.filter_by(name=perm_name).first()
                if permission:
                    role.permissions.append(permission)
            
            db.session.add(role)
            created_roles.append(role)
            print(f"Created role: {role_data['name']} with {len(role_data['permissions'])} permissions")
        else:
            print(f"Role already exists: {role_data['name']}")
    
    return created_roles

def create_admin_user():
    """Create default admin user."""
    admin_email = "admin@example.com"
    admin_user = User.query.filter_by(email=admin_email).first()
    
    if not admin_user:
        admin_user = User(
            email=admin_email,
            username="admin",
            password="Admin123!",  # Change this in production
            first_name="System",
            last_name="Administrator",
            is_active=True,
            is_verified=True
        )
        
        # Assign admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin_user.roles.append(admin_role)
        
        db.session.add(admin_user)
        print(f"Created admin user: {admin_email}")
        print("Default password: Admin123! (Change this immediately!)")
    else:
        print(f"Admin user already exists: {admin_email}")
    
    return admin_user

def init_database():
    """Initialize the database with default data."""
    app = create_app()
    
    with app.app_context():
        print("Initializing database...")
        
        # Create tables
        db.create_all()
        print("Database tables created.")
        
        # Create default permissions
        print("\nCreating default permissions...")
        create_default_permissions()
        
        # Create default roles
        print("\nCreating default roles...")
        create_default_roles()
        
        # Create admin user
        print("\nCreating default admin user...")
        create_admin_user()
        
        # Commit all changes
        db.session.commit()
        print("\nDatabase initialization completed successfully!")
        
        # Print summary
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION SUMMARY")
        print("="*50)
        print(f"Total Permissions: {Permission.query.count()}")
        print(f"Total Roles: {Role.query.count()}")
        print(f"Total Users: {User.query.count()}")
        print("\nDefault Admin Credentials:")
        print("Email: admin@example.com")
        print("Password: Admin123!")
        print("\n⚠️  IMPORTANT: Change the admin password immediately after first login!")
        print("="*50)

if __name__ == '__main__':
    init_database()
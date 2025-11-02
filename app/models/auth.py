from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt
from app.models import db

bcrypt = Bcrypt()

# Association tables for many-to-many relationships
user_roles = Table('user_roles', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table('role_permissions', db.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class User(db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime)
    
    # Relationships
    roles = relationship('Role', secondary=user_roles, lazy='subquery', back_populates='users')
    refresh_tokens = relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan')
    
    def __init__(self, email, username, password, first_name, last_name, **kwargs):
        """Initialize user with hashed password."""
        self.email = email
        self.username = username
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, permission_name):
        """Check if user has a specific permission."""
        for role in self.roles:
            if role.has_permission(permission_name):
                return True
        return False
    
    def get_permissions(self):
        """Get all permissions for user."""
        permissions = set()
        for role in self.roles:
            permissions.update([perm.name for perm in role.permissions])
        return list(permissions)
    
    def to_dict(self, include_roles=False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_roles:
            data['roles'] = [role.to_dict() for role in self.roles]
            data['permissions'] = self.get_permissions()
        
        return data

class Role(db.Model):
    """Role model for RBAC."""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    users = relationship('User', secondary=user_roles, lazy='subquery', back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, lazy='subquery', back_populates='roles')
    
    def has_permission(self, permission_name):
        """Check if role has a specific permission."""
        return any(perm.name == permission_name for perm in self.permissions)
    
    def to_dict(self, include_permissions=False):
        """Convert role to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_permissions:
            data['permissions'] = [perm.to_dict() for perm in self.permissions]
        
        return data

class Permission(db.Model):
    """Permission model for RBAC."""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False, index=True)
    description = Column(Text)
    resource = Column(String(80), nullable=False)  # e.g., 'user', 'post', 'admin'
    action = Column(String(80), nullable=False)    # e.g., 'create', 'read', 'update', 'delete'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    roles = relationship('Role', secondary=role_permissions, lazy='subquery', back_populates='permissions')
    
    def to_dict(self):
        """Convert permission to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'resource': self.resource,
            'action': self.action,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RefreshToken(db.Model):
    """Refresh token model for JWT token management."""
    __tablename__ = 'refresh_tokens'
    
    id = Column(Integer, primary_key=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='refresh_tokens')
    
    def is_expired(self):
        """Check if token is expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    def to_dict(self):
        """Convert refresh token to dictionary."""
        return {
            'id': self.id,
            'token': self.token,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat(),
            'is_revoked': self.is_revoked,
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat()
        }

class BlacklistedToken(db.Model):
    """Blacklisted token model for JWT token management."""
    __tablename__ = 'blacklisted_tokens'
    
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), unique=True, nullable=False, index=True)
    token_type = Column(String(10), nullable=False)  # 'access' or 'refresh'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    blacklisted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def to_dict(self):
        """Convert blacklisted token to dictionary."""
        return {
            'id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat(),
            'blacklisted_at': self.blacklisted_at.isoformat()
        }
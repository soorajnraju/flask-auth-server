from datetime import datetime, timezone, timedelta
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError
from app.models import db
from app.models.auth import User, Role, Permission, RefreshToken, BlacklistedToken
import secrets

class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    def register_user(data):
        """Register a new user."""
        try:
            user = User(
                email=data['email'],
                username=data['username'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            
            # Assign default role if exists
            default_role = Role.query.filter_by(name='user').first()
            if default_role:
                user.roles.append(default_role)
            
            db.session.add(user)
            db.session.commit()
            
            return {'success': True, 'user': user.to_dict()}, 201
        except IntegrityError as e:
            db.session.rollback()
            if 'email' in str(e.orig):
                return {'success': False, 'message': 'Email already exists'}, 409
            elif 'username' in str(e.orig):
                return {'success': False, 'message': 'Username already exists'}, 409
            else:
                return {'success': False, 'message': 'User registration failed'}, 400
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user and return tokens."""
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if not user or not user.check_password(password):
            return {'success': False, 'message': 'Invalid credentials'}, 401
        
        if not user.is_verified:
            return {'success': False, 'message': 'Account not verified'}, 401
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        
        # Create tokens (convert user.id to string for JWT compatibility)
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'username': user.username,
                'roles': [role.name for role in user.roles],
                'permissions': user.get_permissions()
            }
        )
        
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Store refresh token
        AuthService.store_refresh_token(refresh_token, user.id)
        
        db.session.commit()
        
        return {
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(include_roles=True)
        }, 200
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Refresh access token using refresh token."""
        stored_token = RefreshToken.query.filter_by(token=refresh_token).first()
        
        if not stored_token or stored_token.is_revoked or stored_token.is_expired():
            return {'success': False, 'message': 'Invalid or expired refresh token'}, 401
        
        user = User.query.get(stored_token.user_id)
        if not user or not user.is_active:
            return {'success': False, 'message': 'User not found or inactive'}, 401
        
        # Create new access token (convert user.id to string for JWT compatibility)
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'username': user.username,
                'roles': [role.name for role in user.roles],
                'permissions': user.get_permissions()
            }
        )
        
        return {
            'success': True,
            'access_token': access_token
        }, 200
    
    @staticmethod
    def store_refresh_token(token, user_id):
        """Store refresh token in database."""
        expires_at = datetime.now(timezone.utc) + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
        
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        
        db.session.add(refresh_token)
        return refresh_token
    
    @staticmethod
    def revoke_refresh_token(token):
        """Revoke a refresh token."""
        stored_token = RefreshToken.query.filter_by(token=token).first()
        if stored_token:
            stored_token.is_revoked = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def logout_user(access_token_jti, refresh_token=None):
        """Logout user by blacklisting tokens."""
        user_id = get_jwt_identity()
        
        # Blacklist access token
        access_token_blacklist = BlacklistedToken(
            jti=access_token_jti,
            token_type='access',
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        )
        db.session.add(access_token_blacklist)
        
        # Revoke refresh token if provided
        if refresh_token:
            AuthService.revoke_refresh_token(refresh_token)
        
        db.session.commit()
        return {'success': True, 'message': 'Successfully logged out'}, 200
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password."""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404
        
        if not user.check_password(old_password):
            return {'success': False, 'message': 'Invalid current password'}, 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return {'success': True, 'message': 'Password changed successfully'}, 200

class RBACService:
    """Service class for RBAC operations."""
    
    @staticmethod
    def create_role(data):
        """Create a new role."""
        try:
            role = Role(
                name=data['name'],
                description=data.get('description', ''),
                is_active=data.get('is_active', True)
            )
            
            # Assign permissions if provided
            if 'permission_ids' in data:
                permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
                role.permissions.extend(permissions)
            
            db.session.add(role)
            db.session.commit()
            
            return {'success': True, 'role': role.to_dict(include_permissions=True)}, 201
        except IntegrityError:
            db.session.rollback()
            return {'success': False, 'message': 'Role name already exists'}, 409
    
    @staticmethod
    def create_permission(data):
        """Create a new permission."""
        try:
            permission = Permission(
                name=data['name'],
                description=data.get('description', ''),
                resource=data['resource'],
                action=data['action'],
                is_active=data.get('is_active', True)
            )
            
            db.session.add(permission)
            db.session.commit()
            
            return {'success': True, 'permission': permission.to_dict()}, 201
        except IntegrityError:
            db.session.rollback()
            return {'success': False, 'message': 'Permission name already exists'}, 409
    
    @staticmethod
    def assign_roles_to_user(user_id, role_ids):
        """Assign roles to a user."""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404
        
        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        if len(roles) != len(role_ids):
            return {'success': False, 'message': 'One or more roles not found'}, 404
        
        # Clear existing roles and assign new ones
        user.roles.clear()
        user.roles.extend(roles)
        db.session.commit()
        
        return {'success': True, 'user': user.to_dict(include_roles=True)}, 200
    
    @staticmethod
    def get_user_permissions(user_id):
        """Get all permissions for a user."""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404
        
        return {'success': True, 'permissions': user.get_permissions()}, 200
    
    @staticmethod
    def check_user_permission(user_id, permission_name):
        """Check if user has a specific permission."""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404
        
        has_permission = user.has_permission(permission_name)
        return {'success': True, 'has_permission': has_permission}, 200
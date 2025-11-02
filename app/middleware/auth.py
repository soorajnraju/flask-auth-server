from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app.models.auth import User, BlacklistedToken, Permission
from app.models import db

def token_required(f):
    """Decorator for routes that require authentication."""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        try:
            # Check if token is blacklisted
            jti = get_jwt()['jti']
            blacklisted = BlacklistedToken.query.filter_by(jti=jti).first()
            
            if blacklisted:
                return jsonify({
                    'success': False,
                    'message': 'Token has been revoked'
                }), 401
            
            # Get current user (convert string ID back to int)
            current_user_id = get_jwt_identity()
            current_user = User.query.get(int(current_user_id))
            
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': f'User not found with ID: {current_user_id}'
                }), 401
                
            if not current_user.is_active:
                return jsonify({
                    'success': False,
                    'message': 'User account is inactive'
                }), 401
            
            # Add current_user to kwargs for easy access in routes
            kwargs['current_user'] = current_user
            
            return f(*args, **kwargs)
        except Exception as e:
            # Better error reporting for debugging
            import traceback
            print(f"JWT Middleware Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Invalid token: {str(e)}'
            }), 401
    
    return decorated

def role_required(*allowed_roles):
    """Decorator for routes that require specific roles."""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            user_roles = [role.name for role in current_user.roles]
            
            if not any(role in user_roles for role in allowed_roles):
                return jsonify({
                    'success': False,
                    'message': f'Access denied. Required roles: {", ".join(allowed_roles)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

def permission_required(*required_permissions):
    """Decorator for routes that require specific permissions."""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            user_permissions = current_user.get_permissions()
            
            if not any(perm in user_permissions for perm in required_permissions):
                return jsonify({
                    'success': False,
                    'message': f'Access denied. Required permissions: {", ".join(required_permissions)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

def admin_required(f):
    """Decorator for admin-only routes."""
    @wraps(f)
    @role_required('admin')
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated

def optional_token(f):
    """Decorator for routes where token is optional."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            
            if user_id:
                current_user = User.query.get(int(user_id))
                kwargs['current_user'] = current_user
            else:
                kwargs['current_user'] = None
                
        except Exception:
            kwargs['current_user'] = None
        
        return f(*args, **kwargs)
    
    return decorated

class RBACMiddleware:
    """Middleware class for RBAC functionality."""
    
    @staticmethod
    def check_resource_permission(resource, action):
        """Check if current user has permission for resource and action."""
        def decorator(f):
            @wraps(f)
            @token_required
            def decorated(*args, **kwargs):
                current_user = kwargs.get('current_user')
                
                # Check for specific permission
                permission_name = f"{resource}:{action}"
                if current_user.has_permission(permission_name):
                    return f(*args, **kwargs)
                
                # Check for manage permission on resource
                manage_permission = f"{resource}:manage"
                if current_user.has_permission(manage_permission):
                    return f(*args, **kwargs)
                
                # Check for admin role (has all permissions)
                if current_user.has_role('admin'):
                    return f(*args, **kwargs)
                
                return jsonify({
                    'success': False,
                    'message': f'Access denied. Required permission: {permission_name}'
                }), 403
            
            return decorated
        return decorator
    
    @staticmethod
    def check_resource_ownership(resource_param='id'):
        """Check if user owns the resource being accessed."""
        def decorator(f):
            @wraps(f)
            @token_required
            def decorated(*args, **kwargs):
                current_user = kwargs.get('current_user')
                resource_id = kwargs.get(resource_param)
                
                # Admin can access any resource
                if current_user.has_role('admin'):
                    return f(*args, **kwargs)
                
                # Check if user owns the resource (for user resources)
                if resource_param == 'user_id' or resource_param == 'id':
                    if str(current_user.id) == str(resource_id):
                        return f(*args, **kwargs)
                
                return jsonify({
                    'success': False,
                    'message': 'Access denied. You can only access your own resources'
                }), 403
            
            return decorated
        return decorator
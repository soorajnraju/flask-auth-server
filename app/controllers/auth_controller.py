from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from marshmallow import ValidationError
from app.schemas.auth import (
    UserRegistrationSchema, UserLoginSchema, UserUpdateSchema, 
    PasswordChangeSchema, RefreshTokenSchema
)
from app.services.auth_service import AuthService
from app.middleware.auth import token_required, admin_required, optional_token
from app.models.auth import User
from app.models import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        schema = UserRegistrationSchema()
        data = schema.load(request.json)
        
        result, status_code = AuthService.register_user(data)
        return jsonify(result), status_code
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens."""
    try:
        schema = UserLoginSchema()
        data = schema.load(request.json)
        
        result, status_code = AuthService.authenticate_user(
            data['email'], 
            data['password']
        )
        return jsonify(result), status_code
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'error': str(e)
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token."""
    try:
        schema = RefreshTokenSchema()
        data = schema.load(request.json)
        
        result, status_code = AuthService.refresh_access_token(data['refresh_token'])
        return jsonify(result), status_code
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Token refresh failed',
            'error': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(**kwargs):
    """Logout user by blacklisting tokens."""
    try:
        jti = get_jwt()['jti']
        refresh_token = request.json.get('refresh_token') if request.json else None
        
        result, status_code = AuthService.logout_user(jti, refresh_token)
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Logout failed',
            'error': str(e)
        }), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(**kwargs):
    """Get current user information."""
    try:
        current_user = kwargs['current_user']
        return jsonify({
            'success': True,
            'user': current_user.to_dict(include_roles=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get user information',
            'error': str(e)
        }), 500

@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_current_user(**kwargs):
    """Update current user information."""
    try:
        schema = UserUpdateSchema()
        data = schema.load(request.json)
        current_user = kwargs['current_user']
        
        # Update user fields
        for field, value in data.items():
            if field in ['email', 'username', 'first_name', 'last_name']:
                setattr(current_user, field, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': current_user.to_dict(include_roles=True)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update user',
            'error': str(e)
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(**kwargs):
    """Change current user's password."""
    try:
        schema = PasswordChangeSchema()
        data = schema.load(request.json)
        current_user = kwargs['current_user']
        
        result, status_code = AuthService.change_password(
            current_user.id,
            data['old_password'],
            data['new_password']
        )
        return jsonify(result), status_code
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Password change failed',
            'error': str(e)
        }), 500

@auth_bp.route('/verify-token', methods=['GET'])
@token_required
def verify_token(**kwargs):
    """Verify if token is valid and return user info."""
    try:
        current_user = kwargs['current_user']
        jwt_data = get_jwt()
        
        return jsonify({
            'success': True,
            'valid': True,
            'user': current_user.to_dict(include_roles=True),
            'token_data': {
                'jti': jwt_data['jti'],
                'exp': jwt_data['exp'],
                'iat': jwt_data['iat'],
                'type': jwt_data['type']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Token verification failed',
            'error': str(e)
        }), 500

# Admin routes for user management
@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_users(**kwargs):
    """Get all users (admin only)."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.email.contains(search),
                    User.username.contains(search),
                    User.first_name.contains(search),
                    User.last_name.contains(search)
                )
            )
        
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'users': [user.to_dict(include_roles=True) for user in users.items],
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get users',
            'error': str(e)
        }), 500

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(**kwargs):
    """Get user by ID (admin only)."""
    try:
        user_id = kwargs.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict(include_roles=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get user',
            'error': str(e)
        }), 500

@auth_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(**kwargs):
    """Activate user (admin only)."""
    try:
        user_id = kwargs.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user.is_active = True
        user.is_verified = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User activated successfully',
            'user': user.to_dict(include_roles=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to activate user',
            'error': str(e)
        }), 500

@auth_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(**kwargs):
    """Deactivate user (admin only)."""
    try:
        user_id = kwargs.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deactivated successfully',
            'user': user.to_dict(include_roles=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to deactivate user',
            'error': str(e)
        }), 500
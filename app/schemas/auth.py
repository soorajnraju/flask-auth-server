from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load
import re

def validate_password_strength(password):
    """Validate password strength requirements."""
    errors = []
    
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one digit')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')
    
    if errors:
        raise ValidationError(errors)
    
    return password

class UserRegistrationSchema(Schema):
    """Schema for user registration."""
    email = fields.Email(required=True, validate=validate.Length(max=255))
    username = fields.Str(required=True, validate=[
        validate.Length(min=3, max=80),
        validate.Regexp(r'^[a-zA-Z0-9_]+$', error='Username must contain only letters, numbers, and underscores')
    ])
    password = fields.Str(required=True, validate=[validate.Length(min=8), validate_password_strength])
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))

class UserLoginSchema(Schema):
    """Schema for user login."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserUpdateSchema(Schema):
    """Schema for user updates."""
    email = fields.Email(validate=validate.Length(max=255))
    username = fields.Str(validate=[
        validate.Length(min=3, max=80),
        validate.Regexp(r'^[a-zA-Z0-9_]+$', error='Username must contain only letters, numbers, and underscores')
    ])
    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))
    is_active = fields.Bool()
    is_verified = fields.Bool()

class PasswordChangeSchema(Schema):
    """Schema for changing password."""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=[validate.Length(min=8), validate_password_strength])

class RoleSchema(Schema):
    """Schema for role operations."""
    name = fields.Str(required=True, validate=[
        validate.Length(min=1, max=80),
        validate.Regexp(r'^[a-zA-Z0-9_-]+$', error='Role name must contain only letters, numbers, underscores, and hyphens')
    ])
    description = fields.Str(validate=validate.Length(max=500))
    is_active = fields.Bool()
    permission_ids = fields.List(fields.Int(), load_default=[])

class PermissionSchema(Schema):
    """Schema for permission operations."""
    name = fields.Str(required=True, validate=[
        validate.Length(min=1, max=80),
        validate.Regexp(r'^[a-zA-Z0-9_:-]+$', error='Permission name must contain only letters, numbers, underscores, colons, and hyphens')
    ])
    description = fields.Str(validate=validate.Length(max=500))
    resource = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    action = fields.Str(required=True, validate=validate.OneOf(['create', 'read', 'update', 'delete', 'manage']))
    is_active = fields.Bool()

class UserRoleAssignmentSchema(Schema):
    """Schema for user role assignment."""
    user_id = fields.Int(required=True)
    role_ids = fields.List(fields.Int(), required=True, validate=validate.Length(min=1))

class RefreshTokenSchema(Schema):
    """Schema for refresh token operations."""
    refresh_token = fields.Str(required=True)
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.schemas.auth import RoleSchema, PermissionSchema, UserRoleAssignmentSchema
from app.services.auth_service import RBACService
from app.middleware.auth import admin_required, permission_required
from app.models.auth import Role, Permission, User
from app.models import db

rbac_bp = Blueprint('rbac', __name__, url_prefix='/api/v1/rbac')

# Role management endpoints
@rbac_bp.route('/roles', methods=['GET'])
@permission_required('role:read', 'role:manage')
def get_roles(**kwargs):
    """Get all roles."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        include_permissions = request.args.get('include_permissions', 'false').lower() == 'true'
        
        query = Role.query
        
        if search:
            query = query.filter(
                db.or_(
                    Role.name.contains(search),
                    Role.description.contains(search)
                )
            )
        
        roles = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'roles': [role.to_dict(include_permissions=include_permissions) for role in roles.items],
            'pagination': {
                'page': roles.page,
                'pages': roles.pages,
                'per_page': roles.per_page,
                'total': roles.total,
                'has_next': roles.has_next,
                'has_prev': roles.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get roles',
            'error': str(e)
        }), 500

@rbac_bp.route('/roles', methods=['POST'])
@permission_required('role:create', 'role:manage')
def create_role(**kwargs):
    """Create a new role."""
    try:
        schema = RoleSchema()
        data = schema.load(request.json)
        
        result, status_code = RBACService.create_role(data)
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
            'message': 'Failed to create role',
            'error': str(e)
        }), 500

@rbac_bp.route('/roles/<int:role_id>', methods=['GET'])
@permission_required('role:read', 'role:manage')
def get_role(**kwargs):
    """Get role by ID."""
    try:
        role_id = kwargs.get('role_id')
        role = Role.query.get(role_id)
        
        if not role:
            return jsonify({
                'success': False,
                'message': 'Role not found'
            }), 404
        
        return jsonify({
            'success': True,
            'role': role.to_dict(include_permissions=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get role',
            'error': str(e)
        }), 500

@rbac_bp.route('/roles/<int:role_id>', methods=['PUT'])
@permission_required('role:update', 'role:manage')
def update_role(**kwargs):
    """Update role by ID."""
    try:
        role_id = kwargs.get('role_id')
        role = Role.query.get(role_id)
        
        if not role:
            return jsonify({
                'success': False,
                'message': 'Role not found'
            }), 404
        
        schema = RoleSchema(partial=True)
        data = schema.load(request.json)
        
        # Update role fields
        for field, value in data.items():
            if field == 'permission_ids':
                permissions = Permission.query.filter(Permission.id.in_(value)).all()
                role.permissions.clear()
                role.permissions.extend(permissions)
            else:
                setattr(role, field, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Role updated successfully',
            'role': role.to_dict(include_permissions=True)
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
            'message': 'Failed to update role',
            'error': str(e)
        }), 500

@rbac_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@permission_required('role:delete', 'role:manage')
def delete_role(**kwargs):
    """Delete role by ID."""
    try:
        role_id = kwargs.get('role_id')
        role = Role.query.get(role_id)
        
        if not role:
            return jsonify({
                'success': False,
                'message': 'Role not found'
            }), 404
        
        # Check if role is assigned to users
        if role.users:
            return jsonify({
                'success': False,
                'message': 'Cannot delete role that is assigned to users'
            }), 400
        
        db.session.delete(role)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Role deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete role',
            'error': str(e)
        }), 500

# Permission management endpoints
@rbac_bp.route('/permissions', methods=['GET'])
@permission_required('permission:read', 'permission:manage')
def get_permissions(**kwargs):
    """Get all permissions."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        resource = request.args.get('resource', '')
        action = request.args.get('action', '')
        
        query = Permission.query
        
        if search:
            query = query.filter(
                db.or_(
                    Permission.name.contains(search),
                    Permission.description.contains(search)
                )
            )
        
        if resource:
            query = query.filter(Permission.resource == resource)
        
        if action:
            query = query.filter(Permission.action == action)
        
        permissions = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'permissions': [permission.to_dict() for permission in permissions.items],
            'pagination': {
                'page': permissions.page,
                'pages': permissions.pages,
                'per_page': permissions.per_page,
                'total': permissions.total,
                'has_next': permissions.has_next,
                'has_prev': permissions.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get permissions',
            'error': str(e)
        }), 500

@rbac_bp.route('/permissions', methods=['POST'])
@permission_required('permission:create', 'permission:manage')
def create_permission(**kwargs):
    """Create a new permission."""
    try:
        schema = PermissionSchema()
        data = schema.load(request.json)
        
        result, status_code = RBACService.create_permission(data)
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
            'message': 'Failed to create permission',
            'error': str(e)
        }), 500

@rbac_bp.route('/permissions/<int:permission_id>', methods=['GET'])
@permission_required('permission:read', 'permission:manage')
def get_permission(**kwargs):
    """Get permission by ID."""
    try:
        permission_id = kwargs.get('permission_id')
        permission = Permission.query.get(permission_id)
        
        if not permission:
            return jsonify({
                'success': False,
                'message': 'Permission not found'
            }), 404
        
        return jsonify({
            'success': True,
            'permission': permission.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get permission',
            'error': str(e)
        }), 500

@rbac_bp.route('/permissions/<int:permission_id>', methods=['PUT'])
@permission_required('permission:update', 'permission:manage')
def update_permission(**kwargs):
    """Update permission by ID."""
    try:
        permission_id = kwargs.get('permission_id')
        permission = Permission.query.get(permission_id)
        
        if not permission:
            return jsonify({
                'success': False,
                'message': 'Permission not found'
            }), 404
        
        schema = PermissionSchema(partial=True)
        data = schema.load(request.json)
        
        # Update permission fields
        for field, value in data.items():
            setattr(permission, field, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Permission updated successfully',
            'permission': permission.to_dict()
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
            'message': 'Failed to update permission',
            'error': str(e)
        }), 500

@rbac_bp.route('/permissions/<int:permission_id>', methods=['DELETE'])
@permission_required('permission:delete', 'permission:manage')
def delete_permission(**kwargs):
    """Delete permission by ID."""
    try:
        permission_id = kwargs.get('permission_id')
        permission = Permission.query.get(permission_id)
        
        if not permission:
            return jsonify({
                'success': False,
                'message': 'Permission not found'
            }), 404
        
        # Check if permission is assigned to roles
        if permission.roles:
            return jsonify({
                'success': False,
                'message': 'Cannot delete permission that is assigned to roles'
            }), 400
        
        db.session.delete(permission)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Permission deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete permission',
            'error': str(e)
        }), 500

# User role assignment endpoints
@rbac_bp.route('/users/<int:user_id>/roles', methods=['GET'])
@permission_required('user:read', 'user:manage')
def get_user_roles(**kwargs):
    """Get roles for a user."""
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
            'user_id': user_id,
            'roles': [role.to_dict(include_permissions=True) for role in user.roles]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get user roles',
            'error': str(e)
        }), 500

@rbac_bp.route('/users/<int:user_id>/roles', methods=['POST'])
@permission_required('user:update', 'user:manage')
def assign_user_roles(**kwargs):
    """Assign roles to a user."""
    try:
        user_id = kwargs.get('user_id')
        schema = UserRoleAssignmentSchema()
        data = schema.load(request.json)
        
        # Override user_id from URL
        data['user_id'] = user_id
        
        result, status_code = RBACService.assign_roles_to_user(
            data['user_id'],
            data['role_ids']
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
            'message': 'Failed to assign user roles',
            'error': str(e)
        }), 500

@rbac_bp.route('/users/<int:user_id>/permissions', methods=['GET'])
@permission_required('user:read', 'user:manage')
def get_user_permissions(**kwargs):
    """Get all permissions for a user."""
    try:
        user_id = kwargs.get('user_id')
        result, status_code = RBACService.get_user_permissions(user_id)
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get user permissions',
            'error': str(e)
        }), 500

@rbac_bp.route('/users/<int:user_id>/permissions/<permission_name>/check', methods=['GET'])
@permission_required('user:read', 'user:manage')
def check_user_permission(**kwargs):
    """Check if user has a specific permission."""
    try:
        user_id = kwargs.get('user_id')
        permission_name = kwargs.get('permission_name')
        
        result, status_code = RBACService.check_user_permission(user_id, permission_name)
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to check user permission',
            'error': str(e)
        }), 500

# Utility endpoints
@rbac_bp.route('/resources', methods=['GET'])
@permission_required('permission:read', 'permission:manage')
def get_resources(**kwargs):
    """Get all unique resources from permissions."""
    try:
        resources = db.session.query(Permission.resource).distinct().all()
        resource_list = [r[0] for r in resources]
        
        return jsonify({
            'success': True,
            'resources': resource_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get resources',
            'error': str(e)
        }), 500

@rbac_bp.route('/actions', methods=['GET'])
@permission_required('permission:read', 'permission:manage')
def get_actions(**kwargs):
    """Get all unique actions from permissions."""
    try:
        actions = db.session.query(Permission.action).distinct().all()
        action_list = [a[0] for a in actions]
        
        return jsonify({
            'success': True,
            'actions': action_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get actions',
            'error': str(e)
        }), 500
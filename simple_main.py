from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from simple_config import config
from app.models import init_db
from app.models.auth import BlacklistedToken

# Import controllers
from app.controllers.auth_controller import auth_bp
from app.controllers.rbac_controller import rbac_bp

def create_simple_app(config_name=None):
    """Simplified application factory pattern without Redis dependencies."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db = init_db(app)
    
    # JWT Manager
    jwt = JWTManager(app)
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # JWT Configuration
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if token is blacklisted."""
        jti = jwt_payload['jti']
        token = BlacklistedToken.query.filter_by(jti=jti).first()
        return token is not None
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired token."""
        return jsonify({
            'success': False,
            'message': 'Token has expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid token."""
        return jsonify({
            'success': False,
            'message': 'Invalid token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing token."""
        return jsonify({
            'success': False,
            'message': 'Token is required'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Handle revoked token."""
        return jsonify({
            'success': False,
            'message': 'Token has been revoked'
        }), 401
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(rbac_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'success': True,
            'message': 'Authorization server is healthy',
            'version': '1.0.0'
        }), 200
    
    # API Info endpoint
    @app.route('/api/v1/info')
    def api_info():
        """API information endpoint."""
        return jsonify({
            'success': True,
            'api': {
                'name': 'Enterprise Authorization Server',
                'version': '1.0.0',
                'description': 'Enterprise-grade Flask API with JWT authentication and RBAC',
                'endpoints': {
                    'auth': '/api/v1/auth',
                    'rbac': '/api/v1/rbac'
                },
                'features': [
                    'JWT Authentication',
                    'Role-Based Access Control (RBAC)',
                    'User Management',
                    'Permission Management',
                    'Token Blacklisting',
                    'CORS Support',
                    'Password Security',
                    'API Versioning'
                ]
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'success': False,
            'message': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({
            'success': False,
            'message': 'Method not allowed'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    return app

if __name__ == '__main__':
    app = create_simple_app()
    print("Starting Enterprise Authorization Server (Simplified)...")
    app.run(debug=True, host='127.0.0.1', port=5001)
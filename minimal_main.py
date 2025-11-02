from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from datetime import timedelta
from dotenv import load_dotenv
from app.models import init_db
from app.models.auth import BlacklistedToken

# Import controllers
from app.controllers.auth_controller import auth_bp
from app.controllers.rbac_controller import rbac_bp

load_dotenv()

def create_minimal_app():
    """Minimal application without any Redis dependencies."""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql+psycopg://postgres:postgres@localhost:5432/flask')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT Configuration - Use same secret as main server
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-this-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    # Security
    app.config['BCRYPT_LOG_ROUNDS'] = 12
    app.config['PASSWORD_MIN_LENGTH'] = 8
    
    # CORS
    app.config['CORS_ORIGINS'] = ['http://localhost:3000']
    
    # Initialize extensions
    db = init_db(app)
    jwt = JWTManager(app)
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
    
    return app

if __name__ == '__main__':
    app = create_minimal_app()
    print("🚀 Starting Minimal Enterprise Authorization Server...")
    print("📍 Server will be available at: http://localhost:5001")
    print("🔐 Admin credentials: admin@example.com / Admin123!")
    app.run(debug=True, host='127.0.0.1', port=5001)
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
import os
from datetime import timedelta
from app.models import init_db
from app.models.auth import User

def create_debug_app():
    """Debug app to test JWT configuration."""
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/flask'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT Configuration - use same secret as main server
    app.config['JWT_SECRET_KEY'] = 'your-super-secret-jwt-key-change-this-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    db = init_db(app)
    jwt = JWTManager(app)
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token error: {error}")
        return jsonify({
            'success': False,
            'message': f'Invalid token: {error}'
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"Expired token: {jwt_payload}")
        return jsonify({
            'success': False,
            'message': 'Token has expired'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"Missing token: {error}")
        return jsonify({
            'success': False,
            'message': 'Token is required'
        }), 401
    
    @app.route('/debug-jwt')
    @jwt_required()
    def debug_jwt():
        try:
            user_id = get_jwt_identity()
            jwt_claims = get_jwt()
            user = User.query.get(user_id)
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'user_found': user is not None,
                'username': user.username if user else None,
                'jwt_claims': {
                    'jti': jwt_claims.get('jti'),
                    'exp': jwt_claims.get('exp'),
                    'type': jwt_claims.get('type')
                }
            })
        except Exception as e:
            import traceback
            print(f"Debug JWT error: {e}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_debug_app()
    print("🔍 Starting JWT Debug Server on port 5003...")
    app.run(debug=True, host='127.0.0.1', port=5003)
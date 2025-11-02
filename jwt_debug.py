from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
import os
from datetime import timedelta
from app.models import init_db
from app.models.auth import User

def create_jwt_test_app():
    """Test app to debug JWT issues."""
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/flask'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    db = init_db(app)
    jwt = JWTManager(app)
    
    @app.route('/test-jwt')
    @jwt_required()
    def test_jwt():
        """Simple JWT test endpoint."""
        try:
            user_id = get_jwt_identity()
            jwt_data = get_jwt()
            
            user = User.query.get(user_id)
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'username': user.username if user else 'Unknown',
                'jwt_data': {
                    'jti': jwt_data.get('jti'),
                    'exp': jwt_data.get('exp'),
                    'type': jwt_data.get('type')
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }), 500
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})
        
    return app

if __name__ == '__main__':
    app = create_jwt_test_app()
    print("🔍 Starting JWT Debug Server on port 5002...")
    app.run(debug=True, port=5002)
#!/bin/bash
# Docker Entrypoint Script for Enterprise Flask Authorization Server

set -e

echo "🚀 Starting Enterprise Flask Authorization Server..."
echo "📅 Build Date: ${BUILD_DATE:-unknown}"
echo "🏷️  Version: ${VERSION:-unknown}"
echo "🌍 Environment: ${FLASK_ENV:-production}"

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for PostgreSQL database..."
    
    # Extract database connection details from DATABASE_URL
    DB_HOST=$(python -c "
import os
from urllib.parse import urlparse
url = urlparse(os.getenv('DATABASE_URL', ''))
print(url.hostname or 'db')
")
    
    DB_PORT=$(python -c "
import os
from urllib.parse import urlparse
url = urlparse(os.getenv('DATABASE_URL', ''))
print(url.port or 5432)
")
    
    # Wait for database to be ready
    until nc -z "$DB_HOST" "$DB_PORT"; do
        echo "⏳ Database not ready yet, waiting 2 seconds..."
        sleep 2
    done
    
    echo "✅ Database is ready!"
}

# Function to wait for Redis (optional)
wait_for_redis() {
    if [ -n "$REDIS_URL" ]; then
        echo "⏳ Waiting for Redis..."
        
        REDIS_HOST=$(python -c "
import os
from urllib.parse import urlparse
url = urlparse(os.getenv('REDIS_URL', ''))
print(url.hostname or 'redis')
")
        
        REDIS_PORT=$(python -c "
import os
from urllib.parse import urlparse
url = urlparse(os.getenv('REDIS_URL', ''))
print(url.port or 6379)
")
        
        until nc -z "$REDIS_HOST" "$REDIS_PORT"; do
            echo "⏳ Redis not ready yet, waiting 2 seconds..."
            sleep 2
        done
        
        echo "✅ Redis is ready!"
    fi
}

# Function to initialize database
init_database() {
    echo "🗄️  Initializing database..."
    
    # Check if database tables exist using a simpler approach
    if python -c "
from minimal_main import create_minimal_app
from app.models.auth import User
app = create_minimal_app()
with app.app_context():
    try:
        User.query.first()
        print('EXISTS')
    except:
        print('MISSING')
" | grep -q "MISSING"; then
        echo "📋 Database tables not found, initializing..."
        python init_db.py
        echo "✅ Database initialized successfully!"
    else
        echo "✅ Database tables already exist"
    fi
}

# Function to run database migrations (if using Flask-Migrate)
run_migrations() {
    if [ -d "migrations" ]; then
        echo "🔄 Running database migrations..."
        python -c "
from flask_migrate import upgrade
from app import create_minimal_app
app = create_minimal_app()
with app.app_context():
    try:
        upgrade()
        print('✅ Migrations completed successfully!')
    except Exception as e:
        print(f'⚠️  Migration warning: {e}')
"
    fi
}

# Function to create required directories
create_directories() {
    echo "📁 Creating required directories..."
    mkdir -p /app/logs
    mkdir -p /app/uploads
    echo "✅ Directories created"
}

# Main execution
main() {
    # Create directories
    create_directories
    
    # Wait for dependencies
    wait_for_db
    wait_for_redis
    
    # Initialize database
    init_database
    
    # Run migrations
    run_migrations
    
    # Start the application
    echo "🚀 Starting Flask application..."
    
    if [ "$FLASK_ENV" = "development" ]; then
        echo "🔧 Starting in development mode..."
        exec python minimal_main.py
    else
        echo "🏭 Starting in production mode with Gunicorn..."
        exec gunicorn \
            --bind 0.0.0.0:5001 \
            --workers ${WORKERS:-4} \
            --worker-class gthread \
            --threads ${THREADS:-2} \
            --timeout ${TIMEOUT:-120} \
            --keep-alive ${KEEP_ALIVE:-5} \
            --max-requests ${MAX_REQUESTS:-1000} \
            --max-requests-jitter ${MAX_REQUESTS_JITTER:-100} \
            --access-logfile /app/logs/access.log \
            --error-logfile /app/logs/error.log \
            --log-level ${LOG_LEVEL:-info} \
            --capture-output \
            "minimal_main:create_minimal_app()"
    fi
}

# Execute main function
main "$@"
#!/bin/bash
# Test script for Docker deployment of Enterprise Flask Authorization Server

set -e

echo "🧪 Testing Docker Deployment of Enterprise Flask Authorization Server"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:5001"
TIMEOUT=10

# Helper functions
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Test functions
test_service_health() {
    print_status "Testing service health..."
    
    if curl -sf "$BASE_URL/health" --max-time $TIMEOUT > /dev/null; then
        print_success "Health check passed"
        return 0
    else
        print_error "Health check failed"
        return 1
    fi
}

test_database_connection() {
    print_status "Testing database connection..."
    
    if docker-compose exec -T db pg_isready -U flask_user -q; then
        print_success "Database connection OK"
        return 0
    else
        print_error "Database connection failed"
        return 1
    fi
}

test_redis_connection() {
    print_status "Testing Redis connection..."
    
    if docker-compose exec -T redis redis-cli -a secure_redis_password_change_in_production ping | grep -q "PONG"; then
        print_success "Redis connection OK"
        return 0
    else
        print_warning "Redis connection failed (may be optional)"
        return 1
    fi
}

test_user_registration() {
    print_status "Testing user registration..."
    
    local test_email="test$(date +%s)@example.com"
    local test_username="testuser$(date +%s)"
    
    local response=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$test_email\",
            \"username\": \"$test_username\",
            \"password\": \"TestPass123!\",
            \"first_name\": \"Test\",
            \"last_name\": \"User\"
        }" \
        --max-time $TIMEOUT)
    
    if echo "$response" | grep -q '"success": true' && echo "$response" | grep -q '"user":{'; then
        print_success "User registration successful"
        return 0
    else
        print_error "User registration failed: $response"
        return 1
    fi
}

test_admin_login() {
    print_status "Testing admin login..."
    
    local response=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@example.com",
            "password": "Admin123!"
        }' \
        --max-time $TIMEOUT)
    
    if echo "$response" | grep -q '"access_token"'; then
        print_success "Admin login successful"
        # Extract token for further tests
        ADMIN_TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        return 0
    else
        print_error "Admin login failed: $response"
        return 1
    fi
}

test_protected_endpoint() {
    print_status "Testing protected endpoint access..."
    
    if [ -z "$ADMIN_TOKEN" ]; then
        print_error "No admin token available for protected endpoint test"
        return 1
    fi
    
    local response=$(curl -s -X GET "$BASE_URL/api/v1/auth/me" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        --max-time $TIMEOUT)
    
    if echo "$response" | grep -q '"success": true' && echo "$response" | grep -q '"username": "admin"'; then
        print_success "Protected endpoint access successful"
        return 0
    else
        print_error "Protected endpoint access failed: $response"
        return 1
    fi
}

test_rbac_endpoints() {
    print_status "Testing RBAC endpoints..."
    
    if [ -z "$ADMIN_TOKEN" ]; then
        print_error "No admin token available for RBAC test"
        return 1
    fi
    
    # Test roles endpoint
    local roles_response=$(curl -s -X GET "$BASE_URL/api/v1/rbac/roles" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        --max-time $TIMEOUT)
    
    if echo "$roles_response" | grep -q '"success": true' || echo "$roles_response" | grep -q '"roles":\['; then
        print_success "RBAC roles endpoint accessible"
    else
        print_error "RBAC roles endpoint failed: $roles_response"
        return 1
    fi
    
    # Test permissions endpoint
    local permissions_response=$(curl -s -X GET "$BASE_URL/api/v1/rbac/permissions" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        --max-time $TIMEOUT)
    
    if echo "$permissions_response" | grep -q '"success": true' || echo "$permissions_response" | grep -q '"permissions":\['; then
        print_success "RBAC permissions endpoint accessible"
        return 0
    else
        print_error "RBAC permissions endpoint failed: $permissions_response"
        return 1
    fi
}

check_docker_services() {
    print_status "Checking Docker services status..."
    
    local services=$(docker-compose ps --services)
    local running_services=$(docker-compose ps --services --filter "status=running")
    
    echo "Services defined: $services"
    echo "Services running: $running_services"
    
    if docker-compose ps | grep -q "Up"; then
        print_success "Docker services are running"
        return 0
    else
        print_error "Some Docker services are not running"
        docker-compose ps
        return 1
    fi
}

display_service_logs() {
    print_status "Recent service logs:"
    echo "===================="
    docker-compose logs --tail=10 app
}

# Main test execution
main() {
    echo "Starting tests at $(date)"
    echo ""
    
    local failed_tests=0
    local total_tests=0
    
    # Check if Docker Compose services are running
    if ! check_docker_services; then
        print_error "Docker services not running. Please start with: docker-compose up -d"
        exit 1
    fi
    
    echo ""
    
    # Wait a moment for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 5
    
    # Run tests
    tests=(
        "test_service_health"
        "test_database_connection" 
        "test_redis_connection"
        "test_admin_login"
        "test_protected_endpoint"
        "test_rbac_endpoints"
        "test_user_registration"
    )
    
    for test in "${tests[@]}"; do
        echo ""
        ((total_tests++))
        if ! $test; then
            ((failed_tests++))
        fi
    done
    
    echo ""
    echo "=================================================================="
    echo "Test Results:"
    echo "Total tests: $total_tests"
    echo "Failed tests: $failed_tests"
    echo "Success rate: $(( (total_tests - failed_tests) * 100 / total_tests ))%"
    
    if [ $failed_tests -eq 0 ]; then
        print_success "🎉 All tests passed! Docker deployment is working correctly."
        exit 0
    else
        print_error "❌ $failed_tests test(s) failed. Check the logs above for details."
        echo ""
        display_service_logs
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "health")
        test_service_health
        ;;
    "login")
        test_admin_login
        ;;
    "register")
        test_user_registration
        ;;
    "rbac")
        test_admin_login && test_rbac_endpoints
        ;;
    "logs")
        display_service_logs
        ;;
    *)
        main
        ;;
esac
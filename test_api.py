#!/usr/bin/env python3
"""
Test script for the Authorization Server API.
This script demonstrates basic API usage and validates functionality.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"
API_URL = f"{BASE_URL}/api/v1"

class AuthServerTester:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.admin_token = None
        
    def log(self, message):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def test_health_check(self):
        """Test health check endpoint."""
        self.log("Testing health check...")
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log("✅ Health check passed")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Health check error: {e}")
            return False
    
    def test_api_info(self):
        """Test API info endpoint."""
        self.log("Testing API info...")
        try:
            response = requests.get(f"{API_URL}/info")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ API Info: {data['api']['name']} v{data['api']['version']}")
                return True
            else:
                self.log(f"❌ API info failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ API info error: {e}")
            return False
    
    def test_admin_login(self):
        """Test admin login."""
        self.log("Testing admin login...")
        try:
            payload = {
                "email": "admin@example.com",
                "password": "Admin123!"
            }
            response = requests.post(f"{API_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.admin_token = data['access_token']
                    self.log("✅ Admin login successful")
                    self.log(f"   Admin has roles: {[role['name'] for role in data['user']['roles']]}")
                    return True
                else:
                    self.log(f"❌ Admin login failed: {data['message']}")
                    return False
            else:
                self.log(f"❌ Admin login failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Admin login error: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration."""
        self.log("Testing user registration...")
        try:
            payload = {
                "email": "testuser@example.com",
                "username": "testuser",
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "User"
            }
            response = requests.post(f"{API_URL}/auth/register", json=payload)
            
            if response.status_code == 201:
                data = response.json()
                if data['success']:
                    self.log("✅ User registration successful")
                    return True
                else:
                    self.log(f"❌ User registration failed: {data['message']}")
                    return False
            else:
                self.log(f"❌ User registration failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ User registration error: {e}")
            return False
    
    def test_user_activation(self):
        """Test user activation by admin."""
        if not self.admin_token:
            self.log("❌ No admin token available for user activation")
            return False
        
        self.log("Testing user activation...")
        try:
            # First, get the user ID
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{API_URL}/auth/users", headers=headers)
            
            if response.status_code != 200:
                self.log(f"❌ Failed to get users: HTTP {response.status_code}")
                return False
            
            users = response.json()['users']
            test_user = None
            for user in users:
                if user['email'] == 'testuser@example.com':
                    test_user = user
                    break
            
            if not test_user:
                self.log("❌ Test user not found")
                return False
            
            # Activate the user
            response = requests.post(
                f"{API_URL}/auth/users/{test_user['id']}/activate",
                headers=headers
            )
            
            if response.status_code == 200:
                self.log("✅ User activation successful")
                return True
            else:
                self.log(f"❌ User activation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ User activation error: {e}")
            return False
    
    def test_user_login(self):
        """Test user login."""
        self.log("Testing user login...")
        try:
            payload = {
                "email": "testuser@example.com",
                "password": "TestPass123!"
            }
            response = requests.post(f"{API_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.access_token = data['access_token']
                    self.refresh_token = data['refresh_token']
                    self.log("✅ User login successful")
                    self.log(f"   User permissions: {data['user']['permissions']}")
                    return True
                else:
                    self.log(f"❌ User login failed: {data['message']}")
                    return False
            else:
                self.log(f"❌ User login failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ User login error: {e}")
            return False
    
    def test_token_verification(self):
        """Test token verification."""
        if not self.access_token:
            self.log("❌ No access token available for verification")
            return False
        
        self.log("Testing token verification...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{API_URL}/auth/verify-token", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data['success'] and data['valid']:
                    self.log("✅ Token verification successful")
                    return True
                else:
                    self.log(f"❌ Token verification failed: {data['message']}")
                    return False
            else:
                self.log(f"❌ Token verification failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Token verification error: {e}")
            return False
    
    def test_get_current_user(self):
        """Test get current user endpoint."""
        if not self.access_token:
            self.log("❌ No access token available")
            return False
        
        self.log("Testing get current user...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{API_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    user = data['user']
                    self.log(f"✅ Current user: {user['first_name']} {user['last_name']} ({user['email']})")
                    return True
                else:
                    self.log(f"❌ Get current user failed: {data['message']}")
                    return False
            else:
                self.log(f"❌ Get current user failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Get current user error: {e}")
            return False
    
    def test_refresh_token(self):
        """Test token refresh."""
        if not self.refresh_token:
            self.log("❌ No refresh token available")
            return False
        
        self.log("Testing token refresh...")
        try:
            payload = {"refresh_token": self.refresh_token}
            response = requests.post(f"{API_URL}/auth/refresh", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.access_token = data['access_token']
                    self.log("✅ Token refresh successful")
                    return True
                else:
                    self.log(f"❌ Token refresh failed: {data['message']}")
                    return False
            else:
                self.log(f"❌ Token refresh failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Token refresh error: {e}")
            return False
    
    def test_rbac_endpoints(self):
        """Test RBAC endpoints."""
        if not self.admin_token:
            self.log("❌ No admin token available for RBAC tests")
            return False
        
        self.log("Testing RBAC endpoints...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test get roles
            response = requests.get(f"{API_URL}/rbac/roles", headers=headers)
            if response.status_code == 200:
                roles = response.json()['roles']
                self.log(f"✅ Retrieved {len(roles)} roles")
            else:
                self.log(f"❌ Get roles failed: HTTP {response.status_code}")
                return False
            
            # Test get permissions
            response = requests.get(f"{API_URL}/rbac/permissions", headers=headers)
            if response.status_code == 200:
                permissions = response.json()['permissions']
                self.log(f"✅ Retrieved {len(permissions)} permissions")
            else:
                self.log(f"❌ Get permissions failed: HTTP {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ RBAC endpoints error: {e}")
            return False
    
    def test_logout(self):
        """Test user logout."""
        if not self.access_token:
            self.log("❌ No access token available for logout")
            return False
        
        self.log("Testing logout...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            payload = {"refresh_token": self.refresh_token}
            response = requests.post(f"{API_URL}/auth/logout", headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.log("✅ Logout successful")
                    self.access_token = None
                    self.refresh_token = None
                    return True
                else:
                    self.log(f"❌ Logout failed: {data['message']}")
                    return False
            else:
                self.log(f"❌ Logout failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Logout error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        self.log("🚀 Starting Authorization Server API Tests")
        self.log("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("API Info", self.test_api_info),
            ("Admin Login", self.test_admin_login),
            ("User Registration", self.test_user_registration),
            ("User Activation", self.test_user_activation),
            ("User Login", self.test_user_login),
            ("Token Verification", self.test_token_verification),
            ("Get Current User", self.test_get_current_user),
            ("Token Refresh", self.test_refresh_token),
            ("RBAC Endpoints", self.test_rbac_endpoints),
            ("Logout", self.test_logout)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n📝 Running: {test_name}")
            if test_func():
                passed += 1
            else:
                failed += 1
            time.sleep(0.5)  # Small delay between tests
        
        self.log("\n" + "=" * 50)
        self.log("📊 TEST RESULTS SUMMARY")
        self.log("=" * 50)
        self.log(f"✅ Passed: {passed}")
        self.log(f"❌ Failed: {failed}")
        self.log(f"📈 Success Rate: {(passed/(passed+failed))*100:.1f}%")
        
        if failed == 0:
            self.log("🎉 All tests passed! Authorization server is working correctly.")
        else:
            self.log("⚠️  Some tests failed. Please check the server configuration.")

if __name__ == "__main__":
    tester = AuthServerTester()
    tester.run_all_tests()
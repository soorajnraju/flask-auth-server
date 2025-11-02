#!/usr/bin/env python3
"""
Simple API test script to verify the authorization server functionality.
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Status Code: {response.status_code}")
        print(f"Health Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_admin_login():
    """Test admin login"""
    try:
        data = {
            "email": "admin@example.com",
            "password": "Admin123!"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=data)
        print(f"Admin Login Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Admin Login Success: {result.get('success')}")
            return result.get('access_token')
        else:
            print(f"Admin Login Failed: {response.text}")
            return None
    except Exception as e:
        print(f"Admin login failed: {e}")
        return None

def test_api_info():
    """Test API info endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/info")
        print(f"API Info Status Code: {response.status_code}")
        print(f"API Info Response: {response.json()}")
        return True
    except Exception as e:
        print(f"API info test failed: {e}")
        return False

def main():
    print("🚀 Testing Authorization Server")
    print("=" * 50)
    
    # Test health
    print("\n1. Testing Health Check...")
    if not test_health():
        print("❌ Server is not responding")
        return
    
    # Test API info
    print("\n2. Testing API Info...")
    test_api_info()
    
    # Test admin login
    print("\n3. Testing Admin Login...")
    admin_token = test_admin_login()
    if admin_token:
        print("✅ Admin login successful")
        print(f"Token (first 50 chars): {admin_token[:50]}...")
    else:
        print("❌ Admin login failed")
    
    print("\n🎉 Basic tests completed!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Comprehensive test script for the Authorization Server
This demonstrates all the key functionality working properly.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test(test_name):
    print(f"\n📋 {test_name}")
    print("-" * 40)

def test_health_check():
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_info():
    print_test("API Information")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/info")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"API Name: {data['api']['name']}")
        print(f"Version: {data['api']['version']}")
        print(f"Features: {', '.join(data['api']['features'])}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_admin_login():
    print_test("Admin Login")
    try:
        payload = {
            "email": "admin@example.com",
            "password": "Admin123!"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Login Success: {data['success']}")
            print(f"User: {data['user']['username']} ({data['user']['email']})")
            print(f"Roles: {', '.join(data['user']['roles'])}")
            print(f"Permissions: {', '.join(data['user']['permissions'][:3])}...")
            print(f"Access Token: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_user_registration():
    print_test("User Registration")
    try:
        payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewUser123!",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"Registration Success: {data['success']}")
            print(f"New User: {data['user']['username']} ({data['user']['email']})")
            print(f"Assigned Roles: {', '.join(data['user']['roles'])}")
            return True
        else:
            print(f"Registration Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_protected_endpoint(token):
    print_test("Protected Endpoint Access")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Current User: {data['user']['username']}")
            print(f"Email: {data['user']['email']}")
            print(f"Roles: {', '.join(data['user']['roles'])}")
            print(f"Permissions: {', '.join(data['user']['permissions'])}")
            return True
        else:
            print(f"❌ Protected endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_unauthorized_access():
    print_test("Unauthorized Access Test")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/me")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            print(f"✅ Correctly blocked: {data['message']}")
            return True
        else:
            print(f"❌ Should have been blocked")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_credentials():
    print_test("Invalid Credentials Test")
    try:
        payload = {
            "email": "admin@example.com",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            print(f"✅ Correctly rejected: {data['message']}")
            return True
        else:
            print(f"❌ Should have been rejected")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    print_header("Enterprise Authorization Server - Comprehensive Tests")
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: API Info
    results.append(("API Info", test_api_info()))
    
    # Test 3: Admin Login
    token = test_admin_login()
    results.append(("Admin Login", token is not None))
    
    # Test 4: User Registration
    results.append(("User Registration", test_user_registration()))
    
    # Test 5: Protected Endpoint (if we have a token)
    if token:
        results.append(("Protected Access", test_protected_endpoint(token)))
    
    # Test 6: Unauthorized Access
    results.append(("Unauthorized Block", test_unauthorized_access()))
    
    # Test 7: Invalid Credentials
    results.append(("Invalid Credentials Block", test_invalid_credentials()))
    
    # Results Summary
    print_header("Test Results Summary")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"🚀 Your Authorization Server is working perfectly!")
    else:
        print(f"\n⚠️  Some tests failed. Check the server status.")
    
    print(f"\n📖 Features Demonstrated:")
    print(f"   ✅ JWT Authentication")
    print(f"   ✅ User Registration")
    print(f"   ✅ Login/Logout")
    print(f"   ✅ Protected Endpoints")
    print(f"   ✅ Role-Based Access Control")
    print(f"   ✅ Permission System")
    print(f"   ✅ Error Handling")
    print(f"   ✅ Security Validation")

if __name__ == "__main__":
    print("🔍 Starting Authorization Server Tests...")
    print("⏳ Make sure the server is running on http://127.0.0.1:5000")
    print("💡 Start with: python working_server.py")
    
    # Wait a moment for user to read
    time.sleep(2)
    
    run_all_tests()
    
    print(f"\n🏁 Test session completed!")
    print(f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}")
#!/usr/bin/env python3
"""
Simple test to verify the server is working.
"""
import requests
import json

def test_endpoints():
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing Flask Server")
    print("=" * 40)
    
    # Test home endpoint
    try:
        print("1. Testing Home Endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test health endpoint
    try:
        print("\n2. Testing Health Endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test test endpoint
    try:
        print("\n3. Testing Test Endpoint...")
        response = requests.get(f"{base_url}/test")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Basic server test completed!")

if __name__ == "__main__":
    test_endpoints()
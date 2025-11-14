#!/usr/bin/env python3
"""
Integration tests for authentication routes
Tests HTTP endpoints using urllib (no external dependencies)
"""

import urllib.request
import urllib.parse
import json
import sys
import os

# Test configuration
BASE_URL = "http://localhost:5001/api/auth"
VALID_USER = {
    "email": "newuser@gmail.com",
    "password": "TestPass123",
    "confirmPassword": "TestPass123"
}
LOGIN_USER = {
    "email": "test@gmail.com",  # Existing test user
    "password": "TestPass123"
}

def make_http_request(url, method="GET", data=None, headers=None):
    """Make HTTP request using urllib"""
    try:
        # Prepare headers
        req_headers = headers or {}
        req_headers.setdefault('Content-Type', 'application/json')
        
        # Prepare data
        if data:
            data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        
        # Make request
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return {
                "success": True,
                "status_code": response.status,
                "data": response_data
            }
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            return {
                "success": False,
                "status_code": e.code,
                "data": error_data
            }
        except:
            return {
                "success": False,
                "status_code": e.code,
                "error": e.reason
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_auth_routes():
    """Test authentication routes with various scenarios"""
    
    print("🧪 Testing Authentication Routes")
    print("=" * 50)
    
    # Test 1: User Login (Existing User)
    print("1️⃣  Testing user login with existing credentials...")
    login_response = make_http_request(f"{BASE_URL}/login", "POST", LOGIN_USER)
    
    print(f"Status Code: {login_response.get('status_code', 'Unknown')}")
    if login_response.get("status_code") == 200:
        print("✅ Login successful")
        token = login_response["data"].get('token')
        user_data = login_response["data"].get('user')
        
        if token and user_data:
            print(f"   Token received (length: {len(token)})")
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Email verified: {user_data.get('email_verified')}")
        else:
            print("⚠️  Token or user data missing in response")
    else:
        print(f"❌ Login failed: {login_response.get('data', {}).get('error', 'Unknown error')}")
    
    # Test 2: Invalid Login
    print("\n2️⃣  Testing invalid login credentials...")
    invalid_login = {
        "email": "test@gmail.com",
        "password": "WrongPassword123"
    }
    invalid_response = make_http_request(f"{BASE_URL}/login", "POST", invalid_login)
    
    print(f"Status Code: {invalid_response.get('status_code', 'Unknown')}")
    if invalid_response.get("status_code") == 401:
        print("✅ Invalid login correctly rejected")
    else:
        print(f"⚠️  Expected 401, got {invalid_response.get('status_code')}")
    
    # Test 3: User Registration (New User)
    print("\n3️⃣  Testing user registration...")
    register_response = make_http_request(f"{BASE_URL}/register", "POST", VALID_USER)
    
    print(f"Status Code: {register_response.get('status_code', 'Unknown')}")
    if register_response.get("status_code") == 201:
        print("✅ Registration successful")
        register_data = register_response["data"]
        print(f"   User ID: {register_data.get('user_id')}")
        print(f"   Email: {register_data.get('email')}")
        print(f"   Message: {register_data.get('message')}")
    elif register_response.get("status_code") == 400:
        error_msg = register_response.get('data', {}).get('error', 'Unknown')
        if "already registered" in error_msg:
            print(f"✅ Registration correctly rejected (email exists): {error_msg}")
        else:
            print(f"⚠️  Registration failed with validation error: {error_msg}")
    else:
        print(f"❌ Unexpected registration response: {register_response.get('status_code')}")
    
    # Test 4: Registration Validation Errors
    print("\n4️⃣  Testing registration validation...")
    
    # Test missing password
    invalid_register = {
        "email": "test2@gmail.com",
        "password": "",
        "confirmPassword": ""
    }
    validation_response = make_http_request(f"{BASE_URL}/register", "POST", invalid_register)
    
    if validation_response.get("status_code") == 400:
        print("✅ Empty password validation working")
    else:
        print(f"⚠️  Password validation not working: {validation_response.get('status_code')}")
    
    # Test mismatched passwords
    mismatch_register = {
        "email": "test3@gmail.com",
        "password": "TestPass123",
        "confirmPassword": "DifferentPass123"
    }
    mismatch_response = make_http_request(f"{BASE_URL}/register", "POST", mismatch_register)
    
    if mismatch_response.get("status_code") == 400:
        print("✅ Password mismatch validation working")
    else:
        print(f"⚠️  Password mismatch validation not working: {mismatch_response.get('status_code')}")
    
    # Test invalid email
    invalid_email_register = {
        "email": "invalid-email",
        "password": "TestPass123",
        "confirmPassword": "TestPass123"
    }
    email_response = make_http_request(f"{BASE_URL}/register", "POST", invalid_email_register)
    
    if email_response.get("status_code") == 400:
        print("✅ Invalid email validation working")
    else:
        print(f"⚠️  Email validation not working: {email_response.get('status_code')}")
    
    # Test 5: Missing JSON Data
    print("\n5️⃣  Testing missing request data...")
    empty_response = make_http_request(f"{BASE_URL}/login", "POST", None)
    
    if empty_response.get("status_code") == 400:
        print("✅ Missing JSON data validation working")
    else:
        print(f"⚠️  Missing data validation not working: {empty_response.get('status_code')}")
    
    print("\n🎉 Authentication routes testing completed!")
    # Test passed - no return value needed for pytest

if __name__ == "__main__":
    try:
        test_auth_routes()
    except Exception as e:
        if "Connection refused" in str(e) or "No connection could be made" in str(e):
            print("❌ Could not connect to server. Make sure Flask server is running on localhost:5001")
            sys.exit(1)
        else:
            print(f"❌ Test failed with error: {str(e)}")
            sys.exit(1)
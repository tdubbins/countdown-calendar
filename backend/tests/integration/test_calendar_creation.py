#!/usr/bin/env python3
"""
Test script for calendar creation endpoint
Run this after starting the Flask server to test calendar creation functionality
Uses built-in urllib instead of external requests library
"""

import urllib.request
import urllib.parse
import json
import sys

# Test configuration
BASE_URL = "http://localhost:5001/api"
TEST_USER = {
    "email": "test@gmail.com", 
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

def test_calendar_creation():
    """Test the calendar creation endpoint with various scenarios"""
    
    print("🧪 Testing Calendar Creation Endpoint")
    print("=" * 50)
    
    # Step 1: Login to get JWT token
    print("1️⃣  Logging in to get authentication token...")
    login_response = make_http_request(f"{BASE_URL}/auth/login", "POST", TEST_USER)
    
    if not login_response["success"] or login_response["status_code"] != 200:
        print(f"❌ Login failed: {login_response.get('status_code', 'Unknown')}")
        print(f"Response: {login_response.get('data', login_response.get('error', 'Unknown error'))}")
        return False
    
    token = login_response["data"].get('token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print("✅ Login successful, token obtained")
    
    # Step 2: Test valid calendar creation
    print("\n2️⃣  Testing valid calendar creation...")
    valid_calendar = {
        "title": "Christmas Countdown 2025",
        "startDate": "2025-12-01", 
        "duration": 25
    }
    
    create_response = make_http_request(f"{BASE_URL}/calendars", "POST", valid_calendar, headers)
    
    print(f"Status Code: {create_response.get('status_code', 'Unknown')}")
    print(f"Response: {json.dumps(create_response.get('data', {}), indent=2)}")
    
    if create_response.get("status_code") == 201:
        print("✅ Valid calendar creation successful")
        created_calendar = create_response["data"].get('calendar', {})
        calendar_id = created_calendar.get('id')
        share_token = created_calendar.get('shareToken')
        
        # Validate response structure
        required_fields = ['id', 'title', 'startDate', 'duration', 'endDate', 'shareToken']
        missing_fields = [field for field in required_fields if field not in created_calendar]
        
        if missing_fields:
            print(f"⚠️  Missing fields in response: {missing_fields}")
        else:
            print("✅ All required fields present in response")
            
        # Check calculated fields
        expected_end_date = "2025-12-25"
        if created_calendar.get('endDate') == expected_end_date:
            print("✅ End date calculated correctly")
        else:
            print(f"⚠️  End date incorrect. Expected: {expected_end_date}, Got: {created_calendar.get('endDate')}")
    else:
        print("❌ Valid calendar creation failed")
        return False
    
    # Step 3: Test calendar listing
    print("\n3️⃣  Testing calendar listing...")
    list_response = make_http_request(f"{BASE_URL}/calendars", "GET", None, headers)
    
    print(f"Status Code: {list_response.get('status_code', 'Unknown')}")
    if list_response.get("status_code") == 200:
        calendars = list_response["data"].get('calendars', [])
        print(f"✅ Calendar listing successful - Found {len(calendars)} calendar(s)")
        if len(calendars) > 0:
            print(f"First calendar: {calendars[0].get('title', 'No title')}")
    else:
        print("❌ Calendar listing failed")
    
    # Step 4: Test validation errors
    print("\n4️⃣  Testing validation errors...")
    
    # Test missing title
    invalid_calendar_1 = {
        "startDate": "2025-12-01",
        "duration": 25
    }
    
    error_response_1 = make_http_request(f"{BASE_URL}/calendars", "POST", invalid_calendar_1, headers)
    
    if error_response_1.get("status_code") == 400:
        print("✅ Missing title validation working")
    else:
        print(f"⚠️  Missing title validation not working: {error_response_1.get('status_code')}")
    
    # Test invalid duration
    invalid_calendar_2 = {
        "title": "Test Calendar",
        "startDate": "2025-12-01",
        "duration": 50  # Invalid: > 31
    }
    
    error_response_2 = make_http_request(f"{BASE_URL}/calendars", "POST", invalid_calendar_2, headers)
    
    if error_response_2.get("status_code") == 400:
        print("✅ Invalid duration validation working")
    else:
        print(f"⚠️  Invalid duration validation not working: {error_response_2.get('status_code')}")
    
    # Test invalid date format
    invalid_calendar_3 = {
        "title": "Test Calendar",
        "startDate": "12/01/2025",  # Invalid format
        "duration": 25
    }
    
    error_response_3 = make_http_request(f"{BASE_URL}/calendars", "POST", invalid_calendar_3, headers)
    
    if error_response_3.get("status_code") == 400:
        print("✅ Invalid date format validation working")
    else:
        print(f"⚠️  Invalid date format validation not working: {error_response_3.get('status_code')}")
    
    print("\n🎉 Calendar creation endpoint testing completed!")
    return True

if __name__ == "__main__":
    try:
        test_calendar_creation()
    except Exception as e:
        if "Connection refused" in str(e) or "No connection could be made" in str(e):
            print("❌ Could not connect to server. Make sure Flask server is running on localhost:5001")
            sys.exit(1)
        else:
            print(f"❌ Test failed with error: {str(e)}")
            sys.exit(1)
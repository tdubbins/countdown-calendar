#!/usr/bin/env python3
"""
Test script for calendar creation endpoint
Run this after starting the Flask server to test calendar creation functionality
"""

import requests
import json
import sys

# Test configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER = {
    "email": "test@gmail.com", 
    "password": "TestPass123"
}

def test_calendar_creation():
    """Test the calendar creation endpoint with various scenarios"""
    
    print("🧪 Testing Calendar Creation Endpoint")
    print("=" * 50)
    
    # Step 1: Login to get JWT token
    print("1️⃣  Logging in to get authentication token...")
    login_response = requests.post(f"{BASE_URL}/auth/login", 
                                   json=TEST_USER,
                                   headers={'Content-Type': 'application/json'})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token = login_response.json().get('token')
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
    
    create_response = requests.post(f"{BASE_URL}/calendars",
                                    json=valid_calendar,
                                    headers=headers)
    
    print(f"Status Code: {create_response.status_code}")
    print(f"Response: {json.dumps(create_response.json(), indent=2)}")
    
    if create_response.status_code == 201:
        print("✅ Valid calendar creation successful")
        created_calendar = create_response.json().get('calendar', {})
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
    list_response = requests.get(f"{BASE_URL}/calendars", headers=headers)
    
    print(f"Status Code: {list_response.status_code}")
    if list_response.status_code == 200:
        calendars = list_response.json().get('calendars', [])
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
    
    error_response_1 = requests.post(f"{BASE_URL}/calendars",
                                     json=invalid_calendar_1,
                                     headers=headers)
    
    if error_response_1.status_code == 400:
        print("✅ Missing title validation working")
    else:
        print(f"⚠️  Missing title validation not working: {error_response_1.status_code}")
    
    # Test invalid duration
    invalid_calendar_2 = {
        "title": "Test Calendar",
        "startDate": "2025-12-01",
        "duration": 50  # Invalid: > 31
    }
    
    error_response_2 = requests.post(f"{BASE_URL}/calendars",
                                     json=invalid_calendar_2,
                                     headers=headers)
    
    if error_response_2.status_code == 400:
        print("✅ Invalid duration validation working")
    else:
        print(f"⚠️  Invalid duration validation not working: {error_response_2.status_code}")
    
    # Test invalid date format
    invalid_calendar_3 = {
        "title": "Test Calendar",
        "startDate": "12/01/2025",  # Invalid format
        "duration": 25
    }
    
    error_response_3 = requests.post(f"{BASE_URL}/calendars",
                                     json=invalid_calendar_3,
                                     headers=headers)
    
    if error_response_3.status_code == 400:
        print("✅ Invalid date format validation working")
    else:
        print(f"⚠️  Invalid date format validation not working: {error_response_3.status_code}")
    
    print("\n🎉 Calendar creation endpoint testing completed!")
    return True

if __name__ == "__main__":
    try:
        test_calendar_creation()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Flask server is running on localhost:5000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        sys.exit(1)
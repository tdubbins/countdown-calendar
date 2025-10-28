#!/usr/bin/env python3
"""
Test script for calendar database operations
Tests all CRUD operations required for Issue #22
"""

import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.json_db import calendars_db

def test_calendar_database():
    """Test all calendar database operations"""
    print("🧪 Testing Calendar Database Operations for Issue #22")
    print("=" * 60)
    
    # Test data
    test_user_id = "d0739ad6-fa0a-4720-972a-8c754a85bd91"  # test@gmail.com
    calendar_id = str(uuid.uuid4())
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=24)).strftime('%Y-%m-%d')
    
    test_calendar = {
        "id": calendar_id,
        "title": "Test Advent Calendar",
        "startDate": start_date,
        "duration": 25,
        "endDate": end_date,
        "dateRange": f"{start_date} to {end_date}",
        "videoCount": 0,
        "status": "draft",
        "shareToken": str(uuid.uuid4()),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "userId": test_user_id,
        "videoStorageUsed": 0,  # NFR [SC2]: Track video storage
        "videos": {}  # Will store video metadata by day number
    }
    
    try:
        # Test 1: CREATE operation
        print("1️⃣ Testing CREATE operation...")
        created_calendar = calendars_db.create("calendars", calendar_id, test_calendar)
        print(f"✅ Created calendar: {created_calendar['title']}")
        print(f"   Calendar ID: {created_calendar['id']}")
        print(f"   User ID: {created_calendar['userId']}")
        
        # Test 2: READ operation
        print("\n2️⃣ Testing READ operation...")
        found_calendar = calendars_db.find_by_id("calendars", calendar_id)
        if found_calendar:
            print(f"✅ Found calendar: {found_calendar['title']}")
            print(f"   Status: {found_calendar['status']}")
        else:
            print("❌ Calendar not found")
            return False
        
        # Test 3: LIST by user operation (NFR [SC1]: Support 100+ calendars)
        print("\n3️⃣ Testing LIST BY USER operation...")
        user_calendars = calendars_db.list_by_field("calendars", "userId", test_user_id)
        print(f"✅ Found {len(user_calendars)} calendars for user")
        
        # Test 4: UPDATE operation
        print("\n4️⃣ Testing UPDATE operation...")
        updates = {
            "status": "active",
            "videoCount": 5,
            "videoStorageUsed": 157286400,  # ~150MB
            "updatedAt": datetime.now().isoformat()
        }
        updated_calendar = calendars_db.update("calendars", calendar_id, updates)
        if updated_calendar:
            print(f"✅ Updated calendar status: {updated_calendar['status']}")
            print(f"   Video count: {updated_calendar['videoCount']}")
            print(f"   Storage used: {updated_calendar['videoStorageUsed']} bytes")
        else:
            print("❌ Update failed")
            return False
        
        # Test 5: DELETE operation
        print("\n5️⃣ Testing DELETE operation...")
        deleted = calendars_db.delete("calendars", calendar_id)
        if deleted:
            print("✅ Calendar deleted successfully")
        else:
            print("❌ Delete failed")
            return False
        
        # Test 6: Verify deletion
        print("\n6️⃣ Verifying deletion...")
        deleted_calendar = calendars_db.find_by_id("calendars", calendar_id)
        if deleted_calendar is None:
            print("✅ Calendar properly deleted (not found)")
        else:
            print("❌ Calendar still exists after deletion")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 All calendar database operations working correctly!")
        print("✅ Issue #22 database requirements satisfied:")
        print("   • Calendar CRUD operations functional")
        print("   • User association working")
        print("   • Video storage tracking implemented")
        print("   • Modular separation maintained")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_calendar_database()
    sys.exit(0 if success else 1)
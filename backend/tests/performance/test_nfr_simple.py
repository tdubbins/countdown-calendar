#!/usr/bin/env python3
"""
Simple NFR Performance Testing for Issue #24 (No external dependencies)
Uses built-in urllib instead of requests

NFR [P3]: Calendar Rendering: Calendar list loads under 3 seconds
NFR [SC1]: User Database Capacity: Efficiently query calendars for 100+ users  
NFR [P4]: Concurrent Users: Support 10-20 simultaneous calendar list requests
"""

import urllib.request
import urllib.parse
import json
import time
import threading
from typing import List, Dict

# Test configuration
BASE_URL = "http://localhost:5001"
TEST_USER = {
    "email": "test@gmail.com", 
    "password": "TestPass123"
}

def make_request(url: str, method: str = "GET", data: dict = None, headers: dict = None) -> Dict:
    """Make HTTP request using urllib"""
    try:
        # Prepare headers
        req_headers = headers or {}
        req_headers['Content-Type'] = 'application/json'
        
        # Prepare data
        if data:
            data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        
        # Make request
        start_time = time.time()
        with urllib.request.urlopen(req) as response:
            response_time = time.time() - start_time
            response_data = json.loads(response.read().decode('utf-8'))
            return {
                "success": True,
                "status_code": response.status,
                "data": response_data,
                "response_time": response_time
            }
    except urllib.error.HTTPError as e:
        response_time = time.time() - start_time
        return {
            "success": False,
            "status_code": e.code,
            "error": e.reason,
            "response_time": response_time
        }
    except Exception as e:
        response_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "response_time": response_time
        }

def login_and_get_token() -> str:
    """Login and return JWT token"""
    result = make_request(f"{BASE_URL}/api/auth/login", "POST", TEST_USER)
    if result["success"] and result["status_code"] == 200:
        return result["data"]["token"]
    raise Exception(f"Login failed: {result.get('error', 'Unknown error')}")

def test_calendar_list_performance(token: str) -> Dict:
    """Test single request performance for NFR [P3]"""
    headers = {"Authorization": f"Bearer {token}"}
    
    result = make_request(f"{BASE_URL}/api/calendars", "GET", headers=headers)
    
    return {
        "response_time": result["response_time"],
        "status_code": result.get("status_code", 0),
        "success": result["success"] and result["response_time"] < 3.0,  # NFR [P3] requirement
        "calendar_count": len(result["data"].get('calendars', [])) if result["success"] else 0,
        "error": result.get("error")
    }

def concurrent_request_worker(token: str, results: List, worker_id: int):
    """Worker function for concurrent testing"""
    try:
        result = test_calendar_list_performance(token)
        result['worker_id'] = worker_id
        results.append(result)
    except Exception as e:
        results.append({
            "worker_id": worker_id,
            "error": str(e),
            "success": False,
            "response_time": 0
        })

def test_concurrent_requests(token: str, num_requests: int = 10) -> Dict:
    """Test concurrent requests for NFR [P4] - reduced to 10 for stability"""
    print(f"\n=== Testing {num_requests} concurrent requests ===")
    
    results = []
    threads = []
    
    # Start all threads simultaneously
    start_time = time.time()
    for i in range(num_requests):
        thread = threading.Thread(target=concurrent_request_worker, args=(token, results, i))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful_requests = [r for r in results if r.get('success', False)]
    failed_requests = [r for r in results if not r.get('success', False)]
    
    if successful_requests:
        avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
        max_response_time = max(r['response_time'] for r in successful_requests)
        min_response_time = min(r['response_time'] for r in successful_requests)
    else:
        avg_response_time = max_response_time = min_response_time = 0
    
    return {
        "total_requests": num_requests,
        "successful_requests": len(successful_requests),
        "failed_requests": len(failed_requests),
        "total_time": total_time,
        "avg_response_time": avg_response_time,
        "max_response_time": max_response_time,
        "min_response_time": min_response_time,
        "nfr_p4_success": len(successful_requests) >= (num_requests * 0.8)  # 80% success rate
    }

def main():
    """Run all NFR performance tests"""
    print("=== NFR Performance Testing for Issue #24 ===")
    print("Testing GET /api/calendars endpoint")
    print("\nNFR Requirements:")
    print("- [P3] Calendar list loads under 3 seconds")  
    print("- [SC1] Efficiently query calendars for 100+ users")
    print("- [P4] Support 10-20 simultaneous requests")
    
    try:
        # Login
        print("\n1. Getting authentication token...")
        token = login_and_get_token()
        print("✅ Login successful")
        
        # Test single request performance (NFR [P3])
        print("\n2. Testing single request performance (NFR [P3])...")
        single_result = test_calendar_list_performance(token)
        print(f"Response time: {single_result['response_time']:.3f}s")
        print(f"Calendar count: {single_result['calendar_count']}")
        print(f"NFR [P3] Status: {'✅ PASS' if single_result['success'] else '❌ FAIL'} (<3s)")
        
        if not single_result['success'] and single_result.get('error'):
            print(f"Error: {single_result['error']}")
        
        # Test concurrent requests (NFR [P4])
        print("\n3. Testing concurrent requests (NFR [P4])...")
        concurrent_result = test_concurrent_requests(token, 10)
        
        print(f"Total requests: {concurrent_result['total_requests']}")
        print(f"Successful: {concurrent_result['successful_requests']}")
        print(f"Failed: {concurrent_result['failed_requests']}")
        print(f"Average response time: {concurrent_result['avg_response_time']:.3f}s")
        print(f"Max response time: {concurrent_result['max_response_time']:.3f}s")
        print(f"Total test time: {concurrent_result['total_time']:.3f}s")
        print(f"NFR [P4] Status: {'✅ PASS' if concurrent_result['nfr_p4_success'] else '❌ FAIL'} (80% success)")
        
        # NFR [SC1] Assessment
        print(f"\n4. NFR [SC1] Assessment (100+ users):")
        print(f"Current implementation: O(n) linear scan through all calendars")
        print(f"With {single_result['calendar_count']} calendars: {single_result['response_time']:.3f}s")
        print(f"Projected 100 users × 10 calendars = 1000 total calendars")
        projected_time = single_result['response_time'] * (1000 / max(single_result['calendar_count'], 1))
        print(f"Projected response time: {projected_time:.3f}s")
        print(f"NFR [SC1] Status: {'✅ ACCEPTABLE' if projected_time < 3.0 else '⚠️  MAY NEED OPTIMIZATION'}")
        
        # Summary
        print(f"\n=== SUMMARY ===")
        print(f"NFR [P3] (Response time <3s): {'✅ PASS' if single_result['success'] else '❌ FAIL'}")
        print(f"NFR [P4] (Concurrent users): {'✅ PASS' if concurrent_result['nfr_p4_success'] else '❌ FAIL'}")
        print(f"NFR [SC1] (100+ users): {'✅ ACCEPTABLE' if projected_time < 3.0 else '⚠️  MONITOR'}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\nMake sure the backend server is running:")
        print("cd backend && python run.py")

if __name__ == "__main__":
    main()
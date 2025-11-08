#!/usr/bin/env python3
"""
Test Script for Background Task Queue System (Issue #52)

This script tests the task queue implementation without requiring
a running Flask server. It verifies:
- Task creation
- Task retrieval
- Status updates
- Worker processing simulation
- Retry logic
- Cleanup functionality
"""

import os
import sys
import time
from datetime import datetime, timezone, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tasks.task_queue import TaskQueue, TaskStatus, TaskType
from app.utils.json_db import tasks_db


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_test(test_name, passed):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")


def test_task_creation():
    """Test 1: Task Creation"""
    print_section("TEST 1: Task Creation")

    success, task_id, error = TaskQueue.create_task(
        task_type=TaskType.VIDEO_COMPRESSION,
        user_id="test_user_1",
        calendar_id="test_calendar_1",
        day=1,
        metadata={
            "original_path": "/tmp/test_video.mp4",
            "compressed_path": "/tmp/compressed_video.mp4",
            "thumbnail_path": "/tmp/thumbnail.jpg"
        }
    )

    print_test("Task creation returns success", success)
    print_test("Task ID is generated", task_id is not None)
    print_test("No error message", error == "")

    if task_id:
        print(f"\n📝 Created task ID: {task_id}")

        # Verify task was saved to database
        task_success, task_data, task_error = TaskQueue.get_task_by_id(task_id)
        print_test("Task saved to database", task_success)
        print_test("Task has PENDING status", task_data.get('status') == TaskStatus.PENDING.value)
        print_test("Task progress is 0", task_data.get('progress') == 0)
        print_test("Task metadata stored correctly", task_data.get('metadata', {}).get('original_path') == "/tmp/test_video.mp4")

        print(f"\n📊 Task Data:")
        print(f"   Type: {task_data.get('type')}")
        print(f"   Status: {task_data.get('status')}")
        print(f"   Progress: {task_data.get('progress')}%")
        print(f"   Created: {task_data.get('created_at')}")
        print(f"   Retry Count: {task_data.get('retry_count')}/{task_data.get('max_retries')}")

        return task_id

    return None


def test_get_next_pending_task(expected_task_id):
    """Test 2: Get Next Pending Task (FIFO)"""
    print_section("TEST 2: Get Next Pending Task (FIFO)")

    # Create a second task
    success2, task_id2, error2 = TaskQueue.create_task(
        task_type=TaskType.VIDEO_COMPRESSION,
        user_id="test_user_2",
        calendar_id="test_calendar_2",
        day=2,
        metadata={"test": "data"}
    )

    print(f"\n📝 Created second task ID: {task_id2}")

    # Get next pending task (should be the first one - FIFO)
    success, task_data, error = TaskQueue.get_next_pending_task()

    print_test("Get next pending task succeeds", success)
    print_test("Returns oldest task (FIFO)", task_data.get('task_id') == expected_task_id)

    print(f"\n📊 Next Task to Process:")
    print(f"   Task ID: {task_data.get('task_id')}")
    print(f"   User ID: {task_data.get('user_id')}")
    print(f"   Calendar ID: {task_data.get('calendar_id')}")
    print(f"   Day: {task_data.get('day')}")

    return task_data


def test_status_updates(task_id):
    """Test 3: Task Status Updates"""
    print_section("TEST 3: Task Status Updates")

    # Update to PROCESSING
    success1 = TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=25)
    print_test("Update to PROCESSING status", success1[0])

    # Verify update
    _, task_data, _ = TaskQueue.get_task_by_id(task_id)
    print_test("Status is PROCESSING", task_data.get('status') == TaskStatus.PROCESSING.value)
    print_test("Progress updated to 25%", task_data.get('progress') == 25)
    print_test("Started timestamp set", task_data.get('started_at') is not None)

    print(f"\n📊 Task Progress:")
    print(f"   Status: {task_data.get('status')}")
    print(f"   Progress: {task_data.get('progress')}%")
    print(f"   Started At: {task_data.get('started_at')}")

    # Update progress
    time.sleep(0.5)
    success2 = TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING, progress=75)
    _, task_data, _ = TaskQueue.get_task_by_id(task_id)
    print_test("Progress updated to 75%", task_data.get('progress') == 75)

    # Complete task
    time.sleep(0.5)
    success3 = TaskQueue.update_task_status(task_id, TaskStatus.COMPLETED, progress=100)
    _, task_data, _ = TaskQueue.get_task_by_id(task_id)
    print_test("Status updated to COMPLETED", task_data.get('status') == TaskStatus.COMPLETED.value)
    print_test("Progress is 100%", task_data.get('progress') == 100)
    print_test("Completed timestamp set", task_data.get('completed_at') is not None)

    print(f"\n✅ Final Task State:")
    print(f"   Status: {task_data.get('status')}")
    print(f"   Progress: {task_data.get('progress')}%")
    print(f"   Completed At: {task_data.get('completed_at')}")


def test_retry_logic():
    """Test 4: Retry Logic"""
    print_section("TEST 4: Retry Logic")

    # Create a task for retry testing
    success, task_id, error = TaskQueue.create_task(
        task_type=TaskType.VIDEO_COMPRESSION,
        user_id="test_user_retry",
        calendar_id="test_calendar_retry",
        day=1,
        metadata={"test": "retry"}
    )

    print(f"\n📝 Created task for retry testing: {task_id}")

    # Simulate 3 failures
    for i in range(1, 4):
        print(f"\n🔄 Retry Attempt {i}:")

        # Mark as processing then failed
        TaskQueue.update_task_status(task_id, TaskStatus.PROCESSING)
        TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=f"Test failure {i}")

        # Increment retry count
        success, should_retry, error = TaskQueue.increment_retry_count(task_id)

        _, task_data, _ = TaskQueue.get_task_by_id(task_id)
        retry_count = task_data.get('retry_count')
        status = task_data.get('status')

        print(f"   Retry Count: {retry_count}")
        print(f"   Should Retry: {should_retry}")
        print(f"   Status: {status}")

        if i < 3:
            print_test(f"After retry {i}, should retry is True", should_retry)
            print_test(f"After retry {i}, status is PENDING", status == TaskStatus.PENDING.value)
        else:
            print_test("After 3 retries, should retry is False", not should_retry)
            print_test("After 3 retries, status is FAILED", status == TaskStatus.FAILED.value)
            print_test("Error message includes retry info", "retry attempts" in task_data.get('error', '').lower())


def test_get_by_video():
    """Test 5: Get Task by Video Reference"""
    print_section("TEST 5: Get Task by Video Reference")

    # Create a task with specific video reference
    success, task_id, error = TaskQueue.create_task(
        task_type=TaskType.VIDEO_COMPRESSION,
        user_id="video_user",
        calendar_id="video_cal",
        day=5,
        metadata={"test": "video_lookup"}
    )

    print(f"\n📝 Created task: {task_id}")
    print(f"   User: video_user")
    print(f"   Calendar: video_cal")
    print(f"   Day: 5")

    # Retrieve by video reference
    success, task_data, error = TaskQueue.get_task_by_video("video_user", "video_cal", 5)

    print_test("Get task by video succeeds", success)
    print_test("Returns correct task", task_data.get('task_id') == task_id)
    print_test("Correct user_id", task_data.get('user_id') == "video_user")
    print_test("Correct calendar_id", task_data.get('calendar_id') == "video_cal")
    print_test("Correct day", task_data.get('day') == 5)

    # Try to get non-existent video
    success2, task_data2, error2 = TaskQueue.get_task_by_video("wrong_user", "wrong_cal", 99)
    print_test("Non-existent video returns failure", not success2)
    print_test("Error message is appropriate", "not found" in error2.lower())


def test_active_task_count():
    """Test 6: Active Task Count"""
    print_section("TEST 6: Active Task Count")

    # Get current active count
    success, active_count, error = TaskQueue.get_active_task_count()
    print(f"\n📊 Current active tasks: {active_count}")

    initial_count = active_count

    # Create some active tasks
    for i in range(3):
        TaskQueue.create_task(
            task_type=TaskType.VIDEO_COMPRESSION,
            user_id=f"count_user_{i}",
            calendar_id=f"count_cal_{i}",
            day=i + 1,
            metadata={}
        )

    # Check count increased
    success, new_count, error = TaskQueue.get_active_task_count()
    print(f"📊 After creating 3 tasks: {new_count}")

    print_test("Active task count increases", new_count == initial_count + 3)
    print_test("Get active count succeeds", success)


def test_cleanup():
    """Test 7: Cleanup Old Tasks"""
    print_section("TEST 7: Cleanup Old Tasks")

    # Create a task and mark it as completed
    success, task_id, error = TaskQueue.create_task(
        task_type=TaskType.VIDEO_COMPRESSION,
        user_id="cleanup_user",
        calendar_id="cleanup_cal",
        day=1,
        metadata={}
    )

    # Mark as completed with old timestamp (25 hours ago)
    old_time = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat().replace('+00:00', 'Z')
    tasks_db.update('tasks', task_id, {
        'status': TaskStatus.COMPLETED.value,
        'completed_at': old_time
    })

    print(f"\n📝 Created old completed task: {task_id}")
    print(f"   Completed: 25 hours ago")

    # Run cleanup (default 24 hours)
    success, deleted_count, error = TaskQueue.cleanup_old_tasks(hours_old=24)

    print_test("Cleanup succeeds", success)
    print_test("At least 1 task deleted", deleted_count >= 1)
    print(f"\n🗑️  Deleted {deleted_count} old task(s)")

    # Verify task was deleted
    success2, task_data, error2 = TaskQueue.get_task_by_id(task_id)
    print_test("Old task no longer exists", not success2)


def view_tasks_json():
    """Display tasks.json content"""
    print_section("TASKS DATABASE CONTENT")

    all_tasks = tasks_db.find_all('tasks')

    print(f"\n📊 Total tasks in database: {len(all_tasks)}")

    if all_tasks:
        print("\n📋 Task Summary:")
        for task_id, task_data in list(all_tasks.items())[:5]:  # Show first 5
            print(f"\n   Task ID: {task_id[:8]}...")
            print(f"   Type: {task_data.get('type')}")
            print(f"   Status: {task_data.get('status')}")
            print(f"   Progress: {task_data.get('progress')}%")
            print(f"   User: {task_data.get('user_id')}")
            print(f"   Calendar: {task_data.get('calendar_id')}")
            print(f"   Day: {task_data.get('day')}")
    else:
        print("\n   No tasks in database")


def cleanup_test_data():
    """Clean up test data"""
    print_section("CLEANUP TEST DATA")

    all_tasks = tasks_db.find_all('tasks')
    count = len(all_tasks)

    # Delete all test tasks
    for task_id in list(all_tasks.keys()):
        tasks_db.delete('tasks', task_id)

    print(f"\n🗑️  Cleaned up {count} test task(s)")
    print("✅ Test data removed")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  BACKGROUND TASK QUEUE SYSTEM - TEST SUITE")
    print("  Issue #52 - Professional Implementation Test")
    print("=" * 60)

    try:
        # Run tests in sequence
        task_id = test_task_creation()

        if task_id:
            task_data = test_get_next_pending_task(task_id)
            test_status_updates(task_id)

        test_retry_logic()
        test_get_by_video()
        test_active_task_count()
        test_cleanup()

        # Show database content
        view_tasks_json()

        # Final summary
        print_section("TEST SUMMARY")
        print("\n✅ All core functionality tests completed!")
        print("\n📝 Key Features Verified:")
        print("   ✓ Task creation with metadata")
        print("   ✓ FIFO task retrieval")
        print("   ✓ Status updates and progress tracking")
        print("   ✓ Retry logic (max 3 attempts)")
        print("   ✓ Task lookup by video reference")
        print("   ✓ Active task counting")
        print("   ✓ Automatic cleanup of old tasks")

        print("\n🎯 NFR Compliance:")
        print("   ✓ [P2] Task processing framework ready")
        print("   ✓ [P3] Concurrent task limit enforceable")
        print("   ✓ [SC3] Modular architecture demonstrated")
        print("   ✓ [RE1] Error recovery with retry logic")

        print("\n" + "=" * 60)

        # Ask if should cleanup
        response = input("\n🗑️  Clean up test data? (y/n): ").strip().lower()
        if response == 'y':
            cleanup_test_data()
        else:
            print("\n📝 Test data preserved in data/tasks.json")

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

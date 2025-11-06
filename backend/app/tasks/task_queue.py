# Task Queue Manager - Background Task Management System
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum

from app.utils.json_db import tasks_db


class TaskStatus(Enum):
    """Task status enumeration for state machine"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(Enum):
    """Task type enumeration"""
    VIDEO_COMPRESSION = "video_compression"


class TaskQueue:
    """
    Task Queue Manager for background job processing

    NFR Compliance:
        - [P2] Task processing starts within 5 seconds of creation
        - [P3] Handle up to 10 concurrent video processing tasks
        - [SC3] Modular architecture - reusable task queue system
        - [RE1] System continues processing tasks after errors

    This class manages the lifecycle of background tasks using JSON-based persistence.
    Tasks are stored in tasks.json and processed by Worker instances.

    Design Pattern: Producer-Consumer Queue Pattern
    - Producers create tasks via create_task()
    - Consumers (Workers) retrieve tasks via get_next_pending_task()
    - State machine ensures task lifecycle integrity
    """

    @staticmethod
    def create_task(
        task_type: TaskType,
        user_id: str,
        calendar_id: str,
        day: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], str]:
        """
        Create a new background task

        Args:
            task_type: Type of task to create (e.g., VIDEO_COMPRESSION)
            user_id: User ID who owns this task
            calendar_id: Calendar ID associated with this task
            day: Day number for the video (1-31)
            metadata: Optional additional task-specific data

        Returns:
            Tuple of (success, task_id, error_message)
        """
        try:
            task_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

            task_data = {
                'task_id': task_id,
                'type': task_type.value,
                'user_id': user_id,
                'calendar_id': calendar_id,
                'day': day,
                'status': TaskStatus.PENDING.value,
                'progress': 0,
                'created_at': now,
                'updated_at': now,
                'started_at': None,
                'completed_at': None,
                'error': None,
                'retry_count': 0,
                'max_retries': 3,
                'metadata': metadata or {}
            }

            # Save task to database
            tasks_db.create('tasks', task_id, task_data)

            return True, task_id, ""

        except Exception as e:
            print(f"Task creation error: {str(e)}")
            return False, None, f"Failed to create task: {str(e)}"

    @staticmethod
    def get_task_by_id(task_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Get task by ID

        Args:
            task_id: Task ID to retrieve

        Returns:
            Tuple of (success, task_data, error_message)
        """
        try:
            task = tasks_db.find_by_id('tasks', task_id)

            if not task:
                return False, None, "Task not found"

            return True, task, ""

        except Exception as e:
            print(f"Get task error: {str(e)}")
            return False, None, f"Failed to retrieve task: {str(e)}"

    @staticmethod
    def get_task_by_video(
        user_id: str,
        calendar_id: str,
        day: int
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Get task for specific video (user_id, calendar_id, day combination)

        This is used by the status endpoint to check video processing status.

        Args:
            user_id: User ID
            calendar_id: Calendar ID
            day: Day number

        Returns:
            Tuple of (success, task_data, error_message)
        """
        try:
            # Get all tasks and filter by user_id, calendar_id, and day
            all_tasks = tasks_db.find_all('tasks')

            for task_id, task_data in all_tasks.items():
                if (task_data.get('user_id') == user_id and
                    task_data.get('calendar_id') == calendar_id and
                    task_data.get('day') == day):
                    # Return most recent task for this video
                    return True, task_data, ""

            return False, None, "No task found for this video"

        except Exception as e:
            print(f"Get task by video error: {str(e)}")
            return False, None, f"Failed to retrieve task: {str(e)}"

    @staticmethod
    def get_next_pending_task() -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Get next pending task for processing (FIFO order)

        Workers call this method to retrieve the next task to process.
        Only returns tasks in PENDING status.

        Returns:
            Tuple of (success, task_data, error_message)
        """
        try:
            all_tasks = tasks_db.find_all('tasks')

            # Filter pending tasks and sort by created_at (FIFO)
            pending_tasks = [
                (task_id, task_data)
                for task_id, task_data in all_tasks.items()
                if task_data.get('status') == TaskStatus.PENDING.value
            ]

            if not pending_tasks:
                return False, None, "No pending tasks"

            # Sort by created_at timestamp (earliest first - FIFO)
            pending_tasks.sort(key=lambda x: x[1].get('created_at', ''))

            # Return the oldest pending task
            task_id, task_data = pending_tasks[0]
            return True, task_data, ""

        except Exception as e:
            print(f"Get next pending task error: {str(e)}")
            return False, None, f"Failed to retrieve pending task: {str(e)}"

    @staticmethod
    def update_task_status(
        task_id: str,
        status: TaskStatus,
        progress: Optional[int] = None,
        error: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Update task status and progress

        Args:
            task_id: Task ID to update
            status: New task status
            progress: Optional progress percentage (0-100)
            error: Optional error message (for FAILED status)

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Get current task
            task_success, task_data, task_error = TaskQueue.get_task_by_id(task_id)
            if not task_success:
                return False, task_error

            # Prepare updates
            now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            updates = {
                'status': status.value,
                'updated_at': now
            }

            # Update progress if provided
            if progress is not None:
                updates['progress'] = max(0, min(100, progress))  # Clamp 0-100

            # Update error if provided
            if error:
                updates['error'] = error

            # Set timestamps based on status
            if status == TaskStatus.PROCESSING and not task_data.get('started_at'):
                updates['started_at'] = now
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                updates['completed_at'] = now
                updates['progress'] = 100 if status == TaskStatus.COMPLETED else task_data.get('progress', 0)

            # Update task in database
            tasks_db.update('tasks', task_id, updates)

            return True, ""

        except Exception as e:
            print(f"Update task status error: {str(e)}")
            return False, f"Failed to update task status: {str(e)}"

    @staticmethod
    def increment_retry_count(task_id: str) -> Tuple[bool, bool, str]:
        """
        Increment task retry count and check if max retries exceeded

        Args:
            task_id: Task ID to increment retry count

        Returns:
            Tuple of (success, should_retry, error_message)
            - should_retry is True if task should be retried, False if max retries exceeded
        """
        try:
            task_success, task_data, task_error = TaskQueue.get_task_by_id(task_id)
            if not task_success:
                return False, False, task_error

            current_retry = task_data.get('retry_count', 0)
            max_retries = task_data.get('max_retries', 3)
            new_retry_count = current_retry + 1

            # Update retry count
            updates = {
                'retry_count': new_retry_count,
                'updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }

            # If max retries exceeded, mark as FAILED
            if new_retry_count >= max_retries:
                updates['status'] = TaskStatus.FAILED.value
                updates['error'] = f"Task failed after {max_retries} retry attempts"
                updates['completed_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                should_retry = False
            else:
                # Reset to PENDING for retry
                updates['status'] = TaskStatus.PENDING.value
                should_retry = True

            tasks_db.update('tasks', task_id, updates)

            return True, should_retry, ""

        except Exception as e:
            print(f"Increment retry count error: {str(e)}")
            return False, False, f"Failed to increment retry count: {str(e)}"

    @staticmethod
    def cleanup_old_tasks(hours_old: int = 24) -> Tuple[bool, int, str]:
        """
        Clean up completed and failed tasks older than specified hours

        NFR Compliance:
            - Resource management: Prevent tasks.json from growing indefinitely
            - [SC3] Modular architecture: Automatic cleanup mechanism

        Args:
            hours_old: Delete tasks completed/failed more than this many hours ago (default: 24)

        Returns:
            Tuple of (success, deleted_count, error_message)
        """
        try:
            all_tasks = tasks_db.find_all('tasks')
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_old)
            deleted_count = 0

            for task_id, task_data in list(all_tasks.items()):
                status = task_data.get('status')

                # Only delete completed or failed tasks
                if status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
                    completed_at_str = task_data.get('completed_at')

                    if completed_at_str:
                        try:
                            # Parse ISO format timestamp
                            completed_at = datetime.fromisoformat(completed_at_str.replace('Z', '+00:00'))

                            # Delete if older than cutoff
                            if completed_at < cutoff_time:
                                tasks_db.delete('tasks', task_id)
                                deleted_count += 1
                        except (ValueError, AttributeError):
                            # Skip tasks with invalid timestamps
                            continue

            return True, deleted_count, ""

        except Exception as e:
            print(f"Cleanup old tasks error: {str(e)}")
            return False, 0, f"Failed to cleanup tasks: {str(e)}"

    @staticmethod
    def get_active_task_count() -> Tuple[bool, int, str]:
        """
        Get count of active tasks (pending or processing)

        Used to enforce concurrency limits (NFR [P3]: max 10 concurrent tasks)

        Returns:
            Tuple of (success, active_count, error_message)
        """
        try:
            all_tasks = tasks_db.find_all('tasks')

            active_count = sum(
                1 for task_data in all_tasks.values()
                if task_data.get('status') in [TaskStatus.PENDING.value, TaskStatus.PROCESSING.value]
            )

            return True, active_count, ""

        except Exception as e:
            print(f"Get active task count error: {str(e)}")
            return False, 0, f"Failed to get active task count: {str(e)}"

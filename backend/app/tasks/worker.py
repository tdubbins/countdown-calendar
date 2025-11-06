# Background Worker - Task Processing Engine
import threading
import time
from typing import Optional

from app.tasks.task_queue import TaskQueue, TaskStatus, TaskType
from app.tasks.video_tasks import VideoCompressionTask


class Worker:
    """
    Background Worker for processing tasks from the queue

    NFR Compliance:
        - [P2] Task processing starts within 5 seconds of upload
        - [P3] Handle up to 10 concurrent video processing tasks
        - [RE1] System continues processing tasks after errors
        - [SC3] Modular architecture: Separate worker process

    Design Pattern: Worker Thread Pattern
    - Runs in separate thread to avoid blocking Flask application
    - Continuously polls for pending tasks
    - Executes tasks and handles failures with retry logic
    - Graceful shutdown mechanism

    Usage:
        worker = Worker()
        worker.start()  # Start background processing
        # ... application runs ...
        worker.stop()   # Graceful shutdown
    """

    def __init__(self, poll_interval: int = 2, max_concurrent: int = 10):
        """
        Initialize worker

        Args:
            poll_interval: Seconds between queue polls (default: 2)
            max_concurrent: Maximum concurrent tasks to process (default: 10, NFR [P3])
        """
        self.poll_interval = poll_interval
        self.max_concurrent = max_concurrent
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """
        Start the background worker thread

        This creates and starts a daemon thread that processes tasks.
        Daemon threads automatically terminate when the main program exits.
        """
        with self._lock:
            if self.running:
                print("Worker is already running")
                return

            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("Background worker started")

    def stop(self) -> None:
        """
        Stop the background worker gracefully

        Sets the running flag to False and waits for the worker thread to finish.
        """
        with self._lock:
            if not self.running:
                print("Worker is not running")
                return

            print("Stopping background worker...")
            self.running = False

        # Wait for thread to finish (with timeout)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)
            print("Background worker stopped")

    def is_running(self) -> bool:
        """Check if worker is currently running"""
        with self._lock:
            return self.running

    def _run(self) -> None:
        """
        Main worker loop

        Continuously polls for pending tasks and processes them.
        Implements retry logic and error handling per NFR [RE1].
        """
        print("Worker thread started - polling for tasks")

        while self.running:
            try:
                # Check if we can process more tasks (concurrency limit)
                success, active_count, error = TaskQueue.get_active_task_count()
                if success and active_count >= self.max_concurrent:
                    # Too many active tasks, wait before polling again
                    time.sleep(self.poll_interval)
                    continue

                # Get next pending task
                success, task_data, error = TaskQueue.get_next_pending_task()

                if not success:
                    # No tasks available, wait before polling again
                    time.sleep(self.poll_interval)
                    continue

                # Process task based on type
                self._process_task(task_data)

            except Exception as e:
                # Worker continues running even if task processing fails (NFR [RE1])
                print(f"Worker error: {str(e)}")
                time.sleep(self.poll_interval)

        print("Worker thread stopped")

    def _process_task(self, task_data: dict) -> None:
        """
        Process a single task

        Dispatches task to appropriate handler based on task type.
        Implements retry logic for failed tasks.

        Args:
            task_data: Task data from queue
        """
        task_id = task_data.get('task_id')
        task_type = task_data.get('type')

        print(f"Processing task {task_id} (type: {task_type})")

        try:
            # Dispatch to appropriate task handler
            if task_type == TaskType.VIDEO_COMPRESSION.value:
                success, error = VideoCompressionTask.execute(task_data)
            else:
                error = f"Unknown task type: {task_type}"
                success = False
                TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error)

            # Handle task failure with retry logic
            if not success:
                print(f"Task {task_id} failed: {error}")
                self._handle_task_failure(task_id)
            else:
                print(f"Task {task_id} completed successfully")

        except Exception as e:
            error_msg = f"Unexpected error processing task {task_id}: {str(e)}"
            print(error_msg)
            TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
            self._handle_task_failure(task_id)

    def _handle_task_failure(self, task_id: str) -> None:
        """
        Handle task failure with retry logic

        NFR Compliance: [RE1] System continues after errors

        Args:
            task_id: Failed task ID
        """
        try:
            # Increment retry count and check if should retry
            success, should_retry, error = TaskQueue.increment_retry_count(task_id)

            if success:
                if should_retry:
                    print(f"Task {task_id} will be retried")
                else:
                    print(f"Task {task_id} failed permanently (max retries exceeded)")
            else:
                print(f"Failed to handle task failure: {error}")

        except Exception as e:
            print(f"Error handling task failure: {str(e)}")


# Global worker instance (singleton)
_worker_instance: Optional[Worker] = None


def get_worker() -> Worker:
    """
    Get or create the global worker instance

    This ensures only one worker runs in the application.

    Returns:
        Worker instance
    """
    global _worker_instance
    if _worker_instance is None:
        _worker_instance = Worker()
    return _worker_instance


def start_worker() -> None:
    """Start the global background worker"""
    worker = get_worker()
    worker.start()


def stop_worker() -> None:
    """Stop the global background worker"""
    worker = get_worker()
    worker.stop()

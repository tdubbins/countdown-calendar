# Background Worker - Task Processing Engine
import logging
import threading
import time
from typing import Optional

from app.tasks.task_queue import TaskQueue, TaskStatus, TaskType
from app.tasks.video_tasks import VideoCompressionTask

# Configure logger (no timestamp - journalctl provides it)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[WORKER] %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class Worker:
    """
    Background Worker for processing tasks from the queue.

    Runs in a separate thread, continuously polling for pending tasks
    and executing them with retry logic on failures.
    """

    def __init__(self, poll_interval: int = 2, max_concurrent: int = 10, cleanup_interval: int = 3600):
        """
        Initialize worker.

        Args:
            poll_interval: Seconds between queue polls (default: 2)
            max_concurrent: Maximum concurrent tasks to process (default: 10)
            cleanup_interval: Seconds between cleanup runs (default: 3600)
        """
        self.poll_interval = poll_interval
        self.max_concurrent = max_concurrent
        self.cleanup_interval = cleanup_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.cleanup_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the background worker thread and cleanup scheduler."""
        with self._lock:
            if self.running:
                logger.warning("Worker is already running")
                return

            self.running = True

            # Start task processing thread
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

            # Start cleanup scheduler thread
            self.cleanup_thread = threading.Thread(target=self._run_cleanup, daemon=True)
            self.cleanup_thread.start()

            logger.info("Background worker started (task processing + cleanup scheduler)")

    def stop(self) -> None:
        """Stop the background worker and cleanup scheduler gracefully."""
        with self._lock:
            if not self.running:
                logger.warning("Worker is not running")
                return

            logger.info("Stopping background worker...")
            self.running = False

        # Wait for task processing thread to finish (with timeout)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)

        # Wait for cleanup thread to finish (with timeout)
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=10)

        logger.info("Background worker stopped")

    def is_running(self) -> bool:
        """Check if worker is currently running"""
        with self._lock:
            return self.running

    def _run(self) -> None:
        """Main worker loop - polls for pending tasks and processes them."""
        logger.info("Worker thread started - polling for tasks")

        while self.running:
            try:
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
                # Worker continues running even if task processing fails
                logger.error(f"Worker error: {str(e)}")
                time.sleep(self.poll_interval)

        logger.info("Worker thread stopped")

    def _run_cleanup(self) -> None:
        """Cleanup scheduler loop - periodically deletes old tasks."""
        logger.info("Cleanup scheduler started - will run every hour")

        # Run initial cleanup on startup
        try:
            success, deleted_count, error = TaskQueue.cleanup_old_tasks(hours_old=24)
            if success and deleted_count > 0:
                logger.info(f"Initial cleanup: deleted {deleted_count} old task(s)")
        except Exception as e:
            logger.error(f"Initial cleanup error: {str(e)}")

        while self.running:
            try:
                # Sleep for cleanup interval (default: 1 hour)
                time.sleep(self.cleanup_interval)

                # Run cleanup
                success, deleted_count, error = TaskQueue.cleanup_old_tasks(hours_old=24)

                if success:
                    if deleted_count > 0:
                        logger.info(f"Cleanup: deleted {deleted_count} old task(s)")
                else:
                    logger.error(f"Cleanup error: {error}")

            except Exception as e:
                # Scheduler continues running even if cleanup fails
                logger.error(f"Cleanup scheduler error: {str(e)}")
                time.sleep(self.cleanup_interval)

        logger.info("Cleanup scheduler stopped")

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
        calendar_id = task_data.get('calendar_id', 'unknown')
        day = task_data.get('day', 'unknown')
        retry_count = task_data.get('retry_count', 0)

        # Start timing
        start_time = time.time()

        logger.info(f"TASK START | id={task_id[:8]}... | type={task_type} | calendar={calendar_id[:8]}... | day={day} | retry={retry_count}")

        try:
            # Dispatch to appropriate task handler
            if task_type == TaskType.VIDEO_COMPRESSION.value:
                success, error = VideoCompressionTask.execute(task_data)
            else:
                error = f"Unknown task type: {task_type}"
                success = False
                TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error)

            # Calculate duration
            duration = time.time() - start_time

            # Handle task failure with retry logic
            if not success:
                logger.error(f"TASK FAILED | id={task_id[:8]}... | duration={duration:.2f}s | error={error}")
                self._handle_task_failure(task_id)
            else:
                logger.info(f"TASK COMPLETE | id={task_id[:8]}... | duration={duration:.2f}s | calendar={calendar_id[:8]}... | day={day}")

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"TASK ERROR | id={task_id[:8]}... | duration={duration:.2f}s | error={error_msg}")
            TaskQueue.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
            self._handle_task_failure(task_id)

    def _handle_task_failure(self, task_id: str) -> None:
        """Handle task failure with retry logic."""
        try:
            # Increment retry count and check if should retry
            success, should_retry, error = TaskQueue.increment_retry_count(task_id)

            if success:
                if should_retry:
                    logger.warning(f"TASK RETRY | id={task_id[:8]}... | scheduled for retry")
                else:
                    logger.error(f"TASK PERMANENT FAIL | id={task_id[:8]}... | max retries exceeded")
            else:
                logger.error(f"Failed to handle task failure: {error}")

        except Exception as e:
            logger.error(f"Error handling task failure: {str(e)}")


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

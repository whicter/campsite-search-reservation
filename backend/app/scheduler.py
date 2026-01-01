"""Task scheduler for monitoring campsite availability"""
from rq import Queue
from rq.job import Job
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.redis_client import redis_conn
from app.database import SessionLocal
from app.db_models import MonitoringTask
from app.tasks import check_campsite_availability


# Create RQ queue
monitoring_queue = Queue('monitoring', connection=redis_conn)


def enqueue_monitoring_task(task_id: int, delay_seconds: int = 0) -> Optional[Job]:
    """
    Enqueue a monitoring task to RQ.

    Args:
        task_id: ID of the monitoring task
        delay_seconds: Delay before execution (for scheduling)

    Returns:
        RQ Job object or None if failed
    """
    try:
        if delay_seconds > 0:
            # Schedule for later
            job = monitoring_queue.enqueue_in(
                timedelta(seconds=delay_seconds),
                check_campsite_availability,
                task_id=task_id,
                job_timeout='5m'
            )
        else:
            # Execute immediately
            job = monitoring_queue.enqueue(
                check_campsite_availability,
                task_id=task_id,
                job_timeout='5m'
            )

        # Update task with job ID
        db: Session = SessionLocal()
        try:
            task = db.query(MonitoringTask).filter(MonitoringTask.id == task_id).first()
            if task:
                task.rq_job_id = job.id
                db.commit()
        finally:
            db.close()

        return job

    except Exception as e:
        print(f"Error enqueueing task {task_id}: {e}")
        return None


def schedule_all_active_tasks():
    """
    Schedule all active monitoring tasks.

    This should be called when the application starts to ensure
    all active tasks are running.
    """
    db: Session = SessionLocal()

    try:
        active_tasks = db.query(MonitoringTask).filter(
            MonitoringTask.status == 'active'
        ).all()

        scheduled_count = 0
        for task in active_tasks:
            job = enqueue_monitoring_task(task.id)
            if job:
                scheduled_count += 1

        print(f"Scheduled {scheduled_count} active monitoring tasks")
        return scheduled_count

    finally:
        db.close()


def get_job_status(job_id: str) -> Optional[dict]:
    """
    Get status of an RQ job.

    Args:
        job_id: RQ job ID

    Returns:
        Job status dict or None if not found
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return {
            "id": job.id,
            "status": job.get_status(),
            "created_at": job.created_at,
            "started_at": job.started_at,
            "ended_at": job.ended_at,
            "result": job.result,
            "exc_info": job.exc_info
        }
    except Exception as e:
        print(f"Error fetching job {job_id}: {e}")
        return None


def cancel_job(job_id: str) -> bool:
    """
    Cancel an RQ job.

    Args:
        job_id: RQ job ID

    Returns:
        True if cancelled successfully
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        job.cancel()
        return True
    except Exception as e:
        print(f"Error cancelling job {job_id}: {e}")
        return False

"""RQ background tasks for campsite monitoring"""
import time
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.db_models import MonitoringTask, NotificationHistory
from app.providers.camply_provider import CamplyProvider


def check_campsite_availability(task_id: int) -> Dict[str, Any]:
    """
    Background task to check campsite availability.

    This task is executed by RQ worker to monitor campsite availability.
    It runs periodically to check if the desired campsite is available.

    Args:
        task_id: ID of the monitoring task in database

    Returns:
        Result dict with status and availability info
    """
    db: Session = SessionLocal()

    try:
        # Get task from database
        task = db.query(MonitoringTask).filter(MonitoringTask.id == task_id).first()

        if not task:
            return {"status": "error", "message": f"Task {task_id} not found"}

        # Update last checked time
        task.last_checked_at = datetime.utcnow()

        # Check availability using provider
        provider = CamplyProvider()

        try:
            result = provider.check_availability(
                campground_id=task.campground_id,
                start_date=task.start_date.isoformat(),
                end_date=task.end_date.isoformat()
            )

            # If available, create notification record
            if result.get("available"):
                notification = NotificationHistory(
                    user_id=task.user_id,
                    task_id=task.id,
                    notification_type="system",  # Will be extended to support email/pushover
                    campground_name=task.campground_name,
                    availability_data={
                        "start_date": task.start_date.isoformat(),
                        "end_date": task.end_date.isoformat(),
                        "campground_id": task.campground_id,
                        "details": result
                    },
                    success=True
                )
                db.add(notification)

                # Mark task as completed
                task.status = "completed"
                task.completed_at = datetime.utcnow()

                db.commit()

                return {
                    "status": "success",
                    "available": True,
                    "task_id": task_id,
                    "campground": task.campground_name,
                    "message": "Campsite is available!"
                }
            else:
                # Not available yet, task continues
                db.commit()

                return {
                    "status": "success",
                    "available": False,
                    "task_id": task_id,
                    "message": "No availability yet, will check again"
                }

        except Exception as e:
            # Provider error
            task.error_message = str(e)
            task.status = "failed"
            db.commit()

            return {
                "status": "error",
                "task_id": task_id,
                "message": f"Provider error: {str(e)}"
            }

    except Exception as e:
        # Database or other error
        if db:
            db.rollback()
        return {
            "status": "error",
            "task_id": task_id,
            "message": f"Task error: {str(e)}"
        }
    finally:
        if db:
            db.close()


def test_task(message: str) -> Dict[str, Any]:
    """Test task for verifying RQ is working"""
    time.sleep(2)
    return {
        "status": "success",
        "message": f"Test task completed: {message}",
        "timestamp": datetime.utcnow().isoformat()
    }

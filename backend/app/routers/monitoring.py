"""Monitoring task routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date as date_type

from app.database import get_db
from app.db_models import User, MonitoringTask, NotificationHistory
from app.api_models import (
    MonitoringTaskCreate,
    MonitoringTaskUpdate,
    MonitoringTaskResponse,
    NotificationHistoryResponse
)
from app.auth import get_current_user
from app.scheduler import enqueue_monitoring_task, cancel_job, get_job_status

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/tasks", response_model=MonitoringTaskResponse, status_code=status.HTTP_201_CREATED)
def create_monitoring_task(
    task_data: MonitoringTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new monitoring task.

    The task will be automatically scheduled to run in the background
    to check campsite availability.

    - **provider**: Provider name (e.g., "RecreationDotGov")
    - **campground_id**: Campground ID
    - **campground_name**: Campground name
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)
    - **nights**: Optional number of consecutive nights for range search
    - **search_mode**: "exact" or "range"
    """
    # Parse dates
    try:
        start_date = date_type.fromisoformat(task_data.start_date)
        end_date = date_type.fromisoformat(task_data.end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Create task
    new_task = MonitoringTask(
        user_id=current_user.id,
        provider=task_data.provider,
        campground_id=task_data.campground_id,
        campground_name=task_data.campground_name,
        start_date=start_date,
        end_date=end_date,
        nights=task_data.nights,
        search_mode=task_data.search_mode,
        status="active"
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Enqueue task to RQ
    job = enqueue_monitoring_task(new_task.id)

    if not job:
        # Failed to enqueue, but task is created
        new_task.status = "failed"
        new_task.error_message = "Failed to enqueue task to worker"
        db.commit()

    return new_task


@router.get("/tasks", response_model=List[MonitoringTaskResponse])
def get_monitoring_tasks(
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all monitoring tasks for the current user.

    - **status**: Optional filter by status (active, paused, completed, cancelled, failed)
    """
    query = db.query(MonitoringTask).filter(MonitoringTask.user_id == current_user.id)

    if status:
        query = query.filter(MonitoringTask.status == status)

    tasks = query.order_by(MonitoringTask.created_at.desc()).all()

    return tasks


@router.get("/tasks/{task_id}", response_model=MonitoringTaskResponse)
def get_monitoring_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific monitoring task by ID"""
    task = db.query(MonitoringTask).filter(
        MonitoringTask.id == task_id,
        MonitoringTask.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.patch("/tasks/{task_id}", response_model=MonitoringTaskResponse)
def update_monitoring_task(
    task_id: int,
    task_update: MonitoringTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a monitoring task.

    Currently supports updating the status:
    - **active**: Resume monitoring
    - **paused**: Pause monitoring
    - **cancelled**: Cancel monitoring
    """
    task = db.query(MonitoringTask).filter(
        MonitoringTask.id == task_id,
        MonitoringTask.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update status
    if task_update.status:
        old_status = task.status
        task.status = task_update.status

        # Handle job based on status change
        if task_update.status == "cancelled" and task.rq_job_id:
            # Cancel RQ job
            cancel_job(task.rq_job_id)

        elif task_update.status == "active" and old_status in ["paused", "failed"]:
            # Re-enqueue task
            job = enqueue_monitoring_task(task.id)
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to restart monitoring task"
                )

    db.commit()
    db.refresh(task)

    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitoring_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a monitoring task"""
    task = db.query(MonitoringTask).filter(
        MonitoringTask.id == task_id,
        MonitoringTask.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Cancel job if exists
    if task.rq_job_id:
        cancel_job(task.rq_job_id)

    db.delete(task)
    db.commit()

    return None


@router.get("/tasks/{task_id}/status")
def get_task_job_status(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the RQ job status for a monitoring task.

    Returns detailed information about the background job execution.
    """
    task = db.query(MonitoringTask).filter(
        MonitoringTask.id == task_id,
        MonitoringTask.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if not task.rq_job_id:
        return {"status": "no_job", "message": "No background job associated"}

    job_status = get_job_status(task.rq_job_id)

    if not job_status:
        return {"status": "not_found", "message": "Job not found in queue"}

    return job_status


@router.get("/notifications", response_model=List[NotificationHistoryResponse])
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notification history for the current user.

    Returns all notifications sent when campsites become available.
    """
    notifications = db.query(NotificationHistory).filter(
        NotificationHistory.user_id == current_user.id
    ).order_by(NotificationHistory.sent_at.desc()).all()

    return notifications

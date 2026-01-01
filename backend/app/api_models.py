"""Pydantic models for API requests and responses"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime


# Authentication models
class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User info response"""
    id: int
    email: str
    created_at: datetime

    class Config:
        orm_mode = True


# Monitoring task models
class MonitoringTaskCreate(BaseModel):
    """Create monitoring task request"""
    provider: str
    campground_id: str
    campground_name: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    nights: Optional[int] = None
    search_mode: str = "exact"


class MonitoringTaskUpdate(BaseModel):
    """Update monitoring task request"""
    status: Optional[str] = None  # active, paused, cancelled


class MonitoringTaskResponse(BaseModel):
    """Monitoring task response"""
    id: int
    user_id: int
    provider: str
    campground_id: str
    campground_name: str
    start_date: date
    end_date: date
    nights: Optional[int]
    search_mode: str
    status: str
    rq_job_id: Optional[str]
    last_checked_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str]

    class Config:
        orm_mode = True


# Notification models
class NotificationHistoryResponse(BaseModel):
    """Notification history response"""
    id: int
    user_id: int
    task_id: Optional[int]
    notification_type: str
    campground_name: str
    availability_data: dict
    sent_at: datetime
    success: bool
    error_message: Optional[str]

    class Config:
        orm_mode = True

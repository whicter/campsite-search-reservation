"""SQLAlchemy database models"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User account"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    monitoring_tasks = relationship("MonitoringTask", back_populates="user", cascade="all, delete-orphan")
    notification_settings = relationship("NotificationSetting", back_populates="user", cascade="all, delete-orphan")
    notification_history = relationship("NotificationHistory", back_populates="user", cascade="all, delete-orphan")
    favorite_campgrounds = relationship("FavoriteCampground", back_populates="user", cascade="all, delete-orphan")


class MonitoringTask(Base):
    """Campsite monitoring task"""
    __tablename__ = "monitoring_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Campground info
    provider = Column(String(100), nullable=False)
    campground_id = Column(String(50), nullable=False)
    campground_name = Column(String(255), nullable=False)

    # Search parameters
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    nights = Column(Integer, nullable=True)  # NULL = exact dates, >0 = range search
    search_mode = Column(String(20), default="exact")  # "exact" or "range"

    # Task status
    status = Column(String(20), default="active")  # active, paused, completed, cancelled, failed
    rq_job_id = Column(String(255), nullable=True)  # RQ job ID

    # Timestamps
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Error info
    error_message = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="monitoring_tasks")

    # Indexes
    __table_args__ = (
        Index('idx_monitoring_tasks_user_id', 'user_id'),
        Index('idx_monitoring_tasks_status', 'status'),
        Index('idx_monitoring_tasks_active', 'user_id', 'status', postgresql_where=(Column('status') == 'active')),
    )


class NotificationSetting(Base):
    """User notification configuration"""
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Notification type
    notification_type = Column(String(50), nullable=False)  # email, pushover, telegram

    # Configuration data (JSON)
    config_data = Column(JSONB, nullable=False)

    # Enabled flag
    is_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notification_settings")

    # Unique constraint: one config per user per type
    __table_args__ = (
        Index('idx_notification_settings_user_type', 'user_id', 'notification_type', unique=True),
    )


class NotificationHistory(Base):
    """Notification history log"""
    __tablename__ = "notification_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("monitoring_tasks.id", ondelete="SET NULL"), nullable=True)

    # Notification content
    notification_type = Column(String(50), nullable=False)
    campground_name = Column(String(255), nullable=False)
    availability_data = Column(JSONB, nullable=False)

    # Send status
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="notification_history")

    # Indexes
    __table_args__ = (
        Index('idx_notification_history_user_id', 'user_id'),
        Index('idx_notification_history_sent_at', 'sent_at', postgresql_using='btree', postgresql_ops={'sent_at': 'DESC'}),
    )


class FavoriteCampground(Base):
    """User's favorite campgrounds"""
    __tablename__ = "favorite_campgrounds"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    provider = Column(String(100), nullable=False)
    campground_id = Column(String(50), nullable=False)
    campground_name = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="favorite_campgrounds")

    # Unique constraint
    __table_args__ = (
        Index('idx_favorite_campgrounds_user_id', 'user_id'),
        Index('idx_favorite_unique', 'user_id', 'provider', 'campground_id', unique=True),
    )

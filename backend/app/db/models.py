import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class TaskStatusEnum(str):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DownloadTask(Base):
    __tablename__ = "download_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    thread_url = Column(String(500), nullable=False)
    thread_id = Column(String(100), nullable=True, index=True)
    status = Column(String(20), default=TaskStatusEnum.PENDING, nullable=False)
    progress = Column(Integer, default=0, nullable=False)
    total_downloaded = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    media_items = relationship("MediaItem", back_populates="task", cascade="all, delete-orphan")

class MediaItem(Base):
    __tablename__ = "media_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("download_tasks.id", ondelete="CASCADE"), nullable=True)
    thread_id = Column(String(100), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    original_url = Column(Text, nullable=False)
    media_type = Column(String(20), default="image", nullable=False)  # "image" ou "video"
    file_size = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("DownloadTask", back_populates="media_items")

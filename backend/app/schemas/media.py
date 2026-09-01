from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MediaItemResponse(BaseModel):
    id: str
    task_id: Optional[str] = None
    thread_id: str
    file_path: str
    original_url: str
    media_type: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True

class MediaListResponse(BaseModel):
    items: List[MediaItemResponse]
    total: int

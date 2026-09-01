from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class TaskCreateRequest(BaseModel):
    thread_url: str
    full_history: bool = True  # Volta até o início absoluto da conversa por padrão
    max_scrolls: Optional[int] = 150  # Limite máximo de segurança para conversas imensas
    headless: bool = False  # Por padrão abre visível para o usuário ver a conversa rolando

class TaskStatusResponse(BaseModel):
    id: str
    thread_url: str
    thread_id: Optional[str] = None
    status: str
    progress: int
    total_downloaded: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    tasks: List[TaskStatusResponse]

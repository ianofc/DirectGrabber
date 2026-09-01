from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.dao.base import BaseDAO
from app.db.models import MediaItem

class MediaDAO(BaseDAO[MediaItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(MediaItem, db)

    async def get_by_thread(self, thread_id: str) -> List[MediaItem]:
        query = select(MediaItem).where(MediaItem.thread_id == thread_id).order_by(MediaItem.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_task(self, task_id: str) -> List[MediaItem]:
        query = select(MediaItem).where(MediaItem.task_id == task_id).order_by(MediaItem.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def exists_by_url(self, original_url: str) -> bool:
        query = select(MediaItem.id).where(MediaItem.original_url == original_url)
        result = await self.db.execute(query)
        return result.scalars().first() is not None

    async def list_recent(self, limit: int = 100, offset: int = 0, media_type: Optional[str] = None) -> List[MediaItem]:
        query = select(MediaItem)
        if media_type:
            query = query.where(MediaItem.media_type == media_type)
        query = query.order_by(MediaItem.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

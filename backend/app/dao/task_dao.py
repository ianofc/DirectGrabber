from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.dao.base import BaseDAO
from app.db.models import DownloadTask

class TaskDAO(BaseDAO[DownloadTask]):
    def __init__(self, db: AsyncSession):
        super().__init__(DownloadTask, db)

    async def update_status(
        self,
        task_id: str,
        status: str,
        progress: Optional[int] = None,
        total_downloaded: Optional[int] = None,
        error_message: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> Optional[DownloadTask]:
        task = await self.get_by_id(task_id)
        if not task:
            return None
        
        task.status = status
        if progress is not None:
            task.progress = progress
        if total_downloaded is not None:
            task.total_downloaded = total_downloaded
        if error_message is not None:
            task.error_message = error_message
        if thread_id is not None:
            task.thread_id = thread_id
            
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_recent_tasks(self, limit: int = 20) -> List[DownloadTask]:
        query = select(DownloadTask).order_by(DownloadTask.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dao.media_dao import MediaDAO
from app.core.config import settings
from app.schemas.media import MediaListResponse, MediaItemResponse

router = APIRouter()

@router.get("/", response_model=MediaListResponse)
async def list_media(
    thread_id: Optional[str] = None,
    media_type: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    media_dao = MediaDAO(db)
    if thread_id:
        items = await media_dao.get_by_thread(thread_id)
        # Aplica filtro de media_type se especificado
        if media_type:
            items = [item for item in items if item.media_type == media_type]
        paginated_items = items[offset:offset+limit]
        return MediaListResponse(items=paginated_items, total=len(items))
    else:
        items = await media_dao.list_recent(limit=limit, offset=offset, media_type=media_type)
        return MediaListResponse(items=items, total=len(items))

@router.get("/thread/{thread_id}", response_model=MediaListResponse)
async def get_thread_media(
    thread_id: str,
    db: AsyncSession = Depends(get_db)
):
    media_dao = MediaDAO(db)
    items = await media_dao.get_by_thread(thread_id)
    return MediaListResponse(items=items, total=len(items))

@router.get("/{media_id}/file")
async def get_media_file(
    media_id: str,
    db: AsyncSession = Depends(get_db)
):
    media_dao = MediaDAO(db)
    item = await media_dao.get_by_id(media_id)
    if not item:
        raise HTTPException(status_code=404, detail="Arquivo de mídia não encontrado.")

    # file_path armazena formato "downloads/thread_id/filename.ext"
    # Resolve dentro do storage dir
    storage_root = settings.DOWNLOADS_DIR.parent  # storage/
    full_path = storage_root / item.file_path

    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no disco.")

    media_type_header = "video/mp4" if item.media_type == "video" else "image/jpeg"
    return FileResponse(
        path=str(full_path),
        media_type=media_type_header,
        filename=full_path.name
    )

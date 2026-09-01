from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dao.task_dao import TaskDAO
from app.dao.media_dao import MediaDAO
from app.services.session_manager import SessionManager
from app.services.playwright_engine import PlaywrightEngine
from app.schemas.auth import (
    SessionStatusResponse,
    StartSessionResponse,
    ImportCookiesRequest,
)
from fastapi import HTTPException

router = APIRouter()


@router.get("/session/status", response_model=SessionStatusResponse)
async def get_session_status():
    info = SessionManager.get_session_info()
    return SessionStatusResponse(**info)


@router.post("/session/start", response_model=StartSessionResponse)
async def start_interactive_session(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Abre o Chromium para o usuário fazer login no Instagram. Salva a sessão permanentemente."""
    engine = PlaywrightEngine(TaskDAO(db), MediaDAO(db))
    background_tasks.add_task(engine.run_interactive_login)
    return StartSessionResponse(
        status="started",
        message="Navegador aberto. Faça login no Instagram. A sessão será salva automaticamente.",
    )


@router.post("/import-cookies")
async def import_cookies(req: ImportCookiesRequest):
    """Importa cookies manualmente (sessionid / raw / storage_state)."""
    if req.session_id:
        success = SessionManager.import_session_id(req.session_id, req.ds_user_id)
        if success:
            return {"success": True, "message": "Cookie sessionid importado com sucesso!"}

    if req.raw_cookies:
        success = SessionManager.import_raw_cookie_header(req.raw_cookies)
        if success:
            return {"success": True, "message": "Cookies brutos importados com sucesso!"}

    if req.storage_state_json:
        success = SessionManager.import_storage_state(req.storage_state_json)
        if success:
            return {"success": True, "message": "Storage state importado com sucesso!"}

    raise HTTPException(
        status_code=400,
        detail="Nenhum cookie ou sessionid válido foi fornecido.",
    )


@router.delete("/session")
async def clear_session():
    success = SessionManager.delete_session()
    return {
        "success": success,
        "message": "Sessão removida." if success else "Nenhuma sessão ativa.",
    }

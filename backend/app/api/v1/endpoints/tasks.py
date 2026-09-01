import asyncio
import threading
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db, AsyncSessionLocal
from app.dao.task_dao import TaskDAO
from app.dao.media_dao import MediaDAO
from app.services.playwright_engine import PlaywrightEngine
from app.schemas.task import TaskCreateRequest, TaskStatusResponse, TaskListResponse

router = APIRouter()


def _run_scraping_in_thread(task_id: str, thread_url: str, max_scrolls: int, headless: bool):
    """
    Roda o Playwright em uma thread separada com seu próprio event loop.
    Necessário no Windows: asyncio.BackgroundTasks não suporta create_subprocess_exec
    no ProactorEventLoop do uvicorn. A thread cria um SelectorEventLoop próprio.
    """
    async def _job():
        async with AsyncSessionLocal() as session:
            task_dao = TaskDAO(session)
            media_dao = MediaDAO(session)
            engine = PlaywrightEngine(task_dao, media_dao)
            await engine.process_task(
                task_id, thread_url,
                max_scrolls=max_scrolls,
                headless=headless
            )

    # No Windows, subprocessos (como o Playwright) precisam de ProactorEventLoop
    import sys
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_job())
    finally:
        loop.close()


@router.post("/start", response_model=TaskStatusResponse)
async def start_task(
    request: TaskCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    thread_url = request.thread_url.strip()
    if not thread_url:
        raise HTTPException(status_code=400, detail="A URL da conversa nao pode ser vazia.")

    task_dao = TaskDAO(db)
    thread_id = PlaywrightEngine.extract_thread_id_from_url(thread_url)

    max_scrolls = request.max_scrolls or 150
    headless = request.headless

    # Cria registro da tarefa no banco
    task = await task_dao.create(
        thread_url=thread_url,
        thread_id=thread_id,
        status="pending",
        progress=0,
        total_downloaded=0,
    )

    # Lança em thread dedicada (com ProactorEventLoop no Windows)
    t = threading.Thread(
        target=_run_scraping_in_thread,
        args=(task.id, thread_url, max_scrolls, headless),
        daemon=True,
    )
    t.start()

    return task


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    task_dao = TaskDAO(db)
    task = await task_dao.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa nao encontrada.")
    return task


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    task_dao = TaskDAO(db)
    tasks = await task_dao.get_recent_tasks(limit=limit)
    return TaskListResponse(tasks=tasks)

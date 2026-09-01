import os
import pathlib

base_dir = r"c:\Users\Ian Santos\Desktop\VSCODE\DirectGrabber\backend"
os.makedirs(base_dir, exist_ok=True)

files = {
    "requirements.txt": """fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.30
aiosqlite==0.20.0
pydantic==2.7.1
pydantic-settings==2.2.1
playwright==1.44.0
httpx==0.27.0
python-dotenv==1.0.1
aiofiles==23.2.1
python-multipart==0.0.9
""",

    ".env.example": """DATABASE_URL=sqlite+aiosqlite:///./directgrabber.db
SESSIONS_DIR=assets/sessions
DOWNLOADS_DIR=storage/downloads
CORS_ORIGINS=["http://localhost:5173"]
""",

    "app/__init__.py": "",
    "app/core/__init__.py": "",
    "app/core/config.py": """import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./directgrabber.db"
    sessions_dir: str = "assets/sessions"
    downloads_dir: str = "storage/downloads"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    app_name: str = "DirectGrabber"
    app_version: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def session_file_path(self) -> Path:
        return Path(self.sessions_dir) / "session.json"

settings = Settings()
""",
    "app/db/__init__.py": "",
    "app/db/database.py": """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
""",
    "app/db/models.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from app.db.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class DownloadTask(Base):
    __tablename__ = "download_tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_url = Column(String, nullable=False)
    thread_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    total_found = Column(Integer, default=0)
    total_downloaded = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class MediaItem(Base):
    __tablename__ = "media_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("download_tasks.id"))
    thread_id = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    original_url = Column(Text, nullable=False)
    media_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utcnow)
""",
    "app/dao/__init__.py": "",
    "app/dao/base.py": """from typing import TypeVar, Generic, Type, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseDAO(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db = db_session

    async def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        stmt = select(self.model).filter(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, obj: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        await self.db.delete(obj)
        await self.db.commit()
""",
    "app/dao/task_dao.py": """from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.dao.base import BaseDAO
from app.db.models import DownloadTask

class TaskDAO(BaseDAO[DownloadTask]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(DownloadTask, db_session)

    async def get_by_thread_id(self, thread_id: str) -> Optional[DownloadTask]:
        stmt = select(DownloadTask).filter(DownloadTask.thread_id == thread_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_status(self, task_id: str, status: str, error_message: str = None) -> Optional[DownloadTask]:
        task = await self.get_by_id(task_id)
        if task:
            task.status = status
            if error_message is not None:
                task.error_message = error_message
            await self.db.commit()
            await self.db.refresh(task)
        return task

    async def update_progress(self, task_id: str, progress: int, total_found: int, total_downloaded: int) -> Optional[DownloadTask]:
        task = await self.get_by_id(task_id)
        if task:
            task.progress = progress
            task.total_found = total_found
            task.total_downloaded = total_downloaded
            await self.db.commit()
            await self.db.refresh(task)
        return task

    async def get_recent(self, limit: int = 20) -> List[DownloadTask]:
        stmt = select(DownloadTask).order_by(desc(DownloadTask.created_at)).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
""",
    "app/dao/media_dao.py": """from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.dao.base import BaseDAO
from app.db.models import MediaItem

class MediaDAO(BaseDAO[MediaItem]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(MediaItem, db_session)

    async def get_by_task_id(self, task_id: str) -> List[MediaItem]:
        stmt = select(MediaItem).filter(MediaItem.task_id == task_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_thread_id(self, thread_id: str) -> List[MediaItem]:
        stmt = select(MediaItem).filter(MediaItem.thread_id == thread_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def exists_by_url(self, original_url: str) -> bool:
        stmt = select(MediaItem).filter(MediaItem.original_url == original_url)
        result = await self.db.execute(stmt)
        return result.scalars().first() is not None

    async def count_by_thread(self, thread_id: str) -> int:
        stmt = select(func.count(MediaItem.id)).filter(MediaItem.thread_id == thread_id)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
""",
    "app/schemas/__init__.py": "",
    "app/schemas/auth.py": """from pydantic import BaseModel

class SessionStatus(BaseModel):
    exists: bool
    path: str
    valid: bool
    message: str

class SessionCreateResponse(BaseModel):
    success: bool
    message: str
""",
    "app/schemas/task.py": """from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, List

class TaskCreate(BaseModel):
    thread_url: str
    
    @field_validator("thread_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if "instagram.com/direct/t/" not in v:
            raise ValueError("Must be a valid Instagram Direct thread URL")
        return v

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    thread_url: str
    thread_id: Optional[str]
    status: str
    progress: int
    total_found: int
    total_downloaded: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
""",
    "app/schemas/media.py": """from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class MediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    task_id: str
    thread_id: str
    file_path: str
    file_name: str
    original_url: str
    media_type: str
    file_size: Optional[int]
    created_at: datetime

class MediaListResponse(BaseModel):
    items: List[MediaResponse]
    total: int
    thread_id: Optional[str] = None
""",
    "app/services/__init__.py": "",
    "app/services/session_manager.py": """import os
import json
from pathlib import Path
from app.core.config import settings

class SessionManager:
    def __init__(self):
        self.settings = settings
        
    def session_exists(self) -> bool:
        return self.settings.session_file_path.exists()
        
    def get_session_info(self) -> dict:
        exists = self.session_exists()
        if not exists:
            return {"exists": False, "path": str(self.settings.session_file_path), "size": 0, "mtime": 0}
        
        stat = self.settings.session_file_path.stat()
        return {
            "exists": True,
            "path": str(self.settings.session_file_path),
            "size": stat.st_size,
            "mtime": stat.st_mtime
        }
        
    def delete_session(self) -> None:
        if self.session_exists():
            self.settings.session_file_path.unlink()
            
    def get_storage_state_path(self) -> Path:
        return self.settings.session_file_path
""",
    "app/services/playwright_engine.py": """import asyncio
import re
import random
from typing import Set, Tuple, Callable, Awaitable
from playwright.async_api import async_playwright, Page, Response
from app.core.config import settings
from app.services.session_manager import SessionManager

class PlaywrightEngine:
    def __init__(self):
        self.session_manager = SessionManager()
        
    async def save_session_async(self):
        print(f"[DirectGrabber] Iniciando salvamento de sessão...")
        settings.session_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("https://www.instagram.com/")
            print(f"[DirectGrabber] Por favor, faça login no Instagram na janela que abriu.")
            print(f"[DirectGrabber] O navegador fechará e a sessão será salva quando terminar (aguardando 60 segundos por padrão, ou até fechar).")
            try:
                await page.wait_for_timeout(60000)
            except Exception:
                pass
            await context.storage_state(path=settings.session_file_path)
            await browser.close()
            print(f"[DirectGrabber] Sessão salva em {settings.session_file_path}")

    def save_session(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.save_session_async())
        loop.close()

    async def extract_media(self, task_id: str, thread_url: str, progress_callback: Callable[[int, int], Awaitable[None]]) -> Set[Tuple[str, str]]:
        found_media = set()
        print(f"[DirectGrabber] Iniciando extração para tarefa {task_id}")
        
        async with async_playwright() as p:
            storage_state = str(settings.session_file_path) if self.session_manager.session_exists() else None
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state=storage_state)
            page = await context.new_page()
            
            async def handle_response(response: Response):
                url = response.url
                if "cdninstagram.com" in url:
                    if ".mp4" in url:
                        found_media.add((url, "video"))
                    elif (".jpg" in url or ".jpeg" in url) and not any(x in url for x in ["s150x150", "s320x320"]):
                        found_media.add((url, "image"))
                
                if response.request.resource_type in ["fetch", "xhr"]:
                    try:
                        content_type = response.headers.get("content-type", "")
                        if "application/json" in content_type:
                            json_data = await response.json()
                            self._extract_from_json(json_data, found_media)
                    except Exception:
                        pass
            
            page.on("response", handle_response)
            
            print(f"[DirectGrabber] Navegando para {thread_url}")
            await page.goto(thread_url, wait_until="networkidle")
            
            attempts_without_new = 0
            while attempts_without_new < 3:
                count_before = len(found_media)
                await page.evaluate("window.scrollBy(0, -1000)")
                await asyncio.sleep(random.uniform(1.5, 3.5))
                
                imgs = await page.query_selector_all("img[src*='cdninstagram.com']")
                for img in imgs:
                    src = await img.get_attribute("src")
                    if src and not any(x in src for x in ["s150x150", "s320x320"]):
                        found_media.add((src, "image"))
                        
                videos = await page.query_selector_all("video source[src]")
                for video in videos:
                    src = await video.get_attribute("src")
                    if src:
                        found_media.add((src, "video"))
                
                if len(found_media) > count_before:
                    attempts_without_new = 0
                    await progress_callback(len(found_media), 0)
                else:
                    attempts_without_new += 1
            
            await browser.close()
            return found_media

    def _extract_from_json(self, data: dict, found_media: set) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "video_url" and isinstance(value, str):
                    found_media.add((value, "video"))
                elif key == "display_url" and isinstance(value, str):
                    found_media.add((value, "image"))
                elif key == "image_versions2" and isinstance(value, dict):
                    candidates = value.get("candidates", [])
                    if candidates and isinstance(candidates, list):
                        found_media.add((candidates[0]["url"], "image"))
                else:
                    self._extract_from_json(value, found_media)
        elif isinstance(data, list):
            for item in data:
                self._extract_from_json(item, found_media)
""",
    "app/services/media_downloader.py": """import os
import uuid
import time
from typing import List, Tuple, Callable, Awaitable
import httpx
from app.core.config import settings

class MediaDownloader:
    async def download_media(self, url: str, thread_id: str, task_id: str, media_type: str) -> dict:
        target_dir = os.path.join(settings.downloads_dir, thread_id)
        os.makedirs(target_dir, exist_ok=True)
        
        timestamp = int(time.time())
        short_uuid = str(uuid.uuid4())[:8]
        ext = ".mp4" if media_type == "video" else ".jpg"
        file_name = f"{timestamp}_{short_uuid}{ext}"
        file_path = os.path.join(target_dir, file_name)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        file_size = 0
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(response.content)
                file_size = os.path.getsize(file_path)
        except Exception as e:
            print(f"[DirectGrabber] Erro ao baixar {url}: {e}")
            raise
            
        return {
            "file_path": file_path,
            "file_name": file_name,
            "file_size": file_size
        }

    async def download_batch(self, urls_with_types: List[Tuple[str, str]], thread_id: str, task_id: str, progress_callback: Callable[[int], Awaitable[None]]) -> List[dict]:
        results = []
        downloaded = 0
        for url, media_type in urls_with_types:
            try:
                res = await self.download_media(url, thread_id, task_id, media_type)
                res["original_url"] = url
                res["media_type"] = media_type
                results.append(res)
                downloaded += 1
                await progress_callback(downloaded)
            except Exception:
                continue
        return results
""",
    "app/api/__init__.py": "",
    "app/api/v1/__init__.py": "",
    "app/api/v1/endpoints/__init__.py": "",
    "app/api/v1/endpoints/auth.py": """from fastapi import APIRouter, BackgroundTasks
from app.schemas.auth import SessionStatus, SessionCreateResponse
from app.services.session_manager import SessionManager
from app.services.playwright_engine import PlaywrightEngine

router = APIRouter()
session_manager = SessionManager()
engine = PlaywrightEngine()

@router.get("/session/status", response_model=SessionStatus)
async def get_session_status():
    info = session_manager.get_session_info()
    return SessionStatus(
        exists=info["exists"],
        path=info["path"],
        valid=info["exists"],
        message="Session found" if info["exists"] else "Session not found"
    )

@router.post("/session/save", response_model=SessionCreateResponse)
async def save_session(background_tasks: BackgroundTasks):
    background_tasks.add_task(engine.save_session)
    return SessionCreateResponse(success=True, message="Navegador aberto para login e salvamento de sessão")

@router.delete("/session")
async def delete_session():
    session_manager.delete_session()
    return {"success": True}
""",
    "app/api/v1/endpoints/tasks.py": """import asyncio
import re
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse
from app.db.database import get_db, AsyncSessionLocal
from app.db.models import DownloadTask, MediaItem
from app.dao.task_dao import TaskDAO
from app.dao.media_dao import MediaDAO
from app.services.playwright_engine import PlaywrightEngine
from app.services.media_downloader import MediaDownloader
import concurrent.futures

router = APIRouter()

def run_extraction_sync(task_id: str, thread_url: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def extract_and_download():
        async with AsyncSessionLocal() as db:
            task_dao = TaskDAO(db)
            media_dao = MediaDAO(db)
            
            task = await task_dao.get_by_id(task_id)
            if not task:
                return
            
            await task_dao.update_status(task_id, "processing")
            
            match = re.search(r'direct/t/(\d+)', thread_url)
            thread_id = match.group(1) if match else "unknown"
            await task_dao.update(task, thread_id=thread_id)
            
            engine = PlaywrightEngine()
            
            async def progress_cb(found: int, downloaded: int):
                await task_dao.update_progress(task_id, 0, found, downloaded)
                
            try:
                found_media = await engine.extract_media(task_id, thread_url, progress_cb)
                
                downloader = MediaDownloader()
                
                async def download_cb(downloaded: int):
                    await task_dao.update_progress(task_id, 0, len(found_media), downloaded)
                    
                results = await downloader.download_batch(list(found_media), thread_id, task_id, download_cb)
                
                for res in results:
                    media = MediaItem(
                        task_id=task_id,
                        thread_id=thread_id,
                        file_path=res["file_path"],
                        file_name=res["file_name"],
                        original_url=res["original_url"],
                        media_type=res["media_type"],
                        file_size=res["file_size"]
                    )
                    await media_dao.create(media)
                    
                await task_dao.update_status(task_id, "completed")
            except Exception as e:
                print(f"[DirectGrabber] Erro na extração: {e}")
                await task_dao.update_status(task_id, "failed", str(e))
                
    loop.run_until_complete(extract_and_download())
    loop.close()

def extract_and_download_task(task_id: str, thread_url: str):
    with concurrent.futures.ThreadPoolExecutor() as pool:
        pool.submit(run_extraction_sync, task_id, thread_url)

@router.post("/start", response_model=TaskResponse)
async def start_task(task_in: TaskCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    task_dao = TaskDAO(db)
    new_task = DownloadTask(thread_url=task_in.thread_url)
    await task_dao.create(new_task)
    
    background_tasks.add_task(extract_and_download_task, new_task.id, task_in.thread_url)
    
    return new_task

@router.get("/{task_id}/status", response_model=TaskResponse)
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_db)):
    task_dao = TaskDAO(db)
    task = await task_dao.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/", response_model=TaskListResponse)
async def list_tasks(db: AsyncSession = Depends(get_db)):
    task_dao = TaskDAO(db)
    tasks = await task_dao.get_recent()
    return TaskListResponse(tasks=tasks, total=len(tasks))
""",
    "app/api/v1/endpoints/media.py": """from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.media import MediaResponse, MediaListResponse
from app.db.database import get_db
from app.dao.media_dao import MediaDAO
import os

router = APIRouter()

@router.get("/", response_model=MediaListResponse)
async def list_media(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    media_dao = MediaDAO(db)
    items = await media_dao.list_all(limit=limit, offset=skip)
    return MediaListResponse(items=items, total=len(items))

@router.get("/thread/{thread_id}", response_model=MediaListResponse)
async def list_media_by_thread(thread_id: str, db: AsyncSession = Depends(get_db)):
    media_dao = MediaDAO(db)
    items = await media_dao.get_by_thread_id(thread_id)
    return MediaListResponse(items=items, total=len(items), thread_id=thread_id)

@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(media_id: str, db: AsyncSession = Depends(get_db)):
    media_dao = MediaDAO(db)
    item = await media_dao.get_by_id(media_id)
    if not item:
        raise HTTPException(status_code=404, detail="Media not found")
    return item

@router.get("/{media_id}/file")
async def get_media_file(media_id: str, db: AsyncSession = Depends(get_db)):
    media_dao = MediaDAO(db)
    item = await media_dao.get_by_id(media_id)
    if not item or not os.path.exists(item.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(item.file_path, filename=item.file_name)
""",
    "app/api/v1/router.py": """from fastapi import APIRouter
from app.api.v1.endpoints import auth, tasks, media

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(media.router, prefix="/media", tags=["media"])
""",
    "app/main.py": """from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import create_tables
from app.api.v1.router import router as v1_router
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.sessions_dir, exist_ok=True)
    os.makedirs(settings.downloads_dir, exist_ok=True)
    await create_tables()
    yield

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=settings.cors_origins, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

app.include_router(v1_router, prefix="/api/v1")
""",
    "Dockerfile": """FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium --with-deps
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "assets/sessions/.gitkeep": "",
    "storage/downloads/.gitkeep": "",
    "tests/__init__.py": ""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Successfully created DirectGrabber backend files.")

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.database import Base
from app.db.models import DownloadTask, MediaItem
from app.dao.task_dao import TaskDAO
from app.dao.media_dao import MediaDAO

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_task_dao_crud(db_session: AsyncSession):
    task_dao = TaskDAO(db_session)
    task = await task_dao.create(
        thread_url="https://www.instagram.com/direct/t/123456789/",
        thread_id="123456789",
        status="pending"
    )
    assert task.id is not None
    assert task.status == "pending"

    # Atualização de status
    updated = await task_dao.update_status(task.id, status="processing", progress=50, total_downloaded=5)
    assert updated.status == "processing"
    assert updated.progress == 50
    assert updated.total_downloaded == 5

@pytest.mark.asyncio
async def test_media_dao_crud(db_session: AsyncSession):
    media_dao = MediaDAO(db_session)
    item = await media_dao.create(
        thread_id="test_thread",
        file_path="downloads/test_thread/sample.mp4",
        original_url="https://cdninstagram.com/sample.mp4",
        media_type="video",
        file_size=102400
    )
    assert item.id is not None
    assert item.media_type == "video"

    items = await media_dao.get_by_thread("test_thread")
    assert len(items) == 1
    assert items[0].file_size == 102400

    exists = await media_dao.exists_by_url("https://cdninstagram.com/sample.mp4")
    assert exists is True

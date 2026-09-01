import os
import re
import uuid
import httpx
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.dao.media_dao import MediaDAO
from app.db.models import MediaItem


class MediaDownloader:
    def __init__(self, media_dao: MediaDAO):
        self.media_dao = media_dao
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.instagram.com/",
        }

    @staticmethod
    def _sanitize(raw_id: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_-]', '_', raw_id)

    async def download_and_save(
        self,
        media_url: str,
        thread_id: str,
        task_id: Optional[str] = None,
        media_type: str = "image"
    ) -> Optional[MediaItem]:
        """Baixa uma mídia e salva no disco + banco de dados."""

        # Verifica duplicatas pelo URL original
        if await self.media_dao.exists_by_url(media_url):
            print(f"[Downloader] Já existe no banco, pulando: {media_url[:80]}")
            return None

        clean_id = self._sanitize(thread_id)
        thread_dir = settings.DOWNLOADS_DIR / clean_id
        thread_dir.mkdir(parents=True, exist_ok=True)

        # Determina extensão correta
        url_lower = media_url.lower().split("?")[0]  # ignora query string para detectar ext
        if ".mp4" in url_lower or media_type == "video":
            ext = "mp4"
        elif ".png" in url_lower:
            ext = "png"
        elif ".webp" in url_lower:
            ext = "webp"
        else:
            ext = "jpg"

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_suffix = uuid.uuid4().hex[:8]
        filename = f"{timestamp}_{unique_suffix}.{ext}"
        target_path = thread_dir / filename

        try:
            async with httpx.AsyncClient(
                timeout=60.0,
                follow_redirects=True,
                headers=self.headers
            ) as client:
                response = await client.get(media_url)
                if response.status_code != 200:
                    print(f"[Downloader] HTTP {response.status_code} para {media_url[:80]}")
                    return None

                content = response.content
                file_size = len(content)

                if file_size < 1024:  # Ignora arquivos menores que 1KB (provavelmente erros)
                    print(f"[Downloader] Arquivo muito pequeno ({file_size}B), ignorando.")
                    return None

            # Salva no disco
            async with aiofiles.open(target_path, "wb") as f:
                await f.write(content)

            print(f"[Downloader] ✅ Salvo: {filename} ({file_size // 1024}KB) [{media_type}]")

            relative_path = f"downloads/{clean_id}/{filename}"

            media_item = await self.media_dao.create(
                task_id=task_id,
                thread_id=clean_id,
                file_path=relative_path,
                original_url=media_url,
                media_type=media_type,
                file_size=file_size
            )
            return media_item

        except Exception as e:
            print(f"[Downloader] ❌ Erro ao baixar {media_url[:80]}: {e}")
            if target_path.exists():
                try:
                    target_path.unlink()
                except Exception:
                    pass
            return None

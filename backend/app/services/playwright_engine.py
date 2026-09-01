import asyncio
import json
import random
import re
import sys
from typing import Set, Tuple, Optional, Any
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Page
from app.core.config import settings
from app.dao.task_dao import TaskDAO
from app.dao.media_dao import MediaDAO
from app.services.media_downloader import MediaDownloader
from app.db.models import TaskStatusEnum

# Força UTF-8 no stdout para evitar UnicodeEncodeError no Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# CDN do Instagram/Facebook
CDN_HOSTS = ("cdninstagram.com", "fbcdn.net")

# Padroes de thumbnails/avatares para ignorar
SKIP_PATTERNS = (
    "s150x150", "s320x320", "s640x640",
    "t51.2885-19",   # avatar de perfil
    "/emoji/",
    "static.cdninstagram.com/rsrc",
    "44x44",
    "e35",           # icone pequeno
)


def _is_cdn(url: str) -> bool:
    return any(h in url for h in CDN_HOSTS)


def _is_skip(url: str) -> bool:
    return any(p in url for p in SKIP_PATTERNS)


def log(msg: str):
    """Print seguro para Windows (evita UnicodeEncodeError com emojis)."""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        try:
            safe = msg.encode("ascii", "replace").decode("ascii")
            print(safe, flush=True)
        except Exception:
            pass


class PlaywrightEngine:
    def __init__(self, task_dao: TaskDAO, media_dao: MediaDAO):
        self.task_dao = task_dao
        self.media_dao = media_dao
        self.downloader = MediaDownloader(media_dao)

    @staticmethod
    def extract_thread_id_from_url(url: str) -> str:
        match = re.search(r"/direct/t/([0-9a-zA-Z_-]+)", url)
        if match:
            return match.group(1)
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split("/") if p]
        return parts[-1] if parts else "unknown_thread"

    # ------------------------------------------------------------------
    # Login interativo
    # ------------------------------------------------------------------
    async def run_interactive_login(self, timeout_seconds: int = 300) -> bool:
        settings.PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(settings.PROFILE_DIR),
                headless=False,
                viewport={"width": 1280, "height": 850},
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
            )
            page = context.pages[0] if context.pages else await context.new_page()
            log("[Login] Abrindo Instagram no perfil persistente...")
            await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")

            start = asyncio.get_event_loop().time()
            logged_in = False
            while (asyncio.get_event_loop().time() - start) < timeout_seconds:
                cookies = await context.cookies()
                has_session = any(c["name"] == "sessionid" for c in cookies)
                if has_session and "accounts/login" not in page.url:
                    log("[Login] Sessao ativa detectada!")
                    logged_in = True
                    settings.SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
                    await context.storage_state(path=str(settings.SESSION_FILE))
                    break
                await asyncio.sleep(2)

            await context.close()
            return logged_in

    # ------------------------------------------------------------------
    # Processo principal de extracao
    # ------------------------------------------------------------------
    async def process_task(
        self,
        task_id: str,
        thread_url: str,
        max_scrolls: int = 150,
        headless: bool = False,
    ):
        thread_id = self.extract_thread_id_from_url(thread_url)
        log(f"\n[Engine] === Iniciando extracao ===")
        log(f"[Engine] Thread: {thread_id}")
        log(f"[Engine] URL: {thread_url}")
        log(f"[Engine] Max scrolls: {max_scrolls} | headless: {headless}")

        await self.task_dao.update_status(
            task_id=task_id,
            status=TaskStatusEnum.PROCESSING,
            progress=5,
            thread_id=thread_id,
        )

        has_profile = (
            settings.PROFILE_DIR.exists()
            and any(settings.PROFILE_DIR.iterdir())
        )
        has_file = (
            settings.SESSION_FILE.exists()
            and settings.SESSION_FILE.stat().st_size > 0
        )

        if not (has_profile or has_file):
            await self.task_dao.update_status(
                task_id=task_id,
                status=TaskStatusEnum.FAILED,
                error_message="Nenhuma sessao salva. Clique em 'Conectar Instagram' primeiro.",
            )
            return

        discovered_media: Set[Tuple[str, str]] = set()

        try:
            async with async_playwright() as p:
                if has_profile:
                    log(f"[Engine] Usando perfil persistente: {settings.PROFILE_DIR}")
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=str(settings.PROFILE_DIR),
                        headless=headless,
                        viewport={"width": 1280, "height": 900},
                        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
                    )
                    page = context.pages[0] if context.pages else await context.new_page()
                else:
                    log(f"[Engine] Usando storage_state: {settings.SESSION_FILE}")
                    browser = await p.chromium.launch(
                        headless=headless,
                        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                    )
                    context = await browser.new_context(
                        storage_state=str(settings.SESSION_FILE),
                        viewport={"width": 1280, "height": 900},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
                    )
                    page = await context.new_page()

                # Interceptador de rede
                async def handle_response(response):
                    try:
                        url = response.url
                        if response.status not in (200, 206):
                            return
                        ct = response.headers.get("content-type", "")

                        if (".mp4" in url or "video/mp4" in ct):
                            if _is_cdn(url) and not _is_skip(url):
                                discovered_media.add((url, "video"))
                                log(f"[Net] VIDEO: {url[:90]}")

                        elif any(t in ct for t in ("image/jpeg", "image/png", "image/webp")):
                            if _is_cdn(url) and not _is_skip(url):
                                discovered_media.add((url, "image"))
                                log(f"[Net] IMG: {url[:90]}")

                        elif "application/json" in ct:
                            if "graphql" in url or "/api/v1/direct" in url or "direct_v2" in url:
                                try:
                                    body = await response.body()
                                    data = json.loads(body)
                                    before = len(discovered_media)
                                    self._extract_urls_from_json(data, discovered_media)
                                    added = len(discovered_media) - before
                                    if added:
                                        log(f"[Net] JSON payload +{added} midias")
                                except Exception:
                                    pass
                    except Exception:
                        pass

                page.on("response", handle_response)

                # Navega para a conversa
                log(f"[Engine] Navegando para: {thread_url}")
                try:
                    await page.goto(thread_url, wait_until="networkidle", timeout=60000)
                except Exception:
                    pass  # timeout de networkidle nao e fatal

                await page.wait_for_timeout(5000)
                await self.task_dao.update_status(
                    task_id=task_id, status=TaskStatusEnum.PROCESSING, progress=15
                )

                # Localiza o container de mensagens
                chat_sel = await self._find_chat_container(page)
                log(f"[Engine] Container de chat: {chat_sel}")

                # Loop de scroll retroativo
                log(f"[Engine] Iniciando backtracking (max_scrolls={max_scrolls})...")
                last_count = len(discovered_media)
                no_new = 0
                reached_start = False

                for step in range(1, max_scrolls + 1):
                    # Rola para cima no container ou na pagina inteira
                    if chat_sel:
                        await page.evaluate(
                            "(sel) => { const el = document.querySelector(sel); if (el) el.scrollTop = 0; }",
                            chat_sel,
                        )
                    else:
                        # Rola todos os divs scrollaveis para cima
                        await page.evaluate("""() => {
                            Array.from(document.querySelectorAll('div'))
                                .filter(d => {
                                    const s = window.getComputedStyle(d);
                                    return (s.overflowY === 'auto' || s.overflowY === 'scroll')
                                        && d.scrollHeight > d.clientHeight + 10;
                                })
                                .forEach(d => { d.scrollTop = 0; });
                        }""")

                    # PageUp via teclado
                    await page.keyboard.press("PageUp")
                    await page.keyboard.press("PageUp")

                    # Aguarda carregamento de mensagens antigas
                    await asyncio.sleep(random.uniform(2.0, 3.2))

                    # Varre DOM
                    await self._scrape_dom_media(page, discovered_media)

                    # Detecta inicio da conversa
                    reached_start = await self._detect_chat_start(page)

                    cur = len(discovered_media)
                    prog = min(15 + int((step / max_scrolls) * 60), 75)
                    await self.task_dao.update_status(
                        task_id=task_id,
                        status=TaskStatusEnum.PROCESSING,
                        progress=prog,
                        total_downloaded=cur,
                    )
                    log(
                        f"[Engine] Scroll {step}/{max_scrolls} | midias={cur} | inicio={'SIM' if reached_start else 'nao'}"
                    )

                    if cur == last_count:
                        no_new += 1
                        if reached_start or no_new >= 6:
                            log(f"[Engine] Fim do historico no passo {step}.")
                            break
                    else:
                        no_new = 0
                        last_count = cur

                await context.close()

            log(f"\n[Engine] Total de midias descobertas: {len(discovered_media)}")

            if not discovered_media:
                log("[Engine] AVISO: Nenhuma midia encontrada.")
                await self.task_dao.update_status(
                    task_id=task_id,
                    status=TaskStatusEnum.COMPLETED,
                    progress=100,
                    total_downloaded=0,
                )
                return

            await self.task_dao.update_status(
                task_id=task_id, status=TaskStatusEnum.PROCESSING, progress=75
            )

            downloaded = 0
            total = len(discovered_media)
            for idx, (url, mtype) in enumerate(discovered_media, 1):
                item = await self.downloader.download_and_save(
                    media_url=url,
                    thread_id=thread_id,
                    task_id=task_id,
                    media_type=mtype,
                )
                if item:
                    downloaded += 1
                prog = 75 + int((idx / total) * 24)
                await self.task_dao.update_status(
                    task_id=task_id,
                    status=TaskStatusEnum.PROCESSING,
                    progress=prog,
                    total_downloaded=downloaded,
                )

            await self.task_dao.update_status(
                task_id=task_id,
                status=TaskStatusEnum.COMPLETED,
                progress=100,
                total_downloaded=downloaded,
            )
            log(f"[Engine] CONCLUIDO! Baixadas {downloaded}/{total} midias.")

        except Exception as e:
            import traceback
            traceback.print_exc()
            log(f"[Engine] ERRO FATAL: {e}")
            await self.task_dao.update_status(
                task_id=task_id,
                status=TaskStatusEnum.FAILED,
                error_message=str(e)[:500],
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    async def _find_chat_container(self, page: Page) -> Optional[str]:
        """Encontra o seletor CSS do container scrollavel de mensagens."""
        candidates = [
            "div[role='grid']",
            "div[role='listbox']",
            "div[data-pagelet='DirectThreadMessageList']",
            "main > div > div > div > div > div",
        ]
        for sel in candidates:
            try:
                is_ok = await page.evaluate(
                    """(s) => {
                        const el = document.querySelector(s);
                        if (!el) return false;
                        const st = window.getComputedStyle(el);
                        return el.scrollHeight > el.clientHeight + 30
                            && (st.overflowY === 'auto' || st.overflowY === 'scroll' || st.overflow === 'auto');
                    }""",
                    sel,
                )
                if is_ok:
                    log(f"[Engine] Container encontrado: {sel}")
                    return sel
            except Exception:
                pass

        # Fallback dinamico: maior div scrollavel
        try:
            result = await page.evaluate("""() => {
                let best = null, bestH = 0;
                document.querySelectorAll('div').forEach(d => {
                    const s = window.getComputedStyle(d);
                    if ((s.overflowY === 'auto' || s.overflowY === 'scroll')
                            && d.scrollHeight > d.clientHeight + 30
                            && d.scrollHeight > bestH) {
                        bestH = d.scrollHeight;
                        best = d.className ? '.' + d.className.trim().split(/\s+/)[0] : null;
                    }
                });
                return best;
            }""")
            if result:
                log(f"[Engine] Container dinamico: {result}")
                return result
        except Exception:
            pass

        log("[Engine] Container nao localizado, usando scroll global.")
        return None

    async def _detect_chat_start(self, page: Page) -> bool:
        try:
            return await page.evaluate("""() => {
                const kws = ['ver perfil', 'view profile', 'inicio da conversa',
                             'you started a conversation', 'comecar a conversar',
                             'vocês são amigos', 'foram conectados'];
                const els = Array.from(document.querySelectorAll('span, div, p, a, h1, h2, h3'));
                return els.some(el => {
                    const t = (el.innerText || el.textContent || '').toLowerCase().trim();
                    return kws.some(k => t.includes(k)) && t.length < 120;
                });
            }""")
        except Exception:
            return False

    async def _scrape_dom_media(self, page: Page, media_set: Set[Tuple[str, str]]):
        try:
            imgs = await page.evaluate("""() =>
                Array.from(document.querySelectorAll('img'))
                    .map(i => i.src)
                    .filter(s => s && (s.includes('cdninstagram.com') || s.includes('fbcdn.net')))
            """)
            for src in imgs:
                if not _is_skip(src):
                    media_set.add((src, "image"))

            videos = await page.evaluate("""() => {
                const out = [];
                document.querySelectorAll('video').forEach(v => {
                    if (v.src) out.push(v.src);
                    v.querySelectorAll('source').forEach(s => { if (s.src) out.push(s.src); });
                });
                return out.filter(s => s && (s.includes('cdninstagram.com') || s.includes('fbcdn.net') || s.includes('.mp4')));
            }""")
            for src in videos:
                media_set.add((src, "video"))
        except Exception:
            pass

    def _extract_urls_from_json(self, data: Any, media_set: Set[Tuple[str, str]]):
        if isinstance(data, dict):
            if "video_versions" in data and isinstance(data["video_versions"], list):
                if data["video_versions"]:
                    v = data["video_versions"][0]
                    if isinstance(v, dict) and "url" in v:
                        media_set.add((v["url"], "video"))

            if "image_versions2" in data and isinstance(data["image_versions2"], dict):
                cands = data["image_versions2"].get("candidates", [])
                if cands:
                    c = cands[0]
                    if isinstance(c, dict) and "url" in c and not _is_skip(c["url"]):
                        media_set.add((c["url"], "image"))

            for key, val in data.items():
                if isinstance(val, str) and val.startswith("http"):
                    if key in ("video_url", "video_uri"):
                        if _is_cdn(val):
                            media_set.add((val, "video"))
                    elif key in ("display_url", "src", "thumbnail_src"):
                        if _is_cdn(val) and not _is_skip(val):
                            media_set.add((val, "image"))
                elif isinstance(val, (dict, list)):
                    self._extract_urls_from_json(val, media_set)
        elif isinstance(data, list):
            for item in data:
                self._extract_urls_from_json(item, media_set)

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from app.core.config import settings

class SessionManager:
    @staticmethod
    def session_exists() -> bool:
        # Se existe profile_dir com cookies ou session.json
        has_profile = settings.PROFILE_DIR.exists() and any(settings.PROFILE_DIR.iterdir()) if settings.PROFILE_DIR.exists() else False
        has_file = settings.SESSION_FILE.exists() and settings.SESSION_FILE.stat().st_size > 0
        return has_profile or has_file

    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        has_profile = settings.PROFILE_DIR.exists() and any(settings.PROFILE_DIR.iterdir()) if settings.PROFILE_DIR.exists() else False
        has_file = settings.SESSION_FILE.exists() and settings.SESSION_FILE.stat().st_size > 0

        if not (has_profile or has_file):
            return {
                "authenticated": False,
                "session_file_exists": False,
                "last_modified": None,
                "message": "Nenhuma sessão ativa. Faça login uma única vez pelo navegador."
            }

        if has_file:
            try:
                with open(settings.SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cookies = data.get("cookies", [])
                has_sessionid = any(c.get("name") == "sessionid" for c in cookies)
                mtime = datetime.fromtimestamp(settings.SESSION_FILE.stat().st_mtime)
                return {
                    "authenticated": True,
                    "session_file_exists": True,
                    "last_modified": mtime,
                    "message": "Sessão conectada e reconhecida."
                }
            except Exception:
                pass

        if has_profile:
            mtime = datetime.fromtimestamp(settings.PROFILE_DIR.stat().st_mtime)
            return {
                "authenticated": True,
                "session_file_exists": True,
                "last_modified": mtime,
                "message": "Perfil de navegação persistente conectado."
            }

        return {
            "authenticated": False,
            "session_file_exists": False,
            "last_modified": None,
            "message": "Sessão não encontrada."
        }

    @staticmethod
    def import_session_id(session_id: str, ds_user_id: Optional[str] = None) -> bool:
        """Cria um storage_state.json Playwright a partir do sessionid do Instagram."""
        clean_sid = session_id.strip()
        if not clean_sid:
            return False

        cookies = [
            {
                "name": "sessionid",
                "value": clean_sid,
                "domain": ".instagram.com",
                "path": "/",
                "expires": -1,
                "httpOnly": True,
                "secure": True,
                "sameSite": "None"
            }
        ]

        if ds_user_id:
            cookies.append({
                "name": "ds_user_id",
                "value": ds_user_id.strip(),
                "domain": ".instagram.com",
                "path": "/",
                "expires": -1,
                "httpOnly": False,
                "secure": True,
                "sameSite": "None"
            })

        storage_data = {
            "cookies": cookies,
            "origins": []
        }

        settings.SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(storage_data, f, indent=2)

        return True

    @staticmethod
    def import_raw_cookie_header(cookie_header: str) -> bool:
        """Converte uma string no formato 'key1=val1; key2=val2' para cookies do Instagram."""
        cookies = []
        for pair in cookie_header.split(";"):
            if "=" in pair:
                name, val = pair.strip().split("=", 1)
                cookies.append({
                    "name": name.strip(),
                    "value": val.strip(),
                    "domain": ".instagram.com",
                    "path": "/",
                    "expires": -1,
                    "httpOnly": True if name.strip() == "sessionid" else False,
                    "secure": True,
                    "sameSite": "None"
                })

        if not cookies:
            return False

        storage_data = {
            "cookies": cookies,
            "origins": []
        }

        settings.SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(storage_data, f, indent=2)

        return True

    @staticmethod
    def import_storage_state(json_str: str) -> bool:
        """Importa diretamente um storage_state JSON exportado."""
        try:
            data = json.loads(json_str)
            if "cookies" not in data:
                return False
            settings.SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(settings.SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    @staticmethod
    def delete_session() -> bool:
        if SessionManager.session_exists():
            settings.SESSION_FILE.unlink()
            return True
        return False

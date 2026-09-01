from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionStatusResponse(BaseModel):
    authenticated: bool
    session_file_exists: bool
    last_modified: Optional[datetime] = None
    message: str

class StartSessionResponse(BaseModel):
    status: str
    message: str

class LoginCredentialsRequest(BaseModel):
    username: str
    password: str
    two_factor_code: Optional[str] = None

class ImportCookiesRequest(BaseModel):
    session_id: Optional[str] = None
    ds_user_id: Optional[str] = None
    raw_cookies: Optional[str] = None
    storage_state_json: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    requires_2fa: bool = False
    message: str


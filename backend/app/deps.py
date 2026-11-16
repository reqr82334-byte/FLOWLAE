from fastapi import Header, HTTPException
from .config import settings
def require_admin(x_admin_key: str | None = Header(default=None)):
    if not x_admin_key or x_admin_key != settings.admin_api_key or settings.admin_api_key == "change-me":
        raise HTTPException(status_code=403, detail="Admin authentication failed")

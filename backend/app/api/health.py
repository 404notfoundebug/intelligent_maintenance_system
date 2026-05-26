from fastapi import APIRouter

from app.core.config import settings
from app.core.database import check_database_connection

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health_check():
    return {
        "code": 0,
        "message": "service is running",
        "data": {
            "app_name": settings.app_name,
            "app_env": settings.app_env,
            "status": "ok",
        },
    }


@router.get("/db")
def database_health_check():
    ok, message = check_database_connection()
    return {
        "code": 0 if ok else 1,
        "message": message,
        "data": {
            "database": "ok" if ok else "error",
        },
    }

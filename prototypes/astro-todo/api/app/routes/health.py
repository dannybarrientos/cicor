from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.infrastructure.database import get_db

router = APIRouter()


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        db_status = f"error: {exc}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "module": settings.module_name,
        "version": settings.module_version,
        "database": db_status,
    }


@router.get("/meta")
async def meta():
    return {
        "module": settings.module_name,
        "version": settings.module_version,
        "title": f"CICOR – {settings.module_name}",
    }

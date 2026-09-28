from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.session import get_db
from app.config.settings import settings

router = APIRouter(tags=["Health Check"])


@router.get(
    "/health",
    summary="Service Health Check",
    description="Inspect API operational status and database connectivity."
)
def check_health(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as err:
        db_status = f"unhealthy: {str(err)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status
    }

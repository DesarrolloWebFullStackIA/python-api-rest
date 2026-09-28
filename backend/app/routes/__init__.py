from fastapi import APIRouter
from app.routes.categories import router as categories_router
from app.routes.games import router as games_router
from app.routes.health import router as health_router
from app.routes.steam import router as steam_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(categories_router)
api_router.include_router(games_router)
api_router.include_router(health_router)
api_router.include_router(steam_router)

__all__ = ["api_router"]

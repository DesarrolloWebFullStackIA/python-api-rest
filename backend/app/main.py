from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import settings
from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.models.category import Category
from app.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager:
    - Startup: creates database tables and seeds starter categories if empty.
    - Yields control to the running server.
    - Shutdown: clean up resources if needed.
    """
    Base.metadata.create_all(bind=engine)

    # Seed initial categories if newly created
    db = SessionLocal()
    try:
        if db.query(Category).count() == 0:
            starter_categories = [
                Category(name="Action", description="Fast-paced games focusing on combat, reflexes, and physical challenges."),
                Category(name="Role-Playing (RPG)", description="Games emphasizing narrative choices, character progression, and quests."),
                Category(name="Strategy", description="Games that require tactical planning, resource management, and strategic thinking."),
                Category(name="Adventure", description="Exploration and puzzle-focused experiences with strong storytelling."),
                Category(name="Indie", description="Creative and innovative games produced by independent development studios.")
            ]
            db.add_all(starter_categories)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    yield


# Initialize FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API router with /api/v1 prefix
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root_endpoint():
    """
    Root endpoint providing service information, status, and API documentation links.
    """
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1_url": "/api/v1",
        "health_check": "/api/v1/health"
    }


# Mount frontend static files if directory exists
frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_path.is_dir():
    app.mount("/client", StaticFiles(directory=str(frontend_path), html=True), name="client")

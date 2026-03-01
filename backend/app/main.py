"""Entry point for the FastAPI application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .dashboard import router as dashboard_router
from .config import get_settings
from .database import Base, engine
from .scrape_actions import router as scrape_actions_router

settings = get_settings()

async def on_startup() -> None:
    """Create the database schema on app startup."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
@asynccontextmanager
async def lifespan_(app: FastAPI):
    await on_startup()
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan_)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(dashboard_router)
app.include_router(scrape_actions_router)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


def mount_frontend(app: FastAPI) -> None:
    """Mount the built Vue frontend if available."""

    backend_dir = Path(__file__).resolve().parent.parent
    dist_dir = (backend_dir.parent / settings.front_end_dist).resolve()
    if dist_dir.exists():
        app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")
    else:

        @app.get("/")
        async def missing_frontend() -> JSONResponse:  # type: ignore[func-returns-value]
            return JSONResponse(
                {
                    "message": f"Frontend build not found at {dist_dir}. Run `npm run build` inside frontend."
                },
                status_code=200,
            )


mount_frontend(app)

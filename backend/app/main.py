"""Entry point for the FastAPI application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .admin import router as admin_router
from .auth import auth_backend, fastapi_users
from .config import get_settings
from .database import Base, engine
from .models import User
from .schemas import UserCreate, UserRead, UserUpdate

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
current_active_user = fastapi_users.current_user(active=True)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/users",
    tags=["users"],
)
app.include_router(admin_router)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/me", response_model=UserRead)
async def read_current_user(user: User = Depends(current_active_user)) -> User:
    return user


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

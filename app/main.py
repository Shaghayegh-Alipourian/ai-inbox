from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.analysis import router as analysis_router
from app.api.routes.emails import router as emails_router
from app.api.routes.evaluation import router as evaluation_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.db.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(emails_router)
app.include_router(analysis_router)
app.include_router(evaluation_router)
frontend_path = Path(__file__).parent / "frontend"

app.mount(
    "/frontend",
    StaticFiles(directory=frontend_path),
    name="frontend",
)


@app.get("/")
async def frontend() -> FileResponse:
    return FileResponse(
        frontend_path / "index.html",
    )

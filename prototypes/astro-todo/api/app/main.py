from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.infrastructure.database import engine, run_migrations
from app.routes import health, todos


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_migrations(engine)
    yield


app = FastAPI(
    title=f"CICOR – {settings.module_name}",
    version="1.0.0",
    description=f"Backend API for CICOR module: {settings.module_name}",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(todos.router, prefix="/api/v1/todos", tags=["todos"])

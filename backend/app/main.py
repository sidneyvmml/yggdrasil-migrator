from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import SqliteRepository
from app.routers import exploration, migration, keycloak_migration, templates, jobs

app = FastAPI(
    title="Yggdrasil Migrator",
    version="0.1.0",
    description="Internal migration app for MongoDB with preview and async job execution.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    SqliteRepository.initialize(settings.sqlite_path)

app.include_router(exploration, prefix="/api/explore", tags=["exploration"])
app.include_router(migration, prefix="/api/migration", tags=["migration"])
app.include_router(keycloak_migration, prefix="/api/keycloak", tags=["keycloak-migration"])
app.include_router(jobs, prefix="/api/jobs", tags=["jobs"])
app.include_router(templates, prefix="/api/templates", tags=["templates"])

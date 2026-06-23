import logging

from fastapi import APIRouter, HTTPException

from app.db import SqliteRepository
from app.schemas.keycloak import (
    KeycloakExecuteRequest,
    KeycloakPreviewRequest,
    KeycloakPreviewResponse,
    KeycloakUsersRequest,
    KeycloakValidateRequest,
)
from app.services.keycloak_service import KeycloakService
from app.workers.tasks import execute_keycloak_migration_job

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/validate")
async def validate_connection(payload: KeycloakValidateRequest):
    try:
        connected = await KeycloakService.validate_connection(payload)
        return {"connected": connected}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to validate Keycloak connection: {exc}") from exc


@router.post("/users")
async def list_users(payload: KeycloakUsersRequest):
    try:
        items = await KeycloakService.list_users(payload, first=0, max_items=payload.limit)
        return {"items": items}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to list Keycloak users: {exc}") from exc


@router.post("/preview", response_model=KeycloakPreviewResponse)
async def preview_migration(payload: KeycloakPreviewRequest):
    try:
        items = await KeycloakService.preview(payload.config, limit=payload.limit)
        return {"items": items}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to preview Keycloak migration: {exc}") from exc


@router.post("/execute")
def execute_migration(payload: KeycloakExecuteRequest):
    try:
        config_payload = payload.config.model_dump()
        job = execute_keycloak_migration_job.apply_async(args=[config_payload, payload.maxDocuments])
        SqliteRepository.create_job(job.id, status="pending", config=config_payload, max_documents=payload.maxDocuments)
        return {"jobId": job.id, "status": "pending"}
    except Exception as exc:
        logger.exception("Failed to enqueue keycloak migration job")
        raise HTTPException(status_code=503, detail=f"Failed to enqueue keycloak migration job: {exc}") from exc

import logging

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.db import SqliteRepository
from app.schemas.common import JobCreateRequest, MigrationConfig, PreviewResponse
from app.workers.tasks import execute_migration_job

router = APIRouter()
logger = logging.getLogger(__name__)


def _normalize_filter_rules(config: dict) -> dict:
    rules = config.get("filterRules")
    if not isinstance(rules, list):
        return config

    normalized_rules = []
    for rule in rules:
        if not isinstance(rule, dict):
            normalized_rules.append(rule)
            continue

        if rule.get("op") == "truthy":
            normalized_rule = dict(rule)
            normalized_rule["op"] = "eq"
            normalized_rule["value"] = True
            normalized_rules.append(normalized_rule)
            continue

        normalized_rules.append(rule)

    normalized = dict(config)
    normalized["filterRules"] = normalized_rules
    return normalized


@router.post("/preview", response_model=PreviewResponse)
async def preview_migration(config: MigrationConfig):
    from app.services.migration_service import MigrationService
    from app.services.mongo_client import MongoClientFactory
    from app.config import settings

    client = MongoClientFactory.create_client(config.source.connectionString, timeout_ms=settings.mongodb_connect_timeout_ms)
    try:
        service = MigrationService(
            client,
            config.source.database,
            config.source.collection,
            config.target.database,
            config.target.collection,
        )
        items = await service.preview(config, limit=10)
        return {"items": jsonable_encoder(items, custom_encoder={ObjectId: str})}
    finally:
        client.close()


@router.post("/execute")
def execute_migration(request: JobCreateRequest):
    try:
        config_payload = _normalize_filter_rules(request.config.model_dump())
        job = execute_migration_job.apply_async(args=[config_payload, request.maxDocuments])
        SqliteRepository.create_job(job.id, status="pending", config=config_payload, max_documents=request.maxDocuments)
        return {"jobId": job.id, "status": "pending"}
    except Exception as exc:
        logger.exception("Failed to enqueue migration job")
        detail = "Nao foi possivel enviar o job para a fila. Verifique a conexao/auth do Redis e tente novamente."
        if "Authentication required" in str(exc):
            detail = "Falha de autenticacao no Redis. Verifique REDIS_PASS/REDIS_PASSWORD e reinicie API e worker."
        raise HTTPException(status_code=503, detail=detail) from exc

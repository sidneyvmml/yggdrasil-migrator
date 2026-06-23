import asyncio
from typing import Any, Dict

from celery import Task

from app.config import settings
from app.db import SqliteRepository
from app.schemas.common import MigrationConfig
from app.schemas.keycloak import KeycloakMigrationConfig
from app.services.keycloak_service import KeycloakService
from app.services.migration_service import MigrationService
from app.services.mongo_client import MongoClientFactory
from app.workers.celery_app import celery


class BaseMigrationTask(Task):
    @staticmethod
    def _is_auth_error(exc: Exception) -> bool:
        message = str(exc).lower()
        return "authentication failed" in message or "authenticationfailed" in message

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        SqliteRepository.update_job_status(task_id, "failed")
        error_message = str(exc)
        if self._is_auth_error(exc):
            error_message = (
                "MongoDB authentication failed during migration job. "
                "Check username, password and authSource in the source/target connection strings. "
                f"Original error: {error_message}"
            )
        SqliteRepository.store_job_result(task_id, {"error": error_message})
        super().on_failure(exc, task_id, args, kwargs, einfo)


async def _build_validated_client(connection_string: str, timeout_ms: int, label: str):
    async def _ping_client(conn: str):
        client = MongoClientFactory.create_client(conn, timeout_ms=timeout_ms)
        try:
            await client.admin.command("ping")
            return client, conn
        except Exception:
            client.close()
            raise

    try:
        return await _ping_client(connection_string)
    except Exception as exc:
        if not BaseMigrationTask._is_auth_error(exc):
            raise Exception(f"Failed to connect to {label} MongoDB. Original error: {exc}") from exc

        fallback_connection_string = MongoClientFactory.strip_credentials(connection_string)
        if fallback_connection_string == connection_string:
            raise Exception(
                f"MongoDB authentication failed for {label}. Check username, password and authSource in the connection string. Original error: {exc}"
            ) from exc

        try:
            return await _ping_client(fallback_connection_string)
        except Exception as fallback_exc:
            raise Exception(
                f"MongoDB authentication failed for {label} even after removing credentials from the URI. If this database does not require auth, remove username/password and leave authSource blank. Original error: {fallback_exc}"
            ) from fallback_exc


@celery.task(bind=True, base=BaseMigrationTask, name="app.workers.tasks.execute_migration_job")
def execute_migration_job(self, config_dict: Dict[str, Any], max_documents: int | None = None) -> Dict[str, Any]:
    job_id = self.request.id
    SqliteRepository.update_job_status(job_id, "loading_source", progress=5)

    config = MigrationConfig.model_validate(config_dict)
    source_client = None
    target_client = None

    async def _run():
        nonlocal source_client, target_client
        source_connection_string = MongoClientFactory.with_auth_source(
            config.source.connectionString,
            config.source.authSource,
        )
        target_connection_string = MongoClientFactory.with_auth_source(
            config.target.connectionString,
            config.target.authSource,
        )
        source_client, validated_source_connection = await _build_validated_client(
            source_connection_string,
            settings.mongodb_connect_timeout_ms,
            "source",
        )
        target_client, validated_target_connection = await _build_validated_client(
            target_connection_string,
            settings.mongodb_connect_timeout_ms,
            "target",
        )
        service = MigrationService(
            source_client,
            target_client,
            config.source.database,
            config.source.collection,
            config.target.database,
            config.target.collection,
        )

        SqliteRepository.update_job_status(job_id, "mapping_fields", progress=15)

        def _on_progress(progress: int):
            SqliteRepository.update_job_status(job_id, "inserting_documents", progress=progress)

        return await service.run_batch(
            config,
            batch_size=100,
            max_documents=max_documents,
            progress_callback=_on_progress,
        )

    try:
        result = asyncio.run(_run())

        SqliteRepository.store_job_result(job_id, result)
        SqliteRepository.update_job_status(job_id, "done", progress=100)
        return result
    finally:
        if source_client:
            source_client.close()
        if target_client:
            target_client.close()


@celery.task(bind=True, base=BaseMigrationTask, name="app.workers.tasks.execute_keycloak_migration_job")
def execute_keycloak_migration_job(self, config_dict: Dict[str, Any], max_documents: int | None = None) -> Dict[str, Any]:
    job_id = self.request.id
    SqliteRepository.update_job_status(job_id, "loading_source", progress=5)

    config = KeycloakMigrationConfig.model_validate(config_dict)

    async def _run():
        SqliteRepository.update_job_status(job_id, "mapping_fields", progress=15)

        def _on_progress(progress: int):
            SqliteRepository.update_job_status(job_id, "inserting_documents", progress=progress)

        return await KeycloakService.run_migration(
            config,
            max_documents=max_documents,
            timeout_ms=settings.mongodb_connect_timeout_ms,
            progress_callback=_on_progress,
        )

    result = asyncio.run(_run())
    SqliteRepository.store_job_result(job_id, result)
    SqliteRepository.update_job_status(job_id, "done", progress=100)
    return result

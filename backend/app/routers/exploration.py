from fastapi import APIRouter, HTTPException
from re import escape
from typing import Any

from app.schemas.common import (
    MongoCollectionRequest,
    MongoConnectionRequest,
    MongoDatabaseRequest,
    MongoDocumentRequest,
    PostgresConnectionRequest,
    PostgresDatabaseRequest,
    PostgresTablesRequest,
)
from app.services.mongo_client import MongoClientFactory, MongoExplorationService
from app.services.postgres_client import PostgresExplorationService

router = APIRouter()


def _contains_forbidden_operator(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key == "$where":
                return True
            if _contains_forbidden_operator(nested):
                return True
        return False
    if isinstance(value, list):
        return any(_contains_forbidden_operator(item) for item in value)
    return False


def _build_sample_query(connection: MongoCollectionRequest) -> dict[str, Any]:
    if connection.mongoQuery is not None:
        if _contains_forbidden_operator(connection.mongoQuery):
            raise HTTPException(status_code=400, detail="Mongo query uses forbidden operator '$where'.")
        return connection.mongoQuery

    if not connection.filterField:
        return {}

    operator = connection.filterOperator or "exists"
    field = connection.filterField

    if operator == "exists":
        return {field: {"$exists": True}}
    if operator == "eq":
        return {field: connection.filterValue}
    if operator == "ne":
        return {field: {"$ne": connection.filterValue}}
    if operator == "contains":
        value = "" if connection.filterValue is None else str(connection.filterValue)
        return {field: {"$regex": escape(value), "$options": "i"}}
    if operator in {"gt", "gte", "lt", "lte"}:
        op_map = {
            "gt": "$gt",
            "gte": "$gte",
            "lt": "$lt",
            "lte": "$lte",
        }
        return {field: {op_map[operator]: connection.filterValue}}

    return {}


def _normalize_exploration_error(exc: Exception) -> str:
    message = str(exc)
    lowered = message.lower()

    if "no servers found yet" in lowered or "serverselectiontimeouterror" in lowered:
        return (
            "MongoDB host unreachable. Check if Mongo is running and if the connection string is correct. "
            "Try mongodb://localhost:27017 when Mongo is local or port-forwarded from Docker. "
            "If credentials are required, include user/password and authSource. "
            f"Original error: {message}"
        )

    return message


def _normalize_postgres_error(exc: Exception) -> str:
    message = str(exc)
    lowered = message.lower()

    if "connection refused" in lowered:
        return (
            "PostgreSQL host refused connection. Check host, port, and whether PostgreSQL is running. "
            f"Original error: {message}"
        )

    if "could not translate host name" in lowered or "name or service not known" in lowered:
        return (
            "PostgreSQL host name could not be resolved. Check the host value in connection settings. "
            f"Original error: {message}"
        )

    if "password authentication failed" in lowered:
        return (
            "PostgreSQL authentication failed. Check username and password. "
            f"Original error: {message}"
        )

    return message


@router.post("/databases")
async def list_databases(connection: MongoConnectionRequest):
    try:
        connection_string = MongoClientFactory.with_auth_source(connection.connectionString, connection.authSource)
        return {"databases": await MongoExplorationService.list_databases(connection_string)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=_normalize_exploration_error(exc))


@router.post("/collections")
async def list_collections(connection: MongoDatabaseRequest):
    try:
        connection_string = MongoClientFactory.with_auth_source(connection.connectionString, connection.authSource)
        return {"collections": await MongoExplorationService.list_collections(connection_string, connection.database)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=_normalize_exploration_error(exc))


@router.post("/validate")
async def validate_connection(connection: MongoConnectionRequest):
    try:
        connection_string = MongoClientFactory.with_auth_source(connection.connectionString, connection.authSource)
        connected = await MongoExplorationService.validate_connection(connection_string)
        return {"connected": connected}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=_normalize_exploration_error(exc))


@router.post("/postgres/validate")
async def validate_postgres_connection(connection: PostgresConnectionRequest):
    try:
        connected = await PostgresExplorationService.validate_connection(connection.connectionString)
        return {"connected": connected}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=_normalize_postgres_error(exc))


@router.post("/postgres/databases")
async def list_postgres_databases(connection: PostgresConnectionRequest):
    try:
        databases = await PostgresExplorationService.list_databases(connection.connectionString)
        return {"databases": databases}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=_normalize_postgres_error(exc))


@router.post("/postgres/schemas")
async def list_postgres_schemas(connection: PostgresDatabaseRequest):
    try:
        schemas = await PostgresExplorationService.list_schemas(
            connection.connectionString,
            connection.database,
        )
        return {"schemas": schemas}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=_normalize_postgres_error(exc))


@router.post("/postgres/tables")
async def list_postgres_tables(connection: PostgresTablesRequest):
    try:
        tables = await PostgresExplorationService.list_tables(
            connection.connectionString,
            connection.database,
            connection.schemaName,
        )
        return {"tables": tables}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=_normalize_postgres_error(exc))


@router.post("/sample")
async def sample_documents(connection: MongoCollectionRequest):
    try:
        connection_string = MongoClientFactory.with_auth_source(connection.connectionString, connection.authSource)
        query = _build_sample_query(connection)
        items = await MongoExplorationService.sample_documents(
            connection_string,
            connection.database,
            connection.collection,
            connection.limit,
            query,
        )
        return {"items": items}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=_normalize_exploration_error(exc))


@router.post("/document")
async def get_document(connection: MongoDocumentRequest):
    try:
        connection_string = MongoClientFactory.with_auth_source(connection.connectionString, connection.authSource)
        item = await MongoExplorationService.get_document_by_id(
            connection_string,
            connection.database,
            connection.collection,
            connection.documentId,
        )
        if item is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"item": item}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=_normalize_exploration_error(exc))

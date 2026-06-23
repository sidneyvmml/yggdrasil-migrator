from fastapi import APIRouter, HTTPException

from app.schemas.common import MongoCollectionRequest, MongoConnectionRequest, MongoDatabaseRequest, MongoDocumentRequest
from app.services.mongo_client import MongoClientFactory, MongoExplorationService

router = APIRouter()


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


@router.post("/sample")
async def sample_documents(connection: MongoCollectionRequest):
    try:
        connection_string = MongoClientFactory.with_auth_source(connection.connectionString, connection.authSource)
        items = await MongoExplorationService.sample_documents(connection_string, connection.database, connection.collection)
        return {"items": items}
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

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any, Awaitable, Callable, Dict, List
from bson import ObjectId, DBRef
from bson.binary import Binary
import base64
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class MongoClientFactory:
    @staticmethod
    def with_auth_source(connection_string: str, auth_source: str | None) -> str:
        auth_source = (auth_source or "").strip()
        if not auth_source:
            return connection_string

        parts = urlsplit(connection_string)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        query["authSource"] = auth_source
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))

    @staticmethod
    def _serialize_bson(obj: Any) -> Any:
        """Recursively convert BSON types to JSON-serializable objects."""
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, Binary):
            # Keep Binary values lossless by returning MongoDB Extended JSON.
            return {
                "$binary": {
                    "base64": base64.b64encode(bytes(obj)).decode("ascii"),
                    "subType": format(obj.subtype, "02x"),
                }
            }
        elif isinstance(obj, DBRef):
            return {
                "$ref": obj.collection,
                "$id": str(obj.id),
                "$db": obj.database,
            }
        elif isinstance(obj, dict):
            return {k: MongoClientFactory._serialize_bson(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [MongoClientFactory._serialize_bson(item) for item in obj]
        elif isinstance(obj, bytes):
            return {
                "$binary": {
                    "base64": base64.b64encode(obj).decode("ascii"),
                    "subType": "00",
                }
            }
        return obj
    
    @staticmethod
    def create_client(connection_string: str, timeout_ms: int = 5000) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(
            connection_string,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=timeout_ms,
        )

    @staticmethod
    def strip_credentials(connection_string: str) -> str:
        parts = urlsplit(connection_string)
        if "@" not in parts.netloc:
            return connection_string

        host_part = parts.netloc.rsplit("@", 1)[1]
        return urlunsplit((parts.scheme, host_part, parts.path, parts.query, parts.fragment))


class MongoExplorationService:
    @staticmethod
    def _is_auth_error(exc: Exception) -> bool:
        message = str(exc).lower()
        return "authentication failed" in message or "authenticationfailed" in message

    @staticmethod
    async def _run_with_auth_fallback(
        connection_string: str,
        operation: Callable[[str], Awaitable[Any]],
    ) -> Any:
        try:
            return await operation(connection_string)
        except Exception as exc:
            fallback_connection_string = MongoClientFactory.strip_credentials(connection_string)
            if fallback_connection_string != connection_string and MongoExplorationService._is_auth_error(exc):
                return await operation(fallback_connection_string)
            raise

    @staticmethod
    async def validate_connection(connection_string: str) -> bool:
        async def operation(conn: str) -> bool:
            client = MongoClientFactory.create_client(conn)
            try:
                await client.admin.command("ping")
                return True
            finally:
                client.close()

        return await MongoExplorationService._run_with_auth_fallback(connection_string, operation)

    @staticmethod
    async def list_databases(connection_string: str) -> List[str]:
        async def operation(conn: str) -> List[str]:
            client = MongoClientFactory.create_client(conn)
            try:
                return await client.list_database_names()
            finally:
                client.close()

        return await MongoExplorationService._run_with_auth_fallback(connection_string, operation)

    @staticmethod
    async def list_collections(connection_string: str, database: str) -> List[str]:
        async def operation(conn: str) -> List[str]:
            client = MongoClientFactory.create_client(conn)
            try:
                db = client[database]
                return await db.list_collection_names()
            finally:
                client.close()

        return await MongoExplorationService._run_with_auth_fallback(connection_string, operation)

    @staticmethod
    async def sample_documents(connection_string: str, database: str, collection: str, limit: int = 10) -> List[Dict[str, Any]]:
        async def operation(conn: str) -> List[Dict[str, Any]]:
            client = MongoClientFactory.create_client(conn)
            try:
                cursor = client[database][collection].find({}, limit=limit)
                docs = [doc async for doc in cursor]
                # Serialize BSON types to JSON-compatible format
                return [MongoClientFactory._serialize_bson(doc) for doc in docs]
            finally:
                client.close()

        return await MongoExplorationService._run_with_auth_fallback(connection_string, operation)

    @staticmethod
    async def get_document_by_id(connection_string: str, database: str, collection: str, document_id: str) -> Dict[str, Any] | None:
        async def operation(conn: str) -> Dict[str, Any] | None:
            client = MongoClientFactory.create_client(conn)
            try:
                parsed_id: Any = ObjectId(document_id) if ObjectId.is_valid(document_id) else document_id
                document = await client[database][collection].find_one({"_id": parsed_id})
                if document is None:
                    return None
                return MongoClientFactory._serialize_bson(document)
            finally:
                client.close()

        return await MongoExplorationService._run_with_auth_fallback(connection_string, operation)

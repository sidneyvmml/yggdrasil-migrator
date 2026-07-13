from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

import httpx

from app.schemas.keycloak import KeycloakConnectionInfo, KeycloakMigrationConfig, MongoToKeycloakMigrationConfig
from app.services.mongo_client import MongoClientFactory


class KeycloakService:
    @staticmethod
    def read_value_by_path(document: Dict[str, Any], path: str) -> Any:
        current: Any = document
        for segment in path.split("."):
            if not isinstance(current, dict) or segment not in current:
                return None
            current = current[segment]
        return current

    @staticmethod
    def write_value_by_path(target: Dict[str, Any], path: str, value: Any) -> None:
        segments = path.split(".")
        cursor = target
        for idx, segment in enumerate(segments):
            is_last = idx == len(segments) - 1
            if is_last:
                cursor[segment] = value
                return
            if segment not in cursor or not isinstance(cursor[segment], dict):
                cursor[segment] = {}
            cursor = cursor[segment]

    @staticmethod
    def _normalize_match_value(value: Any) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @staticmethod
    async def _get_token(connection: KeycloakConnectionInfo, timeout_ms: int = 10000) -> str:
        url = f"{connection.baseUrl.rstrip('/')}/realms/{connection.realm}/protocol/openid-connect/token"
        timeout = httpx.Timeout(timeout_ms / 1000)
        async with httpx.AsyncClient(timeout=timeout) as client:
            form_data = {
                "client_id": connection.clientId,
            }
            if connection.authMode == "password":
                form_data["grant_type"] = "password"
                form_data["username"] = connection.username or ""
                form_data["password"] = connection.password or ""
            else:
                form_data["grant_type"] = "client_credentials"
                form_data["client_secret"] = connection.clientSecret or ""

            response = await client.post(
                url,
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            payload = response.json()
            token = payload.get("access_token")
            if not token:
                raise Exception("Keycloak token response did not include access_token")
            return token

    @staticmethod
    async def validate_connection(connection: KeycloakConnectionInfo, timeout_ms: int = 10000) -> bool:
        token = await KeycloakService._get_token(connection, timeout_ms=timeout_ms)
        url = f"{connection.baseUrl.rstrip('/')}/admin/realms/{connection.realm}"
        timeout = httpx.Timeout(timeout_ms / 1000)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            return True

    @staticmethod
    def _match_filter_value(current_value: Any, expected_value: Any) -> bool:
        if isinstance(current_value, list):
            return any(KeycloakService._match_filter_value(item, expected_value) for item in current_value)

        if isinstance(current_value, dict):
            return current_value == expected_value

        return current_value == expected_value

    @staticmethod
    def _to_comparable_value(value: Any) -> Any:
        if isinstance(value, bool) or value is None:
            return value
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            stripped = value.strip()
            try:
                return float(stripped)
            except ValueError:
                return stripped.lower()
        return value

    @staticmethod
    def _matches_operator(
        current_value: Any,
        filter_operator: Literal["eq", "ne", "contains", "gt", "gte", "lt", "lte", "null", "notNull"],
        expected_value: Any,
    ) -> bool:
        if filter_operator == "null":
            return current_value is None

        if filter_operator == "notNull":
            return current_value is not None

        if filter_operator == "eq":
            return KeycloakService._match_filter_value(current_value, expected_value)

        if filter_operator == "ne":
            return not KeycloakService._match_filter_value(current_value, expected_value)

        if isinstance(current_value, list):
            return any(
                KeycloakService._matches_operator(item, filter_operator, expected_value)
                for item in current_value
            )

        if filter_operator == "contains":
            if current_value is None or expected_value is None:
                return False
            return str(expected_value).lower() in str(current_value).lower()

        left = KeycloakService._to_comparable_value(current_value)
        right = KeycloakService._to_comparable_value(expected_value)

        if left is None or right is None:
            return False

        if filter_operator == "gt":
            return left > right
        if filter_operator == "gte":
            return left >= right
        if filter_operator == "lt":
            return left < right
        if filter_operator == "lte":
            return left <= right

        return False

    @staticmethod
    def _apply_users_filter(
        users: List[Dict[str, Any]],
        filter_mode: Literal["none", "field", "fieldValue"] = "none",
        filter_field: Optional[str] = None,
        filter_operator: Literal["eq", "ne", "contains", "gt", "gte", "lt", "lte", "null", "notNull"] = "eq",
        filter_value: Any = None,
    ) -> List[Dict[str, Any]]:
        if filter_mode == "none":
            return users

        field = (filter_field or "").strip()
        if not field:
            return users

        filtered_users: List[Dict[str, Any]] = []
        for user in users:
            current_value = KeycloakService.read_value_by_path(user, field)

            if filter_mode == "field":
                if current_value is not None:
                    filtered_users.append(user)
                continue

            if KeycloakService._matches_operator(current_value, filter_operator, filter_value):
                filtered_users.append(user)

        return filtered_users

    @staticmethod
    async def list_users_page(
        connection: KeycloakConnectionInfo,
        first: int = 0,
        max_items: int = 10,
        timeout_ms: int = 10000,
        filter_mode: Literal["none", "field", "fieldValue"] = "none",
        filter_field: Optional[str] = None,
        filter_operator: Literal["eq", "ne", "contains", "gt", "gte", "lt", "lte", "null", "notNull"] = "eq",
        filter_value: Any = None,
    ) -> tuple[List[Dict[str, Any]], bool]:
        token = await KeycloakService._get_token(connection, timeout_ms=timeout_ms)
        url = f"{connection.baseUrl.rstrip('/')}/admin/realms/{connection.realm}/users"
        timeout = httpx.Timeout(timeout_ms / 1000)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                url,
                params={"first": first, "max": max_items},
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            users = response.json()
            filtered_users = KeycloakService._apply_users_filter(
                users,
                filter_mode=filter_mode,
                filter_field=filter_field,
                filter_operator=filter_operator,
                filter_value=filter_value,
            )
            has_more = len(users) == max_items
            return filtered_users, has_more

    @staticmethod
    async def list_users(
        connection: KeycloakConnectionInfo,
        first: int = 0,
        max_items: int = 10,
        timeout_ms: int = 10000,
        filter_mode: Literal["none", "field", "fieldValue"] = "none",
        filter_field: Optional[str] = None,
        filter_operator: Literal["eq", "ne", "contains", "gt", "gte", "lt", "lte", "null", "notNull"] = "eq",
        filter_value: Any = None,
    ) -> List[Dict[str, Any]]:
        items, _ = await KeycloakService.list_users_page(
            connection,
            first=first,
            max_items=max_items,
            timeout_ms=timeout_ms,
            filter_mode=filter_mode,
            filter_field=filter_field,
            filter_operator=filter_operator,
            filter_value=filter_value,
        )
        return items

    @staticmethod
    async def _find_user_by_username(connection: KeycloakConnectionInfo, username: str, timeout_ms: int = 10000) -> Optional[Dict[str, Any]]:
        token = await KeycloakService._get_token(connection, timeout_ms=timeout_ms)
        url = f"{connection.baseUrl.rstrip('/')}/admin/realms/{connection.realm}/users"
        timeout = httpx.Timeout(timeout_ms / 1000)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                url,
                params={"username": username, "exact": "true", "max": 1},
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            payload = response.json()
            return payload[0] if payload else None

    @staticmethod
    async def _find_user_by_match_field(
        target_connection: KeycloakConnectionInfo,
        target_field: str,
        match_value: str,
        timeout_ms: int = 10000,
        token: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> Optional[Dict[str, Any]]:
        field = (target_field or "").strip()
        if not field:
            raise Exception("Target match field is required")

        value = KeycloakService._normalize_match_value(match_value)
        if value is None:
            return None

        own_token = token or await KeycloakService._get_token(target_connection, timeout_ms=timeout_ms)
        users_url = f"{target_connection.baseUrl.rstrip('/')}/admin/realms/{target_connection.realm}/users"
        timeout = httpx.Timeout(timeout_ms / 1000)

        async def _search_users(search_client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
            if field == "username":
                response = await search_client.get(
                    users_url,
                    params={"username": value, "exact": "true", "max": 1},
                    headers={"Authorization": f"Bearer {own_token}"},
                )
                response.raise_for_status()
                payload = response.json()
                return payload[0] if payload else None

            if field in {"email", "id", "firstName", "lastName"}:
                response = await search_client.get(
                    users_url,
                    params={field: value, "exact": "true", "max": 2},
                    headers={"Authorization": f"Bearer {own_token}"},
                )
                response.raise_for_status()
                payload = response.json()
                for candidate in payload:
                    if KeycloakService._normalize_match_value(
                        KeycloakService.read_value_by_path(candidate, field)
                    ) == value:
                        return candidate

            first = 0
            page_size = 100
            while True:
                response = await search_client.get(
                    users_url,
                    params={"first": first, "max": page_size},
                    headers={"Authorization": f"Bearer {own_token}"},
                )
                response.raise_for_status()
                users = response.json()
                if not users:
                    return None

                for candidate in users:
                    candidate_value = KeycloakService._normalize_match_value(
                        KeycloakService.read_value_by_path(candidate, field)
                    )
                    if candidate_value == value:
                        return candidate

                if len(users) < page_size:
                    return None
                first += page_size

        if client is not None:
            return await _search_users(client)

        async with httpx.AsyncClient(timeout=timeout) as own_client:
            return await _search_users(own_client)

    @staticmethod
    def map_user(source_user: Dict[str, Any], config: KeycloakMigrationConfig) -> Dict[str, Any]:
        mapped: Dict[str, Any] = {}
        for source_field, target_field in config.fieldMapping.items():
            value = KeycloakService.read_value_by_path(source_user, source_field)
            if value is not None:
                KeycloakService.write_value_by_path(mapped, target_field, value)

        username_value = KeycloakService.read_value_by_path(source_user, config.usernameSourceField)
        if not username_value:
            raise Exception(f"Source user missing username value from '{config.usernameSourceField}'")

        mapped["username"] = str(username_value)
        mapped.setdefault("enabled", source_user.get("enabled", True))
        return mapped

    @staticmethod
    def map_fields(source_document: Dict[str, Any], field_mapping: Dict[str, str]) -> Dict[str, Any]:
        mapped: Dict[str, Any] = {}
        for source_field, target_field in field_mapping.items():
            value = KeycloakService.read_value_by_path(source_document, source_field)
            if value is not None:
                KeycloakService.write_value_by_path(mapped, target_field, value)
        return mapped

    @staticmethod
    async def preview(config: KeycloakMigrationConfig, limit: int = 10, timeout_ms: int = 10000) -> List[Dict[str, Any]]:
        source_users = await KeycloakService.list_users(config.source, first=0, max_items=limit, timeout_ms=timeout_ms)
        preview_items: List[Dict[str, Any]] = []
        for user in source_users:
            mapped_user = KeycloakService.map_user(user, config)
            preview_items.append(mapped_user)
        return preview_items

    @staticmethod
    async def run_migration(config: KeycloakMigrationConfig, max_documents: Optional[int] = None, timeout_ms: int = 10000, progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        source_users = await KeycloakService.list_users(
            config.source,
            first=0,
            max_items=max_documents or 100,
            timeout_ms=timeout_ms,
        )
        if max_documents is not None:
            source_users = source_users[:max_documents]

        processed = 0
        inserted = 0
        merged = 0
        skipped = 0
        errors: List[Dict[str, Any]] = []

        target_token = await KeycloakService._get_token(config.target, timeout_ms=timeout_ms)
        users_url = f"{config.target.baseUrl.rstrip('/')}/admin/realms/{config.target.realm}/users"
        timeout = httpx.Timeout(timeout_ms / 1000)

        async with httpx.AsyncClient(timeout=timeout) as client:
            for user in source_users:
                processed += 1
                try:
                    mapped_user = KeycloakService.map_user(user, config)
                    username = mapped_user["username"]

                    existing = await KeycloakService._find_user_by_username(config.target, username, timeout_ms=timeout_ms)
                    if existing:
                        user_id = existing.get("id")
                        if not user_id:
                            skipped += 1
                            continue
                        payload = dict(existing)
                        payload.update(mapped_user)
                        payload.pop("id", None)
                        response = await client.put(
                            f"{users_url}/{user_id}",
                            json=payload,
                            headers={"Authorization": f"Bearer {target_token}"},
                        )
                        response.raise_for_status()
                        merged += 1
                    else:
                        response = await client.post(
                            users_url,
                            json=mapped_user,
                            headers={"Authorization": f"Bearer {target_token}"},
                        )
                        if response.status_code not in (201, 204):
                            response.raise_for_status()
                        inserted += 1
                except Exception as exc:
                    errors.append({"id": user.get("id"), "reason": str(exc)})

                if progress_callback and len(source_users) > 0:
                    progress_callback(min(99, int(processed / len(source_users) * 100)))

        return {
            "processed": processed,
            "inserted": inserted,
            "merged": merged,
            "skipped": skipped,
            "errors": errors,
        }

    @staticmethod
    async def run_mongo_source_update(
        config: MongoToKeycloakMigrationConfig,
        max_documents: Optional[int] = None,
        timeout_ms: int = 10000,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        source_connection_string = MongoClientFactory.with_auth_source(
            config.source.connectionString,
            config.source.authSource,
        )
        source_client = MongoClientFactory.create_client(source_connection_string, timeout_ms=timeout_ms)
        target_token = await KeycloakService._get_token(config.target, timeout_ms=timeout_ms)
        users_url = f"{config.target.baseUrl.rstrip('/')}/admin/realms/{config.target.realm}/users"
        timeout = httpx.Timeout(timeout_ms / 1000)

        try:
            source_collection = source_client[config.source.database][config.source.collection]
            source_total = await source_collection.estimated_document_count()
            expected_total = min(source_total, max_documents) if max_documents is not None else source_total
            if max_documents is not None:
                source_cursor = source_collection.find({}, limit=max_documents)
            else:
                source_cursor = source_collection.find({})

            processed = 0
            updated = 0
            not_found = 0
            errors: List[Dict[str, Any]] = []

            async with httpx.AsyncClient(timeout=timeout) as client:
                async for source_document in source_cursor:
                    processed += 1
                    try:
                        source_match_raw = KeycloakService.read_value_by_path(source_document, config.sourceMatchField)
                        source_match_value = KeycloakService._normalize_match_value(source_match_raw)
                        if source_match_value is None:
                            raise Exception(
                                f"Source document missing match value for '{config.sourceMatchField}'"
                            )

                        existing = await KeycloakService._find_user_by_match_field(
                            config.target,
                            config.targetMatchField,
                            source_match_value,
                            timeout_ms=timeout_ms,
                            token=target_token,
                            client=client,
                        )
                        if not existing:
                            not_found += 1
                            if progress_callback and expected_total > 0:
                                progress_callback(min(99, int(processed / expected_total * 100)))
                            continue

                        user_id = existing.get("id")
                        if not user_id:
                            not_found += 1
                            if progress_callback and expected_total > 0:
                                progress_callback(min(99, int(processed / expected_total * 100)))
                            continue

                        mapped_payload = KeycloakService.map_fields(source_document, config.fieldMapping)
                        if not mapped_payload:
                            if progress_callback and expected_total > 0:
                                progress_callback(min(99, int(processed / expected_total * 100)))
                            continue

                        payload = dict(existing)
                        payload.update(mapped_payload)
                        payload.pop("id", None)

                        response = await client.put(
                            f"{users_url}/{user_id}",
                            json=payload,
                            headers={"Authorization": f"Bearer {target_token}"},
                        )
                        response.raise_for_status()
                        updated += 1
                    except Exception as exc:
                        errors.append({"id": str(source_document.get("_id", "")), "reason": str(exc)})

                    if progress_callback and expected_total > 0:
                        progress_callback(min(99, int(processed / expected_total * 100)))

            return {
                "processed": processed,
                "updated": updated,
                "notFound": not_found,
                "inserted": 0,
                "merged": updated,
                "skipped": not_found,
                "errors": errors,
            }
        finally:
            source_client.close()

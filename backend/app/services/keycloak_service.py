from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.schemas.keycloak import KeycloakConnectionInfo, KeycloakMigrationConfig


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
    async def list_users(connection: KeycloakConnectionInfo, first: int = 0, max_items: int = 10, timeout_ms: int = 10000) -> List[Dict[str, Any]]:
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
            return response.json()

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

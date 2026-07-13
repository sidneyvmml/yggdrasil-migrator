import pytest

from app.services.postgres_client import PostgresExplorationService


@pytest.mark.asyncio
async def test_validate_connection_delegates_to_sync_validator(monkeypatch):
    calls = {}

    def fake_sync_validator(connection_string: str, timeout_seconds: int) -> bool:
        calls["connection_string"] = connection_string
        calls["timeout_seconds"] = timeout_seconds
        return True

    monkeypatch.setattr(
        PostgresExplorationService,
        "_validate_connection_sync",
        staticmethod(fake_sync_validator),
    )

    result = await PostgresExplorationService.validate_connection(
        "postgresql://user:pass@localhost:5432/mydb",
        timeout_seconds=7,
    )

    assert result is True
    assert calls == {
        "connection_string": "postgresql://user:pass@localhost:5432/mydb",
        "timeout_seconds": 7,
    }

from fastapi import HTTPException

from app.config import settings
from app.routers.keycloak_migration import _ensure_mongo_to_keycloak_enabled


def test_mongo_to_keycloak_blocked_when_flag_is_off(monkeypatch):
    monkeypatch.setattr(settings, "enable_mongo_to_keycloak_migration", False)

    try:
        _ensure_mongo_to_keycloak_enabled({"migrationType": "mongo_to_keycloak"})
    except HTTPException as exc:
        assert exc.status_code == 403
        assert "temporarily disabled" in str(exc.detail)
    else:
        raise AssertionError("Expected MongoDB -> Keycloak to be blocked when flag is off")


def test_mongo_to_keycloak_allowed_when_flag_is_on(monkeypatch):
    monkeypatch.setattr(settings, "enable_mongo_to_keycloak_migration", True)

    _ensure_mongo_to_keycloak_enabled({"migrationType": "mongo_to_keycloak"})


def test_keycloak_to_keycloak_not_affected_by_flag(monkeypatch):
    monkeypatch.setattr(settings, "enable_mongo_to_keycloak_migration", False)

    _ensure_mongo_to_keycloak_enabled({"migrationType": "keycloak"})

from app.schemas.keycloak import KeycloakConnectionInfo, KeycloakMigrationConfig
from app.services.keycloak_service import KeycloakService


def _build_config() -> KeycloakMigrationConfig:
    conn = KeycloakConnectionInfo(
        baseUrl="http://localhost:8080",
        realm="master",
        clientId="admin-cli",
        clientSecret="secret",
    )
    return KeycloakMigrationConfig(
        migrationName="KC migration",
        source=conn,
        target=conn,
        usernameSourceField="email",
        fieldMapping={
            "firstName": "firstName",
            "lastName": "lastName",
            "attributes.department": "attributes.department",
        },
    )


def test_map_user_uses_username_source_field_and_mapping():
    config = _build_config()
    source_user = {
        "id": "abc",
        "email": "john.doe@acme.org",
        "firstName": "John",
        "lastName": "Doe",
        "enabled": True,
        "attributes": {"department": ["engineering"]},
    }

    mapped = KeycloakService.map_user(source_user, config)

    assert mapped["username"] == "john.doe@acme.org"
    assert mapped["firstName"] == "John"
    assert mapped["lastName"] == "Doe"
    assert mapped["attributes"]["department"] == ["engineering"]


def test_map_user_raises_when_username_source_missing():
    config = _build_config()
    source_user = {
        "id": "abc",
        "firstName": "John",
    }

    try:
        KeycloakService.map_user(source_user, config)
    except Exception as exc:
        assert "username" in str(exc)
    else:
        raise AssertionError("Expected map_user to fail when username source is missing")

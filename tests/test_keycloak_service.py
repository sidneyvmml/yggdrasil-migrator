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


def test_apply_users_filter_by_field():
    users = [
        {"username": "alice", "email": "alice@acme.org"},
        {"username": "bob"},
    ]

    filtered = KeycloakService._apply_users_filter(
        users,
        filter_mode="field",
        filter_field="email",
    )

    assert len(filtered) == 1
    assert filtered[0]["username"] == "alice"


def test_apply_users_filter_by_field_value_matches_nested_and_list():
    users = [
        {
            "username": "alice",
            "attributes": {"department": ["engineering", "platform"]},
        },
        {
            "username": "bob",
            "attributes": {"department": ["finance"]},
        },
    ]

    filtered = KeycloakService._apply_users_filter(
        users,
        filter_mode="fieldValue",
        filter_field="attributes.department",
        filter_value="engineering",
    )

    assert len(filtered) == 1
    assert filtered[0]["username"] == "alice"


def test_apply_users_filter_by_field_value_supports_other_operators():
    users = [
        {"username": "alice", "firstName": "Alice", "loginCount": 12},
        {"username": "bob", "firstName": "Robert", "loginCount": 5},
        {"username": "carol", "firstName": "Carol", "loginCount": 12},
    ]

    filtered_ne = KeycloakService._apply_users_filter(
        users,
        filter_mode="fieldValue",
        filter_field="username",
        filter_operator="ne",
        filter_value="alice",
    )
    assert [item["username"] for item in filtered_ne] == ["bob", "carol"]

    filtered_contains = KeycloakService._apply_users_filter(
        users,
        filter_mode="fieldValue",
        filter_field="firstName",
        filter_operator="contains",
        filter_value="ali",
    )
    assert [item["username"] for item in filtered_contains] == ["alice"]

    filtered_gt = KeycloakService._apply_users_filter(
        users,
        filter_mode="fieldValue",
        filter_field="loginCount",
        filter_operator="gt",
        filter_value=10,
    )
    assert [item["username"] for item in filtered_gt] == ["alice", "carol"]

    filtered_lte = KeycloakService._apply_users_filter(
        users,
        filter_mode="fieldValue",
        filter_field="loginCount",
        filter_operator="lte",
        filter_value=5,
    )
    assert [item["username"] for item in filtered_lte] == ["bob"]


def test_apply_users_filter_by_field_value_supports_null_operators():
    users = [
        {"username": "alice", "email": "alice@acme.org"},
        {"username": "bob", "email": None},
        {"username": "carol"},
    ]

    filtered_null = KeycloakService._apply_users_filter(
        users,
        filter_mode="fieldValue",
        filter_field="email",
        filter_operator="null",
    )
    assert [item["username"] for item in filtered_null] == ["bob", "carol"]

    filtered_not_null = KeycloakService._apply_users_filter(
        users,
        filter_mode="fieldValue",
        filter_field="email",
        filter_operator="notNull",
    )
    assert [item["username"] for item in filtered_not_null] == ["alice"]

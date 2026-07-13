import pytest
from pydantic import ValidationError

from app.schemas.keycloak import KeycloakUsersRequest


BASE_PAYLOAD = {
    "baseUrl": "http://localhost:8080",
    "realm": "master",
    "authMode": "client_credentials",
    "clientId": "admin-cli",
    "clientSecret": "secret",
}


def test_keycloak_users_request_accepts_null_operator_without_filter_value():
    payload = {
        **BASE_PAYLOAD,
        "filterMode": "fieldValue",
        "filterField": "email",
        "filterOperator": "null",
    }

    model = KeycloakUsersRequest(**payload)

    assert model.filterOperator == "null"
    assert model.filterValue is None


def test_keycloak_users_request_accepts_not_null_operator_without_filter_value():
    payload = {
        **BASE_PAYLOAD,
        "filterMode": "fieldValue",
        "filterField": "email",
        "filterOperator": "notNull",
    }

    model = KeycloakUsersRequest(**payload)

    assert model.filterOperator == "notNull"
    assert model.filterValue is None


def test_keycloak_users_request_requires_filter_value_for_non_null_operators():
    payload = {
        **BASE_PAYLOAD,
        "filterMode": "fieldValue",
        "filterField": "email",
        "filterOperator": "eq",
        "filterValue": "",
    }

    with pytest.raises(ValidationError):
        KeycloakUsersRequest(**payload)

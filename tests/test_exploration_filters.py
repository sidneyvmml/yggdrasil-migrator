from fastapi import HTTPException

from app.routers.exploration import _build_sample_query
from app.schemas.common import MongoCollectionRequest


BASE_PAYLOAD = {
    "connectionString": "mongodb://localhost:27017",
    "database": "db",
    "collection": "users",
}


def test_build_sample_query_by_field_exists():
    request = MongoCollectionRequest.model_validate(
        {
            **BASE_PAYLOAD,
            "filterField": "name",
            "filterOperator": "exists",
        }
    )

    assert _build_sample_query(request) == {"name": {"$exists": True}}


def test_build_sample_query_by_field_value_equals_empty_string():
    request = MongoCollectionRequest.model_validate(
        {
            **BASE_PAYLOAD,
            "filterField": "name",
            "filterOperator": "eq",
            "filterValue": "",
        }
    )

    assert _build_sample_query(request) == {"name": ""}


def test_build_sample_query_uses_raw_mongo_query_when_provided():
    request = MongoCollectionRequest.model_validate(
        {
            **BASE_PAYLOAD,
            "mongoQuery": {"status": {"$ne": "inactive"}},
        }
    )

    assert _build_sample_query(request) == {"status": {"$ne": "inactive"}}


def test_build_sample_query_rejects_where_operator():
    request = MongoCollectionRequest.model_validate(
        {
            **BASE_PAYLOAD,
            "mongoQuery": {"$where": "this.name === 'Alice'"},
        }
    )

    try:
        _build_sample_query(request)
        raised = False
    except HTTPException as exc:
        raised = True
        assert exc.status_code == 400
        assert "forbidden operator" in str(exc.detail)

    assert raised

import pytest
from bson import ObjectId
from bson.binary import Binary

from app.schemas.common import FilterRule, FlattenConfigItem
from app.services.migration_service import MigrationService


class DummyClient:
    def __init__(self, docs):
        self._docs = docs

    def __getitem__(self, item):
        return self

    def __getattr__(self, item):
        return self

    async def find(self, query=None, limit=None):
        return self._docs[:limit or len(self._docs)]

    async def find_one(self, query):
        for doc in self._docs:
            if doc.get("_id") == query.get("_id"):
                return doc
        return None


@pytest.mark.asyncio
async def test_apply_field_mapping():
    document = {"id": "123", "name": "Alice", "documentId": "xyz"}
    mapping = {"id": "id", "name": "nameClient", "documentId": "document"}
    transformed = MigrationService.apply_field_mapping(document, mapping)
    assert transformed == {"id": "123", "nameClient": "Alice", "document": "xyz"}


def test_apply_flatten_explode():
    document = {"profiles": [{"key": 1}, {"key": 2}], "name": "Alice"}
    result = MigrationService.apply_flatten([document], [FlattenConfigItem(field="profiles", mode="explode")])
    assert len(result) == 2
    assert result[0]["profiles"] == {"key": 1}
    assert result[1]["profiles"] == {"key": 2}


def test_apply_flatten_preserve():
    document = {"profiles": [{"key": 1}], "name": "Alice"}
    result = MigrationService.apply_flatten([document], [FlattenConfigItem(field="profiles", mode="preserve")])
    assert len(result) == 1
    assert result[0]["profiles"] == [{"key": 1}]


def test_apply_flatten_nested_and_filter_truthy():
    document = {
        "starreds": [
            {"position": 0, "starred": "false", "service": "a"},
            {"position": 1, "starred": "true", "service": "b"},
            {"position": 2, "starred": 1, "service": "c"},
        ]
    }

    expanded = MigrationService.apply_flatten([document], [FlattenConfigItem(field="starreds", mode="explode")])
    filtered = MigrationService.apply_filters(expanded, [FilterRule(field="starreds.starred", op="truthy", value=True)])

    assert len(filtered) == 2
    assert filtered[0]["starreds"]["service"] == "b"
    assert filtered[1]["starreds"]["service"] == "c"


def test_normalize_manual_value_binary_extended_json():
    value = {
        "$binary": {
            "base64": "CUYYGF4EyjPCh4U8tjZVmw==",
            "subType": "03",
        }
    }

    normalized = MigrationService._normalize_manual_value(value)

    assert isinstance(normalized, Binary)
    assert normalized.subtype == 3


def test_normalize_manual_value_objectid_extended_json():
    value = {"$oid": "6865f1d8acfa6959e7f4b8b1"}

    normalized = MigrationService._normalize_manual_value(value)

    assert isinstance(normalized, ObjectId)
    assert str(normalized) == "6865f1d8acfa6959e7f4b8b1"

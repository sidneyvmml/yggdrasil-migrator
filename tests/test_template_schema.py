from app.schemas.common import TemplateCreateRequest


def test_template_payload_accepts_extended_migration_fields():
    payload = TemplateCreateRequest.model_validate(
        {
            "name": "Migration model",
            "description": "Reusable model",
            "payload": {
                "migrationName": "Template",
                "source": {"database": "source_db", "collection": "users"},
                "target": {"database": "target_db", "collection": "clients"},
                "sourceBaseDocumentId": "6865f1d8acfa6959e7f4b8b1",
                "fieldMapping": {"name": "full_name"},
                "manualMapping": {"active": True},
                "concatRules": [{"sourceFields": ["name", "surname"], "targetField": "display_name", "separator": " "}],
                "dbRefRules": [{"targetField": "company", "fromCollection": "companies", "foreignField": "_id"}],
                "mergeByField": "email",
                "lookups": [],
                "flattenConfig": [],
                "filterRules": [{"field": "active", "op": "eq", "value": True}],
            },
        }
    )

    assert payload.description == "Reusable model"
    assert payload.payload.sourceBaseDocumentId == "6865f1d8acfa6959e7f4b8b1"
    assert payload.payload.mergeByField == "email"
    assert payload.payload.dbRefRules[0].fromCollection == "companies"

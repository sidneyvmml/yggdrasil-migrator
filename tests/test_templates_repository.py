from app.db import SqliteRepository


def test_create_and_get_template_with_description_and_payload():
    payload = {
        "migrationName": "Template test",
        "source": {"database": "source_db", "collection": "users"},
        "target": {"database": "target_db", "collection": "clients"},
        "sourceBaseDocumentId": "6865f1d8acfa6959e7f4b8b1",
        "fieldMapping": {"name": "full_name"},
        "manualMapping": {"status": "active"},
        "concatRules": [{"sourceFields": ["name", "surname"], "targetField": "display_name", "separator": " "}],
        "dbRefRules": [{"targetField": "company", "fromCollection": "companies", "foreignField": "_id"}],
        "mergeByField": "email",
        "lookups": [],
        "flattenConfig": [],
        "filterRules": [],
    }

    template_id = SqliteRepository.create_template("Users migration", payload, "Main users template")
    created = SqliteRepository.get_template(template_id)

    assert created is not None
    assert created["templateId"] == template_id
    assert created["name"] == "Users migration"
    assert created["description"] == "Main users template"
    assert created["payload"]["sourceBaseDocumentId"] == "6865f1d8acfa6959e7f4b8b1"
    assert created["payload"]["manualMapping"] == {"status": "active"}


def test_update_template_updates_description_and_payload():
    template_id = SqliteRepository.create_template(
        "Old",
        {
            "migrationName": "Old",
            "source": {"database": "a", "collection": "b"},
            "target": {"database": "c", "collection": "d"},
            "fieldMapping": {"a": "b"},
            "manualMapping": {},
            "concatRules": [],
            "dbRefRules": [],
            "mergeByField": None,
            "lookups": [],
            "flattenConfig": [],
            "filterRules": [],
        },
        None,
    )

    SqliteRepository.update_template(
        template_id,
        "New",
        {
            "migrationName": "New",
            "source": {"database": "x", "collection": "users"},
            "target": {"database": "y", "collection": "clients"},
            "sourceBaseDocumentId": "abc123",
            "fieldMapping": {"email": "contact.email"},
            "manualMapping": {"active": True},
            "concatRules": [],
            "dbRefRules": [],
            "mergeByField": "contact.email",
            "lookups": [],
            "flattenConfig": [],
            "filterRules": [],
        },
        "Updated",
    )

    updated = SqliteRepository.get_template(template_id)
    assert updated is not None
    assert updated["name"] == "New"
    assert updated["description"] == "Updated"
    assert updated["payload"]["fieldMapping"] == {"email": "contact.email"}
    assert updated["payload"]["mergeByField"] == "contact.email"

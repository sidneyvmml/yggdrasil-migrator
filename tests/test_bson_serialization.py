import base64

from bson.binary import Binary

from app.services.mongo_client import MongoClientFactory


def test_serialize_bson_binary_preserves_extended_json():
    value = Binary(base64.b64decode("fktJig5hplKYt9vgwpLbvA=="), subtype=3)

    serialized = MongoClientFactory._serialize_bson({"_id": value})

    assert serialized["_id"] == {
        "$binary": {
            "base64": "fktJig5hplKYt9vgwpLbvA==",
            "subType": "03",
        }
    }

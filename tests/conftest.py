import pytest

from app.db import SqliteRepository

@pytest.fixture(autouse=True)
def initialize_db(tmp_path):
    SqliteRepository.initialize(str(tmp_path / "test.db"))
    yield

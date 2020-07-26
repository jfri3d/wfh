import pytest

from api.app import build_routes
from api.client import DBClient


@pytest.fixture()
def client():
    app = build_routes(client=DBClient(db_path="./test.sqlite", table_name="test"))
    yield app.test_client()

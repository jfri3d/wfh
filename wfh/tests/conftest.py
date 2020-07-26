import pytest

from wfh.api.client import DBClient
from wfh.app import build_routes


@pytest.fixture()
def client():
    app = build_routes(client=DBClient(db_path="./test.sqlite", table_name="test"))
    yield app.test_client()

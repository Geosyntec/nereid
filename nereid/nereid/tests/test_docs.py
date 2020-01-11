import pytest

from starlette.testclient import TestClient

from nereid.main import app


class TestReferenceData(object):
    def setup(self):
        self.client = TestClient(app)

    @pytest.mark.parametrize(
        "route, title_contents", [("/docs", "swagger"), ("/redoc", "redoc")]
    )
    def test_endpoints(self, route, title_contents):
        response = self.client.get(route)
        assert response.status_code == 200
        assert title_contents in response.content.decode().lower()

import pytest
from starlette.testclient import TestClient

from nereid.core.config import API_LATEST
from nereid.main import app


class TestReferenceData(object):
    def setup(self):
        self.route = API_LATEST + "/reference_data"
        self.client = TestClient(app)

    def test_refresh(self):
        endpoint = "refresh"
        url = "/".join([self.route, endpoint])

        response = self.client.get(url)
        assert response.status_code == 200
        rjson = response.json()
        assert "status" in rjson
        assert rjson["status"] == "success"

    @pytest.mark.parametrize(
        "query, should_work",
        [
            ("", False),
            ("?filename=bmp_params", True),
            ("?state=state&region=region&filename=bmp_params", True),
            ("?state=state&filename=bmp_params", True),
            ("?state=state&region=sea", False),
            ("?state=wa&region=sea", False),
        ],
    )
    def test_endpoints(self, query, should_work):
        url = self.route + query

        response = self.client.get(url)

        if should_work:
            assert response.status_code == 200
            rjson = response.json()
            assert "path" in rjson
            assert "schema" in rjson["data"]
            assert "data" in rjson["data"]
        else:
            assert response.status_code == 404

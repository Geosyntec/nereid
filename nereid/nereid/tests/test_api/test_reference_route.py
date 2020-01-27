import pytest
from starlette.testclient import TestClient

from nereid.core.config import API_LATEST
from nereid.main import app


class TestReferenceData(object):
    def setup(self):
        self.route = API_LATEST + "/reference_data"
        self.client = TestClient(app)

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
            assert rjson["status"] == "success"

            rjsondata = rjson["data"]
            assert "state" in rjsondata
            assert "region" in rjsondata
            assert "schema" in rjsondata["filedata"]
            assert "data" in rjsondata["filedata"]

        else:
            assert response.status_code == 404

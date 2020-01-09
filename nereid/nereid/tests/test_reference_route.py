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
        assert 'status' in rjson
        assert rjson['status'] == 'success'


    @pytest.mark.parametrize(
        "endpoint, query, should_work",
        [
            ("bmp_params", "", True),
            ("bmp_params", "?state=state&region=region", True),
            ("bmp_params", "?state=state", True),
            ("bmp_params", "?state=state&region=sea", False),
            ("bmp_params", "?state=wa&region=sea", False),
        ]
    )
    def test_endpoints(self, endpoint, query, should_work):
        url = "/".join([self.route, endpoint]) + query

        response = self.client.get(url)

        if should_work:
            assert response.status_code == 200
            rjson = response.json()
            assert 'schema' in rjson['data']
        else:
            assert response.status_code == 404

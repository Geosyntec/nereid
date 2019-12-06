import os
import time

from starlette.testclient import TestClient

from nereid.core.config import API_LATEST
from nereid.main import app
import nereid.data.test_data


TEST_PATH = os.path.dirname(nereid.data.test_data.__file__)


class TestNetworkValidationRoutes(object):
    def setup(self):

        self.test_data_dir = TEST_PATH
        self.route = API_LATEST + "/network/validate"
        self.client = TestClient(app)
        time.sleep(1)

    def get_payload(self, file):
        path = os.path.join(self.test_data_dir, file)
        assert os.path.isfile(path)

        with open(path, "r") as f:
            payload = f.read()
        return payload

    def test_network_validate_easy(self):

        file = "network_validate_is_valid.json"
        payload = self.get_payload(file)

        response = self.client.post(self.route, data=payload)
        assert response.status_code == 200

        rjson = response.json()
        assert rjson["status"].lower() == "success"
        assert rjson["result"]["status"].lower() == "valid"

    def test_network_validate_cycle(self):

        file = "network_validate_is_invalid_cycle.json"
        payload = self.get_payload(file)

        response = self.client.post(self.route, data=payload)
        assert response.status_code == 200

        rjson = response.json()
        assert rjson["status"].lower() == "success"
        assert rjson["result"]["status"].lower() == "invalid"

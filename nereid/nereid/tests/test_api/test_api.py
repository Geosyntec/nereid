from pathlib import Path

from starlette.testclient import TestClient

from nereid.core.config import API_LATEST
from nereid.main import app
import nereid.tests.test_data


TEST_PATH = Path(nereid.tests.test_data.__file__).parent.resolve()


class TestNetworkValidationRoutes(object):
    def setup(self):

        self.test_data_dir = TEST_PATH
        self.route = API_LATEST + "/network/validate"
        self.client = TestClient(app)

    def get_payload(self, file):
        path = self.test_data_dir / file
        assert path.is_file()

        return path.read_text()

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

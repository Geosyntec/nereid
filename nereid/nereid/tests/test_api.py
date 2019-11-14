import os

from starlette.testclient import TestClient

from nereid.core.config import API_LATEST
from nereid.main import app
import nereid.data.test_data

client = TestClient(app)
TEST_PATH = os.path.dirname(nereid.data.test_data.__file__)


def test_network_validate_easy():

    file = "network_validate_isvalid.json"
    path = os.path.join(TEST_PATH, file)
    assert os.path.isfile(path)

    with open(path, "r") as f:
        payload = f.read()

    response = client.post(API_LATEST + "/network/validate", data=payload)
    assert response.status_code == 200


def test_network_validate_cycle():

    file = "network_validate_is_invalid_cycle.json"
    path = os.path.join(TEST_PATH, file)
    assert os.path.isfile(path)

    with open(path, "r") as f:
        payload = f.read()

    response = client.post(API_LATEST + "/network/validate", data=payload)
    assert response.status_code != 200

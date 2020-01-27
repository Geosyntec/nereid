from pathlib import Path
import json
from time import time

import pytest
import networkx as nx
from starlette.testclient import TestClient

from nereid.core.config import API_LATEST
from nereid.main import app
from nereid.src.network.utils import nxGraph_to_dict
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
        assert rjson["data"]["isvalid"] == True

    def test_network_validate_cycle(self):

        file = "network_validate_is_invalid_cycle.json"
        payload = self.get_payload(file)

        response = self.client.post(self.route, data=payload)
        assert response.status_code == 200

        rjson = response.json()
        assert rjson["status"].lower() == "success"
        assert rjson["data"]["isvalid"] == False

    @pytest.mark.parametrize("N", [10, 100, 1000, 5000, 15000])
    def test_long_validation(self, N):
        g = nx.gnc_graph(N, seed=42)
        payload = json.dumps(nxGraph_to_dict(g))

        start = time()
        response = self.client.post(self.route, data=payload)
        end = time()

        elapsed = end - start
        print(f"elapsed time: {elapsed:.4f} seconds")
        assert response.status_code == 200

        rjson = response.json()
        if rjson["status"].lower() == "success":
            assert rjson["data"]["isvalid"] == False
        else:
            assert rjson["status"].lower() in ["started", "pending", "success"]
            assert rjson["result_route"] is not None
            assert rjson["task_id"] is not None
            response = self.client.get(self.route + f"/{rjson['task_id']}")
            assert response.status_code == 200


class TestNetworkSubgraphRoutes(object):
    def setup(self):

        self.test_data_dir = TEST_PATH
        self.route = API_LATEST + "/network/subgraph"
        self.client = TestClient(app)

    def get_payload(self, file):
        path = self.test_data_dir / file
        assert path.is_file()

        return path.read_text()

    def test_network_subgraph_example(self):

        file = "network_subgraph_request.json"
        payload = self.get_payload(file)

        response = self.client.post(self.route, data=payload)
        assert response.status_code == 200

        rjson = response.json()
        assert rjson["status"].lower() == "success"
        assert len(rjson["data"]["subgraph_nodes"]) == 2

    def test_get_network_subgraph_example(self):

        file = "network_subgraph_request.json"
        payload = self.get_payload(file)

        response = self.client.post(self.route, data=payload)
        assert response.status_code == 200

        tid = response.json()["task_id"]

        response = self.client.get(self.route + f"/{tid}")
        assert response.status_code == 200

        rjson = response.json()
        assert rjson["status"].lower() == "success"
        assert len(rjson["data"]["subgraph_nodes"]) == 2

    def test_render_subgraph_svg(self):
        file = "network_subgraph_request.json"
        payload = self.get_payload(file)

        response = self.client.post(self.route, data=payload)
        assert response.status_code == 200

        task_id = response.json()["task_id"]

        svg_response = self.client.get(self.route + f"/{task_id}/img")
        assert svg_response.status_code == 200

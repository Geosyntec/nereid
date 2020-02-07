from pathlib import Path
import json
from time import time

import pytest
import networkx as nx
from starlette.testclient import TestClient

from nereid.core.config import API_LATEST
from nereid.main import app
from nereid.api.api_v1.models import network_models
from nereid.src.network.utils import nxGraph_to_dict
import nereid.tests.test_data


TEST_PATH = Path(nereid.tests.test_data.__file__).parent.resolve()


def get_payload(file):
    path = TEST_PATH / file
    return path.read_text()


class TestNetworkValidationRoutes(object):
    def setup(self):
        self.route = API_LATEST + "/network/validate"
        self.client = TestClient(app)

        self.init_post_requests = [
            ("valid_graph_response", "network_validate_is_valid.json"),
            ("invalid_graph_response", "network_validate_is_invalid_cycle.json"),
        ]

        for attr, file in self.init_post_requests:
            payload = get_payload(file)
            response = self.client.post(self.route, data=payload)
            setattr(self, attr, response)

    @pytest.mark.parametrize(
        "post_response_name, isvalid",
        [("valid_graph_response", True), ("invalid_graph_response", False)],
    )
    def test_get_network_validate(self, post_response_name, isvalid):
        post_response = getattr(self, post_response_name)

        prjson = post_response.json()
        result_route = prjson["result_route"]

        get_response = self.client.get(result_route)
        assert get_response.status_code == 200

        grjson = get_response.json()
        assert network_models.NetworkValidationResponse(**grjson)

        assert grjson["task_id"] == prjson["task_id"]
        assert grjson["result_route"] == prjson["result_route"]

        gr_status = prjson["status"].lower()
        assert gr_status != "failure"
        if gr_status == "success":
            assert prjson["data"] is not None
            assert prjson["data"]["isvalid"] == isvalid


    @pytest.mark.parametrize(
        "post_response_name, isvalid",
        [("valid_graph_response", True), ("invalid_graph_response", False)],
    )
    def test_post_network_validate(self, post_response_name, isvalid):

        post_response = getattr(self, post_response_name)
        assert post_response.status_code == 200

        prjson = post_response.json()
        assert network_models.NetworkValidationResponse(**prjson)
        assert prjson["task_id"] is not None
        assert prjson["result_route"] is not None
        ping = self.client.get(prjson["result_route"])
        assert ping.status_code == 200

        pr_status = prjson["status"].lower()
        assert pr_status != "failure"
        if pr_status == "success":
            assert prjson["data"] is not None
            assert prjson["data"]["isvalid"] == isvalid


    @pytest.mark.parametrize("N", [10, 100, 1000, 5000, 15000])
    @pytest.mark.parametrize(
        "nxGraph, gkwargs, isvalid",
        [(nx.gnc_graph, {}, False), (nx.gnr_graph, {"p": 0.05}, True)],
    )
    def test_long_validation(self, N, nxGraph, gkwargs, isvalid):
        g = nxGraph(N, seed=42, **gkwargs)
        payload = json.dumps(nxGraph_to_dict(g))

        start = time()
        response = self.client.post(self.route, data=payload)
        end = time()

        elapsed = end - start
        print(f"elapsed time: {elapsed:.4f} seconds")
        assert response.status_code == 200

        prjson = response.json()
        assert network_models.NetworkValidationResponse(**prjson)
        assert prjson["result_route"] is not None
        assert prjson["task_id"] is not None

        pr_status = prjson["status"].lower()
        assert pr_status != "failure"
        if pr_status == "success":
            assert prjson["data"]["isvalid"] == isvalid

        response = self.client.get(prjson["result_route"])
        assert response.status_code == 200


class TestNetworkSubgraphRoutes(object):
    def setup(self):
        self.route = API_LATEST + "/network/subgraph"
        self.client = TestClient(app)

        self.init_post_requests = [
            ("subgraph_response", "network_subgraph_request.json")
        ]

        for attr, file in self.init_post_requests:
            payload = get_payload(file)
            response = self.client.post(self.route, data=payload)
            setattr(self, attr, response)

    @pytest.mark.parametrize(
        "post_response_name, exp_n_nodes", [("subgraph_response", 2)]
    )
    def test_get_network_subgraph(self, post_response_name, exp_n_nodes):
        post_response = getattr(self, post_response_name)

        prjson = post_response.json()
        result_route = prjson["result_route"]

        get_response = self.client.get(result_route)
        assert get_response.status_code == 200

        grjson = get_response.json()
        assert network_models.SubgraphResponse(**prjson)

        assert grjson["status"].lower() != "failure"
        assert grjson["task_id"] is not None
        assert grjson["result_route"] is not None

        if grjson["status"].lower() == "success":
            assert grjson["data"] is not None
            assert len(grjson["data"]["subgraph_nodes"]) == exp_n_nodes

    @pytest.mark.parametrize(
        "post_response_name, exp_n_nodes", [("subgraph_response", 2)]
    )
    def test_post_network_subgraph(self, post_response_name, exp_n_nodes):

        post_response = getattr(self, post_response_name)
        assert post_response.status_code == 200

        prjson = post_response.json()
        assert network_models.SubgraphResponse(**prjson)

        assert prjson["status"].lower() != "failure"
        assert prjson["task_id"] is not None
        assert prjson["result_route"] is not None

        if prjson["status"].lower() == "success":
            assert prjson["data"] is not None
            assert len(prjson["data"]["subgraph_nodes"]) == exp_n_nodes

    def test_render_subgraph_svg(self):

        rjson = self.subgraph_response.json()

        result_route = rjson["result_route"]

        svg_response = self.client.get(result_route + "/img")
        assert svg_response.status_code == 200
        assert "svg" in svg_response.content.decode()

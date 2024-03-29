import json

import pytest

from nereid.models import land_surface_models


@pytest.mark.parametrize("details", ["true", "false"])
@pytest.mark.parametrize("n_rows", [10, 50, 500])
@pytest.mark.parametrize("n_nodes", [5, 50, 100])
def test_post_land_surface_loading(
    land_surface_loading_responses, details, n_rows, n_nodes
):
    key = details, n_rows, n_nodes
    post_response = land_surface_loading_responses[key]

    assert post_response.status_code == 200, post_response
    prjson = post_response.json()
    assert land_surface_models.LandSurfaceResponse(**prjson)
    assert prjson["status"].lower() != "failure"


@pytest.mark.parametrize("details", ["true", "false"])
@pytest.mark.parametrize("n_rows", [10, 50, 500])
@pytest.mark.parametrize("n_nodes", [5, 50, 100])
def test_get_land_surface_loading(
    client, land_surface_loading_responses, details, n_rows, n_nodes
):
    key = details, n_rows, n_nodes
    post_response = land_surface_loading_responses[key]
    assert post_response.status_code == 200, post_response.content

    prjson = post_response.json()
    grjson = prjson

    if prjson.get("result_route"):
        result_route = prjson["result_route"]

        get_response = client.get(result_route)
        assert get_response.status_code == 200, get_response.content

        grjson = get_response.json()
    try:
        assert land_surface_models.LandSurfaceResponse(**prjson)
        assert grjson["task_id"] == prjson["task_id"]
        assert grjson["result_route"] == prjson["result_route"]
        assert grjson["status"].lower() != "failure"

        if grjson["status"].lower() == "success":  # pragma: no branch
            assert len(grjson["data"]["summary"]) <= n_nodes
            if details == "true":
                assert len(grjson["data"]["details"]) == n_rows
            else:
                assert grjson["data"]["details"] is None
    except AssertionError:  # pragma: no cover
        print(json.dumps(grjson, indent=2))
        raise

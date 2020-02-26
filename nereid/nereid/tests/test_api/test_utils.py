from fastapi import HTTPException
import pytest

from nereid.api.api_v1 import utils


@pytest.mark.parametrize(
    "state, region, raises, exp",
    [("state", "region", False, {"test": True}), ("wa", "sea", True, {})],
)
def test_get_valid_context(state, region, raises, exp):
    if raises:
        pytest.raises(HTTPException, utils.get_valid_context, state, region)
    else:
        req_context = utils.get_valid_context(state, region)
        assert all([req_context[k] == v for k, v in exp.items()])


def test_run_task_by_name(subgraph_request_dict):
    args = (subgraph_request_dict["graph"], subgraph_request_dict["nodes"])

    result = utils.run_task_by_name(
        taskname="network_subgraphs",
        router=r"¯\_(ツ)_/¯",
        args=args,
        get_route=r"¯\_(ツ)_/¯",
        force_foreground=True,
    )

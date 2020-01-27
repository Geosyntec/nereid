import pytest

from nereid.core import utils


@pytest.mark.parametrize(
    "state, region, dirname, context, exp",
    [
        ("state", "region", None, None, {"test": True}),
        ("state", "region", None, {"data_path": "string"}, {"data_path": "string"}),
        (
            "state",
            "region",
            "NotNone",
            {"data_path": "string"},
            {"data_path": "string"},
        ),
    ],
)
def test_get_request_context(state, region, dirname, context, exp):
    req_context = utils.get_request_context(state, region, dirname, context)
    assert all([k in req_context for k in exp.keys()])

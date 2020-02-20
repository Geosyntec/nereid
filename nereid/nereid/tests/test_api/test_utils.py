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

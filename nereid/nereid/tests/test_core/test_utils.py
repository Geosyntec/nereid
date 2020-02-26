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


@pytest.mark.parametrize(
    "key",
    [
        "default",
        "default_no_data_path_invalid",
        "default_dne_data_path_invalid",
        "default_no_ref_data_invalid",
        "default_no_lst_file_invalid",
        "default_lst_file_dne_invalid",
        "default_lst_not_dict_invalid",
        "default_lst_no_expanded_fields_valid",
        "default_emc_file_dne_invalid",
        "default_emc_no_params_valid",
        "default_api_no_ls_joins_valid",
        "default_api_no_ls_remaps_valid",
        "default_api_no_ls_joins_or_remaps_valid",
        "default_api_ls_joins_no_merge_no_params_valid",
    ],
)
def test_validate_request_context(contexts, key):
    context = contexts[key]

    isvalid, msg = utils.validate_request_context(context)

    assert len(msg) > 0

    if "invalid" in key:
        assert not isvalid

    else:
        assert isvalid
        assert msg == "valid"

import pytest

from nereid.src.treatment_facility.tasks import initialize_treatment_facilities


@pytest.mark.parametrize(
    "ctxt_key, has_met_data",
    [("default", True), ("default_api_no_tf_joins_valid", False)],
)
def test_construct_nodes_from_treatment_facility_request(
    contexts, valid_treatment_facilities, ctxt_key, has_met_data
):

    context = contexts[ctxt_key]
    tmnt_facilities = {"treatment_facilities": valid_treatment_facilities}
    treatment_facilities = initialize_treatment_facilities(
        tmnt_facilities, pre_validated=True, context=context
    )

    tmnt_lst = treatment_facilities["treatment_facilities"]

    assert len(tmnt_lst) == len(valid_treatment_facilities)

    for n in tmnt_lst:
        if has_met_data:
            assert n.get("rain_gauge") is not None
        else:
            assert n.get("rain_gauge") is None


@pytest.mark.parametrize(
    "ctxt_key, has_met_data",
    [("default", True), ("default_api_no_tf_joins_valid", False)],
)
@pytest.mark.parametrize(
    "model, checkfor",
    [
        ("PermPoolFacility", "treatment_volume_cuft"),
        ("RetAndTmntFacility", "retention_volume_cuft"),
        ("BioInfFacility", "retention_volume_cuft"),
        ("FlowAndRetFacility", "retention_volume_cuft"),
        ("RetentionFacility", "retention_volume_cuft"),
        ("TmntFacility", "treatment_volume_cuft"),
        ("CisternFacility", "retention_volume_cuft"),
        ("DryWellFacility", "retention_volume_cuft"),
        ("LowFlowFacility", "ini_treatment_rate_cfs"),
        ("FlowFacility", "treatment_rate_cfs"),
        ("NTFacility", "design_storm_depth_inches"),
    ],
)
def test_construct_nodes_from_treatment_facility_request_checkval(
    contexts, valid_treatment_facility_dicts, ctxt_key, has_met_data, model, checkfor,
):

    context = contexts[ctxt_key]
    tmnt_facilities = {"treatment_facilities": [valid_treatment_facility_dicts[model]]}

    treatment_facilities = initialize_treatment_facilities(
        tmnt_facilities, pre_validated=True, context=context
    )
    tmnt_lst = treatment_facilities["treatment_facilities"][0]

    check_val = tmnt_lst.get(checkfor)
    assert isinstance(check_val, float)
    assert tmnt_lst.get("errors") is None

    if has_met_data:
        assert tmnt_lst.get("rain_gauge") is not None
    else:
        assert tmnt_lst.get("rain_gauge") is None


@pytest.mark.parametrize("pre_validated", [True, False])
def test_construct_nodes_from_treatment_facility_request_pre_validation(
    contexts, treatment_facility_dicts, valid_treatment_facility_dicts, pre_validated
):

    context = contexts["default"]
    facilities = context["api_recognize"]["treatment_facility"]["facility_type"]
    model_map = {k: dct["validator"] for k, dct in facilities.items()}
    _tmnt_ls = []

    if pre_validated:
        facility_dicts = valid_treatment_facility_dicts
    else:
        facility_dicts = treatment_facility_dicts

    for k, model in model_map.items():
        dct = facility_dicts[model]
        dct["facility_type"] = k
        _tmnt_ls.append(dct)

    tmnt_facilities = {"treatment_facilities": _tmnt_ls}

    treatment_facilities = initialize_treatment_facilities(
        tmnt_facilities, pre_validated=pre_validated, context=context
    )
    tmnt_lst = treatment_facilities["treatment_facilities"]

    for m in tmnt_lst:

        # check that the joins happened
        assert m.get("rain_gauge") is not None
        if not pre_validated:
            # check that the model got validated
            assert m.get("valid_model") is not None

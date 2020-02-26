import pytest

from nereid.src.treatment_facility.constructors import build_treatment_facility_nodes


@pytest.mark.parametrize(
    "ctxt_key, has_met_data",
    [("default", True), ("default_api_no_tf_joins_valid", False)],
)
@pytest.mark.parametrize(
    "model, checkfor",
    [
        ("PermPoolFacility", "retention_volume_cuft"),
        ("RetAndTmntFacility", "retention_volume_cuft"),
        ("BioInfFacility", "retention_volume_cuft"),
        ("FlowAndRetFacility", "retention_volume_cuft"),
        ("RetentionFacility", "retention_volume_cuft"),
        ("TmntFacility", "treatment_volume_cuft"),
        ("CisternFacility", "design_storm_depth_inches"),  # TODO
        ("DryWellFacility", "retention_volume_cuft"),
        ("LowFlowFacility", "design_storm_depth_inches"),  # TODO
        ("FlowFacility", "design_storm_depth_inches"),  # TODO
        ("NTFacility", "design_storm_depth_inches"),
    ],
)
def test_build_treatment_facility_nodes(
    contexts, valid_treatment_facility_dicts, ctxt_key, has_met_data, model, checkfor
):

    context = contexts[ctxt_key]
    tmnt_facilities = [valid_treatment_facility_dicts[model]]
    nodes, msg = build_treatment_facility_nodes(tmnt_facilities, context)

    check_val = nodes[0].get(checkfor)
    assert isinstance(check_val, float)

    if has_met_data:
        assert nodes[0].get("rain_gauge") is not None
    else:
        assert nodes[0].get("rain_gauge") is None


@pytest.mark.parametrize(
    "ctxt_key, has_met_data",
    [("default", True), ("default_api_no_tf_joins_valid", False)],
)
def test_build_treatment_facility_nodes_from_long_list(
    contexts, valid_treatment_facilities, ctxt_key, has_met_data
):

    context = contexts[ctxt_key]
    tmnt_facilities = valid_treatment_facilities
    nodes, msg = build_treatment_facility_nodes(tmnt_facilities, context)

    for n in nodes:
        if has_met_data:
            assert n.get("rain_gauge") is not None
        else:
            assert n.get("rain_gauge") is None

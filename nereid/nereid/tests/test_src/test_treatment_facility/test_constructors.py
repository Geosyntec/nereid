import pandas
import pytest

from nereid.core.io import parse_configuration_logic
from nereid.src.treatment_facility.constructors import build_treatment_facility_nodes


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
def test_build_treatment_facility_nodes(
    contexts, valid_treatment_facility_dicts, ctxt_key, has_met_data, model, checkfor
):

    context = contexts[ctxt_key]
    tmnt_facilities = pandas.DataFrame([valid_treatment_facility_dicts[model]])
    df, messages = parse_configuration_logic(
        df=pandas.DataFrame(tmnt_facilities),
        config_section="api_recognize",
        config_object="treatment_facility",
        context=context,
    )
    node = build_treatment_facility_nodes(df)[0]

    check_val = node.get(checkfor)
    assert isinstance(check_val, (int, float)), (node, model, checkfor)

    if has_met_data:
        assert node.get("rain_gauge") is not None, (node, model, checkfor)
    else:
        assert node.get("rain_gauge") is None, (node, model, checkfor)


@pytest.mark.parametrize(
    "ctxt_key, has_met_data",
    [("default", True), ("default_api_no_tf_joins_valid", False)],
)
def test_build_treatment_facility_nodes_from_long_list(
    contexts, valid_treatment_facilities, ctxt_key, has_met_data
):

    context = contexts[ctxt_key]
    tmnt_facilities = pandas.DataFrame(valid_treatment_facilities)
    df, messages = parse_configuration_logic(
        df=tmnt_facilities,
        config_section="api_recognize",
        config_object="treatment_facility",
        context=context,
    )
    nodes = build_treatment_facility_nodes(df)

    for n in nodes:
        if has_met_data:
            assert n.get("rain_gauge") is not None
        else:
            assert n.get("rain_gauge") is None


@pytest.mark.parametrize(
    "months_operational", ["summer", "winter", "both", r"¯\_(ツ)_/¯"]
)
@pytest.mark.parametrize(
    "facility_type",
    [
        "LowFlowFacility",
        "DryWeatherDiversionLowFlowFacility",
        "DryWeatherTreatmentLowFlowFacility",
    ],
)
def test_build_diversion_facility_months_operational(
    contexts, valid_treatment_facilities, months_operational, facility_type
):

    context = contexts["default"]

    tmnt_facilities = (
        pandas.DataFrame(valid_treatment_facilities)
        .query("valid_model == @facility_type")
        .assign(months_operational=months_operational)
    )

    df, messages = parse_configuration_logic(
        df=tmnt_facilities,
        config_section="api_recognize",
        config_object="treatment_facility",
        context=context,
    )
    nodes = build_treatment_facility_nodes(df)

    if "treatment" in facility_type.lower():
        reduction_type, no_reduction_type = "treatment", "retention"
    else:
        reduction_type, no_reduction_type = "retention", "treatment"

    summer_reduction = months_operational in ["summer", "both"]
    winter_reduction = months_operational in ["winter", "both"]

    for n in nodes:
        assert n, "error: no data created"
        if summer_reduction:
            assert n.get(f"summer_dry_weather_{reduction_type}_rate_cfs") > 0.0, n
            assert n.get(f"summer_dry_weather_{no_reduction_type}_rate_cfs") == 0.0, n
        else:
            assert n.get(f"summer_dry_weather_{reduction_type}_rate_cfs") == 0.0, n
            assert n.get(f"summer_dry_weather_{no_reduction_type}_rate_cfs") == 0.0, n

        if winter_reduction:
            assert n.get(f"winter_dry_weather_{reduction_type}_rate_cfs") > 0.0, n
            assert n.get(f"winter_dry_weather_{no_reduction_type}_rate_cfs") == 0.0, n
        else:
            assert n.get(f"winter_dry_weather_{reduction_type}_rate_cfs") == 0.0, n
            assert n.get(f"winter_dry_weather_{no_reduction_type}_rate_cfs") == 0.0, n

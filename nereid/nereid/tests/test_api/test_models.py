import pytest

from nereid.models.treatment_facility_models import (
    validate_treatment_facility_models,
)


@pytest.mark.parametrize("ctxt_key", ["default", "default_no_dw_valid"])
@pytest.mark.parametrize(
    "err, data_dict",
    [
        (
            False,
            {
                "node_id": "1",
                "facility_type": "biofiltration",
                "ref_data_key": "10101200",
                "design_storm_depth_inches": 0.87,
                "is_online": False,
                "tributary_area_tc_min": 40,
                "total_volume_cuft": 5500.1,
                "area_sqft": 1500.80,
                "media_filtration_rate_inhr": 12.6,
                "offline_diversion_rate_cfs": 13.30,
            },
        ),
        (
            False,
            {
                "node_id": "1",
                "facility_type": "biofiltration",
                "ref_data_key": "10101200",
                "design_storm_depth_inches": 0.87,
                "is_online": False,
                "tributary_area_tc_min": 40,
                "total_volume_cuft": 5500.1,
                "area_sqft": 1500.80,
                "media_filtration_rate_inhr": 12.6,
                "offline_diversion_rate_cfs": None,
            },
        ),
        (
            "not in `model_mapping`",
            {
                "node_id": "1",
                "facility_type": r"¯\_(ツ)_/¯",
                "ref_data_key": "10101200",
                "design_storm_depth_inches": 0.87,
                "is_online": True,
                "tributary_area_tc_min": 40,
                "total_volume_cuft": 5500.1,
                "area_sqft": 1500.80,
                "media_filtration_rate_inhr": 12.6,
                "offline_diversion_rate_cfs": None,
            },
        ),
        (
            False,
            {
                "node_id": "1",
                "facility_type": "dry_weather_diversion",
                "ref_data_key": "10101000",
                "design_storm_depth_inches": 0.85,
                "tributary_area_tc_min": 5.0,
                "treatment_rate_cfs": 2.5,
            },
        ),
        (
            False,
            {
                "node_id": "1",
                "facility_type": "dry_weather_diversion",
                "ref_data_key": "10101000",
                "design_storm_depth_inches": 0.85,
                "tributary_area_tc_min": 5.0,
                "design_capacity_cfs": 2.5,
            },
        ),
        (
            "validation error",
            {
                "node_id": "1",
                "facility_type": "dry_weather_diversion",
                "ref_data_key": "10101000",
                "design_storm_depth_inches": 0.85,
            },
        ),
        (
            "validation error",
            {
                "node_id": "1",
                "facility_type": "dry_weather_diversion",
                "ref_data_key": "10101000",
                "design_storm_depth_inches": 0.85,
                "tributary_area_tc_min": None,
                "design_capacity_cfs": None,
            },
        ),
    ],
)
def test_build_treatment_facility_nodes_errors(contexts, ctxt_key, err, data_dict):
    context = contexts[ctxt_key]
    tmnt_facilities = [data_dict]
    valid_models = validate_treatment_facility_models(tmnt_facilities, context)

    vm_dict = valid_models[0]

    if err:
        assert err in vm_dict["errors"]
    else:
        assert vm_dict.get("errors") is None

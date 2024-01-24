import json

import pytest

from nereid.src.tasks import solve_watershed
from nereid.tests.utils import get_test_data


@pytest.mark.parametrize(
    "downstream_facility",
    [
        {
            "facility_type": "biofiltration",
            "node_id": "0",
            "ref_data_key": "10101000",
            "design_storm_depth_inches": 0.85,
            "total_volume_cuft": 10000,
            "area_sqft": 5000,
            "media_filtration_rate_inhr": 5,
        },
        {
            "facility_type": "infiltration",
            "node_id": "0",
            "ref_data_key": "10101000",
            "design_storm_depth_inches": 0.85,
            "total_volume_cuft": 4000,
            "area_sqft": 2000,
            "inf_rate_inhr": 2,
        },
        {
            "facility_type": "bioretention",
            "node_id": "0",
            "ref_data_key": "10101000",
            "design_storm_depth_inches": 0.85,
            "total_volume_cuft": 4000,
            "retention_volume_cuft": 0.0,  # no retention volume
            "area_sqft": 1000,
            "media_filtration_rate_inhr": 5.25,
            "hsg": "b",
        },
        {
            "facility_type": "bioretention",
            "node_id": "0",
            "ref_data_key": "10101000",
            "design_storm_depth_inches": 0.85,
            "total_volume_cuft": 4000,
            "retention_volume_cuft": 2000,
            "area_sqft": 1000,
            "media_filtration_rate_inhr": 5.25,
            "hsg": "b",
        },
    ],
)
def test_nested_solution(contexts, downstream_facility):
    ctx = contexts["default"]
    watershed = json.loads(get_test_data("nested_watershed_request.json"))

    tmnt_facilities = watershed["treatment_facilities"]
    replace_node_id = downstream_facility["node_id"]
    for d in tmnt_facilities:
        if d["node_id"] == replace_node_id:
            d.update(downstream_facility)

    res = solve_watershed(
        watershed=watershed, treatment_pre_validated=False, context=ctx
    )

    tmnt_results = [n for n in res["results"] if n.get("node_id") == "0"].pop()
    assert tmnt_results["captured_pct"] > 0.0, json.dumps(tmnt_results, indent=2)


TMNT_FACILITIES = [
    # (facility, reduces_load, retention, tmnt)
    (
        {
            "node_id": "1",
            "facility_type": "shrug_emoji",
            "captured_pct": 80,
            "retained_pct": 20,
        },
        False,
        False,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "bioretention_simple",
            "captured_pct": 80,
            "retained_pct": 20,  # retention should be less than or equal to capture
        },
        True,
        True,
        True,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "bioretention_simple",
            "captured_pct": 80,
            # retention should default to zero
        },
        True,
        False,
        True,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "infiltration_simple",
            "captured_pct": 80,
            "retained_pct": None,  # retention should match capture
        },
        True,
        True,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "infiltration_simple",
            "captured_pct": 80,
            # retention should match capture
        },
        True,
        True,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "sand_filter_simple",
            "captured_pct": 80,
            "retained_pct": None,  # retention should be zero
        },
        True,
        False,
        True,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "sand_filter_simple",
            "captured_pct": 80,
            # retention should be zero
        },
        True,
        False,
        True,
    ),
    ## invalid input should have no load reduction and no capture
    (
        {
            "node_id": "1",
            "facility_type": "bioretention_simple",
            "captured_pct": 80,
            "retained_pct": -15,  # must be 0-100
        },
        False,
        False,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "bioretention_simple",
            "captured_pct": 80,
            "retained_pct": 81,  # must be <= capture
        },
        False,
        False,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "bioretention_simple",
            "captured_pct": None,  # capture is required
            "retained_pct": 81,
        },
        False,
        False,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "bioretention_simple",
            "captured_pct": 101,  # must be 0-100
            "retained_pct": 81,
        },
        False,
        False,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "infiltration_simple",
            "captured_pct": 80,
            "retained_pct": 81,  # must be equal to capture
        },
        False,
        False,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "infiltration_simple",
            "captured_pct": None,  # capture is required
            "retained_pct": 81,
        },
        False,
        False,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "sand_filter_simple",
            "captured_pct": 80,
            "retained_pct": 5,  # cannot retain
        },
        False,
        False,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "sand_filter_simple",
            "captured_pct": 101,  # must be 0-100
            "retained_pct": 0,
        },
        False,
        False,
        False,
    ),
    (
        {
            "node_id": "1",
            "facility_type": "sand_filter_simple",
            "captured_pct": None,  # capture is required
            "retained_pct": 0,
        },
        False,
        False,
        False,
    ),
]


@pytest.mark.parametrize(
    "tmnt_facility, reduces_load, does_retention, does_treatment", TMNT_FACILITIES
)
def test_minimal_watershed(
    contexts, tmnt_facility, reduces_load, does_retention, does_treatment
):
    cxmin = contexts["min"]

    wshd = {
        "graph": {
            "directed": True,
            "multigraph": False,
            "graph": {},
            "nodes": [
                {"metadata": {}, "id": "0"},
                {"metadata": {}, "id": "1"},
                {
                    "metadata": {
                        "runoff_volume_cuft": 35000,
                        "eff_area_acres": 0.6,
                        "TSS_load_lbs": 43,
                    },
                    "id": "2",
                },
            ],
            "edges": [
                {"metadata": {}, "source": "1", "target": "0"},
                {"metadata": {}, "source": "2", "target": "1"},
            ],
        },
        "treatment_facilities": [tmnt_facility],
    }
    res = solve_watershed(wshd, treatment_pre_validated=False, context=cxmin)
    tmnt_results = [n for n in res["results"] if n.get("node_id") == "1"].pop()
    lr = tmnt_results.get("TSS_load_lbs_removed", 0) > 0.0
    vol_ret = tmnt_results.get("runoff_volume_cuft_retained", 0) > 0.0
    vol_trt = tmnt_results.get("runoff_volume_cuft_treated", 0) > 0.0
    ds_node_id = tmnt_results.get("_ds_node_id")
    assert reduces_load == lr, tmnt_results.get("TSS_load_lbs_removed", 0)
    assert does_retention == vol_ret, tmnt_results.get("runoff_volume_cuft_retained", 0)
    assert does_treatment == vol_trt, tmnt_results.get("runoff_volume_cuft_treated", 0)
    assert "0" == ds_node_id, ds_node_id

import pytest

from nereid.src.tasks import solve_watershed

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
    assert reduces_load == lr, tmnt_results.get("TSS_load_lbs_removed", 0)
    assert does_retention == vol_ret, tmnt_results.get("runoff_volume_cuft_retained", 0)
    assert does_treatment == vol_trt, tmnt_results.get("runoff_volume_cuft_treated", 0)

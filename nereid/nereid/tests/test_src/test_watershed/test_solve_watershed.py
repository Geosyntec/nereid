from copy import deepcopy

import networkx as nx
import numpy
import pytest

from nereid.api.api_v1.models.treatment_facility_models import TREATMENT_FACILITY_MODELS
from nereid.src.network.algorithms import get_subset
from nereid.src.watershed.solve_watershed import (
    initialize_graph,
    solve_watershed_loading,
)
from nereid.src.watershed.utils import attrs_to_resubmit
from nereid.tests.utils import (
    check_graph_data_equal,
    generate_random_watershed_solve_request_from_graph,
)


def test_watershed_solve_scaler_conservation(
    contexts, watershed_graph, initial_node_data
):
    g, data = watershed_graph, deepcopy(initial_node_data)
    context = contexts["default"]

    nx.set_node_attributes(g, data)
    solve_watershed_loading(g, context)

    # no errors should appear for a watershed with only land surfaces
    assert all(len(dct["node_errors"]) == 0 for n, dct in g.nodes(data=True))

    for single, total in [
        ("eff_area_acres", "eff_area_acres_total_cumul"),
        ("runoff_volume_cuft", "runoff_volume_cuft_total_discharged"),
        ("TSS_load_lbs", "TSS_load_lbs_total_discharged"),
        (
            "summer_dry_weather_flow_cuft",
            "summer_dry_weather_flow_cuft_total_discharged",
        ),
        ("summer_dwTSS_load_lbs", "summer_dwTSS_load_lbs_total_discharged"),
        (
            "winter_dry_weather_flow_cuft",
            "winter_dry_weather_flow_cuft_total_discharged",
        ),
        ("winter_dwTSS_load_lbs", "winter_dwTSS_load_lbs_total_discharged"),
    ]:
        outfall_total = g.nodes["0"][total]
        assert outfall_total > 1e-3
        sum_individual = sum(nx.get_node_attributes(g, single).values())

        # allow floating point errors only
        assert abs(outfall_total - sum_individual) / outfall_total < 1e-15


@pytest.mark.parametrize("ctx_key", ["default", "default_no_dw_valid"])
def test_solve_watershed_stable_with_subsets(
    contexts, watershed_graph, initial_node_data, ctx_key
):
    g, data = watershed_graph, deepcopy(initial_node_data)
    context = contexts[ctx_key]

    nx.set_node_attributes(g, data)
    solve_watershed_loading(g, context)

    # from the previous solution, we only need the keys which contain the accumulated keys.
    # keys = ["_direct", "_upstream", "_cumul", "_inflow", "_discharged"]
    reqd_min_attrs = attrs_to_resubmit([data for n, data in g.nodes(data=True)])
    prev_solve_data = {
        n: {k: dct[k] for k in dct.keys() if k in reqd_min_attrs}
        for n, dct in g.nodes(data=True)
    }

    # check single dirty nodes
    for dirty_node in g.nodes():
        dirty_nodes = [dirty_node]
        subg = nx.DiGraph(g.subgraph(get_subset(g, nodes=dirty_nodes)).edges)

        # always send the info that was sent the first time
        nx.set_node_attributes(
            subg, {k: v for k, v in data.items() if k in subg.nodes()}
        )
        nx.set_node_attributes(
            subg, {k: v for k, v in prev_solve_data.items() if k not in dirty_nodes}
        )
        solve_watershed_loading(subg, context)

        check_graph_data_equal(g, subg)

    # check multiple dirty nodes
    numpy.random.seed(42)
    for dirty_nodes in [
        numpy.random.choice(g.nodes(), size=size, replace=False)
        for size in [2, 4, 6, 8, 10]
    ]:
        subg = nx.DiGraph(g.subgraph(get_subset(g, nodes=dirty_nodes)).edges)

        # always send the info that was sent the first time
        nx.set_node_attributes(
            subg, {k: v for k, v in data.items() if k in subg.nodes()}
        )
        nx.set_node_attributes(
            subg, {k: v for k, v in prev_solve_data.items() if k not in dirty_nodes}
        )
        solve_watershed_loading(subg, context)

        check_graph_data_equal(g, subg)


tmnt_facilities = [
    {
        "facility_type": "bioinfiltration",
        "design_storm_depth_inches": 0.91,
        "is_online": True,
        "tributary_area_tc_min": 15.0,
        "offline_diversion_rate_cfs": 17.773482892257434,
        "total_volume_cuft": 5000.0,
        "retention_volume_cuft": 2200.0,
        "area_sqft": 950.0,
        "media_filtration_rate_inhr": 8.0,
        "hsg": "c",
        "constructor": "bioinfiltration_facility_constructor",
        "tmnt_performance_facility_type": "Biofiltration",
        "inf_rate_inhr": 0.24,
        "validation_fallback": "NTFacility",
        "valid_model": "BioInfFacility",
        "validator": "BioInfFacility",
        "subbasin": "101012",
        "rain_gauge": "1130_LAGUNA_AUDUBON",
        "et_zone": "Zone6",
        "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
        "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
        "retention_depth_ft": 2.3157894736842106,
        "retention_ddt_hr": 115.78947368421053,
        "treatment_volume_cuft": 2800.0,
        "treatment_depth_ft": 2.9473684210526314,
        "treatment_ddt_hr": 4.421052631578947,
        "node_type": "volume_based_facility",
    },
    {
        "facility_type": "swale",
        "design_storm_depth_inches": 0.8,
        "is_online": True,
        "tributary_area_tc_min": 10.0,
        "area_sqft": 686.26,
        "hsg": "c",
        "constructor": "flow_and_retention_facility_constructor",
        "tmnt_performance_facility_type": "Vegetated Swale",
        "inf_rate_inhr": 0.24,
        "validation_fallback": "NTFacility",
        "valid_model": "FlowAndRetFacility",
        "validator": "FlowAndRetFacility",
        "treatment_rate_cfs": 0.16,
        "depth_ft": 0.8,
        "subbasin": "101012",
        "rain_gauge": "1130_LAGUNA_AUDUBON",
        "et_zone": "Zone6",
        "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
        "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
        "retention_volume_cuft": 549.008,
        "retention_depth_ft": 0.8,
        "retention_ddt_hr": 40.00000000000001,
        "node_type": "flow_based_facility",
    },
    {
        "facility_type": "swale",
        "design_storm_depth_inches": 0.8,
        "is_online": True,
        "tributary_area_tc_min": 10.0,
        "area_sqft": 686.26,
        "hsg": "c",
        "constructor": "flow_and_retention_facility_constructor",
        "tmnt_performance_facility_type": "Vegetated Swale",
        "inf_rate_inhr": 0.24,
        "validation_fallback": "NTFacility",
        "valid_model": "FlowAndRetFacility",
        "validator": "FlowAndRetFacility",
        "treatment_rate_cfs": 0.16,
        "depth_ft": 0.8,
        "subbasin": "101012",
        "rain_gauge": "1130_LAGUNA_AUDUBON",
        "et_zone": "Zone6",
        "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
        "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
        "retention_volume_cuft": 0.0,  # zero retention
        "retention_depth_ft": 0.0,
        "retention_ddt_hr": 40.00000000000001,
        "node_type": "flow_based_facility",
    },
    {
        "facility_type": "hds",
        "design_storm_depth_inches": 0.7414346515768613,
        "treatment_rate_cfs": 0.665505501038112,
        "tributary_area_tc_min": 15.0,
        "constructor": "flow_facility_constructor",
        "tmnt_performance_facility_type": "Hydrodynamic Separator",
        "is_online": True,
        "validation_fallback": "NTFacility",
        "valid_model": "FlowFacility",
        "validator": "FlowFacility",
        "subbasin": "101012",
        "rain_gauge": "1130_LAGUNA_AUDUBON",
        "et_zone": "Zone6",
        "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
        "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
        "node_type": "flow_based_facility",
    },
    {
        "facility_type": "bioinfiltration",
        "design_storm_depth_inches": 0.91,
        "is_online": True,
        "tributary_area_tc_min": 15.0,
        "offline_diversion_rate_cfs": 17.773482892257434,
        "total_volume_cuft": 5000.0,
        "retention_volume_cuft": 0,  # zero retention
        "area_sqft": 950.0,
        "media_filtration_rate_inhr": 8.0,
        "hsg": "c",
        "constructor": "bioinfiltration_facility_constructor",
        "tmnt_performance_facility_type": "Biofiltration",
        "inf_rate_inhr": 0.24,
        "validation_fallback": "NTFacility",
        "valid_model": "BioInfFacility",
        "validator": "BioInfFacility",
        "subbasin": "101012",
        "rain_gauge": "1130_LAGUNA_AUDUBON",
        "et_zone": "Zone6",
        "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
        "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
        "retention_depth_ft": 0,
        "retention_ddt_hr": 0,
        "treatment_volume_cuft": 5000.0,
        "treatment_depth_ft": 2.9473684210526314,
        "treatment_ddt_hr": 4.421052631578947,
        "node_type": "volume_based_facility",
    },
    {
        "facility_type": "hds",
        "design_storm_depth_inches": 0.7414346515768613,
        "treatment_rate_cfs": 0.665505501038112,
        "tributary_area_tc_min": 4.0,  # bad tc
        "constructor": "flow_facility_constructor",
        "tmnt_performance_facility_type": "Hydrodynamic Separator",
        "is_online": True,
        "validation_fallback": "NTFacility",
        "valid_model": "FlowFacility",
        "validator": "FlowFacility",
        "subbasin": "101012",
        "rain_gauge": "1130_LAGUNA_AUDUBON",
        "et_zone": "Zone6",
        "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
        "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
        "node_type": "flow_based_facility",
    },
    {
        "node_id": "WQMP-1a-tmnt",
        "treatment_facilities": [
            {
                "node_id": "WQMP-1a-tmnt",
                "facility_type": "bioretention",
                "area_pct": 75,
                "captured_pct": 80,
                "retained_pct": 10,
                "tmnt_performance_facility_type": "Biofiltration",
            },
            {
                "node_id": "WQMP-1a-tmnt",
                "facility_type": "nt",
                "area_pct": 25,
                "captured_pct": 0,
                "retained_pct": 0,
                "tmnt_performance_facility_type": "nt",
            },
        ],
        "node_type": "site_based",
    },
    {
        "facility_type": "dry_well",
        "design_storm_depth_inches": 0.85,
        "is_online": True,
        "tributary_area_tc_min": 5.0,
        "total_volume_cuft": 2000.0,
        "treatment_rate_cfs": 2.5,
        "constructor": "dry_well_facility_constructor",
        "validation_fallback": "NTFacility",
        "validator": "DryWellFacility",
        "tmnt_performance_facility_type": "¯\\_(ツ)_/¯",
        "valid_model": "DryWellFacility",
        "subbasin": "10101000",
        "rain_gauge": "100_LAGUNABEACH",
        "et_zone": "Zone4",
        "volume_nomograph": "nomographs/100_LAGUNABEACH_volume_nomo.csv",
        "flow_nomograph": "nomographs/100_LAGUNABEACH_flow_nomo.csv",
        "retention_volume_cuft": 2000.0,
        "retention_ddt_hr": 0.22222,
        "node_type": "volume_based_facility",
    },
    {
        "facility_type": "dry_well",
        "design_storm_depth_inches": 0.85,
        "is_online": True,
        "tributary_area_tc_min": 0.0,  # bad tc
        "total_volume_cuft": 6000.0,
        "treatment_rate_cfs": 0.5,
        "constructor": "dry_well_facility_constructor",
        "validation_fallback": "NTFacility",
        "validator": "DryWellFacility",
        "tmnt_performance_facility_type": "¯\\_(ツ)_/¯",
        "valid_model": "DryWellFacility",
        "subbasin": "10101000",
        "rain_gauge": "100_LAGUNABEACH",
        "et_zone": "Zone4",
        "volume_nomograph": "nomographs/100_LAGUNABEACH_volume_nomo.csv",
        "flow_nomograph": "nomographs/100_LAGUNABEACH_flow_nomo.csv",
        "retention_volume_cuft": 4000.0,
        "retention_ddt_hr": 0.22222,
        "node_type": "dry_well_facility",
    },
    {
        "facility_type": "dry_weather_diversion",
        "ref_data_key": "10101000",
        "design_storm_depth_inches": 0.85,
        "tributary_area_tc_min": 5.0,
        "treatment_rate_cfs": 2.5,
        "constructor": "dw_and_low_flow_facility_constructor",
        "validation_fallback": "NTFacility",
        "validator": "LowFlowFacility",
        "tmnt_performance_facility_type": "¯\\_(ツ)_/¯",
        "valid_model": "LowFlowFacility",
        "design_capacity_cfs": 2.5,
        "months_operational": "summer",
        "subbasin": "10101000",
        "rain_gauge": "100_LAGUNABEACH",
        "et_zone": "Zone4",
        "volume_nomograph": "nomographs/100_LAGUNABEACH_volume_nomo.csv",
        "flow_nomograph": "nomographs/100_LAGUNABEACH_flow_nomo.csv",
        "ini_treatment_rate_cfs": 2.5,
        "summer_dry_weather_retention_rate_cfs": 2.5,
        "summer_dry_weather_treatment_rate_cfs": 0.0,
        "winter_dry_weather_retention_rate_cfs": 0.0,
        "winter_dry_weather_treatment_rate_cfs": 0.0,
        "node_type": "diversion_facility",
    },
    {
        "node_id": "BMP-Bio-simple",
        "facility_type": "bioretention_simple",
        "validator": "SimpleFacility",
        "validation_fallback": "NTFacility",
        "valid_model": "SimpleFacility",
        "captured_pct": 80,
        "retained_pct": 21,
        "tmnt_performance_facility_type": "Biofiltration",
        "node_type": "simple_facility",
        "constructor": "simple_facility_constructor",
    },
]


@pytest.mark.parametrize("tmnt_facility", tmnt_facilities)
@pytest.mark.parametrize("dwf_override", [False, True])  # default is false.
def test_facility_load_reduction(contexts, tmnt_facility, dwf_override):
    context = contexts["default"]

    g = nx.relabel_nodes(nx.gnr_graph(n=3, p=0.0, seed=0), lambda x: str(x))
    data = {
        "2": {
            "area_acres": 9.58071049103565,
            "imp_area_acres": 5.593145122640718,
            "perv_area_acres": 3.9875653683949315,
            "imp_ro_volume_cuft": 228016.14562485245,
            "perv_ro_volume_cuft": 55378.354666523395,
            "runoff_volume_cuft": 283394.50029137585,
            "eff_area_acres": 6.461638142128291,
            "developed_area_acres": 9.58071049103565,
            "TSS_load_lbs": 2258.8814515144954,
            "TCu_load_lbs": 0.9702150595320715,
            "FC_load_mpn": 4140816712319.9717,
            "winter_dwTSS_load_lbs": 251.83974023768664,
            "summer_dwTSS_load_lbs": 330.06583891090344,
            "winter_dwTCu_load_lbs": 0.10816800872990859,
            "summer_dwTCu_load_lbs": 0.14176700035928835,
            "winter_dwFC_load_mpn": 461654242414.25323,
            "summer_dwFC_load_mpn": 605052620628.5996,
            "winter_dry_weather_flow_cuft_psecond": 0.002874213147310695,
            "winter_dry_weather_flow_cuft": 31595.282386474148,
            "summer_dry_weather_flow_cuft_psecond": 0.002874213147310695,
            "summer_dry_weather_flow_cuft": 41409.36365593464,
            "land_surfaces_count": 1,
            "imp_pct": 58.37923114234624,
            "ro_coeff": 0.6744424798321826,
            "TSS_conc_mg/l": 127.68000000000005,
            "TCu_conc_ug/l": 54.84000000000001,
            "FC_conc_mpn/100ml": 51600.0,
            "winter_dwTSS_conc_mg/l": 127.68000000000008,
            "winter_dwTCu_conc_ug/l": 54.84,
            "winter_dwFC_conc_mpn/100ml": 51600.0,
            "summer_dwTSS_conc_mg/l": 127.68000000000005,
            "summer_dwTCu_conc_ug/l": 54.84,
            "summer_dwFC_conc_mpn/100ml": 51599.99999999999,
        },
    }

    if "site" not in tmnt_facility.get("node_type"):
        tmnt_facility["eliminate_all_dry_weather_flow_override"] = dwf_override
    else:
        for dct in tmnt_facility.get("treatment_facilities") or []:
            dct["eliminate_all_dry_weather_flow_override"] = dwf_override

    data["1"] = tmnt_facility

    nx.set_node_attributes(g, data)
    solve_watershed_loading(g, context)

    assert all(len(dct["node_errors"]) == 0 for n, dct in g.nodes(data=True))
    assert len(g.nodes["0"]["node_warnings"]) >= 1  # there is no node_id for this node.

    sum_ret = sum(nx.get_node_attributes(g, "runoff_volume_cuft_retained").values())
    sum_inflow = sum(nx.get_node_attributes(g, "runoff_volume_cuft").values())
    outflow = g.nodes["0"]["runoff_volume_cuft_total_discharged"]
    assert abs(sum_inflow - sum_ret - outflow) / sum_inflow < 1e-15

    scalers = [
        ("summer_dwTSS_load_lbs_removed", "summer_dwTSS_load_lbs_total_removed"),
        ("runoff_volume_cuft_retained", "runoff_volume_cuft_total_retained"),
        (
            "summer_dry_weather_flow_cuft_retained",
            "summer_dry_weather_flow_cuft_total_retained",
        ),
        (
            "summer_dry_weather_flow_cuft_psecond_retained",
            "summer_dry_weather_flow_cuft_psecond_total_retained",
        ),
    ]

    for s, t in scalers:
        outfall_total = g.nodes["0"][t]
        sum_individual = sum(nx.get_node_attributes(g, s).values())

        # assert that these add up
        assert abs(sum_individual - outfall_total) < 1e-6, (s, t)

    tmnt_node = g.nodes["1"]
    outfall_node = g.nodes["0"]

    m_op = tmnt_node.get("months_operational") or "both"
    if m_op == "both":
        seasons = ["summer", "winter"]
    else:
        seasons = [m_op]

    params = [
        ("summer_dwTSS_load_lbs", "summer_dwTSS_load_lbs_total_discharged"),
    ]

    if dwf_override:
        for s in ["summer", "winter"]:
            if s in seasons:  # this means the facility will retain all dw flow
                for k, v in outfall_node.items():
                    if all(c in k for c in [s, "inflow"]):
                        assert v == 0
                    if all(c in k for c in [s, "discharged"]):
                        assert v == 0
                    if all(c in k for c in [s, "conc", "influent"]):
                        assert v == 0
                    if all(c in k for c in [s, "conc", "effluent"]):
                        assert v == 0

                assert tmnt_node[f"{s}_dry_weather_flow_cuft_retained_pct"] > 99.9999
                assert tmnt_node[f"{s}_dry_weather_flow_cuft_captured_pct"] > 99.9999
                assert tmnt_node[f"{s}_dry_weather_flow_cuft_treated_pct"] < 0.00001

                if "site" not in tmnt_facility.get("node_type"):
                    assert (
                        tmnt_node[f"{s}_dry_weather_flow_cuft_psecond_retained_pct"]
                        > 99.9999
                    )
                    assert (
                        tmnt_node[f"{s}_dry_weather_flow_cuft_psecond_treated_pct"]
                        < 0.00001
                    )

            else:  # this means that the facility is not treating dw flow for this season
                for k, v in outfall_node.items():
                    if all(c in k for c in [s, "inflow"]):
                        assert v > 0
                    if all(c in k for c in [s, "discharged"]):
                        assert v > 0
                    if all(c in k for c in [s, "conc", "influent"]):
                        assert v > 0
                    if all(c in k for c in [s, "conc", "effluent"]):
                        assert v > 0

    if "diversion" not in tmnt_facility.get("facility_type", ""):
        assert tmnt_node["captured_pct"] > 0
        assert tmnt_node["TSS_load_lbs_removed"] > 0
        assert tmnt_node["runoff_volume_cuft_captured"] > 0
        assert tmnt_node["winter_dry_weather_flow_cuft_captured_pct"] > 0
        assert tmnt_node["TSS_load_lbs_inflow"] > tmnt_node["TSS_load_lbs_discharged"]
        assert (
            tmnt_node["winter_dwTSS_load_lbs_inflow"]
            > tmnt_node["winter_dwTSS_load_lbs_discharged"]
        )

        params += [
            ("TSS_load_lbs", "TSS_load_lbs_total_discharged"),
            ("winter_dwTSS_load_lbs", "winter_dwTSS_load_lbs_total_discharged"),
        ]

    for s, t in params:
        outfall_total = outfall_node[t]
        sum_individual = sum(nx.get_node_attributes(g, s).values())

        # assert that load reduction occurred
        assert outfall_total < sum_individual, (s, t)

    assert tmnt_node["summer_dry_weather_flow_cuft_captured_pct"] > 0
    assert (
        tmnt_node["summer_dwTSS_load_lbs_inflow"]
        > tmnt_node["summer_dwTSS_load_lbs_discharged"]
    )

    for _n, dct in g.nodes(data=True):
        if "_nomograph_solution_status" in dct:
            assert "successful" in dct["_nomograph_solution_status"]


@pytest.mark.parametrize(
    "facility_data",
    [
        {
            "test_model": "DryWellFacilityFlowOrVolume",
            "treatment_rate_cfs": 0.001,
            "total_volume_cuft": 40,
        },
        {
            "test_model": "DryWellFacilityFlowOrVolume",
            "treatment_rate_cfs": 0.001,
            "total_volume_cuft": 0,
        },
        {
            "test_model": "DryWellFacility",
            "treatment_rate_cfs": 0.001,
            "total_volume_cuft": 40,
        },
    ]
    + [{"test_model": i.schema()["title"]} for i in TREATMENT_FACILITY_MODELS],
)
def test_single_facility_watershed(
    contexts, valid_treatment_facility_dicts, facility_data
):
    tmnt = deepcopy(valid_treatment_facility_dicts[facility_data["test_model"]])
    tmnt.update(facility_data)
    tmnt["node_id"] = "0"
    tmnt["months_operational"] = "both"
    wshd = {
        "graph": {
            "directed": True,
            "edges": [
                {"source": "1", "target": "0"},
            ],
        },
        "land_surfaces": [
            {
                "area_acres": 12,
                "imp_area_acres": 7.5,
                "node_id": "1",
                "surface_key": "10101200-RESSFH-C-5",
            },
        ],
        "treatment_facilities": [tmnt],
    }

    g, _ = initialize_graph(
        wshd, treatment_pre_validated=False, context=contexts["default"]
    )
    solve_watershed_loading(g, context=contexts["default"])

    tmnt_node = g.nodes["0"]

    node_type = tmnt_node.get("node_type", "")
    valid_model = tmnt_node.get("valid_model", "")

    if "drywell" in valid_model.lower():
        assert tmnt_node.get("runoff_volume_cuft_retained", 0) > 0.0
        assert tmnt_node.get("winter_dry_weather_flow_cuft_retained", 0) > 0
        assert tmnt_node.get("summer_dry_weather_flow_cuft_retained", 0) > 0

        assert tmnt_node.get("treated_pct", 0) < 0.1
        assert tmnt_node.get("winter_dry_weather_flow_cuft_treated", 0) == 0
        assert tmnt_node.get("summer_dry_weather_flow_cuft_treated", 0) == 0

    if any(t in node_type for t in ["dry_weather_only", "diversion_facility"]):
        assert tmnt_node.get("runoff_volume_cuft_captured", 0) == 0.0  # no wet weather
        assert tmnt_node.get("winter_dry_weather_flow_cuft_captured", 0) > 0
        assert tmnt_node.get("summer_dry_weather_flow_cuft_captured", 0) > 0

    elif node_type:
        assert tmnt_node.get("runoff_volume_cuft_captured", 0) > 0.0
        assert tmnt_node.get("winter_dry_weather_flow_cuft_captured", 0) > 0
        assert tmnt_node.get("summer_dry_weather_flow_cuft_captured", 0) > 0

    else:
        assert tmnt_node.get("runoff_volume_cuft_captured", 0) == 0.0
        assert tmnt_node.get("winter_dry_weather_flow_cuft_captured", 0) == 0
        assert tmnt_node.get("summer_dry_weather_flow_cuft_captured", 0) == 0


@pytest.mark.parametrize(
    "f9, f2, upstream_ret",
    [
        (tmnt_facilities[0], tmnt_facilities[0], True),
        (tmnt_facilities[1], tmnt_facilities[0], True),
        (tmnt_facilities[2], tmnt_facilities[0], False),
        (tmnt_facilities[3], tmnt_facilities[0], False),
        (tmnt_facilities[0], tmnt_facilities[4], False),
    ],
)
def test_nested_treatment_facilities(
    contexts, watershed_graph, initial_node_data, f9, f2, upstream_ret
):
    g, data = watershed_graph, deepcopy(initial_node_data)
    context = contexts["default"]

    data["9"] = f9
    data["2"] = f2

    nx.set_node_attributes(g, data)
    solve_watershed_loading(g, context)

    sum_ret = sum(nx.get_node_attributes(g, "runoff_volume_cuft_retained").values())
    sum_inflow = sum(nx.get_node_attributes(g, "runoff_volume_cuft").values())
    outflow = g.nodes["0"]["runoff_volume_cuft_total_discharged"]

    assert abs(sum_inflow - sum_ret - outflow) / sum_inflow < 1e-15


def test_invalid_graph(contexts, subbasins, land_surface_permutations):
    context = contexts["default"]

    g = nx.gnc_graph(10)
    data = generate_random_watershed_solve_request_from_graph(
        g, context, ref_data_keys=subbasins, surface_keys=land_surface_permutations
    )

    g, err = initialize_graph(data, False, context)

    assert len(err) > 0


@pytest.mark.parametrize("ctx_key", ["default", "default_no_dw_valid"])
def test_watershed_graph_land_surface_only(
    contexts, watershed_graph, initial_node_data, ctx_key
):
    g, data = watershed_graph, deepcopy(initial_node_data)
    context = contexts[ctx_key]

    nx.set_node_attributes(g, data)
    solve_watershed_loading(g, context)

    surface_discharges = nx.get_node_attributes(g, "runoff_volume_cuft")
    sum_inflow = sum(surface_discharges.values())
    outflow = g.nodes["0"]["runoff_volume_cuft_total_discharged"]

    assert sum_inflow > 0, f"error, no runoff generated: {surface_discharges}"
    assert outflow > 0, "error, no runoff observed at outfall"
    assert (
        abs(sum_inflow - outflow) / sum_inflow < 1e-15
    ), f"sum inflow: {sum_inflow:.2f}; outfall: {outflow:.2f}"

    return

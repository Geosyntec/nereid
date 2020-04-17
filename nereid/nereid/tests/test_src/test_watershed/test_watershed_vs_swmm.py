from io import StringIO

import networkx as nx
import pandas
import pytest

from nereid.core.utils import get_request_context
from nereid.src.nomograph.nomo import load_nomograph_mapping
from nereid.src.tmnt_performance.tasks import effluent_function_map
from nereid.src.watershed.solve_watershed import solve_node
from nereid.src.wq_parameters import init_wq_parameters


@pytest.fixture
def swmm_results():
    swmm = """
    node_id type    vol_Mgal    captured_pct    retained_pct
    BMP_Dist1   STORAGE 70.6    48.16   14.05
    BMP_Dist2   STORAGE 64.9    42.06   42.06
    BMP_Redev1  STORAGE 32.7    77.74   35.78
    BMP_Redev2  STORAGE 57.8    51.38   15.14
    BMP_Redev3  STORAGE 78.3    77.27   0.00
    BMP_Redev4  STORAGE 164.0   63.66   20.91
    BMP_Reg1    STORAGE 641.0   42.90   27.61
    BMP_Reg2    STORAGE 637.0   19.62   19.62
    BMP_Reg3    STORAGE 788.0   49.49   0.00
    BMP_Reg4    STORAGE 7360.0  35.05   15.76
    """
    swmm_df = pandas.read_csv(StringIO(swmm), sep=r"\s+").assign(
        node_id=lambda df: df["node_id"].str.lower().str.replace("_", "-")
    )
    return swmm_df


@pytest.fixture
def realistic_graph():
    edgelist = [
        ("reg1", "bmp-reg1"),
        ("bmp-reg1", "bmp-reg4"),
        ("dist1", "bmp-dist1"),
        ("redev3", "bmp-redev3"),
        ("dist2", "bmp-dist2"),
        ("reg3", "bmp-reg3"),
        ("bmp-dist1", "bmp-reg3"),
        ("bmp-redev3", "bmp-reg3"),
        ("bmp-dist2", "bmp-reg3"),
        ("redev1", "bmp-redev1"),
        ("redev2", "bmp-redev2"),
        ("bmp-redev2", "bmp-reg2"),
        ("reg2", "bmp-reg2"),
        ("bmp-redev1", "bmp-reg2"),
        ("reg4", "bmp-reg4"),
        ("bmp-reg2", "bmp-reg4"),
        ("bmp-reg4", "of"),
        ("redev4", "bmp-redev4"),
        ("bmp-redev4", "bmp-reg4"),
        ("bmp-reg3", "bmp-reg4"),
    ]

    facility_info = {
        "bmp-reg1": {
            "node_id": "bmp-reg1",
            "node_type": "volume_based_facility",
            "regional_subbasin": "reg1",
            "design_storm_depth_inches": 1,
            "retention_ddt_hr": 96,
            "treatment_ddt_hr": 48,
            "retention_volume_cuft": 65500,
            "treatment_volume_cuft": 65500,
            "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
            "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
            "tmnt_performance_facility_type": "Biofiltration",
        },
        "bmp-dist1": {
            "node_id": "bmp-dist1",
            "node_type": "volume_based_facility",
            "regional_subbasin": "reg3",
            "design_storm_depth_inches": 1,
            "retention_ddt_hr": 72,
            "treatment_ddt_hr": 12,
            "retention_volume_cuft": 3000,
            "treatment_volume_cuft": 7000,
            "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
            "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
            "tmnt_performance_facility_type": "Biofiltration",
        },
        "bmp-redev3": {
            "node_id": "bmp-redev3",
            "node_type": "volume_based_facility",
            "regional_subbasin": "reg3",
            "design_storm_depth_inches": 1,
            "retention_ddt_hr": 48,
            "treatment_ddt_hr": 48,
            "retention_volume_cuft": 0,
            "treatment_volume_cuft": 39000,
            "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
            "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
            "tmnt_performance_facility_type": "Biofiltration",
        },
        "bmp-dist2": {
            "node_id": "bmp-dist2",
            "node_type": "volume_based_facility",
            "regional_subbasin": "reg3",
            "design_storm_depth_inches": 1,
            "retention_ddt_hr": 120,
            "treatment_ddt_hr": 48,
            "retention_volume_cuft": 15000,
            "treatment_volume_cuft": 0,
            "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
            "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
            "tmnt_performance_facility_type": "Biofiltration",
        },
        "bmp-redev2": {
            "node_id": "bmp-redev2",
            "node_type": "volume_based_facility",
            "regional_subbasin": "reg2",
            "design_storm_depth_inches": 1,
            "retention_ddt_hr": 96,
            "treatment_ddt_hr": 12,
            "retention_volume_cuft": 3000,
            "treatment_volume_cuft": 6000,
            "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
            "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
            "tmnt_performance_facility_type": "Biofiltration",
        },
        "bmp-redev1": {
            "node_id": "bmp-redev1",
            "node_type": "volume_based_facility",
            "regional_subbasin": "reg2",
            "design_storm_depth_inches": 1,
            "retention_ddt_hr": 48,
            "treatment_ddt_hr": 12,
            "retention_volume_cuft": 4000,
            "treatment_volume_cuft": 8000,
            "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
            "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
            "tmnt_performance_facility_type": "Biofiltration",
        },
        "bmp-reg2": {
            "node_id": "bmp-reg2",
            "node_type": "volume_based_facility",
            "regional_subbasin": "reg2",
            "design_storm_depth_inches": 1,
            "retention_ddt_hr": 480,
            "treatment_ddt_hr": 48,
            "retention_volume_cuft": 98000,
            "treatment_volume_cuft": 0,
            "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
            "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
            "tmnt_performance_facility_type": "Biofiltration",
        },
        "bmp-reg4": {
            "node_id": "bmp-reg4",
            "node_type": "volume_based_facility",
            "regional_subbasin": "reg4",
            "design_storm_depth_inches": 1,
            "retention_ddt_hr": 240,
            "treatment_ddt_hr": 48,
            "retention_volume_cuft": 588000,
            "treatment_volume_cuft": 588000,
            "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
            "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
            "tmnt_performance_facility_type": "Biofiltration",
        },
        "bmp-redev4": {
            "node_id": "bmp-redev4",
            "node_type": "volume_based_facility",
            "regional_subbasin": "reg4",
            "design_storm_depth_inches": 1,
            "retention_ddt_hr": 96,
            "treatment_ddt_hr": 12,
            "retention_volume_cuft": 13000,
            "treatment_volume_cuft": 26000,
            "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
            "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
            "tmnt_performance_facility_type": "Biofiltration",
        },
        "bmp-reg3": {
            "node_id": "bmp-reg3",
            "node_type": "volume_based_facility",
            "regional_subbasin": "reg3",
            "design_storm_depth_inches": 1,
            "retention_ddt_hr": 48,
            "treatment_ddt_hr": 48,
            "retention_volume_cuft": 0,
            "treatment_volume_cuft": 154000,
            "volume_nomograph": "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
            "flow_nomograph": "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
            "tmnt_performance_facility_type": "Biofiltration",
        },
    }

    land_surface_data = {
        "reg1": {
            "node_id": "reg1",
            "eff_area_acres": 97.5,
            "runoff_volume_cuft": 1365.0,
        },
        "reg2": {
            "node_id": "reg2",
            "eff_area_acres": 84.375,
            "runoff_volume_cuft": 1181.25,
        },
        "dist1": {
            "node_id": "dist1",
            "eff_area_acres": 10.5,
            "runoff_volume_cuft": 147.0,
        },
        "redev3": {
            "node_id": "redev3",
            "eff_area_acres": 11.25,
            "runoff_volume_cuft": 157.5,
        },
        "dist2": {
            "node_id": "dist2",
            "eff_area_acres": 9.75,
            "runoff_volume_cuft": 136.5,
        },
        "reg3": {
            "node_id": "reg3",
            "eff_area_acres": 91.875,
            "runoff_volume_cuft": 1286.25,
        },
        "redev1": {
            "node_id": "redev1",
            "eff_area_acres": 4.725,
            "runoff_volume_cuft": 66.15,
        },
        "redev2": {
            "node_id": "redev2",
            "eff_area_acres": 8.25,
            "runoff_volume_cuft": 115.5,
        },
        "reg4": {
            "node_id": "reg4",
            "eff_area_acres": 840.0,
            "runoff_volume_cuft": 11760.0,
        },
        "redev4": {
            "node_id": "redev4",
            "eff_area_acres": 24.0,
            "runoff_volume_cuft": 336.0,
        },
    }

    node_data = {**facility_info, **land_surface_data}

    g = nx.DiGraph(edgelist)
    nx.set_node_attributes(g, node_data)

    return g


def test_watershed_vs_swmm(contexts, realistic_graph, swmm_results):

    context = contexts["default"]

    # This is necessary because the swmm runs sized the facilities with the assumption that
    # the design storm is 1". This does not match the actual rainfall record simulated in swmm
    # meaning that the basins are slightly oversized (actual design storm depth is 0.89"). To
    # correct for this and use the nomographs that use a vol/design vol x-axis normalization, we
    # need to use a scaler of 1/.89 in order to get the correct x position on the normalized scale.
    # this means that by doing the interpolation on the nomographs 'depth_inches' column we can
    # correct for this scaler offset.
    # double check this size_factor -> depth_inches value.
    context["project_reference_data"]["met_table"]["volume_nomo"][
        "x_col"
    ] = "depth_inches"

    wet_weather_parameters = init_wq_parameters(
        "land_surface_emc_table", context=context
    )
    wet_weather_facility_performance_map = effluent_function_map(
        "tmnt_performance_table", context=context
    )
    nomograph_map = load_nomograph_mapping(context=context)

    g = realistic_graph

    for node in nx.lexicographical_topological_sort(g):
        solve_node(
            g,
            node,
            wet_weather_parameters,
            [],
            wet_weather_facility_performance_map,
            {},
            nomograph_map,
        )

    assert all([len(dct["node_errors"]) == 0 for n, dct in g.nodes(data=True)])

    sum_ret = sum(nx.get_node_attributes(g, "runoff_volume_cuft_retained").values())
    sum_inflow = sum(nx.get_node_attributes(g, "runoff_volume_cuft").values())
    sum_discharge = g.nodes["of"]["runoff_volume_cuft_total_discharged"]
    assert abs(sum_inflow - sum_discharge - sum_ret) < 1e-3

    results = (
        pandas.DataFrame([v for k, v in g.nodes(data=True)])
        .query("node_type=='volume_based_facility'")[
            ["node_id", "captured_pct", "retained_pct"]
        ]
        .merge(swmm_results, on="node_id")
        .assign(cap_diff=lambda df: df["captured_pct_x"] - df["captured_pct_y"])
        .assign(ret_diff=lambda df: df["retained_pct_x"] - df["retained_pct_y"])
    )

    assert all(results.cap_diff.abs() < 5)
    assert all(results.ret_diff.abs() < 4)

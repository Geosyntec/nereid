from pathlib import Path

import pytest
import pandas

import nereid.core.io
import nereid.data
from nereid.core import io


def test_io_load_multiple_cfgs():
    cfgbase = Path(nereid.core.io.__file__).parent.resolve() / "base_config.yml"
    cfgdata = (
        Path(nereid.data.__file__).parent.resolve()
        / "default_data"
        / "state"
        / "region"
        / "config.yml"
    )

    dct = io.load_multiple_cfgs(files=[cfgbase, cfgdata])
    assert "test" in dct  # from cfgdata
    assert "default_data_directory" in dct  # from cfgbase


@pytest.mark.parametrize(
    "table",
    [
        "land_surface_table",
        "land_surface_emc_table",
        "met_table",
        "tmnt_performance_table",
    ],
)
@pytest.mark.parametrize(
    "key",
    [
        "default",
        "default_lst_no_expanded_fields_valid",
        "default_emc_no_params_valid",
        "default_api_no_ls_joins_valid",
        "default_api_no_ls_remaps_valid",
        "default_api_no_ls_joins_or_remaps_valid",
        "default_api_ls_joins_no_merge_no_params_valid",
        "default_api_ls_joins_other_dne_valid",
        "default_api_ls_remap_left_dne_valid",
        "default_api_ls_remap_how_dne_valid",
        "default_api_ls_remap_right_dne_valid",
    ],
)
def test_load_ref_data(contexts, table, key):

    context = contexts[key]
    ref_table = io.load_ref_data(table, context)
    assert len(ref_table) > 1


@pytest.mark.parametrize("n_rows", [10])
@pytest.mark.parametrize("n_nodes", [5])
@pytest.mark.parametrize("recog", ["land_surfaces", r"¯\_(ツ)_/¯"])
@pytest.mark.parametrize(
    "key, raises_msgs",
    [
        ("default", False),
        ("default_api_no_ls_remaps_valid", False),
        ("default_api_no_ls_joins_or_remaps_valid", False),
        ("default_api_ls_joins_no_merge_no_params_valid", False),
        ("default_lst_no_expanded_fields_valid", True),
        ("default_api_no_ls_joins_valid", True),
        ("default_api_ls_joins_other_dne_valid", True),
        ("default_api_ls_remap_left_dne_valid", True),
        ("default_api_ls_remap_how_dne_valid", True),
        ("default_api_ls_remap_right_dne_valid", True),
        ("default_lst_expand_field_dne_valid", True),
    ],
)
def test_parse_api_recognize(
    contexts,
    land_surface_loading_response_dicts,
    recog,
    key,
    raises_msgs,
    n_rows,
    n_nodes,
):

    context = contexts[key]

    land_surfaces = land_surface_loading_response_dicts[(n_rows, n_nodes)]
    land_surfaces_list = land_surfaces["land_surfaces"]
    df = pandas.DataFrame(land_surfaces_list)

    if recog == "land_surfaces":
        df["imp_pct"] = 100 * df["imp_area_acres"] / df["area_acres"]
    df, msg = io.parse_configuration_logic(df, "api_recognize", recog, context)
    if recog in ["land_surfaces", "treatment_facility"] and not raises_msgs:
        assert len(msg) == 0
    else:
        assert len(msg) > 0

from pathlib import Path

import numpy
import pandas
import pytest

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
    assert "facility_type" in dct["api_recognize"]["treatment_facility"]


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
        "default_lst_no_collapse_fields_valid",
        "default_lst_collapse_fields_valid",
        "default_no_dw_valid",
    ],
)
def test_load_ref_data(contexts, table, key):
    context = contexts[key]
    ref_table, msg = io.load_ref_data(table, context)
    assert ref_table is not None
    assert len(ref_table) > 1, ref_table
    assert all("error" not in m.lower() for m in msg), msg


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
        ("default_lst_no_expanded_fields_valid", False),
        ("default_api_no_ls_joins_valid", False),
        ("default_api_ls_joins_other_dne_valid", True),
        ("default_api_ls_remap_left_dne_valid", True),
        ("default_api_ls_remap_how_dne_valid", True),
        ("default_api_ls_remap_right_dne_valid", True),
        ("default_lst_expand_field_dne_valid", True),
        ("default_lst_no_collapse_fields_valid", True),
        ("default_lst_collapse_fields_valid", False),
        ("default_no_dw_valid", False),
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
    if key == "default" and recog == "land_surfaces":
        # test how=addend
        assert all(df.query('soil == "water"').imp_pct.ge(100).values), df.query(
            'soil == "water"'
        ).imp_pct

        # test how=left
        assert all(df.query('land_use == "COMM"').is_developed.values)
        assert all(
            numpy.invert(
                df.query('land_use == "WATER"').is_developed.values.astype(bool)
            )
        ), df.query('land_use == "WATER"')

    if recog in ["land_surfaces", "treatment_facility"] and not raises_msgs:
        assert len(msg) == 0, msg
    else:
        assert len(msg) > 0, msg

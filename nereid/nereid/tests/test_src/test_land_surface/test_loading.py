import numpy
import pandas
import pytest

from nereid.core.io import parse_configuration_logic
from nereid.src.land_surface.loading import (
    clean_land_surface_dataframe,
    detailed_loading_results,
    detailed_pollutant_loading_results,
    detailed_volume_loading_results,
)
from nereid.src.wq_parameters import init_wq_parameters


@pytest.mark.parametrize("n_rows", [10])
@pytest.mark.parametrize("n_nodes", [5])
def test_build_land_surface_dataframe(
    land_surface_loading_response_dicts, n_rows, n_nodes
):

    land_surfaces = land_surface_loading_response_dicts[(n_rows, n_nodes)]
    land_surfaces_list = land_surfaces["land_surfaces"]
    df = pandas.DataFrame(land_surfaces_list)
    df["imp_pct"] = 100 * df["imp_area_acres"] / df["area_acres"]
    land_surfaces_df = clean_land_surface_dataframe(df)

    total_area = sum([ls["area_acres"] for ls in land_surfaces_list])
    numpy.testing.assert_allclose(total_area, land_surfaces_df["area_acres"].sum())


@pytest.mark.parametrize("n_rows", [10])
@pytest.mark.parametrize("n_nodes", [5])
@pytest.mark.parametrize(
    "key",
    [
        "default",
        "default_emc_no_params_valid",
        # "default_api_no_ls_remaps_valid",
        "default_api_ls_joins_no_merge_no_params_valid",
        "default_dw_flow_null_months_valid",
        "default_dw_flow_unknown_season_valid",
    ],
)
def test_detailed_land_surface_loading_results(
    land_surface_loading_response_dicts, contexts, key, n_rows, n_nodes
):

    land_surfaces = land_surface_loading_response_dicts[(n_rows, n_nodes)]
    land_surfaces_list = land_surfaces["land_surfaces"]
    df = pandas.DataFrame(land_surfaces_list)
    context = contexts[key]
    df["imp_pct"] = 100 * df["imp_area_acres"] / df["area_acres"]

    df, msg = parse_configuration_logic(
        df=df,
        config_section="api_recognize",
        config_object="land_surfaces",
        context=context,
    )

    land_surfaces_df = clean_land_surface_dataframe(df)

    wet_weather_parameters = init_wq_parameters("land_surface_emc_table", context)
    dry_weather_parameters = init_wq_parameters(
        "dry_weather_land_surface_emc_table", context
    )

    seasons = (
        context.get("project_reference_data", {})
        .get("dry_weather_flow_table", {})
        .get("seasons", {})
    )

    t = detailed_loading_results(
        land_surfaces_df,
        wet_weather_parameters,
        dry_weather_parameters,
        seasons,
    )
    assert t["area_acres"].sum() == land_surfaces_df["area_acres"].sum()
    assert len(t) == len(land_surfaces_list)
    if not "no_joins" in key and not "no_params" in key:
        assert any(["conc" in c for c in t.columns])
        assert any(["load" in c for c in t.columns])

    t = detailed_volume_loading_results(land_surfaces_df)
    assert t["area_acres"].sum() == land_surfaces_df["area_acres"].sum()
    assert len(t) == len(land_surfaces_list)
    assert t["runoff_volume_cuft"].sum() > 0

    t = detailed_pollutant_loading_results(
        land_surfaces_df,
        wet_weather_parameters,
        dry_weather_parameters,
        seasons.keys(),
    )
    assert t["area_acres"].sum() == land_surfaces_df["area_acres"].sum()
    assert len(t) == len(land_surfaces_list)
    if not "no_joins" in key and not "no_params" in key:
        assert any(["conc" in c for c in t.columns])
        assert any(["load" in c for c in t.columns])


def test_detailed_land_surface_volume_loading_results(
    known_land_surface_volume_loading_result,
):

    numpy.random.seed(42)
    size = 2
    MAP = 10  # inches
    area_acres = numpy.random.randint(0, 11, size)
    imp_area_acres = numpy.round(numpy.random.random(size) * area_acres, 1)
    perv_ro_depth_inches = numpy.random.randint(0, 5, size)
    imp_ro_depth_inches = 2 * perv_ro_depth_inches
    perv_ro_coeff = perv_ro_depth_inches / MAP
    imp_ro_coeff = imp_ro_depth_inches / MAP

    input_df = pandas.DataFrame(
        dict(
            area_acres=area_acres,
            imp_area_acres=imp_area_acres,
            is_developed=[True, True],
            perv_ro_depth_inches=perv_ro_depth_inches,
            imp_ro_depth_inches=imp_ro_depth_inches,
            perv_ro_coeff=perv_ro_coeff,
            imp_ro_coeff=imp_ro_coeff,
        )
    )

    result = detailed_volume_loading_results(input_df).round(2)
    known = known_land_surface_volume_loading_result
    numpy.testing.assert_array_equal(result, known)


def test_detailed_land_surface_pollutant_loading_results(
    known_land_surface_pollutant_loading_result,
):
    numpy.random.seed(42)
    size = 4

    runoff_volume_cuft = numpy.random.randint(0, 4, size)
    FC_conc = numpy.random.randint(0, 1e5, size)  # mpn/100ml
    TCu_conc = numpy.random.randint(0, 1000, size)  # ug/l
    TSS_conc = numpy.random.randint(0, 1000, size)  # mg/l

    input_df = pandas.DataFrame(
        {
            "runoff_volume_cuft": runoff_volume_cuft,
            "FC_conc_mpn/100ml": FC_conc,
            "TCu_conc_ug/l": TCu_conc,
            "TSS_conc_mg/l": TSS_conc,
        }
    )
    parameters = [
        {
            "long_name": "Total Suspended Solids",
            "short_name": "TSS",
            "concentration_unit": "mg/L",
            "load_unit": "lbs",
            "load_col": "TSS_load_lbs",
            "conc_col": "TSS_conc_mg/l",
            "load_to_conc_factor": 16018.463373960149,
            "conc_to_load_factor": 6.24279605761446e-05,
        },
        {
            "long_name": "Total Copper",
            "short_name": "TCu",
            "concentration_unit": "ug/L",
            "load_unit": "lbs",
            "load_col": "TCu_load_lbs",
            "conc_col": "TCu_conc_ug/l",
            "load_to_conc_factor": 16018463.373960149,
            "conc_to_load_factor": 6.242796057614458e-08,
        },
        {
            "long_name": "Fecal Coliform",
            "short_name": "FC",
            "concentration_unit": "MPN/_100mL",
            "load_unit": "mpn",
            "load_col": "FC_load_mpn",
            "conc_col": "FC_conc_mpn/100ml",
            "load_to_conc_factor": 0.00353146667214886,
            "conc_to_load_factor": 283.1684659199999,
        },
    ]

    def sigfigs(x, N):

        if x > 0 or x < 0:
            return numpy.round(x, 4 - int(numpy.floor(numpy.log10(abs(x)))))
        else:
            return 0

    result = detailed_pollutant_loading_results(input_df, parameters, [], []).applymap(
        lambda x: sigfigs(x, 4)
    )
    known = known_land_surface_pollutant_loading_result
    numpy.testing.assert_allclose(result, known, rtol=1e-7, atol=1e-6)

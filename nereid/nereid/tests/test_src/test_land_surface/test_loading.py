import pytest
import pandas
import numpy

from nereid.core.utils import get_request_context
from nereid.src.land_surface.io import load_land_surface_data
from nereid.src.land_surface.loading import (
    detailed_land_surface_loading_results,
    detailed_land_surface_volume_loading_results,
    detailed_land_surface_pollutant_loading_results,
    summary_land_surface_loading_results,
)


@pytest.mark.parametrize("n_rows", [10])
@pytest.mark.parametrize("n_nodes", [5])
@pytest.mark.parametrize(
    "key",
    [
        "default",
        "land_surface_table_no_joins",
        "land_surface_table_no_joins_no_expanded_fields",
        "land_surface_emc_table_no_params",
    ],
)
def test_detailed_land_surface_loading_results(
    land_surface_loading_response_dicts,
    land_surface_data_contexts,
    key,
    n_rows,
    n_nodes,
):

    land_surfaces = land_surface_loading_response_dicts[(n_rows, n_nodes)]
    context = land_surface_data_contexts[key]

    parameters = context["project_reference_data"]["land_surface_emc_table"].get(
        "parameters", []
    )

    ref_table_df = load_land_surface_data(context)
    land_surfaces_list = land_surfaces["land_surfaces"]

    land_surfaces_df = pandas.DataFrame(land_surfaces_list).merge(
        ref_table_df,
        left_on="surface_key",
        right_on="surface_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    t = detailed_land_surface_loading_results(land_surfaces_df, parameters)
    assert t["area_acres"].sum() == land_surfaces_df["area_acres"].sum()
    assert len(t) == len(land_surfaces_list)
    if not "no_joins" in key and not "no_params" in key:
        assert any(["conc" in c for c in t.columns])
        assert any(["load" in c for c in t.columns])

    t = detailed_land_surface_volume_loading_results(land_surfaces_df)
    assert t["area_acres"].sum() == land_surfaces_df["area_acres"].sum()
    assert len(t) == len(land_surfaces_list)
    assert t["runoff_volume_cuft"].sum() > 0

    t = detailed_land_surface_pollutant_loading_results(land_surfaces_df, parameters)
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
            perv_ro_depth_inches=perv_ro_depth_inches,
            imp_ro_depth_inches=imp_ro_depth_inches,
            perv_ro_coeff=perv_ro_coeff,
            imp_ro_coeff=imp_ro_coeff,
        )
    )

    result = detailed_land_surface_volume_loading_results(input_df).round(2)
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
        {"long_name": "Total Suspended Solids", "short_name": "TSS", "unit": "mg/L"},
        {"long_name": "Total Copper", "short_name": "TCu", "unit": "ug/L"},
        {"long_name": "Fecal Coliform", "short_name": "FC", "unit": "MPN/100mL"},
    ]

    def sigfigs(x, N):

        if x > 0 or x < 0:
            return numpy.round(x, 4 - int(numpy.floor(numpy.log10(abs(x)))))
        else:
            return 0

    result = detailed_land_surface_pollutant_loading_results(
        input_df, parameters
    ).applymap(lambda x: sigfigs(x, 4))
    known = known_land_surface_pollutant_loading_result
    numpy.testing.assert_allclose(result, known, rtol=1e-7, atol=1e-6)

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

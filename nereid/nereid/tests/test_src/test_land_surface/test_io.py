import pytest
from nereid.src.land_surface.io import load_land_surface_data


@pytest.mark.parametrize(
    "key",
    [
        "default",
        "land_surface_table_no_joins",
        "land_surface_table_no_joins_no_expanded_fields",
        "land_surface_emc_table_dne",
        "land_surface_emc_table_no_params",
    ],
)
def test_land_surface_loading(land_surface_data_contexts, key):

    context = land_surface_data_contexts[key]
    ref_table = load_land_surface_data(context)
    assert "surface_id" in ref_table

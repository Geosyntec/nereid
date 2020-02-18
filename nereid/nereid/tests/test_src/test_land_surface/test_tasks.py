import pytest

from nereid.core.utils import get_request_context
from nereid.src.land_surface.tasks import land_surface_loading


@pytest.mark.parametrize("details", [True, False])
@pytest.mark.parametrize("n_rows", [10, 50, 5000])
@pytest.mark.parametrize("n_nodes", [5, 50, 1000])
def test_land_surface_loading(
    land_surface_loading_response_dicts, details, n_rows, n_nodes
):
    key = n_rows, n_nodes
    land_surfaces = land_surface_loading_response_dicts[key]
    context = get_request_context()
    result = land_surface_loading(land_surfaces, details, context)

    return

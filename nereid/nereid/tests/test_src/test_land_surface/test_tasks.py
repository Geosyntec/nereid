import pytest

from nereid.core.context import get_request_context
from nereid.src.land_surface.tasks import land_surface_loading


@pytest.mark.parametrize("details", [True, False])
@pytest.mark.parametrize("n_rows", [10, 50, 5000])
@pytest.mark.parametrize("n_nodes", [5, 50, 1000])
def test_land_surface_loading(
    land_surface_loading_response_dicts, details, n_rows, n_nodes
):
    key = n_rows, n_nodes
    land_surfaces = land_surface_loading_response_dicts[key]
    result = land_surface_loading(land_surfaces, details, context=get_request_context())

    assert result.get("summary") is not None
    assert len(result.get("summary")) <= len(land_surfaces["land_surfaces"])

    if details:
        assert result.get("details") is not None
        assert len(result.get("details")) == len(land_surfaces["land_surfaces"])


@pytest.mark.parametrize("details", [True, False])
@pytest.mark.parametrize("n_rows", [10])
@pytest.mark.parametrize("n_nodes", [5])
def test_land_surface_loading_with_err(
    land_surface_loading_response_dicts, details, n_rows, n_nodes
):
    key = n_rows, n_nodes
    land_surfaces = land_surface_loading_response_dicts[key]

    land_surfaces["land_surfaces"][5]["surface_key"] = r"¯\_(ツ)_/¯"
    result = land_surface_loading(land_surfaces, details, context=get_request_context())

    assert "ERROR" in result.get("errors", ["nope"])[0]
    assert result.get("summary") is not None
    assert len(result.get("summary")) <= len(land_surfaces["land_surfaces"])

    if details:
        assert result.get("details") is not None
        assert len(result.get("details")) == len(land_surfaces["land_surfaces"])

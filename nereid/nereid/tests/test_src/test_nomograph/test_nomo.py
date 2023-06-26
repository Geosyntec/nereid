import numpy
import pytest

from nereid.core.io import load_ref_data
from nereid.src.nomograph.interpolators import bisection_search
from nereid.src.nomograph.nomo import (
    build_nomo,
    get_flow_nomograph,
    get_volume_nomograph,
)
from nereid.tests.utils import TEST_PATH

try:
    import matplotlib
except ImportError:
    matplotlib = None


@pytest.mark.parametrize(
    "path, name, x, t, z, exception",
    [
        (
            "volume_nomo.csv",
            "VolumeNomograph",
            "size_fraction",
            "ddt_hr",
            "capture_fraction",
            None,
        ),
        (
            "none.csv",
            "VolumeNomograph",
            "size_fraction",
            "ddt_hr",
            "capture_fraction",
            FileNotFoundError,
        ),
        (
            "flow_nomo.csv",
            "FlowNomograph",
            "intensity_inhr",
            "tc_minutes",
            "performance_frac",
            None,
        ),
        (
            "flow_nomo.csv",
            "OtherNomograph",
            "intensity_inhr",
            "tc_minutes",
            "performance_frac",
            NotImplementedError,
        ),
    ],
)
def test_build_nomograph(path, name, x, t, z, exception):
    if exception is None:
        build_nomo(name, TEST_PATH / path, x_col=x, t_col=t, y_col=z)
    else:
        pytest.raises(
            exception, build_nomo, name, TEST_PATH / path, x_col=x, t_col=t, y_col=z
        )


def construct_vol_nomo():
    path = TEST_PATH / "volume_nomo.csv"

    nomo = build_nomo(
        "VolumeNomograph",
        path,
        x_col="size_fraction",
        t_col="ddt_hr",
        y_col="capture_fraction",
    )
    return nomo


@pytest.fixture
def vol_nomo():
    return construct_vol_nomo()


def construct_vol_nomos():
    ls = []
    nomo = construct_vol_nomo()
    for ddt in set(nomo.nomo.t_data):
        ls.append((ddt, nomo))

    return ls


@pytest.fixture(params=construct_vol_nomos())
def vol_nomos(request):
    yield request.param


def construct_flow_nomo():
    path = TEST_PATH / "flow_nomo.csv"

    nomo = build_nomo(
        "FlowNomograph",
        path,
        x_col="intensity_inhr",
        t_col="tc_minutes",
        y_col="performance_frac",
    )
    return nomo


@pytest.fixture
def flow_nomo():
    return construct_flow_nomo()


def construct_flow_nomos():
    ls = []
    nomo = construct_flow_nomo()
    for ddt in set(nomo.nomo.t_data):
        ls.append((ddt, nomo))

    return ls


@pytest.fixture(params=construct_flow_nomos())
def flow_nomos(request):
    yield request.param


def test_volume_nomograph_matches_source_data(vol_nomos):
    ddt, nomo = vol_nomos
    res = nomo(size=nomo.nomo.x_data[nomo.nomo.t_data == ddt], ddt=ddt)
    assert all((nomo.nomo.y_data[nomo.nomo.t_data == ddt] - res) < 1e-6)


def test_flow_nomograph_matches_source_data(flow_nomos):
    tc, nomo = flow_nomos
    res = nomo(intensity=nomo.nomo.x_data[nomo.nomo.t_data == tc], tc=tc)
    assert all((nomo.nomo.y_data[nomo.nomo.t_data == tc] - res) < 1e-6)


def test_get_volume_nomograph(contexts):
    context = contexts["default"]

    met, _ = load_ref_data("met_table", context)
    assert met is not None
    paths = met["volume_nomograph"].unique()

    for path in paths:
        nomo = get_volume_nomograph(context=context, nomo_path=path)
        ddt = 3
        res = nomo(size=nomo.nomo.x_data[nomo.nomo.t_data == ddt], ddt=ddt)  # type: ignore
        assert all((nomo.nomo.y_data[nomo.nomo.t_data == ddt] - res) < 1e-6)  # type: ignore


def test_get_flow_nomograph(contexts):
    context = contexts["default"]

    met, _ = load_ref_data("met_table", context)
    assert met is not None
    paths = met["flow_nomograph"].unique()

    for path in paths:
        nomo = get_flow_nomograph(context=context, nomo_path=path)
        tc = 15
        res = nomo(intensity=nomo.nomo.x_data[nomo.nomo.t_data == tc], tc=tc)  # type: ignore
        assert all((nomo.nomo.y_data[nomo.nomo.t_data == tc] - res) < 1e-6)  # type: ignore


@pytest.mark.parametrize(
    "fxn, seek_value, bounds, exp, converges",
    [
        (lambda x: x * x, 2, (0, 5), 1.414, True),
        (lambda x: x * x, 0, (-5, 5.1), -5, False),
        (lambda x: x * x, 2, (-5, -1), -5, False),
        (lambda x: x * x, 0.5, None, 0.707, True),
        (lambda x: x * x * x, 2, (-5, 5), 1.259, True),
        (lambda x: x * x * x, -2, (-5, 5), -1.259, True),
        (lambda x: x * x * x, 0, (-5, 5), 0, True),
    ],
)
def test_bisection_search(fxn, seek_value, bounds, exp, converges):
    value, converged = bisection_search(fxn, seek_value=seek_value, bounds=bounds)

    assert converged == converges
    assert abs(exp - value) < 1e-3


@pytest.mark.parametrize(
    "size, ddt, performance, exp",
    [
        (1.5, 24, None, 0.962),
        (1, 24, None, 0.899),
        (1, 24.5, None, 0.897),
        (60, 24, None, 0.99),  # size 60 is out of bounds
        (2, 12, None, 0.99),
        (None, 24, 0.8, 0.668),
        (None, 500, 0.90, 3.338),
        ([1.5], [24], None, 0.967),
        (1.5, 24, None, 0.967),
        (1, 24, None, 0.899),
        (1, [24.5], None, 0.897),
        ([1, 1.5], [24.5, 24], None, [0.897, 0.967]),
        ([1, 60], [24.5, 24], None, [0.897, 0.99]),
        (None, [24, 24], [0.8, 0.9], [0.668, 1.01]),
        ([1, 1.5], [24.5, 24], None, [0.897, 0.967]),
    ],
)
def test_nomo_single_list_roundtrip(vol_nomo, size, ddt, performance, exp):
    result = vol_nomo(size=size, ddt=ddt, performance=performance)
    numpy.testing.assert_allclose(result, exp, atol=1e-2)


@pytest.mark.parametrize(
    "s, t, y, exception",
    [
        (1, None, None, ValueError),
        (None, [6, 12], [0.5, 0.5, 0.5], ValueError),
        (2.5, [6, 12], [0.5, 0.5, 0.5], ValueError),
    ],
)
def test_nomo_raises(vol_nomo, s, t, y, exception):
    pytest.raises(exception, vol_nomo, size=s, ddt=t, performance=y)


@pytest.mark.skipif(matplotlib is None, reason="optional matplotlib is not installed")
def test_nomo_plots(vol_nomo, flow_nomo):
    _ = vol_nomo.plot()
    _ = vol_nomo.surface_plot()

    _ = flow_nomo.plot()
    _ = flow_nomo.surface_plot()

    return

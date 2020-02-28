import numpy
import pytest

from nereid.src.tmnt_performance import tmnt
from nereid.src.tmnt_performance import tasks


@pytest.fixture
def eff_conc_mapping(tmnt_params):
    return tmnt.build_effluent_function_map(tmnt_params, "bmp", "pollutant")


@pytest.fixture
def pollutant_facilities_map(KTRL_curves):
    dct = {
        k: [c for c in v.columns if c not in ["xhat", "param"]]
        for k, v in KTRL_curves.items()
    }

    return dct


@pytest.fixture
def pollutant_units_map(tmnt_params):
    return tmnt_params.set_index("pollutant")["unit"].to_dict()


@pytest.mark.parametrize(
    "poc",
    [
        "Dissolved Copper",
        "Dissolved Zinc",
        "Fecal Coliform",
        "Total Copper",
        "Total Lead",
        "Total Nitrogen",
        "Total Phosphorus",
        "Total Suspended Solids",
        "Total Zinc",
    ],
)
def test_eff_concs(
    KTRL_curves, eff_conc_mapping, pollutant_facilities_map, pollutant_units_map, poc
):

    check_infs = KTRL_curves[poc]["xhat"]
    unit = pollutant_units_map[poc]

    for fac_type in pollutant_facilities_map[poc]:
        check_curve = KTRL_curves[poc][fac_type]
        eff_fxn = eff_conc_mapping[(fac_type, poc)]

        results = [eff_fxn(i, unit) for i in check_infs]
        numpy.testing.assert_allclose(results, check_curve)


@pytest.mark.parametrize(
    "inf_conc, inf_unit, kwargs, exp",
    [
        (0, "mg/l", {}, 1e-17),  # nearly zero
        (5, "mg/l", {"A": 2}, 2),  # A sets eff to constant
        (5, "mg/l", {"B": 2}, 5),  # eff can't be greater, so out == in
        (5, "mg/l", {"B": 0.5}, 2.5),  # eff is half of inf
        (5, "mg/l", {"B": 0.5, "unit": "lbs/cubic_feet"}, 2.5),  # units are handled
    ],
)
def test_eff_conc_varied_input(eff_conc_mapping, inf_conc, inf_unit, kwargs, exp):

    res = tmnt.effluent_conc(inf_conc, inf_unit, **kwargs)
    assert abs(exp - res) < 1e-3


@pytest.mark.parametrize("cxt_key", ["default"])
def test_tmnt_task(
    contexts, KTRL_curves, pollutant_facilities_map, pollutant_units_map, cxt_key
):
    context = contexts[cxt_key]
    eff_conc_mapping = tasks.effluent_function_map(context=context)

    for (fac_type, poc), eff_fxn in eff_conc_mapping.items():
        check_infs = KTRL_curves[poc]["xhat"]
        check_curve = KTRL_curves[poc][fac_type]
        unit = pollutant_units_map[poc]
        results = [eff_fxn(i, unit) for i in check_infs]
        numpy.testing.assert_allclose(results, check_curve)

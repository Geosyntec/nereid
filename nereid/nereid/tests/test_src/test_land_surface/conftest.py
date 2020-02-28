from copy import deepcopy
from io import StringIO

import pandas
import pytest

from nereid.core.utils import get_request_context


@pytest.fixture
def land_surface_data_contexts():

    cx1 = get_request_context()

    cx2 = deepcopy(cx1)
    cx2["project_reference_data"]["land_surface_table"].pop("joins")

    cx3 = deepcopy(cx2)
    cx3["project_reference_data"]["land_surface_table"].pop("expand_fields")

    cx4 = deepcopy(cx1)
    cx4["project_reference_data"]["land_surface_emc_table"]["file"] = r"¯\_(ツ)_/¯"

    cx5 = deepcopy(cx1)
    cx5["project_reference_data"]["land_surface_emc_table"].pop("parameters")

    keys = [
        "default",
        "land_surface_table_no_joins",
        "land_surface_table_no_joins_no_expanded_fields",
        "land_surface_emc_table_dne",
        "land_surface_emc_table_no_params",
    ]

    values = [cx1, cx2, cx3, cx4, cx5]

    return {k: v for k, v in zip(keys, values)}


@pytest.fixture
def known_land_surface_volume_loading_result():
    known = StringIO(
        """
   area_acres  imp_area_acres  perv_ro_depth_inches  imp_ro_depth_inches  perv_ro_coeff  imp_ro_coeff  imp_pct  perv_area_acres  imp_area_sqft  perv_area_sqft  imp_ro_depth_feet  perv_ro_depth_feet  imp_ro_volume_cuft  perv_ro_volume_cuft  runoff_volume_cuft  imp_eff_area_acres  perv_eff_area_acres  eff_area_acres
0           6             5.7                     4                    8            0.4           0.8    95.00              0.3       248292.0         13068.0               0.67                0.33            165528.0               4356.0            169884.0                4.56                 0.12            4.68
1           3             2.2                     4                    8            0.4           0.8    73.33              0.8        95832.0         34848.0               0.67                0.33             63888.0              11616.0             75504.0                1.76                 0.32            2.08
"""
    )
    return pandas.read_csv(known, sep="\s+")


@pytest.fixture
def known_land_surface_pollutant_loading_result():
    known = StringIO(
        """
   runoff_volume_cuft  FC_conc_mpn/100ml  TCu_conc_ug/l  TSS_conc_mg/l  TSS_load_lbs  TCu_load_lbs  FC_load_mpn
0                   2              76820            214            372      0.046446      0.000027   43506000.0
1                   3              54886            330             99      0.018541      0.000062   46626000.0
2                   0               6265            458            871      0.000000      0.000000          0.0
3                   2              82386             87            663      0.082779      0.000011   46658000.0
"""
    )
    return pandas.read_csv(known, sep="\s+")

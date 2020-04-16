from typing import Any, Dict, List, Union

from nereid.core.units import (
    conversion_factor_conc_to_load,
    conversion_factor_load_to_conc,
)


def make_wq_column_name(type: str, poc: str, unit: str) -> str:
    return "_".join([poc, type, unit.lower().replace("_", "")])


def init_wq_parameters(tablename: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Gets a list of parameter specifications from the config.yml and reference data files.

    See also config.yml::project_reference_data::land_surface_emc_table which defines what pollutants
    can enter the watershed.

    Returns
    -------
    parameters : list of dicts

    >>>[
        {
            'long_name': 'Total Suspended Solids',
            'short_name': 'TSS',
            'concentration_unit': 'mg/L',
            'load_unit': 'lbs',
            'load_col': 'TSS_load_lbs',
            'conc_col': 'TSS_conc_mg/l',
            'load_to_conc_factor': 16018.463373960149,
            'conc_to_load_factor': 6.24279605761446e-05
        },
        {
            'long_name': 'Total Copper',
            'short_name': 'TCu',
            'concentration_unit': 'ug/L',
            'load_unit': 'lbs',
            'load_col': 'TCu_load_lbs',
            'conc_col': 'TCu_conc_ug/l',
            'load_to_conc_factor': 16018463.373960149,
            'conc_to_load_factor': 6.242796057614458e-08
        },
            'long_name': 'Fecal Coliform',
            'short_name': 'FC',
            'concentration_unit': 'MPN/_100mL',
            'load_unit': 'mpn',
            'load_col': 'FC_load_mpn',
            'conc_col': 'FC_conc_mpn/100ml',
            'load_to_conc_factor': 0.00353146667214886,
            'conc_to_load_factor': 283.1684659199999
        }
    ]


    """

    parameters: List[Dict[str, Any]] = context.get("project_reference_data", {}).get(
        tablename, {}
    ).get("parameters", [])

    for param in parameters:

        conc_unit = param["concentration_unit"]
        load_unit = param["load_unit"]
        poc = param["short_name"]
        param["load_col"] = make_wq_column_name("load", poc, load_unit)
        param["conc_col"] = make_wq_column_name("conc", poc, conc_unit)

        param["load_to_conc_factor"] = conversion_factor_load_to_conc(
            load_unit=load_unit, conc_unit=conc_unit, vol_unit="cubic_feet"
        )

        param["conc_to_load_factor"] = conversion_factor_conc_to_load(
            conc_unit=conc_unit, load_unit=load_unit, vol_unit="cubic_feet"
        )

    return parameters

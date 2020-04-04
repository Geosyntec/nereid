from typing import Any, Dict, List, Union

from nereid.core.units import (
    conversion_factor_load_to_conc,
    conversion_factor_conc_to_load,
)


def make_wq_column_name(type: str, poc: str, unit: str) -> str:
    return "_".join([poc, type, unit.lower().replace("_", "")])


def init_wq_parameters(tablename: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:

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

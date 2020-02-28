from typing import List, Dict, Any

import pandas

from nereid.core.io import parse_configuration_logic
from nereid.core.units import update_unit_registry
from nereid.src.land_surface.loading import (
    detailed_loading_results,
    summary_loading_results,
)


@update_unit_registry
def land_surface_loading(
    land_surfaces: Dict[str, Any], details: bool, context: Dict[str, Any]
) -> Dict[str, List]:

    df = pandas.DataFrame(land_surfaces["land_surfaces"])
    df["imp_pct"] = 100 * df["imp_area_acres"] / df["area_acres"]

    df, messages = parse_configuration_logic(
        df=df,
        config_section="api_recognize",
        config_object="land_surfaces",
        context=context,
    )

    parameters = context["project_reference_data"]["land_surface_emc_table"].get(
        "parameters"
    )

    detailed_results = detailed_loading_results(df, parameters)
    summary_results = summary_loading_results(detailed_results, parameters)

    response = {}

    if len(messages) > 0:
        response["errors"] = messages

    response["summary"] = summary_results.fillna(0).to_dict(orient="records")

    if details:
        response["details"] = detailed_results.fillna(0).to_dict(orient="records")

    return response

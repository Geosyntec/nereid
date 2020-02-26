from typing import List, Dict, Any
from copy import deepcopy

from nereid.src.land_surface.loading import (
    build_land_surface_dataframe,
    detailed_loading_results,
    summary_loading_results,
)


def land_surface_loading(
    land_surfaces: Dict[str, Any], details: bool, context: Dict[str, Any]
) -> Dict[str, List]:

    land_surfaces_df, messages = build_land_surface_dataframe(
        land_surfaces["land_surfaces"], context
    )

    parameters = context["project_reference_data"]["land_surface_emc_table"].get(
        "parameters"
    )

    detailed_results = detailed_loading_results(land_surfaces_df, parameters)
    summary_results = summary_loading_results(detailed_results, parameters)

    response = {}

    if len(messages) > 0:
        response["errors"] = messages

    response["summary"] = summary_results.fillna(0).to_dict(orient="records")

    if details:
        response["details"] = detailed_results.fillna(0).to_dict(orient="records")

    return response

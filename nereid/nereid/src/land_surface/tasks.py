from typing import List, Dict, Any

import pandas

from nereid.src.land_surface.io import load_land_surface_data
from nereid.src.land_surface.loading import (
    detailed_land_surface_loading_results,
    summary_land_surface_loading_results,
)


def land_surface_loading(
    land_surfaces: Dict[str, Any], details: bool, context: Dict[str, Any]
) -> Dict[str, List]:

    emc_context = "str"

    req_join_key = (
        context.get("project_reference_data", {})
        .get("land_surface_table", {})
        .get("request_join_key")
    )

    parameters = context["project_reference_data"]["land_surface_emc_table"].get(
        "parameters", []
    )

    ref_table_df = load_land_surface_data(context)
    land_surfaces_list = land_surfaces["land_surfaces"]

    land_surfaces_df = pandas.DataFrame(land_surfaces_list).merge(
        ref_table_df,
        left_on="surface_key",  # this is not configurable, it's part of the api spec.
        right_on=req_join_key,
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    response = {}

    if not all(land_surfaces_df["_merge"] == "both"):
        message = "ERROR: unable match all requested 'surface_keys' to reference data."
        response["errors"] = [message]

    detailed_results = detailed_land_surface_loading_results(
        land_surfaces_df.drop(columns="_merge"), parameters
    )

    summary_results = summary_land_surface_loading_results(detailed_results, parameters)

    response["summary"] = summary_results.fillna(0).to_dict(orient="records")

    if details:
        response["details"] = detailed_results.fillna(0).to_dict(orient="records")

    return response

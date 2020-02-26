from typing import Dict, Any, List

from nereid.src.treatment_facility.constructors import build_treatment_facility_nodes


def initialize_treatment_facilities(
    treatment_facilities: Dict[str, List[Dict[str, Any]]], context: Dict[str, Any]
) -> Dict[str, Any]:

    treatment_facility_list = treatment_facilities["treatment_facilities"]

    treatment_facility_nodes, messages = build_treatment_facility_nodes(
        treatment_facility_list, context=context,
    )

    response = {}

    if len(messages) > 0:
        response["errors"] = messages

    response["treatment_facilities"] = treatment_facility_nodes

    return response

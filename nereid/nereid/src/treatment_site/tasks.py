from typing import Any, Dict, List

import pandas


def initialize_treatment_sites(
    treatment_sites: Dict[str, List[Dict[str, Any]]], context: Dict[str, Any]
) -> Dict[str, Any]:

    response: Dict[str, Any] = {"errors": []}

    sites = treatment_sites["treatment_sites"]

    # tmnt_map is connects the facility name with the treatment
    # key for the influent-> effluent concentration transformation
    # e.g. {"bioretention": "Biofiltration"}
    tmnt_map = {
        k: dct["tmnt_performance_facility_type"]
        for k, dct in (
            context["api_recognize"]
            .get("treatment_facility", {})
            .get("facility_type", {})
            .items()
        )
    }

    tmnt_sites = []

    if sites:

        _df = pandas.DataFrame(sites)

        remaider_data = []
        for node, g in _df.groupby("node_id"):
            remainder = 100 - g["area_pct"].sum()
            remaider_data.append(
                {
                    "node_id": node,
                    "area_pct": remainder,
                    "facility_type": "no_treatment",
                }
            )

        df = (
            _df.append(remaider_data)
            .fillna(0)
            .assign(
                tmnt_performance_facility_type=lambda df: df["facility_type"].replace(
                    tmnt_map
                )
            )
        )

        tmnt_sites = [
            {
                "node_id": key,
                "treatment_facilities": g.to_dict("records"),
                "node_type": "site_based",
            }
            for key, g in df.groupby("node_id")
        ]

    response["treatment_sites"] = tmnt_sites

    return response

from typing import Any, Dict, List, Optional, Union
from copy import deepcopy

import pandas

from nereid.core.io import parse_api_recognize


def build_treatment_facility_nodes(
    treatment_facility_list: List[Dict[str, Any]], context: Dict[str, Any]
) -> pandas.DataFrame:

    tmnt_facilities_df = pandas.DataFrame(treatment_facility_list)
    df = tmnt_facilities_df

    df, msg = parse_api_recognize(df, "treatment_facility", context)
    treatment_facility_list = [
        {k: v for k, v in m.items() if pandas.notnull(v)}
        for m in df.to_dict(orient="records")
    ]

    treatment_facility_list = list(
        map(construct_treatment_facility_node_context, treatment_facility_list)
    )

    return treatment_facility_list, msg


def construct_treatment_facility_node_context(
    node_context: Dict[str, Any]
) -> Dict[str, Any]:

    constructor_str = node_context.get("constructor", "nt_facility_constructor")
    fxn = getattr(TreatmentFacilityConstructor, constructor_str)

    result = fxn(**node_context)
    node_context.update(result)

    return deepcopy(node_context)


class TreatmentFacilityConstructor:
    @staticmethod
    def nt_facility_constructor(**kwargs: dict) -> Dict:
        return {}

    @staticmethod
    def retention_facility_constructor(
        *,
        total_volume_cuft: float,
        area_sqft: float,
        inf_rate_inhr: float,
        **kwargs: dict,
    ) -> Dict[str, float]:

        retention_volume_cuft = total_volume_cuft
        retention_depth_ft = retention_volume_cuft / area_sqft
        retention_ddt_hr = (retention_depth_ft * 12) / inf_rate_inhr

        result = dict(
            retention_volume_cuft=retention_volume_cuft,
            retention_depth_ft=retention_depth_ft,
            retention_ddt_hr=retention_ddt_hr,
        )

        return result

    @staticmethod
    def dry_well_facility_constructor(
        *, total_volume_cuft: float, treatment_rate_cfs: float, **kwargs: dict
    ) -> Dict[str, float]:

        retention_volume_cuft = total_volume_cuft
        retention_ddt_hr = total_volume_cuft / treatment_rate_cfs * 3600

        result = dict(
            retention_volume_cuft=retention_volume_cuft,
            retention_ddt_hr=retention_ddt_hr,
        )

        return result

    @staticmethod
    def bioinfiltration_facility_constructor(
        *,
        total_volume_cuft: float,
        retention_volume_cuft: float,
        area_sqft: float,
        media_filtration_rate_inhr: float,
        inf_rate_inhr: float,
        **kwargs: dict,
    ) -> Dict[str, float]:
        """This bmp has incidental infiltration and a raised underdrain.
        """

        retention_depth_ft = retention_volume_cuft / area_sqft
        retention_ddt_hr = (retention_depth_ft * 12) / inf_rate_inhr

        treatment_volume_cuft = total_volume_cuft - retention_volume_cuft
        treatment_depth_ft = treatment_volume_cuft / area_sqft
        treatment_ddt_hr = (treatment_depth_ft * 12) / media_filtration_rate_inhr

        result = dict(
            inf_rate_inhr=inf_rate_inhr,
            retention_volume_cuft=retention_volume_cuft,
            retention_depth_ft=retention_depth_ft,
            retention_ddt_hr=retention_ddt_hr,
            treatment_volume_cuft=treatment_volume_cuft,
            treatment_depth_ft=treatment_depth_ft,
            treatment_ddt_hr=treatment_ddt_hr,
        )

        return result

    @staticmethod
    def retention_and_treatment_facility_constructor(
        *,
        total_volume_cuft: float,
        retention_volume_cuft: float,
        area_sqft: float,
        total_drawdown_time_hr: float,
        inf_rate_inhr: float,
        **kwargs: dict,
    ) -> Dict[str, float]:

        retention_depth_ft = retention_volume_cuft / area_sqft
        retention_ddt_hr = retention_depth_ft * 12 / inf_rate_inhr

        treatment_volume_cuft = total_volume_cuft - retention_volume_cuft
        treatment_depth_ft = treatment_volume_cuft / area_sqft
        treatment_ddt_hr = total_drawdown_time_hr - retention_ddt_hr

        result = dict(
            inf_rate_inhr=inf_rate_inhr,
            retention_volume_cuft=retention_volume_cuft,
            retention_depth_ft=retention_depth_ft,
            retention_ddt_hr=retention_ddt_hr,
            treatment_volume_cuft=treatment_volume_cuft,
            treatment_depth_ft=treatment_depth_ft,
            treatment_ddt_hr=treatment_ddt_hr,
        )

        return result

    @staticmethod
    def treatment_facility_constructor(
        *,
        total_volume_cuft: float,
        area_sqft: float,
        media_filtration_rate_inhr: float,
        **kwargs: dict,
    ) -> Dict[str, float]:

        treatment_volume_cuft = total_volume_cuft
        treatment_depth_ft = treatment_volume_cuft / area_sqft
        treatment_ddt_hr = treatment_depth_ft * 12 / media_filtration_rate_inhr

        result = dict(
            treatment_volume_cuft=total_volume_cuft,
            treatment_depth_ft=treatment_depth_ft,
            treatment_ddt_hr=treatment_ddt_hr,
        )

        return result

    @staticmethod
    def flow_and_retention_facility_constructor(
        *,
        treatment_rate_cfs: float,
        area_sqft: float,
        depth_ft: float,
        inf_rate_inhr: float,
        **kwargs: dict,
    ) -> Dict[str, float]:

        retention_depth_ft = depth_ft
        retention_volume_cuft = area_sqft * retention_depth_ft
        retention_ddt_hr = retention_depth_ft * 12 / inf_rate_inhr

        result = dict(
            inf_rate_inhr=inf_rate_inhr,
            retention_volume_cuft=retention_volume_cuft,
            retention_depth_ft=retention_depth_ft,
            retention_ddt_hr=retention_ddt_hr,
            # this needs params for the flow based nomographs
        )

        return result

    @staticmethod
    def perm_pool_facility_constructor(
        *,
        pool_volume_cuft: float,
        pool_drawdown_time_hr: float,
        treatment_volume_cuft: float,
        treatment_drawdown_time_hr: float,
        winter_demand_cfs: float,
        summer_demand_cfs: float,
        **kwargs: dict,
    ) -> Dict[str, float]:

        retention_volume_cuft = pool_volume_cuft
        retention_ddt_hr = pool_drawdown_time_hr
        treatment_ddt_hr = treatment_drawdown_time_hr

        # consider winter demand

        result = dict(
            retention_volume_cuft=retention_volume_cuft,
            retention_ddt_hr=retention_ddt_hr,
            treatment_volume_cuft=treatment_volume_cuft,
            treatment_ddt_hr=treatment_ddt_hr,
        )

        return result

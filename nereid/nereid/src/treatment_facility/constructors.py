from copy import deepcopy
from typing import Any

import pandas

from nereid.core.utils import safe_divide


def build_treatment_facility_nodes(df: pandas.DataFrame) -> list[dict[str, Any]]:
    _treatment_facility_list: list[dict[str, Any]] = [
        {str(k): v for k, v in m.items() if pandas.notnull(v)}
        for m in df.to_dict(orient="records")
    ]

    treatment_facility_list: list[dict[str, Any]] = list(
        map(construct_treatment_facility_node_context, _treatment_facility_list)
    )

    return treatment_facility_list


def construct_treatment_facility_node_context(
    node_context: dict[str, Any],
) -> dict[str, Any]:
    n_cxt: dict[str, Any] = deepcopy(node_context)

    constructor_str = n_cxt.get("constructor") or "nt_facility_constructor"
    fxn = getattr(TreatmentFacilityConstructor, constructor_str)

    result = fxn(**n_cxt)
    n_cxt.update(result)

    return n_cxt


class TreatmentFacilityConstructor:
    @staticmethod
    def nt_facility_constructor(**kwargs: dict) -> dict:
        return {"captured_pct": 0, "retained_pct": 0, "treated_pct": 0}

    @staticmethod
    def simple_facility_constructor(**kwargs: dict) -> dict:
        return {"node_type": "simple_facility"}

    @staticmethod
    def retention_facility_constructor(
        *,
        total_volume_cuft: float,
        area_sqft: float,
        inf_rate_inhr: float,
        **kwargs: dict,
    ) -> dict[str, Any]:
        retention_volume_cuft = total_volume_cuft
        retention_depth_ft = safe_divide(retention_volume_cuft, area_sqft)
        retention_ddt_hr = safe_divide(retention_depth_ft * 12, inf_rate_inhr)

        result = {
            "retention_volume_cuft": retention_volume_cuft,
            "retention_depth_ft": retention_depth_ft,
            "retention_ddt_hr": retention_ddt_hr,
            "node_type": "volume_based_facility",
        }

        return result

    @staticmethod
    def dry_well_facility_constructor(
        *, total_volume_cuft: float, treatment_rate_cfs: float, **kwargs: dict
    ) -> dict[str, Any]:
        retention_volume_cuft = total_volume_cuft
        retention_ddt_hr = safe_divide(total_volume_cuft, treatment_rate_cfs * 3600)

        result = {
            "retention_volume_cuft": retention_volume_cuft,
            "retention_ddt_hr": retention_ddt_hr,
            # We need to override this because dry wells don't perform treatment
            # in either wet weather or dry weather, only retention/volume reduction.
            "ini_treatment_rate_cfs": treatment_rate_cfs,
            "treatment_rate_cfs": 0.0,
            "node_type": "volume_based_facility",
        }

        return result

    @staticmethod
    def dry_well_facility_flow_or_volume_constructor(
        *, total_volume_cuft: float, treatment_rate_cfs: float, **kwargs: dict
    ) -> dict[str, Any]:
        retention_volume_cuft = total_volume_cuft
        retention_ddt_hr = safe_divide(total_volume_cuft, treatment_rate_cfs * 3600)
        retention_rate = treatment_rate_cfs

        result = {
            "retention_volume_cuft": retention_volume_cuft,
            "retention_ddt_hr": retention_ddt_hr,
            # We need to override this because dry wells don't perform treatment
            # in either wet weather or dry weather, only retention/volume reduction.
            "ini_treatment_rate_cfs": treatment_rate_cfs,
            "retention_rate_cfs": retention_rate,
            "treatment_rate_cfs": 0.0,
            "node_type": "dry_well_facility",
        }

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
    ) -> dict[str, Any]:
        """This facility has incidental infiltration and a raised underdrain."""

        retention_depth_ft = safe_divide(retention_volume_cuft, area_sqft)
        retention_ddt_hr = safe_divide(retention_depth_ft * 12, inf_rate_inhr)

        treatment_volume_cuft = total_volume_cuft - retention_volume_cuft
        treatment_depth_ft = safe_divide(treatment_volume_cuft, area_sqft)
        treatment_ddt_hr = safe_divide(
            treatment_depth_ft * 12, media_filtration_rate_inhr
        )

        result = {
            "inf_rate_inhr": inf_rate_inhr,
            "retention_volume_cuft": retention_volume_cuft,
            "retention_depth_ft": retention_depth_ft,
            "retention_ddt_hr": retention_ddt_hr,
            "treatment_volume_cuft": treatment_volume_cuft,
            "treatment_depth_ft": treatment_depth_ft,
            "treatment_ddt_hr": treatment_ddt_hr,
            "node_type": "volume_based_facility",
        }

        return result

    @staticmethod
    def retention_and_treatment_facility_constructor(
        *,
        total_volume_cuft: float,
        retention_volume_cuft: float,
        area_sqft: float,
        treatment_drawdown_time_hr: float,
        inf_rate_inhr: float,
        **kwargs: dict,
    ) -> dict[str, Any]:
        retention_depth_ft = safe_divide(retention_volume_cuft, area_sqft)
        retention_ddt_hr = safe_divide(retention_depth_ft * 12, inf_rate_inhr)

        treatment_volume_cuft = total_volume_cuft - retention_volume_cuft
        treatment_depth_ft = safe_divide(treatment_volume_cuft, area_sqft)
        treatment_ddt_hr = treatment_drawdown_time_hr

        result = {
            "inf_rate_inhr": inf_rate_inhr,
            "retention_volume_cuft": retention_volume_cuft,
            "retention_depth_ft": retention_depth_ft,
            "retention_ddt_hr": retention_ddt_hr,
            "treatment_volume_cuft": treatment_volume_cuft,
            "treatment_depth_ft": treatment_depth_ft,
            "treatment_ddt_hr": treatment_ddt_hr,
            "node_type": "volume_based_facility",
        }

        return result

    @staticmethod
    def treatment_facility_constructor(
        *,
        total_volume_cuft: float,
        area_sqft: float,
        media_filtration_rate_inhr: float,
        **kwargs: dict,
    ) -> dict[str, Any]:
        treatment_volume_cuft = total_volume_cuft
        treatment_depth_ft = safe_divide(treatment_volume_cuft, area_sqft)
        treatment_ddt_hr = safe_divide(
            treatment_depth_ft * 12, media_filtration_rate_inhr
        )

        result = {
            "treatment_volume_cuft": total_volume_cuft,
            "treatment_depth_ft": treatment_depth_ft,
            "treatment_ddt_hr": treatment_ddt_hr,
            "node_type": "volume_based_facility",
        }

        return result

    @staticmethod
    def flow_and_retention_facility_constructor(
        *, area_sqft: float, depth_ft: float, inf_rate_inhr: float, **kwargs: dict
    ) -> dict[str, Any]:
        retention_depth_ft = depth_ft
        retention_volume_cuft = area_sqft * retention_depth_ft
        retention_ddt_hr = safe_divide(retention_depth_ft * 12, inf_rate_inhr)

        result = {
            "inf_rate_inhr": inf_rate_inhr,
            "retention_volume_cuft": retention_volume_cuft,
            "retention_depth_ft": retention_depth_ft,
            "retention_ddt_hr": retention_ddt_hr,
            "node_type": "flow_based_facility",
        }

        return result

    @staticmethod
    def flow_facility_constructor(**kwargs: dict) -> dict[str, Any]:
        result = {"node_type": "flow_based_facility"}

        return result

    @staticmethod
    def dry_weather_diversion_low_flow_facility_constructor(
        *,
        treatment_rate_cfs: float,
        design_capacity_cfs: float,
        months_operational: str,
        **kwargs: dict,
    ) -> dict[str, Any]:
        """These are diversions, so their 'treatment' eliminates volume from the system."""

        modeled_tmnt_rate = min(treatment_rate_cfs, design_capacity_cfs)

        summer_dry_weather_retention_rate_cfs = 0.0
        winter_dry_weather_retention_rate_cfs = 0.0

        if months_operational in ["summer", "both"]:
            summer_dry_weather_retention_rate_cfs = modeled_tmnt_rate

        if months_operational in ["winter", "both"]:
            winter_dry_weather_retention_rate_cfs = modeled_tmnt_rate

        result = {
            "ini_treatment_rate_cfs": treatment_rate_cfs,
            # diversions 'retain' their diverted volume, so we use it for the retention rate
            # and set the treatment rate to 0 since none of the discharge is treated.
            "summer_dry_weather_retention_rate_cfs": summer_dry_weather_retention_rate_cfs,
            "summer_dry_weather_treatment_rate_cfs": 0.0,
            "winter_dry_weather_retention_rate_cfs": winter_dry_weather_retention_rate_cfs,
            "winter_dry_weather_treatment_rate_cfs": 0.0,
            "node_type": "dry_weather_only_facility",  # this node type has no influence on wet weather.
        }

        return result

    @staticmethod
    def dry_weather_treatment_low_flow_facility_constructor(
        *,
        treatment_rate_cfs: float,
        design_capacity_cfs: float,
        months_operational: str,
        **kwargs: dict,
    ) -> dict[str, Any]:
        """These are treat and discharge facilities."""

        modeled_tmnt_rate = min(treatment_rate_cfs, design_capacity_cfs)

        summer_dry_weather_treatment_rate_cfs = 0.0
        winter_dry_weather_treatment_rate_cfs = 0.0

        if months_operational in ["summer", "both"]:
            summer_dry_weather_treatment_rate_cfs = modeled_tmnt_rate

        if months_operational in ["winter", "both"]:
            winter_dry_weather_treatment_rate_cfs = modeled_tmnt_rate

        result = {
            "ini_treatment_rate_cfs": treatment_rate_cfs,
            # treatment systems 'treat and discharge' their inflow volume, so we use it for the
            # teatment rate and set the retention rate to 0 since none of the discharge is retained.
            "summer_dry_weather_retention_rate_cfs": 0.0,
            "summer_dry_weather_treatment_rate_cfs": summer_dry_weather_treatment_rate_cfs,
            "winter_dry_weather_retention_rate_cfs": 0.0,
            "winter_dry_weather_treatment_rate_cfs": winter_dry_weather_treatment_rate_cfs,
            "node_type": "dry_weather_only_facility",  # this node type has no influence on wet weather.
        }

        return result

    @staticmethod
    def dw_and_low_flow_facility_constructor(
        *,
        treatment_rate_cfs: float,
        design_capacity_cfs: float,
        months_operational: str,
        **kwargs: dict,
    ) -> dict[str, Any]:
        """These are diversions, so their 'treatment' eliminates volume from the system."""

        modeled_tmnt_rate = min(treatment_rate_cfs, design_capacity_cfs)

        summer_dry_weather_retention_rate_cfs = 0.0
        winter_dry_weather_retention_rate_cfs = 0.0

        if months_operational in ["summer", "both"]:
            summer_dry_weather_retention_rate_cfs = modeled_tmnt_rate

        if months_operational in ["winter", "both"]:
            winter_dry_weather_retention_rate_cfs = modeled_tmnt_rate

        result = {
            "ini_treatment_rate_cfs": treatment_rate_cfs,
            # diversions 'retain' their diverted volume, so we use it for the retention rate
            # and set the treatment rate to 0 since none of the discharge is treated.
            "summer_dry_weather_retention_rate_cfs": summer_dry_weather_retention_rate_cfs,
            "summer_dry_weather_treatment_rate_cfs": 0.0,
            "winter_dry_weather_retention_rate_cfs": winter_dry_weather_retention_rate_cfs,
            "winter_dry_weather_treatment_rate_cfs": 0.0,
            "node_type": "diversion_facility",  # this node type has no influence on wet weather.
        }

        return result

    @staticmethod
    def cistern_facility_constructor(
        *,
        total_volume_cuft: float,
        winter_demand_cfs: float,
        summer_demand_cfs: float,
        winter_dry_weather_flow_cuft_psecond_inflow: float | None = None,
        summer_dry_weather_flow_cuft_psecond_inflow: float | None = None,
        **kwargs: dict,
    ) -> dict[str, Any]:
        winter_dry_weather_flow_cuft_psecond_inflow = (
            winter_dry_weather_flow_cuft_psecond_inflow or 0.0
        )
        summer_dry_weather_flow_cuft_psecond_inflow = (
            summer_dry_weather_flow_cuft_psecond_inflow or 0.0
        )

        winter_demand_cfs_user = winter_demand_cfs
        summer_demand_cfs_user = summer_demand_cfs

        winter_demand_cfs = max(
            0, winter_demand_cfs_user - winter_dry_weather_flow_cuft_psecond_inflow
        )

        summer_demand_cfs = max(
            0, summer_demand_cfs_user - summer_dry_weather_flow_cuft_psecond_inflow
        )

        winter_demand_cfhr = winter_demand_cfs * 3600
        retention_ddt_hr = safe_divide(total_volume_cuft, winter_demand_cfhr)
        retention_volume_cuft = total_volume_cuft if retention_ddt_hr > 0 else 0

        result = {
            "winter_demand_cfs": winter_demand_cfs,
            "summer_demand_cfs": summer_demand_cfs,
            "winter_demand_cfs_user": winter_demand_cfs_user,
            "summer_demand_cfs_user": summer_demand_cfs_user,
            "retention_volume_cuft": retention_volume_cuft,
            "retention_ddt_hr": retention_ddt_hr,
            "summer_dry_weather_retention_rate_cfs": summer_demand_cfs,
            "summer_dry_weather_treatment_rate_cfs": 0.0,
            "winter_dry_weather_retention_rate_cfs": winter_demand_cfs,
            "winter_dry_weather_treatment_rate_cfs": 0.0,
            "node_type": "volume_based_cistern_facility",
        }

        return result

    @staticmethod
    def perm_pool_facility_constructor(
        *,
        pool_volume_cuft: float,
        treatment_volume_cuft: float,
        **kwargs: dict,
    ) -> dict[str, Any]:
        # TODO: wetponds are lined, thus they do not perform retention
        # during wet weather. The perm pool volume is treated during the hrt and
        # discharged. Therefore a future release will need to handle two nomograph
        # traversals with the same fate; in this case both traversals yield
        # % treated + % treated, rather than the typical % retained + % treated.
        # reference issue: https://github.com/Geosyntec/nereid/issues/99

        # Done 2022-09-30: decision to model them as a single combined compartment
        # with the HRT as the drawdown time. Fixed to 48hrs

        result = {
            # pool vol and tmnt vol have same fate so we sum them
            "treatment_volume_cuft": treatment_volume_cuft + pool_volume_cuft,
            "treatment_ddt_hr": 48,  # set to 48 hr, the time needed to refresh the treatment capacity
            "node_type": "volume_based_facility",
        }

        return result

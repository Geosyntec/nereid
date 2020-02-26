from typing import Any, Dict, List, Optional, Union

from fastapi import Depends
from pydantic import BaseModel, Field, validator

from nereid.api.api_v1.models.response_models import JSONAPIResponse
from nereid.api.api_v1.models.utils import validate_models_with_discriminator


class FacilityBase(BaseModel):
    node_id: str
    facility_type: str
    ref_data_key: str
    design_storm_depth_inches: float = Field(..., gt=0)

    class Config:
        extra = "allow"


class NTFacility(FacilityBase):
    constructor: str = "nt_facility_constructor"


class FlowFacility(FacilityBase):
    treatment_rate_cfs: float
    tributary_area_tc_min: float
    constructor: str = "nt_facility_constructor"


# class LowFlowFacility(FlowFacility): # check with Aaron if this needs tc too.
#     design_capacity_cfs: float
#     months_operational: str = DEFAULT_MONTHS_OPERATIONAL


class LowFlowFacility(FacilityBase):
    treatment_rate_cfs: float
    design_capacity_cfs: float
    months_operational: str
    constructor: str = "nt_facility_constructor"


class OnlineFaciltyBase(FacilityBase):
    is_online: bool = True
    tributary_area_tc_min: float = 5.0
    offline_diversion_rate_cfs: Optional[float] = None

    @validator("offline_diversion_rate_cfs", pre=True, always=True)
    def required_if_offline(cls, v, values):
        if not values.get("is_online") and v is None:
            _node_id = values["node_id"]
            raise ValueError(
                f"'offline_diversion_rate_cfs' is required if facility [{_node_id}] is offline."
            )
        return v


class RetentionFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    area_sqft: float
    inf_rate_inhr: float
    constructor: str = "retention_facility_constructor"


class DryWellFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    treatment_rate_cfs: float
    constructor: str = "dry_well_facility_constructor"


class BioInfFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    retention_volume_cuft: float
    area_sqft: float
    media_filtration_rate_inhr: float
    hsg: str
    constructor: str = "bioinfiltration_facility_constructor"


class RetAndTmntFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    retention_volume_cuft: float
    area_sqft: float
    total_drawdown_time_hr: float
    hsg: str
    constructor: str = "retention_and_treatment_facility_constructor"


class TmntFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    area_sqft: float
    media_filtration_rate_inhr: float
    constructor: str = "treatment_facility_constructor"


class FlowAndRetFacility(OnlineFaciltyBase):
    treatment_rate_cfs: float
    area_sqft: float
    depth_ft: float
    hsg: str
    constructor: str = "flow_and_retention_facility_constructor"


class CisternFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    winter_demand_cfs: float
    summer_demand_cfs: float
    constructor: str = "nt_facility_constructor"


class PermPoolFacility(OnlineFaciltyBase):
    pool_volume_cuft: float
    pool_drawdown_time_hr: float
    treatment_volume_cuft: float
    treatment_drawdown_time_hr: float
    winter_demand_cfs: float
    summer_demand_cfs: float
    constructor: str = "perm_pool_facility_constructor"


STRUCTURAL_FACILITY_TYPE = Union[  # Used only for the openapi spec, not for validation
    PermPoolFacility,
    RetAndTmntFacility,
    BioInfFacility,
    FlowAndRetFacility,
    RetentionFacility,
    TmntFacility,
    CisternFacility,
    DryWellFacility,
    LowFlowFacility,
    FlowFacility,
    NTFacility,
]

TREATMENT_FACILITY_MODELS = [
    PermPoolFacility,
    RetAndTmntFacility,
    BioInfFacility,
    FlowAndRetFacility,
    RetentionFacility,
    TmntFacility,
    CisternFacility,
    DryWellFacility,
    LowFlowFacility,
    FlowFacility,
    NTFacility,
]


class TreatmentFacilities(BaseModel):
    treatment_facilities: List[STRUCTURAL_FACILITY_TYPE]


class TreatmentFacilitiesResponse(JSONAPIResponse):
    data: Optional[TreatmentFacilities] = None


def validate_treatment_facility_models(
    unvalidated_data: List[Dict[str, Any]], context: Dict[str, Any]
) -> List[Any]:

    mapping = context["api_recognize"]["treatment_facility"]["facility_type"]
    model_map = {k: globals().get(v.get("validator")) for k, v in mapping.items()}
    fallback_map = {
        k: globals().get(v.get("validation_fallback")) for k, v in mapping.items()
    }

    valid_models = validate_models_with_discriminator(
        unvalidated_data=unvalidated_data,
        discriminator="facility_type",
        model_mapping=model_map,
        fallback_mapping=fallback_map,
    )

    return valid_models

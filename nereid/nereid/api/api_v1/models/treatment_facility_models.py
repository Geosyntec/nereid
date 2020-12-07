from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator

from nereid.api.api_v1.models.response_models import JSONAPIResponse
from nereid.core.utils import validate_with_discriminator


class FacilityBase(BaseModel):
    node_id: str
    facility_type: str
    ref_data_key: str
    design_storm_depth_inches: float = Field(..., gt=0)
    eliminate_all_dry_weather_flow_override: bool = False


class NTFacility(FacilityBase):
    _constructor: str = "nt_facility_constructor"

    class Config:
        extra = "allow"


class FlowFacility(FacilityBase):
    treatment_rate_cfs: float
    tributary_area_tc_min: float = Field(5.0, le=60)
    _constructor: str = "flow_facility_constructor"


class LowFlowFacility(FacilityBase):
    treatment_rate_cfs: Optional[float] = None
    design_capacity_cfs: Optional[float] = None
    tributary_area_tc_min: float = Field(5.0, le=60)
    months_operational: str = Field("both", regex="summer$|winter$|both$")
    _constructor: str = "dw_and_low_flow_facility_constructor"

    @root_validator(pre=True)
    def one_or_both(cls, values):
        _fields = ["treatment_rate_cfs", "design_capacity_cfs"]
        if all([values.get(v) is None for v in _fields]):
            raise ValueError(
                "One or both of 'treatment_rate_cfs' and 'design_capacity_cfs' are required."
            )
        else:
            values[_fields[0]] = values.get(_fields[0], values.get(_fields[1]))
            values[_fields[1]] = values.get(_fields[1], values.get(_fields[0]))
        return values


class OnlineFaciltyBase(FacilityBase):
    is_online: bool = True
    tributary_area_tc_min: float = Field(5.0, le=60)
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
    _constructor: str = "retention_facility_constructor"


class DryWellFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    treatment_rate_cfs: float
    _constructor: str = "dry_well_facility_constructor"


class BioInfFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    retention_volume_cuft: float
    area_sqft: float
    media_filtration_rate_inhr: float
    hsg: str
    _constructor: str = "bioinfiltration_facility_constructor"


class RetAndTmntFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    retention_volume_cuft: float
    area_sqft: float
    treatment_drawdown_time_hr: float
    hsg: str
    _constructor: str = "retention_and_treatment_facility_constructor"


class TmntFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    area_sqft: float
    media_filtration_rate_inhr: float
    _constructor: str = "treatment_facility_constructor"


class FlowAndRetFacility(OnlineFaciltyBase):
    treatment_rate_cfs: float
    area_sqft: float
    depth_ft: float
    hsg: str
    _constructor: str = "flow_and_retention_facility_constructor"


class CisternFacility(OnlineFaciltyBase):
    total_volume_cuft: float
    winter_demand_cfs: float
    summer_demand_cfs: float
    _constructor: str = "cistern_facility_constructor"


class PermPoolFacility(OnlineFaciltyBase):
    pool_volume_cuft: float
    pool_drawdown_time_hr: float
    treatment_volume_cuft: float
    treatment_drawdown_time_hr: float
    winter_demand_cfs: float
    summer_demand_cfs: float
    _constructor: str = "perm_pool_facility_constructor"


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
    treatment_facilities: List[Dict[str, Any]]
    errors: Optional[List[str]] = None


class TreatmentFacilitiesStrict(BaseModel):
    treatment_facilities: List[STRUCTURAL_FACILITY_TYPE]
    errors: Optional[List[str]] = None


class TreatmentFacilitiesResponse(JSONAPIResponse):
    data: Optional[TreatmentFacilities] = None


def validate_treatment_facility_models(
    unvalidated_data: List[Dict[str, Any]], context: Dict[str, Any]
) -> List[Dict[str, Any]]:

    mapping = context["api_recognize"]["treatment_facility"]["facility_type"]
    model_map_str = {k: v.get("validator") for k, v in mapping.items()}
    fallback_map_str = {k: v.get("validation_fallback") for k, v in mapping.items()}
    tmnt_performance_map_str = {
        k: v.get("tmnt_performance_facility_type") for k, v in mapping.items()
    }

    model_map = {k: globals().get(v) for k, v in model_map_str.items()}
    fallback_map = {k: globals().get(v) for k, v in fallback_map_str.items()}

    valid_models = []

    for dct in unvalidated_data:
        facility_type = dct["facility_type"]
        model = validate_with_discriminator(
            unvalidated_data=dct,
            discriminator="facility_type",
            model_mapping=model_map,
            fallback_mapping=fallback_map,
        )

        valid_dct = model.dict()
        valid_dct["constructor"] = getattr(
            model, "_constructor", "nt_facility_constructor"
        )
        valid_dct["valid_model"] = model.schema()["title"]
        valid_dct["validator"] = model_map_str.get(facility_type)
        valid_dct["validation_fallback"] = fallback_map_str.get(facility_type)
        valid_dct["tmnt_performance_facility_type"] = tmnt_performance_map_str.get(
            facility_type
        )

        valid_models.append(valid_dct)

    return valid_models

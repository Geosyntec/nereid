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


class DryWeatherDiversionLowFlowFacility(LowFlowFacility):
    _constructor: str = "dry_weather_diversion_low_flow_facility_constructor"


class DryWeatherTreatmentLowFlowFacility(LowFlowFacility):
    _constructor: str = "dry_weather_treatment_low_flow_facility_constructor"


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
    DryWeatherTreatmentLowFlowFacility,
    DryWeatherDiversionLowFlowFacility,
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
    DryWeatherTreatmentLowFlowFacility,
    DryWeatherDiversionLowFlowFacility,
    LowFlowFacility,
    FlowFacility,
    NTFacility,
]

EXAMPLE_TREATMENT_FACILITIES = {
    "treatment_facilities": [
        {
            "node_id": "1",
            "facility_type": "no_treatment",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 1.45,
        },
        {
            "node_id": "1",
            "facility_type": "dry_extended_detention",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 1.05,
            "is_online": True,
            "tributary_area_tc_min": 30,
            "total_volume_cuft": 5500,
            "retention_volume_cuft": 4400,
            "area_sqft": 1600,
            "treatment_drawdown_time_hr": 24 * 3,
            "hsg": "d",
            "offline_diversion_rate_cfs": 2.9,
            "eliminate_all_dry_weather_flow_override": False,
        },
        {
            "node_id": "1",
            "facility_type": "infiltration",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 0.88,
            "is_online": True,
            "tributary_area_tc_min": 25,
            "total_volume_cuft": 6200,
            "area_sqft": 2000,
            "inf_rate_inhr": 3.5,
            "offline_diversion_rate_cfs": 5,
            "eliminate_all_dry_weather_flow_override": False,
        },
        {
            "node_id": "1",
            "facility_type": "bioretention",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 0.85,
            "is_online": True,
            "tributary_area_tc_min": 15,
            "total_volume_cuft": 5800,
            "retention_volume_cuft": 3500,
            "area_sqft": 1300,
            "media_filtration_rate_inhr": 12,
            "hsg": "a",
            "offline_diversion_rate_cfs": 6,
            "eliminate_all_dry_weather_flow_override": False,
        },
        {
            "node_id": "1",
            "facility_type": "biofiltration",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 0.95,
            "is_online": True,
            "tributary_area_tc_min": 40,
            "total_volume_cuft": 4400,
            "area_sqft": 1200,
            "media_filtration_rate_inhr": 15,
            "offline_diversion_rate_cfs": 6,
            "eliminate_all_dry_weather_flow_override": False,
        },
        {
            "node_id": "1",
            "facility_type": "wet_detention",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 0.78,
            "is_online": True,
            "tributary_area_tc_min": 45,
            "pool_volume_cuft": 5550,
            "pool_drawdown_time_hr": 24 * 30,
            "treatment_volume_cuft": 2500,
            "treatment_drawdown_time_hr": 12,
            "winter_demand_cfs": 0.05,
            "summer_demand_cfs": 0.88,
            "offline_diversion_rate_cfs": 4,
            "eliminate_all_dry_weather_flow_override": False,
        },
        {
            "node_id": "1",
            "facility_type": "sand_filter",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 0.78,
            "total_volume_cuft": 5000,
            "area_sqft": 2700,
            "media_filtration_rate_inhr": 12,
            "is_online": True,
            "offline_diversion_rate_cfs": 2.1,
            "eliminate_all_dry_weather_flow_override": False,
            "tributary_area_tc_min": 20,
        },
        {
            "node_id": "1",
            "facility_type": "swale",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 1.0,
            "treatment_rate_cfs": 0.55,
            "area_sqft": 15600,
            "depth_ft": 1.5,
            "hsg": "b",
            "is_online": True,
            "offline_diversion_rate_cfs": 0.5,
            "eliminate_all_dry_weather_flow_override": False,
            "tributary_area_tc_min": 25,
        },
        {
            "node_id": "1",
            "facility_type": "hydrodynamic_separator",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 1.12,
            "treatment_rate_cfs": 0.2,
            "eliminate_all_dry_weather_flow_override": False,
            "tributary_area_tc_min": 50,
            "is_online": True,
        },
        {
            "node_id": "1",
            "facility_type": "dry_well",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 0.85,
            "total_volume_cuft": 800,
            "treatment_rate_cfs": 0.5,
            "is_online": True,
            "offline_diversion_rate_cfs": 0.5,
            "eliminate_all_dry_weather_flow_override": False,
            "tributary_area_tc_min": 5,
        },
        {
            "node_id": "1",
            "facility_type": "cistern",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 1.3,
            "total_volume_cuft": 5500,
            "winter_demand_cfs": 0.05,
            "summer_demand_cfs": 0.25,
            "is_online": True,
            "offline_diversion_rate_cfs": 0.5,
            "eliminate_all_dry_weather_flow_override": False,
            "tributary_area_tc_min": 55,
        },
        {
            "node_id": "1",
            "facility_type": "dry_weather_diversion",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 1.43,
            "design_capacity_cfs": 3.5,
            "months_operational": "summer",
            "tributary_area_tc_min": 30,
            "treatment_rate_cfs": 2.92,
            "eliminate_all_dry_weather_flow_override": False,
            "is_online": True,
        },
        {
            "node_id": "1",
            "facility_type": "dry_weather_treatment",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 1.32,
            "design_capacity_cfs": 6.1,
            "months_operational": "summer",
            "tributary_area_tc_min": 10,
            "treatment_rate_cfs": 3.5,
            "eliminate_all_dry_weather_flow_override": False,
            "is_online": True,
        },
        {
            "node_id": "1",
            "facility_type": "low_flow_facility",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 0.91,
            "design_capacity_cfs": 5.1,
            "months_operational": "summer",
            "tributary_area_tc_min": 20,
            "treatment_rate_cfs": 5.0,
            "eliminate_all_dry_weather_flow_override": False,
            "is_online": True,
        },
    ]
}


class TreatmentFacilities(BaseModel):
    treatment_facilities: List[Dict[str, Any]]
    errors: Optional[List[str]] = None

    class Config:
        schema_extra = {"example": EXAMPLE_TREATMENT_FACILITIES}


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

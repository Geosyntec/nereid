from typing import Annotated, Any, TypeAlias

from pydantic import BaseModel, Field, field_validator, model_validator

from nereid.core.utils import validate_with_discriminator
from nereid.models.node import Node
from nereid.models.response_models import JSONAPIResponse


class _Base(Node):
    facility_type: str


FLOAT_NON_ZERO = Annotated[float, Field(..., gt=0.0)]
FLOAT_GE_ZERO = Annotated[float, Field(0.0, ge=0.0)]


class SimpleFacilityBase(_Base):
    captured_pct: float = 0.0
    retained_pct: float | None = None
    _constructor: str = "simple_facility_constructor"

    model_config = {"extra": "allow"}

    @field_validator("captured_pct", mode="before")
    @classmethod
    def captured_default(cls, v):
        if v is None:
            v = 0.0
        else:
            v = float(v)
            assert 0.0 <= v <= 100.0, (
                "Error: This value must be a number between 0.0 - 100.0."
            )
        return v


class SimpleFacility(SimpleFacilityBase):
    @model_validator(mode="before")
    @classmethod
    def retained_default(cls, data):
        if isinstance(data, dict):  # pragma: no branch
            v = data.get("retained_pct")
            if v is None:
                data["retained_pct"] = 0.0
            else:
                v = float(v)
                assert 0.0 <= v <= 100.0, "retained percent must be between 0.0-100.0"
                assert v <= float(data.get("captured_pct", 0.0)), (
                    "retained percent must be less than or equal to captured percent"
                )
        return data


class SimpleTmntFacility(SimpleFacilityBase):
    @model_validator(mode="before")
    @classmethod
    def retained_default(cls, data):
        if isinstance(data, dict):  # pragma: no branch
            v = data.get("retained_pct")
            if v is not None:
                v = float(v)
                assert abs(v) <= 1e-6, "retained percent must be zero."
            data["retained_pct"] = 0.0
        return data


class SimpleRetFacility(SimpleFacilityBase):
    @model_validator(mode="before")
    @classmethod
    def retained_default(cls, data):
        if isinstance(data, dict):  # pragma: no branch
            v = data.get("retained_pct")
            if v is not None:
                v = float(v)
                assert v == data.get("captured_pct"), (
                    "retained must equal captured for retention BMPs"
                )
            data["retained_pct"] = float(data.get("captured_pct", 0.0))
        return data


class FacilityBase(_Base):
    ref_data_key: str = Field(
        ...,
        description=(
            "This attribute is used to determine which nomographs "
            "to reference in order to compute the long-term volume "
            "capture performance of the facility."
        ),
    )
    design_storm_depth_inches: float = Field(
        ..., gt=0, description="85th percentile design storm depth in inches"
    )
    eliminate_all_dry_weather_flow_override: bool = Field(
        False,
        description=(
            "Whether to override the dry weather flow capture calculation "
            "and set the performance to 'fully eliminates all dry weather flow'. "
            "(default=False)"
        ),
    )


class NTFacility(_Base):
    _constructor: str = "nt_facility_constructor"

    model_config = {"extra": "allow"}


class FlowFacility(FacilityBase):
    treatment_rate_cfs: float
    tributary_area_tc_min: float = Field(5.0, le=60)
    _constructor: str = "flow_facility_constructor"


class LowFlowFacility(FacilityBase):
    treatment_rate_cfs: float | None = None
    design_capacity_cfs: float | None = None
    tributary_area_tc_min: float = Field(5.0, le=60)
    months_operational: str = Field("both", pattern="summer$|winter$|both$")

    _constructor: str = "dw_and_low_flow_facility_constructor"

    @model_validator(mode="before")
    @classmethod
    def one_or_both(cls, values):
        if not isinstance(values, dict):
            return values  # pragma: no cover
        _fields = ["treatment_rate_cfs", "design_capacity_cfs"]
        if all(values.get(v) is None for v in _fields):
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


class RetentionFacility(FacilityBase):
    total_volume_cuft: FLOAT_NON_ZERO
    area_sqft: FLOAT_NON_ZERO
    inf_rate_inhr: FLOAT_NON_ZERO
    _constructor: str = "retention_facility_constructor"


class RetentionFacilityHSG(FacilityBase):
    total_volume_cuft: FLOAT_NON_ZERO
    area_sqft: FLOAT_NON_ZERO
    hsg: str
    _constructor: str = "retention_facility_constructor"


class DryWellFacility(FacilityBase):
    total_volume_cuft: FLOAT_NON_ZERO
    treatment_rate_cfs: FLOAT_NON_ZERO
    _constructor: str = "dry_well_facility_constructor"


class DryWellFacilityFlowOrVolume(DryWellFacility, FlowFacility):
    _constructor: str = "dry_well_facility_flow_or_volume_constructor"


class BioInfFacility(FacilityBase):
    total_volume_cuft: FLOAT_NON_ZERO
    retention_volume_cuft: FLOAT_GE_ZERO
    area_sqft: FLOAT_NON_ZERO
    media_filtration_rate_inhr: FLOAT_NON_ZERO
    hsg: str
    _constructor: str = "bioinfiltration_facility_constructor"


class RetAndTmntFacility(FacilityBase):
    total_volume_cuft: FLOAT_NON_ZERO
    retention_volume_cuft: FLOAT_GE_ZERO
    area_sqft: FLOAT_NON_ZERO
    treatment_drawdown_time_hr: FLOAT_NON_ZERO
    hsg: str
    _constructor: str = "retention_and_treatment_facility_constructor"


class TmntFacility(FacilityBase):
    total_volume_cuft: FLOAT_NON_ZERO
    area_sqft: FLOAT_NON_ZERO
    media_filtration_rate_inhr: FLOAT_NON_ZERO
    _constructor: str = "treatment_facility_constructor"


class TmntFacilityWithRetentionOverride(TmntFacility):
    # min retention pct is meant to estimate incidental retention performance of
    # vegetated tmnt-only BMPs.
    minimum_retention_pct_override: float = Field(
        0,
        le=100,
        description=(
            "This parameter can be used to set the long term retention "
            "performance to a fixed percentage of the long-term inflow volume. "
            "This is useful for taking retention credit for ET in a "
            "vegetated system that is lined. "
        ),
    )


class FlowAndRetFacility(FlowFacility, FacilityBase):
    area_sqft: FLOAT_NON_ZERO

    # TODO: if hsg = lined then users may enter zero for the depth.
    depth_ft: FLOAT_NON_ZERO
    hsg: str
    _constructor: str = "flow_and_retention_facility_constructor"


class CisternFacility(FacilityBase):
    total_volume_cuft: FLOAT_NON_ZERO
    winter_demand_cfs: FLOAT_NON_ZERO
    summer_demand_cfs: float = 0.0
    _constructor: str = "cistern_facility_constructor"


class PermPoolFacility(FacilityBase):
    pool_volume_cuft: float = 0.0
    treatment_volume_cuft: float = 0.0
    _constructor: str = "perm_pool_facility_constructor"

    @model_validator(mode="before")
    @classmethod
    def non_zero_volume(cls, data):
        if isinstance(data, dict):  # pragma: no branch
            pool = data.get("pool_volume_cuft") or 0.0
            tmnt = data.get("treatment_volume_cuft") or 0.0
            assert (pool + tmnt) > 0.0, "facility must have pool or treatment volume."
        return data


STRUCTURAL_FACILITY_TYPE: TypeAlias = (  # Used only for the openapi spec, not for validation
    PermPoolFacility
    | RetAndTmntFacility
    | BioInfFacility
    | FlowAndRetFacility
    | RetentionFacility
    | RetentionFacilityHSG
    | TmntFacility
    | TmntFacilityWithRetentionOverride
    | CisternFacility
    | DryWellFacility
    | DryWellFacilityFlowOrVolume
    | DryWeatherTreatmentLowFlowFacility
    | DryWeatherDiversionLowFlowFacility
    | LowFlowFacility
    | FlowFacility
    | SimpleFacility
    | SimpleTmntFacility
    | SimpleRetFacility
    | NTFacility
)


TREATMENT_FACILITY_MODELS = [
    PermPoolFacility,
    RetAndTmntFacility,
    BioInfFacility,
    FlowAndRetFacility,
    RetentionFacility,
    RetentionFacilityHSG,
    TmntFacility,
    TmntFacilityWithRetentionOverride,
    CisternFacility,
    DryWellFacility,
    DryWellFacilityFlowOrVolume,
    DryWeatherTreatmentLowFlowFacility,
    DryWeatherDiversionLowFlowFacility,
    LowFlowFacility,
    FlowFacility,
    SimpleFacility,
    SimpleTmntFacility,
    SimpleRetFacility,
    NTFacility,
]

EXAMPLE_TREATMENT_FACILITIES: dict = {
    "treatment_facilities": [
        {
            "node_id": "1",
            "facility_type": "no_treatment",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 1.45,
        },
        {
            "node_id": 2,
            "facility_type": "bioretention_simple",
            "captured_pct": 80,
            "retained_pct": 20,
        },
        {
            "node_id": 2,
            "facility_type": "hydrodynamic_separator_simple",
            "captured_pct": 80,
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
    treatment_facilities: list[dict[str, Any] | STRUCTURAL_FACILITY_TYPE]
    errors: list[str] | None = None
    model_config = {"json_schema_extra": {"example": EXAMPLE_TREATMENT_FACILITIES}}


class TreatmentFacilitiesResponse(JSONAPIResponse):
    data: TreatmentFacilities | None = None


def validate_treatment_facility_models(
    unvalidated_data: list[dict[str, Any]], context: dict[str, Any]
) -> list[dict[str, Any]]:
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

        valid_dct = model.model_dump()
        valid_dct["constructor"] = getattr(
            model, "_constructor", "nt_facility_constructor"
        )
        valid_dct["valid_model"] = model.model_json_schema()["title"]
        valid_dct["validator"] = model_map_str.get(facility_type)
        valid_dct["validation_fallback"] = fallback_map_str.get(facility_type)
        valid_dct["tmnt_performance_facility_type"] = tmnt_performance_map_str.get(
            facility_type
        )

        valid_models.append(valid_dct)

    return valid_models

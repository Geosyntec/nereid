from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from nereid._compat import PYDANTIC_V2
from nereid.api.api_v1.models.land_surface_models import LandSurface
from nereid.api.api_v1.models.network_models import Graph
from nereid.api.api_v1.models.response_models import JSONAPIResponse
from nereid.api.api_v1.models.results_models import PreviousResult, Result
from nereid.api.api_v1.models.treatment_facility_models import STRUCTURAL_FACILITY_TYPE
from nereid.api.api_v1.models.treatment_site_models import TreatmentSite

EXAMPLE_WATERSHED = {
    "graph": {
        "directed": True,
        "multigraph": False,
        "graph": {},
        "nodes": [
            {"metadata": {}, "id": "0"},
            {"metadata": {}, "id": "1"},
            {"metadata": {}, "id": "2"},
            {"metadata": {}, "id": "3"},
            {"metadata": {}, "id": "4"},
            {"metadata": {}, "id": "5"},
            {"metadata": {}, "id": "6"},
        ],
        "edges": [
            {"metadata": {}, "source": "1", "target": "0"},
            {"metadata": {}, "source": "2", "target": "1"},
            {"metadata": {}, "source": "3", "target": "2"},
            {"metadata": {}, "source": "4", "target": "2"},
            {"metadata": {}, "source": "5", "target": "2"},
            {"metadata": {}, "source": "6", "target": "1"},
        ],
    },
    "treatment_facilities": [
        {
            "node_id": "0",
            "facility_type": "sand_filter",
            "ref_data_key": "10101200",
            "design_storm_depth_inches": 0.85,
            "total_volume_cuft": 335,
            "area_sqft": 1532,
            "media_filtration_rate_inhr": 22.5,
            "constructor": "treatment_facility_constructor",
            "tributary_area_tc_min": 30,
            "is_online": True,
        },
        {
            "node_id": "2",
            "facility_type": "bioretention",
            "ref_data_key": "10101000",
            "design_storm_depth_inches": 0.85,
            "total_volume_cuft": 382,
            "retention_volume_cuft": 333,
            "area_sqft": 2658,
            "media_filtration_rate_inhr": 14.6,
            "hsg": "a",
            "constructor": "bioinfiltration_facility_constructor",
            "tributary_area_tc_min": 55,
            "is_online": True,
        },
    ],
    "treatment_sites": [
        {
            "facility_type": "wet_detention",
            "node_id": "1",
            "area_pct": 6,
            "captured_pct": 57,
            "retained_pct": 38,
        },
        {
            "facility_type": "cistern",
            "node_id": "1",
            "area_pct": 80,
            "captured_pct": 74,
            "retained_pct": 49,
        },
        {
            "facility_type": "swale",
            "node_id": "1",
            "area_pct": 0,
            "captured_pct": 61,
            "retained_pct": 44,
        },
        {
            "facility_type": "dry_weather_diversion",
            "node_id": "1",
            "area_pct": 12,
            "captured_pct": 80,
            "retained_pct": 56,
        },
        {
            "facility_type": "dry_extended_detention",
            "node_id": "1",
            "area_pct": 1,
            "captured_pct": 40,
            "retained_pct": 0,
        },
        {
            "facility_type": "infiltration",
            "node_id": "1",
            "area_pct": 1,
            "captured_pct": 73,
            "retained_pct": 59,
        },
    ],
    "land_surfaces": [
        {
            "node_id": "3",
            "surface_key": "10101000-RESSFH-rock-5",
            "area_acres": 0.3984569310124453,
            "imp_area_acres": 0.009673489252693119,
        },
        {
            "node_id": "3",
            "surface_key": "10101100-RESSFH-D-0",
            "area_acres": 8.065001059380828,
            "imp_area_acres": 2.16741977121951,
        },
        {
            "node_id": "3",
            "surface_key": "10101100-EDU-D-5",
            "area_acres": 2.5839358997133957,
            "imp_area_acres": 2.55343628659585,
        },
        {
            "node_id": "3",
            "surface_key": "10101100-UTIL-A-5",
            "area_acres": 4.312089428850966,
            "imp_area_acres": 4.131205425493061,
        },
        {
            "node_id": "3",
            "surface_key": "10101200-RESSFL-D-5",
            "area_acres": 3.9337442224446297,
            "imp_area_acres": 0.7661658366327859,
        },
        {
            "node_id": "4",
            "surface_key": "10101200-COMM-A-0",
            "area_acres": 0.28767325522239817,
            "imp_area_acres": 0.08026707777353169,
        },
        {
            "node_id": "4",
            "surface_key": "10101200-TRANS-rock-10",
            "area_acres": 6.9571538459344495,
            "imp_area_acres": 1.2273914932176564,
        },
        {
            "node_id": "4",
            "surface_key": "10101200-OSLOW-rock-0",
            "area_acres": 2.403387703304852,
            "imp_area_acres": 0.9959985713261311,
        },
        {
            "node_id": "4",
            "surface_key": "10101200-OSWET-D-5",
            "area_acres": 2.79314881649118,
            "imp_area_acres": 0.15499820430359323,
        },
        {
            "node_id": "4",
            "surface_key": "10101100-OSFOR-D-5",
            "area_acres": 2.905930886150414,
            "imp_area_acres": 1.4925738336538064,
        },
        {
            "node_id": "4",
            "surface_key": "10101000-TRANS-A-5",
            "area_acres": 9.350620373618705,
            "imp_area_acres": 5.232513213963891,
        },
        {
            "node_id": "4",
            "surface_key": "10101200-COMM-C-0",
            "area_acres": 2.1979646924219196,
            "imp_area_acres": 0.2053466380605771,
        },
        {
            "node_id": "4",
            "surface_key": "10101000-OSWET-D-0",
            "area_acres": 9.316054897695937,
            "imp_area_acres": 8.379096506045641,
        },
        {
            "node_id": "4",
            "surface_key": "10101200-TRFWY-A-0",
            "area_acres": 1.4272661923917718,
            "imp_area_acres": 1.2613822514526472,
        },
        {
            "node_id": "4",
            "surface_key": "10101200-OSDEV-C-10",
            "area_acres": 4.221871721446085,
            "imp_area_acres": 0.4549400198109034,
        },
        {
            "node_id": "4",
            "surface_key": "10101100-RESSFH-C-0",
            "area_acres": 0.26360615441130775,
            "imp_area_acres": 0.13605449920172205,
        },
        {
            "node_id": "4",
            "surface_key": "10101000-OSDEV-D-5",
            "area_acres": 7.289650539203478,
            "imp_area_acres": 6.077668638347337,
        },
        {
            "node_id": "5",
            "surface_key": "10101000-IND-A-10",
            "area_acres": 4.930498275495615,
            "imp_area_acres": 4.450757471699112,
        },
        {
            "node_id": "5",
            "surface_key": "10101200-OSLOW-rock-0",
            "area_acres": 7.814106399568224,
            "imp_area_acres": 1.078526163782842,
        },
        {
            "node_id": "5",
            "surface_key": "10101200-RESSFL-D-5",
            "area_acres": 6.185417372804003,
            "imp_area_acres": 5.76250105686173,
        },
        {
            "node_id": "5",
            "surface_key": "10101200-OSIRR-water-10",
            "area_acres": 0.36715726648133273,
            "imp_area_acres": 0.23531606583046188,
        },
        {
            "node_id": "5",
            "surface_key": "10101200-RESMF-D-5",
            "area_acres": 5.3935429017017515,
            "imp_area_acres": 3.810512599072686,
        },
        {
            "node_id": "5",
            "surface_key": "10101100-RESSFH-A-5",
            "area_acres": 2.3620796715469004,
            "imp_area_acres": 1.870944109794398,
        },
        {
            "node_id": "5",
            "surface_key": "10101200-WATER-A-10",
            "area_acres": 5.506805596166197,
            "imp_area_acres": 2.0512411750860533,
        },
        {
            "node_id": "5",
            "surface_key": "10101200-TRFWY-A-5",
            "area_acres": 2.2549267594382885,
            "imp_area_acres": 0.059337765905655114,
        },
        {
            "node_id": "5",
            "surface_key": "10101200-EDU-A-5",
            "area_acres": 6.945443095820329,
            "imp_area_acres": 2.426366435613679,
        },
        {
            "node_id": "5",
            "surface_key": "10101100-IND-D-0",
            "area_acres": 3.8291536983619254,
            "imp_area_acres": 2.4237194475207304,
        },
        {
            "node_id": "5",
            "surface_key": "10101000-RESSFH-D-10",
            "area_acres": 4.720854566650611,
            "imp_area_acres": 1.9563886575871627,
        },
        {
            "node_id": "5",
            "surface_key": "10101000-EDU-C-10",
            "area_acres": 1.7804423698966843,
            "imp_area_acres": 0.3371318723066817,
        },
        {
            "node_id": "6",
            "surface_key": "10101200-TRANS-D-0",
            "area_acres": 2.2754330855140923,
            "imp_area_acres": 1.0211331313414405,
        },
        {
            "node_id": "6",
            "surface_key": "10101100-OSLOW-D-5",
            "area_acres": 6.214500618686376,
            "imp_area_acres": 0.6340460489422389,
        },
        {
            "node_id": "6",
            "surface_key": "10101100-UTIL-A-10",
            "area_acres": 2.555615240745477,
            "imp_area_acres": 2.131208949421928,
        },
        {
            "node_id": "6",
            "surface_key": "10101000-RESSFH-A-5",
            "area_acres": 8.175748802007071,
            "imp_area_acres": 1.8980919101830314,
        },
        {
            "node_id": "6",
            "surface_key": "10101200-RESSFH-A-0",
            "area_acres": 3.860268456910725,
            "imp_area_acres": 1.9184629017741963,
        },
        {
            "node_id": "6",
            "surface_key": "10101200-OSDEV-C-5",
            "area_acres": 0.5748050245941472,
            "imp_area_acres": 0.1411875823737466,
        },
        {
            "node_id": "6",
            "surface_key": "10101000-RESSFH-D-0",
            "area_acres": 7.945535238259879,
            "imp_area_acres": 0.6302494865328522,
        },
        {
            "node_id": "6",
            "surface_key": "10101000-RESMF-D-0",
            "area_acres": 6.915337959629758,
            "imp_area_acres": 3.162694892687792,
        },
        {
            "node_id": "6",
            "surface_key": "10101000-IND-A-5",
            "area_acres": 5.262089934922299,
            "imp_area_acres": 0.012019588367122497,
        },
        {
            "node_id": "6",
            "surface_key": "10101200-EDU-D-10",
            "area_acres": 9.142141560695912,
            "imp_area_acres": 8.229015560695975,
        },
        {
            "node_id": "6",
            "surface_key": "10101200-OSAGIR-A-10",
            "area_acres": 1.1171651349206269,
            "imp_area_acres": 0.5990037582520297,
        },
        {
            "node_id": "6",
            "surface_key": "10101100-OSAGIR-C-0",
            "area_acres": 3.304545692925136,
            "imp_area_acres": 0.36222350149989435,
        },
        {
            "node_id": "6",
            "surface_key": "10101000-RESSFH-D-0",
            "area_acres": 9.63416946726306,
            "imp_area_acres": 7.1542071673930625,
        },
        {
            "node_id": "6",
            "surface_key": "10101100-OSLOW-D-0",
            "area_acres": 4.8579106327541695,
            "imp_area_acres": 0.25541389152635474,
        },
        {
            "node_id": "6",
            "surface_key": "10101200-OSDEV-C-5",
            "area_acres": 6.798391444820259,
            "imp_area_acres": 2.2112485428708193,
        },
        {
            "node_id": "6",
            "surface_key": "10101000-RESSFH-D-10",
            "area_acres": 3.4948300942486963,
            "imp_area_acres": 3.233078107164885,
        },
        {
            "node_id": "6",
            "surface_key": "10101000-OSAGIR-A-10",
            "area_acres": 3.6289953644281625,
            "imp_area_acres": 0.38263683466075843,
        },
        {
            "node_id": "6",
            "surface_key": "10101100-OSDEV-D-0",
            "area_acres": 5.376760581619445,
            "imp_area_acres": 4.5257872671756365,
        },
    ],
}

## Request Models


class Watershed(BaseModel):
    graph: Graph
    land_surfaces: Optional[List[LandSurface]] = None
    treatment_facilities: Optional[
        Union[List[Dict[str, Any]], List[STRUCTURAL_FACILITY_TYPE]]
    ] = None
    treatment_sites: Optional[List[TreatmentSite]] = None
    previous_results: Optional[List[PreviousResult]] = None

    if PYDANTIC_V2:
        model_config = {"json_schema_extra": {"examples": [EXAMPLE_WATERSHED]}}
    else:  # pragma: no cover

        class Config:
            schema_extra = {"examples": [EXAMPLE_WATERSHED]}


## Response Models


class WatershedResults(BaseModel):
    results: Optional[List[Result]] = None
    leaf_results: Optional[List[Result]] = None
    previous_results_keys: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class WatershedResponse(JSONAPIResponse):
    data: Optional[WatershedResults] = None

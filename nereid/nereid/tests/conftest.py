from copy import deepcopy
from itertools import product

import numpy
import pytest

from nereid.core.context import get_request_context
from nereid.models.treatment_facility_models import (
    EXAMPLE_TREATMENT_FACILITIES,
    TREATMENT_FACILITY_MODELS,
    validate_treatment_facility_models,
)
from nereid.tests.utils import (
    generate_random_land_surface_request_sliver,
    generate_random_treatment_facility_request_node,
    generate_random_treatment_site_request,
    generate_random_watershed_solve_request,
)


def pytest_addoption(parser):
    parser.addoption("--async", action="store_true", default=False)


@pytest.fixture(scope="session")
def async_mode(request):
    return request.config.getoption("--async", False)


@pytest.fixture
def subgraph_request_dict():
    graph = {
        "graph": {
            "directed": True,
            "edges": [
                {"source": "3", "target": "1"},
                {"source": "5", "target": "3"},
                {"source": "7", "target": "1"},
                {"source": "9", "target": "1"},
                {"source": "11", "target": "1"},
                {"source": "13", "target": "3"},
                {"source": "15", "target": "9"},
                {"source": "17", "target": "7"},
                {"source": "19", "target": "17"},
                {"source": "21", "target": "15"},
                {"source": "23", "target": "1"},
                {"source": "25", "target": "5"},
                {"source": "27", "target": "11"},
                {"source": "29", "target": "7"},
                {"source": "31", "target": "11"},
                {"source": "33", "target": "25"},
                {"source": "35", "target": "23"},
                {"source": "4", "target": "2"},
                {"source": "6", "target": "2"},
                {"source": "8", "target": "6"},
                {"source": "10", "target": "2"},
                {"source": "12", "target": "2"},
                {"source": "14", "target": "2"},
                {"source": "16", "target": "12"},
                {"source": "18", "target": "12"},
                {"source": "20", "target": "8"},
                {"source": "22", "target": "6"},
                {"source": "24", "target": "12"},
            ],
        },
        "nodes": [{"id": "3"}, {"id": "29"}, {"id": "18"}],
    }

    return graph


@pytest.fixture(scope="module")
def land_surface_loading_response_dicts(contexts, land_surface_permutations):
    n_rows = [10, 50, 500]
    n_nodes = [5, 50, 100]
    responses = {}
    contexts["default"]

    for nrows, nnodes in product(n_rows, n_nodes):
        node_list = list(map(str, range(nnodes)))
        ls_list = [
            generate_random_land_surface_request_sliver(
                numpy.random.choice(node_list),
                numpy.random.choice(land_surface_permutations),
            )
            for _ in range(nrows)
        ]

        ls_request = {"land_surfaces": ls_list}

        responses[(nrows, nnodes)] = ls_request

    yield responses


@pytest.fixture(scope="session")
def contexts():
    cx1 = get_request_context()

    cx2 = deepcopy(cx1)
    cx2.pop("data_path")

    cx3 = deepcopy(cx1)
    cx3["data_path"] = r"¯\_(ツ)_/¯"

    cx4 = deepcopy(cx1)
    cx4.pop("project_reference_data")

    cx5 = deepcopy(cx1)
    cx5["project_reference_data"]["land_surface_table"].pop("file")

    cx6 = deepcopy(cx1)
    cx6["project_reference_data"]["land_surface_table"]["file"] = r"¯\_(ツ)_/¯"

    cx7 = deepcopy(cx1)
    cx7["project_reference_data"]["land_surface_table"] = [r"¯\_(ツ)_/¯"]

    cx8 = deepcopy(cx1)
    cx8["project_reference_data"]["land_surface_table"].pop("preprocess", None)

    cx9 = deepcopy(cx1)
    cx9["project_reference_data"]["land_surface_emc_table"]["file"] = r"¯\_(ツ)_/¯"

    cx10 = deepcopy(cx1)
    cx10["project_reference_data"]["land_surface_emc_table"].pop("parameters")

    cx11 = deepcopy(cx1)
    del cx11["api_recognize"]["land_surfaces"]["preprocess"][2]  # no joins

    cx12 = deepcopy(cx1)
    del cx12["api_recognize"]["land_surfaces"]["preprocess"][3]  # no remaps

    cx13 = deepcopy(cx11)
    del cx13["api_recognize"]["land_surfaces"]["preprocess"][2]  # no joins or remaps

    cx14 = deepcopy(cx11)
    cx14["api_recognize"]["land_surfaces"]["preprocess"].insert(
        1,
        {
            "joins": [
                {
                    "other": "land_surface_table",
                    "how": "left",
                    "left_on": "surface_key",
                    "right_on": "surface_id",
                }
            ]
        },
    )

    cx15 = deepcopy(cx1)
    del cx15["api_recognize"]["treatment_facility"]["preprocess"][0]  # no joins

    cx16 = deepcopy(cx1)
    cx16["api_recognize"]["land_surfaces"]["preprocess"][1]["joins"] = [
        {
            "other": r"¯\_(ツ)_/¯",
            "how": "left",
            "left_on": "surface_key",
            "right_on": "surface_id",
        }
    ]

    cx17 = deepcopy(cx1)
    cx17["api_recognize"]["land_surfaces"]["preprocess"][2]["remaps"] = [
        {
            "left": r"¯\_(ツ)_/¯",
            "right": "imp_pct",
            "how": "addend",
            "mapping": {
                "COMM": 10,
                "RESMF": 15,
                "RESSFH": 20,
                "TRANS": 30,
                "WATER": 100,
            },
        }
    ]

    cx18 = deepcopy(cx1)
    cx18["api_recognize"]["land_surfaces"]["preprocess"][2]["remaps"] = [
        {
            "left": "land_use",
            "right": "imp_pct",
            "how": r"¯\_(ツ)_/¯",
            "mapping": {
                "COMM": 10,
                "RESMF": 15,
                "RESSFH": 20,
                "TRANS": 30,
                "WATER": 100,
            },
        }
    ]

    cx19 = deepcopy(cx1)
    cx19["api_recognize"]["land_surfaces"]["preprocess"][2]["remaps"] = [
        {
            "left": "land_use",
            "right": r"¯\_(ツ)_/¯",
            "how": "addend",
            "mapping": {
                "COMM": 10,
                "RESMF": 15,
                "RESSFH": 20,
                "TRANS": 30,
                "WATER": 100,
            },
        }
    ]

    cx20 = deepcopy(cx1)
    cx20["project_reference_data"]["land_surface_table"]["preprocess"] = [
        {
            "expand_fields": [
                {"field": r"¯\_(ツ)_/¯", "sep": "-", "new_column_names": [1, 2, 3]}
            ]
        },
    ]

    cx21 = deepcopy(cx1)
    cx21["project_reference_data"]["dry_weather_flow_table"]["seasons"] = {
        "summer": None
    }

    cx22 = deepcopy(cx1)
    cx22["project_reference_data"]["dry_weather_flow_table"]["seasons"] = {
        r"¯\_(ツ)_/¯": ["these", "are", "months"]
    }

    cx23 = deepcopy(cx1)  # collapse fields don't exist
    cx23["project_reference_data"]["land_surface_table"]["preprocess"] = [
        {
            "collapse_fields": [
                {"new_column_name": "some_name", "sep": "-", "fields": [1, 2, 3]}
            ]
        },
    ]

    cx24 = deepcopy(cx1)  # collapse should work
    cx24["project_reference_data"]["land_surface_table"]["preprocess"] = [
        {
            "expand_fields": [
                {
                    "field": "surface_id",
                    "sep": "-",
                    "new_column_names": ["_subbasin", "_land_use", "_soil", "_slope"],
                }
            ]
        },
        {
            "collapse_fields": [
                {
                    "new_column_name": "some_name",
                    "sep": "-",
                    "fields": ["_soil", "_slope"],
                }
            ]
        },
    ]

    cx25 = deepcopy(cx1)  # no dry weather calcs
    for t in [
        "dry_weather_flow_table",
        "dry_weather_tmnt_performance_table",
        "dry_weather_land_surface_emc_table",
    ]:
        del cx25["project_reference_data"][t]
    joins = cx25["api_recognize"]["land_surfaces"]["preprocess"][2]["joins"]  # no joins
    del_ix = []
    for i, dct in enumerate(joins):
        other = dct["other"]
        if "dry_weather" in other:
            del_ix.append(i)

    for i in sorted(del_ix, reverse=True):
        del joins[i]

    cxmin = {
        "data_path": cx1["data_path"],
        "api_recognize": {
            "treatment_facility": {
                "facility_type": {
                    "no_treatment": {
                        "validator": "NTFacility",
                        "validation_fallback": "NTFacility",
                        "tmnt_performance_facility_type": "¯\\_(ツ)_/¯",
                        "label": "No Treatment",
                    },
                    "infiltration_simple": {
                        "validator": "SimpleRetFacility",
                        "validation_fallback": "NTFacility",
                        "tmnt_performance_facility_type": "¯\\_(ツ)_/¯",
                        "label": "Infiltration Basin (simple)",
                    },
                    "bioretention_simple": {
                        "validator": "SimpleFacility",
                        "validation_fallback": "NTFacility",
                        "tmnt_performance_facility_type": "Biofiltration",
                        "label": "Bioretention (simple)",
                    },
                    "sand_filter_simple": {
                        "validator": "SimpleTmntFacility",
                        "validation_fallback": "NTFacility",
                        "tmnt_performance_facility_type": "Sand Filter",
                        "label": "Sand Filter (simple)",
                    },
                }
            }
        },
        "project_reference_data": {
            "tmnt_performance_table": {
                "file": "bmp_params.json",
                "facility_column": "facility_type",
                "pollutant_column": "pollutant",
            },
            "land_surface_emc_table": {
                "parameters": [
                    {
                        "long_name": "Total Suspended Solids",
                        "short_name": "TSS",
                        "concentration_unit": "mg/L",
                        "load_unit": "lbs",
                    },
                ]
            },
        },
    }

    keys = [  # these are easier to copy into tests
        "default",
        "default_no_data_path_invalid",
        "default_dne_data_path_invalid",
        "default_no_ref_data_invalid",
        "default_no_lst_file_valid",
        "default_lst_file_dne_invalid",
        "default_lst_not_dict_invalid",
        "default_lst_no_expanded_fields_valid",
        "default_emc_file_dne_invalid",
        "default_emc_no_params_valid",
        "default_api_no_ls_joins_valid",
        "default_api_no_ls_remaps_valid",
        "default_api_no_ls_joins_or_remaps_valid",
        "default_api_ls_joins_no_merge_no_params_valid",
        "default_api_no_tf_joins_valid",
        "default_api_ls_joins_other_dne_valid",
        "default_api_ls_remap_left_dne_valid",
        "default_api_ls_remap_how_dne_valid",
        "default_api_ls_remap_right_dne_valid",
        "default_lst_expand_field_dne_valid",
        "default_dw_flow_null_months_valid",
        "default_dw_flow_unknown_season_valid",
        "default_lst_no_collapse_fields_valid",
        "default_lst_collapse_fields_valid",
        "default_no_dw_valid",
        "min",
    ]

    values = [
        cx1,
        cx2,
        cx3,
        cx4,
        cx5,
        cx6,
        cx7,
        cx8,
        cx9,
        cx10,
        cx11,
        cx12,
        cx13,
        cx14,
        cx15,
        cx16,
        cx17,
        cx18,
        cx19,
        cx20,
        cx21,
        cx22,
        cx23,
        cx24,
        cx25,
        cxmin,
    ]

    return dict(zip(keys, values, strict=True))


@pytest.fixture(scope="module")
def treatment_facility_dicts():
    responses = {}

    for model in TREATMENT_FACILITY_MODELS:
        model_str = model.model_json_schema()["title"]
        dct = generate_random_treatment_facility_request_node(
            model_str, model_str, "10101200", node_id="default"
        )
        responses[model_str] = dct

    yield responses


@pytest.fixture(scope="module")
def valid_treatment_facility_dicts(contexts):
    context = contexts["default"]

    facility_type_dict = contexts["default"]["api_recognize"]["treatment_facility"][
        "facility_type"
    ]

    responses = {}

    for model in TREATMENT_FACILITY_MODELS:
        model_str = model.model_json_schema()["title"]
        facility_type = [
            ft
            for ft, dct in facility_type_dict.items()
            if dct["validator"] == model_str
        ][0]

        dct = generate_random_treatment_facility_request_node(
            model_str, facility_type, "10101200", node_id="default"
        )
        responses[model_str] = validate_treatment_facility_models([dct], context)[0]

    yield responses


@pytest.fixture(scope="module")
def default_context_treatment_facility_dicts(contexts):
    facility_type_dict = contexts["default"]["api_recognize"]["treatment_facility"][
        "facility_type"
    ]

    responses = {}

    for facility_type, dct in facility_type_dict.items():
        model_str = dct["validator"]
        req_dct = generate_random_treatment_facility_request_node(
            model_str, facility_type, "10101200", node_id="default"
        )

        responses[facility_type] = req_dct

    yield responses


@pytest.fixture(scope="module")
def valid_treatment_facilities(valid_treatment_facility_dicts):
    yield list(valid_treatment_facility_dicts.values())


@pytest.fixture(scope="module")
def valid_treatment_site_requests(contexts):
    context = contexts["default"]

    reqs = {}
    for size in [1, 3, 5]:
        node_list = list(map(str, range(size)))
        reqs[size] = generate_random_treatment_site_request(node_list, context)

    return reqs


SIZE = [50, 100, 500]
PCT_TMNT = [0, 0.3, 0.6]


@pytest.fixture(scope="session")
def watershed_requests(contexts, subbasins, land_surface_permutations):
    context = contexts["default"]
    requests = {}
    numpy.random.seed(42)
    for n_nodes, pct_tmnt in product(SIZE, PCT_TMNT):
        seed = numpy.random.randint(1_000_000)
        req = generate_random_watershed_solve_request(
            context,
            subbasins,
            land_surface_permutations,
            n_nodes,
            pct_tmnt,
            seed=seed,
        )
        requests[(n_nodes, pct_tmnt)] = deepcopy(req)
    return requests


def _construct_watershed_test_cases():
    cases = []
    numpy.random.seed(28)
    # this is way overkill, but I wanted to be sure all subsets work.
    for _s, n_nodes, pct_tmnt in product(range(2), SIZE, PCT_TMNT):
        node_ids = list(map(str, range(n_nodes)))

        # max dirty-node length is 50, 4 dirty set-sizes are created
        n_dirty_nodes = numpy.random.randint(2, min(50, n_nodes - 1), size=4)
        for n in n_dirty_nodes:
            # select random dirty nodes for this test case
            random_dirty_nodes = list(
                numpy.random.choice(node_ids, size=n, replace=False)
            )
            cases.append([n_nodes, pct_tmnt, random_dirty_nodes])

    return cases


@pytest.fixture(scope="module", params=_construct_watershed_test_cases())
def watershed_test_case(request):
    yield request.param


@pytest.fixture(scope="session")
def subbasins():
    yield ["10101200", "10101100", "10101000"]


@pytest.fixture(scope="session")
def land_surface_permutations(subbasins):
    land_use = [
        "COMM",
        "EDU",
        "IND",
        "UTIL",
        "RESSFH",
        "RESSFL",
        "RESMF",
        "TRFWY",
        "TRANS",
        "TROTH",
        "OSAGIR",
        "OSAGNI",
        "OSDEV",
        "OSIRR",
        "OSLOW",
        "OSFOR",
        "OSWET",
        "OSVAC",
        "WATER",
    ]
    soil = ["A", "B", "C", "D", "rock", "water"]
    slope = ["0", "10", "5"]

    yield ["-".join(lgu) for lgu in product(subbasins, land_use, soil, slope)]


@pytest.fixture()
def simple_3_node_watershed():
    req = {
        "graph": {
            "directed": True,
            "multigraph": False,
            "graph": {},
            "edges": [
                {"metadata": {}, "source": "1", "target": "0"},
                {"metadata": {}, "source": "2", "target": "1"},
            ],
        },
        "treatment_facilities": [
            {
                "node_id": "1",
                "facility_type": "bioretention",
                "ref_data_key": "10101000",
                "design_storm_depth_inches": 0.85,
                "total_volume_cuft": 5000,
                "retention_volume_cuft": 3000,
                "area_sqft": 2500,
                "media_filtration_rate_inhr": 10,
                "hsg": "a",
                "constructor": "bioinfiltration_facility_constructor",
                "tributary_area_tc_min": 5,
                "is_online": True,
            }
        ],
        "land_surfaces": [
            {
                "node_id": "2",
                "surface_key": "10101000-RESSFH-C-0",
                "area_acres": 0.4,
                "imp_area_acres": 0.38,
            },
            {
                "node_id": "2",
                "surface_key": "10101100-RESSFH-D-0",
                "area_acres": 8.0,
                "imp_area_acres": 4.1,
            },
            {
                "node_id": "2",
                "surface_key": "10101100-EDU-D-5",
                "area_acres": 2.58,
                "imp_area_acres": 2.55,
            },
            {
                "node_id": "2",
                "surface_key": "10101100-UTIL-A-5",
                "area_acres": 4.31,
                "imp_area_acres": 4.1,
            },
            {
                "node_id": "2",
                "surface_key": "10101200-RESSFL-D-5",
                "area_acres": 3.93,
                "imp_area_acres": 1.5,
            },
        ],
    }

    return req


@pytest.fixture()
def treatment_facilities_dict():
    yield {
        dct["facility_type"]: dct
        for dct in EXAMPLE_TREATMENT_FACILITIES["treatment_facilities"]
    }

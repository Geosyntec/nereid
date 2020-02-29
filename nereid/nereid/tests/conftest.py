from pathlib import Path
from itertools import product
from copy import deepcopy

import numpy
import pytest

from nereid.core.utils import get_request_context
from nereid.core.io import load_json
from nereid.src.land_surface.utils import make_fake_land_surface_requests
from nereid.api.api_v1.models.utils import create_random_model_dict
from nereid.api.api_v1.models.treatment_facility_models import TREATMENT_FACILITY_MODELS


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
def land_surface_ids():

    context = get_request_context()
    ls_data = load_json(Path(context["data_path"]) / "land_surface_data.json")["data"]
    ls_ids = [dct["surface_id"] for dct in ls_data]

    yield ls_ids


@pytest.fixture(scope="module")
def land_surface_loading_response_dicts(land_surface_ids):

    n_rows = [10, 50, 5000]
    n_nodes = [5, 50, 1000]
    responses = {}

    for nrows, nnodes in product(n_rows, n_nodes):
        ls_list = make_fake_land_surface_requests(nrows, nnodes, land_surface_ids)
        ls_request = dict(land_surfaces=ls_list)

        responses[(nrows, nnodes)] = ls_request

    yield responses


@pytest.fixture
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
    cx8["project_reference_data"]["land_surface_table"].pop("preprocess")

    cx9 = deepcopy(cx1)
    cx9["project_reference_data"]["land_surface_emc_table"]["file"] = r"¯\_(ツ)_/¯"

    cx10 = deepcopy(cx1)
    cx10["project_reference_data"]["land_surface_emc_table"].pop("parameters")

    cx11 = deepcopy(cx1)
    del cx11["api_recognize"]["land_surfaces"]["preprocess"][0]  # no joins

    cx12 = deepcopy(cx1)
    del cx12["api_recognize"]["land_surfaces"]["preprocess"][1]  # no remaps

    cx13 = deepcopy(cx11)
    del cx13["api_recognize"]["land_surfaces"]["preprocess"][0]  # no joins or remaps

    cx14 = deepcopy(cx11)
    cx14["api_recognize"]["land_surfaces"]["preprocess"].insert(
        0,
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
    cx16["api_recognize"]["land_surfaces"]["preprocess"][0]["joins"] = [
        {
            "other": r"¯\_(ツ)_/¯",
            "how": "left",
            "left_on": "surface_key",
            "right_on": "surface_id",
        }
    ]

    cx17 = deepcopy(cx1)
    cx17["api_recognize"]["land_surfaces"]["preprocess"][1]["remaps"] = [
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
    cx18["api_recognize"]["land_surfaces"]["preprocess"][1]["remaps"] = [
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
    cx19["api_recognize"]["land_surfaces"]["preprocess"][1]["remaps"] = [
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
    cx20["project_reference_data"]["land_surface_table"]["preprocess"][0][
        "expand_fields"
    ] = [{"field": r"¯\_(ツ)_/¯", "sep": "-", "new_column_names": [1, 2, 3]}]

    keys = [  # these are easier to copy into tests
        "default",
        "default_no_data_path_invalid",
        "default_dne_data_path_invalid",
        "default_no_ref_data_invalid",
        "default_no_lst_file_invalid",
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
    ]

    return {k: v for k, v in zip(keys, values)}


@pytest.fixture(scope="module")
def valid_treatment_facility_dicts():
    responses = {}

    for model in TREATMENT_FACILITY_MODELS:

        name = model.schema()["title"]
        dct = create_random_model_dict(model=model, can_fail=False)

        dct["facility_type"] = name
        dct["ref_data_key"] = "10101200"
        dct["design_storm_depth_inches"] = 1.5 * numpy.random.random()

        dct["tributary_area_tc_min"] = int(numpy.random.choice(range(0, 60, 5)))
        dct["offline_diversion_rate_cfs"] = 20 * numpy.random.random()

        if "inf_rate_inhr" in dct:
            dct["inf_rate_inhr"] = 6 * numpy.random.random()

        if "hsg" in dct:
            dct["hsg"] = numpy.random.choice(["a", "b", "c", "d"])

        responses[name] = dct

    yield responses


@pytest.fixture(scope="module")
def valid_treatment_facilities(valid_treatment_facility_dicts):
    yield list(valid_treatment_facility_dicts.values())

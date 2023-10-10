import string
import time
from pathlib import Path
from typing import Any, Dict, List, Set, Union

import networkx as nx
import numpy
import pandas
from pydantic import BaseModel

import nereid.tests.test_data
from nereid._compat import model_json_schema
from nereid.api.api_v1.models import treatment_facility_models
from nereid.src.network.utils import clean_graph_dict

TEST_PATH = Path(nereid.tests.test_data.__file__).parent.resolve()


def get_payload(file):
    path = TEST_PATH / file
    return path.read_text()


def poll_testclient_url(testclient, url, timeout=5, verbose=False):  # pragma: no cover
    ts = time.perf_counter()

    def timer():
        return time.perf_counter() - ts

    tries = 0

    while timer() < timeout:
        response = testclient.get(url)
        if "html" in response.headers["content-type"]:
            return response
        status = response.json().get("status")
        if status is None:
            raise ValueError(
                f"Status is missing from url: {url} \nresponse{response.json()}"
            )
        if status.lower() == "success":
            if verbose:
                print(f"\nget request polling tried: {tries} times")
            return response
        tries += 1
        time.sleep(0.1)
    raise TimeoutError("Task did not return in time.")


def is_equal_subset(
    subset: Union[Dict, List, Set], superset: Union[Dict, List, Set]
) -> bool:
    """determine if all shared keys have equal value"""

    if isinstance(subset, dict):
        return all(
            key in superset and is_equal_subset(val, superset[key])  # type: ignore
            for key, val in subset.items()
        )

    if isinstance(subset, list) or isinstance(subset, set):
        return all(
            any(is_equal_subset(subitem, superitem) for superitem in superset)
            for subitem in subset
        )

    # assume that subset is a plain value if none of the above match
    return subset == superset


def check_graph_data_equal(g, subg):
    for node, dct in subg.nodes(data=True):
        for k, v in dct.items():
            if k == "_is_leaf":
                continue
            og = g.nodes[node][k]
            if isinstance(v, str):
                err_stmt = f"node: {node}; attr: {k}, orig value: {og}; new value: {v}"
                assert v == og, err_stmt
            elif isinstance(v, (int, float)):
                err_stmt = f"node: {node}; attr: {k}, orig value: {og}; new value: {v}"
                # allow floating point errors only
                if og == 0:
                    assert v >= 0 and v < 1e-3, (type(og), type(v), err_stmt)
                else:
                    assert abs(og - v) < 1e-3 or (abs(og - v) / og) < 1e-6, err_stmt


def generate_n_random_valid_watershed_graphs(
    n_graphs: int = 3,
    min_graph_nodes: int = 20,
    max_graph_nodes: int = 50,
    seed: int = 42,
):
    G = nx.DiGraph()
    numpy.random.seed(seed)
    for i in range(n_graphs):
        n_nodes = numpy.random.randint(min_graph_nodes, max_graph_nodes)
        offset = len(G.nodes())
        g = nx.gnr_graph(n_nodes, 0.0, seed=i)
        G.add_edges_from([((offset + s), (offset + t)) for s, t in g.edges])
    return G


def create_random_model_dict(
    model: type[BaseModel], can_fail: bool = True
) -> Dict[str, Any]:
    def random_string(nchars: int) -> str:
        letters = list(string.ascii_letters)
        return "".join([numpy.random.choice(letters) for i in range(nchars)])

    schema = model_json_schema(model)
    reqds = schema["required"]
    props = schema["properties"]
    optionalprops = list(set(props.keys()) - set(reqds))

    extras: List = []
    if can_fail:  # pragma: no cover
        if len(optionalprops) > 1:
            extras = [numpy.random.choice(optionalprops)]
        elif numpy.random.random() > 0.5:
            extras = optionalprops
    else:
        extras = optionalprops

    keys_subset = reqds + extras

    dct = {}
    for k in keys_subset:  # pragma: no cover
        v = props[k]
        value: Any = None

        anyOf = v.get("anyOf", [])
        for d in anyOf:
            if d.get("type", "") in ["string", "number"]:
                v["type"] = d["type"]

        if v.get("default") is not None:
            value = v["default"]
        elif v["type"] == "string":
            value = random_string(12)
        elif v["type"] == "boolean":
            value = numpy.random.choice([True, False])
        elif v["type"] == "number":
            value = numpy.random.random() * 1000

        dct[k] = value

    return dct


def generate_int_sequence_with_sum(total):
    result = []
    remainder = total

    while remainder > 1:
        value = numpy.random.randint(0, remainder)
        result.append(value)
        remainder = total - sum(result)
    result.append(total - sum(result))

    return result


def generate_random_treatment_site_request_node(context, node_id="default"):
    facility_types = list(
        (
            context["api_recognize"]
            .get("treatment_facility", {})
            .get("facility_type", {})
        ).keys()
    )
    treatment_site = []
    site_area_pcts = generate_int_sequence_with_sum(100)
    for area_pct in site_area_pcts:
        dct = {}
        dct["facility_type"] = numpy.random.choice(facility_types)
        dct["node_id"] = node_id
        dct["area_pct"] = area_pct
        dct["captured_pct"] = numpy.random.randint(40, 90)
        dct["retained_pct"] = numpy.random.randint(0, dct["captured_pct"])
        treatment_site.append(dct)
    return treatment_site


def generate_random_treatment_site_request(node_list, context):
    nodes = []
    for node_id in node_list:
        node = generate_random_treatment_site_request_node(context, node_id)
        nodes.extend(node)

    return {"treatment_sites": nodes}


def generate_random_treatment_facility_request_node(
    model_str, facility_type, ref_data_key, node_id="default"
):
    model = getattr(treatment_facility_models, model_str)
    dct = create_random_model_dict(model=model, can_fail=False)

    dct["node_id"] = node_id
    dct["facility_type"] = facility_type
    dct["ref_data_key"] = ref_data_key
    if "simple" in model_str.lower():
        dct["captured_pct"] = numpy.random.uniform(0.1, 99.0)
        del dct["retained_pct"]
    dct["design_storm_depth_inches"] = numpy.random.uniform(0.75, 1.5)

    if "tributary_area_tc_min" in dct:
        dct["tributary_area_tc_min"] = int(numpy.random.choice(range(5, 60, 5)))

    if "months_operational" in dct:
        dct["months_operational"] = numpy.random.choice(["both", "summer"])

    if "inf_rate_inhr" in dct:
        dct["inf_rate_inhr"] = 6 * numpy.random.random()

    if "hsg" in dct:
        dct["hsg"] = numpy.random.choice(["a", "b", "c", "d"])

    if "area_sqft" in dct:
        if "total_volume_cuft" in dct:
            dct["area_sqft"] = dct["total_volume_cuft"] * numpy.random.uniform(4, 8)
        else:
            dct["area_sqft"] = numpy.random.uniform(500, 2500)

    if "depth_ft" in dct:
        dct["depth_ft"] = 6 * numpy.random.random()

    if "treatment_rate_cfs" in dct:
        dct["treatment_rate_cfs"] = 3 * numpy.random.random()

    if "retention_volume_cuft" in dct:
        dct["retention_volume_cuft"] = dct["total_volume_cuft"] * numpy.random.random()

    if "pool_volume_cuft" in dct:  # pragma: no cover
        dct["pool_volume_cuft"] = 2000 * numpy.random.random()

    if "treatment_volume_cuft" in dct:
        dct["treatment_volume_cuft"] = 2000 * numpy.random.random()

    if "treatment_drawdown_time_hr" in dct:
        dct["treatment_drawdown_time_hr"] = 720 * numpy.random.random()

    if "winter_demand_cfs" in dct:
        dct["winter_demand_cfs"] = 2 * numpy.random.random()

    if "summer_demand_cfs" in dct:
        dct["summer_demand_cfs"] = 2 * numpy.random.random()

    return dct


def generate_random_treatment_facility_request(node_list, context, ref_data_keys):
    mapping = context["api_recognize"]["treatment_facility"]["facility_type"]
    facility_types = list(mapping.keys())

    nodes = []
    for node_id in node_list:
        facility_type = numpy.random.choice(facility_types)
        model_str = mapping[facility_type]["validator"]
        ref_data_key = numpy.random.choice(ref_data_keys)
        node = generate_random_treatment_facility_request_node(
            model_str, facility_type, ref_data_key=ref_data_key, node_id=node_id
        )
        nodes.append(node)

    return {"treatment_facilities": nodes}


def generate_random_land_surface_request_sliver(
    node_id,
    surface_key,
    min_acres: float = 0,
    max_acres: float = 10,
    pct_imp_min: float = 0,
    pct_imp_max: float = 1,
):
    area_acres = numpy.random.uniform(min_acres, max_acres)
    imp_area_acres = area_acres * numpy.random.uniform(pct_imp_min, pct_imp_max)

    return {
        "node_id": node_id,
        "surface_key": surface_key,
        "area_acres": area_acres,
        "imp_area_acres": imp_area_acres,
    }


def generate_random_land_surface_request_node(
    surface_keys, node_id="default", sliver_min=5, sliver_max=25, **kwargs
):
    node = []
    for _ in range(numpy.random.randint(sliver_min, sliver_max)):
        surface_key = numpy.random.choice(surface_keys)
        sliver = generate_random_land_surface_request_sliver(
            node_id, surface_key, **kwargs
        )
        node.append(sliver)
    return node


def generate_random_land_surface_request(
    node_list, surface_keys, sliver_min=5, sliver_max=25, **kwargs
):
    nodes = []
    for node_id in node_list:
        node = generate_random_land_surface_request_node(
            surface_keys, node_id, sliver_min, sliver_max, **kwargs
        )
        nodes.extend(node)

    return {"land_surfaces": nodes}


def generate_random_graph_request(n_nodes, seed=0):  # pragma: no cover
    g = nx.gnr_graph(n=n_nodes, p=0.0, seed=seed)
    graph_dict = clean_graph_dict(g)
    return {"graph": graph_dict}


def generate_random_watershed_solve_request_from_graph(
    g,
    context,
    ref_data_keys,
    surface_keys,
    pct_tmnt=0.5,
):
    request = {"graph": clean_graph_dict(g)}

    treatment_facility_nodes = []
    treatment_site_nodes = []
    land_surface_nodes = []

    for n in g:
        if g.in_degree(n) >= 1 and numpy.random.random() < pct_tmnt:
            treatment_facility_nodes.append(n)
        elif g.in_degree(n) >= 1 and numpy.random.random() < pct_tmnt:
            treatment_site_nodes.append(n)
        else:
            land_surface_nodes.append(n)

    if treatment_facility_nodes:
        request.update(
            generate_random_treatment_facility_request(
                treatment_facility_nodes, context, ref_data_keys=ref_data_keys  # type: ignore
            )
        )
    if treatment_site_nodes:
        request.update(
            generate_random_treatment_site_request(treatment_site_nodes, context)  # type: ignore
        )
    if land_surface_nodes:  # pragma: no branch
        request.update(
            generate_random_land_surface_request(land_surface_nodes, surface_keys)  # type: ignore
        )

    return request


def generate_random_watershed_solve_request(
    context,
    ref_data_keys,
    surface_keys,
    n_nodes=55,
    pct_tmnt=0.5,
    seed=42,
):
    g = nx.relabel_nodes(nx.gnr_graph(n=n_nodes, p=0.0, seed=seed), lambda x: str(x))

    request = generate_random_watershed_solve_request_from_graph(
        g,
        context,
        ref_data_keys=ref_data_keys,
        surface_keys=surface_keys,
        pct_tmnt=pct_tmnt,
    )

    return request


def check_subgraph_response_equal(subgraph_results, original_results):
    for subg_result in subgraph_results:
        node = subg_result["node_id"]
        og_result = [n for n in original_results if n["node_id"] == node][0]
        for k, v in subg_result.items():
            if k == "_is_leaf":
                continue
            og = og_result[k]
            if isinstance(v, str):
                err_stmt = f"node: {node}; attr: {k}, orig value: {og}; new value: {v}"
                assert v == og, err_stmt

            elif "load_mpn" in k and isinstance(v, (int, float)):
                err_stmt = f"node: {node}; attr: {k}, orig value: {og}; new value: {v}"

                # the MPN load is frequently in the gazillions, so this
                # tolerance can be a little more forgiving, especially considering
                # the serialization round-trip. Note that the mpn_conc is not
                # afforded the same concession.
                assert abs(og - v) < 1, err_stmt

            elif isinstance(v, (int, float)):
                err_stmt = f"node: {node}; attr: {k}, orig value: {og}; new value: {v}"
                # allow floating point errors only
                if og == 0:
                    assert v >= 0 and v < 1e-3, (og, v, err_stmt)
                else:
                    assert abs(og - v) < 1e-3 or (abs(og - v) / og) < 1e-6, err_stmt


def check_results_dataframes(db1, db2):
    """
    db1 is being checked
    db2 is the reference
    """
    ignore = [c for c in db2.columns if c[0] == "_"] + [
        "node_errors",
        "node_warnings",
        "treatment_facilities",
    ]

    db = db1[[c for c in db1.columns if c not in ignore]]

    for col in db.select_dtypes(include=[numpy.number]):
        if "load_mpn" in col:
            assert abs(numpy.nansum(db[col] - db2[col])) < 1, col
        else:
            assert abs(numpy.nansum(db[col] - db2[col])) < 1e-6, col

    for col in db.select_dtypes(exclude=[numpy.number]):
        pandas.testing.assert_series_equal(db[col], db2[col])

from typing import Any, Callable, Dict, List, Mapping, Tuple, Union

import networkx as nx

from nereid.core.utils import dictlist_to_dict
from nereid.src.land_surface.tasks import land_surface_loading
from nereid.src.network.utils import graph_factory
from nereid.src.network.validate import is_valid, validate_network
from nereid.src.nomograph.nomo import load_nomograph_mapping
from nereid.src.tmnt_performance.tasks import effluent_function_map
from nereid.src.treatment_facility.tasks import initialize_treatment_facilities
from nereid.src.treatment_site.tasks import initialize_treatment_sites
from nereid.src.watershed.dry_weather_loading import (
    accumulate_dry_weather_loading,
    compute_dry_weather_load_reduction,
    compute_dry_weather_volume_performance,
)
from nereid.src.watershed.treatment_facility_capture import (
    compute_volume_capture_with_nomograph,
)
from nereid.src.watershed.treatment_site_capture import solve_treatment_site
from nereid.src.watershed.wet_weather_loading import (
    accumulate_wet_weather_loading,
    check_node_results_close,
    compute_wet_weather_load_reduction,
    compute_wet_weather_volume_discharge,
)
from nereid.src.wq_parameters import init_wq_parameters


def initialize_graph(
    watershed: Dict[str, Any],
    treatment_pre_validated: bool,
    context: Dict[str, Any],
) -> Tuple[nx.DiGraph, List[str]]:

    errors: List[str] = []

    g = graph_factory(watershed["graph"])

    if not is_valid(g):
        err_msg = "NetworkValidationError: "
        _keys = ["node_cycles", "edge_cycles", "multiple_out_edges", "duplicate_edges"]
        for key, value in zip(_keys, validate_network(g)):
            if len(value) > 0:
                err_msg += ", " + ": ".join([key, str(value)])
        errors.append(err_msg)

    land_surface = land_surface_loading(watershed, details=False, context=context)
    errors.extend(land_surface["errors"])

    treatment_facilities = initialize_treatment_facilities(
        watershed, pre_validated=treatment_pre_validated, context=context
    )
    errors.extend(treatment_facilities["errors"])

    treatment_sites = initialize_treatment_sites(watershed, context=context)
    errors.extend(treatment_sites["errors"])

    data: Dict[str, Any] = {}
    for dictlist in [
        watershed.get("previous_results") or [],
        land_surface.get("summary") or [],
        treatment_facilities.get("treatment_facilities") or [],
        treatment_sites.get("treatment_sites") or [],
    ]:
        node_data = dictlist_to_dict(dictlist, "node_id")
        for n, _data in node_data.items():
            if n not in data:
                data[n] = {}
            data[n].update(_data)

    nx.set_node_attributes(g, data)

    return g, errors


def solve_watershed_loading(
    g: nx.DiGraph,
    context: Dict[str, Any],
) -> None:

    wet_weather_parameters = init_wq_parameters(
        "land_surface_emc_table", context=context
    )
    dry_weather_parameters = init_wq_parameters(
        "dry_weather_land_surface_emc_table", context=context
    )

    wet_weather_facility_performance_map = effluent_function_map(
        "tmnt_performance_table", context=context
    )
    dry_weather_facility_performance_map = effluent_function_map(
        "dry_weather_tmnt_performance_table", context=context
    )

    nomograph_map = load_nomograph_mapping(context=context)

    nereid_version = context.get("version", "error: no version info")
    cfg_version = context.get("config_date", "error: no config version info")

    for node in nx.lexicographical_topological_sort(g):
        g.nodes[node]["_version"] = nereid_version
        g.nodes[node]["_config_version"] = cfg_version

        solve_node(
            g,
            node,
            wet_weather_parameters,
            dry_weather_parameters,
            wet_weather_facility_performance_map,
            dry_weather_facility_performance_map,
            nomograph_map,
        )

    return


def solve_node(
    g: nx.DiGraph,
    node: Union[str, int],
    wet_weather_parameters: List[Dict[str, Any]],
    dry_weather_parameters: List[Dict[str, Any]],
    wet_weather_facility_performance_map: Mapping[Tuple[str, str], Callable],
    dry_weather_facility_performance_map: Mapping[Tuple[str, str], Callable],
    nomograph_map: Mapping[str, Callable],
) -> None:
    """Solve a single node of the graph data structure in place.

    This method _must_ be called for each node in a given graph in topological
    order, which ensures that upstream nodes are fully solved before solving
    downstream nodes.

    This top-level function calls helper functions to accomplish several tasks
    including:
    * Collecting all values that need to be passed downstream
    * Determining if the node performs a volume or wq transformation (i.e., it is
      a stormwater facility)
    * Preparing the results of the calculation to be transmitted downstream such that
      the next downstream solution only requires knowledge of the immediate
      predecessors
    * Performing a final mass balance check on the node before exiting.

    Parameters
    ----------
    g : nx.DiGraph
        directed and acyclic graph data structure with nodes
        representing facilities or tributary areas
    node : str or int
        the node id to be analyzed
    *_parameters: list of dicts
        this contains information aabout each parameter, like long_name, short_name and
        conversion factor information. see the *land_surface_emc_tables in the config file.
        these dicts are pre-processed to cache some helpful unit conversions too prior to
        being passed to this function.
        This is needed for both wet weather and dry weather.
        Reference: `nereid.src.wq_parameters.init_wq_parameters`
    *_facility_performance_map : mapping
        this mapping uses a facility type and a pollutant as the keys to retrieve a function
        that returns effluent concentration as output when given influent concentration as input.
        This is needed for both wet weather and dry weather.
        Reference: `nereid.src.tmnt_performance.tmnt.effluent_conc`
        Reference: `nereid.src.tmnt_performance.tasks.effluent_function_map`
    nomograph_map : mapping
        this mapping uses the nomograph data filepath as the key to return a 2d nomograph
        interpolator function. this is not 1:1 with facility types because some facility types,
        like swales, require us to traverse both a flow-based nomograph and a volume based
        nomograph in order to solve for the volume capture, e.g., swales. The necessary information
        for each facility, e.g., which nomograph files to refer to when needed, is joined to the facility
        information from the config.yml::project_reference_data::met_table
        Reference: `nereid.src.nomograph.nomo.load_nomograph_mapping`


    Returns
    -------
    None : results are stored in-place in the graph data structure
        by assigning keys and values to the mutable dict of each
        node in the graph.

    """
    data = g.nodes[node]
    data["_current_node"] = node
    data["_visited"] = True
    data["node_errors"] = []
    data["node_warnings"] = []
    data["_is_leaf"] = False

    if data.get("node_id") is None:
        data["node_id"] = node
        data["node_warnings"].append(
            "WARNING: This node is missing from all input tables."
        )

    # leaf nodes are read only
    if g.in_degree(node) < 1:
        data["_is_leaf"] = True
        return

    node_type = data.get("node_type", "")
    predecessors = list(g.predecessors(node))

    accumulate_wet_weather_loading(g, data, predecessors, wet_weather_parameters)
    accumulate_dry_weather_loading(g, data, predecessors, dry_weather_parameters)

    if "site_based" in node_type:
        # This sequence handles volume capture, load reductions, and also delivers
        # downstream loads.
        # Note that site-based treatment can _never_ be a centralized facility and so
        # certain parameters like 'upstream vol reduction' that are important for
        # computing nested volume capture are not passed through this node type.
        # This means that downstream nodes that are solved via nested volume based
        # treatment will be aware of volume reduction capacity of site-based nodes,
        # but not of volume reducing activities upstream of them. This is fine because
        # the only node type that should ever drain to a site-based treatment facility
        # is a raw land surface, and not an upstream standalone facility.
        solve_treatment_site(
            data,
            wet_weather_parameters,
            dry_weather_parameters,
            wet_weather_facility_performance_map,
            dry_weather_facility_performance_map,
        )

    elif "facility" in node_type:
        if any(
            [_type in node_type for _type in ["volume_based", "flow_based", "dry_well"]]
        ):
            compute_volume_capture_with_nomograph(data, nomograph_map)
            compute_wet_weather_volume_discharge(data)
            compute_wet_weather_load_reduction(
                data, wet_weather_parameters, wet_weather_facility_performance_map
            )

        else:
            # This catches diversions that don't do wet weather tmnt.
            compute_wet_weather_volume_discharge(data)

        compute_dry_weather_volume_performance(data)
        compute_dry_weather_load_reduction(
            data, dry_weather_parameters, dry_weather_facility_performance_map
        )

    else:
        # This is a null node or a land surface node. Just aggregate necessary
        # pass-along values and continue.
        compute_wet_weather_volume_discharge(data)

    check_node_results_close(data)

    return

from typing import Any, Dict

from nereid.core.units import update_unit_registry
from nereid.src.nomograph.nomo import build_nomo
from nereid.src.watershed.solve_watershed import (
    initialize_graph,
    solve_watershed_loading,
)


@update_unit_registry
def solve_watershed(
    watershed: Dict[str, Any], treatment_pre_validated: bool, context: Dict[str, Any],
) -> Dict[str, Any]:
    """Main program function. This function builds the network and solves for water quality
    at each node in the input graph.

    Parameters
    ----------
    watershed : dict
        watersheds have 5 data entities:
            1. graph : defines the connectivity of each component part of the watershed. These
                components can be any of: land surface, treatment facility, treatment site,
                other/nothing/null. See `src.network.
            2. land_surfaces :  which load the graph with

    """

    response = {}

    build_nomo.cache_clear()

    g, msgs = initialize_graph(watershed, treatment_pre_validated, context,)
    response["errors"] = [e for e in msgs if "error" in e.lower()]
    response["warnings"] = [w for w in msgs if "warning" in w.lower()]

    if len(response["errors"]) == 0:  # pragma: no branch
        solve_watershed_loading(g, context=context)

        all_results = [dct for n, dct in g.nodes(data=True)]
        results = [dct for dct in all_results if not dct["_is_leaf"]]
        leafs = [dct for dct in all_results if dct["_is_leaf"]]

        response["results"] = results
        response["leaf_results"] = leafs

    return response

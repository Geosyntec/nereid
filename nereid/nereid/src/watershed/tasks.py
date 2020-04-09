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

    g, errors = initialize_graph(watershed, treatment_pre_validated, context,)
    response["errors"] = errors

    solve_watershed_loading(g, context=context)
    results = [dct for n, dct in g.nodes(data=True)]

    response["results"] = results

    return response

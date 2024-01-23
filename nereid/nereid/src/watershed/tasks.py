from typing import Any

from nereid.core.log import logging
from nereid.core.units import update_reg_from_context
from nereid.src.watershed.solve_watershed import (
    initialize_graph,
    solve_watershed_loading,
)
from nereid.src.watershed.utils import attrs_to_resubmit

logger = logging.getLogger(__name__)


def solve_watershed(
    watershed: dict[str, Any],
    treatment_pre_validated: bool,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Main program function. This function builds the network and solves for water quality
    at each node in the input graph.

    Parameters
    ----------
    watershed : dict
        watersheds have 5 data entities:
            1. graph : defines the connectivity of each component part of the watershed. These
                components can be any of: land surface, treatment facility, treatment site,
                other/nothing/null. See src.network.
            2. land_surfaces :  which load the graph with

    """

    update_reg_from_context(context)

    response = {}

    g, msgs = initialize_graph(
        watershed,
        treatment_pre_validated,
        context,
    )
    response["errors"] = [e for e in msgs if "error" in e.lower()]
    response["warnings"] = [w for w in msgs if "warning" in w.lower()]

    try:  # pragma: no branch
        solve_watershed_loading(g, context=context)

        all_results: list[Any] = [dct for n, dct in g.nodes(data=True)]
        results = [dct for dct in all_results if not dct["_is_leaf"]]
        leafs = [dct for dct in all_results if dct["_is_leaf"]]
        previous_results_keys = attrs_to_resubmit(all_results)

        response["results"] = results
        response["leaf_results"] = leafs
        response["previous_results_keys"] = previous_results_keys

    except Exception as e:  # pragma: no cover
        logger.exception(e)
        response["errors"].append(str(e))

    return response

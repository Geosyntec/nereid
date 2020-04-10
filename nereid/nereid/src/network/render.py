from typing import Optional, IO, Dict, Union, Tuple, List
from io import BytesIO
from functools import lru_cache, partial
from itertools import cycle

import numpy
import networkx as nx
import orjson as json

import matplotlib as mpl
from matplotlib import pyplot as plt


@lru_cache(maxsize=100)
def _cached_layout(
    edge_json: str, prog: str
) -> Dict[Union[str, int], Tuple[float, float]]:
    g = nx.from_edgelist(json.loads(edge_json), create_using=nx.MultiDiGraph)
    layout: Dict[Union[str, int], Tuple[float, float]] = nx.nx_pydot.pydot_layout(
        g, prog=prog
    )
    return layout


def cached_layout(
    g: nx.Graph, prog: str = "dot"
) -> Dict[Union[str, int], Tuple[float, float]]:
    edges = sorted(g.edges(), key=lambda x: str(x))
    edge_json = json.dumps(list(edges))
    return _cached_layout(edge_json, prog=prog)


def get_figure_width_height_from_graph_layout(
    layout_dict: Dict[Union[int, str], Tuple[float, float]],
    npi: Optional[float] = None,
    min_width: float = 1.0,
    min_height: float = 1.0,
) -> Tuple[float, float]:
    """
    Parameters
    ----------
    layout_dict : dict e.g., {'node_id': (x, y), ...}
        layout mapping created by nx.nx_pydot.pydot_layout
    npi : float, optional (default=3)
        nodes per inch of the final figure
    min_width : float, optional (default=1) in inches
    min_height : float, optional (default=1) in inches
    """

    if npi is None:  # pragma: no branch
        npi = 4.0

    ndots = len(layout_dict)

    xmax = max([v[0] for v in layout_dict.values()])
    ymax = max([v[1] for v in layout_dict.values()])
    aspect = ymax / xmax

    width = min_width + (ndots / npi)
    height = min_height + (ndots / npi) * aspect

    return width, height


def render_subgraphs(
    g: nx.DiGraph,
    request_nodes: list,
    subgraph_nodes: list,
    layout: Optional[Dict[Union[str, int], Tuple[float, float]]] = None,
    npi: Optional[float] = None,
    node_size: float = 200,
    ax: Optional[mpl.axes.Axes] = None,
    fig_kwargs: Optional[Dict] = None,
) -> mpl.figure.Figure:

    if fig_kwargs is None:  # pragma: no branch
        fig_kwargs = {}

    if layout is None:  # pragma: no branch
        layout = cached_layout(g, prog="dot")

    if "figsize" not in fig_kwargs:  # pragma: no branch
        width, height = get_figure_width_height_from_graph_layout(layout, npi=npi)
        fig_kwargs["figsize"] = width, height

    if ax is None:  # pragma: no branch
        fig, ax = plt.subplots(**fig_kwargs)

    sgs = [[n["id"] for n in ng["nodes"]] for ng in subgraph_nodes]
    req = [n["id"] for n in request_nodes]

    edge_color = (51 / 255, 51 / 255, 51 / 255)

    basenodes = nx.draw_networkx(
        g,
        pos=layout,
        ax=ax,
        node_size=node_size,
        node_color="lightsteelblue",
        with_labels=True,
        label="all nodes",
        edge_color=edge_color,
    )

    selection = nx.draw_networkx_nodes(
        g.subgraph(req),
        ax=ax,
        pos=layout,
        node_shape="o",
        node_color="none",
        node_size=node_size * 2,
        with_labels=False,
        label="requested nodes",
    )

    selection.set_edgecolor("firebrick")
    selection.set_linewidths(1.5)

    for i, _nodes in enumerate(sgs):
        subgraphs = nx.draw_networkx_nodes(
            g.subgraph(_nodes),
            ax=ax,
            pos=layout,
            node_size=node_size,
            node_color=f"C{i}",
            with_labels=True,
            label=f"subgraph {i+1}",
        )

    ax.legend(loc="upper center", ncol=4, bbox_to_anchor=(0.5, -0.05))
    ax.set_title("User requested nodes: " + ", ".join(req))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")

    return ax.get_figure()


def render_solution_sequence(
    G: nx.DiGraph,
    solution_sequence: List[List[List]],
    ax: Optional[mpl.axes.Axes] = None,
    layout: Optional[Dict[Union[str, int], Tuple[float, float]]] = None,
    npi: Optional[float] = None,
    min_marker_size: float = 40.0,
    max_marker_size: float = 600.0,
    cmap_str: str = "Blues_r",
    marker_cycle_str: str = "^ovs>",
    nx_draw_kwargs: Optional[Dict] = None,
    fig_kwargs: Optional[Dict] = None,
) -> mpl.figure.Figure:
    if layout is None:  # pragma: no branch
        layout = cached_layout(G, prog="dot")
    if fig_kwargs is None:  # pragma: no branch
        fig_kwargs = {}
    if nx_draw_kwargs is None:  # pragma: no branch
        nx_draw_kwargs = {}

    if "figsize" not in fig_kwargs:  # pragma: no branch
        width, height = get_figure_width_height_from_graph_layout(layout, npi=npi)
        fig_kwargs["figsize"] = width, height

    if ax is None:  # pragma: no branch
        fig, ax = plt.subplots(**fig_kwargs)

    marker_cycle = cycle(marker_cycle_str)
    cmap = mpl.cm.get_cmap(cmap_str)

    for k, series_graphs in enumerate(solution_sequence):
        node_shape = next(marker_cycle)

        for i, g in enumerate(series_graphs):

            color_frac = i / len(series_graphs)
            size_inc = (max_marker_size - min_marker_size) / len(series_graphs) * i
            group_size = max_marker_size - size_inc

            color = cmap(color_frac)
            font_color = "k"

            sg = G.subgraph(g)

            _nx_draw_kwargs = dict(
                pos=layout,
                ax=ax,
                node_shape=node_shape,
                node_color=[color for _ in sg.nodes()],
                edge_color=(51 / 255, 51 / 255, 51 / 255),
                width=1.5,
                linewidths=0.5,
                edgecolors=(51 / 255, 51 / 255, 51 / 255),
                node_size=group_size,
                arrows=True,
                with_labels=True,
                font_color=font_color,
                label=f"{k}-{i}",
            )

            _nx_draw_kwargs.update(**nx_draw_kwargs)

            nx.draw(sg, **_nx_draw_kwargs)

    ax.legend(loc="center right", bbox_to_anchor=(-0.05, 0.5))

    return ax.get_figure()


def fig_to_image(fig: mpl.figure.Figure, **kwargs: dict) -> IO:
    bbox_inches = kwargs.pop("bbox_inches", "tight")
    format_ = "svg"

    img = BytesIO()
    fig.savefig(img, bbox_inches=bbox_inches, format=format_, **kwargs)
    img.seek(0)

    return img

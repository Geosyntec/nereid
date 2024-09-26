import warnings
from functools import lru_cache
from io import BytesIO
from itertools import cycle
from typing import IO, TYPE_CHECKING, Any, cast

import networkx as nx
import orjson as json

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
else:
    Axes = Any
    Figure = Any


def pydot_layout(*args, **kwargs) -> dict:
    with warnings.catch_warnings():
        warnings.filterwarnings(action="ignore", message="nx.nx_pydot")
        v = cast(dict, nx.nx_pydot.pydot_layout(*args, **kwargs))
    return v


@lru_cache(maxsize=100)
def _cached_layout(edge_json: str, prog: str) -> dict[str | int, tuple[float, float]]:
    g = nx.from_edgelist(json.loads(edge_json), create_using=nx.MultiDiGraph)
    layout: dict[str | int, tuple[float, float]] = pydot_layout(g, prog=prog)
    return layout


def cached_layout(
    g: nx.Graph, prog: str = "dot"
) -> dict[str | int, tuple[float, float]]:
    edges = sorted(g.edges(), key=lambda x: str(x))
    edge_json = json.dumps(list(edges))
    return _cached_layout(edge_json, prog=prog)


def get_figure_width_height_from_graph_layout(
    layout_dict: dict[str | int, tuple[float, float]],
    npi: float | None = None,
    min_width: float = 1.0,
    min_height: float = 1.0,
) -> tuple[float, float]:
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
    g: nx.Graph,
    request_nodes: list,
    subgraph_nodes: list,
    layout: dict[str | int, tuple[float, float]] | None = None,
    npi: float | None = None,
    node_size: int = 200,
    ax: Axes | None = None,
    fig_kwargs: dict | None = None,
) -> Figure:
    import matplotlib.pyplot as plt

    if fig_kwargs is None:  # pragma: no branch
        fig_kwargs = {}

    if layout is None:  # pragma: no branch
        layout = cached_layout(g, prog="dot")

    if "figsize" not in fig_kwargs:  # pragma: no branch
        width, height = get_figure_width_height_from_graph_layout(layout, npi=npi)
        fig_kwargs["figsize"] = width, height

    if ax is None:  # pragma: no branch
        _, ax = cast(tuple[Figure, Axes], plt.subplots(**fig_kwargs))

    sgs = [[n["id"] for n in ng["nodes"]] for ng in subgraph_nodes]
    req = [n["id"] for n in request_nodes]

    edge_color = (51 / 255, 51 / 255, 51 / 255)

    nx.draw_networkx(
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
        label="requested nodes",
    )

    selection.set_edgecolor("firebrick")
    selection.set_linewidths(1.5)

    for i, _nodes in enumerate(sgs):
        nx.draw_networkx_nodes(
            g.subgraph(_nodes),
            ax=ax,
            pos=layout,
            node_size=node_size,
            node_color=f"C{i}",
            label=f"subgraph {i+1}",
        )

    ax.legend(loc="upper center", ncol=4, bbox_to_anchor=(0.5, -0.05))
    ax.set_title("User requested nodes: " + ", ".join(req))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")

    fig = ax.get_figure() or Figure()

    return fig


def render_solution_sequence(
    G: nx.DiGraph,
    solution_sequence: list[list[list]],
    ax: Axes | None = None,
    layout: dict[str | int, tuple[float, float]] | None = None,
    npi: float | None = None,
    min_marker_size: float = 40.0,
    max_marker_size: float = 600.0,
    cmap_str: str | None = None,
    marker_cycle_str: str = "^ovs>",
    nx_draw_kwargs: dict | None = None,
    fig_kwargs: dict | None = None,
) -> Figure:
    import matplotlib.pyplot as plt
    from matplotlib import colormaps

    if layout is None:  # pragma: no branch
        layout = cached_layout(G, prog="dot")
    if cmap_str is None:  # pragma: no branch
        cmap_str = "Blues_r"
    if fig_kwargs is None:  # pragma: no branch
        fig_kwargs = {}
    if nx_draw_kwargs is None:  # pragma: no branch
        nx_draw_kwargs = {}

    if "figsize" not in fig_kwargs:  # pragma: no branch
        width, height = get_figure_width_height_from_graph_layout(layout, npi=npi)
        fig_kwargs["figsize"] = width, height

    if ax is None:  # pragma: no branch
        _, ax = cast(tuple[Figure, Axes], plt.subplots(**fig_kwargs))

    marker_cycle = cycle(marker_cycle_str)
    cmap = colormaps.get(cmap_str)

    for k, series_graphs in enumerate(solution_sequence):
        node_shape = next(marker_cycle)

        for i, g in enumerate(series_graphs):
            color_frac = i / len(series_graphs)
            size_inc = (max_marker_size - min_marker_size) / len(series_graphs) * i
            group_size = max_marker_size - size_inc

            color = cmap(color_frac) if cmap else "C0"
            font_color = "k"

            sg = G.subgraph(g)

            _nx_draw_kwargs = {
                "pos": layout,
                "ax": ax,
                "node_shape": node_shape,
                "node_color": [color for _ in sg.nodes()],
                "edge_color": [(0.2, 0.2, 0.2, 1) for _ in sg.edges()],
                "width": 1.5,
                "linewidths": 0.5,
                "edgecolors": [(0.2, 0.2, 0.2, 1) for _ in sg.nodes()],
                "node_size": group_size,
                "arrows": True,
                "with_labels": True,
                "font_color": font_color,
                "label": f"{k}-{i}",
            }

            _nx_draw_kwargs.update(**nx_draw_kwargs)

            nx.draw(sg, **_nx_draw_kwargs)

    ax.legend(loc="center right", bbox_to_anchor=(-0.05, 0.5))

    fig = ax.get_figure() or Figure()

    return fig


def fig_to_image(fig: Figure, **kwargs: Any) -> IO:
    _kwargs = {"bbox_inches": "tight", "format": "svg", "dpi": 300}
    _kwargs.update(kwargs)

    img = BytesIO()
    fig.savefig(img, **_kwargs)  # type: ignore[arg-type]
    img.seek(0)

    return img

from io import BytesIO

import numpy
import networkx as nx

import matplotlib as mpl

mpl.use("svg")
from matplotlib import pyplot as plt


def render(
    g, request_nodes, subgraph_nodes, xs=None, ys=None, node_size=None, zoom=None
):
    if xs is None:
        xs = 1
    if ys is None:
        ys = 1
    if node_size is None:
        node_size = 10
    if zoom is None:
        zoom = 1

    ns = numpy.pi * ((node_size * zoom) ** 2) / 4

    fig, ax = plt.subplots(figsize=(8 * zoom, 8 * zoom))

    ax.set_aspect(float(ys) / float(xs))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")

    pos = nx.nx_pydot.pydot_layout(g, prog="dot")

    sgs = [[n["id"] for n in ng["nodes"]] for ng in subgraph_nodes]
    req = [n["id"] for n in request_nodes]

    basenodes = nx.draw_networkx(
        g,
        pos=pos,
        ax=ax,
        node_size=ns,
        node_color="lightsteelblue",
        with_labels=True,
        font_size=5 * zoom,
        label="all nodes",
    )

    for i, _nodes in enumerate(sgs):
        subgraphs = nx.draw_networkx_nodes(
            g.subgraph(_nodes),
            ax=ax,
            pos=pos,
            node_size=ns,
            node_color=f"C{i}",
            with_labels=True,
            font_size=5 * zoom,
            label=f"subgraph {i+1}",
        )

    selection = nx.draw_networkx_nodes(
        g.subgraph(req),
        ax=ax,
        pos=pos,
        node_shape="o",
        node_color="none",
        node_size=ns * 2,
        with_labels=False,
        label="requested nodes",
    )

    selection.set_edgecolor("firebrick")
    selection.set_linewidths(1.5)

    ax.legend(loc="upper center", ncol=4, bbox_to_anchor=(0.5, -0.05))
    ax.set_title("User requested nodes: " + ", ".join(req))

    return fig


def fig_to_image(fig):
    img = BytesIO()
    fig.savefig(img, bbox_inches="tight")
    img.seek(0)

    return img

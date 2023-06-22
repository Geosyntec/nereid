import networkx as nx
import pytest

from nereid.src.network.algorithms import (
    find_leafy_branch_larger_than_size,
    get_all_predecessors,
    get_all_successors,
    get_subset,
    parallel_sequential_subgraph_nodes,
    sequential_subgraph_nodes,
)


def _construct_graphs():
    graphs = [
        # one out edge; these are 'valid' in `nereid`
        (nx.gn_graph(25, seed=42)),
        # many out edges; these are not 'valid' in `nereid`
        (nx.gnc_graph(25, seed=42)),
    ]

    return graphs


@pytest.fixture(params=_construct_graphs())
def g(request):
    yield request.param


def test_network_algo_get_all_predecessors(g):

    # ensure input is a dag
    tsort = list(nx.lexicographical_topological_sort(g))
    for node in g.nodes():
        nix = tsort.index(node)
        preds = get_all_predecessors(g, node)
        ancestors = set(nx.ancestors(g, node))

        # check equivalence with networkx
        assert preds == ancestors

        # double tap
        # this is overkill, but proves all preds
        # are upstream of the input node
        assert all(tsort.index(i) < nix for i in preds)


def test_network_algo_get_all_successors(g):
    tsort = list(nx.lexicographical_topological_sort(g))
    for node in g.nodes():
        nix = tsort.index(node)
        succs = get_all_successors(g, node)
        desc = set(nx.descendants(g, node))

        # check equivalence with networkx
        assert succs == desc

        # double tap
        # this is overkill, but proves all preds
        # are upstream of the input node
        assert all(tsort.index(i) > nix for i in succs)


def test_network_algo_get_subset_dag(g):
    for node in g.nodes():
        subset = get_subset(g, node)
        assert len(subset) <= len(g)


@pytest.fixture
def graph():
    edgelist = [
        ("3", "1"),
        ("5", "3"),
        ("7", "1"),
        ("9", "1"),
        ("11", "1"),
        ("13", "3"),
        ("15", "9"),
        ("17", "7"),
        ("19", "17"),
        ("21", "15"),
        ("23", "1"),
        ("25", "5"),
        ("27", "11"),
        ("29", "7"),
        ("31", "11"),
        ("33", "25"),
        ("35", "23"),
        ("4", "2"),
        ("6", "2"),
        ("8", "6"),
        ("10", "2"),
        ("12", "2"),
        ("14", "2"),
        ("16", "12"),
        ("18", "12"),
        ("20", "8"),
        ("22", "6"),
        ("24", "12"),
    ]

    yield nx.from_edgelist(edgelist, create_using=nx.DiGraph)


@pytest.mark.parametrize(
    "nodes, exp",
    [
        (
            ["3", "29", "18"],
            [
                "3",
                "7",
                "5",
                "29",
                "23",
                "17",
                "9",
                "13",
                "1",
                "11",
                "12",
                "6",
                "2",
                "4",
                "24",
                "10",
                "16",
                "18",
                "14",
            ],
        )
    ],
)
def test_network_algo_get_subset(graph, nodes, exp):

    subset = get_subset(graph, nodes)
    assert subset == set(exp)


def test_find_leafy_branch_larger_than_size(graph):

    with pytest.raises(nx.NetworkXUnfeasible):
        sg = find_leafy_branch_larger_than_size(graph, len(graph))

    for components in nx.weakly_connected_components(graph):
        c_graph = graph.subgraph(components)
        for size in range(1, len(c_graph) + 3):
            sg = find_leafy_branch_larger_than_size(c_graph, size)

            assert len(sg) >= size or sg == c_graph


def check_sequential(seqs, ls):

    root = seqs[-1][-1]  # last sequence, last element
    ls_ix_of_prev_seq_root = -1

    results = []
    last_ele = None
    for seq in seqs:
        last_ele = seq[-1]

        ls_ix_of_current_seq_root = ls.index(last_ele)

        # ensures that the roots of the sub sequences are
        # in topographical order with the entire sorted graph
        results.append(ls_ix_of_current_seq_root > ls_ix_of_prev_seq_root)

    results.append(last_ele == root)

    return all(results)


@pytest.mark.parametrize("size", [1, 3, 5, 10, 100])
def test_sequential_subgraph_nodes(graph, size):

    with pytest.raises(nx.NetworkXUnfeasible):
        _ = sequential_subgraph_nodes(graph, size)

    for components in nx.weakly_connected_components(graph):
        c_graph = graph.subgraph(components)

        if size == 1:
            with pytest.raises(nx.NetworkXUnfeasible):
                seqs = sequential_subgraph_nodes(c_graph, size)

        else:
            seqs = sequential_subgraph_nodes(c_graph, size)
            ls = list(nx.lexicographical_topological_sort(c_graph))
            assert check_sequential(seqs, ls)


@pytest.mark.parametrize("size", [1, 3, 5, 10, 100])
def test_parallel_sequential_subgraph_nodes(graph, size):

    if size == 1:
        with pytest.raises(nx.NetworkXUnfeasible):
            p_seqs = parallel_sequential_subgraph_nodes(graph, size)

    else:
        p_seqs = parallel_sequential_subgraph_nodes(graph, size)
        ls = list(nx.lexicographical_topological_sort(graph))
        for seqs in p_seqs:
            assert check_sequential(seqs, ls)

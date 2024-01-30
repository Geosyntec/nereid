import store from "../../lib/state.js";
import * as util from "../../lib/util.js";

// https://github.com/ChristophKuper/d3-graph-editor/blob/master/src/GraphEditor.js
export class Graph {
  constructor(nodes, edges, options) {
    this.nodes = nodes || [];
    this.edges = edges || [];
    this.options = options || {};
    this.resolve_links();

    store.dispatch("newGraph", { graph: this });
  }

  resolve_links() {
    let self = this;
    self.nodes = self.nodes.filter((n) => n.id != null);
    this.edges.forEach(function (d) {
      let src = d.source;
      let tgt = d.target;

      d.source = self.nodes.find((n) => n.id === src);
      d.target = self.nodes.find((n) => n.id === tgt);
    });

    let xloc = this.options.width || 600;
    let yloc = this.options.height || 400;

    this.nodes.forEach(function (d) {
      if (!d.x) {
        d.x = xloc / 2 + (xloc / 3) * (Math.random() - 1);
      }

      if (!d.y) {
        d.y = yloc / 2 + (yloc / 3) * (Math.random() - 1);
      }
    });
  }

  spliceLinksForNode(node_id) {
    const toSplice = this.edges.filter(
      (l) => l.source.id === node_id || l.target.id === node_id
    );
    for (const l of toSplice) {
      this.edges.splice(this.edges.indexOf(l), 1);
    }
  }
}

export function applyEdges() {
  let { nodes, edges, scenario_name } = util.deepCopy(
    util.get(store, "state.staged_changes")
  );

  let _ = new Graph(nodes, edges);
  store.dispatch("clearStagedChanges", { staged_changes: {} });

  if (scenario_name) store.dispatch("updateScenarioName", { scenario_name });
}

export function updateEdges() {
  let new_nodes = util.deepCopy(util.get(store, "state.staged_changes.nodes")),
    new_edges = util.deepCopy(util.get(store, "state.staged_changes.edges")),
    old_nodes = util.deepCopy(util.get(store, "state.graph.nodes")),
    old_edges = util.deepCopy(util.get(store, "state.graph.edges")),
    edges = [...old_edges, ...new_edges].map((d) => {
      return {
        source: d.source?.id || d.source,
        target: d.target?.id || d.target,
      };
    });

  let nodes = new_nodes;
  for (let n of old_nodes) {
    if (!new_nodes.map((n) => n.id).includes(n.id)) {
      nodes.push(n);
    }
  }

  let _ = new Graph(nodes, edges);

  store.dispatch("clearStagedChanges", { staged_changes: {} });
}

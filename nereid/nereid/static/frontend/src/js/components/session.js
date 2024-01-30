import * as util from "../lib/util";
import store from "../lib/state";
import { Graph } from "./graph-interface/graph";

const saveSession = () => {
  let { graph, scenario_name } = util.get(store, "state");

  sessionStorage.setItem(
    "autosave_graph",
    JSON.stringify({ graph, scenario_name })
  );
};

export const restoreSession = () => {
  let autosave_data = sessionStorage.getItem("autosave_graph");
  let default_graph = util.deepCopy(util.get(store, "state.default_graph"));
  if (autosave_data) {
    // Restore the contents of the graph
    const { graph, scenario_name } = JSON.parse(autosave_data);

    sessionStorage.removeItem("autosave_graph");

    if (graph?.nodes?.length > 0) {
      let _ = new Graph(
        graph.nodes,
        graph.edges.map((e) => {
          return { source: e.source.id, target: e.target.id };
        })
      );
    } else {
      let _ = new Graph(default_graph.nodes, default_graph.edges);
    }

    if (scenario_name) {
      store.dispatch("restoreScenarioName", { scenario_name });
    }
  } else {
    let _ = new Graph(default_graph.nodes, default_graph.edges);
  }
};

window.addEventListener("beforeunload", saveSession);
window.addEventListener("load", (e) => {
  const urlParams = new URLSearchParams(window.location.search);
  const tab = urlParams.get("tab");
  if (tab) {
    store.dispatch("changedTab", { current_tab: tab });
  }
});

import LoadFileUIBase from "../../../../base/load-blob.js";
import * as util from "../../../../../lib/util.js";
import { applyEdges, updateEdges } from "../../../../graph-interface/graph.js";

export const loadGraphFileUI = new LoadFileUIBase({
  id: "graph-file-loader",
  title: "Load Graph (.csv)",
  primary_callback: applyEdges,
  secondary_callback: updateEdges,
  data_callback: function stageEdges(edges) {
    let node_ids = [
      ...new Set(edges.map((a) => a.source).concat(edges.map((a) => a.target))),
    ];
    let old_nodes = util.deepCopy(
      this.store.state.graph.nodes.filter((d) => node_ids.includes(d.id)) || [
        {},
      ]
    );

    // console.log("existing graph", util.get(this, "store.state.graph"));

    let existing_ids = old_nodes.map((d) => d.id);

    let nodes = [];
    let xloc = 50; //this.graph_editor.width / 2;
    let yloc = 50; //this.graph_editor.height / 2;
    let n;

    for (let node_id of node_ids) {
      if (existing_ids.includes(node_id)) {
        n = old_nodes.find((d) => d.id === node_id);
      } else {
        let edge = edges.find((d) => d.source === node_id);

        n = {
          id: node_id,
          x: +edge?.x || xloc + 10 * Math.random(),
          y: +edge?.y || yloc + 10 * Math.random(),
        };
        if (edge?.x || edge?.y) {
          n.fx = +edge?.x;
          n.fy = +edge?.y;
        }
      }
      nodes.push(n);
    }
    this.store.dispatch("setStagedChanges", {
      staged_changes: { edges, nodes },
    });
  },
});

export const loadLandSurfaceFileUI = new LoadFileUIBase({
  id: "land-surface-file-loader",
  title: "Load Land Surfaces (.csv)",
  primary_callback: applyEdges,
  data_callback: function stageLandSurfaces(landsurfaces) {
    let node_ids = [...new Set(landsurfaces.map((a) => a.node_id))];

    let nodes = util.deepCopy(util.get(this, "store.state.graph.nodes"), [{}]);
    let edges = util
      .deepCopy(util.get(this, "store.state.graph.edges"))
      .map((d) => {
        return { source: d.source.id, target: d.target.id };
      });

    let existing_ids = nodes.map((d) => d.id);

    let new_nodes = [];

    let gen_random = () => 400 * Math.random(); // points generated in 400x400 box in upper left of editor

    for (let node_id of node_ids) {
      let data = landsurfaces.filter((d) => d.node_id === node_id);
      let n;
      let long = util.mean(data.filter((d) => d?.long)?.map((d) => +d.long));
      let lat = util.mean(data.filter((d) => d?.lat)?.map((d) => +d.lat));

      let new_data = data.map(
        ({ node_id, surface_key, area_acres, imp_area_acres }) => ({
          node_id,
          surface_key,
          area_acres,
          imp_area_acres,
        })
      );

      if (existing_ids.includes(node_id)) {
        // update existing graph node data
        n = nodes.find((d) => d.id === node_id);
        n.node_type = "land_surface";
        n.data = new_data;

        if (long && lat) {
          n.longlat = [+long, +lat];
        }
      } else {
        // insert any missing nodes into the graph
        n = {
          id: node_id,
          node_type: "land_surface",
          x: gen_random(),
          y: gen_random(),
          data: new_data,
        };

        if (long && lat) {
          n.longlat = [+long, +lat];
        }

        new_nodes.push(n);
      }
    }
    nodes = nodes.concat(new_nodes);

    this.store.dispatch("setStagedChanges", {
      staged_changes: { edges, nodes },
    });
  },
});

export const loadTreatmentFacilitiesFileUI = new LoadFileUIBase({
  id: "treatment-facilities-file-loader",
  title: "Load Treatment Facilities (.csv)",
  primary_callback: applyEdges,
  data_callback: function stageTmntFacilities(tmntfacilities) {
    let node_ids = [...new Set(tmntfacilities.map((a) => a.node_id))];

    let nodes = util.deepCopy(
      util.get(this, "store.state.graph.nodes") || [{}]
    );
    let edges = util
      .deepCopy(util.get(this, "store.state.graph.edges") || [{}])
      .map((d) => {
        return { source: d.source.id, target: d.target.id };
      });
    let existing_ids = nodes.map((d) => d.id);

    let new_nodes = [];

    let gen_random = () => 400 * Math.random(); // points generated in 400x400 box in upper left of editor

    for (let node_id of node_ids) {
      // find returns the first matching element, filter returns a list of all matching elements
      let data = tmntfacilities.find((d) => d.node_id === node_id);
      let n;

      let { long, lat } = data;

      if (existing_ids.includes(node_id)) {
        // update existing graph node data
        n = nodes.find((d) => d.id === node_id);
        n.data = data;
        n.node_type = "treatment_facility";
        if (long && lat) {
          n.longlat = [+long, +lat];
        }
      } else {
        // insert any missing nodes into the graph
        n = {
          id: node_id,
          node_type: "treatment_facility",
          x: gen_random(),
          y: gen_random(),
          data: data,
        };
        if (long && lat) {
          n.longlat = [+long, +lat];
        }
        new_nodes.push(n);
      }
    }
    nodes = nodes.concat(new_nodes);

    this.store.dispatch("setStagedChanges", {
      staged_changes: { edges, nodes },
    });
  },
});

export const loadScenarioFileUI = new LoadFileUIBase({
  id: "scenario-file-loader",
  title: "Load Scenario (.json)",
  primary_callback: applyEdges,
  secondary_callback: updateEdges,
  data_callback: function stageScenario(scenario) {
    let graph = scenario.graph;
    let scenario_name = scenario.name;
    let nodes = util.deepCopy(graph.nodes || [{}]);

    for (let node of nodes) {
      if (node.id == null) {
        console.error("bad egg:", node);
      }
    }
    let edges = graph.edges.map((d) => {
      return { source: d.source.id, target: d.target.id };
    });

    this.store.dispatch("setStagedChanges", {
      staged_changes: { edges, nodes, scenario_name },
    });
  },
});

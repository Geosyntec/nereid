import * as topojson from "topojson-client";
import rewind from "@turf/rewind";

import * as api from "../../lib/nereid-api";
import store from "../../lib/state.js";
import * as util from "../../lib/util.js";

import Component from "./component.js";

export default class VectorLayer extends Component {
  constructor({ vector }) {
    super({ store });
    let self = this;
    self.group = vector.append("g");
    self.stroke_width = 0;
    self.domain = [0, 1];
    self.projection = util.get(self, "store.state.projection");
    self.renderer = d3.geoPath(self.projection).digits(15);
  }

  get transform() {
    return util.get(this, "store.state.transform");
  }

  async _load_data(info) {
    let self = this;

    if (!info) return;

    let geojson, rsp;

    try {
      if (info?.filepath) {
        rsp = await api.getReferenceData(info.filepath);
      } else if (info?.url) {
        rsp = await util.getJsonResponse(info.url);
      } else {
        return;
      }
    } catch (error) {
      console.error(error);
      return;
    }

    try {
      if (rsp?.type === "Topology") {
        let topology = rsp;
        geojson = topojson.feature(topology, topology.objects[info.name]);
      } else if (rsp?.type === "FeatureCollection") {
        geojson = rsp;
        geojson.features = geojson.features.map((d) =>
          rewind(d, { reverse: true })
        );
      }
    } catch (error) {
      console.error(error);
      return;
    }
    if (geojson) {
      geojson._field = info.field;
      let domain_arr = geojson.features.map((d) => d.properties[info.field]);
      self.domain = [Math.min(...domain_arr), Math.max(...domain_arr)];
      self.geojson = geojson;
    }
  }
}

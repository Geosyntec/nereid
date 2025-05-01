import Component from "../../../../base/component.js";
import d3 from "../../../../../lib/d3.js";
import * as util from "../../../../../lib/util.js";
import store from "../../../../../lib/state.js";
import { saveAs } from "file-saver";

export class SaveTmntFacilityUI extends Component {
  constructor(options) {
    super({ store, id: options.id });
  }

  get facility_types() {
    return Object.keys(util.get(this, "store.state.facility_type_map"));
  }

  get facility_type_map() {
    return util.get(this, "store.state.facility_type_map");
  }

  get schema() {
    return util.get(this, "store.state.schema");
  }

  get scenario_name() {
    return util.get(this.store, "state.scenario_name");
  }

  get facility_properties() {
    let properties = new Set();

    for (let facility of this.facility_types) {
      let schema_name = this.facility_type_map[facility];
      let schema = this.schema[schema_name];
      Object.keys(schema.properties).forEach(properties.add, properties);
    }

    // add in the ones not in the nereid schemas
    ["long", "lat"].forEach(properties.add, properties);

    return properties;
  }

  get facility_data() {
    let properties = this.facility_properties;

    let records = [];

    let treatment_facility_nodes = util
      .deepCopy(util.get(this, "store.state.graph.nodes") || [{}])
      .filter((n) => n.node_type == "treatment_facility");

    if (treatment_facility_nodes.length == 0) {
      treatment_facility_nodes = [{}];
    }

    treatment_facility_nodes.forEach((n) => {
      let record = {};
      for (let p of properties) {
        record[p] = util.get(n.data, p) || "";
      }

      let longlat = n?.longlat || ["", ""];

      record["long"] = longlat[0];
      record["lat"] = longlat[1];

      records.push(record);
    });

    return records;
  }

  facility_template() {
    let self = this;

    let records = [];

    let state = util.get(self, `store.state.nereid_state`);
    let region = util.get(self, `store.state.nereid_region`);

    let treatment_facility_fields =
      util.get(
        self,
        `store.state.treatment_facility_fields.${state}.${region}`
      ) || util.get(self, "store.state.treatment_facility_fields.state.region");

    let ignored = treatment_facility_fields?.ignored || [];
    let disabled = treatment_facility_fields?.disabled || [];

    let properties = [...this.facility_properties].filter(
      (p) => !ignored.includes(p)
    );

    for (let [name, type] of Object.entries(this.facility_type_map)) {
      let schema = this.schema[type];
      let record = {};

      for (let prop of properties) {
        let text = util.get(schema.properties[prop], "type") || "";
        if (schema.required.includes(prop)) {
          text += "-req";
        }
        if (disabled.includes(prop)) {
          text += "-uneditable";
        }
        record[prop] = text;
      }
      record["long"] = "number";
      record["lat"] = "number";
      record.facility_type = name;
      records.push(record);
    }

    return records;
  }

  saveTreatmentCSV() {
    let csv_data = this.facility_data;
    let scenario_name = this.scenario_name.replaceAll(" ", "-");

    let proto_csv = {
      filename: `${scenario_name}-treatment_facilities.csv`,
      csv: util.convertArrayOfObjectsToCSV({ data: csv_data }),
    };

    let blob = new Blob([proto_csv.csv], {
      type: "text/plain;charset=utf-8",
    });
    saveAs(blob, proto_csv.filename);
  }

  saveTreatmentTemplateCSV() {
    let csv_data = this.facility_template();
    let state = util.get(this, "store.state.nereid_state");
    let region = util.get(this, "store.state.nereid_region");

    let proto_csv = {
      filename: `${state}-${region}-treatment_facilities-template.csv`,
      csv: util.convertArrayOfObjectsToCSV({ data: csv_data }),
    };

    let blob = new Blob([proto_csv.csv], {
      type: "text/plain;charset=utf-8",
    });
    saveAs(blob, proto_csv.filename);
  }

  _template() {
    return `
<div>
  <div class="flex flex-row w-full p-4 justify-between items-center"><strong>Save Treatment Facility Info to File (csv)</strong>
      <button
        id="save-tmnt"
        class="btn btn-blue"
      >
        Save
      </button>
  </div>
</div
<div>
  <div class="flex flex-row w-full p-4 justify-between items-center"><strong>Save Treatment Facility Template to File (csv)</strong>
      <button
        id="save-tmnt-template"
        class="btn btn-blue"
      >
        Save
      </button>
  </div>
</div
    `;
  }

  _render() {
    let self = this;
    self.element = d3
      .select(`#${self.parent_id}-content`)
      .append("div")
      .attr("id", self.id);
    self.element.html(self._template());

    self.store.events.subscribe("updateConfig", () => {
      // console.log(self.facility_data);
    });

    self.element
      .select("#save-tmnt")
      .on("click", self.saveTreatmentCSV.bind(self));

    self.element
      .select("#save-tmnt-template")
      .on("click", self.saveTreatmentTemplateCSV.bind(self));
  }
}

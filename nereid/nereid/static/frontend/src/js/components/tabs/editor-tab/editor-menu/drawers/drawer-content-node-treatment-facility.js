import Component from "../../../../base/component.js";
import d3 from "../../../../../lib/d3.js";
import store from "../../../../../lib/state.js";
import * as util from "../../../../../lib/util.js";

export class TreatmentFacilityNodeEditorUI extends Component {
  constructor(options) {
    super({ store });
    let self = this;
  }

  get node_editor_type() {
    return util.get(this, "store.state.node_editor_type");
  }

  get selected_node() {
    let id = util.get(this, "store.state.selected_node_id");
    let n = util.get(this, "store.state.graph.nodes").find((n) => n.id === id);
    return n;
  }

  get config() {
    let {
      schema,
      facility_types,
      facility_type_map,
      facility_alias_map,
      facility_label_map,
    } = util.get(this, "store.state");
    return {
      schema,
      facility_types,
      facility_type_map,
      facility_alias_map,
      facility_label_map,
    };
  }

  update() {
    let self = this;
    self.element.html("").classed("flex flex-col w-full", true);
    self.element.classed(
      "hidden",
      !(self.node_editor_type === "treatment_facility")
    );

    let select = self.element
      .append("select")
      .classed("px-2 my-4 h-8 border rounded-md", true)
      .attr("id", "facility-picker")
      .on("change", function () {
        let facility_type = self.element
          .select("#facility-picker")
          .property("value");
        if (!facility_type.length) {
          return false;
        }
        // let facility_key = self.config.facility_alias_map[facility_type];

        let facility_schema = self.config.facility_type_map[facility_type];

        // console.log("facility type", facility_type);
        // console.log("facility schema", facility_schema);

        let existing_data = util.deepCopy(
          util.get(self, "selected_node.data") || {}
        );

        if (Array.isArray(existing_data)) {
          existing_data = {};
        }

        let form_data = {
          node_id: self.selected_node.id,
          facility_type: facility_type,

          ref_data_key:
            self.selected_node?.data?.ref_data_key ||
            self.selected_node?.ref_data_key,

          design_storm_depth_inches:
            self.selected_node?.data?.design_storm_depth_inches ||
            self.selected_node?.design_storm_depth_inches,
        };

        form_data = Object.assign(existing_data, form_data);

        // console.log("data to form:", form_data);

        const onSubmit = (result) => {
          // console.log("tmnt form result", result);
          self.selected_node.node_type = self.node_editor_type;
          self.selected_node.data = Object.assign(
            {
              facility_type: self.element
                .select("#facility-picker")
                .property("value"),
            },
            util.deepCopy(result)
          );
          self.selected_node.id = result.node_id;

          // TODO:  if user sets ref_data_key in the form, it's overwritten upon submit.
          self.store.dispatch("newGraph");
          // self.graph_editor.restart();
          // d3.select("#current_node_id").text(result.node_id);
        };

        let state = util.get(self, `store.state.nereid_state`);
        let region = util.get(self, `store.state.nereid_region`);

        let treatment_facility_fields =
          util.get(
            self,
            `store.state.treatment_facility_fields.${state}.${region}`
          ) ||
          util.get(self, "store.state.treatment_facility_fields.state.region");

        console.debug("tmnt facility fields:", treatment_facility_fields);

        build_form(
          "#facility-form",
          self.config.schema[facility_schema],
          form_data,
          treatment_facility_fields.disabled,
          treatment_facility_fields.ignored,
          onSubmit.bind(self)
        );
      });

    let form_container = self.element.append("div").attr("id", "facility-form");

    let data = util.deepCopy(self.config.facility_types || []);
    data.unshift("");

    let options = select
      // .classed("selectpicker", true)
      .selectAll("option")
      .data(data)
      .enter()
      .append("option")
      .attr("value", (d) => (d ? self.config.facility_label_map[d] : d))
      .text((d) => d);

    let facility_type = util.get(self, "selected_node.data.facility_type");
    if (facility_type) {
      self.element.select("#facility-picker").property("value", facility_type);
      select.on("change")();
    }
    // $("#facility-picker").selectpicker("render");
  }
  _render() {
    let self = this;
    self.element = d3.select(`#${self.parent_id}-content`).append("div");
    self.id = `${self.parent_id}-content-treatment-form`;
    self.element.attr("id", self.id);

    self.update();
    // self.store.events.subscribe("nodeEditorType", () => self.update());
    // self.store.events.subscribe("changedSelectedNode", () => self.update());
    // self.store.events.subscribe("updateConfig", () => self.update());
    self.store.events.subscribe("stateChange", () => this.update());
  }
}

function build_form(divid, schema, existing_data, disabled, ignored, onSubmit) {
  let keys = [...schema.required];
  let optional_keys = Object.keys(schema.properties).filter(
    (k) => !keys.includes(k)
  );
  keys.push(...optional_keys);
  let data = [];
  for (const k of keys.filter((k) => !ignored.includes(k))) {
    let prop = schema.properties[k];
    prop.name = k;
    data.push(prop);
  }

  let div = d3.select(divid);
  div.html("");
  let form = div.append("form");

  form
    .attr("id", divid.replace("#", "") + "-form")
    .attr("name", divid.replace("#", "") + "-form")
    .attr("method", "get")
    .on("submit", function (event) {
      event.preventDefault();
      form.selectAll("input").property("disabled", false);
      const data = new FormData(event.target);
      const value = util.cleanObject(Object.fromEntries(data.entries()));
      if (onSubmit) onSubmit(value);
      // console.log(value, data.entries());
      return false;
    });

  form
    .selectAll("div")
    .data(data)
    .enter()
    .append("div")
    .classed(
      "form-group flex flex-row w-full gap-4 text-sm my-4 h-8 items-center",
      true
    )
    .classed("required", (d) => schema.required.includes(d.name))
    .each(function (d, i) {
      let is_required = schema.required.includes(d.name);
      let html_title =
        (d.description || d.name) +
        (is_required ? " (required)" : " (optional)");

      let self = d3.select(this);
      let label = self
        .append("label")
        .classed("control-label py-2 flex w-1/2 ", true)
        .attr("title", html_title)
        .text(d.title);
      let input;

      switch (d.type) {
        case "string":
          input = self
            .append("input")
            .attr("name", d.name)
            .attr("id", d.name)
            .attr("title", html_title)
            .property("required", schema.required.includes(d.name || ""))
            .property("disabled", disabled.includes(d.name))
            .classed("border-2 rounded-md px-2 py-1", true);

          input
            .attr("type", "text")
            // ["pattern", "placeholder", "default"].forEach(function (key) {
            //   if (key in d) input.attr(key, d[key]);
            // });
            .attr("pattern", d.pattern || ".*")
            // .attr("defaultValue", d.default || "") // apparently d3 cannot set a mixed case attribute.
            .attr("value", d.example || d.default || "");
          break;
        case "number":
          input = self
            .append("input")
            .attr("name", d.name)
            .attr("id", d.name)
            .attr("title", html_title)
            .property("required", schema.required.includes(d.name || ""))
            .property("disabled", disabled.includes(d.name))
            .classed("border-2 rounded-md px-2 py-1", true);

          input
            .attr("type", "number")
            .attr("step", "0.001")
            .attr("value", d.example || d.default || "");
          // ["pattern", "placeholder", "default"].forEach(function (key) {
          //   if (key in d) input.attr(key, d[key]);
          // });
          //   .attr("placeholder", d.example || "");
          break;
        case "boolean":
          input = self.append("div").classed("flex flex-row", true);
          for (let b of [true, false]) {
            let bid = d.name + b.toString();
            let fg = input
              .append("div")
              .classed("flex flex-row items-center", true);

            fg.append("input")
              .classed("form-check-input p-2", true)
              .classed("p-2", true)
              .attr("type", "radio")
              .attr("name", d.name)
              .attr("id", bid)
              .attr("title", html_title)
              .property("checked", d.default == b)
              .property("disabled", disabled.includes(d.name))
              .attr("value", b);

            fg.append("label")
              .classed("p-2", true)
              .attr("for", bid)
              .attr("title", html_title)
              .text(b.toString());
          }

          // todo: add a true check and a false check otherwise false values are dropped.
          // self.classed("form-check-inline", true);
          // input
          //   .attr("class", "form-check-input")
          //   .attr("type", "checkbox")
          //   .property("checked", d.default !== undefined ? d.default : false)
          //   .attr("value", (d) =>
          //     (d.default !== undefined ? d.default : false) ? false : true
          //   );
          break;
      }
    });

  for (let [k, v] of Object.entries(existing_data)) {
    if (["true", "false"].includes(v)) {
      // then it's a boolean
      for (let b of ["true", "false"]) {
        d3.select("#" + k + b).property("checked", v == b);
      }
    } else {
      d3.select("#" + k).property("value", v);
    }
  }

  let btn_gp = form.append("div").classed("flex justify-end", true);

  btn_gp.append("div");
  btn_gp
    .append("button")
    .classed("btn btn-blue", true)
    .attr("type", "submit")
    .text("Apply");
}

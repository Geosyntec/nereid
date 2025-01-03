import Component from "../../base/component.js";
import store from "../../../lib/state.js";
import d3 from "../../../lib/d3.js";
import * as util from "../../../lib/util.js";
// import * as results from "./result_summary";

async function resultTable(divid, options) {
  let { default: XLSX } = await import("xlsx");
  let {
    Tabulator,
    DownloadModule,
    ExportModule,
    FormatModule,
    ResizeColumnsModule,
  } = await import("tabulator-tables");

  Tabulator.registerModule([
    DownloadModule,
    ExportModule,
    FormatModule,
    ResizeColumnsModule,
  ]);

  let default_options = {
    data: [{}], //load row data from array
    // clipboard: true,
    // clipboardPasteAction: "update",
    maxHeight: "500px",
    minHeight: 80,
    // height: 100,
    // width: 800,
    autoResize: false, // Resize observer errors abound if this is true!!!
    layout: "fitData", //fit columns to width of table
    responsiveLayout: false, //hide columns that dont fit on the table
    history: false, //allow undo and redo actions on the table
    tooltipsHeader: true,
    footerElement: `<div class="tabulator-footer"></div>`, //add a custom button to the footer element
    columns: [],
    initialSort: [{ column: "node_id", dir: "asc" }],
    dependencies: { XLSX },
  };

  let merged_options = Object.assign(default_options, options);
  return new Tabulator(divid, merged_options);
}

export class ResultsTab extends Component {
  constructor(options) {
    super({ store, id: options.id });

    let self = this;

    self.table_builders = options.table_builders || [];
    self.tables = [];
  }

  get scenario_name() {
    return util.get(this.store, "state.scenario_name");
  }

  async buildResultsSummary({
    id,
    data,
    prep_fnx,
    title,
    description,
    filename_csv,
  }) {
    let self = this;

    // const id = "table-facility-capture";
    self.element.select(`#${id}`).remove();
    let ele = self.element
      .append("div")
      .attr("id", id)
      .classed("grid grid-cols-1 grid-rows-auto pt-8", true);

    let header = ele
      .append("div")
      .classed(" flex flex-row w-full justify-between items-center", true);
    header.append("div").classed("font-bold", true).html(title);

    const [summary_data, data_keys] = prep_fnx(data);

    if (!summary_data.length) {
      ele
        .append("div")
        .classed("flex justify-center", true)
        .html("no results to show for this summary yet...");
      return;
    }

    let button = header
      .append("div")
      .classed("py-2", true)
      .append("button")
      .text("Download Data (csv)")
      .classed("btn btn-blue", true);

    if (description != null) ele.append("div").html(description);

    const table_id = id + "-results-tabulator";

    ele.append("div").attr("id", table_id);

    let table = await resultTable(`#${table_id}`, {
      data: summary_data,
      columns: data_keys.map((d) => {
        let obj = {
          title: d.replaceAll("_", " "),
          field: d,
          titleDownload: d,
        };
        let num_flags = [
          "_acres",
          "_coeff",
          "_load",
          "_pct",
          "_conc",
          "_lbs",
          "_cuft",
          "_cfs",
          "_mpn",
          "_inhr",
        ];
        if (num_flags.some((e) => d.includes(e))) {
          obj.formatter = "money";
          obj.formatterParams = {
            precision: 2,
          };
        }
        if (d.includes("_pct")) {
          obj.formatterParams = {
            precision: 2,
            symbol: "%",
            symbolAfter: "p",
          };
        }
        if (d.includes("_mpn")) {
          obj.formatterParams = {
            precision: 0,
          };
        }
        return obj;
      }),
    });

    self.tables.push(table);
    let scenario_name = self.scenario_name.replaceAll(" ", "-");

    button.on("click", () => {
      table.download("csv", scenario_name + "-" + filename_csv);
    });
  }

  async update(data) {
    // console.log("running results update", data);
    let self = this;
    data = data || [];
    self.element.html("");
    if (data?.length > 0) {
      self.element.select(`#dummy_table`).remove();
      self.element
        .append("div")
        .attr("id", "dummy_table")
        .classed("hidden", true);
      let table = await resultTable("#dummy_table");
      let download_all_button = self.element
        .append("div")
        .append("button")
        .classed("btn btn-blue", true)
        .text("Download All Data Summaries (xlsx)");

      download_all_button.on("click", () => {
        let sheets = {};
        self.element
          .selectAll("[id$='-results-tabulator']")
          .nodes()
          .forEach((n) => {
            let id = d3.select(n).attr("id");
            let sheet = id
              .replace("-results-tabulator", "")
              .replace("table-", "")
              .replace("facility-", "bmp-")
              .slice(0, 30);
            if (!id.includes("table-all-data")) sheets[sheet] = "#" + id;
          });
        self.element.select(`#dummy_table`).remove();
        self.element
          .append("div")
          .attr("id", "dummy_table")
          .classed("hidden", true);
        table.download("xlsx", "AllData.xlsx", { sheets });
      });
    }
    util.incr_waiting();
    try {
      for (let func of self.table_builders) {
        await self.buildResultsSummary(func(data));
      }

      // // land surface
      // await self.buildResultsSummary(results.table_land_surface_summary(data));

      // // design summary
      // await self.buildResultsSummary(
      //   results.table_facility_design_summary(data)
      // );
      // // volume capture
      // await self.buildResultsSummary(results.table_facility_capture(data));
      // await self.buildResultsSummary(
      //   results.table_facility_volume_reduction(data)
      // );
      // await self.buildResultsSummary(
      //   results.table_facility_total_volume_reduction(data)
      // );

      // await self.buildResultsSummary(
      //   results.table_facility_wet_weather_volume_reduction(data)
      // );

      // await self.buildResultsSummary(
      //   results.table_facility_dry_weather_volume_reduction(data)
      // );

      // // load reduction
      // await self.buildResultsSummary(
      //   results.table_facility_load_reduction(data)
      // );
      // await self.buildResultsSummary(
      //   results.table_facility_total_load_reduction(data)
      // );
      // await self.buildResultsSummary(
      //   results.table_facility_wet_weather_load_reduction(data)
      // );
      // await self.buildResultsSummary(
      //   results.table_facility_dry_weather_load_reduction(data)
      // );

      // All data - Raw
      // await self.buildResultsSummary(results.table_all_data(data));
    } finally {
      util.decr_waiting();
    }
  }

  _template() {
    return `
      <div>Click 'Run Scenario' in the Editor to calculate results.</div>
    `;
  }

  _render() {
    let self = this;
    self.element = d3
      .select(`#${self.id}`)
      .classed("relative flex justify-center", true)
      .append("div")
      .classed("flex flex-col relative max-w-screen-md py-10 ", true)
      .html(self._template());

    self.store.events.subscribe("newResults", ({ results }) =>
      self.update(results)
    );
    self.store.events.subscribe("changedTab", ({ current_tab }) => {
      // TODO make this not re-render the tables when changing tabs unless there's
      // data to show or reload.
      if (current_tab === self.id) {
        let results = util.get(self, "store.state.results");
        self.update(results);
      }
    });
  }
}

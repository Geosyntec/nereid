import Component from "./component.js";
import d3 from "../../lib/d3.js";
import * as util from "../../lib/util.js";
import store from "../../lib/state.js";

export default class LoadFileUIBase extends Component {
  constructor(options) {
    super({ store });
    let self = this;
    self.id = options.id;
    self.title = options.title;
    self.data = [{}];

    self.data_callback =
      options.data_callback ||
      function (data) {
        console.log("loaded data: ", data);
      };

    self.primary_callback =
      options.primary_callback ||
      function () {
        console.log(`clicked primary button load files UI ${self.id}`);
      };
    self.primary_button_label = options.primary_button_label || "Apply";

    self.secondary_callback = options.secondary_callback || null;
    self.secondary_button_label = options.secondary_button_label || "Update";
  }

  _template_primary_button() {
    if (this.primary_callback == null) return "";
    return `<button
    class="
      rounded-r-lg
      text-xs
      h-10
      font-bold
      py-2
      px-4
      btn-blue
      w-20
    "
    type="button"
    id="${this.id}-primary-button"
  >
    ${this.primary_button_label}
  </button>`;
  }

  _template_secondary_button() {
    if (this.secondary_callback == null) return "";
    return `<button
    class="
      text-xs
      h-10
      font-bold
      py-2
      px-4
      btn-gray
      w-20
    "
    type="button"
    id="${this.id}-secondary-button"
  >
    ${this.secondary_button_label}
  </button>`;
  }

  _template() {
    return `
      <div id="${this.id}" class="px-2 pb-10">
      <div class="pb-2"><strong>${this.title}</strong></div>

      <div class="">
        <div
          class="
            relative
            flex flex-row
            h-10
            items-center
            border
            shadow
            rounded-lg
          "
        >
          <div class="relative w-full flex flex-row items-center">
            <input
              type="file"
              class="absolute opacity-0 w-full h-10"
              id="${this.id}-file"
              aria-describedby="${this.id}-file"
            />
            <label
              id="${this.id}-file-label"
              class="relative pl-4 w-full appearance-none text-gray-300 pointer-events-none"
              for="${this.id}-file"
              >browse...</label
            >
          </div>
          ${this._template_secondary_button()}
          ${this._template_primary_button()}
        </div>
      </div>
    </div>`;
    return `
    <div id = "${this.id}" class="px-2 pb-10">
      <div class="pb-2"><strong>${this.title}</strong></div>

      <div class="">
        <div class="flex flex-row w-full">
          <div flex h-full items-center>
            <input
              type="file"
              class="w-full h-20 pl-3 pr-8 text-center placeholder-gray-600 border rounded-lg focus:shadow-outline"
              id="${this.id}-file"
              aria-describedby="${this.id}-file"
            />
          </div>
        </div>
        <div class="flex flex-row w-full pb-4 content-center">
          <label
            id="${this.id}-file-label"
            class=" w-full"
            for="${this.id}-file"
            >None Chosen</label
          >

          <div class="input-group-append">
            <button
              class="btn btn-blue btn-blue:hover text-xs w-20 "
              type="button"
              id="${this.id}-apply-button"
            >
              Apply
            </button>
          </div>
        </div>
        <hr>
      </div>
    </div>


    `;

    return `
  <div id = "${this.id}" class="px-2">
    <h2>${this.title}</h2
    <div class="max-w-md mx-auto bg-white rounded-lg overflow-hidden md:max-w-lg">
        <div class="md:flex">
            <div class="w-full">
                <div class="p-3">
                    <div class="mb-2">
                        <div class="relative h-20 rounded-lg border-dashed border-2 border-gray-200 bg-white flex justify-center items-center hover:cursor-pointer">
                            <div class="absolute">
                                <div class="flex flex-col items-center "> <i class="fa fa-cloud-upload fa-3x text-gray-200"></i> <span class="block text-gray-400 font-normal">Drag files here</span> <span class="block text-gray-400 font-normal">or</span> <span class="block text-blue-400 font-normal">Browse files</span>
                                </div>
                            </div> <input type="file" class="h-full w-full opacity-0" name="">
                        </div>
                        <div class="flex justify-between items-center text-gray-400"> <span>Accepted file type:.doc only</span> </div>
                    </div>
                    <div class="mt-3 text-center pb-3"> <button class="w-full h-6 text-md w-20 bg-blue-600 rounded text-white hover:bg-blue-700">Load</button> </div>
                </div>
            </div>
        </div>
    </div>
  </div>
`;
  }

  loadFileAsJson(evt, fxn) {
    let file = evt.target.files[0]; // FileList object
    // console.log(file);
    // Only process csv or json files.
    if (!file.type.match("csv|excel|json")) {
      alert("csv or json please");
      return;
    }

    let self = this;
    // let _fxn = fxn.bind(self);
    let reader = new FileReader();

    // Closure to capture the file information.
    reader.onload = (function (theFile) {
      return function (e) {
        let data;
        if (true) {
          if (theFile.type.match("csv|excel")) {
            data = d3.csvParse(e.target.result);
          } else if (theFile.type.match("json")) {
            data = JSON.parse(e.target.result);
          }

          data = Array.isArray(data)
            ? data.map((d) => util.cleanObject(d))
            : data;
          // console.log("data:", data);
          // _fxn(data);
          self.data = data;
          // console.log(evt.target.value);
          // console.log(evt.target);
          evt.target.value = "";
        }
      };
    })(file);

    reader.readAsText(file);
  }

  _render() {
    let self = this;
    self.element = d3.select(`#${self.parent_id}-content`).append("div");
    self.element.html(self._template());

    self.primary_button = self.element.select(`#${this.id}-primary-button`);
    self.primary_button.on("click", () => {
      self.data_callback.bind(self)(self.data);
      self.primary_callback.bind(self)();
      let label = self.element.select(`#${this.id} label`);
    });

    self.secondary_button = self.element.select(`#${this.id}-secondary-button`);
    self.secondary_button.on("click", () => {
      self.data_callback.bind(self)(self.data);
      self.secondary_callback.bind(self)();
      let label = self.element.select(`#${this.id} label`);
    });

    self.input = self.element.select(`#${this.id} input`);
    self.input.on("change", (e) => {
      self.loadFileAsJson.bind(self)(e); //, ;
      let label = self.element.select(`#${this.id} label`);
      label.text(e.target.files[0].name);
      label.classed("font-bold", true);
      let label_node = label.node();
      label_node.className = label_node.className.replace(
        /\btext-gray-.+?\b/g,
        ""
      );
      label_node.classList["add"]("text-gray-700");
    });

    return;
  }
}

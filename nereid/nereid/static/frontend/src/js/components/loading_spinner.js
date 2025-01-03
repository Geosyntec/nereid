import Component from "./base/component.js";
import store from "../lib/state.js";
import d3 from "../lib/d3.js";

class LoadingSpinner extends Component {
  constructor(options) {
    super({ store, id: options.id });
  }
  enter() {
    let self = this;
    self.element.classed("pointer-events-none", false);

    let current;
    current = self.element.select(".background-overlay").node();
    current.classList.remove("opacity-0");
    current.classList.add("duration-300", "opacity-40");

    current = self.element.select(".modal-main").node();
    current.classList.remove("opacity-0", "translate-y-4");
    current.classList.add("opacity-100", "translate-y-0");
  }
  exit() {
    let self = this;
    let ele = self.element;
    self.element.classed("pointer-events-none", true);

    let current;

    current = ele.select(".background-overlay").node();
    current.classList.remove("opacity-40", "duration-300");
    current.classList.add("opacity-0");

    current = ele.select(".modal-main").node();
    current.classList.remove("opacity-100", "translate-y-0");
    current.classList.add("opacity-0", "translate-y-4");
  }
  _base_template() {
    return `
<div class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
  <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
    <!--
      Background overlay, show/hide based on modal state.

      Entering: "ease-out duration-300"
        From: "opacity-0"
        To: "opacity-100"
      Leaving: "ease-in duration-200"
        From: "opacity-100"
        To: "opacity-0"
    -->
    <div class="background-overlay fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity opacity-0" aria-hidden="true"></div>

    <!-- This element is to trick the browser into centering the modal contents. -->
    <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

    <!--
      Modal panel, show/hide based on modal state.

      Entering: "ease-out duration-300"
        From: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
        To: "opacity-100 translate-y-0 sm:scale-100"
      Leaving: "ease-in duration-200"
        From: "opacity-100 translate-y-0 sm:scale-100"
        To: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
    -->
    <div class="modal-main inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all opacity-0 translate-y-4 sm:py-8 sm:align-middle sm:max-w-lg sm:w-full">
      <div id="spinner-content">
        <div class=" flex justify-center items-center gap-4 align-middle">
          <span class="font-bold">Loading...</span>
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    </div>
  </div>
</div>
    `;
  }
  _render() {
    let self = this;
    self.element = d3
      .select(`#${this.parent_id}`)
      .append("div")
      .attr("id", self.id);
    self.element.html(self._base_template());

    self.store.events.subscribe("Waiting", ({ waiting }) => {
      if (waiting > 0) self.enter();
    });
    self.store.events.subscribe("Waiting", ({ waiting }) => {
      if (waiting === 0) self.exit();
    });

    // d3.select(self.parent);
  }
}

export const spinner = new LoadingSpinner({ id: "spinner-popup" });

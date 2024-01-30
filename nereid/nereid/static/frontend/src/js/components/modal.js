import Component from "./base/component.js";
import store from "../lib/state.js";

export class Modal extends Component {
  constructor(options) {
    super({ store, id: options.id });
  }
  enter(modal_content) {
    let self = this;

    self.element.classed("pointer-events-none", false);
    let ele = self.element.select(`#modal-content`);
    ele.html(self._content_template(modal_content));
    ele.selectAll(`button`).on("click", this.exit.bind(self));

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

  _content_template(opts) {
    if (!opts) {
      opts = {};
    }
    let fmt = {
      icon: `
        <!-- Heroicon name: outline/exclamation -->
        <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      `,
    };
    switch (opts.alert_type) {
      case "error":
        fmt.bgcolor = "bg-red-300";
        fmt.button_style = "bg-red-600 hover:bg-red-700  focus:ring-red-500";
        fmt.icon_color = "text-red-600";
        fmt.icon_bgcolor = "bg-red-100";

        break;
      case "success":
        fmt.bgcolor = "bg-green-300";
        fmt.button_style =
          "bg-green-600 hover:bg-green-700  focus:ring-green-500";
        fmt.icon_color = "text-green-600";
        fmt.icon_bgcolor = "bg-green-100";
        fmt.icon = `
          <!-- Heroicon name: check -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        `;

        break;
      default:
        fmt.bgcolor = "bg-yellow-300";
        fmt.button_style =
          "bg-yellow-600 hover:bg-yellow-700  focus:ring-yellow-500";
        fmt.icon_color = "text-yellow-600";
        fmt.icon_bgcolor = "bg-yellow-100";
    }

    return `
    <div class="flex w-full h-8 ${fmt.bgcolor}"></div>
    <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 max-h-96 overflow-auto">

      <div class="sm:flex sm:items-start">
        <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full ${
          fmt.icon_bgcolor
        } sm:mx-0 sm:h-10 sm:w-10">
          <div class="icon ${fmt.icon_color}">
            ${fmt.icon}
          </div>
        </div>
        <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
          <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
            ${opts?.title || "Alert"}
          </h3>
          <div class="mt-2">
            <p class="text-sm text-gray-500">
              ${opts?.msg || ""}
            </p>
          </div>
        </div>
      </div>
    </div>
    <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
      <button type="button" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2  text-base font-medium text-white ${
        fmt.button_style
      } focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm">
        ${opts?.button_text || "Dismiss"}
      </button>
    </div>
    `;
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
    <div class="modal-main inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all opacity-0 translate-y-4 sm:my-8 sm:align-middle sm:max-w-xl sm:w-full">
      <div id="modal-content"></div>
    </div>
  </div>
</div>
    `;
  }
  _render() {
    let self = this;

    self.element = d3
      .select("body")
      .append("div")
      .attr("id", self.id)
      .classed("pointer-events-none", true);
    self.element.html(self._base_template());
    self.store.events.subscribe("raiseModal", ({ modal_content }) =>
      self.enter(modal_content)
    );
    self.exit();
  }
}

export const modal = new Modal({ id: "modal-popup" });

import Component from "./component.js";
import d3 from "../../lib/d3.js";
import store from "../../lib/state.js";

export class DrawerBase extends Component {
  constructor(options) {
    super({ store, id: options.id, children: options.children });
    let self = this;
    self.title = options.title;
    self.options = options;
  }

  enter() {
    let self = this;
    let ele = self.element;
    self.transition_direction = "entering";

    // self.element.select(`#${this.id}-content`).classed("hidden", false);
    let current;
    current = ele.select(".drawer-overlay").node();
    current.className = current.className.replace(/\bopacity-.+?\b/g, "");
    current.classList["add"]("opacity-40");

    current = ele.select(".drawer-panel").node();
    current.className = current.className.replace(/\btranslate-x-.+?\b/g, "");
    current.classList["add"]("translate-x-0");
    current.className = current.className.replace(/\bopacity-.+?\b/g, "");
    current.classList["add"]("opacity-100");
    // current.ontransitionend = () => {
    //   self.element.select(`#${this.id}-content`).classed("hidden", false);

    // };
    if (self?.options?.enter_callback) {
      self.options.enter_callback();
    }
  }

  exit() {
    let self = this;
    let ele = document.querySelector(`#${this.id}`);

    let current;
    self.transition_direction = "exiting";

    current = ele.querySelector(".drawer-overlay");
    current.className = current.className.replace(/\bopacity-.+?\b/g, "");
    current.classList["add"]("opacity-0");

    current = ele.querySelector(".drawer-panel");
    current.className = current.className.replace(/\btranslate-x-.+?\b/g, "");
    current.classList["add"]("translate-x-full");
    // current.ontransitionend = () => {
    //   let hidden = false;
    //   if (self.transition_direction === "exiting") {
    //     hidden = true;
    //   }
    //   self.element.select(`#${this.id}-content`).classed("hidden", hidden);
    // };

    if (self?.options?.exit_callback) {
      self.options.exit_callback();
    }
  }

  _template() {
    return `
    <div class="pointer-events-none">
      <!-- This example requires Tailwind CSS v2.0+ -->
      <div
        class="fixed inset-0 overflow-hidden"
        aria-labelledby="slide-over-title"
        role="dialog"
        aria-modal="true"
      >
        <div class="absolute inset-0 overflow-hidden">
          <!--
      Background overlay, show/hide based on slide-over state.

      Entering: "ease-in-out duration-500"
        From: "opacity-0"
        To: "opacity-100"
      Leaving: "ease-in-out duration-500"
        From: "opacity-100"
        To: "opacity-0"
    -->
          <div
            class="
              drawer-overlay
              absolute
              inset-0
              bg-gray-800 bg-opacity-50
              transition-opacity
              ease-in-out
              duration-500
              opacity-0
            "
            aria-hidden="true"
          ></div>

          <div
            class="
              drawer-panel
              fixed
              inset-y-0
              right-0
              pl-2
              max-w-full
              max-h-screen
              flex
              pointer-events-auto
              transition-transform
              ease-in-out
              duration-500
              translate-x-full
            "
          >
            <!--
        Slide-over panel, show/hide based on slide-over state.

        Entering: "transform transition ease-in-out duration-500 sm:duration-700"
          From: "translate-x-full"
          To: "translate-x-0"
        Leaving: "transform transition ease-in-out duration-500 sm:duration-700"
          From: "translate-x-0"
          To: "translate-x-full"
      -->
            <div class="relative w-screen max-w-md lg:max-w-lg">
              <!--
          Close button, show/hide based on slide-over state.

          Entering: "ease-in-out duration-500"
            From: "opacity-0"
            To: "opacity-100"
          Leaving: "ease-in-out duration-500"
            From: "opacity-100"
            To: "opacity-0"
        -->
              <!-- <div
                class="
                  absolute
                  top-0
                  left-0
                  -ml-8
                  pt-4
                  pr-2
                  flex
                  sm:-ml-10 sm:pr-4
                "
              > -->
              <div
                class="absolute top-0 left-0 pt-4 pl-4 flex"
              >
                <button
                  id="${this.id}-close-button"
                  class="
                    rounded-md
                    text-gray-300
                    hover:text-black
                    focus:outline-none focus:ring-2 focus:ring-black
                  "
                >
                  <span class="sr-only">Close panel</span>
                  <!-- Heroicon name: outline/x -->
                  <svg
                    class="h-6 w-6"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              <div
                class="
                  h-full
                  flex flex-col
                  py-6
                  pl-10
                  pr-6
                  bg-white
                  shadow-xl
                  overflow-y-scroll
                "
              >
                <div class="px-0 sm:px-2">
                  <h2
                    class="text-lg font-medium text-gray-900"
                    id="slide-over-title"
                  >
                    ${this.title}
                  </h2>
                </div>
                <div class="mt-6 relative flex-1 w-full px-0 sm:px-2">
                  <!-- Replace with your content -->
                  <div id="${this.id}-content">
                    <div class="absolute inset-0 px-4 sm:px-6 pointer-events-none">
                      <div
                        class="h-full border-2 border-dashed border-gray-200"
                        aria-hidden="true"
                      ></div>
                    </div>
                  </div>
                  <!-- /End replace -->
                </div>
              </div>
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
      .select(`#${this.id}`)
      .append("div")
      .classed("drawer-container", true);
    self.element.html(this._template());

    self.element
      .select(`#${this.id}-close-button`)
      .on("click", this.exit.bind(this));

    if (this?.children?.length > 0) {
      self.element.select(`#${this.id}-content`).html("");
    }

    let current = self.element
      .select(".drawer-container")
      .classed("hidden", true);
    self.exit();
    current.classed("hidden", false);
  }
}

import Component from "./component.js";
import d3 from "../../lib/d3.js";
import store from "../../lib/state.js";

export class ToggleBase extends Component {
  constructor(options) {
    super({ store, id: options.id });
    this.parent_id = options.parent_id;
    this.text = options.text;
    this.callback = options.callback;
    this.isActive = options.isActive;
    this.scale = options.scale || "scale-100";
    this.button;
    this._class = options.class_string || "";
  }

  get class() {
    return this._class;
  }

  _render() {
    let self = this;
    self.toggle = d3.select(`#${self.parent_id}`).append("div");
    self.toggle.html(`
    <!-- Toggle ${self.id} -->
    <div class="transform ${self.scale} m-0 sm:m-2 py-2">
      <label for="${self.id}-toggle" class="flex flex-col sm:flex-row items-center align-center cursor-pointer min-w-0">
        <!-- toggle -->
        <div class="relative">
          <!-- input -->
          <input type="checkbox" id="${self.id}-toggle" class="sr-only" />
          <!-- line -->
          <div class="block bg-gray-600 w-10 h-6 rounded-full"></div>
          <!-- dot -->
          <div
            class="
              dot
              absolute
              left-1
              top-1
              bg-white
              w-4
              h-4
              rounded-full
              transition
            "
          ></div>
        </div>
        <!-- label -->
        <div class="text-center sm:ml-3 text-gray-700 font-medium text-xs sm:text-sm">${self.text}</div>
      </label>
    </div>
    `);

    self.toggle
      .select("input[type=checkbox]")
      .property("checked", self.isActive);
    self.toggle.select("input").on("change", self.callback.bind(self));
  }
}

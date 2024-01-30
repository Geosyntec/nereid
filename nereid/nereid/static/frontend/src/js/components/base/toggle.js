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
    <div class="m-2 transform ${self.scale}">
      <label for="${self.id}-toggle" class="flex items-center cursor-pointer">
        <!-- toggle -->
        <div class="relative">
          <!-- input -->
          <input type="checkbox" id="${self.id}-toggle" class="sr-only" />
          <!-- line -->
          <div class="block bg-gray-600 w-14 h-8 rounded-full"></div>
          <!-- dot -->
          <div
            class="
              dot
              absolute
              left-1
              top-1
              bg-white
              w-6
              h-6
              rounded-full
              transition
            "
          ></div>
        </div>
        <!-- label -->
        <div class="ml-3 text-gray-700 font-medium">${self.text}</div>
      </label>
    </div>
    `);

    self.toggle
      .select("input[type=checkbox]")
      .property("checked", self.isActive);
    self.toggle.select("input").on("change", self.callback.bind(self));
  }
}

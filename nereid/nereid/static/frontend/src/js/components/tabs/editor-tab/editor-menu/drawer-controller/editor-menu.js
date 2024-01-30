import Component from "../../../../base/component.js";
import d3 from "../../../../../lib/d3.js";
import store from "../../../../../lib/state.js";

export default class EditorMenu extends Component {
  constructor(options) {
    super({ store, id: options.id, children: options.children });
  }

  _template() {
    return `
  <div class="absolute pr-12 top-0 right-0">
    <div class="">
      <div id="${this.id}-button-container"
        class="
          menu
          flex flex-col
          items-center
          w-16
          py-3
          gap-y-2
          shadow-xl
          bg-gray-50
          rounded-lg
        "
      >
      </div>
    </div>
  </div>
  `;
  }

  _render() {
    this.element = d3.select(`#${this.id}`);
    this.element.html(this._template());
  }
}

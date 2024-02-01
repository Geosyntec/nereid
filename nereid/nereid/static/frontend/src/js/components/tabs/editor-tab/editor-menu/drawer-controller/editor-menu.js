import Component from "../../../../base/component.js";
import d3 from "../../../../../lib/d3.js";
import store from "../../../../../lib/state.js";

export default class EditorMenu extends Component {
  constructor(options) {
    super({ store, id: options.id, children: options.children });
  }

  _template() {
    return `
  <div
    class="absolute top-0 right-0 pointer-events-none
      mr-1 sm:mr-3
      mt-1 sm:mt-3
      "
    >
    <div class="pointer-events-auto">
      <div id="${this.id}-button-container"
        class="
          menu
          flex
          flex-row sm:flex-col
          items-center
          p-1 sm:p-3
          gap-2
          rounded-lg
          shadow-xl
          bg-white
          bg-opacity-25 sm:bg-opacity-75
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

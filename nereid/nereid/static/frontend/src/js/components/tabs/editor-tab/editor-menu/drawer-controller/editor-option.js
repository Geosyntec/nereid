import Component from "../../../../base/component.js";
import d3 from "../../../../../lib/d3.js";
import store from "../../../../../lib/state.js";

export default class EditorMenuOption extends Component {
  constructor(options) {
    super({ store });
    let self = this;
    self.id = options.id;
    self.title = options.title;
    self.icon = options.icon;
    self.callback = options.callback;
  }

  _template() {
    return `
  <button
    id="${this.id}-button"
    title="${this.title}"
    class="
      rounded-md
      text-gray-600
      hover:text-gray-300
      focus:outline-none focus:ring-2 focus:ring-gray-300
    "
  >
    <span class="sr-only">${this.title}</span>
    ${this.icon}

  </button>`;
  }

  _render() {
    let self = this;
    let parent_container = d3
      .select(`#${this.parent_id}-button-container`)
      .append("div")
      .classed("flex", true);
    // this.button = parent_container.append("div");
    // this.button.html(this._template());
    let html = parent_container.html();
    html += this._template();
    parent_container.html(html);

    this.button = parent_container.select(`button#${this.id}-button`);

    this.button.on(`click`, self.callback.bind(self));
  }
}

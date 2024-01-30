import d3 from "../../lib/d3.js";
import Store from "../../lib/store.js";

export default class Component {
  constructor(props = {}) {
    let self = this;
    this.element;
    this.element_string;
    this.id;

    // We're setting a render function as the one set by whatever inherits this base
    // class or setting it to an empty by default. This is so nothing breaks if someone
    // forgets to set it.
    this._render = this._render || props._render || function () {};

    // If there's a store passed in, subscribe to the state change
    if (props.store instanceof Store) {
      self.store = props.store;
      //   props.store.events.subscribe("stateChange", () => self.render());
    }

    if (props.hasOwnProperty("events") && props.store instanceof Store) {
      props.events.forEach((event) =>
        props.store.events.subscribe(event, () => self.render())
      );
    }

    // Store the HTML element to attach the render to if set
    if (props.hasOwnProperty("element")) {
      self.element = props.element;
    }

    if (props.hasOwnProperty("element_string")) {
      self.element_string = props.element_string;
      self.element = d3.select(element);
    }

    if (props.hasOwnProperty("id")) {
      self.id = props.id;
      self.element_string = `#${self.id}`;
      self.element = d3.select(self.element_string);
    }

    if (props.hasOwnProperty("children")) {
      self.children = props.children;
    }
  }

  render() {
    let self = this;
    this._render();
    if (this?.children) {
      this.children.forEach((child) => {
        if (!child?.parent_id) {
          child.parent_id = self.id;
        }

        child.render();
      });
    }
  }
}

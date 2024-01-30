import store from "./state.js";

export default class PubSub {
  constructor() {
    this.events = {};
  }

  /**
   * Either create a new event instance for passed `event` name
   * or push a new callback into the existing collection
   *
   * @param {string} event
   * @param {function} callback
   * @returns {boolean}
   * @memberof PubSub
   */
  subscribe(event, callback) {
    let self = this;

    // If there's not already an event with this name set in our collection
    // go ahead and create a new one and set it with an empty array, so we don't
    // have to type check it later down-the-line
    if (!self.events.hasOwnProperty(event)) {
      self.events[event] = [];
    }

    // We know we've got an array for this event, so push our callback in there with no fuss
    self.events[event].push(callback);
    return true;
  }

  /**
   * If the passed event has callbacks attached to it, loop through each one
   * and call it
   *
   * @param {string} event
   * @param {object} [data={}]
   * @returns {boolean}
   * @memberof PubSub
   */
  publish(event, data = {}) {
    let self = this;
    if (store.state.DEBUG) console.log("published event: ", event);

    // There's no event to publish to, so bail out
    if (!self.events.hasOwnProperty(event)) {
      if (store.state.DEBUG) console.log(`no subscribers for event ${event}`);
      self.events[event] = [];
      return false;
    }

    // Get each subscription and call its callback with the passed data
    self.events[event].map((callback) => callback(data));
    return true;
  }
}

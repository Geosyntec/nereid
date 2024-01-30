import store from "../../lib/state.js";
import * as util from "../../lib/util";

export class TabSystem {
  constructor(namespace) {
    this.store = store;
    this.namespace = namespace;
    this.registry_underline = {
      0: "translate-x-0",
      1: "translate-x-full",
      2: "translate-x-double",
      3: "translate-x-triple",
      4: "translate-x-quad",
      5: "translate-x-pent",
      6: "translate-x-sext",
      7: "translate-x-sept",
      8: "translate-x-octa",
    };

    this.registry = {};
  }

  init() {
    let self = this;
    let namespace = this.namespace;

    document.querySelectorAll(`${namespace}`).forEach((tabMenu) => {
      Array.from(tabMenu.children).forEach((child, ind) => {
        self.registry[child.dataset.target] = self.registry_underline[ind];
        if (child.dataset.target) {
          child.addEventListener(`click`, () => {
            self.store.dispatch("changedTab", {
              current_tab: child.dataset.target,
            });
            self.toggle.bind(self)(child.dataset.target);
          });
          if (child.className.includes("active")) {
            self.toggle.bind(self)(child.dataset.target);
          }
        }
      });
    });

    self.store.events.subscribe("changedTab", ({ current_tab }) => {
      self.toggle(current_tab);
    });

    let current_tab = util.get(self.store, "state.current_tab");
    if (current_tab) self.toggle(current_tab);
  }
  toggle(targetId) {
    let self = this;
    let namespace = this.namespace;

    let slider = document.querySelector(`${namespace} .tab-slider`);
    slider.className = slider.className.replace(/\btranslate-x-.+?\b/g, "");
    slider.classList["add"](self.registry[targetId]);

    document
      .querySelectorAll(`${namespace} .tab-content`)
      .forEach((contentElement) => {
        contentElement.classList[
          contentElement.id === targetId ? "remove" : "add"
        ]("hidden");

        document
          .querySelector(`[data-target="${contentElement.id}"]`)
          .classList.toggle("active", contentElement.id === targetId);
      });
  }
}

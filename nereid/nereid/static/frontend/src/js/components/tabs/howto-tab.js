import Component from "../base/component.js";
import store from "../../lib/state.js";
import d3 from "../../lib/d3.js";
import * as util from "../../lib/util.js";

export class HowTab extends Component {
  constructor(options) {
    super({ store, id: options.id });
  }
  _template() {
    return `
    <div class="markdown">
      <div class="flex justify-center pt-10 px-24">
        <div class="markdown_content prose prose-lg md:prose-2xl">
          how to coming soon...
        </div>
      </div>
    </div>
    `;
  }
  async fetch_page() {
    let self = this;
    let url = `${store.state.nereid_host}` + "/static/pages/how_to";
    util.incr_waiting();
    fetch(url, { method: "GET" })
      .then((resp) => {
        if (resp.status_code === 200) {
          return resp.text().then(function (text) {
            self.element.select(".markdown_content").html(text);
          });
        }
      })
      .finally(util.decr_waiting);
  }

  _render() {
    let self = this;
    self.element = d3
      .select(`#${self.id}`)
      .classed("relative flex flex-col justify-center", true)
      .html(self._template());

    self.fetch_page();
  }
}

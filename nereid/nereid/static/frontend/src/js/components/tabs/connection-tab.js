import Component from "../base/component.js";
import { getConfig } from "../../lib/nereid-api.js";
import store from "../../lib/state.js";
import * as util from "../../lib/util.js";
import d3 from "../../lib/d3.js";

// export class ConnTab extends Component {
//   constructor(options) {
//     super({ store, id: options.id });
//   }
//   async _update(value) {
//     let self = this;
//     const cfg = await getConfig(value);
//     self.store.dispatch("updateConfig", cfg);
//   }
//   _template() {
//     return `
//     <div class="flex w-full justify-center pt-10">
//       <form class="config-form" id="config-form">
//         <div class="grid grid-cols-3 gap-4 justify-start items-center">
//           <label class="font-medium" for="nereid-host">Nereid Host</label>
//           <input
//             class="border-2 rounded-md px-2 py-1 col-span-2"
//             type="text"
//             name="nereid_host"
//             id="nereid-host"
//             value=""
//           />

//           <label class="font-medium" for="nereid-state">State</label>
//           <input
//               class="border-2 rounded-md px-2 py-1 col-span-2"
//               type="text"
//               name="nereid_state"
//               id="nereid-state"
//               value="ca"
//             />
//           <label class="font-medium" for="nereid-region">Region</label>
//           <input
//               class="border-2 rounded-md px-2 py-1 col-span-2"
//               type="text"
//               name="nereid_region"
//               id="nereid-region"
//               value="cosd"
//           />
//         </div>
//         <div class="flex justify-end py-4">
//           <button
//             type="submit"
//             class="btn btn-blue"
//           >
//             Refresh
//           </button>
//         </div>
//       </form>
//     </div>
//     `;
//   }
//   _render() {
//     let self = this;
//     let element = d3.select(`#${self.id}`).append("div").html(self._template());
//     let form = element
//       .select("form")
//       .attr("method", "get")
//       .on("submit", function (event) {
//         event.preventDefault();
//         const data = new FormData(event.target);
//         const value = util.cleanObject(Object.fromEntries(data.entries()));
//         // self.store.dispatch("updateConfig", value);
//         self._update(value);

//         // console.log("form submit", value);
//         return false;
//       });

//     let button = form.select("button");
//     button.node().click();
//   }
// }

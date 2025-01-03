var _e=Object.defineProperty;var he=(n,e,t)=>e in n?_e(n,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):n[e]=t;var M=(n,e,t)=>he(n,typeof e!="symbol"?e+"":e,t);import{j as ge,D as ye,s as be,a as ve,b as we,g as xe,c as ke,d as Se,e as $e,f as je,t as Oe,h as Te,z as Le}from"./d3-BnyQevZd.js";import{f as Z,t as Ee,F as W}from"./vendor-B7rdgAvP.js";(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const a of document.querySelectorAll('link[rel="modulepreload"]'))s(a);new MutationObserver(a=>{for(const r of a)if(r.type==="childList")for(const i of r.addedNodes)i.tagName==="LINK"&&i.rel==="modulepreload"&&s(i)}).observe(document,{childList:!0,subtree:!0});function t(a){const r={};return a.integrity&&(r.integrity=a.integrity),a.referrerPolicy&&(r.referrerPolicy=a.referrerPolicy),a.crossOrigin==="use-credentials"?r.credentials="include":a.crossOrigin==="anonymous"?r.credentials="omit":r.credentials="same-origin",r}function s(a){if(a.ep)return;a.ep=!0;const r=t(a);fetch(a.href,r)}})();class Me{constructor(){this.events={}}subscribe(e,t){let s=this;return s.events.hasOwnProperty(e)||(s.events[e]=[]),s.events[e].push(t),!0}publish(e,t={}){let s=this;return _.state.DEBUG&&console.log("published event: ",e),s.events.hasOwnProperty(e)?(s.events[e].map(a=>a(t)),!0):(_.state.DEBUG&&console.log(`no subscribers for event ${e}`),s.events[e]=[],!1)}}class q{constructor(e){let t=this;t.actions={},t.mutations={},t.state={},t.status="resting",t.events=new Me,t.state=new Proxy(e.state||{},{set:function(s,a,r){return s[a]=r,_.state.DEBUG&&console.log(`stateChange: ${a}`,r),t.status!=="mutation"&&(_.state.DEBUG&&console.warn(`You should use a mutation to set ${a}`),t.events.publish("stateChange",t.state)),!0}})}dispatch(e,t){let s=this;return typeof s.actions[e]!="function"&&(_.state.DEBUG&&console.log(`Action "${e} doesn't exist.`),s.actions[e]=(a,r)=>{a.commit(e,r)}),_.state.DEBUG&&console.groupCollapsed(`ACTION: ${e}`),s.status="action",s.actions[e](s,t),_.state.DEBUG&&console.groupEnd(),!0}commit(e,t){let s=this;typeof s.mutations[e]!="function"&&(_.state.DEBUG&&console.log(`Mutation "${e}" doesn't exist`),s.mutations[e]=(r,i)=>i),s.status="mutation";let a=s.mutations[e](s.state,t);return s.state=Object.assign(s.state,a),s.events.publish("stateChange",s.state),s.events.publish(e,s.state),s.status="resting",!0}}const Ne={DEBUG:!1,current_tab:"editor-tab",config:{},scenario_name:"New Scenario",nereid_host:"",nereid_api_latest:"/api/v1",nereid_state:"state",nereid_region:"region",facility_types:[],facility_type_map:{},initialScale:1<<20,initialCenter:[-116.9337,32.74337],staged_changes:{},default_nodesize:20,max_graph_size:100,map_mode:!0,show_states:!0,graph_edit_mode:!0,show_info_tooltip:!0,treatment_facility_fields:{state:{region:{ignored:["is_online","offline_diversion_rate_cfs","eliminate_all_dry_weather_flow_override"],disabled:["facility_type"]}},ca:{cosd:{ignored:["is_online","offline_diversion_rate_cfs","eliminate_all_dry_weather_flow_override"],disabled:["facility_type","ref_data_key","design_storm_depth_inches"]},soc:{ignored:["is_online","offline_diversion_rate_cfs","eliminate_all_dry_weather_flow_override"],disabled:["facility_type"]}}},node_types:{land_surface:{title:"Land Surface",color:"limegreen"},treatment_facility:{title:"Treatment Facility",color:"steelblue"},treatment_site:{title:"Treatment Site",color:"orangered",disabled:!0},none:{title:"None",color:"dimgrey"}},default_graph:{nodes:[{id:"0",node_type:"treatment_facility"},{id:"1",node_type:"land_surface"}],edges:[{source:"1",target:"0"}]}},_=new q({state:Ne}),Ce=()=>x((p(_,"state.graph.nodes")||[]).filter(n=>(n==null?void 0:n.node_type)==="land_surface"&&(n==null?void 0:n.data)).map(n=>n==null?void 0:n.data)),K=()=>x((p(_,"state.graph.nodes")||[]).filter(n=>(n==null?void 0:n.node_type)==="treatment_facility"&&(n==null?void 0:n.data)).map(n=>n==null?void 0:n.data)),De=()=>x((p(_,"state.graph.nodes")||[]).filter(n=>(n==null?void 0:n.node_type)==="treatment_site"&&(n==null?void 0:n.data)).map(n=>n==null?void 0:n.data)),ee=()=>({edges:(p(_,"state.graph.edges")||[]).map(e=>({source:e.source.id.toString(),target:e.target.id.toString()})),directed:!0,multigraph:!0}),Ae=()=>({graph:ee(),land_surfaces:Ce()||[],treatment_facilities:K()||[],treatment_sites:De()||[]}),T={getOpenApi:async n=>{let e;try{return e=await N(`${n}/openapi.json`),e}catch(t){console.error(t)}},getConfig:async(n,e,t)=>{var a,r;let s;try{return s=await N(`${n}/config?state=${e}&region=${t}`),(r=(a=s==null?void 0:s.detail)==null?void 0:a.toLowerCase())!=null&&r.includes("no config")&&console.warn(`no config for ${e} ${t}`),s}catch(i){console.error(i)}},getReferenceData:async(n,e,t,s,a)=>{let r;try{return r=await N(`${n}${e}/reference_data_file?state=${t}&region=${s}&filename=${a}`),r}catch(i){console.error(i)}},getTaskData:async(n,e,t)=>{let s;try{return s=await N(`${n}${e}/task/${t}`),s}catch(a){console.error(a)}},postValidateNetwork:async(n,e,t,s,a)=>{var c;let r=`${n}${e}/network/validate?state=${t}&region=${s}`,i;try{return i=await I(r,a),(c=i==null?void 0:i.data)!=null&&c.isvalid?{title:"Validation Succeeded",msg:"Success",alert_type:"success"}:{title:"Validation Errors",msg:`<pre>${JSON.stringify(i==null?void 0:i.data,void 0,2)}</pre>`,alert_type:"error"}}catch(u){return{title:"Validation Error",msg:`<pre>${JSON.stringify(u,void 0,2)}</pre>`,alert_type:"error"}}},postValidateTreatmentFacilities:async(n,e,t,s,a)=>{var c,u;let r=`${n}${e}/treatment_facility/validate?state=${t}&region=${s}`,i;try{i=await I(r,a);let m=[];for(let l of(c=i==null?void 0:i.data)==null?void 0:c.treatment_facilities)l!=null&&l.errors&&m.push(l==null?void 0:l.errors.replace(/\n/g," "));for(let l of(u=i==null?void 0:i.data)==null?void 0:u.errors)l.toLowerCase().substring(0,6).includes("error")&&m.push(l);return m.length==0?{title:"Validation Succeeded",msg:"",alert_type:"success"}:{title:"Validation Errors",msg:`<pre>${JSON.stringify(m,void 0,2)}</pre>`,alert_type:"error"}}catch(m){return{title:"Validation Error",msg:`<pre>${JSON.stringify(m,void 0,2)}</pre>`,alert_type:"error"}}},postSolveWatershed:async(n,e,t,s,a)=>{var c,u,m,l;let r=`${n}${e}/watershed/solve?state=${t}&region=${s}`,i;try{if(i=await I(r,a),((u=(c=i==null?void 0:i.data)==null?void 0:c.errors)==null?void 0:u.length)==0)return i;if((i==null?void 0:i.data)==null&["pending","started"].includes((m=i==null?void 0:i.status)==null?void 0:m.toLowerCase())&(i==null?void 0:i.task_id)!=null)return i=await de({fn:()=>T.getTaskData(n,e,i.task_id),validate:o=>(o==null?void 0:o.data)!=null,interval_milli:333,maxAttempts:20}),i}catch(o){console.error(o)}return console.error(i,(l=i==null?void 0:i.data)==null?void 0:l.errors),i}},te=async n=>{let{nereid_host:e,nereid_api_latest:t,nereid_state:s,nereid_region:a}=p(_,"state"),r;try{r=await T.getReferenceData(e,t,s,a,n)}catch(i){console.error(i)}return r},se=async()=>{let n=ee(),{nereid_host:e,nereid_api_latest:t,nereid_state:s,nereid_region:a}=p(_,"state"),r;try{r=await T.postValidateNetwork(e,t,s,a,n)}catch(i){console.error(i)}return r},ae=async()=>{let n={treatment_facilities:K()},{nereid_host:e,nereid_api_latest:t,nereid_state:s,nereid_region:a}=p(_,"state"),r;try{r=await T.postValidateTreatmentFacilities(e,t,s,a,n)}catch(i){console.error(i)}return r},re=async()=>{let n=Ae(),{nereid_host:e,nereid_api_latest:t,nereid_state:s,nereid_region:a}=p(_,"state"),r;try{r=await T.postSolveWatershed(e,t,s,a,n)}catch(i){console.error(i)}return r};function ne(n,e){for(let t in n)if(typeof n[t]=="object"&&n[t]!==null)ne(n[t],e);else if(t=="$ref"){let s=n[t].split("/").slice(-1).pop();s&&(delete n.$ref,n=Object.assign(n,e[s]))}}const ie=async({nereid_host:n,nereid_state:e,nereid_region:t})=>{n||(n=window.location.origin);const s=await T.getOpenApi(n),a=await T.getConfig(n,e,t),r=w(s.components.schemas);for(let o in r)ne(r[o],r);const i=a.api_recognize.treatment_facility.facility_type,c={};for(const[o,d]of Object.entries(i))c[o]=d.validator;const u={};for(const[o,d]of Object.entries(i))if(d!=null&&d.alias)for(let f of d==null?void 0:d.alias)u[f]=o;else u[o]=o;const m={};for(const[o,d]of Object.entries(i))m[(d==null?void 0:d.label)||o]=o;const l=Object.keys(m);return{nereid_host:n,nereid_state:e,nereid_region:t,config:a,openapi:s,schema:r,facility_types:l,facility_type_map:c,facility_alias_map:u,facility_label_map:m}},Re=Object.freeze(Object.defineProperty({__proto__:null,getConfig:ie,getReferenceData:te,solveWatershed:re,validateNetwork:se,validateTreatmentFacilities:ae},Symbol.toStringTag,{value:"Module"})),p=(n,e="")=>e.split(".").reduce((t,s)=>t==null?t:t[s],n),$=(n,e="")=>{let t=p(n,e);return t===void 0?!1:t};function le(n){let e="",t="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",s=t.length;for(let a=0;a<n;a++)e+=t.charAt(Math.floor(Math.random()*s));return e}const oe=(n,e=[],t=[])=>Object.keys(n).filter(a=>e.length?e.includes(a):!0).filter(a=>!t.includes(a)).reduce((a,r)=>({...a,[r]:n[r]}),{});function z(n){return Object.entries(n).filter(([e,t])=>t!=""&&t!=null).reduce((e,[t,s])=>({...e,[t]:s===Object(s)?z(s):s}),{})}function w(n){return JSON.parse(JSON.stringify(n))}function H(n){return n.length?n.reduce((e,t)=>e+t)/n.length:void 0}function x(n){return Array.isArray(n)?[].concat(...n.map(x)):n}const F=()=>{let n=(p(_,"state.waiting")||0)+1;_.dispatch("Waiting",{waiting:n})},P=()=>{let n=(p(_,"state.waiting")||0)-1;n<0&&(console.error("waiting counter is negative"),n=0),_.dispatch("Waiting",{waiting:n})};async function N(n){return console.debug("fetching with get",n),F(),await fetch(n,{method:"GET"}).then(t=>{if(console.debug("getJsonResponse response:",t),t.status==200)return t.json();if(t.status==422)return t.json();throw new Error("got back "+t.content)}).then(t=>(console.debug("getJsonResponse data returned:",t),t)).finally(P)}async function I(n,e){return console.debug("fetching with post",n,e),F(),await fetch(n,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(e)}).then(s=>{if(console.debug("postJsonResponse response:",s),s.status==200)return s.json();if(s.status==422)return s.json();throw new Error("got back "+s)}).then(s=>(console.debug("postJsonResponse data returned:",s),s)).finally(P)}const de=({fn:n,validate:e,interval_milli:t,maxAttempts:s})=>{console.debug("Start poll...");let a=0;const r=async(i,c)=>{console.debug("- poll");const u=await n();if(a++,console.debug(a,u),e(u))return i(u);if(s&&a===s)return c(new Error("Exceeded max attempts"));setTimeout(r,t,i,c)};return new Promise(r)};function G(n){var e,t,s,a,r,i;return i=n.data||null,i==null||!i.length?null:(a=n.columnDelimiter||",",r=n.lineDelimiter||`
`,s=n.keys||Object.keys(i[0]),e="",e+=s.map(c=>String(c).includes(",")?`"${c}"`:`${c}`).join(a),e+=r,i.forEach(function(c){t=0,s.forEach(function(u){t>0&&(e+=a);const m=String(c[u]);m.includes(",")?e+=`"${m}"`:e+=`${m}`,t++}),e+=r}),e)}const ce=async()=>{const n=new URLSearchParams(window.location.search);let{state:e,region:t,host:s}=Object.fromEntries(n.entries());const a=await ie({nereid_host:s,nereid_state:e||_.state.nereid_state,nereid_region:t||_.state.nereid_region});return _.dispatch("updateConfig",a),console.debug(a),!1},ze=Object.freeze(Object.defineProperty({__proto__:null,cleanObject:z,convertArrayOfObjectsToCSV:G,decr_waiting:P,deepCopy:w,filter:oe,flatten:x,get:p,getConfigFromUrlQueryParams:ce,getJsonResponse:N,getTruthy:$,incr_waiting:F,mean:H,poll:de,postJsonResponse:I,randomString:le},Symbol.toStringTag,{value:"Module"}));class C{constructor(e,t,s){this.nodes=e||[],this.edges=t||[],this.options=s||{},this.resolve_links(),_.dispatch("newGraph",{graph:this})}resolve_links(){let e=this;e.nodes=e.nodes.filter(a=>a.id!=null),this.edges.forEach(function(a){let r=a.source,i=a.target;a.source=e.nodes.find(c=>c.id===r),a.target=e.nodes.find(c=>c.id===i)});let t=this.options.width||600,s=this.options.height||400;this.nodes.forEach(function(a){a.x||(a.x=t/2+t/3*(Math.random()-1)),a.y||(a.y=s/2+s/3*(Math.random()-1))})}spliceLinksForNode(e){const t=this.edges.filter(s=>s.source.id===e||s.target.id===e);for(const s of t)this.edges.splice(this.edges.indexOf(s),1)}}function V(){let{nodes:n,edges:e,scenario_name:t}=w(p(_,"state.staged_changes"));new C(n,e),_.dispatch("clearStagedChanges",{staged_changes:{}}),t&&_.dispatch("updateScenarioName",{scenario_name:t})}function ue(){let n=w(p(_,"state.staged_changes.nodes")),e=w(p(_,"state.staged_changes.edges")),t=w(p(_,"state.graph.nodes")),s=w(p(_,"state.graph.edges")),a=[...s,...e].map(i=>{var c,u;return{source:((c=i.source)==null?void 0:c.id)||i.source,target:((u=i.target)==null?void 0:u.id)||i.target}}),r=n;for(let i of t)n.map(c=>c.id).includes(i.id)||r.push(i);new C(r,a),_.dispatch("clearStagedChanges",{staged_changes:{}})}const Fe=()=>{let{graph:n,scenario_name:e}=p(_,"state");sessionStorage.setItem("autosave_graph",JSON.stringify({graph:n,scenario_name:e}))},Pe=()=>{var t;let n=sessionStorage.getItem("autosave_graph"),e=w(p(_,"state.default_graph"));if(n){const{graph:s,scenario_name:a}=JSON.parse(n);sessionStorage.removeItem("autosave_graph"),((t=s==null?void 0:s.nodes)==null?void 0:t.length)>0?new C(s.nodes,s.edges.map(r=>({source:r.source.id,target:r.target.id}))):new C(e.nodes,e.edges),a&&_.dispatch("restoreScenarioName",{scenario_name:a})}else new C(e.nodes,e.edges)};window.addEventListener("beforeunload",Fe);window.addEventListener("load",n=>{const t=new URLSearchParams(window.location.search).get("tab");t&&_.dispatch("changedTab",{current_tab:t})});const h=Object.assign({json:ge,Delaunay:ye},be,ve,we,xe,ke,Se,$e,je,Oe,Te,Le);class v{constructor(e={}){let t=this;this.element,this.element_string,this.id,this._render=this._render||e._render||function(){(t==null?void 0:t.class)!=null&&h.select(t.element_string).classed(t.class,!0),console.debug(`component ${this.element_string||"unknown"} called without a render method`)},e.store instanceof q&&(t.store=e.store),e.hasOwnProperty("events")&&e.store instanceof q&&e.events.forEach(s=>e.store.events.subscribe(s,()=>t.render())),e.hasOwnProperty("element")&&(t.element=e.element),e.hasOwnProperty("element_string")&&(t.element_string=e.element_string,t.element=h.select(element)),e.hasOwnProperty("id")&&(t.id=e.id,t.element_string=`#${t.id}`,t.element=h.select(t.element_string)),e.hasOwnProperty("children")&&(t.children=e.children),e.hasOwnProperty("class")&&(t.class=e.class)}render(){let e=this;this._render(),this!=null&&this.children&&this.children.forEach(t=>{t!=null&&t.parent_id||(t.parent_id=e.id),t.render()})}}class Ie extends v{constructor(e){super({store:_,id:e.id})}enter(){let e=this;e.element.classed("pointer-events-none",!1);let t;t=e.element.select(".background-overlay").node(),t.classList.remove("opacity-0"),t.classList.add("duration-300","opacity-40"),t=e.element.select(".modal-main").node(),t.classList.remove("opacity-0","translate-y-4"),t.classList.add("opacity-100","translate-y-0")}exit(){let e=this,t=e.element;e.element.classed("pointer-events-none",!0);let s;s=t.select(".background-overlay").node(),s.classList.remove("opacity-40","duration-300"),s.classList.add("opacity-0"),s=t.select(".modal-main").node(),s.classList.remove("opacity-100","translate-y-0"),s.classList.add("opacity-0","translate-y-4")}_base_template(){return`
<div class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
  <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
    <!--
      Background overlay, show/hide based on modal state.

      Entering: "ease-out duration-300"
        From: "opacity-0"
        To: "opacity-100"
      Leaving: "ease-in duration-200"
        From: "opacity-100"
        To: "opacity-0"
    -->
    <div class="background-overlay fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity opacity-0" aria-hidden="true"></div>

    <!-- This element is to trick the browser into centering the modal contents. -->
    <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

    <!--
      Modal panel, show/hide based on modal state.

      Entering: "ease-out duration-300"
        From: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
        To: "opacity-100 translate-y-0 sm:scale-100"
      Leaving: "ease-in duration-200"
        From: "opacity-100 translate-y-0 sm:scale-100"
        To: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
    -->
    <div class="modal-main inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all opacity-0 translate-y-4 sm:py-8 sm:align-middle sm:max-w-lg sm:w-full">
      <div id="spinner-content">
        <div class=" flex justify-center items-center gap-4 align-middle">
          <span class="font-bold">Loading...</span>
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    </div>
  </div>
</div>
    `}_render(){let e=this;e.element=h.select(`#${this.parent_id}`).append("div").attr("id",e.id),e.element.html(e._base_template()),e.store.events.subscribe("Waiting",({waiting:t})=>{t>0&&e.enter()}),e.store.events.subscribe("Waiting",({waiting:t})=>{t===0&&e.exit()})}}const Ve=new Ie({id:"spinner-popup"});class Be extends v{constructor(e){super({store:_,id:e.id})}enter(e){let t=this;t.element.classed("pointer-events-none",!1);let s=t.element.select("#modal-content");s.html(t._content_template(e)),s.selectAll("button").on("click",this.exit.bind(t));let a;a=t.element.select(".background-overlay").node(),a.classList.remove("opacity-0"),a.classList.add("duration-300","opacity-40"),a=t.element.select(".modal-main").node(),a.classList.remove("opacity-0","translate-y-4"),a.classList.add("opacity-100","translate-y-0")}exit(){let e=this,t=e.element;e.element.classed("pointer-events-none",!0);let s;s=t.select(".background-overlay").node(),s.classList.remove("opacity-40","duration-300"),s.classList.add("opacity-0"),s=t.select(".modal-main").node(),s.classList.remove("opacity-100","translate-y-0"),s.classList.add("opacity-0","translate-y-4")}_content_template(e){e||(e={});let t={icon:`
        <!-- Heroicon name: outline/exclamation -->
        <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      `};switch(e.alert_type){case"error":t.bgcolor="bg-red-300",t.button_style="bg-red-600 hover:bg-red-700  focus:ring-red-500",t.icon_color="text-red-600",t.icon_bgcolor="bg-red-100";break;case"success":t.bgcolor="bg-green-300",t.button_style="bg-green-600 hover:bg-green-700  focus:ring-green-500",t.icon_color="text-green-600",t.icon_bgcolor="bg-green-100",t.icon=`
          <!-- Heroicon name: check -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        `;break;default:t.bgcolor="bg-yellow-300",t.button_style="bg-yellow-600 hover:bg-yellow-700  focus:ring-yellow-500",t.icon_color="text-yellow-600",t.icon_bgcolor="bg-yellow-100"}return`
    <div class="flex w-full h-8 ${t.bgcolor}"></div>
    <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 max-h-96 overflow-auto">

      <div class="sm:flex sm:items-start">
        <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full ${t.icon_bgcolor} sm:mx-0 sm:h-10 sm:w-10">
          <div class="icon ${t.icon_color}">
            ${t.icon}
          </div>
        </div>
        <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
          <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
            ${(e==null?void 0:e.title)||"Alert"}
          </h3>
          <div class="mt-2">
            <p class="text-sm text-gray-500">
              ${(e==null?void 0:e.msg)||""}
            </p>
          </div>
        </div>
      </div>
    </div>
    <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
      <button type="button" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2  text-base font-medium text-white ${t.button_style} focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm">
        ${(e==null?void 0:e.button_text)||"Dismiss"}
      </button>
    </div>
    `}_base_template(){return`
<div class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
  <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
    <!--
      Background overlay, show/hide based on modal state.

      Entering: "ease-out duration-300"
        From: "opacity-0"
        To: "opacity-100"
      Leaving: "ease-in duration-200"
        From: "opacity-100"
        To: "opacity-0"
    -->
    <div class="background-overlay fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity opacity-0" aria-hidden="true"></div>

    <!-- This element is to trick the browser into centering the modal contents. -->
    <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

    <!--
      Modal panel, show/hide based on modal state.

      Entering: "ease-out duration-300"
        From: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
        To: "opacity-100 translate-y-0 sm:scale-100"
      Leaving: "ease-in duration-200"
        From: "opacity-100 translate-y-0 sm:scale-100"
        To: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
    -->
    <div class="modal-main inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all opacity-0 translate-y-4 sm:my-8 sm:align-middle sm:max-w-xl sm:w-full">
      <div id="modal-content"></div>
    </div>
  </div>
</div>
    `}_render(){let e=this;e.element=h.select("body").append("div").attr("id",e.id).classed("pointer-events-none",!0),e.element.html(e._base_template()),e.store.events.subscribe("raiseModal",({modal_content:t})=>e.enter(t)),e.exit()}}const Ue=new Be({id:"modal-popup"});class We{constructor(e){this.store=_,this.namespace=e,this.registry_underline={0:"translate-x-0",1:"translate-x-full",2:"translate-x-double",3:"translate-x-triple",4:"translate-x-quad",5:"translate-x-pent",6:"translate-x-sext",7:"translate-x-sept",8:"translate-x-octa"},this.registry={}}init(){let e=this,t=this.namespace;document.querySelectorAll(`${t}`).forEach(a=>{Array.from(a.children).forEach((r,i)=>{e.registry[r.dataset.target]=e.registry_underline[i],r.dataset.target&&(r.addEventListener("click",()=>{e.store.dispatch("changedTab",{current_tab:r.dataset.target}),e.toggle.bind(e)(r.dataset.target)}),r.className.includes("active")&&e.toggle.bind(e)(r.dataset.target))})}),e.store.events.subscribe("changedTab",({current_tab:a})=>{e.toggle(a)});let s=p(e.store,"state.current_tab");s&&e.toggle(s)}toggle(e){let t=this,s=this.namespace,a=document.querySelector(`${s} .tab-slider`);a.className=a.className.replace(/\btranslate-x-.+?\b/g,""),a.classList.add(t.registry[e]),document.querySelectorAll(`${s} .tab-content`).forEach(r=>{r.classList[r.id===e?"remove":"add"]("hidden"),document.querySelector(`[data-target="${r.id}"]`).classList.toggle("active",r.id===e)})}}class qe extends v{constructor({children:e}){super({store:_,children:e}),this.classname="main-tab-group-namespace"}_template(){return`
    <!-- nav tabs -->
    <div
      class="
        ${this.classname}
        flex
        mt-3
        border-b border-gray-300
        relative
        flex-row
      "
    >
      <div data-target="editor-tab" class="relative tab active">
        Editor
        <div class="absolute tab-slider"></div>
      </div>
      <div data-target="how-to-tab" class="tab">How To</div>
      <div data-target="treatment-facility-results-tab" class="tab">Treatment Results</div>
      <div data-target="land-surface-results-tab" class="tab">Land Surface Results</div>
      <a class="tab" href="./logout">Logout</a>
    </div>

    <!-- end nav tabs -->

    <!-- tab content -->

    <div class="${this.classname} h-screen">
      <div id="how-to-tab" class="tab-content"></div>
      <div id="treatment-facility-results-tab" class="tab-content"></div>
      <div id="land-surface-results-tab" class="tab-content"></div>
      <div id="editor-tab" class="tab-content"></div>
    </div>

    <!-- end tab content -->
    `}_render(){let e=this;h.select(`#${this.parent_id}`).append("div").html(e._template()),new We(`.${this.classname}`).init()}}class He extends v{constructor(e){super({store:_,id:e.id,children:e.children}),this.store.events.subscribe("updateScenarioName",this._update_scenario_name.bind(this))}get scenario_name(){return p(this.store,"state.scenario_name")}_update_scenario_name(){let e=this;h.select(`#${e.id}`).select("#scenario-name").text(e.scenario_name)}_template(){return`
    <div class="flex flex-row justify-center text-lg font-bold p-4">
      Scenario:&nbsp
      <span id="scenario-name" contenteditable="true" class="border-b-2 border-black bg-gray-100 px-2">
        ${this.scenario_name}
      </span>
    </div>

    <div class="flex flex-row h-screen max-h-[650px]">
      <div class="flex flex-col sm:w-full min-w-0 max-w-[175px] ">
        <div id="toggle-container"></div>
      </div>
      <div class="relative w-full ">
        <div id="map" class="has-tooltip h-full max-w-screen"></div>
        <div id="editor-menu"></div>
      </div>

    </div>

    <div id="editor-info" class="grid grid-cols-2 gap-2 pl-12 py-2"></div>

    `}_render(){let e=this,t=h.select(`#${e.id}`).classed("flex flex-col ",!0).html(e._template());t.select("#scenario-name").on("input",()=>{let s=t.select("#scenario-name").text().trim();e.store.dispatch("changeScenarioName",{scenario_name:s})})}}class D extends v{constructor(e){super({store:_,id:e.id}),this.parent_id=e.parent_id,this.text=e.text,this.callback=e.callback,this.isActive=e.isActive,this.scale=e.scale||"scale-100",this.button,this._class=e.class_string||""}get class(){return this._class}_render(){let e=this;e.toggle=h.select(`#${e.parent_id}`).append("div"),e.toggle.html(`
    <!-- Toggle ${e.id} -->
    <div class="transform ${e.scale} m-0 sm:m-2 py-2">
      <label for="${e.id}-toggle" class="flex flex-col sm:flex-row items-center align-center cursor-pointer min-w-0">
        <!-- toggle -->
        <div class="relative">
          <!-- input -->
          <input type="checkbox" id="${e.id}-toggle" class="sr-only" />
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
        <div class="text-center sm:ml-3 text-gray-700 font-medium text-xs sm:text-sm">${e.text}</div>
      </label>
    </div>
    `),e.toggle.select("input[type=checkbox]").property("checked",e.isActive),e.toggle.select("input").on("change",e.callback.bind(e))}}const A="scale-75 sm:scale-100",Ge=new D({id:"map-edit-toggle",text:"Base Map",isActive:$(_,"state.map_mode"),scale:A,callback:function(){let n=!$(this,"store.state.map_mode");this.toggle.select("input[type=checkbox]").property("checked",!!n),this.store.dispatch("isMapMode",{map_mode:n})}}),Je=new D({id:"graph-edit-toggle",text:"Edit Graph",isActive:$(_,"state.graph_edit_mode"),scale:A,callback:function(){let n=!$(this,"store.state.graph_edit_mode");this.toggle.select("input[type=checkbox]").property("checked",!!n),this.store.dispatch("isGraphEditMode",{graph_edit_mode:n})}}),Xe=new D({id:"states-vector-toggle",text:"States",isActive:$(_,"state.show_states"),scale:A,callback:function(){let n=!$(this,"store.state.show_states");this.toggle.select("input[type=checkbox]").property("checked",!!n),this.store.dispatch("isShowStatesMode",{show_states:n})}}),Qe=new D({id:"design-storm-vector-toggle",text:"Design Storm",isActive:$(_,"state.show_design_storm"),scale:A,callback:function(){let n=!$(this,"store.state.show_design_storm");this.toggle.select("input[type=checkbox]").property("checked",!!n),this.store.dispatch("isShowDesignStorm",{show_design_storm:n})}}),Ye=new D({id:"rain-zone-vector-toggle",text:"Rain Zones",isActive:$(_,"state.show_rain_zone"),scale:A,callback:function(){let n=!$(this,"store.state.show_rain_zone");this.toggle.select("input[type=checkbox]").property("checked",!!n),this.store.dispatch("isShowRainZones",{show_rain_zone:n})}}),Ze=new D({id:"into-tooltip-toggle",text:"Node Info",isActive:$(_,"state.show_info_tooltip"),scale:A,callback:function(){let n=!$(this,"store.state.show_info_tooltip");this.toggle.select("input[type=checkbox]").property("checked",!!n),this.store.dispatch("isShowInfoTooltip",{show_info_tooltip:n})}}),Ke=new v({id:"toggle-container",class:"",children:[Ge,Xe,Qe,Ye,Je,Ze]});class et extends v{constructor(t){super({store:_,id:t.id});M(this,"width",()=>h.select(`#${this.id}`).node().getBoundingClientRect().width);M(this,"height",()=>h.select(`#${this.id}`).node().getBoundingClientRect().height);let s=this;s.store.events.subscribe("isMapMode",()=>s.toggleMapMode()),s.store.events.subscribe("changedTransform",a=>s.zoomed(a)),s.svg=t.svg,s.initialScale=p(s,"store.state.initialScale"),s._k={},s.initialCenter=p(s,"store.state.config.project_spatial_data.app.centroid")||p(s,"store.state.initialCenter"),s.tilesize=256,s._current_point,s._zoomed=!1,s.url=(a,r,i)=>`https://${"abc"[Math.abs(a+r)%3]}.basemaps.cartocdn.com/rastertiles/voyager/${i}/${a}/${r}${devicePixelRatio>1?"@2x":""}.png`,s.projection=h.geoMercator().scale(1/(2*Math.PI)).translate([0,0]),s.store.dispatch("setProjection",{projection:s.projection}),s.transform=h.zoomIdentity.translate(s.projection([0,0])[0],s.projection([0,0])[1]).scale(s.projection.scale()*2*Math.PI),s.store.dispatch("setTransform",{transform:s.transform}),s.renderer=h.geoPath(s.projection),s.tile=h.tile().extent([[0,0],[s.width(),s.height()]]).tileSize(s.tilesize),s.image_bg=s.svg.append("svg:g").classed("bg basemap",!0).attr("pointer-events","none").style("overflow","hidden").attr("pointer-events","none").classed("hidden",!s.store.state.map_mode).selectAll("image"),s.image_fg=s.svg.append("svg:g").classed("fg basemap",!0).attr("pointer-events","none").style("overflow","hidden").classed("hidden",!s.store.state.map_mode).selectAll("image"),s.image_group=s.svg.selectAll(".basemap"),s.vector=s.svg.append("svg:g").attr("id","vectors").attr("pointer-events","none"),s.zoom=h.zoom().scaleExtent([64,1<<30]).extent([[0,0],[s.width(),s.height()]]).filter(()=>!s.drag_lock).on("start",a=>{}).on("zoom",a=>{s.store.dispatch("changedTransform",{transform:a.transform})}).on("end",a=>{s.store.dispatch("changedZoomTransform",{zoomTransform:s.zoom.transform})})}get drag_lock(){return p(this,"store.state.drag_lock")}toggleMapMode(){let t=this;t.image_group.classed("hidden",!t.store.state.map_mode),console.debug("map mode toggled!")}resize(){let t=this;t.tile=h.tile().extent([[0,0],[t.width(),t.height()]]).tileSize(t.tilesize);const s=t.tile(t.transform);t.image_bg=t.image_bg.data(s,a=>a).join("image").attr("xlink:href",a=>t.url(...a)).attr("x",([a])=>(a+s.translate[0])*s.scale-.5).attr("y",([,a])=>(a+s.translate[1])*s.scale-.5).attr("width",s.scale+1).attr("height",s.scale+1),t.image_fg=t.image_fg.data(s,a=>a).join("image").attr("xlink:href",a=>t.url(...a)).attr("x",([a])=>(a+s.translate[0])*s.scale).attr("y",([,a])=>(a+s.translate[1])*s.scale).attr("width",s.scale).attr("height",s.scale)}zoomed({transform:t}){let s=this;s.transform=t,s._k=t.k,s.resize(),s.vector.attr("transform",t)}_render(){let t=this;t.svg.call(t.zoom).call(t.zoom.transform,h.zoomIdentity.translate(t.width()/2,t.height()/2).scale(-t.initialScale).translate(...t.projection(t.initialCenter)).scale(-1))}}class tt extends v{constructor(e){super({store:_});let t=this;t.stroke_width=1,t.store.events.subscribe("changedTransform",()=>{t.path.style("stroke-width",t.stroke_width/t.transform.k)}),t.store.events.subscribe("isShowStatesMode",()=>{t.path.classed("hidden",t.hidden)}),t.projection=p(t,"store.state.projection"),t.renderer=h.geoPath(t.projection).digits(15),t.url="https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json",t.vector=e.vector,t.path=t.vector.append("path").attr("pointer-events","all").attr("fill","none").attr("stroke","green").attr("stroke-linecap","round").attr("stroke-linejoin","round").classed("hidden",t.hidden).style("stroke-width",t.stroke_width/t.transform.k)}get hidden(){return!p(this,"store.state.show_states")}get transform(){return p(this,"store.state.transform")}async _render(){let e=this,t=await h.json(e.url),s=Z(t,t.objects.states);e.geojson=s,e.store.dispatch("setStateQuery",{state_query:s}),e.path.attr("d",e.renderer(s))}}class pe extends v{constructor({vector:e}){super({store:_});let t=this;t.group=e.append("g"),t.stroke_width=0,t.domain=[0,1],t.projection=p(t,"store.state.projection"),t.renderer=h.geoPath(t.projection).digits(15)}get transform(){return p(this,"store.state.transform")}async _load_data(e){let t=this;if(!e)return;let s,a;try{if(e!=null&&e.filepath)a=await te(e.filepath);else if(e!=null&&e.url)a=await N(e.url);else return}catch(r){console.error(r);return}try{if((a==null?void 0:a.type)==="Topology"){let r=a;s=Z(r,r.objects[e.name])}else(a==null?void 0:a.type)==="FeatureCollection"&&(s=a,s.features=s.features.map(r=>Ee(r,{reverse:!0})))}catch(r){console.error(r);return}if(s){s._field=e.field;let r=s.features.map(i=>i.properties[e.field]);t.domain=[Math.min(...r),Math.max(...r)],t.geojson=s}}}class st extends pe{constructor({vector:e}){super({vector:e});let t=this;t.store.events.subscribe("changedTransform",()=>{t.group.selectAll("path").style("stroke-width",t.stroke_width/t.transform.k)}),t.store.events.subscribe("isShowDesignStorm",async()=>{let s=p(t,"store.state.design_storm_geojson");if(!s){await t.load_data();return}t._draw(s)}),t.store.events.subscribe("setDesignStormQuery",({design_storm_geojson:s})=>t._draw(s))}get hidden(){return!p(this,"store.state.show_design_storm")}async load_data(){var a;let e=this,t=p(e.store,"state.config"),s=w((a=t==null?void 0:t.project_spatial_data)==null?void 0:a.design_storm);await e._load_data(s),e.geojson&&e.store.dispatch("setDesignStormQuery",{design_storm_geojson:e.geojson})}_draw(e){if(!e)return;let t=this;t.group.selectAll("path").remove(),!t.hidden&&(t.colorScale=h.scaleLinear().domain(t.domain).range(["white","blue"]),t.group.selectAll("path").data(e.features).enter().append("path").attr("d",t.renderer).attr("pointer-events","all").attr("fill",s=>t.colorScale(s.properties[e._field])).attr("stroke","#eee").attr("stroke-linecap","round").attr("stroke-linejoin","round").style("stroke-width",t.stroke_width/t.transform.k))}async _render(){let e=this;e.store.events.subscribe("updateConfig",e.load_data.bind(e))}}class at extends pe{constructor({vector:e}){super({vector:e});let t=this;t.stroke_width=1,t.store.events.subscribe("changedTransform",()=>{t.group.selectAll("path").style("stroke-width",t.stroke_width/t.transform.k)}),t.store.events.subscribe("isShowRainZones",async()=>{let s=p(t,"store.state.ref_data_key_geojson");if(!s){await t.load_data();return}t._draw(s)}),t.store.events.subscribe("setRefDataQuery",({ref_data_key_geojson:s})=>t._draw(s))}get hidden(){return!p(this,"store.state.show_rain_zone")}async load_data(){var a;let e=this,t=p(e.store,"state.config"),s=w((a=t==null?void 0:t.project_spatial_data)==null?void 0:a.ref_data_key);await e._load_data(s),e.geojson&&e.store.dispatch("setRefDataQuery",{ref_data_key_geojson:e.geojson})}_draw(e){if(!e)return;let t=this;t.group.selectAll("path").remove(),!t.hidden&&(t.colorScale=h.scaleOrdinal().domain(t.domain).range(h.schemeSet3),t.group.selectAll("path").data(e.features).enter().append("path").attr("d",t.renderer).attr("pointer-events","all").attr("fill",s=>t.colorScale(s.properties[e._field])).attr("stroke","#eee").attr("stroke-linecap","round").attr("stroke-linejoin","round").style("stroke-width",t.stroke_width/t.transform.k))}async _render(){let e=this;e.store.events.subscribe("updateConfig",e.load_data.bind(e))}}class rt extends v{constructor(t){super({store:_,id:t.id});M(this,"fixedScale",()=>!1);M(this,"getScale",()=>{let t=this;return t.fixedScale()?p(t,"store.state.transform.k")/p(t,"store.state.initialScale"):1});M(this,"getLoc",t=>this.longLatToPoint(t.longlat));let s=this;s.svg=t.svg,s.options=t||{},s.default_nodesize=s.options.default_nodesize||12,s.charge=s.options.charge||-300,s.edge_distance=s.options.edge_distance||80,s.node_types=s.options.node_types||{},s.onNodeSelected=typeof s.options.onNodeSelected<"u"?s.options.onNodeSelected:function(){},s.onNodeUnSelected=typeof s.options.onNodeUnSelected<"u"?s.options.onNodeUnSelected:function(){},s._selected_node_id=null,s._mousedown_edge=null,s._mousedown_node=null,s._mouseup_node=null,s._lastKeyDown=-1,s.container=s.svg.append("svg:g").classed("graph-editor",!0).style("pointer-events","all"),s.container.append("svg:defs").append("svg:marker").attr("id","end-arrow").attr("viewBox","0 -5 10 10").attr("refX",5).attr("markerWidth",3).attr("markerHeight",3).attr("orient","auto").style("fill","#333").append("svg:path").attr("d","M0,-5L10,0L0,5"),s.dragLine=s.container.append("svg:path").attr("class","link dragline hidden").attr("d","M0,0L0,0"),s.path=s.container.append("svg:g").selectAll("path"),s.circle=s.container.append("svg:g").selectAll("g"),s.drag=h.drag().filter(a=>a.button===0||a.button===2).on("drag",(a,r)=>{r.longlat=s.pointToLongLat([a.x,a.y]),s.update()}).on("end",()=>s.store.dispatch("stateChange")),h.select(window).on("mousemove.graph-editor",s.mousemove.bind(s)).on("keydown.graph-editor",s.keydown.bind(s)).on("keyup.graph-editor",s.keyup.bind(s)),s.svg.on("click.graph-editor",s.mousedown_addNode.bind(s)).on("mouseup.graph-editor",s.mouseup.bind(s)).on("mouseenter",s.mouseenter.bind(s)).on("mouseleave",s.mouseleave.bind(s))}subscribe(){let t=this;t.store.events.subscribe("isConstNodeArea",()=>t.toggleConstNodeArea()),t.store.events.subscribe("changedTransform",()=>t.update()),t.store.events.subscribe("editorUpdate",()=>{t.update()}),t.store.events.subscribe("newGraph",()=>{t.update()}),t.store.events.subscribe("setRefDataQuery",()=>{t.update()}),t.store.events.subscribe("setDesignStormQuery",()=>{t.update()})}get bbox(){return this.svg.node().getBoundingClientRect()}get width(){return this.bbox.width}get height(){return this.bbox.height}get transform(){return p(this,"store.state.transform")}get projection(){return p(this,"store.state.projection")}get editing_mode(){return p(this,"store.state.graph_edit_mode")}get graph(){return p(this,"store.state.graph")}get_node_by_id(t){return this.graph.nodes.find(s=>s.id===t)}pointToLongLat(t){let s=this;return s.projection.invert(s.transform.invert(t))}longLatToPoint(t){let s=this;return s.transform.apply(s.projection(t))}recalculateNodeSize(t){let s=this;return Math.max(3,t.size*s.getScale())*(t.id===s._selected_node_id?1.3:1)}getColor(t){let s=this;if(t!=null&&t.color)return h.rgb(t.color);let a=p(s.store.state.node_types,t.node_type);return h.rgb((a==null?void 0:a.color)||"lightgrey")}tick(){let t=this;t.path.attr("d",s=>{const a=s.target.x-s.source.x,r=s.target.y-s.source.y,i=Math.sqrt(a*a+r*r),c=a/i,u=r/i,m=t.recalculateNodeSize(s.source),l=5+t.recalculateNodeSize(s.target),o=s.source.x+m*c,d=s.source.y+m*u,f=s.target.x-l*c,g=s.target.y-l*u;return a*(f-o)<0||r*(g-d)<0?`M${s.source.x},${s.source.y}L${s.target.x},${s.target.y}`:`M${o},${d}L${f},${g}`}),t.circle.selectAll(".node").attr("r",s=>t.recalculateNodeSize(s)*.95),t.circle.attr("transform",s=>`translate(${s.x},${s.y})`)}getState(t){var c;let a=p(this,"store.state.state_query"),r="undefined",i;return a!=null?(i=a.features.find(u=>h.geoContains(u,t)),((c=i==null?void 0:i.properties)==null?void 0:c.name)||"undefined"):r}getDesignStormDepth(t){var i;let a=p(this,"store.state.design_storm_geojson"),r;if(a!=null)return r=a.features.find(c=>h.geoContains(c,t)),(i=r==null?void 0:r.properties)==null?void 0:i[a._field]}getRefDataKey(t){var i;let a=p(this,"store.state.ref_data_key_geojson"),r;if(a!=null)return r=a.features.find(c=>h.geoContains(c,t)),(i=r==null?void 0:r.properties)==null?void 0:i[a._field]}setNodeDefaults(t){let s=this;t.map(a=>a!=null&&a.size?a:Object.assign(a,{size:s.default_nodesize})),t.map(a=>a!=null&&a.longlat?a:Object.assign(a,{longlat:s.pointToLongLat([a.x,a.y])})),t.map(a=>{let[r,i]=s.longLatToPoint(a.longlat);return a.x=r,a.y=i,a}),t.map(a=>(a.state=s.getState(a.longlat),a)),t.map(a=>{var r;if(!((r=a==null?void 0:a.node_type)!=null&&r.includes("land_surface"))){let i=s.getDesignStormDepth(a.longlat);if(i==null)return a;a.design_storm_depth_inches=+parseFloat(i).toFixed(2),a!=null&&a.data&&(a.data.design_storm_depth_inches=a.design_storm_depth_inches)}return a}),t.map(a=>{var r;if(!((r=a==null?void 0:a.node_type)!=null&&r.includes("land_surface"))){let i=s.getRefDataKey(a.longlat);if(i==null)return a;a.ref_data_key=i,a!=null&&a.data&&(a.data.ref_data_key=a.ref_data_key)}return a})}update(){let t=this,s;s=t.graph.nodes,t.setNodeDefaults(s),t.path=t.path.data(t.graph.edges),t.path.classed("selected",r=>r===t._selected_edge).style("marker-end","url(#end-arrow)"),t.path.exit().remove(),t.path=t.path.enter().append("svg:path").classed("link",!0).classed("selected",r=>r===t._selected_edge).style("marker-end","url(#end-arrow)").on("mousedown",(r,i)=>{r.ctrlKey||(t._mousedown_edge=i,t._selected_edge=t._mousedown_edge===t._selected_edge?null:t._mousedown_edge,t._selected_node_id=null,t.update())}).merge(t.path),t.circle=t.circle.data(s,r=>JSON.stringify(r)),t.circle.selectAll(".node").attr("r",r=>t.recalculateNodeSize(r)).style("fill",r=>{let i=t.getColor(r);return r.id===t._selected_node_id?i.brighter(3):i}).style("stroke",r=>t.getColor(r).darker().toString()),t.circle.selectAll("text").text(r=>r.id),t.circle.exit().remove();const a=t.circle.enter().append("svg:g");a.append("circle").classed("node has-tooltip",!0).attr("r",r=>t.recalculateNodeSize(r)).style("fill",r=>{let i=t.getColor(r);return r.id===t._selected_node_id?i.brighter(3):i}).style("stroke",r=>t.getColor(r).darker().toString()).on("mouseover",function(r,i){t._hovered_node=i,t.store.dispatch("isNodeHovered",{node_hovered:i.id}),!t._selected_node_id&&(p(t,"store.state.current_node_data.id"),i.id),!(!t._mousedown_node||i.id===t._mousedown_node.id)&&h.select(r.target).attr("transform","scale(1.25)")}).on("mouseout",(r,i)=>{t._hovered_node=void 0,t.store.dispatch("isNodeHovered",{node_hovered:void 0}),!(!t._mousedown_node||i.id===t._mousedown_node.id)&&h.select(r.target).attr("transform","")}).on("mousedown",(r,i)=>{r.shiftKey||r.ctrlKey||(t.store.dispatch("drag_lock",{drag_lock:!0}),t._mousedown_node=i,t._mousedown_node.id===t._selected_node_id?(t._selected_node_id=null,t.onNodeUnSelected(i),t.store.dispatch("changedSelectedNode",{selected_node_id:null})):(t._selected_node_id=t._mousedown_node.id,_.dispatch("changedSelectedNode",{selected_node_id:i.id}),t.onNodeSelected(i)),t._selected_edge=null,t.update())}).on("mouseup",(r,i)=>{if(t.dragLine.classed("hidden",!0).style("marker-end",""),t.store.dispatch("drag_lock",{drag_lock:!1}),!t._mousedown_node||!t.editing_mode)return;if(t._mouseup_node=i,t._mouseup_node.id===t._mousedown_node.id){t.resetMouseVars();return}h.select(r.target).attr("transform","");const c=t._mousedown_node.id,u=t._mouseup_node.id,m=t.graph.edges.find(l=>l.source===c&&l.target===u);if(!m){let l=t.graph.nodes.find(d=>d.id===c),o=t.graph.nodes.find(d=>d.id===u);t.graph.edges.push({source:l,target:o})}t._selected_edge=m,t._selected_node_id=null,t.update()}),a.append("text").attr("x",0).attr("y","0.3rem").attr("class","id no-select align-middle text-center font-bold text-base pointer-events-none").text(r=>r.id),t.circle=a.merge(t.circle),t.tick()}zoom_to_group(t){let s=this;const a=s.container.node().getBBox(),[[r,i],[c,u]]=[[a.x,a.y],[a.x+a.width,a.y+a.height]];t==null&&(t=1);let m=s.transform.k;for(;t>0;)t-=1,m=Math.min(1<<28,m*(.9/Math.max((c-r)/s.width,(u-i)/s.height)));const l=[r+a.width/2,i+a.height/2];let o=p(s,"store.state.zoomTransform");s.svg.interrupt().transition().duration(800).call(o,h.zoomIdentity.translate(s.width/2,s.height/2).scale(-m).translate(...s.transform.invert(l)).scale(-1))}mouseenter(){this.svg.classed("listening-to-keys",!0)}mouseleave(){this.svg.classed("listening-to-keys",!1)}keydown(t){let s=this;if(s.svg.classed("listening-to-keys")&&(t.keyCode,t.keyCode===71&&s.zoom_to_group(),!!s.editing_mode)){if(t.keyCode===17){s.circle.call(s.drag),s.svg.classed("ctrl",!0);return}if(!(!this._selected_node_id&&!this._selected_edge))switch(t.keyCode){case 8:case 46:this._selected_node_id?(this.graph.nodes.splice(this.graph.nodes.map(a=>a.id).indexOf(this._selected_node_id),1),this.graph.spliceLinksForNode(this._selected_node_id)):this._selected_edge&&this.graph.edges.splice(this.graph.edges.indexOf(this._selected_edge),1),this._selected_edge=null,this._selected_node_id=null,s.store.dispatch("changedSelectedNode",{selected_node_id:null}),this.resetMouseVars(),this.update();break}}}keyup(t){let s=this;t.keyCode===17&&(s.circle.on(".drag",null),s.svg.classed("ctrl",!1))}mousedown_addNode(t){var m;let s=this;if(this.svg.classed("active",!0),t.shiftKey||t.ctrlKey||!s.editing_mode||s._mousedown_node||s._mousedown_edge||s._hovered_node){s.resetMouseVars();return}const a=h.pointer(t);let[r,i]=a,c=s.pointToLongLat([r,i]);const u={id:le(5),x:r,y:i,size:s.default_nodesize,longlat:c};u.design_storm_depth_inches=+parseFloat(s.getDesignStormDepth(u.longlat)).toFixed(2),u.ref_data_key=s.getRefDataKey(u.longlat),this.graph.nodes.push(u),s.store.dispatch("changedSelectedNode",{selected_node_id:u.id}),s._selected_node_id=(m=this.graph.nodes.find(l=>l.id===u.id))==null?void 0:m.id,s.update(),s.mouseup()}mouseup(){if(this.svg.classed("active",!1),this._mousedown_node){this.dragLine.classed("hidden",!0).style("marker-end","");return}this.resetMouseVars()}mousemove(t){let s=this;if(!this._mousedown_node||!this.editing_mode)return;let{x:a,y:r}=p(this,"store.state.graph.nodes").find(c=>c.id===this._mousedown_node.id);s.dragLine.style("marker-end","url(#end-arrow)").classed("hidden",!1).attr("d",`M${s._mousedown_node.x},${s._mousedown_node.y}L${s._mousedown_node.x},${s._mousedown_node.y}`);const i=h.pointer(t,this.container.node());this.dragLine.attr("d",`M${a},${r}L${i[0]},${i[1]}`)}resetMouseVars(){this._mousedown_node=null,this._mouseup_node=null,this._mousedown_edge=null}_render(){let t=this;t.subscribe(),t.update(),t.zoom_to_group()}}class nt extends v{constructor(){super({store:_})}resize(){var t;p(this.store,"state.current_tab")=="editor-tab"&&(this.svg.attr("viewBox",[0,0,h.select("#map").node().getBoundingClientRect().width,h.select("#map").node().getBoundingClientRect().height]),(t=this==null?void 0:this.map)==null||t.resize())}_render(){let e=this;e.svg=h.select("#map").append("svg"),e.resize(),e.map=new et({id:"map",svg:e.svg});const t=e.map.vector;e.states=new tt({vector:t}),e.designStorm=new st({vector:t}),e.refData=new at({vector:t}),e.graphEditor=new rt({svg:e.svg}),e.map.render(),e.states.render(),e.designStorm.render(),e.refData.render(),e.graphEditor.render()}}Pe();const R=new nt;class it extends v{constructor(e){super({store:_});let t=this;t.parent_id=e.parent_id,t.id=e.id||""}get current_node_data(){let e=p(this,"store.state.selected_node_id")||p(this,"store.state.node_hovered");if(e)return p(this,"store.state.graph.nodes").find(t=>t.id===e)}get show_info_tooltip(){return p(this,"store.state.show_info_tooltip")}tooltip_move(e){let t=this.element.node().getBoundingClientRect().width,s=null,a=null;e.type=="touchstart"?(s=e.touches[0].pageX,a=e.touches[0].pageY):(s=e.pageX,a=e.pageY);let r=Math.max(0,window.innerWidth-s<t?s-t:s);this.element.style("left",r+"px").style("top",a-28+"px")}hide(){let e=this.element;e.classed("opacity-100 h-auto",!1),e.classed("opacity-0 h-0",!0)}show(){let e=this.element;e.classed("opacity-100 h-auto",!0),e.classed("opacity-0 h-0",!1)}update_contents(){let e=this,t=e.current_node_data,s=e.element;if(!e.show_info_tooltip||!t){e.hide();return}e.show(),s.select(".info-tooltip-header").html(`<h5>Node ID:&nbsp${t.id}</h5>`);let a=`
        <tr>
          <td>Node Type:</td>
          <td>${t.node_type||"No Data"}</td>
        </tr>
      `;s.select(".info-tooltip-content table").html(a);let r=Object.keys(t).filter(u=>u.charAt(0)==="_"),i=oe(t,[],r),c=`<pre>${JSON.stringify(i,void 0,2)}</pre>`;s.select(".info-tooltip-json").html(c)}_render(){let e=this,t=h.select(`#${e.parent_id}`);e.element=t.append("div").attr("id",e.id||"").classed("transition-opacity opacity-0 tooltip rounded shadow-lg p-1 bg-gray-50",!0);let s=e.element.html("");s=s.append("div").classed("info-tooltip p-2",!0),s.append("div").classed("info-tooltip-header mt-2 uppercase text-lg font-bold",!0),s.append("div").classed("info-tooltip-content text-sm",!0).append("table"),s.select(".info-tooltip-content").append("div").classed("info-tooltip-json",!0),s.append("div").classed("info-tooltip-footer",!0),e.store.events.subscribe("stateChange",()=>this.update_contents())}}const lt=new it({parent_id:"editor-info",id:"node-info-tooltip"});class ot extends v{constructor(e){super({store:_});let t=this;t.parent_id=e.parent_id,t.id=e.id||""}get show_tips(){return p(this,"store.state.graph_edit_mode")}hide(){let e=this.element;e.classed("opacity-100 h-auto",!1),e.classed("opacity-0 h-0",!0)}show(){let e=this.element;e.classed("opacity-100 h-auto",!0),e.classed("opacity-0 h-0",!1)}update_contents(){let e=this;if(!e.show_tips){e.hide();return}e.show()}_template(){return`
    <div>
    <strong>Edit Graph</strong> is Active
    <br />
    <br />
    <em>Click</em> in the open space to <strong>add a node</strong>.

    <br />
    <em>Drag</em> from one node to another to <strong>add an edge</strong>

    <br />
    <em>Click</em> a node or an edge to <strong>select</strong> it.

    <br />
    <em>Press Ctrl & Drag</em> a node to <strong>move</strong> the graph node layout.
    Dragging will pin the node to the location.

    <br />
    <em>Press Delete</em> to <strong>remove the selected node or edge</strong>.
    This is possible only when the mouse is within the map editor.

    <br />
    <em>Press G</em> to <strong>zoom</strong> the map to the graph extents.

    </div>
    `}_render(){let e=this,t=h.select(`#${e.parent_id}`);e.element=t.append("div").attr("id",e.id||"").classed("transition-opacity opacity-0 p-2 h-auto text-justify",!0).html(e._template()),this.update_contents(),e.store.events.subscribe("isGraphEditMode",()=>this.update_contents())}}const dt=new ot({parent_id:"editor-info",id:"editor-tips"});class L extends v{constructor(e){super({store:_});let t=this;t.id=e.id,t.title=e.title,t.icon=e.icon,t.callback=e.callback}_template(){return`
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

  </button>`}_render(){let e=this,t=h.select(`#${this.parent_id}-button-container`).append("div").classed("flex ",!0),s=t.html();s+=this._template(),t.html(s),this.button=t.select(`button#${this.id}-button`),this.button.on("click",e.callback.bind(e))}}const ct=new L({id:"node_editor",title:"Configuration",icon:`
  <!-- Heroicon name: adjustments -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    class="h-8 w-8"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
    />
  </svg>`,callback:function(){this.store.dispatch("changedPanel",{active_panel:"node-editor-panel"})}}),ut=new L({id:"load_table",title:"Load from File",icon:`
  <!-- Heroicon name: document-add -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    class="h-8 w-8"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
    />
  </svg>`,callback:function(){this.store.dispatch("changedPanel",{active_panel:"load-table-panel"})}}),pt=new L({id:"save_files",title:"Save Files",icon:`
  <!-- Heroicon name: save -->
  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
  </svg>
`,callback:function(){this.store.dispatch("changedPanel",{active_panel:"save-files-panel"})}}),mt=new L({id:"clear_scenario",title:"Clear Scenario",icon:`
<div class="sm:pt-10 text-red-600 hover:text-gray-300">

  <!-- Heroicon name: x-circle -->
  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
</div>
`,callback:function(){confirm("Are you sure you want to clear all data?")&&new C([],[])}}),ft=new L({id:"check_scenario",title:"Verify Inputs",icon:`
<div class="sm:pt-10 text-blue-600 hover:text-gray-300">

  <!-- Heroicon name: check -->
  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
  </svg>
</div>
`,callback:async function(){Promise.all([ae(),se()]).then(n=>{n.length;const e=n.filter(s=>s.alert_type.toLowerCase()=="error");if(e.length>0){let s=e[0];s.msg=`<div>${e.map(a=>a.msg).join("</br>")}</div>`,this.store.dispatch("raiseModal",{modal_content:s});return}if(n.filter(s=>s.alert_type.toLowerCase()=="success").length===n.length){let s={title:"Validation Successful",msg:"",alert_type:"success"};this.store.dispatch("raiseModal",{modal_content:s});return}}).catch(n=>{let e={title:"Validation Failed",msg:`<pre>${JSON.stringify(n,void 0,2)}</pre>`,alert_type:"error"};this.store.dispatch("raiseModal",{modal_content:e})})}}),_t=new L({id:"run_scenario",title:"Run Scenario",icon:`
<div class="sm:pt-10 text-green-600 hover:text-gray-300">

  <!-- Heroicon name: play -->
  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
</div>
`,callback:async function(){var e;let n=await re();if(((e=n==null?void 0:n.status)==null?void 0:e.toLowerCase())==="success"){let t=p(n,"data.results")||[],s=p(n,"data.leaf_results")||[];this.store.dispatch("newResults",{results:t.concat(s)})}}}),ht=new L({id:"find_node",title:"Find",icon:`
  <!-- Heroicon name: search -->
  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
`,callback:function(){this.store.dispatch("changedPanel",{active_panel:"find-node-panel"})}});class gt extends v{constructor(e){super({store:_,id:e.id,children:e.children})}_template(){return`
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
  `}_render(){this.element=h.select(`#${this.id}`),this.element.html(this._template())}}const yt=new gt({id:"editor-menu",children:[ht,ct,ut,pt,mt,ft,_t]});class B extends v{constructor(e){super({store:_,id:e.id,children:e.children});let t=this;t.title=e.title,t.options=e}enter(){var a;let e=this,t=e.element;e.transition_direction="entering";let s;s=t.select(".drawer-overlay").node(),s.className=s.className.replace(/\bopacity-.+?\b/g,""),s.classList.add("opacity-40"),s=t.select(".drawer-panel").node(),s.className=s.className.replace(/\btranslate-x-.+?\b/g,""),s.classList.add("translate-x-0"),s.className=s.className.replace(/\bopacity-.+?\b/g,""),s.classList.add("opacity-100"),(a=e==null?void 0:e.options)!=null&&a.enter_callback&&e.options.enter_callback()}exit(){var a;let e=this,t=document.querySelector(`#${this.id}`),s;e.transition_direction="exiting",s=t.querySelector(".drawer-overlay"),s.className=s.className.replace(/\bopacity-.+?\b/g,""),s.classList.add("opacity-0"),s=t.querySelector(".drawer-panel"),s.className=s.className.replace(/\btranslate-x-.+?\b/g,""),s.classList.add("translate-x-full"),(a=e==null?void 0:e.options)!=null&&a.exit_callback&&e.options.exit_callback()}_template(){return`
    <div class="pointer-events-none">
      <!-- This example requires Tailwind CSS v2.0+ -->
      <div
        class="fixed inset-0 overflow-hidden"
        aria-labelledby="slide-over-title"
        role="dialog"
        aria-modal="true"
      >
        <div class="absolute inset-0 overflow-hidden">
          <!--
      Background overlay, show/hide based on slide-over state.

      Entering: "ease-in-out duration-500"
        From: "opacity-0"
        To: "opacity-100"
      Leaving: "ease-in-out duration-500"
        From: "opacity-100"
        To: "opacity-0"
    -->
          <div
            class="
              drawer-overlay
              absolute
              inset-0
              bg-gray-800 bg-opacity-50
              transition-opacity
              ease-in-out
              duration-500
              opacity-0
            "
            aria-hidden="true"
          ></div>

          <div
            class="
              drawer-panel
              translate-x-full
              fixed
              inset-y-0
              right-0
              pl-2
              max-w-full
              max-h-screen
              flex
              pointer-events-auto
              transition-transform
              ease-in-out
              duration-500
              translate-x-full
            "
          >
            <!--
        Slide-over panel, show/hide based on slide-over state.

        Entering: "transform transition ease-in-out duration-500 sm:duration-700"
          From: "translate-x-full"
          To: "translate-x-0"
        Leaving: "transform transition ease-in-out duration-500 sm:duration-700"
          From: "translate-x-0"
          To: "translate-x-full"
      -->
            <div class="relative w-screen max-w-md lg:max-w-lg">
              <!--
          Close button, show/hide based on slide-over state.

          Entering: "ease-in-out duration-500"
            From: "opacity-0"
            To: "opacity-100"
          Leaving: "ease-in-out duration-500"
            From: "opacity-100"
            To: "opacity-0"
        -->
              <!-- <div
                class="
                  absolute
                  top-0
                  left-0
                  -ml-8
                  pt-4
                  pr-2
                  flex
                  sm:-ml-10 sm:pr-4
                "
              > -->
              <div
                class="absolute top-0 left-0 pt-4 pl-4 flex"
              >
                <button
                  id="${this.id}-close-button"
                  class="
                    rounded-md
                    text-gray-300
                    hover:text-black
                    focus:outline-none focus:ring-2 focus:ring-black
                  "
                >
                  <span class="sr-only">Close panel</span>
                  <!-- Heroicon name: outline/x -->
                  <svg
                    class="h-6 w-6"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              <div
                class="
                  h-full
                  flex flex-col
                  py-6
                  pl-10
                  pr-6
                  bg-white
                  shadow-xl
                  overflow-y-scroll
                "
              >
                <div class="px-0 sm:px-2">
                  <h2
                    class="text-lg font-medium text-gray-900"
                    id="slide-over-title"
                  >
                    ${this.title}
                  </h2>
                </div>
                <div class="mt-6 relative flex-1 w-full px-0 sm:px-2">
                  <!-- Replace with your content -->
                  <div id="${this.id}-content">
                    <div class="absolute inset-0 px-4 sm:px-6 pointer-events-none">
                      <div
                        class="h-full border-2 border-dashed border-gray-200"
                        aria-hidden="true"
                      ></div>
                    </div>
                  </div>
                  <!-- /End replace -->
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    `}_render(){var s;let e=this;e.element=h.select(`#${this.id}`).append("div").classed("drawer-container",!0),e.element.html(this._template()),e.element.select(`#${this.id}-close-button`).on("click",this.exit.bind(this)),((s=this==null?void 0:this.children)==null?void 0:s.length)>0&&e.element.select(`#${this.id}-content`).html("");let t=e.element.select(".drawer-container").classed("hidden",!0);e.exit(),t.classed("hidden",!1)}}class bt extends B{constructor(e){super(e);let t=this;t.store.events.subscribe("changedPanel",({active_panel:s})=>s==="find-node-panel"?t.enter():null)}}class vt extends B{constructor({id:e,title:t,children:s}){super({store:_,id:e,title:t,children:s});let a=this;a.store.events.subscribe("changedPanel",({active_panel:r})=>r==="node-editor-panel"?a.enter():null)}}class wt extends B{constructor({id:e,title:t,children:s}){super({store:_,id:e,title:t,children:s});let a=this;a.store.events.subscribe("changedPanel",({active_panel:r})=>r==="load-table-panel"?a.enter():null)}}class xt extends B{constructor({id:e,title:t,children:s}){super({store:_,id:e,title:t,children:s});let a=this;a.store.events.subscribe("changedPanel",({active_panel:r})=>r==="save-files-panel"?a.enter():null)}}class kt extends v{constructor({children:e}){super({store:_,children:e})}_template(){return`
    <div id="find-node-drawer"></div>
    <div id="node-editor-drawer"></div>
    <div id="load-table-drawer"></div>
    <div id="save-files-drawer"></div>
    `}_render(){h.select(`#${this.parent_id}`).append("div").html(this._template())}}class St extends v{constructor(e){super({store:_,id:e.id});let t=this;t.primary_callback=s=>{Ot(s.find_node)},t.primary_button_label=e.primary_button_label||"Find"}_template_primary_button(){return this.primary_callback==null?"":`<button
    class="
      rounded-r-lg
      text-xs
      h-10
      font-bold
      py-2
      px-4
      btn-blue
      shadow
      w-20
    "
    type="submit"
    id="${this.id}-primary-button"
  >
    ${this.primary_button_label}
  </button>`}_template(){return`
      <div id="${this.id}" class="px-2 pb-10">
      <!-- <div class="pb-2"><strong>Search</strong></div> -->

      <div class="">
        <form
          class="
            relative
            flex flex-row
            h-10
            items-center

          "
        >
          <div class="relative w-full flex flex-row items-center">
            <input
              type="text"
              class="absolute
              pl-4
              border
              shadow
              rounded-l-lg
              w-full h-10"
              id="${this.id}-find"
              aria-describedby="${this.id}-find"
              placeholder="Search here..."
              name="find_node"
            />

          </div>
          ${this._template_primary_button()}
        </form>
      </div>
    </div>`}_render(){let e=this;e.element=h.select(`#${e.parent_id}-content`).append("div"),e.element.html(e._template());let t=e.element.select("form");t.attr("method","get").on("submit",function(s){s.preventDefault(),t.selectAll("input").property("disabled",!1);const a=new FormData(s.target),r=z(Object.fromEntries(a.entries()));return e.primary_callback.bind(e)(r),!1})}}const $t=new bt({id:"find-node-drawer",title:"Find Node",children:[new St({id:"find-node-ui"})],exit_callback:()=>{p(_,"state.graph.nodes").map(e=>me(e)),_.dispatch("foundNodeIds",{}),_.dispatch("editorUpdate")}}),jt=n=>{n.color="orange",n.size=40},me=n=>{n.color=void 0,n.size=void 0},Ot=n=>{let e=p(_,"state.graph.nodes"),t=e.filter(a=>a.id.includes(n));e.map(a=>me(a));let s=[];for(let a of t)a&&s.push(a);if(s.length){for(let a of s)jt(a);_.dispatch("foundNodeIds",{found_node_ids:s.map(a=>a.id)})}_.dispatch("editorUpdate")};class Tt extends v{constructor(e){super({store:_})}get selected_node_id(){return p(this,"store.state.selected_node_id")}update(){let e=this.selected_node_id?`Node: ${this.selected_node_id.toString()}`:'<div class="pt-20">🡄  Select a Node in the Editor Map<div>';this.element.html(e)}_render(){let e=this;e.element=h.select(`#${e.parent_id}-content`).append("div").classed("text-lg font-bold pb-2",!0),e.update(),e.store.events.subscribe("changedSelectedNode",()=>e.update())}}class Lt extends v{constructor(e){super({store:_});let t=this;t.store.events.subscribe("changedSelectedNode",()=>t.update())}get nodes(){return p(this,"store.state.graph.nodes")}get selected_node_id(){return p(this,"store.state.selected_node_id")}toggleNodeType(){let e=this.element.select("input:checked").property("value");this.store.dispatch("nodeEditorType",{node_editor_type:e||"none"})}_template(){return`
<div id="type-form" class="flex items-center justify-center">

  <!-- Component Start -->
  <form class="grid grid-cols-2 grid-rows-2 gap-2 w-full ">
    <div>
      <input class="hidden" id="radio_1" type="radio" name="radio" value="land_surface">
      <label title="Land Surfaces" class="button-radio-label bg-[#32cd32]" for="radio_1">
        <span>Land Surface</span>
      </label>
    </div>
    <div>
      <input class="hidden" id="radio_2" type="radio" name="radio" value="treatment_facility">
      <label class="button-radio-label bg-[#4682b4]" for="radio_2">
        <span>Treatment Facility</span>
      </label>
    </div>

    <div>
    <!-- <input class="hidden" id="radio_3" type="radio" name="radio" value="treatment_site"> -->
      <label title="Treatment Site (disabled)" class="button-radio-label bg-[#ffa500]" for="radio_3">
        <span>Treatment Site</span>
      </label>
    </div>

    <div>
      <input class="hidden" id="radio_4" type="radio" name="radio" value="none" checked>
      <label class="button-radio-label bg-gray-600" for="radio_4">
        <span>None</span>
      </label>
    </div>
  </form>
  <!-- Component End  -->

</div>`}update(){let e=this;e.element.classed("hidden",e.selected_node_id==null);let t=this.nodes.find(s=>s.id===this.selected_node_id);e.element.select(`input[value=${(t==null?void 0:t.node_type)||"none"}]`).property("checked",!0).dispatch("change"),e.toggleNodeType()}_render(){let e=this;e.element=h.select(`#${e.parent_id}-content`).append("div").classed("hidden",!0),e.element.html(e._template()),e.element.selectAll("input").on("change",this.toggleNodeType.bind(this)),e.update()}}const Et="modulepreload",Mt=function(n){return"/app/"+n},X={},J=function(e,t,s){let a=Promise.resolve();if(t&&t.length>0){document.getElementsByTagName("link");const i=document.querySelector("meta[property=csp-nonce]"),c=(i==null?void 0:i.nonce)||(i==null?void 0:i.getAttribute("nonce"));a=Promise.allSettled(t.map(u=>{if(u=Mt(u),u in X)return;X[u]=!0;const m=u.endsWith(".css"),l=m?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${u}"]${l}`))return;const o=document.createElement("link");if(o.rel=m?"stylesheet":Et,m||(o.as="script"),o.crossOrigin="",o.href=u,c&&o.setAttribute("nonce",c),document.head.appendChild(o),m)return new Promise((d,f)=>{o.addEventListener("load",d),o.addEventListener("error",()=>f(new Error(`Unable to preload CSS for ${u}`)))})}))}function r(i){const c=new Event("vite:preloadError",{cancelable:!0});if(c.payload=i,window.dispatchEvent(c),!c.defaultPrevented)throw i}return a.then(i=>{for(const c of i||[])c.status==="rejected"&&r(c.reason);return e().catch(r)})};async function Nt(n,e){let s=Object.assign({data:[{}],clipboard:!0,clipboardPasteAction:"update",minHeight:100,autoResize:!1,layout:"fitData",responsiveLayout:!1,history:!0,tooltipsHeader:!0,footerElement:'<div class="tabulator-footer"></div>',columns:[]},e),{Tabulator:a,EditModule:r,FormatModule:i,HistoryModule:c,InteractionModule:u,MenuModule:m,ResizeColumnsModule:l,SelectRowModule:o,SortModule:d}=await J(async()=>{const{Tabulator:f,EditModule:g,FormatModule:S,HistoryModule:y,InteractionModule:k,MenuModule:O,ResizeColumnsModule:b,SelectRowModule:E,SortModule:j}=await import("./tabulator-COzAoRaa.js");return{Tabulator:f,EditModule:g,FormatModule:S,HistoryModule:y,InteractionModule:k,MenuModule:O,ResizeColumnsModule:b,SelectRowModule:E,SortModule:j}},[]);return a.registerModule([a,r,i,c,u,m,l,o,d]),new a(n,s)}class Ct extends v{constructor(e){super({store:_})}get node_editor_type(){return p(this,"store.state.node_editor_type")}get selected_node(){let e=p(this,"store.state.selected_node_id");return p(this,"store.state.graph.nodes").find(s=>s.id===e)}landSurfaceTableOptions(){var s,a;let e=this,t=[{}];return(s=e.selected_node)!=null&&s.data?t=w(e.selected_node.data):t=[{node_id:(a=e.selected_node)==null?void 0:a.id}],{data:t,maxHeight:"500px",rowContextMenu:[{label:"<i class='fas fa-check-square'></i> Select Row",action:function(r,i){i.select()}},{label:"<i class='fas fa-trash'></i> Add Row",action:function(r,i){var c;e.table.addRow({node_id:(c=e.selected_node)==null?void 0:c.id})}},{label:"<i class='fas fa-trash'></i> Delete Row",action:function(r,i){e.table.getRows().length>1&&i.delete()}}],initialSort:[{column:"surface_key",dir:"asc"}],columns:[{title:"Node Id",field:"node_id",editor:"input",editable:r=>r.getRow().getPosition()==1},{title:"Surface Key",field:"surface_key",editor:"input"},{title:"Area (acres)",field:"area_acres",hozAlign:"center",editor:!0,width:90},{title:"Impervious Area (acres)",field:"imp_area_acres",hozAlign:"center",editor:!0,width:90}]}}setCurrentNodeDataToTableData(){var a;if(!this.selected_node)return alert("no node selected"),!1;let e=w(this.table.getData()),t=this.selected_node,s=(a=e[0])==null?void 0:a.node_id;e.forEach(r=>r.node_id=s),t.node_type=this.node_editor_type,t.id!==s&&(t.id=s,_.dispatch("changedSelectedNode",{selected_node_id:s})),t.data=e,this.store.dispatch("newGraph"),this.update()}async buildLandSurfaceTable({id:e}){let t=this;t.element.select(`#${e}`).remove();let s=t.element.append("div").attr("id",e).classed("grid grid-cols-1 grid-rows-auto pt-8",!0);const a=e+"-landsurface-tabulator";let r=s.append("div").classed("flex flex-row p-2 gap-2",!0),i=r.append("button").classed("btn btn-gray flex flex-row",!0).html(`
      <span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
        </svg>
      </span>
      <span>undo</span>
      `),c=r.append("button").classed("btn btn-gray flex flex-row",!0).html(`
      <span>redo</span>
      <span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" />
        </svg>
      </span>

      `);s.append("div").attr("id",a);let u=t.landSurfaceTableOptions();t.table=await Nt(`#${a}`,u),i.on("click",()=>t.table.undo()),c.on("click",()=>t.table.redo()),s.append("div").classed("flex flex-row justify-end py-4",!0).append("button").classed("btn btn-blue",!0).on("click",()=>{this.setCurrentNodeDataToTableData.bind(this)()}).text("Apply")}async update(){let e=this;if(e.node_editor_type!=="land_surface"){e.element.classed("hidden",!0);return}e.element.classed("hidden",!1);let t=`${e.parent_id}-content-editor`;await e.buildLandSurfaceTable({id:t})}_render(){let e=this;e.element=h.select(`#${e.parent_id}-content`).append("div").classed("mt-4",!0).classed("hidden",!0),e.update(),e.store.events.subscribe("nodeEditorType",()=>e.update()),e.store.events.subscribe("changedSelectedNode",()=>e.update()),e.store.events.subscribe("changedPanel",()=>e.update()),e.store.events.subscribe("newGraph",()=>e.update())}}class Dt extends v{constructor(e){super({store:_})}get node_editor_type(){return p(this,"store.state.node_editor_type")}get selected_node(){let e=p(this,"store.state.selected_node_id");return p(this,"store.state.graph.nodes").find(s=>s.id===e)}get config(){let{schema:e,facility_types:t,facility_type_map:s,facility_alias_map:a,facility_label_map:r}=p(this,"store.state");return{schema:e,facility_types:t,facility_type_map:s,facility_alias_map:a,facility_label_map:r}}update(){let e=this;e.element.html("").classed("flex flex-col w-full",!0),e.element.classed("hidden",e.node_editor_type!=="treatment_facility");let t=e.element.append("select").classed("px-2 my-4 h-8 border rounded-md",!0).attr("id","facility-picker").on("change",function(){var f,g,S,y,k,O;let r=e.element.select("#facility-picker").property("value");if(!r.length)return!1;let i=e.config.facility_type_map[r],c=w(p(e,"selected_node.data")||{});Array.isArray(c)&&(c={});let u={node_id:e.selected_node.id,facility_type:r,ref_data_key:((g=(f=e.selected_node)==null?void 0:f.data)==null?void 0:g.ref_data_key)||((S=e.selected_node)==null?void 0:S.ref_data_key),design_storm_depth_inches:((k=(y=e.selected_node)==null?void 0:y.data)==null?void 0:k.design_storm_depth_inches)||((O=e.selected_node)==null?void 0:O.design_storm_depth_inches)};u=Object.assign(c,u);const m=b=>{e.selected_node.node_type=e.node_editor_type,e.selected_node.data=Object.assign({facility_type:e.element.select("#facility-picker").property("value")},w(b)),e.selected_node.id=b.node_id,e.store.dispatch("newGraph")};let l=p(e,"store.state.nereid_state"),o=p(e,"store.state.nereid_region"),d=p(e,`store.state.treatment_facility_fields.${l}.${o}`)||p(e,"store.state.treatment_facility_fields.state.region");console.debug("tmnt facility fields:",d),At("#facility-form",e.config.schema[i],u,d.disabled,d.ignored,m.bind(e))});e.element.append("div").attr("id","facility-form");let s=w(e.config.facility_types||[]);s.unshift(""),t.selectAll("option").data(s).enter().append("option").attr("value",r=>r&&e.config.facility_label_map[r]).text(r=>r);let a=p(e,"selected_node.data.facility_type");a&&(e.element.select("#facility-picker").property("value",a),t.on("change")())}_render(){let e=this;e.element=h.select(`#${e.parent_id}-content`).append("div"),e.id=`${e.parent_id}-content-treatment-form`,e.element.attr("id",e.id),e.update(),e.store.events.subscribe("stateChange",()=>this.update())}}function At(n,e,t,s,a,r){let i=[...e.required],c=Object.keys(e.properties).filter(d=>!i.includes(d));i.push(...c);let u=[];for(const d of i.filter(f=>!a.includes(f))){let f=e.properties[d];f.name=d,u.push(f)}let m=h.select(n);m.html("");let l=m.append("form");l.attr("id",n.replace("#","")+"-form").attr("name",n.replace("#","")+"-form").attr("method","get").on("submit",function(d){d.preventDefault(),l.selectAll("input").property("disabled",!1);const f=new FormData(d.target),g=z(Object.fromEntries(f.entries()));return r&&r(g),!1}),l.selectAll("div").data(u).enter().append("div").classed("form-group flex flex-row w-full gap-4 text-sm my-4 h-8 items-center",!0).classed("required",d=>e.required.includes(d.name)).each(function(d,f){let g=e.required.includes(d.name),S=(d.description||d.name)+(g?" (required)":" (optional)"),y=h.select(this);y.append("label").classed("control-label py-2 flex w-1/2 ",!0).attr("title",S).text(d.title);let k;function O(b){if((b==null?void 0:b.anyOf)==null)return b;for(let E of["boolean","number","string"])for(let j of b.anyOf)if(j.type===E)switch(j.type){case"boolean":return b.type="boolean",b.default=(j==null?void 0:j.default)||!1,b;case"number":return b.type="number",b;case"string":return b.type="string",b}return b}switch(d=O(d),d.type){case"string":k=y.append("input").attr("name",d.name).attr("id",d.name).attr("title",S).property("required",e.required.includes(d.name||"")).property("disabled",s.includes(d.name)).classed("border-2 rounded-md px-2 py-1",!0),k.attr("type","text").attr("pattern",(d==null?void 0:d.pattern)||".*").attr("value",[d==null?void 0:d.example,d==null?void 0:d.default,""].find(b=>b!=null));break;case"number":k=y.append("input").attr("name",d.name).attr("id",d.name).attr("title",S).property("required",e.required.includes(d.name||"")).property("disabled",s.includes(d.name)).classed("border-2 rounded-md px-2 py-1",!0),k.attr("type","number").attr("step","0.001").attr("value",[d==null?void 0:d.example,d==null?void 0:d.default,""].find(b=>b!=null));break;case"boolean":k=y.append("div").classed("flex flex-row",!0);for(let b of[!0,!1]){let E=d.name+b.toString(),j=k.append("div").classed("flex flex-row items-center",!0);j.append("input").classed("form-check-input p-2",!0).classed("p-2",!0).attr("type","radio").attr("name",d.name).attr("id",E).attr("title",S).property("checked",d.default==b).property("disabled",s.includes(d.name)).attr("value",b),j.append("label").classed("p-2",!0).attr("for",E).attr("title",S).text(b.toString())}break}});for(let[d,f]of Object.entries(t))if(["true","false"].includes(f))for(let g of["true","false"])h.select("#"+d+g).property("checked",f==g);else h.select("#"+d).property("value",f);let o=l.append("div").classed("flex justify-end",!0);o.append("div"),o.append("button").classed("btn btn-blue",!0).attr("type","submit").text("Apply")}const Rt=new Tt,zt=new Lt,Ft=new Ct,Pt=new Dt,It=new vt({id:"node-editor-drawer",title:"Edit Nodes",children:[Rt,zt,Ft,Pt]});class U extends v{constructor(e){super({store:_});let t=this;t.id=e.id,t.title=e.title,t.data=[{}],t.data_callback=e.data_callback||function(s){console.debug("loaded data: ",s)},t.primary_callback=e.primary_callback||function(){console.debug(`clicked primary button load files UI ${t.id}`)},t.primary_button_label=e.primary_button_label||"Apply",t.secondary_callback=e.secondary_callback||null,t.secondary_button_label=e.secondary_button_label||"Update"}_template_primary_button(){return this.primary_callback==null?"":`<button
    class="
      rounded-r-lg
      text-xs
      h-10
      font-bold
      py-2
      px-4
      btn-blue
      w-20
    "
    type="button"
    id="${this.id}-primary-button"
  >
    ${this.primary_button_label}
  </button>`}_template_secondary_button(){return this.secondary_callback==null?"":`<button
    class="
      text-xs
      h-10
      font-bold
      py-2
      px-4
      btn-gray
      w-20
    "
    type="button"
    id="${this.id}-secondary-button"
  >
    ${this.secondary_button_label}
  </button>`}_template(){return`
      <div id="${this.id}" class="px-2 pb-10">
      <div class="pb-2"><strong>${this.title}</strong></div>

      <div class="">
        <div
          class="
            relative
            flex flex-row
            h-10
            items-center
            border
            shadow
            rounded-lg
          "
        >
          <div class="relative w-full flex flex-row items-center">
            <input
              type="file"
              class="absolute opacity-0 w-full h-10"
              id="${this.id}-file"
              aria-describedby="${this.id}-file"
            />
            <label
              id="${this.id}-file-label"
              class="relative pl-4 w-full appearance-none text-gray-300 pointer-events-none"
              for="${this.id}-file"
              >browse...</label
            >
          </div>
          ${this._template_secondary_button()}
          ${this._template_primary_button()}
        </div>
      </div>
    </div>`}loadFileAsJson(e,t){let s=e.target.files[0];if(!s.type.match("csv|excel|json")){alert("csv or json please");return}let a=this,r=new FileReader;r.onload=function(i){return function(c){let u;i.type.match("csv|excel")?u=h.csvParse(c.target.result):i.type.match("json")&&(u=JSON.parse(c.target.result)),u=Array.isArray(u)?u.map(m=>z(m)):u,a.data=u,e.target.value=""}}(s),r.readAsText(s)}_render(){let e=this;e.element=h.select(`#${e.parent_id}-content`).append("div"),e.element.html(e._template()),e.primary_button=e.element.select(`#${this.id}-primary-button`),e.primary_button.on("click",()=>{e.data_callback.bind(e)(e.data),e.primary_callback.bind(e)(),e.element.select(`#${this.id} label`)}),e.secondary_button=e.element.select(`#${this.id}-secondary-button`),e.secondary_button.on("click",()=>{e.data_callback.bind(e)(e.data),e.secondary_callback.bind(e)(),e.element.select(`#${this.id} label`)}),e.input=e.element.select(`#${this.id} input`),e.input.on("change",t=>{e.loadFileAsJson.bind(e)(t);let s=e.element.select(`#${this.id} label`);s.text(t.target.files[0].name),s.classed("font-bold",!0);let a=s.node();a.className=a.className.replace(/\btext-gray-.+?\b/g,""),a.classList.add("text-gray-700")})}}const Vt=new U({id:"graph-file-loader",title:"Load Graph (.csv)",primary_callback:V,secondary_callback:ue,data_callback:function(e){let t=[...new Set(e.map(m=>m.source).concat(e.map(m=>m.target)))],s=w(this.store.state.graph.nodes.filter(m=>t.includes(m.id))||[{}]),a=s.map(m=>m.id),r=[],i=50,c=50,u;for(let m of t){if(a.includes(m))u=s.find(l=>l.id===m);else{let l=e.find(o=>o.source===m);u={id:m,x:+(l==null?void 0:l.x)||i+10*Math.random(),y:+(l==null?void 0:l.y)||c+10*Math.random()},(l!=null&&l.x||l!=null&&l.y)&&(u.fx=+(l==null?void 0:l.x),u.fy=+(l==null?void 0:l.y))}r.push(u)}this.store.dispatch("setStagedChanges",{staged_changes:{edges:e,nodes:r}})}}),Bt=new U({id:"land-surface-file-loader",title:"Load Land Surfaces (.csv)",primary_callback:V,data_callback:function(e){var u,m;let t=[...new Set(e.map(l=>l.node_id))],s=w(p(this,"store.state.graph.nodes")),a=w(p(this,"store.state.graph.edges")).map(l=>({source:l.source.id,target:l.target.id})),r=s.map(l=>l.id),i=[],c=()=>400*Math.random();for(let l of t){let o=e.filter(y=>y.node_id===l),d,f=H((u=o.filter(y=>y==null?void 0:y.long))==null?void 0:u.map(y=>+y.long)),g=H((m=o.filter(y=>y==null?void 0:y.lat))==null?void 0:m.map(y=>+y.lat)),S=o.map(({node_id:y,surface_key:k,area_acres:O,imp_area_acres:b})=>({node_id:y,surface_key:k,area_acres:O,imp_area_acres:b}));r.includes(l)?(d=s.find(y=>y.id===l),d.node_type="land_surface",d.data=S,f&&g&&(d.longlat=[+f,+g])):(d={id:l,node_type:"land_surface",x:c(),y:c(),data:S},f&&g&&(d.longlat=[+f,+g]),i.push(d))}s=s.concat(i),this.store.dispatch("setStagedChanges",{staged_changes:{edges:a,nodes:s}})}}),Ut=new U({id:"treatment-facilities-file-loader",title:"Load Treatment Facilities (.csv)",primary_callback:V,data_callback:function(e){let t=[...new Set(e.map(u=>u.node_id))],s=w(p(this,"store.state.graph.nodes")||[{}]),a=w(p(this,"store.state.graph.edges")||[{}]).map(u=>({source:u.source.id,target:u.target.id})),r=s.map(u=>u.id),i=[],c=()=>400*Math.random();for(let u of t){let m=e.find(f=>f.node_id===u),l,{long:o,lat:d}=m;r.includes(u)?(l=s.find(f=>f.id===u),l.data=m,l.node_type="treatment_facility",o&&d&&(l.longlat=[+o,+d])):(l={id:u,node_type:"treatment_facility",x:c(),y:c(),data:m},o&&d&&(l.longlat=[+o,+d]),i.push(l))}s=s.concat(i),this.store.dispatch("setStagedChanges",{staged_changes:{edges:a,nodes:s}})}}),Wt=new U({id:"scenario-file-loader",title:"Load Scenario (.json)",primary_callback:V,secondary_callback:ue,data_callback:function(e){let t=e.graph,s=e.name,a=w(t.nodes||[{}]);for(let i of a)i.id==null&&console.error("bad egg:",i);let r=t.edges.map(i=>({source:i.source.id,target:i.target.id}));this.store.dispatch("setStagedChanges",{staged_changes:{edges:r,nodes:a,scenario_name:s}})}}),qt=new wt({id:"load-table-drawer",title:"Load from File",children:[Vt,Bt,Ut,Wt]});class Ht extends v{constructor(e){super({store:_,id:e.id})}get scenario_name(){return p(this.store,"state.scenario_name")}get scenario(){return{name:this.scenario_name,graph:p(this,"store.state.graph")}}saveScenarioBlob(){let e={filename:(this.scenario.name.replaceAll(" ","_")||"scenario")+".json",json:JSON.stringify(this.scenario,void 0,2)},t=new Blob([e.json],{type:"text/plain;charset=utf-8"});W.saveAs(t,e.filename)}dumpScenario(){let e=`<pre>${JSON.stringify(this.scenario,void 0,2)}</pre>`;this.element.select("#dump-scenario-text").html(e)}clearScenario(){this.element.select("#dump-scenario-text").html("")}_template(){return`
<div>
  <div class="flex flex-row w-full p-4 justify-between items-center"><strong>Save Scenario to File (json)</strong>
      <button
        id="save-scenario"
        class="btn btn-blue"
      >
        Save
      </button>
  </div>
  <div  class="flex flex-row w-full p-4 justify-between items-center gap-2">
    <strong>Print Scenario for Review (json)</strong>
      <button
        id="dump-scenario"
        class="btn btn-gray py-0.5 px-1"
      >
        Print
      </button>
      <button
        id="clear-scenario"
        class="btn btn-gray py-0.5 px-1"
      >
        Clear
      </button>
  </div>
  <div id="dump-scenario-text"></div>
</div>

  `}_render(){let e=this;e.element=h.select(`#${e.parent_id}-content`).append("div").attr("id",e.id),e.element.html(e._template()),e.button=e.element.select("#save-scenario"),e.button.on("click",e.saveScenarioBlob.bind(e)),e.button=e.element.select("#dump-scenario"),e.button.on("click",e.dumpScenario.bind(e)),e.button=e.element.select("#clear-scenario"),e.button.on("click",e.clearScenario.bind(e))}}class Gt extends v{constructor(e){super({store:_,id:e.id})}get facility_types(){return Object.keys(p(this,"store.state.facility_type_map"))}get facility_type_map(){return p(this,"store.state.facility_type_map")}get schema(){return p(this,"store.state.schema")}get scenario_name(){return p(this.store,"state.scenario_name")}get facility_properties(){let e=new Set;for(let t of this.facility_types){let s=this.facility_type_map[t],a=this.schema[s];Object.keys(a.properties).forEach(e.add,e)}return["long","lat"].forEach(e.add,e),e}get facility_data(){let e=this.facility_properties,t=[],s=w(p(this,"store.state.graph.nodes")||[{}]).filter(a=>a.node_type=="treatment_facility");return s.length==0&&(s=[{}]),s.forEach(a=>{let r={};for(let c of e)r[c]=p(a.data,c)||"";let i=(a==null?void 0:a.longlat)||["",""];r.long=i[0],r.lat=i[1],t.push(r)}),t}facility_template(){let e=this,t=[],s=p(e,"store.state.nereid_state"),a=p(e,"store.state.nereid_region"),r=p(e,`store.state.treatment_facility_fields.${s}.${a}`),i=[...this.facility_properties].filter(c=>!r.ignored.includes(c));for(let[c,u]of Object.entries(this.facility_type_map)){let m=this.schema[u],l={};for(let o of i){let d=p(m.properties[o],"type")||"";m.required.includes(o)&&(d+="-req"),r.disabled.includes(o)&&(d+="-uneditable"),l[o]=d}l.long="number",l.lat="number",l.facility_type=c,t.push(l)}return t}saveTreatmentCSV(){let e=this.facility_data,s={filename:`${this.scenario_name.replaceAll(" ","-")}-treatment_facilities.csv`,csv:G({data:e})},a=new Blob([s.csv],{type:"text/plain;charset=utf-8"});W.saveAs(a,s.filename)}saveTreatmentTemplateCSV(){let e=this.facility_template(),t=p(this,"store.state.nereid_state"),s=p(this,"store.state.nereid_region"),a={filename:`${t}-${s}-treatment_facilities-template.csv`,csv:G({data:e})},r=new Blob([a.csv],{type:"text/plain;charset=utf-8"});W.saveAs(r,a.filename)}_template(){return`
<div>
  <div class="flex flex-row w-full p-4 justify-between items-center"><strong>Save Treatment Facility Info to File (csv)</strong>
      <button
        id="save-tmnt"
        class="btn btn-blue"
      >
        Save
      </button>
  </div>
</div
<div>
  <div class="flex flex-row w-full p-4 justify-between items-center"><strong>Save Treatment Facility Template to File (csv)</strong>
      <button
        id="save-tmnt-template"
        class="btn btn-blue"
      >
        Save
      </button>
  </div>
</div
    `}_render(){let e=this;e.element=h.select(`#${e.parent_id}-content`).append("div").attr("id",e.id),e.element.html(e._template()),e.store.events.subscribe("updateConfig",()=>{}),e.element.select("#save-tmnt").on("click",e.saveTreatmentCSV.bind(e)),e.element.select("#save-tmnt-template").on("click",e.saveTreatmentTemplateCSV.bind(e))}}const Jt=new Ht({id:"save-scenario"}),Xt=new Gt({id:"save-tmnt-facility"}),Qt=new xt({id:"save-files-drawer",title:"Save to File",children:[Jt,Xt]}),Yt=new kt({children:[$t,It,qt,Qt]}),Zt=new He({id:"editor-tab",children:[Ke,R,lt,dt,yt,Yt]});async function Q(n,e){let{default:t}=await J(async()=>{const{default:l}=await import("./xlsx-CIb8K_6G.js");return{default:l}},[]),{Tabulator:s,DownloadModule:a,ExportModule:r,FormatModule:i,ResizeColumnsModule:c}=await J(async()=>{const{Tabulator:l,DownloadModule:o,ExportModule:d,FormatModule:f,ResizeColumnsModule:g}=await import("./tabulator-COzAoRaa.js");return{Tabulator:l,DownloadModule:o,ExportModule:d,FormatModule:f,ResizeColumnsModule:g}},[]);s.registerModule([a,r,i,c]);let m=Object.assign({data:[{}],maxHeight:"500px",minHeight:80,autoResize:!1,layout:"fitData",responsiveLayout:!1,history:!1,tooltipsHeader:!0,footerElement:'<div class="tabulator-footer"></div>',columns:[],initialSort:[{column:"node_id",dir:"asc"}],dependencies:{XLSX:t}},e);return new s(n,m)}class fe extends v{constructor(e){super({store:_,id:e.id});let t=this;t.table_builders=e.table_builders||[],t.tables=[]}get scenario_name(){return p(this.store,"state.scenario_name")}async buildResultsSummary({id:e,data:t,prep_fnx:s,title:a,description:r,filename_csv:i}){let c=this;c.element.select(`#${e}`).remove();let u=c.element.append("div").attr("id",e).classed("grid grid-cols-1 grid-rows-auto pt-8",!0),m=u.append("div").classed(" flex flex-row w-full justify-between items-center",!0);m.append("div").classed("font-bold",!0).html(a);const[l,o]=s(t);if(!l.length){u.append("div").classed("flex justify-center",!0).html("no results to show for this summary yet...");return}let d=m.append("div").classed("py-2",!0).append("button").text("Download Data (csv)").classed("btn btn-blue",!0);r!=null&&u.append("div").html(r);const f=e+"-results-tabulator";u.append("div").attr("id",f);let g=await Q(`#${f}`,{data:l,columns:o.map(y=>{let k={title:y.replaceAll("_"," "),field:y,titleDownload:y};return["_acres","_coeff","_load","_pct","_conc","_lbs","_cuft","_cfs","_mpn","_inhr"].some(b=>y.includes(b))&&(k.formatter="money",k.formatterParams={precision:2}),y.includes("_pct")&&(k.formatterParams={precision:2,symbol:"%",symbolAfter:"p"}),y.includes("_mpn")&&(k.formatterParams={precision:0}),k})});c.tables.push(g);let S=c.scenario_name.replaceAll(" ","-");d.on("click",()=>{g.download("csv",S+"-"+i)})}async update(e){let t=this;if(e=e||[],t.element.html(""),(e==null?void 0:e.length)>0){t.element.select("#dummy_table").remove(),t.element.append("div").attr("id","dummy_table").classed("hidden",!0);let s=await Q("#dummy_table");t.element.append("div").append("button").classed("btn btn-blue",!0).text("Download All Data Summaries (xlsx)").on("click",()=>{let r={};t.element.selectAll("[id$='-results-tabulator']").nodes().forEach(i=>{let c=h.select(i).attr("id"),u=c.replace("-results-tabulator","").replace("table-","").replace("facility-","bmp-").slice(0,30);c.includes("table-all-data")||(r[u]="#"+c)}),t.element.select("#dummy_table").remove(),t.element.append("div").attr("id","dummy_table").classed("hidden",!0),s.download("xlsx","AllData.xlsx",{sheets:r})})}F();try{for(let s of t.table_builders)await t.buildResultsSummary(s(e))}finally{P()}}_template(){return`
      <div>Click 'Run Scenario' in the Editor to calculate results.</div>
    `}_render(){let e=this;e.element=h.select(`#${e.id}`).classed("relative flex justify-center",!0).append("div").classed("flex flex-col relative max-w-screen-md py-10 ",!0).html(e._template()),e.store.events.subscribe("newResults",({results:t})=>e.update(t)),e.store.events.subscribe("changedTab",({current_tab:t})=>{if(t===e.id){let s=p(e,"store.state.results");e.update(s)}})}}const Kt=n=>({data:n,id:"table-facility-design-summary",title:"Facility design Summary",filename_csv:"facility_design_summary.csv",prep_fnx:t=>{const s=["node_id","facility_type","valid_model","design_intensity_inhr","design_volume_cuft_cumul"];return[(t||[]).filter(r=>r.node_type).filter(r=>r.node_type.includes("facility")).map(r=>Object.fromEntries(Object.entries(r).filter(([i,c])=>s.includes(i)))),s]}}),es=n=>({data:n,id:"table-facility-wet-weather-capture",title:"Facility Wet Weather Volume Capture Results",filename_csv:"wet_weather_volume_capture_results.csv",prep_fnx:t=>{const s=["node_id","facility_type","valid_model","captured_pct","treated_pct","retained_pct","bypassed_pct","peak_flow_mitigated_pct"];return[(t||[]).filter(r=>r.node_type).filter(r=>r.node_type.includes("facility")).map(r=>Object.fromEntries(Object.entries(r).filter(([i,c])=>s.includes(i)))),s]}});function ts(n){return{data:n,id:"table-facility-volume-reduction",title:"Facility Volume Reduction Results",filename_csv:"volume_reduction_results.csv",prep_fnx:t=>{let s=["node_id"];const a=["inflow","treated","retained","captured","bypassed"],i=[...new Set(x(t.map(o=>Object.keys(o))))].filter(o=>{let d=a.some(g=>o.endsWith(`dry_weather_flow_cuft_${g}`)),f=a.some(g=>o.endsWith(`runoff_volume_cuft_${g}`));return d||f}),c=function(o){return s.includes(o)||i.includes(o)};let u=(t||[]).filter(o=>o.node_type).filter(o=>o.node_type.includes("facility")).map(o=>Object.fromEntries(Object.entries(o).filter(([d,f])=>c(d))));const m=[...new Set(x(u.map(o=>Object.keys(o))))],l=s;for(let o of a){let d=m.filter(f=>f.includes(o)).sort((f,g)=>f.includes("winter")||f.includes("summer")?1:-1);l.push(...d)}return[u,l]}}}function ss(n){return{data:n,id:"table-facility-wet-weather-volume-reduction",title:"Facility Wet Weather Volume Reduction Results",filename_csv:"wet_weather_volume_reduction_results.csv",prep_fnx:t=>{let s=["node_id"];const a=["inflow","treated","retained","captured","bypassed"],i=[...new Set(x(t.map(o=>Object.keys(o))))].filter(o=>(a.some(f=>o.endsWith(`dry_weather_flow_cuft_${f}`)),a.some(f=>o.endsWith(`runoff_volume_cuft_${f}`)))),c=function(o){return s.includes(o)||i.includes(o)};let u=(t||[]).filter(o=>o.node_type).filter(o=>o.node_type.includes("facility")).map(o=>Object.fromEntries(Object.entries(o).filter(([d,f])=>c(d))));const m=[...new Set(x(u.map(o=>Object.keys(o))))],l=s;for(let o of a){let d=m.filter(f=>f.includes(o));l.push(...d)}return[u,l]}}}function as(n){return{data:n,id:"table-facility-dry-weather-volume-reduction",title:"Facility Dry Weather Volume Reduction Results",description:"(calculated as total of summer + winter)",filename_csv:"dry_weather_volume_reduction_results.csv",prep_fnx:t=>{let s=["node_id"];const a=["inflow","treated","retained","captured","bypassed"],i=[...new Set(x(t.map(o=>Object.keys(o))))].filter(o=>{let d=a.some(f=>o.endsWith(`dry_weather_flow_cuft_${f}`));return a.some(f=>o.endsWith(`runoff_volume_cuft_${f}`)),d}),c=function(o){return s.includes(o)||i.includes(o)};let u=(t||[]).filter(o=>o.node_type).filter(o=>o.node_type.includes("facility")).map(o=>Object.fromEntries(Object.entries(o).filter(([d,f])=>c(d))));for(let o of u)for(let d of a){let f=o[`summer_dry_weather_flow_cuft_${d}`],g=o[`winter_dry_weather_flow_cuft_${d}`];o[`total_dry_weather_volume_cuft_${d}`]=f+g}const m=[...new Set(x(u.map(o=>Object.keys(o))))],l=s;for(let o of a){let d=m.filter(f=>f.includes(o)).sort((f,g)=>f.includes("total")||f.includes("winter")||f.includes("summer")?1:-1);l.push(...d)}return[u,l]}}}function rs(n){return{data:n,id:"table-facility-total-volume-reduction",title:"Facility Total Volume Reduction Results",description:"(calculated as total of results for wet + summer + winter)",filename_csv:"total_volume_reduction_results.csv",prep_fnx:t=>{let s=["node_id"];const a=["inflow","treated","retained","captured","bypassed"],i=[...new Set(x(t.map(o=>Object.keys(o))))].filter(o=>{let d=a.some(g=>o.endsWith(`dry_weather_flow_cuft_${g}`)),f=a.some(g=>o.endsWith(`runoff_volume_cuft_${g}`));return d||f}),c=function(o){return s.includes(o)||i.includes(o)};let u=(t||[]).filter(o=>o.node_type).filter(o=>o.node_type.includes("facility")).map(o=>Object.fromEntries(Object.entries(o).filter(([d,f])=>c(d))));for(let o of u)for(let d of a){let f=o[`runoff_volume_cuft_${d}`],g=o[`summer_dry_weather_flow_cuft_${d}`],S=o[`winter_dry_weather_flow_cuft_${d}`];o[`total_volume_cuft_${d}`]=f+g+S}const m=[...new Set(x(u.map(o=>Object.keys(o))))],l=s;for(let o of a){let d=m.filter(f=>f.includes(o)).filter(f=>f.includes("total"));l.push(...d)}return[u,l]}}}function ns(n){return{data:n,id:"table-facility-load-reduction",title:"Facility Load Reduction Results",description:`These results are separated in to wet weather results,
    summer dry weather results, and winter dry weather results.`,filename_csv:"load_reduction_results.csv",prep_fnx:t=>{const s=["node_id"],a=function(l){let o=l.endsWith("lbs_removed")||l.endsWith("mpn_removed");return s.includes(l)||o},i=[...new Set(x(t.map(l=>Object.keys(l))))].filter(l=>{let o=l.endsWith("lbs_removed")||l.endsWith("mpn_removed"),d=!l.includes("dw");return o&&d});let c=(t||[]).filter(l=>l.node_type).filter(l=>l.node_type.includes("facility")).map(l=>Object.fromEntries(Object.entries(l).filter(([o,d])=>a(o))));const u=[...new Set(x(c.map(l=>Object.keys(l))))],m=s;for(let l of i.sort()){let o=u.filter(d=>d.includes(l)).sort((d,f)=>d.includes("total")||d.includes("winter")||d.includes("summer")?1:-1);m.push(...o)}return[c,m]}}}function is(n){return{data:n,id:"table-facility-total-load-reduction",title:"Facility Total Load Reduction Results",description:"(calculated as total of results for wet + summer + dry)",filename_csv:"total_load_reduction_results.csv",prep_fnx:t=>{let s=["node_id"];const r=[...new Set(x(t.map(l=>Object.keys(l))))].filter(l=>{let o=l.endsWith("lbs_removed")||l.endsWith("mpn_removed"),d=!l.includes("dw");return o&&d}),i=function(l){let o=l.endsWith("lbs_removed")||l.endsWith("mpn_removed");return s.includes(l)||o};let c=(t||[]).filter(l=>l.node_type).filter(l=>l.node_type.includes("facility")).map(l=>Object.fromEntries(Object.entries(l).filter(([o,d])=>i(o))));for(let l of c)for(let o of r){let d=l[o],f=l[`summer_dw${o}`],g=l[`winter_dw${o}`];l[`total_${o}`]=d+f+g}const u=[...new Set(x(c.map(l=>Object.keys(l))))],m=s;for(let l of r.sort()){let o=u.filter(d=>d.includes(l)).filter(d=>d.includes("total")).sort((d,f)=>d.includes("total")||d.includes("winter")||d.includes("summer")?1:-1);m.push(...o)}return[c,m]}}}function ls(n){return{data:n,id:"table-facility-wet-weather-load-reduction",title:"Facility Wet Weather Load Reduction Results",filename_csv:"wet_weather_load_reduction_results.csv",prep_fnx:t=>{const s=function(i){let c=["node_id"].includes(i),u=i.endsWith("lbs_removed")||i.endsWith("mpn_removed"),m=i.includes("dw");return c||u&&!m};let a=(t||[]).filter(i=>i.node_type).filter(i=>i.node_type.includes("facility")).map(i=>Object.fromEntries(Object.entries(i).filter(([c,u])=>s(c))));const r=[...new Set(x(a.map(i=>Object.keys(i))))];return[a,r]}}}function os(n){return{data:n,id:"table-facility-dry-weather-load-reduction",title:"Facility Dry Weather Load Reduction Results",description:`Includes summer dry weather, winter dry weather, and total dry
      weather results (calculated as summer + winter)`,filename_csv:"dry_weather_load_reduction_results.csv",prep_fnx:t=>{let s=["node_id"];const r=[...new Set(x(t.map(l=>Object.keys(l))))].filter(l=>{let o=l.endsWith("lbs_removed")||l.endsWith("mpn_removed"),d=!l.includes("dw");return o&&d}),i=function(l){let o=l.endsWith("lbs_removed")||l.endsWith("mpn_removed"),d=l.includes("dw");return s.includes(l)||o&&d};let c=(t||[]).filter(l=>l.node_type).filter(l=>l.node_type.includes("facility")).map(l=>Object.fromEntries(Object.entries(l).filter(([o,d])=>i(o))));for(let l of c)for(let o of r){let d=l[`summer_dw${o}`],f=l[`winter_dw${o}`];l[`total_dw${o}`]=d+f}const u=[...new Set(x(c.map(l=>Object.keys(l))))],m=s;for(let l of r.sort()){let o=u.filter(d=>d.includes(l)).sort((d,f)=>d.includes("total")||d.includes("winter")||d.includes("summer")?1:-1);m.push(...o)}return[c,m]}}}const ds=n=>({data:n,id:"table-land-surface-summary",title:"Land Surface Summary",filename_csv:"land_surface_summary.csv",prep_fnx:t=>{let s=["node_id","area_acres","ro_coeff","imp_pct"];return[(t||[]).filter(r=>(r==null?void 0:r.land_surfaces_count)>0).map(r=>Object.fromEntries(Object.entries(r))),s]}}),cs=n=>({data:n,id:"table-land-surface-load-summary",title:"Land Surface Loading Summary",filename_csv:"land_surface_load_summary.csv",prep_fnx:t=>{let s=["node_id"];const a=function(c){let u=c.endsWith("_load_lbs")||c.endsWith("_load_mpn");return s.includes(c)||u};let r=(t||[]).filter(c=>(c==null?void 0:c.land_surfaces_count)>0).map(c=>Object.fromEntries(Object.entries(c).filter(([u,m])=>a(u))));const i=[...new Set(x(r.map(c=>Object.keys(c))))];return console.debug("landsurface load summary:",r),[r,i]}}),us=[Kt,es,ts,rs,ss,as,ns,is,ls,os],ps=[ds,cs],ms=new fe({id:"treatment-facility-results-tab",table_builders:us}),fs=new fe({id:"land-surface-results-tab",table_builders:ps});class _s extends v{constructor(e){super({store:_,id:e.id})}_template(){return`
    <div class="markdown">
      <div class="flex justify-center pt-10 px-24">
        <div class="markdown_content prose prose-lg md:prose-2xl">
          how to coming soon...
        </div>
      </div>
    </div>
    `}async fetch_page(){let e=this,t=`${_.state.nereid_host}/static/pages/how_to`;F(),fetch(t,{method:"GET"}).then(s=>{if(s.status_code===200)return s.text().then(function(a){e.element.select(".markdown_content").html(a)})}).finally(P)}_render(){let e=this;e.element=h.select(`#${e.id}`).classed("relative flex flex-col justify-center",!0).html(e._template()),e.fetch_page()}}const hs=new _s({id:"how-to-tab"}),Y=new qe({children:[Zt,ms,fs,hs]});window.onload=async n=>{await ce(),new v({id:"app",children:[Y,Ve,Ue],class:"leading-normal tracking-normal container mx-auto"}).render(),window.nereid={tabs:Y,editor:R,util:ze,nereidUtil:Re,state:R.store.state},R.store.dispatch("updateConfig",{}),window.onresize=()=>{R.resize()}};

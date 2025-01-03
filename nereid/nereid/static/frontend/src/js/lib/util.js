import store from "./state.js";
import { getConfig } from "./nereid-api.js";

export const get = (object, path = "") =>
  path.split(".").reduce((o, x) => (o == undefined ? o : o[x]), object);

export const getTruthy = (obj, path = "") => {
  let m = get(obj, path);
  return m === undefined ? false : m;
};

// https://stackoverflow.com/a/1349426/7486933
export function randomString(length) {
  let result = "";
  let characters =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let charactersLength = characters.length;
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}

export const filter = (obj, includes = [], excludes = []) => {
  const filtered = Object.keys(obj)
    .filter((key) => (includes.length ? includes.includes(key) : true))
    .filter((key) => !excludes.includes(key))
    .reduce((newobj, key) => {
      return {
        ...newobj,
        [key]: obj[key],
      };
    }, {});
  return filtered;
};

export function cleanObject(obj) {
  return Object.entries(obj)
    .filter(([_, v]) => v != "" && v != null)
    .reduce(
      (acc, [k, v]) => ({ ...acc, [k]: v === Object(v) ? cleanObject(v) : v }),
      {}
    );
}

export function deepCopy(object) {
  return JSON.parse(JSON.stringify(object));
}

export function mean(array) {
  return array.length
    ? array.reduce((a, b) => a + b) / array.length
    : undefined;
}

export function flatten(a) {
  return Array.isArray(a) ? [].concat(...a.map(flatten)) : a;
}

export const incr_waiting = () => {
  let v = (get(store, "state.waiting") || 0) + 1;
  store.dispatch("Waiting", { waiting: v });
};

export const decr_waiting = () => {
  let v = (get(store, "state.waiting") || 0) - 1;
  if (v < 0) {
    console.error("waiting counter is negative");
    v = 0;
  }
  store.dispatch("Waiting", { waiting: v });
};

// fetch API wrappers for json retrieval

export async function getJsonResponse(url) {
  console.debug("fetching with get", url);
  incr_waiting();
  const response = await fetch(url, { method: "GET" })
    // .catch((error) => {
    //   alert(error);
    //   return {};
    // })
    .then((resp) => {
      console.debug("getJsonResponse response:", resp);
      if (resp.status == 200) {
        return resp.json();
      } else if (resp.status == 422) {
        // unprocessable entity
        // alert(`Unprocessable data from get ${resp.json()}`);
        // console.warn(resp.json());
        return resp.json();
      } else {
        throw new Error("got back " + resp.content);
      }
    })
    .then((data) => {
      console.debug("getJsonResponse data returned:", data);
      return data;
    })
    .finally(decr_waiting);

  return response;
}

export async function postJsonResponse(url, data) {
  console.debug("fetching with post", url, data);
  incr_waiting();

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((resp) => {
      console.debug("postJsonResponse response:", resp);
      if (resp.status == 200) {
        return resp.json();
      } else if (resp.status == 422) {
        // alert(`Unprocessable data from post ${resp.json()}`);
        return resp.json();
      } else {
        throw new Error("got back " + resp);
      }
    })
    .then((data) => {
      console.debug("postJsonResponse data returned:", data);
      return data;
    })
    .finally(decr_waiting);
  return response;
}

export const poll = ({ fn, validate, interval_milli, maxAttempts }) => {
  console.debug("Start poll...");
  let attempts = 0;

  const executePoll = async (resolve, reject) => {
    console.debug("- poll");
    const result = await fn();
    attempts++;
    console.debug(attempts, result);

    if (validate(result)) {
      return resolve(result);
    } else if (maxAttempts && attempts === maxAttempts) {
      return reject(new Error("Exceeded max attempts"));
    } else {
      setTimeout(executePoll, interval_milli, resolve, reject);
    }
  };

  return new Promise(executePoll);
};

export function convertArrayOfObjectsToCSV(args) {
  var result, ctr, keys, columnDelimiter, lineDelimiter, data;

  data = args.data || null;
  if (data == null || !data.length) {
    return null;
  }

  columnDelimiter = args.columnDelimiter || ",";
  lineDelimiter = args.lineDelimiter || "\n";

  keys = args.keys || Object.keys(data[0]);

  result = "";
  result += keys
    .map((x) => (String(x).includes(",") ? `"${x}"` : `${x}`))
    .join(columnDelimiter);
  result += lineDelimiter;

  data.forEach(function (item) {
    ctr = 0;
    keys.forEach(function (key) {
      if (ctr > 0) result += columnDelimiter;

      const value = String(item[key]);

      if (value.includes(",")) {
        result += `"${value}"`;
      } else {
        result += `${value}`;
      }
      ctr++;
    });
    result += lineDelimiter;
  });

  return result;
}

export const getConfigFromUrlQueryParams = async () => {
  const params = new URLSearchParams(window.location.search);

  let { state, region, host } = Object.fromEntries(params.entries());

  const cfg = await getConfig({
    nereid_host: host,
    nereid_state: state || store.state.nereid_state,
    nereid_region: region || store.state.nereid_region,
  });
  store.dispatch("updateConfig", cfg);
  console.debug(cfg);

  return false;
};

import * as array from "d3-array";
import * as color from "d3-color";
import * as drag from "d3-drag";
import * as dsv from "d3-dsv";
import * as scale from "d3-scale";
import * as scale_chromatic from "d3-scale-chromatic";
import * as select from "d3-selection";
import * as transition from "d3-transition";
import { json } from "d3-fetch";
import { Delaunay } from "d3-delaunay";
import * as geo from "d3-geo";
import * as zoom from "d3-zoom";
import * as tile from "d3-tile";

const d3 = Object.assign(
  {
    json,
    Delaunay,
  },
  select,
  scale,
  scale_chromatic,
  geo,
  color,
  drag,
  dsv,
  array,
  tile,
  transition,
  zoom
);

export default d3;

from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import pandas

from nereid.core.io import load_ref_data
from nereid.src.nomograph.interpolators import FlowNomograph, VolumeNomograph


@lru_cache()
def build_nomo(
    nomo_type: str,
    path: Path | str,
    x_col: str,
    t_col: str,
    y_col: str,
    **kwargs: dict,
) -> Any:
    df = pandas.read_csv(path)
    x = df[x_col]
    t = df[t_col]
    y = df[y_col]

    if nomo_type == "VolumeNomograph":
        return VolumeNomograph(x, t, y)

    elif nomo_type == "FlowNomograph":
        return FlowNomograph(x, t, y)

    else:
        raise NotImplementedError(f"unsupported nomograph type: {nomo_type}")


def get_volume_nomograph(context: dict[str, Any], nomo_path: str) -> VolumeNomograph:
    met_context = context.get("project_reference_data", {}).get("met_table", {})
    data_path = Path(context["data_path"])
    fpath = (data_path / nomo_path).resolve()
    nomo_params = next(
        filter(lambda n: n["file_key"] == "volume_nomograph", met_context["nomographs"])
    )
    nomo: VolumeNomograph = build_nomo("VolumeNomograph", path=fpath, **nomo_params)
    return nomo


def get_flow_nomograph(context: dict[str, Any], nomo_path: str) -> FlowNomograph:
    met_context = context.get("project_reference_data", {}).get("met_table", {})
    data_path = Path(context["data_path"])
    fpath = (data_path / nomo_path).resolve()
    nomo_params = next(
        filter(lambda n: n["file_key"] == "flow_nomograph", met_context["nomographs"])
    )
    nomo: FlowNomograph = build_nomo("FlowNomograph", path=fpath, **nomo_params)
    return nomo


def load_nomograph_mapping(context: dict[str, Any]) -> dict[str, Callable] | None:
    met_table, msg = load_ref_data("met_table", context)

    if met_table is None:
        return None

    data_path = Path(context["data_path"])

    met_context = context.get("project_reference_data", {}).get("met_table", {})

    nomos = met_context["nomographs"]

    nomo_map = {}
    for nomo in nomos:
        file_key = nomo["file_key"]
        obj_name = nomo["constructor"]
        files = met_table[file_key].unique()

        for file in files:
            nomo_map[file] = build_nomo(obj_name, data_path / file, **nomo)

    return nomo_map

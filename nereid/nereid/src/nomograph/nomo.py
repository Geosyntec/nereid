from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, Union

import pandas

from nereid.core.io import load_ref_data
from nereid.src.nomograph.interpolators import FlowNomograph, VolumeNomograph


@lru_cache()
def build_nomo(
    nomo_type: str, path: Union[Path, str], x_col: str, t_col: str, y_col: str
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


def get_volume_nomograph(context: Dict[str, Any], nomo_path: str) -> VolumeNomograph:
    met_context = context.get("project_reference_data", {}).get("met_table")
    data_path = Path(context["data_path"])
    fpath = (data_path / nomo_path).resolve()
    nomo: VolumeNomograph = build_nomo(
        "VolumeNomograph", path=fpath, **met_context["volume_nomo"]
    )
    return nomo


def get_flow_nomograph(context: Dict[str, Any], nomo_path: str) -> FlowNomograph:
    met_context = context.get("project_reference_data", {}).get("met_table")
    data_path = Path(context["data_path"])
    fpath = (data_path / nomo_path).resolve()
    nomo: FlowNomograph = build_nomo(
        "FlowNomograph", path=fpath, **met_context["flow_nomo"]
    )
    return nomo


def load_nomograph_mapping(context: Dict[str, Any]) -> Dict[str, Callable]:

    met_table, msg = load_ref_data("met_table", context)

    data_path = Path(context["data_path"])

    met_context = context.get("project_reference_data", {}).get("met_table")

    vol_nomo_context = met_context["volume_nomo"]
    flow_nomo_context = met_context["flow_nomo"]

    vol_nomos = [
        ("VolumeNomograph", file, vol_nomo_context)
        for file in met_table["volume_nomograph"].unique()
    ]
    flow_nomos = [
        ("FlowNomograph", file, flow_nomo_context)
        for file in met_table["flow_nomograph"].unique()
    ]

    nomo_map = {}
    for obj_name, file, nomo_context in vol_nomos + flow_nomos:
        nomo_map[file] = build_nomo(obj_name, data_path / file, **nomo_context)

    return nomo_map

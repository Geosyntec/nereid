from typing import List, Dict, Any, Union
from pathlib import Path
import json
from io import StringIO

import yaml
import pandas

from nereid.core.cache import cache_decorator

PathType = Union[Path, str]


@cache_decorator(ex=3600 * 24)  # expires in 24 hours
def _load_file(filepath: PathType) -> str:
    fp = Path(filepath)
    return fp.read_text()


def load_file(filepath: PathType) -> str:
    """wrapper to ensure the cache is called with an absolute path"""
    contents: str = _load_file(Path(filepath).resolve())
    return contents


def load_cfg(filepath: PathType) -> Dict[str, Any]:
    """load cached yaml file"""
    f = load_file(filepath)
    contents: Dict[str, Any] = yaml.safe_load(f)
    return contents


def load_multiple_cfgs(files: List[PathType]) -> Dict[str, Any]:
    """load and combine multiple cached config files"""
    conf: Dict[str, Any] = {}
    for file in files:
        conf.update(load_cfg(file))
    return conf


def load_json(filepath: PathType) -> Dict[str, Any]:
    """load cached json file"""
    f = load_file(filepath)
    contents: Dict[str, Any] = json.loads(f)
    return contents


def load_ref_data(filepath: PathType) -> pandas.DataFrame:
    if "json" in str(filepath):
        return pandas.read_json(load_file(filepath), orient="table")
    else:
        raise ValueError("Only 'json' and 'csv' files are supported")

from typing import List, Dict, Any, Union
from pathlib import Path
import json

import yaml

from nereid.core.cache import cache_decorator

PathType = Union[Path, str]


@cache_decorator(ex=3600 * 24)  # expires in 24 hours
def _load_file(filepath: PathType) -> str:
    fp = Path(filepath)
    return fp.read_text()


def load_file(filepath: PathType) -> str:
    """wrapper to ensure the cache is called with an absolute path"""
    return _load_file(Path(filepath).resolve())


def load_cfg(filepath: PathType):
    """load cached yaml file

    Returns
    -------
    dict

    """
    f = load_file(filepath)
    return yaml.safe_load(f)


def load_multiple_cfgs(files: List[PathType]) -> Dict[str, Any]:
    """load and combine multiple cached config files

    Returns
    -------
    dict

    """
    conf: Dict[str, Any] = {}
    for file in files:
        conf.update(load_cfg(file))
    return conf


def load_json(filepath: PathType) -> Dict[str, Any]:
    """load cached json file

    Returns
    -------
    dict

    """
    f = load_file(filepath)
    return json.loads(f)

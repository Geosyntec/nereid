from pathlib import Path

import nereid.core.io
import nereid.data
from nereid.core.io import load_multiple_cfgs


def test_io_load_multiple_cfgs():
    cfgbase = Path(nereid.core.io.__file__).parent.resolve() / "base_config.yml"
    cfgdata = (
        Path(nereid.data.__file__).parent.resolve()
        / "default_data"
        / "state"
        / "region"
        / "config.yml"
    )

    dct = load_multiple_cfgs(files=[cfgbase, cfgdata])
    assert "test" in dct
    assert "data_path" in dct

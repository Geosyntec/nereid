from pathlib import Path

import pytest

import nereid.core.io
import nereid.data
from nereid.core import io


def test_io_load_multiple_cfgs():
    cfgbase = Path(nereid.core.io.__file__).parent.resolve() / "base_config.yml"
    cfgdata = (
        Path(nereid.data.__file__).parent.resolve()
        / "default_data"
        / "state"
        / "region"
        / "config.yml"
    )

    dct = io.load_multiple_cfgs(files=[cfgbase, cfgdata])
    assert "test" in dct  # from cfgdata
    assert "default_data_directory" in dct  # from cfgbase


def test_load_ref_data():
    pytest.raises(ValueError, io.load_ref_data, "test.doc")

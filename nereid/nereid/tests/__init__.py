from nereid.core.config import nereid_path


def test(*args):  # pragma: no cover
    import pytest

    options = [str(nereid_path)]
    options.extend(list(args))
    return pytest.main(options)

from nereid.core.config import nereid_path


def test(*args):  # pragma: no cover
    try:
        import pytest
    except ImportError:
        raise ImportError("`pytest` is required to run the test suite")

    options = [str(nereid_path)]
    options.extend(list(args))
    return pytest.main(options)

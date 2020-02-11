from pathlib import Path
from typing import Union, Dict, Set, List

import nereid.tests.test_data

TEST_PATH = Path(nereid.tests.test_data.__file__).parent.resolve()


def get_payload(file):
    path = TEST_PATH / file
    return path.read_text()


def is_equal_subset(
    subset: Union[Dict, List, Set], superset: Union[Dict, List, Set]
) -> bool:
    """determine if all shared keys have equal value"""

    if isinstance(subset, dict):
        return all(
            key in superset and is_equal_subset(val, superset[key])
            for key, val in subset.items()
        )

    if isinstance(subset, list) or isinstance(subset, set):
        return all(
            any(is_equal_subset(subitem, superitem) for superitem in superset)
            for subitem in subset
        )

    # assume that subset is a plain value if none of the above match
    return subset == superset

from typing import Any, Dict, List

INCLUDE_TAGS = [
    "node_id",
    "_cumul",
    "_discharged",
    "_total_retained",
    "_total_removed",
]

EXCLUDE_TAGS = ["_total_discharged"]


def minimum_attrs(dct: Dict[str, Any]) -> List[str]:
    def f(x):
        return any(i in x for i in INCLUDE_TAGS) and not any(
            i in x for i in EXCLUDE_TAGS
        )

    return list(filter(f, dct.keys()))


def attrs_to_resubmit(collection: List[Dict[str, Any]]) -> List[str]:

    return list({k for data in collection for k in minimum_attrs(data)})

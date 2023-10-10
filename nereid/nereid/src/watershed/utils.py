from typing import Any

INCLUDE_TAGS = [
    "node_id",
    "_cumul",
    "_discharged",
    "_total_retained",
    "_total_removed",
]

EXCLUDE_TAGS = ["_total_discharged"]


def minimum_attrs(dct: dict[str, Any]) -> list[str]:
    def f(x):
        return any(i in x for i in INCLUDE_TAGS) and not any(
            i in x for i in EXCLUDE_TAGS
        )

    return list(filter(f, dct.keys()))


def attrs_to_resubmit(collection: list[dict[str, Any]]) -> list[str]:
    return list({k for data in collection for k in minimum_attrs(data)})

from typing import Any, Iterable

INCLUDE_TAGS = [
    "node_id",
    "_cumul",
    "_discharged",
    "_total_retained",
    "_total_removed",
]

EXCLUDE_TAGS = ["_total_discharged"]


def f(x):
    return any(i in x for i in INCLUDE_TAGS) and not any(i in x for i in EXCLUDE_TAGS)


def minimum_attrs(keys: Iterable[str]) -> list[str]:
    return list(filter(f, keys))


def attrs_to_resubmit(collection: list[dict[str, Any]]) -> list[str]:
    return minimum_attrs({k for data in collection for k in data})

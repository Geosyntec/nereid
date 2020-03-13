from typing import Dict, Any, Callable
from pathlib import Path
from functools import wraps
import logging

import pint

logging.getLogger("pint").setLevel(logging.ERROR)
ureg = pint.UnitRegistry()
ureg.load_definitions(str(Path(__file__).parent / "unit_def.txt"))


def update_reg_from_context(context: Dict[str, Any]) -> None:

    for reg in context.get("pint_unit_registry", []):
        ureg.define(reg)


def update_unit_registry(fxn: Callable) -> Callable:
    @wraps(fxn)
    def ureg_wrapper(*args, **kwargs):
        context = kwargs.get("context", None)
        if not context:
            raise ValueError("Context is required")
        update_reg_from_context(context=context)
        return fxn(*args, **kwargs)

    return ureg_wrapper

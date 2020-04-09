from typing import Dict, Any, Callable
from pathlib import Path
from functools import wraps, lru_cache
import logging

import pint

logging.getLogger("pint").setLevel(logging.ERROR)
ureg = pint.UnitRegistry()
ureg.load_definitions(str(Path(__file__).parent / "unit_def.txt"))


@lru_cache()
def conversion_factor_load_to_conc(
    load_unit: str, conc_unit: str, vol_unit: str = "cubic_feet"
) -> float:
    factor: float = (ureg(load_unit) / ureg(vol_unit)).to(conc_unit).magnitude
    return factor


@lru_cache()
def conversion_factor_conc_to_load(
    conc_unit: str, load_unit: str, vol_unit: str = "cubic_feet"
) -> float:
    factor: float = (ureg(vol_unit) * ureg(conc_unit)).to(load_unit).magnitude
    return factor


@lru_cache()
def conversion_factor_from_to(from_unit: str, to_unit: str) -> float:
    factor: float = ureg(from_unit).to(to_unit).magnitude
    return factor


def update_reg_from_context(context: Dict[str, Any]) -> None:

    for reg in context.get("pint_unit_registry", []):
        ureg.define(reg)


def update_unit_registry(fxn: Callable) -> Callable:
    @wraps(fxn)
    def ureg_wrapper(*args, **kwargs):
        context = kwargs.get("context")
        if not context:  # pragma: no cover
            raise ValueError("Context is required as a named keyword argument")
        update_reg_from_context(context=context)
        for cached_fxn in [
            conversion_factor_load_to_conc,
            conversion_factor_conc_to_load,
            conversion_factor_from_to,
        ]:
            cached_fxn.cache_clear()
        return fxn(*args, **kwargs)

    return ureg_wrapper


class Constants:
    CFS_per_ACRE_to_INHR = (
        (ureg("cubic_feet / second") / ureg("acres")).to("inches / hr").magnitude
    )

    INCH_ACRES_to_CUFT = (ureg("inches") * ureg("acres")).to("cubic_feet").magnitude

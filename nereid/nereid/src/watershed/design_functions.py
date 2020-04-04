from nereid.core.units import Constants
from nereid.core.utils import safe_divide


def design_volume_cuft(
    design_storm_depth_inches: float, effective_area_acres: float
) -> float:

    result: float = (
        design_storm_depth_inches * effective_area_acres * Constants.INCH_ACRES_to_CUFT
    )

    return result


def design_intensity_inhr(
    treatment_rate_cfs: float, effective_area_acres: float
) -> float:

    result: float = (
        safe_divide(treatment_rate_cfs, effective_area_acres)
        * Constants.CFS_per_ACRE_to_INHR
    )
    return result

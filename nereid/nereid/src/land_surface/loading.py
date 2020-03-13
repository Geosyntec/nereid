from typing import Dict, Any, List, Optional, Tuple
from copy import deepcopy

import pandas

from nereid.core.units import ureg

# TODO: implement fallback to e.g., "TRANS-B-10" rather than "401070-TRANS-B-10"
# in case ref data is missing.


## PMH: is the land clean or the dataframe?
def clean_land_surface_dataframe(df: pandas.DataFrame) -> pandas.DataFrame:
    """ Prepare dataframe to include columns describing the imperviousness,
    which is not provided by OCSurvey's API
    """
    df["imp_pct"] = df["imp_pct"].clip(0, 100)
    df["imp_area_acres"] = df["area_acres"] * (df["imp_pct"] / 100)

    return df


def detailed_volume_loading_results(df: pandas.DataFrame,) -> pandas.DataFrame:

    # method chaining with 'df.assign' looks better, but it's much less memory efficient
    df["imp_pct"] = 100 * df["imp_area_acres"] / df["area_acres"]
    df["perv_area_acres"] = df["area_acres"] - df["imp_area_acres"]
    df["imp_area_sqft"] = df["imp_area_acres"] * 43560
    df["perv_area_sqft"] = df["perv_area_acres"] * 43560
    df["imp_ro_depth_feet"] = df["imp_ro_depth_inches"] / 12
    df["perv_ro_depth_feet"] = df["perv_ro_depth_inches"] / 12
    df["imp_ro_volume_cuft"] = df["imp_ro_depth_feet"] * df["imp_area_sqft"]
    df["perv_ro_volume_cuft"] = df["perv_ro_depth_feet"] * df["perv_area_sqft"]
    df["runoff_volume_cuft"] = df["imp_ro_volume_cuft"] + df["perv_ro_volume_cuft"]
    df["imp_eff_area_acres"] = df["imp_ro_coeff"] * df["imp_area_acres"]
    df["perv_eff_area_acres"] = df["perv_ro_coeff"] * df["perv_area_acres"]
    df["eff_area_acres"] = df["imp_eff_area_acres"] + df["perv_eff_area_acres"]

    return df


## PMH: Docs with examples would be nice (specifically for the `parameters`
##      parameter)
def detailed_pollutant_loading_results(
    df: pandas.DataFrame, parameters: Optional[List[Dict[str, str]]] = None
) -> pandas.DataFrame:

    if parameters is None or len(parameters) == 0:
        return df

    for param in parameters:
        conc_unit = param["concentration_unit"]
        load_unit = param["load_unit"]
        poc = param["short_name"]
        emc_col = "_".join([poc, "conc", conc_unit.lower().replace("_", "")])
        load_col = "_".join([poc, "load", load_unit.lower().replace("_", "")])

        # EMC's aren't required as runoff volume might be the only thing
        # of interest
        if emc_col in df:
            factor = (ureg("cubic_feet") * ureg(conc_unit)).to(load_unit).magnitude
            df[load_col] = df["runoff_volume_cuft"] * df[emc_col] * factor

    return df


def detailed_loading_results(
    land_surfaces_df: pandas.DataFrame,
    parameters: Optional[List[Dict[str, str]]] = None,
) -> pandas.DataFrame:

    # fmt: off
    results = (
        land_surfaces_df
        .pipe(clean_land_surface_dataframe)
        .pipe(detailed_volume_loading_results)
        .pipe(detailed_pollutant_loading_results, parameters)
    )
    # fmt: on

    return results


def summary_loading_results(
    detailed_results: pandas.DataFrame, parameters: List[Dict[str, str]]
) -> pandas.DataFrame:

    GROUPBY_COLS = ["node_id"]
    load_cols = [
        "_".join([dct["short_name"], "load", dct["load_unit"]]) for dct in parameters
    ]

    output_columns_summable = [
        "area_acres",
        "imp_area_acres",
        "perv_area_acres",
        "imp_ro_volume_cuft",
        "perv_ro_volume_cuft",
        "runoff_volume_cuft",
        "eff_area_acres",
    ] + load_cols

    ## PMH suggestion for simplifcation
    # other_agg_reqs = {}
    # agg_dict = dict(**{col: "sum" for col in output_columns_summable}, **other_agg_reqs)
    agg_list = [
        {col: "sum" for col in output_columns_summable},
        # add other aggregation requirements for other columns here
    ]

    df = (
        detailed_results.reindex(columns=GROUPBY_COLS + output_columns_summable)
        .groupby(GROUPBY_COLS)
        .agg({k: v for d in agg_list for k, v in d.items()})
    )

    #  'area_acres' is just a dummy here, any column would do
    df["land_surfaces_count"] = detailed_results.groupby(GROUPBY_COLS)[
        "area_acres"
    ].count()

    df["imp_pct"] = 100 * (df["imp_area_acres"] / df["area_acres"])
    df["ro_coeff"] = df["eff_area_acres"] / df["area_acres"]

    df.reset_index(inplace=True)

    for param in parameters:
        conc_unit = param["concentration_unit"]
        load_unit = param["load_unit"]

        poc = param["short_name"]
        load_col = "_".join([poc, "load", load_unit.lower().replace("_", "")])
        conc_col = "_".join([poc, "conc", conc_unit.lower().replace("_", "")])
        factor = (ureg(load_unit) / ureg("cubic_feet")).to(conc_unit).magnitude

        df[conc_col] = (df[load_col] / df["runoff_volume_cuft"]) * factor

    return df

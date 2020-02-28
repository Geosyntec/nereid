from typing import Dict, Any, List

import pandas

from nereid.core.units import ureg

# TODO: implement fallback to e.g., "TRANS-B-10" rather than "401070-TRANS-B-10"
# in case ref data is missing.


def detailed_land_surface_volume_loading_results(
    land_surfaces_df: pandas.DataFrame,
) -> pandas.DataFrame:

    # method chaining with 'df.assign' looks better, but it's much less memory efficient
    df = land_surfaces_df

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


def detailed_land_surface_pollutant_loading_results(
    land_surfaces_df: pandas.DataFrame, parameters: List[Dict[str, str]]
) -> pandas.DataFrame:

    #  TODO: make this more flexible and units agnostic.
    convert_to_load = {
        "mg/l": (ureg("(mg/l)*(cubic_feet)").to("lbs").magnitude, "lbs"),
        "ug/l": (ureg("(ug/l)*(cubic_feet)").to("lbs").magnitude, "lbs"),
        "mpn/100ml": (
            ureg("(count/(100*ml)) * cubic_feet").to("count").magnitude,
            "mpn",
        ),  # count per cuft
    }

    df = land_surfaces_df

    for param in parameters:
        unit = param["unit"].lower()
        poc = param["short_name"]
        emc_col = "_".join([poc, "conc", unit])
        if emc_col in df:
            factor, to_unit = convert_to_load[unit]

            load_col = "_".join([poc, "load", to_unit])

            df[load_col] = df["runoff_volume_cuft"] * df[emc_col] * factor

    return df


def detailed_land_surface_loading_results(
    land_surfaces_df: pandas.DataFrame, parameters: List[Dict[str, str]]
) -> pandas.DataFrame:

    # fmt: off
    results = (
        land_surfaces_df
        .pipe(detailed_land_surface_volume_loading_results)
        .pipe(detailed_land_surface_pollutant_loading_results, parameters)
    )
    # fmt: on

    return results


def summary_land_surface_loading_results(
    detailed_results: pandas.DataFrame, parameters: List[Dict[str, str]]
) -> pandas.DataFrame:

    groupby_cols = ["node_id"]

    pocs = [dct["short_name"] for dct in parameters]

    # -> TODO clean this process up
    load_cols = [
        c
        for poc in pocs
        for c in detailed_results.columns
        if all((poc == c.split("_")[0], "load" in c))
    ]
    # <-

    output_columns_summable = [
        "area_acres",
        "imp_area_acres",
        "perv_area_acres",
        "imp_ro_volume_cuft",
        "perv_ro_volume_cuft",
        "runoff_volume_cuft",
        "eff_area_acres",
    ] + load_cols

    agg_list = [
        {col: "sum" for col in output_columns_summable},
        # add other aggregation requirements for other columns here
    ]

    df = (
        detailed_results.reindex(columns=groupby_cols + output_columns_summable)
        .groupby(groupby_cols)
        .agg({k: v for d in agg_list for k, v in d.items()})
    )

    #  'area_acres' is just a dummy here, any column would do
    df["land_surfaces_count"] = detailed_results.groupby(groupby_cols)[
        "area_acres"
    ].count()

    df["imp_pct"] = 100 * (df["imp_area_acres"] / df["area_acres"])
    df["ro_coeff"] = df["eff_area_acres"] / df["area_acres"]

    df.reset_index(inplace=True)

    convert_to_conc = {
        ("mg/l", "lbs"): ureg("(lbs/cubic_feet)").to("mg/l").magnitude,
        ("ug/l", "lbs"): ureg("(lbs/cubic_feet)").to("ug/l").magnitude,
        ("mpn/100ml", "mpn"): ureg("count/cubic_feet").to("count/(ml)").magnitude * 100,
    }

    for param in parameters:
        unit = param["unit"].lower()
        poc = param["short_name"]

        # -> TODO clean this process up
        load_col = [c for c in load_cols if all((poc in c, "load" in c))][0]
        load_unit = load_col.split("_")[-1]
        # <-

        conc_col = "_".join([poc, "conc", unit])
        factor = convert_to_conc[(unit, load_unit)]

        df[conc_col] = (df[load_col] / df["runoff_volume_cuft"]) * factor

    return df

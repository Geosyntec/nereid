from typing import Dict, Any, List

import pandas

# TODO: implement fallback to e.g., "TRANS-B-10" rather than "401070-TRANS-B-10"
# in case ref data is missing.


def detailed_land_surface_volume_loading_results(
    land_surfaces_df: pandas.DataFrame,
) -> pandas.DataFrame:

    land_surface_table = (
        land_surfaces_df.assign(
            imp_pct=lambda df: 100 * df["imp_area_acres"] / df["area_acres"]
        )
        .assign(perv_area_acres=lambda df: df["area_acres"] - df["imp_area_acres"])
        .assign(imp_area_sqft=lambda df: df["imp_area_acres"] * 43560)
        .assign(perv_area_sqft=lambda df: df["perv_area_acres"] * 43560)
        .assign(imp_ro_depth_feet=lambda df: df["imp_ro_depth_inches"] / 12)
        .assign(perv_ro_depth_feet=lambda df: df["perv_ro_depth_inches"] / 12)
        .assign(
            imp_ro_volume_cuft=lambda df: df["imp_ro_depth_feet"] * df["imp_area_sqft"]
        )
        .assign(
            perv_ro_volume_cuft=lambda df: df["perv_ro_depth_feet"]
            * df["perv_area_sqft"]
        )
        .assign(
            runoff_volume_cuft=lambda df: df["imp_ro_volume_cuft"]
            + df["perv_ro_volume_cuft"]
        )
        .assign(imp_eff_area_acres=lambda df: df["imp_ro_coeff"] * df["imp_area_acres"])
        .assign(
            perv_eff_area_acres=lambda df: df["perv_ro_coeff"] * df["perv_area_acres"]
        )
        .assign(
            eff_area_acres=lambda df: df["imp_eff_area_acres"]
            + df["perv_eff_area_acres"]
        )
        .fillna(0)
    )

    return land_surface_table


def detailed_land_surface_loading_results(
    land_surfaces_df: pandas.DataFrame,
) -> pandas.DataFrame:

    results = (
        land_surfaces_df.pipe(detailed_land_surface_volume_loading_results)
        # TODO: wq too
    )
    return results


def summary_land_surface_loading_results(verbose_results):

    groupby_cols = ["node_id"]

    output_columns_summable = [
        "area_acres",
        "imp_area_acres",
        "perv_area_acres",
        "imp_ro_volume_cuft",
        "perv_ro_volume_cuft",
        "runoff_volume_cuft",
        "eff_area_acres",
    ]

    agg_list = [
        {col: "sum" for col in output_columns_summable},
        # add other aggregation requirements for other columns here
    ]

    summary_results = (
        verbose_results.reindex(columns=groupby_cols + output_columns_summable)
        .groupby(groupby_cols)
        .agg({k: v for d in agg_list for k, v in d.items()})
        # area is just a dummy here, any column would do
        .assign(
            land_surfaces_count=verbose_results.groupby(groupby_cols)[
                "area_acres"
            ].count()
        )
        .assign(imp_pct=lambda df: 100 * (df["imp_area_acres"] / df["area_acres"]))
        .assign(ro_coeff=lambda df: df["eff_area_acres"] / df["area_acres"])
        .reset_index()
    )

    return summary_results

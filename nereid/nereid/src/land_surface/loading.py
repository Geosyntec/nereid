from typing import Dict, List, Optional

import pandas


def clean_land_surface_dataframe(df: pandas.DataFrame) -> pandas.DataFrame:
    """this function cleans up the imperviousness passed by the client and uses
    the new value to recompute the impervious area in acres. This is used in case
    imperviousness has been remapped in the config file.
    """

    df["imp_pct"] = df["imp_pct"].clip(0, 100)
    df["imp_area_acres"] = df["area_acres"] * (df["imp_pct"] / 100)

    return df


def detailed_volume_loading_results(df: pandas.DataFrame) -> pandas.DataFrame:
    """
    df must contain:
        area_acres: float
        imp_area_acres: float
        imp_ro_depth_inches: float
        perv_ro_depth_inches: float
        imp_ro_coeff: float
        perv_ro_coeff: float
        is_developed: bool

    """

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
    df["ro_coeff"] = df["eff_area_acres"] / df["area_acres"]
    df["developed_area_acres"] = df["area_acres"].mask(
        ~df["is_developed"].fillna(False), other=0
    )

    return df


def detailed_dry_weather_volume_loading_results(
    df: pandas.DataFrame, seasons: Dict[str, Optional[List[str]]]
) -> pandas.DataFrame:
    """This function aggregates the dry weather flowrate (dwf) by season according
    to the config file spec.
    """

    developed_area_acres = df.get("developed_area_acres", 0.0)

    for season, months in seasons.items():
        if months is not None:
            dwf_cfs_ac = df.get(f"{season}_dry_weather_flow_cuft_psecond_pacre", 0.0)

            dwf_cfs = dwf_cfs_ac * developed_area_acres
            df[f"{season}_dry_weather_flow_cuft_psecond"] = dwf_cfs

            dwf_cuft_pday_pacre = dwf_cfs_ac * 3600 * 24

            dwf_pseason_pacre = sum(
                [df.get(f"n_dry_days_{m}", 0.0) * dwf_cuft_pday_pacre for m in months]
            )
            df[f"{season}_dry_weather_flow_cuft"] = (
                dwf_pseason_pacre * developed_area_acres
            )

    return df


def detailed_pollutant_loading_results(
    df: pandas.DataFrame,
    wet_weather_parameters: List[Dict[str, str]],
    dry_weather_parameters: List[Dict[str, str]],
    season_names: List[str],
) -> pandas.DataFrame:
    """convert the washoff concentration to load for both wet and dry seasons.

    Each parameter element in the lists is a dictionary like:

        long_name: Total Suspended Solids
        short_name: TSS
        concentration_unit: mg/L
        load_unit: lbs
        conc_to_load_factor: <some float>

    It also contains derived values from 'src.wq_parameters.init_wq_paramters'
    """

    for param in wet_weather_parameters:
        conc_col = param["conc_col"]
        load_col = param["load_col"]
        factor = param["conc_to_load_factor"]

        if conc_col in df:
            df[load_col] = df["runoff_volume_cuft"] * df[conc_col] * factor

    for param in dry_weather_parameters:
        conc_col = param["conc_col"]
        load_col = param["load_col"]
        factor = param["conc_to_load_factor"]

        if conc_col in df:
            for season in season_names:
                dw_vol_month_col = f"{season}_dry_weather_flow_cuft"
                df[season + "_" + load_col] = (
                    df.get(dw_vol_month_col, 0.0) * df[conc_col] * factor
                )

    return df


def detailed_loading_results(
    land_surfaces_df: pandas.DataFrame,
    wet_weather_parameters: List[Dict[str, str]],
    dry_weather_parameters: List[Dict[str, str]],
    seasons: Dict[str, List[str]],
) -> pandas.DataFrame:

    results = (
        land_surfaces_df.pipe(clean_land_surface_dataframe)
        .pipe(detailed_volume_loading_results)
        .pipe(detailed_dry_weather_volume_loading_results, seasons)
        .pipe(
            detailed_pollutant_loading_results,
            wet_weather_parameters,
            dry_weather_parameters,
            season_names=seasons.keys(),
        )
    )

    return results


def summary_loading_results(
    detailed_results: pandas.DataFrame,
    wet_weather_parameters: List[Dict[str, str]],
    dry_weather_parameters: List[Dict[str, str]],
    season_names: List[str],
) -> pandas.DataFrame:

    groupby_cols = ["node_id"]
    wet_load_cols = [dct["load_col"] for dct in wet_weather_parameters]
    dry_load_cols = [
        s + "_" + dct["load_col"]
        for dct in dry_weather_parameters
        for s in season_names
    ]

    dwf_cols = [
        c
        for c in detailed_results.columns
        if "dry_weather_flow_cuft" in c and not "_pacre" in c
    ]

    output_columns_summable = (
        [
            "area_acres",
            "imp_area_acres",
            "perv_area_acres",
            "imp_ro_volume_cuft",
            "perv_ro_volume_cuft",
            "runoff_volume_cuft",
            "eff_area_acres",
            "developed_area_acres",
        ]
        + wet_load_cols
        + dry_load_cols
        + dwf_cols
    )

    agg_dict = {
        **{col: "sum" for col in output_columns_summable},
        # add other aggregation requirements for other columns here
    }

    df = (
        detailed_results.reindex(columns=groupby_cols + output_columns_summable)
        .groupby(groupby_cols)
        .agg(agg_dict)
    )

    #  'area_acres' is just a dummy here, any column would do
    df["land_surfaces_count"] = detailed_results.groupby(groupby_cols)[
        "area_acres"
    ].count()

    df["imp_pct"] = 100 * (df["imp_area_acres"] / df["area_acres"])
    df["ro_coeff"] = df["eff_area_acres"] / df["area_acres"]

    df.reset_index(inplace=True)

    for param in wet_weather_parameters:
        conc_col = param["conc_col"]
        load_col = param["load_col"]
        factor = param["load_to_conc_factor"]

        df[conc_col] = (df[load_col] / df["runoff_volume_cuft"]) * factor

    for season in season_names:
        dw_vol_col = f"{season}_dry_weather_flow_cuft"
        dw_cfs_col = f"{season}_dry_weather_flow_cuft_psecond"

        for param in dry_weather_parameters:
            conc_col = season + "_" + param["conc_col"]
            load_col = season + "_" + param["load_col"]
            factor = param["load_to_conc_factor"]

            df[conc_col] = (df[load_col] / df[dw_vol_col]).fillna(0) * factor

    return df

"""Compare ERA5 with TSMS forecasts and reduce ERA5 temperatures to the real terrain height.

Usage:  python src/analysis.py
Inputs: data/raw/era5_daily_openmeteo.csv, data/raw/tsms_forecasts.csv
Output: data/processed/izmir_era5_vs_tsms.csv
        data/processed/bozdag_lapse_corrected.csv
        data/processed/summary.json
"""
import json

import pandas as pd

from config import (EVENT_DAY, LAPSE_RATE_K_PER_M, PROCESSED, RAW, SKI_CENTRE_ELEV_M,
                    SNOW_CM_TO_MM_WE)


def reduce_to(t, z_from, z_to, gamma=LAPSE_RATE_K_PER_M):
    """T(z_to) = T(z_from) - Γ (z_to - z_from)."""
    return t - gamma * (z_to - z_from)


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    era = pd.read_csv(RAW / "era5_daily_openmeteo.csv", parse_dates=["date"])
    fc = pd.read_csv(RAW / "tsms_forecasts.csv", parse_dates=["date"])

    # --- İzmir: first city forecast per day (02.05: TRT 8/19; 03.05: Konak 9/15) ---
    city = fc[fc["location"].str.contains(r"İzmir \((?:merkez|Konak)\)", regex=True)]
    city = city.groupby("date", as_index=False).first()[["date", "tmin_c", "tmax_c", "source"]]
    iz = era[era.point == "Izmir_city"][["date", "era5_cell_elev_m", "tmin_c", "tmax_c", "precip_mm"]]
    cmp_ = iz.merge(city, on="date", how="left", suffixes=("_era5", "_tsms"))
    cmp_["bias_tmin"] = (cmp_.tmin_c_era5 - cmp_.tmin_c_tsms).round(1)
    cmp_["bias_tmax"] = (cmp_.tmax_c_era5 - cmp_.tmax_c_tsms).round(1)
    cmp_.to_csv(PROCESSED / "izmir_era5_vs_tsms.csv", index=False)

    # --- Bozdağ: lapse-rate reduction to the villages and to the ski centre ---
    bz = era[era.point == "Bozdag_Golcuk"].copy()
    for lab, z in (("1100m", 1100), ("ski_centre", SKI_CENTRE_ELEV_M)):
        bz[f"tmin_{lab}"] = reduce_to(bz.tmin_c, bz.era5_cell_elev_m, z).round(1)
        bz[f"tmax_{lab}"] = reduce_to(bz.tmax_c, bz.era5_cell_elev_m, z).round(1)
    bz["snowfall_mm_we"] = (bz.snowfall_cm * SNOW_CM_TO_MM_WE).round(1)
    bz.to_csv(PROCESSED / "bozdag_lapse_corrected.csv", index=False)

    ev = bz[bz.date == EVENT_DAY].iloc[0]
    summary = {
        "izmir_mean_bias_tmin": round(cmp_.bias_tmin.mean(), 1), "izmir_mae_tmin": round(cmp_.bias_tmin.abs().mean(), 1),
        "izmir_mean_bias_tmax": round(cmp_.bias_tmax.mean(), 1), "izmir_mae_tmax": round(cmp_.bias_tmax.abs().mean(), 1),
        "izmir_grid_height_effect_c": round(LAPSE_RATE_K_PER_M * (300 - 29), 1),
        "bozdag_cell_elev_m": int(ev.era5_cell_elev_m),
        "event_day_1100m_tmin_tmax": [ev.tmin_1100m, ev.tmax_1100m],
        "event_day_ski_centre_tmin_tmax": [ev.tmin_ski_centre, ev.tmax_ski_centre],
        "tsms_ski_centre_forecast": [0, 2],
        "event_day_precip_mm": ev.precip_mm, "event_day_snowfall_mm_we": ev.snowfall_mm_we,
    }
    (PROCESSED / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
    print(cmp_.to_string(index=False))
    print(json.dumps(summary, indent=2, default=float))


if __name__ == "__main__":
    main()

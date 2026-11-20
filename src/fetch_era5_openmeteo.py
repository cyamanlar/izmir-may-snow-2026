"""Download daily ERA5 values for the two analysis points from the Open-Meteo archive API.

Why Open-Meteo? It serves ERA5 (0.25°) without a Copernicus account. `elevation=nan`
switches OFF Open-Meteo's statistical downscaling, so values refer to the mean height of
the ERA5 grid cell (that height is returned as `elevation`). `timezone=Europe/Istanbul`
gives local (UTC+3) days, matching TSMS daily extremes.

Usage:  python src/fetch_era5_openmeteo.py
Output: data/raw/era5_daily_openmeteo.csv
"""
import csv
import requests

from config import POINTS, RAW, START, END

URL = "https://archive-api.open-meteo.com/v1/archive"
DAILY = ["temperature_2m_min", "temperature_2m_max", "temperature_2m_mean",
         "precipitation_sum", "snowfall_sum", "wind_speed_10m_max"]


def main():
    names = list(POINTS)
    params = {
        "latitude": ",".join(str(POINTS[n][0]) for n in names),
        "longitude": ",".join(str(POINTS[n][1]) for n in names),
        "elevation": ",".join("nan" for _ in names),
        "start_date": START, "end_date": END,
        "daily": ",".join(DAILY), "models": "era5", "timezone": "Europe/Istanbul",
    }
    r = requests.get(URL, params=params, timeout=60)
    r.raise_for_status()
    js = r.json()
    js = js if isinstance(js, list) else [js]
    out = RAW / "era5_daily_openmeteo.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "point", "site_lat", "site_lon", "site_elev_m", "era5_cell_lat", "era5_cell_lon",
                    "era5_cell_elev_m", "tmin_c", "tmax_c", "tmean_c", "precip_mm", "snowfall_cm", "wind_max_kmh"])
        for name, res in zip(names, js):
            lat, lon, z = POINTS[name]
            d = res["daily"]
            for i, day in enumerate(d["time"]):
                w.writerow([day, name, lat, lon, z, res["latitude"], res["longitude"], res["elevation"],
                            *(d[k][i] for k in DAILY)])
    print("written", out)


if __name__ == "__main__":
    main()

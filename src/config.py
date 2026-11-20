"""Shared settings for the İzmir / Bozdağ May-2026 snow case study."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
MAPS = ROOT / "maps"            # downloaded third-party charts (git-ignored)

START, END = "2026-04-30", "2026-05-04"
EVENT_DAY = "2026-05-03"

# name: (lat, lon, real elevation in m)
POINTS = {
    "Izmir_city": (38.42, 27.14, 29),        # İzmir city / station 17220 ≈ 29 m
    "Bozdag_Golcuk": (38.35, 28.03, 1100),   # villages where snow fell (≈1,100 m, approximate coords)
}
SKI_CENTRE_ELEV_M = 1540   # Bozdağ Ski Centre base (TSMS 0–2 °C forecast refers to it)
SUMMIT_ELEV_M = 2159

LAPSE_RATE_K_PER_M = 6.5e-3   # standard-atmosphere lapse rate
SNOW_CM_TO_MM_WE = 10 / 7     # Open-Meteo snowfall (cm of snow) -> mm water equivalent

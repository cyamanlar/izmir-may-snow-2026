"""Make the repository's own figures from the processed data.

Usage:  python src/plot_figures.py   (run src/analysis.py first)
Output: figures/era5_vs_tsms_timeseries.png
        figures/snow_level_profile.png
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import FIGURES, LAPSE_RATE_K_PER_M, PROCESSED, SKI_CENTRE_ELEV_M, SUMMIT_ELEV_M

RED, BLUE, GREY = "#c0392b", "#2c6fbb", "0.75"


def timeseries():
    iz = pd.read_csv(PROCESSED / "izmir_era5_vs_tsms.csv", parse_dates=["date"])
    bz = pd.read_csv(PROCESSED / "bozdag_lapse_corrected.csv", parse_dates=["date"])
    x = np.arange(len(iz)); lab = iz.date.dt.strftime("%d %b")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    a = ax[0]
    a.plot(x, iz.tmax_c_era5, "-o", color=RED, label="ERA5 T max")
    a.plot(x, iz.tmin_c_era5, "-o", color=BLUE, label="ERA5 T min")
    a.plot(x, iz.tmax_c_tsms, "s", mfc="none", ms=9, color=RED, label="TSMS forecast T max")
    a.plot(x, iz.tmin_c_tsms, "s", mfc="none", ms=9, color=BLUE, label="TSMS forecast T min")
    a2 = a.twinx(); a2.bar(x, iz.precip_mm, color=GREY, width=0.5, zorder=0); a2.set_ylim(0, 40); a2.set_ylabel("Precipitation (mm)")
    a.set_zorder(a2.get_zorder() + 1); a.patch.set_visible(False)
    a.set_title(f"a) İzmir (ERA5 cell, {int(iz.era5_cell_elev_m[0])} m)", fontsize=10)
    b = ax[1]
    b.plot(x, bz.tmax_c, "-o", color=RED, alpha=.4, label=f"ERA5 T max ({int(bz.era5_cell_elev_m.iloc[0])} m)")
    b.plot(x, bz.tmin_c, "-o", color=BLUE, alpha=.4, label=f"ERA5 T min ({int(bz.era5_cell_elev_m.iloc[0])} m)")
    b.plot(x, bz.tmax_1100m, "-o", color=RED, label="T max at 1,100 m")
    b.plot(x, bz.tmin_1100m, "-o", color=BLUE, label="T min at 1,100 m")
    b.axhline(0, color="k", lw=.8, ls="--")
    b2 = b.twinx(); b2.bar(x, bz.precip_mm, color=GREY, width=0.5, zorder=0); b2.set_ylim(0, 40); b2.set_ylabel("Precipitation (mm)")
    b.set_zorder(b2.get_zorder() + 1); b.patch.set_visible(False)
    b.set_title("b) Bozdağ / Gölcük (reduced with 6.5 K/km)", fontsize=10)
    for q in ax:
        q.set_xticks(x); q.set_xticklabels(lab); q.set_ylabel("2 m temperature (°C)"); q.set_ylim(-2, 28)
        q.grid(alpha=.3); q.legend(fontsize=7, loc="upper right")
    fig.suptitle("ERA5 vs TSMS forecasts, 30 Apr – 4 May 2026 (local days)", fontsize=11)
    fig.tight_layout(); fig.savefig(FIGURES / "era5_vs_tsms_timeseries.png", dpi=180); plt.close(fig)


def profile():
    """Schematic: why snow reached 1,100 m although the ERA5 cell stayed above freezing."""
    s = json.loads((PROCESSED / "summary.json").read_text())
    bz = pd.read_csv(PROCESSED / "bozdag_lapse_corrected.csv")
    ev = bz[bz.date == "2026-05-03"].iloc[0]
    z = np.linspace(0, 2300, 50)
    t_dry = ev.tmax_c - LAPSE_RATE_K_PER_M * (z - ev.era5_cell_elev_m)          # standard lapse rate from ERA5 Tmax
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.plot(t_dry, z, color=RED, lw=2, label="ERA5 T max (3 May) extended with 6.5 K/km")
    ax.axvline(0, color="k", lw=1)
    ax.axhspan(1400, 2000, color="#5DADE2", alpha=.18, label="Freezing level from 850 hPa ≈ 0 °C (≈1,400–2,000 m)")
    ax.axhspan(1100, 1400, color="#AED6F1", alpha=.25, hatch="//", label="Snow level lowered by melting/evaporative cooling")
    marks = [(29, "İzmir city ≈30 m – rain"), (300, "ERA5 İzmir cell 300 m"), (ev.era5_cell_elev_m, f"ERA5 Bozdağ cell {int(ev.era5_cell_elev_m)} m – no snow in ERA5"),
             (1100, "Gölcük / Bozdağ villages ≈1,100 m – SNOW observed"), (SKI_CENTRE_ELEV_M, "Ski centre ≈1,540 m – TSMS 0–2 °C"),
             (SUMMIT_ELEV_M, "Bozdağ summit 2,159 m")]
    for h, txt in marks:
        ax.axhline(h, color="0.4", lw=.6, ls=":")
        ax.text(16.5, h + 25, txt, fontsize=8, ha="right")
    ax.plot([s["event_day_ski_centre_tmin_tmax"][1]], [SKI_CENTRE_ELEV_M], "o", color=RED)
    ax.set_xlim(-6, 17); ax.set_ylim(0, 2300)
    ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Height (m)")
    ax.set_title("3 May 2026 – heights that matter for the snow line", fontsize=11)
    ax.legend(fontsize=7.5, loc="upper right", bbox_to_anchor=(1, 0.86)); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(FIGURES / "snow_level_profile.png", dpi=180); plt.close(fig)


if __name__ == "__main__":
    FIGURES.mkdir(exist_ok=True)
    timeseries(); profile(); print("figures written")

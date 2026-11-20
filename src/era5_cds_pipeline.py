#!/usr/bin/env python3
"""İzmir / Bozdağ kar olayı (3 Mayıs 2026) — ERA5 indirme, Excel doldurma, harita üretme
ve şekilleri/tabloları Word raporuna yerleştirme (tek komut).

Bu betik eski fetch_era5_to_excel.py'nin yerini alır. Eski betikteki hatalar:
  1) month=["04","05"] + day=[...] CDS'de kartezyen çarpım olarak yorumlanır → 1-4 Nisan ve
     30 Mayıs da iniyordu (gereksiz). Burada yalnızca 29 Nisan–4 Mayıs seçilir.
  2) Yeni CDS, anlık (t2m, rüzgâr) ve birikimli (tp, sf) değişkenleri birlikte isteyince
     NetCDF'leri ZIP içinde iki ayrı dosya olarak verir → xr.open_dataset("era5_sl.nc") çöküyordu.
     Burada ZIP otomatik açılıp birleştirilir.
  3) Günlük istatistik UTC gününe göre alınıyordu; MGM min/maks değerleri yerel güne (UTC+3) aittir.
     Burada gün = 21:00 UTC (önceki gün) – 21:00 UTC.
  4) Birikimli tp/sf için "geçerlilik saati" kaydırması dikkate alınmıyordu (00 UTC değeri önceki
     günün 23–24 UTC birikimidir). Düzeltildi.
  5) Günlük min/maks yalnızca saatlik t2m'den alınıyordu (uçları kaçırır). mn2t/mx2t kullanılır.
  6) En yakın ızgara noktası denize düşebiliyordu (İzmir kıyı). Kara-deniz maskesiyle en yakın
     KARA noktası seçilir; ERA5 ızgara yüksekliği (orografi) hesaplanıp yazılır.

Gereksinimler (bir kez):
  pip install cdsapi xarray netCDF4 h5netcdf openpyxl python-docx numpy scipy matplotlib cartopy metpy requests pillow
  ~/.cdsapirc dosyası (https://cds.climate.copernicus.eu hesabı + iki ERA5 veri setinin lisansını kabul edin).

Kullanım (rapor, Excel ve betik aynı klasörde):
  python era5_izmir_pipeline.py --xlsx Izmir_Kar_3Mayis2026_ERA5_MGM.xlsx --docx Proje_Raporu_Izmir_Kar_3Mayis2026.docx
Seçenekler: --skip-satellite (NASA Worldview indirmesini atla), --only-docx (veri iner ama yalnız rapor güncellenir)

Veri: Hersbach et al. (2023) DOI 10.24381/cds.adbb2d47 (tek seviye) ve 10.24381/cds.bd0915c6 (basınç seviyeleri).
"""
import argparse
import glob
import os
import shutil
import sys
import zipfile

import numpy as np

# ----------------------------------------------------------------------------- ayarlar
G = 9.80665
LAPSE = 6.5e-3                     # K/m, standart atmosfer sıcaklık azalma oranı
UTC_OFFSET_H = 3                   # Türkiye saati
DAYS = ["2026-04-30", "2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04"]
MAP_DAYS = ["2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04"]
MAP_HOUR = "12:00"                 # kar 3 Mayıs öğle saatlerinde başladı → 12 UTC haritaları
PROFILE_TIME = "2026-05-03T12:00"  # Skew-T (ERA5 dikey profili) zamanı
# Nokta adı (Excel'deki ile aynı) : (enlem, boylam, gerçek rakım m)
POINTS = {
    "İzmir (merkez)": (38.42, 27.14, 29),      # İzmir 17220 istasyonu ~29 m
    "Bozdağ (Ödemiş)": (38.35, 28.03, 1100),   # kar gözlenen Gölcük/Bozdağ mah. ~1100 m (YAKLAŞIK; Google Earth ile doğrulayın)
}
BOX = [39.0, 26.5, 38.0, 28.5]     # K, B, G, D — istatistik kutusu
MAP_BOX = [55.0, 0.0, 25.0, 50.0]  # sinoptik harita kutusu
FIG_DIR = "sekiller"
LEVELS_PROFILE = ["300", "400", "500", "600", "700", "750", "800", "850", "900", "925", "950", "975", "1000"]


# ----------------------------------------------------------------------------- CDS
def _req(**kw):
    base = dict(product_type=["reanalysis"], data_format="netcdf", download_format="unarchived")
    base.update(kw)
    return base


def cds_get(dataset, request, target):
    if os.path.exists(target) and os.path.getsize(target) > 0:
        print(f"  (var, tekrar indirilmiyor) {target}")
        return target
    import cdsapi
    print(f"  indiriliyor → {target}")
    cdsapi.Client().retrieve(dataset, request, target)
    return target


def open_cds(path):
    """Yeni CDS çıktısını (tek .nc veya içinde birden çok .nc olan ZIP) aç ve adları sadeleştir."""
    import xarray as xr
    if zipfile.is_zipfile(path):
        out = path + "_dir"
        os.makedirs(out, exist_ok=True)
        with zipfile.ZipFile(path) as z:
            z.extractall(out)
        parts = [xr.open_dataset(f) for f in sorted(glob.glob(os.path.join(out, "**", "*.nc"), recursive=True))]
        ds = xr.merge(parts, compat="override", join="outer")
    else:
        ds = xr.open_dataset(path)
    ren = {k: v for k, v in {"valid_time": "time", "pressure_level": "level"}.items() if k in ds.variables}
    ds = ds.rename(ren)
    if "expver" in ds.dims:              # eski CDS: ERA5/ERA5T birleşimi
        ds = ds.max("expver")
    for c in ("number", "expver"):
        if c in ds.coords and c not in ds.dims:
            ds = ds.drop_vars(c)
    return ds.sortby("latitude")


def download_all():
    stat_days = dict(year=["2026"], time=[f"{h:02d}:00" for h in range(24)])
    sl_vars = ["2m_temperature", "maximum_2m_temperature_since_previous_post_processing",
               "minimum_2m_temperature_since_previous_post_processing", "total_precipitation", "snowfall",
               "10m_u_component_of_wind", "10m_v_component_of_wind", "mean_sea_level_pressure",
               "geopotential", "land_sea_mask"]
    pl_vars = ["temperature", "geopotential", "relative_humidity", "u_component_of_wind", "v_component_of_wind"]
    files = {}
    # Nisan (29–30) ve Mayıs (01–04) AYRI istenir → kartezyen çarpım sorunu yok
    for tag, month, days in (("apr", "04", ["29", "30"]), ("may", "05", ["01", "02", "03", "04"])):
        files[f"sl_{tag}"] = cds_get("reanalysis-era5-single-levels",
                                     _req(variable=sl_vars, month=[month], day=days, area=BOX, **stat_days),
                                     f"era5_sl_{tag}.nc")
        files[f"pl_{tag}"] = cds_get("reanalysis-era5-pressure-levels",
                                     _req(variable=pl_vars, pressure_level=LEVELS_PROFILE, month=[month],
                                          day=days, area=BOX, **stat_days),
                                     f"era5_pl_{tag}.nc")
    map_t = dict(year=["2026"], month=["05"], day=[d[-2:] for d in MAP_DAYS], time=[MAP_HOUR])
    files["map_sl"] = cds_get("reanalysis-era5-single-levels",
                              _req(variable=["mean_sea_level_pressure", "10m_u_component_of_wind",
                                             "10m_v_component_of_wind", "geopotential", "land_sea_mask"],
                                   area=MAP_BOX, **map_t), "era5_map_sl.nc")
    files["map_pl"] = cds_get("reanalysis-era5-pressure-levels",
                              _req(variable=["geopotential", "temperature", "u_component_of_wind",
                                             "v_component_of_wind"],
                                   pressure_level=["300", "500", "700", "850", "1000"], area=MAP_BOX, **map_t),
                              "era5_map_pl.nc")
    return files


def load(files):
    import xarray as xr
    sl = xr.concat([open_cds(files["sl_apr"]), open_cds(files["sl_may"])], dim="time").sortby("time")
    pl = xr.concat([open_cds(files["pl_apr"]), open_cds(files["pl_may"])], dim="time").sortby("time")
    return sl, pl, open_cds(files["map_sl"]), open_cds(files["map_pl"])


# ----------------------------------------------------------------------------- istatistik
def local_day(day, accum=False):
    """Yerel gün (UTC+3) için UTC zaman dilimi. Birikimli alanlarda geçerlilik saati 1 saat kaydırılır."""
    start = np.datetime64(day + "T00:00") - np.timedelta64(UTC_OFFSET_H, "h")
    end = start + np.timedelta64(24, "h")
    if accum:
        return slice(start + np.timedelta64(1, "h"), end)
    return slice(start, end - np.timedelta64(1, "h"))


def pick_land_cell(sl, lat, lon):
    """Noktaya en yakın KARA ızgara hücresi (lsm ≥ 0.5)."""
    lsm = sl["lsm"].isel(time=0) if "lsm" in sl else None
    best = None
    for la in sl.latitude.values:
        for lo in sl.longitude.values:
            if abs(la - lat) > 0.5 or abs(lo - lon) > 0.5:
                continue
            if lsm is not None and float(lsm.sel(latitude=la, longitude=lo)) < 0.5:
                continue
            d = (la - lat) ** 2 + ((lo - lon) * np.cos(np.radians(lat))) ** 2
            if best is None or d < best[0]:
                best = (d, float(la), float(lo))
    if best is None:
        c = sl.sel(latitude=lat, longitude=lon, method="nearest")
        return float(c.latitude), float(c.longitude)
    return best[1], best[2]


def level_crossing_height(z, t, thresh=0.0):
    """Alttan yukarı ilk kez t ≤ thresh olduğu yüksekliği (m) doğrusal interpolasyonla bul."""
    for i in range(len(t) - 1):
        if t[i] > thresh >= t[i + 1]:
            f = (t[i] - thresh) / (t[i] - t[i + 1])
            return z[i] + f * (z[i + 1] - z[i])
    return float("nan")


def compute_stats(sl, pl):
    stats, cells, profiles = {}, {}, {}
    for name, (lat, lon, z_site) in POINTS.items():
        la, lo = pick_land_cell(sl, lat, lon)
        s = sl.sel(latitude=la, longitude=lo)
        p = pl.sel(latitude=la, longitude=lo)
        z_grid = float(s["z"].isel(time=0)) / G
        cells[name] = dict(lat=la, lon=lo, z_grid=z_grid, z_site=z_site)
        for day in DAYS:
            wi, wa = s.sel(time=local_day(day)), s.sel(time=local_day(day, True))
            tmin = float(wa["mn2t"].min() if "mn2t" in wa else wi["t2m"].min()) - 273.15
            tmax = float(wa["mx2t"].max() if "mx2t" in wa else wi["t2m"].max()) - 273.15
            pi = p.sel(time=local_day(day))
            corr = LAPSE * (z_site - z_grid)        # gerçek rakıma indirgeme (K)
            stats[(day, name)] = dict(
                tmin=tmin, tmax=tmax, tmean=float(wi["t2m"].mean()) - 273.15,
                tp=float(wa["tp"].sum()) * 1000, sf=float(wa["sf"].sum()) * 1000,
                wmax=float(np.hypot(wi["u10"], wi["v10"]).max()) * 3.6,
                msl=float(wi["msl"].mean()) / 100,
                t850=float(pi["t"].sel(level=850).mean()) - 273.15,
                z500=float(pi["z"].sel(level=500).mean()) / G,
                z_grid=z_grid, tmin_corr=tmin - corr, tmax_corr=tmax - corr)
        # dikey profil (Skew-T ve donma seviyesi)
        pr = p.sel(time=PROFILE_TIME).sortby("level", ascending=False)   # 1000 → 300 hPa
        t_c = pr["t"].values - 273.15
        z_m = pr["z"].values / G
        rh = np.clip(pr["r"].values, 1, 100)
        try:
            import metpy.calc as mpcalc
            from metpy.units import units
            td = mpcalc.dewpoint_from_relative_humidity(t_c * units.degC, rh / 100 * units.dimensionless).m
            tw = mpcalc.wet_bulb_temperature(pr["level"].values * units.hPa, t_c * units.degC, td * units.degC).m
        except Exception as e:  # metpy yoksa yaklaşık formül (Stull 2011)
            print("  metpy yok/hata, yaklaşık ıslak termometre kullanılıyor:", e)
            a, b = 17.625, 243.04
            gam = np.log(rh / 100) + a * t_c / (b + t_c)
            td = b * gam / (a - gam)
            tw = (t_c * np.arctan(0.151977 * np.sqrt(rh + 8.313659)) + np.arctan(t_c + rh)
                  - np.arctan(rh - 1.676331) + 0.00391838 * rh ** 1.5 * np.arctan(0.023101 * rh) - 4.686035)
        profiles[name] = dict(p=pr["level"].values, t=t_c, td=td, tw=tw, z=z_m,
                              u=pr["u"].values, v=pr["v"].values,
                              fzl=level_crossing_height(z_m, t_c), wbz=level_crossing_height(z_m, tw),
                              t850=float(pr["t"].sel(level=850)) - 273.15)
    return stats, cells, profiles


# ----------------------------------------------------------------------------- haritalar
def _cartopy():
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    return ccrs, cfeature


SPECIAL_ISOTHERMS = {0.0: "blue", -20.0: "blue", -25.0: "green", -30.0: "gold", -35.0: "saddlebrown", -40.0: "black"}


def _map_ax(fig, n, title):
    ccrs, cfeature = _cartopy()
    ax = fig.add_subplot(2, 2, n, projection=ccrs.LambertConformal(central_longitude=27, central_latitude=40,
                                                                    standard_parallels=(30, 50)))
    ax.set_extent([5, 47, 29, 52], ccrs.PlateCarree())
    ax.coastlines("50m", linewidth=0.6, color="0.3")
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="0.5")
    ax.gridlines(draw_labels=False, linewidth=0.3, color="0.7", linestyle=":")
    for nm, (lat, lon, _) in POINTS.items():
        ax.plot(lon, lat, marker="*", color="magenta", markersize=7, transform=ccrs.PlateCarree(), zorder=10)
    ax.set_title(title, fontsize=9)
    return ax


def _isotherms(ax, lon, lat, T):
    ccrs, _ = _cartopy()
    pc = ccrs.PlateCarree()
    lv = np.arange(-50, 35.01, 2.5)
    lv = lv[(lv >= np.nanmin(T)) & (lv <= np.nanmax(T))]
    other = [x for x in lv if float(x) not in SPECIAL_ISOTHERMS]
    if other:
        cs = ax.contour(lon, lat, T, levels=other, colors="red", linestyles="--", linewidths=0.6, transform=pc)
        ax.clabel(cs, fmt="%g", fontsize=5)
    for val, col in SPECIAL_ISOTHERMS.items():
        if len(lv) and lv.min() <= val <= lv.max():
            cs = ax.contour(lon, lat, T, levels=[val], colors=col, linewidths=1.6, transform=pc)
            ax.clabel(cs, fmt="%g", fontsize=6)


def _heights(ax, lon, lat, zgpdm, base, step):
    ccrs, _ = _cartopy()
    lo = base - step * np.ceil((base - np.nanmin(zgpdm)) / step)
    hi = base + step * np.ceil((np.nanmax(zgpdm) - base) / step)
    cs = ax.contour(lon, lat, zgpdm, levels=np.arange(lo, hi + 0.1, step), colors="black", linewidths=0.9,
                    transform=ccrs.PlateCarree())
    ax.clabel(cs, fmt="%d", fontsize=6)


def _mark_hl(ax, lon, lat, field, size=41):
    from scipy.ndimage import maximum_filter, minimum_filter
    ccrs, _ = _cartopy()
    for filt, lab, col in ((maximum_filter, "H", "blue"), (minimum_filter, "L", "red")):
        ys, xs = np.where(filt(field, size=size, mode="nearest") == field)
        for y, x in zip(ys, xs):
            if 3 < y < field.shape[0] - 4 and 3 < x < field.shape[1] - 4:
                ax.text(lon[x], lat[y], lab, color=col, fontsize=13, weight="bold", ha="center", va="center",
                        transform=ccrs.PlateCarree(), clip_on=True)


def _barbs(ax, lon, lat, u, v, every=10):
    ccrs, _ = _cartopy()
    k = 1.94384
    ax.barbs(lon[::every], lat[::every], u[::every, ::every] * k, v[::every, ::every] * k, length=4.5,
             linewidth=0.4, color="0.25", transform=ccrs.PlateCarree())


def _advection(T, u, v, lat, lon):
    R = 6.371e6
    dy = R * np.deg2rad(np.gradient(lat))[:, None]
    dx = R * np.cos(np.deg2rad(lat))[:, None] * np.deg2rad(np.gradient(lon))[None, :]
    dTdy = np.gradient(T, axis=0) / dy
    dTdx = np.gradient(T, axis=1) / dx
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(-(u * dTdx + v * dTdy) * 86400.0, 2)   # K/gün


def make_maps(msl_ds, mpl_ds):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ccrs, _ = _cartopy()
    pc = ccrs.PlateCarree()
    os.makedirs(FIG_DIR, exist_ok=True)
    lat, lon = mpl_ds.latitude.values, mpl_ds.longitude.values
    out = {}
    specs = {
        "surface": ("Yer (MSLP, 4 hPa aralık, taban 1000)", None),
        850: ("850 hPa: Z (3 gpdm, taban 150) + izoterm 2.5 °C + T adveksiyonu", (150, 3)),
        700: ("700 hPa: Z (6 gpdm, taban 300) + izoterm", (300, 6)),
        500: ("500 hPa: Z (6 gpdm, taban 552) + izoterm", (552, 6)),
        300: ("300 hPa: Z (6 gpdm, taban 900) + jet (≥50 kt)", (900, 6)),
    }
    for key, (title, hs) in specs.items():
        fig = plt.figure(figsize=(12, 9.2))
        for i, day in enumerate(MAP_DAYS, 1):
            when = f"{day}T{MAP_HOUR}"
            ax = _map_ax(fig, i, f"{'abcd'[i-1]}) {day[8:]}.{day[5:7]}.2026 {MAP_HOUR[:2]} UTC")
            if key == "surface":
                s = msl_ds.sel(time=when)
                p = s["msl"].values / 100
                lv = np.arange(1000 - 4 * 12, 1000 + 4 * 13, 4)
                cs = ax.contour(lon, lat, p, levels=lv, colors="black", linewidths=0.9, transform=pc)
                ax.clabel(cs, fmt="%d", fontsize=6)
                _mark_hl(ax, lon, lat, p)
                _barbs(ax, lon, lat, s["u10"].values, s["v10"].values)
                # 1000–500 hPa kalınlığı (dam) kesikli mavi
                q = mpl_ds.sel(time=when)
                th = (q["z"].sel(level=500) - q["z"].sel(level=1000)).values / G / 10
                cs2 = ax.contour(lon, lat, th, levels=np.arange(510, 600, 6), colors="royalblue", linestyles="--",
                                 linewidths=0.6, transform=pc)
                ax.clabel(cs2, fmt="%d", fontsize=5)
            else:
                q = mpl_ds.sel(time=when, level=key)
                z = q["z"].values / G / 10
                T = q["t"].values - 273.15
                u, v = q["u"].values, q["v"].values
                if key == 850:
                    adv = _advection(T, u, v, lat, lon)
                    cf = ax.contourf(lon, lat, adv, levels=[-20, -15, -10, -5, -2, 2, 5, 10, 15, 20],
                                     cmap="RdBu_r", extend="both", alpha=0.55, transform=pc)
                if key == 300:
                    spd = np.hypot(u, v) * 1.94384
                    cf = ax.contourf(lon, lat, spd, levels=[50, 70, 90, 110, 130, 150, 170], cmap="YlOrRd",
                                     extend="max", alpha=0.7, transform=pc)
                _heights(ax, lon, lat, z, *hs)
                if key != 300:
                    _isotherms(ax, lon, lat, T)
                _barbs(ax, lon, lat, u, v)
                if key in (850, 500, 700):
                    _mark_hl(ax, lon, lat, z)
        if key in (850, 300):
            cax = fig.add_axes([0.25, 0.04, 0.5, 0.015])
            fig.colorbar(cf, cax=cax, orientation="horizontal",
                         label="Sıcaklık adveksiyonu (K/gün; mavi = soğuk adveksiyon)" if key == 850 else "Rüzgâr hızı (kt)")
        fig.suptitle(f"ERA5 — {title}   (★ İzmir ve Bozdağ)", fontsize=11)
        fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.08, wspace=0.03, hspace=0.12)
        fn = os.path.join(FIG_DIR, f"harita_{key}.png")
        fig.savefig(fn, dpi=170)
        plt.close(fig)
        out[key] = fn
        print("  şekil:", fn)
    return out


def make_location_map(msl_ds, cells):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ccrs, cfeature = _cartopy()
    pc = ccrs.PlateCarree()
    oro = msl_ds["z"].isel(time=0) / G
    lsm = msl_ds["lsm"].isel(time=0)
    oro = oro.where(lsm >= 0.5)
    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(1, 1, 1, projection=pc)
    ax.set_extent([25.8, 29.4, 37.5, 39.3], pc)
    m = ax.pcolormesh(oro.longitude, oro.latitude, oro, cmap="terrain", vmin=-200, vmax=1600, shading="nearest",
                      transform=pc)
    ax.coastlines("10m", linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4)
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, linestyle=":")
    gl.top_labels = gl.right_labels = False
    for nm, (lat, lon, zs) in POINTS.items():
        ax.plot(lon, lat, "r*", markersize=13, transform=pc)
        ax.text(lon + 0.05, lat + 0.06, f"{nm}\n(gerçek ≈{zs} m)", fontsize=8, weight="bold", transform=pc)
        c = cells[nm]
        ax.plot(c["lon"], c["lat"], "kx", markersize=9, mew=2, transform=pc)
        ax.text(c["lon"] + 0.04, c["lat"] - 0.1, f"ERA5 hücresi ≈{c['z_grid']:.0f} m", fontsize=7, transform=pc)
    fig.colorbar(m, ax=ax, shrink=0.75, label="ERA5 model orografisi (m)")
    ins = fig.add_axes([0.62, 0.62, 0.22, 0.2], projection=pc)
    ins.set_extent([25, 45, 35.5, 42.5], pc)
    ins.coastlines("50m", linewidth=0.4)
    ins.add_feature(cfeature.BORDERS, linewidth=0.3)
    ins.plot([25.8, 29.4, 29.4, 25.8, 25.8], [37.5, 37.5, 39.3, 39.3, 37.5], "r-", transform=pc)
    ax.set_title("Çalışma alanı: İzmir ve Bozdağ (★ nokta, × kullanılan ERA5 kara hücresi)", fontsize=10)
    os.makedirs(FIG_DIR, exist_ok=True)
    fn = os.path.join(FIG_DIR, "konum_haritasi.png")
    fig.savefig(fn, dpi=170, bbox_inches="tight")
    plt.close(fig)
    print("  şekil:", fn)
    return fn


def make_skewt(profiles):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from metpy.plots import SkewT
    from metpy.units import units
    fig = plt.figure(figsize=(12, 6.5))
    for i, (nm, pr) in enumerate(profiles.items(), 1):
        sk = SkewT(fig, rotation=45, subplot=(1, 2, i))
        p = pr["p"] * units.hPa
        sk.plot(p, pr["t"] * units.degC, "r", linewidth=2, label="T")
        sk.plot(p, pr["td"] * units.degC, "g", linewidth=2, label="Td")
        sk.plot(p, pr["tw"] * units.degC, "b", linewidth=1, linestyle="--", label="Tw (ıslak termometre)")
        sk.plot_barbs(p, pr["u"] * 1.94384 * units.knots, pr["v"] * 1.94384 * units.knots)
        sk.plot_dry_adiabats(linewidth=0.5)
        sk.plot_moist_adiabats(linewidth=0.5)
        sk.plot_mixing_lines(linewidth=0.5)
        sk.ax.axvline(0, color="c", linewidth=1.5)
        sk.ax.set_ylim(1000, 300)
        sk.ax.set_xlim(-40, 30)
        sk.ax.set_title(f"{nm} — ERA5 profili {PROFILE_TIME.replace('T', ' ')} UTC\n"
                        f"Donma seviyesi ≈ {pr['fzl']:.0f} m, ıslak termometre 0 °C ≈ {pr['wbz']:.0f} m", fontsize=9)
        sk.ax.legend(loc="upper left", fontsize=7)
    fn = os.path.join(FIG_DIR, "skewt_era5.png")
    fig.tight_layout()
    fig.savefig(fn, dpi=170)
    plt.close(fig)
    print("  şekil:", fn)
    return fn


def get_satellite():
    """NASA Worldview Snapshots (MODIS Terra gerçek renk) — 2, 3, 4 Mayıs."""
    import io
    import requests
    from PIL import Image, ImageDraw
    imgs = []
    for day in ["2026-05-02", "2026-05-03", "2026-05-04"]:
        url = ("https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot"
               f"&TIME={day}T00:00:00Z&BBOX=35.5,24.5,41.5,32.5&CRS=EPSG:4326"
               "&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m"
               "&WRAP=day,x&FORMAT=image/jpeg&WIDTH=800&HEIGHT=600")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        im = Image.open(io.BytesIO(r.content)).convert("RGB")
        ImageDraw.Draw(im).text((10, 10), f"{'abc'[len(imgs)]}) {day[8:]}.{day[5:7]}.2026 MODIS Terra",
                                fill=(255, 255, 0))
        imgs.append(im)
    w, h = imgs[0].size
    canvas = Image.new("RGB", (w * 3 + 20, h), "white")
    for i, im in enumerate(imgs):
        canvas.paste(im, (i * (w + 10), 0))
    os.makedirs(FIG_DIR, exist_ok=True)
    fn = os.path.join(FIG_DIR, "uydu_worldview.jpg")
    canvas.save(fn, quality=90)
    print("  şekil:", fn)
    return fn


# ----------------------------------------------------------------------------- Excel
def _iso(d):
    return f"{d[6:]}-{d[3:5]}-{d[:2]}" if isinstance(d, str) else d.strftime("%Y-%m-%d")


def fill_excel(xlsx, stats, profiles):
    from openpyxl import load_workbook
    wb = load_workbook(xlsx)
    ws = wb["ERA5_Veri"]
    keys = ["tmin", "tmax", "tmean", "tp", "sf", "wmax", "msl", "t850", "z500", "z_grid"]
    for row in ws.iter_rows(min_row=2):
        d, name = row[0].value, row[1].value
        if not d or (_iso(d), name) not in stats:
            continue
        st = stats[(_iso(d), name)]
        for j, k in enumerate(keys):
            row[4 + j].value = round(st[k], 2)
    if "ERA5_Profil" in wb.sheetnames:
        wp = wb["ERA5_Profil"]
        for row in wp.iter_rows(min_row=2):
            nm = row[0].value
            if nm in profiles:
                pr = profiles[nm]
                row[2].value = round(float(pr["fzl"]), 0)
                row[3].value = round(float(pr["wbz"]), 0)
                row[4].value = round(float(pr["t850"]), 2)
    wb.save(xlsx)
    print("  Excel dolduruldu:", xlsx)


# ----------------------------------------------------------------------------- Word
def _set_cell(cell, text):
    p = cell.paragraphs[0]
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


def _f(x, nd=1):
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


def fill_docx(docx, stats, figs, profiles=None):
    from docx import Document
    from docx.shared import Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    shutil.copy(docx, docx.replace(".docx", "_yedek.docx"))
    doc = Document(docx)
    # 1) Şekiller
    for p in doc.paragraphs:
        for key, path in figs.items():
            tok = f"[[{key}]]"
            if tok in p.text and path and os.path.exists(path):
                for r in p.runs:
                    r.text = ""
                run = p.runs[0] if p.runs else p.add_run()
                run.add_picture(path, width=Cm(16))
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # 2) Tablo 2 (İzmir): ERA5 min/maks + sapma; son satır ortalama sapma / MAE
    t2 = next((t for t in doc.tables if t.cell(0, 2).text.strip().startswith("ERA5")), None)
    dmin, dmax = [], []
    if t2 is not None:
        for row in t2.rows[1:]:
            d = row.cells[0].text.strip()
            if len(d) == 10 and (_iso(d), "İzmir (merkez)") in stats:
                st = stats[(_iso(d), "İzmir (merkez)")]
                _set_cell(row.cells[2], _f(st["tmin"]))
                _set_cell(row.cells[5], _f(st["tmax"]))
                for col_mgm, val, col_b, acc in ((1, st["tmin"], 3, dmin), (4, st["tmax"], 6, dmax)):
                    try:
                        b = val - float(row.cells[col_mgm].text.replace(",", "."))
                        acc.append(b)
                        _set_cell(row.cells[col_b], f"{b:+.1f}")
                    except ValueError:
                        _set_cell(row.cells[col_b], "–")
            elif d.lower().startswith("mean bias"):
                _set_cell(row.cells[3], f"{np.mean(dmin):+.1f} / {np.mean(np.abs(dmin)):.1f}" if dmin else "–")
                _set_cell(row.cells[6], f"{np.mean(dmax):+.1f} / {np.mean(np.abs(dmax)):.1f}" if dmax else "–")
    # 3) Tablo 3 (Bozdağ): ızgara yüksekliği, ERA5 T, rakım düzeltmeli T, kar, T850
    t3 = next((t for t in doc.tables if "grid" in t.cell(0, 1).text.lower()), None)
    if t3 is not None:
        for row in t3.rows[1:]:
            d = row.cells[0].text.strip()
            key = (_iso(d), "Bozdağ (Ödemiş)") if len(d) == 10 else None
            if key in stats:
                st = stats[key]
                vals = [_f(st["z_grid"], 0), _f(st["tmin"]), _f(st["tmax"]), _f(st["tmin_corr"]),
                        _f(st["tmax_corr"]), _f(st["sf"])]
                for j, v in enumerate(vals, 1):
                    _set_cell(row.cells[j], v)
    # 4) Profil yer tutucuları
    if profiles:
        for p in doc.paragraphs:
            for nm, tag in (("İzmir (merkez)", "IZM"), ("Bozdağ (Ödemiş)", "BOZ")):
                for fld in ("fzl", "wbz"):
                    tok = f"{{{{{tag}_{fld.upper()}}}}}"
                    if tok in p.text:
                        for r in p.runs:
                            if tok in r.text:
                                r.text = r.text.replace(tok, f"{profiles[nm][fld]:.0f}")
    doc.save(docx)
    print("  Rapor güncellendi:", docx, "(yedek: *_yedek.docx)")


# ----------------------------------------------------------------------------- ana akış
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--docx", required=True)
    ap.add_argument("--skip-satellite", action="store_true")
    a = ap.parse_args()
    print("1/5 ERA5 indiriliyor (ilk çalıştırmada CDS kuyruğu nedeniyle uzun sürebilir)…")
    files = download_all()
    print("2/5 Veri okunuyor ve günlük istatistikler hesaplanıyor…")
    sl, pl, msl_ds, mpl_ds = load(files)
    stats, cells, profiles = compute_stats(sl, pl)
    for nm, c in cells.items():
        print(f"  {nm}: ERA5 hücresi {c['lat']:.2f}K {c['lon']:.2f}D, ızgara yüksekliği {c['z_grid']:.0f} m "
              f"(gerçek ≈{c['z_site']} m) | donma seviyesi ≈{profiles[nm]['fzl']:.0f} m, "
              f"Tw=0 seviyesi ≈{profiles[nm]['wbz']:.0f} m")
    print("3/5 Excel dolduruluyor…")
    fill_excel(a.xlsx, stats, profiles)
    print("4/5 Şekiller çiziliyor…")
    figs = {}
    try:
        maps = make_maps(msl_ds, mpl_ds)
        figs.update({"FIG3": maps["surface"], "FIG4": maps[850], "FIG5": maps[500], "FIG6": maps[300]})
        figs["FIG1"] = make_location_map(msl_ds, cells)
    except Exception as e:
        print("  ! harita çizilemedi (cartopy/scipy kurulu mu?):", e)
    try:
        figs["FIG8"] = make_skewt(profiles)
    except Exception as e:
        print("  ! Skew-T çizilemedi (metpy kurulu mu?):", e)
    if not a.skip_satellite:
        try:
            figs["FIG2"] = get_satellite()
        except Exception as e:
            print("  ! Uydu görüntüsü indirilemedi; Worldview'dan elle alın:", e)
    print("5/5 Rapor güncelleniyor…")
    fill_docx(a.docx, stats, figs, profiles)
    print("Bitti. Raporu Word'de açıp metindeki 'ERA5 sonucu' yorum cümlelerini sayılara göre kontrol edin.")


if __name__ == "__main__":
    sys.exit(main())

# Synoptic analysis – 1 to 4 May 2026

All charts are 12 UTC analyses. Click a date to open the original chart (DWD / Wetter3 / NASA).
They are not copied into this repository; `python src/fetch_maps.py` downloads them into `maps/` for study.

| Chart | 1 May | 2 May | 3 May | 4 May |
|---|---|---|---|---|
| Surface (DWD, fronts) | [01.05](https://www.wetter3.de/Archiv/GFS/2026050112_0.gif) | [02.05](https://www.wetter3.de/Archiv/GFS/2026050212_0.gif) | [03.05](https://www.wetter3.de/Archiv/GFS/2026050312_0.gif) | [04.05](https://www.wetter3.de/Archiv/GFS/2026050412_0.gif) |
| 850 hPa | [01.05](https://www.wetter3.de/Archiv/GFS/2026050112_25.gif) | [02.05](https://www.wetter3.de/Archiv/GFS/2026050212_25.gif) | [03.05](https://www.wetter3.de/Archiv/GFS/2026050312_25.gif) | [04.05](https://www.wetter3.de/Archiv/GFS/2026050412_25.gif) |
| 700 hPa | [01.05](https://www.wetter3.de/Archiv/GFS/2026050112_26.gif) | [02.05](https://www.wetter3.de/Archiv/GFS/2026050212_26.gif) | [03.05](https://www.wetter3.de/Archiv/GFS/2026050312_26.gif) | [04.05](https://www.wetter3.de/Archiv/GFS/2026050412_26.gif) |
| 500 hPa | [01.05](https://www.wetter3.de/Archiv/GFS/2026050112_27.gif) | [02.05](https://www.wetter3.de/Archiv/GFS/2026050212_27.gif) | [03.05](https://www.wetter3.de/Archiv/GFS/2026050312_27.gif) | [04.05](https://www.wetter3.de/Archiv/GFS/2026050412_27.gif) |
| 300 hPa jet | [01.05](https://www.wetter3.de/Archiv/GFS/2026050112_38.gif) | [02.05](https://www.wetter3.de/Archiv/GFS/2026050212_38.gif) | [03.05](https://www.wetter3.de/Archiv/GFS/2026050312_38.gif) | [04.05](https://www.wetter3.de/Archiv/GFS/2026050412_38.gif) |
| 500 hPa + MSLP | [01.05](https://www.wetter3.de/Archiv/GFS/2026050112_1.gif) | [02.05](https://www.wetter3.de/Archiv/GFS/2026050212_1.gif) | [03.05](https://www.wetter3.de/Archiv/GFS/2026050312_1.gif) | [04.05](https://www.wetter3.de/Archiv/GFS/2026050412_1.gif) |
| MODIS satellite | [01.05](https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot&TIME=2026-05-01T00:00:00Z&BBOX=34.5,19.5,43.5,32.5&CRS=EPSG:4326&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&WRAP=day,x&FORMAT=image/jpeg&WIDTH=1000&HEIGHT=700) | [02.05](https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot&TIME=2026-05-02T00:00:00Z&BBOX=34.5,19.5,43.5,32.5&CRS=EPSG:4326&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&WRAP=day,x&FORMAT=image/jpeg&WIDTH=1000&HEIGHT=700) | [03.05](https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot&TIME=2026-05-03T00:00:00Z&BBOX=34.5,19.5,43.5,32.5&CRS=EPSG:4326&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&WRAP=day,x&FORMAT=image/jpeg&WIDTH=1000&HEIGHT=700) | [04.05](https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot&TIME=2026-05-04T00:00:00Z&BBOX=34.5,19.5,43.5,32.5&CRS=EPSG:4326&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&WRAP=day,x&FORMAT=image/jpeg&WIDTH=1000&HEIGHT=700) |

## 1. Surface (DWD analysis)
- A broad **anticyclone of 1025–1030 hPa** sits over the eastern Atlantic and western Europe all period.
- On **2–3 May** a **frontal low with a trailing cold front** lies over the Black Sea – north-western Türkiye (eastern edge of the chart).
- The pressure gradient between the two drives the **northerly–north-easterly flow over the Aegean** (TSMS: 40–70 km/h).

## 2. 850 hPa – advection analysis
- 1 May: trough from north-eastern Europe towards the Black Sea, **0 to −5 °C** on its western flank.
- 3 May: **closed low ≈140 gpdm** over the Black Sea – NW Türkiye, **T850 ≈ 0 °C** near the core.
- Northerly wind crosses the isotherms from the cold Balkans towards the warm Aegean → **cold advection**.
- 850 hPa ≈ 1,400 m, so T850 ≈ 0 °C puts the **freezing level at ≈1,400–2,000 m**.

## 3. 700 hPa – ridge / trough
- Ridge over central Europe, closed low downstream: **≈296 gpdm, ≈ −10 °C** in the core on 3 May.

## 4. 500 hPa – ridge / trough, cut-off low
- Strongly amplified pattern: ridge over the Atlantic / central Europe, deep trough downstream.
- 1 May: trough axis NW Russia → Black Sea (552 gpdm, −30 °C). 2 May: closed low ≈547 gpdm.
- **3 May: cut-off low ≈544 gpdm, cold core −25 to −30 °C** over the Balkans – Black Sea – NW Türkiye.
- Cold pool aloft over a mild surface → steep lapse rate → **showers and thunderstorms**.
- 4 May: low shifted towards the Black Sea and weakened (≈547 gpdm).

## 5. 300 hPa – jet stream
- 1–2 May: jet streaks of **90–110 kt** along the eastern flank of the trough.
- 3–4 May: jet of **80–100 kt** curving around the southern and eastern flanks of the cut-off low.
- The Aegean lies in the weak winds of the cold core → ascent driven mainly by **instability**, not jet-streak divergence.

## 6. Satellite (MODIS Terra)
- 2 May: cloud over western Anatolia. **3 May: cellular, convective cloud field** over the Aegean coast and inland.
- 4 May: Aegean and Greece clear, cloud remains over Anatolia.

## 7. Vertical structure and the snow line
No İzmir radiosonde (17220) was available for 3–4 May in the University of Wyoming archive.
From 850 hPa the freezing level was ≈1,400–2,000 m. Inside heavy showers, **melting and evaporation of snowflakes
take heat from the air** and lower the snow level by several hundred metres – enough to bring snow to ≈1,100 m.
See `figures/snow_level_profile.png`.

## 8. ERA5 vs TSMS (data/processed)
| Quantity | Value |
|---|---|
| İzmir mean bias T min (ERA5 − TSMS) | −1.2 °C (MAE 1.5 °C) |
| İzmir mean bias T max | −3.8 °C (MAE 3.8 °C) |
| Part explained by ERA5 cell height (300 m vs 29 m) | ≈1.8 °C |
| Bozdağ ERA5 cell height | 685 m (≈415 m below the villages) |
| 3 May, ERA5 reduced to 1,100 m (T min / T max) | 3.1 / 5.2 °C |
| 3 May, ERA5 reduced to ski centre 1,540 m | 0.2 / 2.3 °C – TSMS forecast 0–2 °C ✔ |
| 3 May ERA5 precipitation / snowfall at Bozdağ | 16.5 mm / 0 mm |

**Reading:** ERA5 captures the cold air mass and the timing, and after terrain correction it reproduces the ski-centre
forecast – but it produces **no snow** because its smoothed terrain is too low and convective cooling is not resolved.

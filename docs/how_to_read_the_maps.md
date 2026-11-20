# How to read the charts used in this case

A short guide for reading (and hand-drawing) the surface and upper-level charts of this event.
The contour conventions below are the ones used in the MTO302E map-analysis assignment.

## Contour conventions

| Chart | Lines | Base | Interval | Analysis to do |
|---|---|---|---|---|
| Surface | isobars (hPa) | 1000 | 4 hPa | highs/lows, fronts, pressure gradient (wind) |
| 850 hPa | height (gpdm) | 150 | 3 gpdm | **temperature advection** |
| 700 hPa | height (gpdm) | 300 | 6 gpdm | ridge & trough |
| 500 hPa | height (gpdm) | 552 | 6 gpdm | ridge & trough, cut-off lows |
| 300 hPa | height (gpdm) | 900 | 6 gpdm | **jet stream** (isotachs) |
| All upper levels | isotherms (°C) | 0 | 2.5 °C | 0 °C and −20 °C blue, −25 green, −30 yellow, −35 brown, −40 black |

The Wetter3 charts linked in this repository use 4 gpdm at 850/500 hPa; when you redraw them by hand use the intervals above.

## Surface chart (DWD Bodenanalyse)
- **H / T** = Hoch / Tief (high / low). Blue triangles = cold front, red half-circles = warm front, purple = occlusion.
- Close isobars = strong wind. In the Northern Hemisphere wind blows with low pressure on the left, slightly across the isobars towards the low.
- Station plots: temperature upper-left, dew point lower-left, pressure upper-right, present weather in the middle.

## 850 hPa – advection
1. Draw the height contours: the wind blows roughly **parallel** to them.
2. Draw the isotherms (2.5 °C).
3. Where wind crosses isotherms **from cold to warm** → cold advection (CAA); from warm to cold → warm advection (WAA).
4. The more perpendicular the crossing and the stronger the wind, the stronger the advection.
- Rule of thumb: **T850 ≤ 0 °C** with precipitation → snow possible on hills and mountains; **T850 ≤ −5 °C** → snow to low ground.

## 700 / 500 hPa – ridges and troughs
- **Trough**: contours bulge towards the equator (U-shape) → cyclonic, ascent and cloud ahead (east) of the axis.
- **Ridge**: contours bulge poleward (∩-shape) → subsidence, fair weather.
- **Cut-off low**: a closed low separated from the westerlies; slow-moving, can bring days of showers.
- Cold core: isotherms form a closed cold pool around the low (here −25 to −30 °C at 500 hPa).
- 552 gpdm at 500 hPa is a rough boundary between cold and mild air masses in spring.

## 300 hPa – jet stream
- Shade isotachs ≥ 60–70 kt; the core of strongest winds is the **jet streak**.
- Four-quadrant rule (straight jet): **right entrance** and **left exit** → upper divergence → ascent at the surface.
- In a cut-off low the jet wraps around the edge; the cold core itself has weak winds.

## Satellite (MODIS true colour)
- Bright, lumpy **cellular** cloud = convection (showers, thunderstorms) in cold air.
- Smooth sheet cloud = stratiform, frontal cloud.

## Reading this event in one line
Surface northerly flow (H west, L east) → 850 hPa cold advection (T850 ≈ 0 °C) → 500 hPa cut-off low with a −25…−30 °C core
→ unstable, convective showers (satellite cells) → snow on the mountains at ≈1,100 m, rain at the coast.

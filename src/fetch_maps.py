"""Download the archived synoptic charts and satellite images listed in data/raw/chart_index.csv.

The charts are © Deutscher Wetterdienst / Wetter3 and the satellite images come from NASA
Worldview. They are NOT stored in this repository (copyright of the chart providers); this
script fetches them into ./maps/ (git-ignored) for personal study.

Usage:  python src/fetch_maps.py            # all charts
        python src/fetch_maps.py 500hPa     # only one level
"""
import csv
import sys
import time

import requests

from config import MAPS, RAW


def main(level=None):
    MAPS.mkdir(exist_ok=True)
    with open(RAW / "chart_index.csv", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if level in (None, r["level"])]
    for r in rows:
        ext = "jpg" if "wvs.earthdata" in r["url"] else "gif"
        out = MAPS / f"{r['date']}_{r['level']}.{ext}"
        if out.exists():
            continue
        resp = requests.get(r["url"], timeout=60, headers={"User-Agent": "izmir-may-snow-2026 (study)"})
        if resp.ok:
            out.write_bytes(resp.content)
            print("saved", out.name)
        else:
            print("failed", resp.status_code, r["url"])
        time.sleep(1)   # be polite to the archive


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

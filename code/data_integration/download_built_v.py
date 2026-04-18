#!/usr/bin/env python3
"""
Stage A: Download GHS-BUILT-V R2023A tiles (R6_C29) for 5 epochs, crop to Changsha.

Epochs downloaded: 1975, 1990, 2000, 2010, 2020 (all 100m Mollweide)
Tile R6_C29 confirmed to cover Changsha (x≈10,451–10,486k m, y≈3,419–3,444k m in Mollweide).

Output: data/integrated/ghs_built_v_changsha_{YEAR}.tif  (one per epoch, <500KB each)
Temporary ZIPs/TIFs in data/auxiliary_rasters/ghs_built_v/ are deleted after crop.
"""

import sys
import zipfile
import shutil
import subprocess
from pathlib import Path

import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds as window_from_bounds
from pyproj import Transformer
import numpy as np

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parents[2]
AUX_DIR   = ROOT / "data" / "auxiliary_rasters" / "ghs_built_v"
INT_DIR   = ROOT / "data" / "integrated"
BLDG_PATH = ROOT / "data" / "from_paper1" / "buildings_changsha_urban_core_solar_baseline.geojson"

AUX_DIR.mkdir(parents=True, exist_ok=True)
INT_DIR.mkdir(parents=True, exist_ok=True)

MOLLWEIDE = "ESRI:54009"
BUFFER_M  = 2000
EPOCHS    = [1975, 1990, 2000, 2010, 2020]

BASE_URL  = (
    "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/"
    "GHS_BUILT_V_GLOBE_R2023A/"
)


def tile_url(year: int) -> str:
    dname = f"GHS_BUILT_V_E{year}_GLOBE_R2023A_54009_100"
    fname = f"GHS_BUILT_V_E{year}_GLOBE_R2023A_54009_100_V1_0_R6_C29.zip"
    return f"{BASE_URL}{dname}/V1-0/tiles/{fname}"


def get_changsha_bbox() -> tuple:
    gdf = gpd.read_file(BLDG_PATH)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.set_crs("EPSG:4326")
    bounds = gdf.total_bounds
    t = Transformer.from_crs("EPSG:4326", MOLLWEIDE, always_xy=True)
    corners = [t.transform(bounds[i], bounds[j]) for i, j in [(0,1),(2,1),(0,3),(2,3)]]
    xs, ys = [c[0] for c in corners], [c[1] for c in corners]
    return (min(xs)-BUFFER_M, min(ys)-BUFFER_M, max(xs)+BUFFER_M, max(ys)+BUFFER_M)


def download_file(url: str, dest: Path, label: str) -> Path:
    if dest.exists():
        print(f"  ✓ Already downloaded: {dest.name} ({dest.stat().st_size/1e6:.1f} MB)")
        return dest
    print(f"  Downloading {label} …  {url}")
    tmp = dest.with_suffix(".tmp")
    try:
        subprocess.run(["curl", "-L", "--progress-bar", "-o", str(tmp), url], check=True)
        tmp.rename(dest)
        print(f"  ✓ Saved {dest.name} ({dest.stat().st_size/1e6:.1f} MB)")
    except subprocess.CalledProcessError as e:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"curl failed for {url}") from e
    return dest


def extract_tif(zip_path: Path, extract_dir: Path) -> Path:
    with zipfile.ZipFile(zip_path, "r") as zf:
        tif_names = [n for n in zf.namelist() if n.lower().endswith(".tif")]
        if not tif_names:
            raise RuntimeError(f"No .tif in {zip_path.name}")
        name = tif_names[0]
        out = extract_dir / Path(name).name
        if not out.exists():
            print(f"  Extracting {Path(name).name} …")
            zf.extract(name, extract_dir)
            extracted = extract_dir / name
            if extracted != out:
                shutil.move(str(extracted), str(out))
    return out


def crop_raster(src_path: Path, out_path: Path, bbox: tuple) -> None:
    if out_path.exists():
        print(f"  ✓ Already cropped: {out_path.name}")
        return
    xmin, ymin, xmax, ymax = bbox
    with rasterio.open(src_path) as src:
        window = window_from_bounds(xmin, ymin, xmax, ymax, src.transform)
        h = max(1, int(round(window.height)))
        w = max(1, int(round(window.width)))
        window = rasterio.windows.Window(window.col_off, window.row_off, w, h)
        data = src.read(window=window)
        transform = src.window_transform(window)
        profile = src.profile.copy()
        profile.update({"height": data.shape[1], "width": data.shape[2],
                        "transform": transform})
        with rasterio.open(out_path, "w", **profile) as dst:
            dst.write(data)
    print(f"  ✓ Cropped: {out_path.name} ({out_path.stat().st_size/1024:.0f} KB)")


def main():
    print("\n" + "="*60)
    print("Stage A: Download GHS-BUILT-V tiles → crop to Changsha")
    print("="*60)

    print("\nComputing Changsha Mollweide bbox …")
    bbox = get_changsha_bbox()
    print(f"  xmin={bbox[0]:.0f} ymin={bbox[1]:.0f} xmax={bbox[2]:.0f} ymax={bbox[3]:.0f}")

    failed = []
    for year in EPOCHS:
        print(f"\n── Epoch {year} ──")
        out_crop = INT_DIR / f"ghs_built_v_changsha_{year}.tif"

        if out_crop.exists():
            print(f"  ✓ Cropped file already present: {out_crop.name}")
            continue

        url  = tile_url(year)
        fname = f"GHS_BUILT_V_E{year}_GLOBE_R2023A_54009_100_V1_0_R6_C29.zip"
        dest = AUX_DIR / fname

        try:
            download_file(url, dest, f"BUILT-V {year}")
            tif_path = extract_tif(dest, AUX_DIR)
            crop_raster(tif_path, out_crop, bbox)
            if tif_path.exists(): tif_path.unlink()
            if dest.exists(): dest.unlink()
            print(f"  ✓ Cleaned up source files for {year}")
        except Exception as e:
            print(f"  ✗ FAILED for epoch {year}: {e}")
            failed.append(year)

    print("\n" + "="*60)
    if failed:
        print(f"FAILED EPOCHS: {failed}")
        print("Do NOT proceed — download these epochs manually and place TIFs in:")
        for y in failed:
            print(f"  data/integrated/ghs_built_v_changsha_{y}.tif")
        sys.exit(1)

    print("All epochs downloaded and cropped. Summary:")
    total_kb = 0
    for year in EPOCHS:
        p = INT_DIR / f"ghs_built_v_changsha_{year}.tif"
        kb = p.stat().st_size / 1024
        total_kb += kb
        # Quick value check
        with rasterio.open(p) as src:
            d = src.read(1)
            nd = src.nodata
            valid = d[d != nd] if nd is not None else d[d > 0]
            mx = float(valid.max()) if valid.size else 0
        print(f"  {year}: {kb:.0f} KB  max_value={mx:.0f} m³")
    print(f"  Total: {total_kb/1024:.1f} MB across {len(EPOCHS)} files")
    print("="*60)


if __name__ == "__main__":
    main()

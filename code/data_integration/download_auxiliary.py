#!/usr/bin/env python3
"""
Step 1: Download and crop auxiliary raster datasets for Paper 3 era classification.

Downloads:
  1. GHS-AGE R2025A 100m 10-year epochs (1980-2020) — global ZIP ~580 MB
     → crop to Changsha bbox + 2 km buffer → data/integrated/ghs_age_changsha.tif
     → delete global TIF after crop
  2. GHS-BUILT-H ANBH R2023A 100m tile R7_C30 — ~6 MB (20-30°N, 110-120°E)
     → crop to same bbox → data/integrated/ghs_built_h_changsha.tif
  3. GADM 4.1 China GPKG (optional, ~200 MB) → data/auxiliary_rasters/gadm/

Usage:
    python code/data_integration/download_auxiliary.py [--skip-gadm]
"""

import os
import sys
import zipfile
import tempfile
import shutil
import argparse
import subprocess
from pathlib import Path

import numpy as np
import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds as window_from_bounds
from pyproj import Transformer

# ── Resolve paths relative to repo root ───────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
AUX_AGE   = ROOT / "data" / "auxiliary_rasters" / "ghs_age"
AUX_BUILT = ROOT / "data" / "auxiliary_rasters" / "ghs_built_h"
AUX_GADM  = ROOT / "data" / "auxiliary_rasters" / "gadm"
INT_DIR   = ROOT / "data" / "integrated"
BLDG_PATH = ROOT / "data" / "from_paper1" / "buildings_changsha_urban_core_solar_baseline.geojson"

for d in (AUX_AGE, AUX_BUILT, AUX_GADM, INT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── URLs ──────────────────────────────────────────────────────────────────────
GHS_AGE_URL = (
    "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/"
    "GHS_AGE_GLOBE_R2025A/V1-0/"
    "GHS_AGE_1980102020_GLOBE_R2025A_54009_100_V1_0.zip"
)
GHS_BUILT_H_URL = (
    "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/"
    "GHS_BUILT_H_GLOBE_R2023A/GHS_BUILT_H_ANBH_E2018_GLOBE_R2023A_54009_100/"
    "V1-0/tiles/"
    "GHS_BUILT_H_ANBH_E2018_GLOBE_R2023A_54009_100_V1_0_R6_C29.zip"
    # R6_C29 covers x=[9959000,10959000], y=[3020047,4020047] in Mollweide
    # Changsha bbox (x≈10451–10486k, y≈3419–3444k) lies within this tile.
    # R7_C30 was incorrect (x=[10959000,11959000] — Changsha is to the west).
)
GADM_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/gadm41_CHN.gpkg"

# ── Mollweide CRS string ───────────────────────────────────────────────────────
MOLLWEIDE = "ESRI:54009"
BUFFER_M  = 2000  # 2 km edge buffer


def download_file(url: str, dest: Path, label: str) -> Path:
    """Download url to dest using curl (fast), skip if already exists."""
    if dest.exists():
        print(f"  ✓ Already downloaded: {dest.name} ({dest.stat().st_size/1e6:.1f} MB)")
        return dest
    print(f"  Downloading {label} …")
    print(f"    URL: {url}")
    tmp = dest.with_suffix(".tmp")
    try:
        result = subprocess.run(
            ["curl", "-L", "--progress-bar", "-o", str(tmp), url],
            check=True,
        )
        tmp.rename(dest)
        print(f"  ✓ Saved: {dest.name} ({dest.stat().st_size/1e6:.1f} MB)")
    except subprocess.CalledProcessError as e:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"curl download failed for {url}: {e}")
    return dest


def extract_tif_from_zip(zip_path: Path, extract_dir: Path) -> Path:
    """Extract the first .tif from zip_path into extract_dir; return its path."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        tif_names = [n for n in zf.namelist() if n.lower().endswith(".tif")]
        if not tif_names:
            raise RuntimeError(f"No .tif found inside {zip_path.name}")
        tif_name = tif_names[0]
        tif_path = extract_dir / Path(tif_name).name
        if not tif_path.exists():
            print(f"  Extracting {tif_name} …")
            zf.extract(tif_name, extract_dir)
            # Handle possible subdirectory in zip
            extracted = extract_dir / tif_name
            if extracted != tif_path:
                shutil.move(str(extracted), str(tif_path))
        else:
            print(f"  ✓ Already extracted: {tif_path.name}")
    return tif_path


def get_changsha_mollweide_bbox() -> tuple:
    """Return (xmin, ymin, xmax, ymax) in Mollweide with BUFFER_M buffer."""
    print("  Reading buildings extent …")
    gdf = gpd.read_file(BLDG_PATH)
    # Ensure WGS84
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.set_crs("EPSG:4326")
    bounds = gdf.total_bounds  # minx, miny, maxx, maxy in WGS84

    t = Transformer.from_crs("EPSG:4326", MOLLWEIDE, always_xy=True)
    # Transform all four corners for robustness
    corners = [
        t.transform(bounds[0], bounds[1]),
        t.transform(bounds[2], bounds[1]),
        t.transform(bounds[0], bounds[3]),
        t.transform(bounds[2], bounds[3]),
    ]
    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    bbox = (
        min(xs) - BUFFER_M,
        min(ys) - BUFFER_M,
        max(xs) + BUFFER_M,
        max(ys) + BUFFER_M,
    )
    print(f"  Changsha Mollweide bbox (+ {BUFFER_M/1000:.0f} km buffer):")
    print(f"    xmin={bbox[0]:.0f}  ymin={bbox[1]:.0f}")
    print(f"    xmax={bbox[2]:.0f}  ymax={bbox[3]:.0f}")
    return bbox


def crop_raster(src_path: Path, out_path: Path, bbox: tuple) -> None:
    """Crop src_path to bbox (in its native CRS) and write to out_path."""
    if out_path.exists():
        print(f"  ✓ Already cropped: {out_path.name}")
        return
    xmin, ymin, xmax, ymax = bbox
    with rasterio.open(src_path) as src:
        window = window_from_bounds(xmin, ymin, xmax, ymax, src.transform)
        data = src.read(window=window)
        transform = src.window_transform(window)
        profile = src.profile.copy()
        profile.update({
            "height": data.shape[1],
            "width":  data.shape[2],
            "transform": transform,
        })
        with rasterio.open(out_path, "w", **profile) as dst:
            dst.write(data)
    size_kb = out_path.stat().st_size / 1024
    print(f"  ✓ Cropped raster saved: {out_path.name} ({size_kb:.0f} KB)")


# ── Main ──────────────────────────────────────────────────────────────────────
def main(skip_gadm: bool = False):
    print("\n" + "=" * 60)
    print("Step 1: Download & crop auxiliary rasters")
    print("=" * 60)

    # --- Changsha bbox in Mollweide ---
    bbox = get_changsha_mollweide_bbox()

    # ── GHS-AGE ─────────────────────────────────────────────────────────────
    print("\n[1/3] GHS-AGE R2025A 100m (10-year epochs, 1980–2020)")
    age_cropped = INT_DIR / "ghs_age_changsha.tif"
    if age_cropped.exists():
        print(f"  ✓ Cropped file already present: {age_cropped.name}")
    else:
        age_zip  = AUX_AGE / "GHS_AGE_1980102020_GLOBE_R2025A_54009_100_V1_0.zip"
        age_glob = AUX_AGE / "GHS_AGE_1980102020_GLOBE_R2025A_54009_100_V1_0.tif"

        download_file(GHS_AGE_URL, age_zip, "GHS-AGE global 100m")

        if not age_glob.exists():
            age_glob = extract_tif_from_zip(age_zip, AUX_AGE)

        print("  Cropping to Changsha bbox …")
        crop_raster(age_glob, age_cropped, bbox)

        # Delete global TIF to save disk space (keep ZIP for provenance check)
        if age_glob.exists():
            age_glob.unlink()
            print(f"  ✓ Deleted global TIF to save space: {age_glob.name}")
        if age_zip.exists():
            age_zip.unlink()
            print(f"  ✓ Deleted global ZIP: {age_zip.name}")

    # ── GHS-BUILT-H ─────────────────────────────────────────────────────────
    print("\n[2/3] GHS-BUILT-H ANBH R2023A 100m (tile R7_C30)")
    bh_cropped = INT_DIR / "ghs_built_h_changsha.tif"
    if bh_cropped.exists():
        print(f"  ✓ Cropped file already present: {bh_cropped.name}")
    else:
        bh_zip  = AUX_BUILT / "GHS_BUILT_H_ANBH_E2018_GLOBE_R2023A_54009_100_V1_0_R7_C30.zip"
        bh_glob = None

        download_file(GHS_BUILT_H_URL, bh_zip, "GHS-BUILT-H tile R7_C30")
        bh_glob = extract_tif_from_zip(bh_zip, AUX_BUILT)

        print("  Cropping to Changsha bbox …")
        crop_raster(bh_glob, bh_cropped, bbox)

        if bh_glob and bh_glob.exists():
            bh_glob.unlink()
            print(f"  ✓ Deleted tile TIF: {bh_glob.name}")
        if bh_zip.exists():
            bh_zip.unlink()
            print(f"  ✓ Deleted tile ZIP: {bh_zip.name}")

    # ── GADM (optional) ────────────────────────────────────────────────────
    if not skip_gadm:
        print("\n[3/3] GADM 4.1 China GPKG (optional)")
        gadm_out = AUX_GADM / "gadm41_CHN.gpkg"
        try:
            download_file(GADM_URL, gadm_out, "GADM China GPKG")
        except Exception as e:
            print(f"  ⚠ GADM download failed (non-fatal): {e}")
            print("    District-level panel in figure will use spatial density map instead.")
    else:
        print("\n[3/3] Skipping GADM (--skip-gadm flag set)")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Download & crop complete. Output files:")
    for p in [INT_DIR / "ghs_age_changsha.tif", INT_DIR / "ghs_built_h_changsha.tif",
              AUX_GADM / "gadm41_CHN.gpkg"]:
        status = f"{p.stat().st_size/1024:.0f} KB" if p.exists() else "MISSING"
        print(f"  {p.relative_to(ROOT)}  [{status}]")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-gadm", action="store_true",
                        help="Skip GADM download (district panel will be a density map instead)")
    args = parser.parse_args()
    main(skip_gadm=args.skip_gadm)

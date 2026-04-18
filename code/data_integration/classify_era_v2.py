#!/usr/bin/env python3
"""
Stage B: Sample GHS-BUILT-V time series at building centroids, compute
rebuild-detection metrics, and assign provisional era via peak_growth_epoch.

Inputs:
  data/from_paper1/buildings_changsha_urban_core_solar_baseline.geojson
  data/integrated/ghs_built_v_changsha_{1975,1990,2000,2010,2020}.tif
  data/integrated/classified_buildings.csv   (v1 — for grid_id, ghsl_height_m)

Output:
  data/integrated/buildings_with_v_metrics.csv   (18,855 rows, no geometry)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.sample import sample_gen
from pyproj import Transformer

ROOT      = Path(__file__).resolve().parents[2]
BLDG_PATH = ROOT / "data" / "from_paper1" / "buildings_changsha_urban_core_solar_baseline.geojson"
INT_DIR   = ROOT / "data" / "integrated"
V1_CSV    = INT_DIR / "classified_buildings_v1_ghs_age_only.csv"
OUT_CSV   = INT_DIR / "buildings_with_v_metrics.csv"

MOLLWEIDE = "ESRI:54009"
EPOCHS    = [1975, 1990, 2000, 2010, 2020]
V_THRESHOLD = 100.0   # m³ — minimum volume to count as "built-up present"
GROWTH_THRESHOLD = 0.5  # 50% volume growth → flagged as likely rebuilt


def load_buildings() -> gpd.GeoDataFrame:
    """
    Use v1 CSV as the master 18,855-row spine (canonical IDs).
    Attach geometry from the GeoJSON (deduplicated first-occurrence per id).
    This avoids multipolygon-explosion duplicates in the raw GeoJSON.
    """
    print("Loading buildings …")
    # Master list: v1 CSV (18,855 rows, deduplicated)
    v1 = pd.read_csv(V1_CSV)
    print(f"  v1 CSV master: {len(v1):,} rows")

    # Geometry: GeoJSON, deduplicated by id
    gdf_raw = gpd.read_file(BLDG_PATH)
    if gdf_raw.crs is None or gdf_raw.crs.to_epsg() != 4326:
        gdf_raw = gdf_raw.set_crs("EPSG:4326")
    gdf_raw = gdf_raw[["id","geometry"]].drop_duplicates(subset="id", keep="first")

    # Join geometry onto v1 CSV
    gdf = gpd.GeoDataFrame(v1.merge(gdf_raw, on="id", how="left"), crs="EPSG:4326")
    n_no_geom = gdf["geometry"].isna().sum()
    if n_no_geom:
        print(f"  ⚠ {n_no_geom} buildings have no geometry — will use (0,0) centroid placeholder")
        from shapely.geometry import Point
        gdf["geometry"] = gdf["geometry"].fillna(gdf["geometry"].mode().iloc[0])
    print(f"  {len(gdf):,} buildings, CRS={gdf.crs}")
    return gdf


def compute_centroids_mollweide(gdf: gpd.GeoDataFrame) -> np.ndarray:
    gdf_m = gdf.to_crs(MOLLWEIDE)
    c = gdf_m.geometry.centroid
    return np.column_stack([c.x.values, c.y.values])


def sample_raster(tif_path: Path, coords: np.ndarray) -> np.ndarray:
    """Sample float raster; replace nodata and negatives with 0."""
    with rasterio.open(tif_path) as src:
        nd = src.nodata
        vals = np.array([v[0] for v in sample_gen(src, coords)], dtype=float)
    if nd is not None:
        vals[vals == nd] = 0.0
    vals[~np.isfinite(vals)] = 0.0
    vals[vals < 0] = 0.0
    return vals


def peak_growth_epoch(row) -> int:
    """
    Return the epoch whose PRECEDING interval had the largest absolute volume jump.
    Epochs and their preceding intervals:
      1990: v1990 - v1975
      2000: v2000 - v1990
      2010: v2010 - v2000
      2020: v2020 - v2010
    Return the end-epoch of the largest interval.
    Returns 0 if all volumes are zero (nodata cell).
    """
    deltas = {
        1990: row["v1990"] - row["v1975"],
        2000: row["v2000"] - row["v1990"],
        2010: row["v2010"] - row["v2000"],
        2020: row["v2020"] - row["v2010"],
    }
    max_delta = max(deltas.values())
    if max_delta <= 0:
        return 0   # No growth detected at all
    return max(deltas, key=deltas.get)


def first_builtup_epoch(row) -> int:
    for y in EPOCHS:
        if row[f"v{y}"] >= V_THRESHOLD:
            return y
    return 0


def provisional_era(peak_ep: int, first_ep: int) -> str:
    """
    Use peak_growth_epoch as primary signal; fall back to first_builtup when no growth.
    """
    ep = peak_ep if peak_ep > 0 else first_ep
    if ep == 0:
        return "era1"   # no signal → oldest era (conservative)
    if ep <= 2000:
        return "era1"
    if ep == 2010:
        return "era2"
    return "era3"  # ep == 2020


def main():
    print("\n" + "="*60)
    print("Stage B: Volume metrics + provisional era assignment")
    print("="*60)

    for y in EPOCHS:
        p = INT_DIR / f"ghs_built_v_changsha_{y}.tif"
        if not p.exists():
            raise FileNotFoundError(f"Missing: {p}. Run download_built_v.py first.")

    gdf = load_buildings()
    print("Computing Mollweide centroids …")
    coords = compute_centroids_mollweide(gdf)

    # ── Sample BUILT-V at each epoch ─────────────────────────────────────────
    vol_cols = {}
    for year in EPOCHS:
        p = INT_DIR / f"ghs_built_v_changsha_{year}.tif"
        print(f"  Sampling {year} …")
        vol_cols[f"v{year}"] = sample_raster(p, coords)

    df = gdf[["id"]].copy()
    for col, vals in vol_cols.items():
        df[col] = vals

    # ── Rebuild metrics ───────────────────────────────────────────────────────
    print("Computing rebuild metrics …")
    df["first_builtup_epoch"] = df.apply(first_builtup_epoch, axis=1)
    df["peak_growth_epoch"]   = df.apply(peak_growth_epoch, axis=1)

    df["v_growth_post2000"] = (df["v2020"] - df["v2000"]) / df["v2000"].clip(lower=1)
    df["v_growth_post2010"] = (df["v2020"] - df["v2010"]) / df["v2010"].clip(lower=1)
    df["likely_rebuilt_post2000"] = df["v_growth_post2000"] > GROWTH_THRESHOLD
    df["likely_rebuilt_post2010"] = df["v_growth_post2010"] > GROWTH_THRESHOLD

    # Recency score (higher = more recent construction mass)
    df["recency_score"] = (
        (df["v2020"] - df["v2000"]) / df["v2020"].clip(lower=1)
        + 0.3 * (df["v2020"] - df["v1990"]) / df["v2020"].clip(lower=1)
    )
    # Clip to reasonable range
    df["recency_score"] = df["recency_score"].clip(-2, 2)

    # ── Provisional era ───────────────────────────────────────────────────────
    df["era_provisional"] = [
        provisional_era(int(r["peak_growth_epoch"]), int(r["first_builtup_epoch"]))
        for _, r in df.iterrows()
    ]

    # ── Merge back all columns from v1 CSV ───────────────────────────────────
    v1_cols = pd.read_csv(V1_CSV)
    # Deduplicate v1 by id before merge to prevent row explosion
    v1_cols = v1_cols.drop_duplicates(subset="id", keep="first")
    merge_cols = ["id", "building", "building_category", "footprint_area_m2",
                  "height_proxy_m", "height_proxy_source", "ghsl_height_m",
                  "solar_potential_score", "solar_potential_class", "is_high_potential",
                  "ghs_age_epoch", "ghs_age_epoch_label", "era", "typology",
                  "era_source", "grid_id"]
    merge_cols = [c for c in merge_cols if c in v1_cols.columns]
    df = df.merge(v1_cols[merge_cols], on="id", how="left")

    # ── Summary ───────────────────────────────────────────────────────────────
    total = len(df)
    print(f"\nProvisional era distribution (peak_growth_epoch logic):")
    for era in ["era1", "era2", "era3"]:
        n = (df["era_provisional"] == era).sum()
        print(f"  {era}: {n:,} ({100*n/total:.1f}%)")

    n_rb2000 = df["likely_rebuilt_post2000"].sum()
    n_rb2010 = df["likely_rebuilt_post2010"].sum()
    print(f"\nLikely rebuilt post-2000 (>50% volume growth): {n_rb2000:,} ({100*n_rb2000/total:.1f}%)")
    print(f"Likely rebuilt post-2010 (>50% volume growth): {n_rb2010:,} ({100*n_rb2010/total:.1f}%)")

    n_no_signal = (df["first_builtup_epoch"] == 0).sum()
    print(f"No volume signal (all epochs below threshold): {n_no_signal:,} ({100*n_no_signal/total:.1f}%)")

    # Hard dedup by id before saving (some OSM IDs appear in both 'way' and
    # 'relation' representations; keep first occurrence throughout the pipeline)
    n_before = len(df)
    df = df.drop_duplicates(subset="id", keep="first").reset_index(drop=True)
    if len(df) < n_before:
        print(f"  Final dedup: {n_before} → {len(df)} rows ({n_before-len(df)} OSM-ID duplicates removed)")

    df.to_csv(OUT_CSV, index=False)
    print(f"\n✓ Saved: {OUT_CSV.relative_to(ROOT)} ({OUT_CSV.stat().st_size/1024:.0f} KB)  [{len(df):,} buildings]")


if __name__ == "__main__":
    main()

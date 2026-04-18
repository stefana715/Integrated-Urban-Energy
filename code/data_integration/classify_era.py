#!/usr/bin/env python3
"""
Step 2: Classify all 18,855 buildings into Era 1 / Era 2 / Era 3.

Era mapping (GHS-AGE R2025A 10-year epoch → Paper 2 era):
  epoch 1 = built pre-1980   → Era 1
  epoch 2 = built 1980-1989  → Era 1
  epoch 3 = built 1990-1999  → Era 1
  epoch 4 = built 2000-2009  → Era 2
  epoch 5 = built 2010-2020  → Era 3
  nodata/0                   → fallback: height_proxy heuristic

Typology:
  height_proxy_m ≤ 18 m → midrise  (≤6 floors × 3 m)
  height_proxy_m  > 18 m → highrise

Outputs:
  data/integrated/classified_buildings.geojson  (geometry retained)
  data/integrated/classified_buildings.csv      (no geometry, for inspection)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.sample import sample_gen
from pyproj import Transformer

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parents[2]
BLDG_PATH = ROOT / "data" / "from_paper1" / "buildings_changsha_urban_core_solar_baseline.geojson"
GRID_PATH = ROOT / "data" / "from_paper1" / "grid_changsha_urban_core_solar_baseline.geojson"
AGE_PATH  = ROOT / "data" / "integrated" / "ghs_age_changsha.tif"
BH_PATH   = ROOT / "data" / "integrated" / "ghs_built_h_changsha.tif"
OUT_GJSON = ROOT / "data" / "integrated" / "classified_buildings.geojson"
OUT_CSV   = ROOT / "data" / "integrated" / "classified_buildings.csv"

MOLLWEIDE = "ESRI:54009"
TYPOLOGY_THRESHOLD_M = 18.0   # ≤18 m → midrise (≤6 floors at 3 m/floor)

# GHS-AGE epoch → era mapping
EPOCH_ERA = {1: "era1", 2: "era1", 3: "era1", 4: "era2", 5: "era3"}
EPOCH_LABEL = {
    0: "nodata",
    1: "pre-1980",
    2: "1980-1989",
    3: "1990-1999",
    4: "2000-2009",
    5: "2010-2020",
}


def load_buildings() -> gpd.GeoDataFrame:
    print("Loading buildings …")
    gdf = gpd.read_file(BLDG_PATH)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.set_crs("EPSG:4326")
    print(f"  {len(gdf):,} buildings loaded, CRS: {gdf.crs}")
    return gdf


def compute_centroids_mollweide(gdf: gpd.GeoDataFrame) -> np.ndarray:
    """Return (N, 2) array of centroid coordinates in Mollweide."""
    print("Computing centroids and reprojecting to Mollweide …")
    gdf_moll = gdf.to_crs(MOLLWEIDE)
    centroids = gdf_moll.geometry.centroid
    coords = np.column_stack([centroids.x.values, centroids.y.values])
    return coords


def sample_raster(tif_path: Path, coords_moll: np.ndarray,
                  nodata_replace: float = np.nan) -> np.ndarray:
    """Sample a Mollweide raster at coords_moll; return 1-D array of values."""
    print(f"  Sampling {tif_path.name} …")
    with rasterio.open(tif_path) as src:
        nodata = src.nodata
        gen = sample_gen(src, coords_moll)
        values = np.array([v[0] for v in gen], dtype=float)
        if nodata is not None:
            values[values == nodata] = nodata_replace
        # Also treat 0 as nodata for GHS-AGE (0 = no built-up detected)
        if "ghs_age" in tif_path.name:
            values[values == 0] = nodata_replace
    return values


def assign_era(epoch: float, height_proxy_m: float) -> tuple:
    """
    Returns (era, era_source) where era_source is 'ghs_age' or 'height_fallback'.
    """
    if not np.isnan(epoch) and int(epoch) in EPOCH_ERA:
        return EPOCH_ERA[int(epoch)], "ghs_age"
    # Fallback: height heuristic
    if height_proxy_m > 30:
        return "era3", "height_fallback"
    elif height_proxy_m > 15:
        return "era2", "height_fallback"
    else:
        return "era1", "height_fallback"


def assign_typology(height_proxy_m: float) -> str:
    return "highrise" if height_proxy_m > TYPOLOGY_THRESHOLD_M else "midrise"


def spatial_join_grid_id(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Join grid_id from grid polygons to buildings via centroid-in-polygon."""
    print("Spatial join: assigning grid_id to each building …")
    grid = gpd.read_file(GRID_PATH)
    if grid.crs is None or grid.crs.to_epsg() != 4326:
        grid = grid.set_crs("EPSG:4326")

    # Use building centroids (reproject to Mollweide first to avoid geographic CRS warning)
    gdf_proj = gdf.to_crs("ESRI:54009")
    grid_proj = grid.to_crs("ESRI:54009")
    centroids_gdf = gdf_proj.copy()
    centroids_gdf.geometry = gdf_proj.geometry.centroid
    centroids_gdf = centroids_gdf.set_crs("ESRI:54009")
    grid = grid_proj

    joined = gpd.sjoin(
        centroids_gdf[["id", "geometry"]],
        grid[["grid_id", "geometry"]],
        how="left",
        predicate="within",
    )
    # Drop right_index column if present
    joined = joined.drop(columns=["index_right"], errors="ignore")

    # Deduplicate: if a centroid falls on a shared boundary it may match >1 cell;
    # keep the first (lowest grid_id) to preserve 1-to-1 mapping.
    joined = joined.drop_duplicates(subset="id", keep="first")

    gdf = gdf.merge(joined[["id", "grid_id"]], on="id", how="left")
    n_assigned = gdf["grid_id"].notna().sum()
    n_missing  = gdf["grid_id"].isna().sum()
    print(f"  {n_assigned:,} buildings assigned a grid_id, {n_missing} unassigned (outside grid extent)")
    return gdf


def main():
    print("\n" + "=" * 60)
    print("Step 2: Building era + typology classification")
    print("=" * 60)

    # Check prerequisites
    for p in (BLDG_PATH, AGE_PATH, BH_PATH):
        if not p.exists():
            raise FileNotFoundError(
                f"Required file missing: {p}\n"
                f"Run download_auxiliary.py first."
            )

    # ── Load buildings ────────────────────────────────────────────────────────
    gdf = load_buildings()

    # Keep only needed input columns; preserve geometry
    keep_cols = [
        "id", "building", "building_category",
        "footprint_area_m2", "height_proxy_m", "height_proxy_source",
        "solar_potential_score", "solar_potential_class",
        "is_high_potential", "start_date", "building:levels",
        "geometry",
    ]
    keep_cols = [c for c in keep_cols if c in gdf.columns]
    gdf = gdf[keep_cols].copy()

    # ── Sample rasters ────────────────────────────────────────────────────────
    print("\nSampling GHS rasters at building centroids …")
    coords_moll = compute_centroids_mollweide(gdf)
    ghs_age_vals   = sample_raster(AGE_PATH, coords_moll, nodata_replace=np.nan)
    ghsl_height_vals = sample_raster(BH_PATH, coords_moll, nodata_replace=np.nan)

    gdf["ghs_age_epoch"]  = ghs_age_vals
    gdf["ghsl_height_m"]  = ghsl_height_vals

    # ── Assign era and typology ───────────────────────────────────────────────
    print("\nAssigning era and typology …")
    era_results = [
        assign_era(epoch, h)
        for epoch, h in zip(gdf["ghs_age_epoch"].values, gdf["height_proxy_m"].values)
    ]
    gdf["era"]        = [r[0] for r in era_results]
    gdf["era_source"] = [r[1] for r in era_results]
    gdf["typology"]   = gdf["height_proxy_m"].apply(assign_typology)

    # Epoch label for readability
    gdf["ghs_age_epoch_label"] = gdf["ghs_age_epoch"].apply(
        lambda v: EPOCH_LABEL.get(int(v), "nodata") if not np.isnan(v) else "nodata"
    )

    # ── Spatial join grid_id ─────────────────────────────────────────────────
    print()
    gdf = spatial_join_grid_id(gdf)

    # ── Floor count estimate ──────────────────────────────────────────────────
    gdf["floor_count_est"] = (gdf["height_proxy_m"] / 3.0).apply(np.ceil).astype(int)
    # Estimated floor area (footprint × floors)
    gdf["floor_area_m2"] = gdf["footprint_area_m2"] * gdf["floor_count_est"]

    # ── Summary statistics ────────────────────────────────────────────────────
    print("\n" + "-" * 40)
    print("Classification summary")
    print("-" * 40)

    total = len(gdf)
    for era in ["era1", "era2", "era3"]:
        n = (gdf["era"] == era).sum()
        print(f"  {era}: {n:,} buildings ({100*n/total:.1f}%)")

    print()
    for typ in ["midrise", "highrise"]:
        n = (gdf["typology"] == typ).sum()
        print(f"  {typ}: {n:,} buildings ({100*n/total:.1f}%)")

    print()
    n_ghs = (gdf["era_source"] == "ghs_age").sum()
    n_fb  = (gdf["era_source"] == "height_fallback").sum()
    print(f"  Era source — ghs_age: {n_ghs:,}  |  height_fallback: {n_fb:,}")

    print()
    print("Era × Typology breakdown:")
    ct = pd.crosstab(gdf["era"], gdf["typology"])
    print(ct.to_string())

    print()
    print("GHS-AGE epoch distribution:")
    ep_counts = gdf["ghs_age_epoch_label"].value_counts().sort_index()
    for label, cnt in ep_counts.items():
        print(f"  {label}: {cnt:,} ({100*cnt/total:.1f}%)")

    # ── Save outputs ─────────────────────────────────────────────────────────
    print(f"\nSaving GeoJSON → {OUT_GJSON.relative_to(ROOT)} …")
    # Column order for GeoJSON
    output_cols = [
        "id", "building", "building_category",
        "footprint_area_m2", "floor_count_est", "floor_area_m2",
        "height_proxy_m", "height_proxy_source",
        "solar_potential_score", "solar_potential_class", "is_high_potential",
        "ghs_age_epoch", "ghs_age_epoch_label", "ghsl_height_m",
        "era", "typology", "era_source",
        "grid_id",
        "geometry",
    ]
    output_cols = [c for c in output_cols if c in gdf.columns]
    gdf[output_cols].to_file(OUT_GJSON, driver="GeoJSON")
    print(f"  Saved: {OUT_GJSON.stat().st_size/1e6:.1f} MB")

    print(f"Saving CSV → {OUT_CSV.relative_to(ROOT)} …")
    csv_cols = [c for c in output_cols if c != "geometry"]
    gdf[csv_cols].to_csv(OUT_CSV, index=False)
    print(f"  Saved: {OUT_CSV.stat().st_size/1024:.0f} KB")

    print("\n✓ Classification complete.")
    return gdf


if __name__ == "__main__":
    main()

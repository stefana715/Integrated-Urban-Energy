#!/usr/bin/env python3
"""
Stage C: Calibrate era distribution to 40/28/32 target proportions using
recency_score quantile assignment. Assign GHSL-based typology.

Inputs:
  data/integrated/buildings_with_v_metrics.csv
  data/integrated/classified_buildings.geojson   (geometry source)
  data/integrated/ghs_built_h_changsha.tif       (GHSL height, already cropped)

Outputs:
  data/integrated/classified_buildings_v1_ghs_age_only.{geojson,csv}  (renamed v1)
  data/integrated/classified_buildings.{geojson,csv}                  (canonical v2)
"""

from pathlib import Path
import shutil
import numpy as np
import pandas as pd
import geopandas as gpd

ROOT     = Path(__file__).resolve().parents[2]
INT_DIR  = ROOT / "data" / "integrated"

METRICS_CSV = INT_DIR / "buildings_with_v_metrics.csv"
V1_GJSON    = INT_DIR / "classified_buildings.geojson"
V1_CSV      = INT_DIR / "classified_buildings.csv"

OUT_GJSON   = INT_DIR / "classified_buildings.geojson"   # will overwrite v1 → rename first
OUT_CSV     = INT_DIR / "classified_buildings.csv"

V1_GJSON_BK = INT_DIR / "classified_buildings_v1_ghs_age_only.geojson"
V1_CSV_BK   = INT_DIR / "classified_buildings_v1_ghs_age_only.csv"
V1_REPORT   = INT_DIR / "classification_validation.md"
V1_REPORT_BK= INT_DIR / "classification_validation_v1.md"

# Target proportions (Zhang et al. 2025 + expert adjustment for urban core)
TARGET = {"era1": 0.40, "era2": 0.28, "era3": 0.32}
TYPOLOGY_THRESHOLD_M = 18.0  # m — GHSL ANBH threshold


def rename_v1_files():
    for src, dst in [(V1_GJSON, V1_GJSON_BK),
                     (V1_CSV, V1_CSV_BK),
                     (V1_REPORT, V1_REPORT_BK)]:
        if src.exists() and not dst.exists():
            shutil.copy2(str(src), str(dst))
            print(f"  Backed up: {dst.name}")
        elif dst.exists():
            print(f"  Already backed up: {dst.name}")


def calibrate_eras(df: pd.DataFrame) -> pd.Series:
    """
    Quantile-based era reassignment using recency_score.
    Lowest 40% → era1, next 28% → era2, top 32% → era3.
    """
    n = len(df)
    n1 = int(round(n * TARGET["era1"]))
    n2 = int(round(n * TARGET["era2"]))
    n3 = n - n1 - n2

    # Sort by recency_score ascending; ties broken by id (stable, reproducible)
    order = df[["recency_score", "id"]].copy()
    order["rank"] = order["recency_score"].rank(method="first")
    idx_sorted = order["rank"].argsort().values   # indices sorted by rank asc

    era_final = pd.Series(index=df.index, dtype=str)
    era_final.iloc[idx_sorted[:n1]]       = "era1"
    era_final.iloc[idx_sorted[n1:n1+n2]]  = "era2"
    era_final.iloc[idx_sorted[n1+n2:]]    = "era3"
    return era_final


def assign_typology(ghsl_h: pd.Series, height_proxy: pd.Series) -> pd.Series:
    """
    Use GHSL ANBH as canonical height; fall back to height_proxy_m where null/zero.
    """
    h = ghsl_h.copy()
    mask_fallback = h.isna() | (h <= 0)
    h[mask_fallback] = height_proxy[mask_fallback]
    return pd.Series(
        np.where(h > TYPOLOGY_THRESHOLD_M, "highrise", "midrise"),
        index=ghsl_h.index,
    )


def floor_area(footprint: pd.Series, height: pd.Series) -> pd.Series:
    floor_count = np.maximum(np.ceil(height / 3.0), 1).astype(int)
    return footprint * floor_count


def main():
    print("\n" + "="*60)
    print("Stage C: Calibrated era assignment + GHSL-height typology")
    print("="*60)

    if not METRICS_CSV.exists():
        raise FileNotFoundError(f"Missing: {METRICS_CSV}. Run classify_era_v2.py first.")

    # ── Back up v1 files ──────────────────────────────────────────────────────
    print("\nBacking up v1 files …")
    rename_v1_files()

    # ── Load metrics ──────────────────────────────────────────────────────────
    print("\nLoading volume metrics …")
    df = pd.read_csv(METRICS_CSV)
    n_before = len(df)
    df = df.drop_duplicates(subset="id", keep="first").reset_index(drop=True)
    print(f"  {n_before:,} rows loaded → {len(df):,} after dedup")

    # ── Typology (GHSL height, canonical) ────────────────────────────────────
    print("Assigning typology from GHSL ANBH …")
    df["building_height_m"] = df["ghsl_height_m"].where(
        df["ghsl_height_m"].notna() & (df["ghsl_height_m"] > 0),
        df["height_proxy_m"]
    )
    n_ghsl = (df["ghsl_height_m"].notna() & (df["ghsl_height_m"] > 0)).sum()
    n_proxy = len(df) - n_ghsl
    print(f"  GHSL height used: {n_ghsl:,}  |  height_proxy fallback: {n_proxy:,}")

    df["typology"] = assign_typology(df["ghsl_height_m"], df["height_proxy_m"])
    df["floor_count_est"] = np.maximum(np.ceil(df["building_height_m"] / 3.0), 1).astype(int)
    df["floor_area_m2"] = df["footprint_area_m2"] * df["floor_count_est"]

    # ── Era calibration ───────────────────────────────────────────────────────
    print("Calibrating eras to 40/28/32 …")
    df["era_final"] = calibrate_eras(df)

    # Verify counts
    total = len(df)
    for era in ["era1", "era2", "era3"]:
        n = (df["era_final"] == era).sum()
        tgt = int(round(total * TARGET[era]))
        print(f"  {era}: {n:,}  (target≈{tgt:,}, {100*n/total:.1f}%)")

    # ── Concordance v1 vs v2 ─────────────────────────────────────────────────
    # v1 era stored in column 'era' from the old CSV (already in df via merge)
    print("\nConcordance (v1 GHS-AGE vs v2_final calibrated):")
    same = (df["era"] == df["era_final"]).sum()
    print(f"  Same era: {same:,} ({100*same/total:.1f}%)")
    print(f"  Changed:  {total-same:,} ({100*(total-same)/total:.1f}%)")
    cm_v1_v2 = pd.crosstab(df["era"], df["era_final"],
                            rownames=["v1"], colnames=["v2_final"])
    print("\n  Confusion matrix (rows=v1, cols=v2_final):")
    print(cm_v1_v2.to_string())

    print("\nConcordance (v2_provisional vs v2_final):")
    same_prov = (df["era_provisional"] == df["era_final"]).sum()
    print(f"  Same era: {same_prov:,} ({100*same_prov/total:.1f}%)")
    cm_prov_v2 = pd.crosstab(df["era_provisional"], df["era_final"],
                              rownames=["provisional"], colnames=["v2_final"])
    print("\n  Confusion matrix (rows=provisional, cols=v2_final):")
    print(cm_prov_v2.to_string())

    # ── Floor area summary ────────────────────────────────────────────────────
    print("\nFloor area (Mm²) by era (v2_final):")
    fa = df.groupby("era_final")["floor_area_m2"].sum() / 1e6
    for era in ["era1", "era2", "era3"]:
        print(f"  {era}: {fa.get(era,0):.2f} Mm²")

    # ── Build canonical output columns ───────────────────────────────────────
    output_cols = [
        "id", "building", "building_category",
        "footprint_area_m2", "floor_count_est", "floor_area_m2",
        "height_proxy_m", "height_proxy_source",
        "ghsl_height_m", "building_height_m",
        "solar_potential_score", "solar_potential_class", "is_high_potential",
        "ghs_age_epoch", "ghs_age_epoch_label",
        "v1975", "v1990", "v2000", "v2010", "v2020",
        "first_builtup_epoch", "peak_growth_epoch",
        "v_growth_post2000", "v_growth_post2010",
        "likely_rebuilt_post2000", "likely_rebuilt_post2010",
        "recency_score",
        "era_provisional", "era_final",
        "typology",
        "grid_id",
    ]
    output_cols = [c for c in output_cols if c in df.columns]

    # ── Save CSV ──────────────────────────────────────────────────────────────
    df[output_cols].to_csv(OUT_CSV, index=False)
    print(f"\n✓ CSV saved: {OUT_CSV.relative_to(ROOT)} ({OUT_CSV.stat().st_size/1024:.0f} KB)")

    # ── Save GeoJSON (merge back geometry) ───────────────────────────────────
    print("Merging geometry and saving GeoJSON …")
    gdf_geo = gpd.read_file(V1_GJSON_BK)[["id", "geometry"]]
    gdf_out = gdf_geo.merge(df[output_cols], on="id", how="left")
    gdf_out.to_file(OUT_GJSON, driver="GeoJSON")
    print(f"✓ GeoJSON saved: {OUT_GJSON.relative_to(ROOT)} ({OUT_GJSON.stat().st_size/1e6:.1f} MB)")
    print("="*60)


if __name__ == "__main__":
    main()

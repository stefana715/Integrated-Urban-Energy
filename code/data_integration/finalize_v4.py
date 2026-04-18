#!/usr/bin/env python3
"""
Task 2 v4 (final): hybrid canonical height + ternary typology + Era 3 downgrade.

Stages:
  A — Compute canonical_height_m (hybrid of ghsl_height_m and height_proxy_m)
  B — Re-apply ternary typology rules using canonical_height_m
  C — Downgrade Era 3 LowRise buildings with weak post-2010 growth to Era 2
  D — Recompute PV generation with v4 typology and floor areas

Inputs:
  data/integrated/classified_buildings.csv / .geojson   (v3, to be overwritten)

Outputs:
  data/integrated/classified_buildings_v3_backup.geojson   (preserved)
  data/integrated/classified_buildings.csv                 (v4, canonical)
  data/integrated/classified_buildings.geojson             (v4, canonical)
"""

from pathlib import Path
import shutil
import numpy as np
import pandas as pd
import geopandas as gpd

ROOT    = Path(__file__).resolve().parents[2]
INT_DIR = ROOT / "data" / "integrated"

IN_CSV    = INT_DIR / "classified_buildings.csv"
IN_GJSON  = INT_DIR / "classified_buildings.geojson"
OUT_CSV   = INT_DIR / "classified_buildings.csv"
OUT_GJSON = INT_DIR / "classified_buildings.geojson"
BK_GJSON  = INT_DIR / "classified_buildings_v3_backup.geojson"

PV_RATE = {"lowrise": 38.8, "midrise": 27.4, "highrise": 6.1}

# Hybrid height thresholds
AGREE_TOL     = 5.0    # m — |ghsl − proxy| < this → average
CAP_RATIO     = 2.0    # ghsl > ratio × proxy → cap
CAP_FACTOR    = 1.5    # cap = proxy × factor

# Typology thresholds (on canonical_height_m)
LOW_MID_M   = 18.0
MID_HIGH_M  = 36.0
ERA1_CAP_M  = 30.0    # Era-1 prior: canonical < this → lowrise
SLAB_FP_M2  = 2500.0  # large-slab footprint
SLAB_H_M    = 25.0    # large-slab height cap

# Era 3 downgrade
ERA3_GROWTH_THRESH = 0.3   # v_growth_post2010 < this → downgrade to era2


# ── Stage A: Hybrid canonical height ─────────────────────────────────────────
def hybrid_height(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Return (canonical_height_m, height_source) Series."""
    ghsl  = df["ghsl_height_m"].copy()
    proxy = df["height_proxy_m"].copy()

    canonical = pd.Series(np.nan, index=df.index)
    source    = pd.Series("", index=df.index, dtype=str)

    # Rule 1: null / zero GHSL → proxy only
    null = (ghsl.isna()) | (ghsl <= 0)
    canonical[null] = proxy[null]
    source[null]    = "proxy_only"

    # Rule 2: agreement within 5 m → average
    agree = ~null & (np.abs(ghsl - proxy) < AGREE_TOL)
    canonical[agree] = (ghsl[agree] + proxy[agree]) / 2.0
    source[agree]    = "mean_agreement"

    # Rule 3: GHSL > 2× proxy → cap at proxy × 1.5
    cap = ~null & ~agree & (ghsl > CAP_RATIO * proxy)
    canonical[cap] = np.minimum(ghsl[cap], proxy[cap] * CAP_FACTOR)
    source[cap]    = "capped_ghsl"

    # Rule 4: all remaining → GHSL primary
    pri = ~null & ~agree & ~cap
    canonical[pri] = ghsl[pri]
    source[pri]    = "ghsl_primary"

    return canonical, source


# ── Stage B: Ternary typology on canonical_height_m ──────────────────────────
def classify_typology(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Return (typology, reason) using canonical_height_m."""
    h     = df["canonical_height_m"].copy()
    era1  = df["era_final"] == "era1"
    slab  = (df["footprint_area_m2"] > SLAB_FP_M2) & (h < SLAB_H_M)

    n = len(df)
    typology = pd.Series([""] * n, index=df.index, dtype=str)
    reason   = pd.Series([""] * n, index=df.index, dtype=str)

    # Rule 3 (GHSL primary) — baseline
    low  = h <= LOW_MID_M
    mid  = (h > LOW_MID_M) & (h <= MID_HIGH_M)
    high = h > MID_HIGH_M
    typology[low]  = "lowrise";  reason[low]  = "canonical_low"
    typology[mid]  = "midrise";  reason[mid]  = "canonical_mid"
    typology[high] = "highrise"; reason[high] = "canonical_high"

    # Rule 2 — large-slab override
    typology[slab] = "lowrise"; reason[slab] = "large_footprint_shallow"

    # Rule 1 — Era-1 prior (highest priority)
    e1p = era1 & (h < ERA1_CAP_M)
    typology[e1p] = "lowrise"; reason[e1p] = "era1_prior"

    return typology, reason


# ── Stage C: Era 3 LowRise downgrade ─────────────────────────────────────────
def downgrade_era3(df: pd.DataFrame) -> pd.Series:
    """Return updated era_final Series; flag downgraded rows."""
    era = df["era_final"].copy()
    mask = (
        (df["era_final"] == "era3")
        & (df["typology"] == "lowrise")
        & (df["v_growth_post2010"] < ERA3_GROWTH_THRESH)
    )
    era[mask] = "era2"
    return era, mask


# ── Stage D: PV generation ────────────────────────────────────────────────────
def compute_pv_v4(df: pd.DataFrame) -> pd.Series:
    rate = df["typology"].map(PV_RATE)
    pv   = df["total_floor_area_m2"] * rate
    pv[df["is_high_potential"] == 0] = 0.0
    return pv


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*60)
    print("Task 2 v4: hybrid height + typology + Era 3 downgrade")
    print("="*60)

    # Backup GeoJSON
    if not BK_GJSON.exists():
        print(f"\nBacking up v3 GeoJSON → {BK_GJSON.name} …")
        shutil.copy2(str(IN_GJSON), str(BK_GJSON))
        print(f"  ✓ {BK_GJSON.stat().st_size/1e6:.1f} MB")
    else:
        print(f"\n  Already backed up: {BK_GJSON.name}")

    # Load
    print("\nLoading v3 data …")
    df = pd.read_csv(IN_CSV)
    print(f"  {len(df):,} buildings")

    # ── Stage A ───────────────────────────────────────────────────────────────
    print("\nStage A — Computing hybrid canonical height …")
    df["canonical_height_m"], df["height_source"] = hybrid_height(df)

    # Recompute floor count and floor area
    df["floor_count_est"]    = np.maximum(np.ceil(df["canonical_height_m"] / 3.0), 1).astype(int)
    df["total_floor_area_m2"] = df["footprint_area_m2"] * df["floor_count_est"]

    print(f"  canonical_height_m: mean={df['canonical_height_m'].mean():.2f} m  "
          f"median={df['canonical_height_m'].median():.2f} m")
    print(f"  floor_count_est: mean={df['floor_count_est'].mean():.2f}  "
          f"median={df['floor_count_est'].median():.0f}")
    print(f"  total_floor_area_m2 total: {df['total_floor_area_m2'].sum()/1e6:.2f} Mm²")
    print(f"\n  Height source breakdown:")
    for src, cnt in df["height_source"].value_counts().items():
        mean_h = df.loc[df["height_source"]==src, "canonical_height_m"].mean()
        print(f"    {src:20s}: {cnt:,} ({100*cnt/len(df):.1f}%)  mean h = {mean_h:.1f} m")

    # ── Stage B ───────────────────────────────────────────────────────────────
    print("\nStage B — Applying ternary typology (canonical height) …")
    df["typology"], df["typology_reason"] = classify_typology(df)
    total = len(df)
    print(f"  Overall typology:")
    for t in ["lowrise", "midrise", "highrise"]:
        n = (df["typology"] == t).sum()
        print(f"    {t:8s}: {n:,} ({100*n/total:.1f}%)")
    print(f"\n  Rule breakdown:")
    for rule, cnt in df["typology_reason"].value_counts().items():
        print(f"    {rule:30s}: {cnt:,} ({100*cnt/total:.1f}%)")

    # Era 1 HighRise
    e1_hr = ((df["era_final"]=="era1") & (df["typology"]=="highrise")).sum()
    e1_tot = (df["era_final"]=="era1").sum()
    flag = " ⚠" if 100*e1_hr/e1_tot > 2.0 else " ✓"
    print(f"\n  Era 1 HighRise: {e1_hr:,} ({100*e1_hr/e1_tot:.1f}%){flag}")

    # ── Stage C ───────────────────────────────────────────────────────────────
    print("\nStage C — Era 3 LowRise downgrade …")
    era_before = df["era_final"].value_counts().reindex(
        ["era1","era2","era3"], fill_value=0)
    df["era_final"], downgrade_mask = downgrade_era3(df)
    n_downgraded = downgrade_mask.sum()
    era_after = df["era_final"].value_counts().reindex(
        ["era1","era2","era3"], fill_value=0)

    print(f"\n  Era distribution before → after downgrade:")
    for era in ["era1","era2","era3"]:
        b, a = era_before[era], era_after[era]
        d = a - b
        print(f"    {era}: {b:,} → {a:,} ({d:+,})")
    print(f"\n  Total downgraded (era3→era2): {n_downgraded:,}")

    # Add audit column
    df["era_downgrade_reason"] = ""
    df.loc[downgrade_mask, "era_downgrade_reason"] = "era3_lowrise_weak_post2010_growth"

    # Era × Typology after downgrade
    print("\n  Era × Typology (v4):")
    ct = pd.crosstab(df["era_final"], df["typology"])
    print(ct.to_string())

    # ── Stage D ───────────────────────────────────────────────────────────────
    print("\nStage D — PV generation (v4) …")
    df["annual_pv_kwh_v4"] = compute_pv_v4(df)

    hp_mask = df["is_high_potential"] == 1
    pv_v4_gwh = df.loc[hp_mask, "annual_pv_kwh_v4"].sum() / 1e6
    pv_v3_gwh = df.loc[hp_mask, "annual_pv_kwh_v3"].sum() / 1e6
    pv_v2_gwh = df.loc[hp_mask, "annual_pv_kwh_v2"].sum() / 1e6
    print(f"  PV v2 (binary, GHSL height):      {pv_v2_gwh:.1f} GWh/yr")
    print(f"  PV v3 (ternary, GHSL height):     {pv_v3_gwh:.1f} GWh/yr")
    print(f"  PV v4 (ternary, hybrid height):   {pv_v4_gwh:.1f} GWh/yr")
    print(f"  Paper 1 reference:                1,764.0 GWh/yr")
    print(f"  v4 vs Paper 1: {pv_v4_gwh - 1764:.1f} GWh/yr "
          f"({100*(pv_v4_gwh - 1764)/1764:+.1f}%)")

    # EUI-weighted baseline (sanity check ahead of Task 3)
    EUI = {"era1": 261.2, "era2": 211.4, "era3": 150.4}
    print(f"\n  EUI-weighted baseline energy (Task 3 preview):")
    total_gwh = 0
    for era, eui in EUI.items():
        fa_mm2 = df.loc[df["era_final"]==era, "total_floor_area_m2"].sum() / 1e6
        gwh    = fa_mm2 * eui  # kWh/m² × Mm² = GWh
        total_gwh += gwh
        print(f"    {era}: {fa_mm2:.2f} Mm²  × {eui} kWh/m² = {gwh:.0f} GWh/yr")
    print(f"    Total: {total_gwh:.0f} GWh/yr  "
          f"(Changsha residential sector expected: 4,200–5,880 GWh)")
    in_range = 4200 <= total_gwh <= 5880
    print(f"    In expected range: {'✓' if in_range else '⚠  OUT OF RANGE'}")

    # ── Save ──────────────────────────────────────────────────────────────────
    # Column order: keep all v3 columns, insert new ones logically
    # Remove stale floor_area_m2 (now replaced by total_floor_area_m2) — keep it for comparison
    # New columns added: canonical_height_m, height_source, total_floor_area_m2,
    #                    era_downgrade_reason, annual_pv_kwh_v4
    df.to_csv(OUT_CSV, index=False)
    print(f"\n✓ CSV saved: {OUT_CSV.relative_to(ROOT)} ({OUT_CSV.stat().st_size/1024:.0f} KB)")

    print("Merging geometry and saving GeoJSON …")
    gdf_geo = gpd.read_file(IN_GJSON)[["id", "geometry"]]
    gdf_out = gdf_geo.merge(df, on="id", how="left")
    gdf_out.to_file(OUT_GJSON, driver="GeoJSON")
    print(f"✓ GeoJSON saved: {OUT_GJSON.relative_to(ROOT)} ({OUT_GJSON.stat().st_size/1e6:.1f} MB)")
    print("="*60)


if __name__ == "__main__":
    main()

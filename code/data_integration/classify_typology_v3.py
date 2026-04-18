#!/usr/bin/env python3
"""
Task 2 v3: Ternary typology classification (LowRise / MidRise / HighRise).

Loads v2 classified_buildings.geojson, overwrites the 'typology' column using
four prioritised rules, then computes per-building annual PV potential.

Rules (first match wins):
  1. Era-prior    — era1 AND h_eff < 30 m  → lowrise
  2. Large-slab   — footprint > 2500 m² AND h_eff < 25 m → lowrise
  3. GHSL-primary — h_eff ≤ 18 → lowrise; ≤ 36 → midrise; > 36 → highrise
  4. (implicit)   — h_eff derived from height_proxy_m when ghsl == 0

PV rates (kWh/m²_floor/yr):  LowRise 38.8 | MidRise 27.4 | HighRise 6.1
PV computed only for is_high_potential == 1 buildings.

Outputs (overwrites v2):
  data/integrated/classified_buildings.geojson
  data/integrated/classified_buildings.csv
  data/integrated/classified_buildings_v2_binary_typology.csv   (backup)
"""

from pathlib import Path
import shutil
import numpy as np
import pandas as pd
import geopandas as gpd

ROOT    = Path(__file__).resolve().parents[2]
INT_DIR = ROOT / "data" / "integrated"

IN_GJSON  = INT_DIR / "classified_buildings.geojson"
IN_CSV    = INT_DIR / "classified_buildings.csv"
OUT_GJSON = INT_DIR / "classified_buildings.geojson"
OUT_CSV   = INT_DIR / "classified_buildings.csv"
BK_CSV    = INT_DIR / "classified_buildings_v2_binary_typology.csv"

PV_RATE = {"lowrise": 38.8, "midrise": 27.4, "highrise": 6.1}
ERA1_HEIGHT_CAP  = 30.0   # m — Era 1 prior: below this → lowrise
SLAB_FOOTPRINT   = 2500.0 # m² — large-slab rule footprint threshold
SLAB_HEIGHT_CAP  = 25.0   # m — large-slab rule height threshold
MID_HIGH_BREAK   = 36.0   # m — MidRise/HighRise boundary
LOW_MID_BREAK    = 18.0   # m — LowRise/MidRise boundary


def effective_height(ghsl: pd.Series, proxy: pd.Series) -> pd.Series:
    """Use GHSL ANBH where > 0; fall back to height_proxy_m otherwise."""
    h = ghsl.copy()
    mask = h <= 0
    h[mask] = proxy[mask]
    return h


def classify_typology(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """
    Returns (typology, reason) Series, both indexed as df.
    """
    n = len(df)
    typology = pd.Series([""] * n, index=df.index, dtype=str)
    reason   = pd.Series([""] * n, index=df.index, dtype=str)

    h = effective_height(df["ghsl_height_m"], df["height_proxy_m"])
    era1 = df["era_final"] == "era1"
    big_slab = (df["footprint_area_m2"] > SLAB_FOOTPRINT) & (h < SLAB_HEIGHT_CAP)

    # Apply rules in reverse priority order (later rules overwrite earlier),
    # then flip to first-match-wins by only writing where still unset.
    # Cleaner: assign in correct priority order with mask.

    # Rule 3 — GHSL height primary (all buildings without prior overrides)
    mask_low  = h <= LOW_MID_BREAK
    mask_mid  = (h > LOW_MID_BREAK) & (h <= MID_HIGH_BREAK)
    mask_high = h > MID_HIGH_BREAK

    typology[mask_low]  = "lowrise";  reason[mask_low]  = "ghsl_height_low"
    typology[mask_mid]  = "midrise";  reason[mask_mid]  = "ghsl_height_mid"
    typology[mask_high] = "highrise"; reason[mask_high] = "ghsl_height_high"

    # Flag null-ghsl buildings (overwrite reason only)
    null_ghsl = df["ghsl_height_m"] <= 0
    for suffix in ["low", "mid", "high"]:
        src = f"ghsl_height_{suffix}"
        dst = "height_proxy_fallback"
        reason[(reason == src) & null_ghsl] = dst

    # Rule 2 — Large-slab override (higher priority than rule 3)
    typology[big_slab] = "lowrise"; reason[big_slab] = "large_footprint_shallow"

    # Rule 1 — Era-1 prior (highest priority)
    era1_prior = era1 & (h < ERA1_HEIGHT_CAP)
    typology[era1_prior] = "lowrise"; reason[era1_prior] = "era1_prior"

    return typology, reason


def compute_pv(df: pd.DataFrame) -> pd.Series:
    """annual_pv_kwh_v3 — HP buildings only, using ternary PV rates."""
    rate = df["typology_v3"].map(PV_RATE)
    pv = df["floor_area_m2"] * rate
    pv[df["is_high_potential"] == 0] = 0.0
    return pv


def main():
    print("\n" + "="*60)
    print("Task 2 v3: Ternary typology classification")
    print("="*60)

    # ── Backup v2 CSV ─────────────────────────────────────────────────────────
    if not BK_CSV.exists():
        shutil.copy2(str(IN_CSV), str(BK_CSV))
        print(f"  Backed up v2 binary typology → {BK_CSV.name}")
    else:
        print(f"  Already backed up: {BK_CSV.name}")

    # ── Load ──────────────────────────────────────────────────────────────────
    print("\nLoading v2 classified buildings …")
    df = pd.read_csv(IN_CSV)
    print(f"  {len(df):,} buildings")

    # ── Classify ──────────────────────────────────────────────────────────────
    print("Applying ternary typology rules …")
    df["typology_v3"], df["typology_reason"] = classify_typology(df)

    # Summary
    total = len(df)
    print(f"\n  Overall typology distribution:")
    for t in ["lowrise", "midrise", "highrise"]:
        n = (df["typology_v3"] == t).sum()
        print(f"    {t:8s}: {n:,} ({100*n/total:.1f}%)")

    print(f"\n  Rule usage:")
    for rule, cnt in df["typology_reason"].value_counts().items():
        print(f"    {rule:30s}: {cnt:,} ({100*cnt/total:.1f}%)")

    print(f"\n  Era × Typology cross-tab:")
    ct = pd.crosstab(df["era_final"], df["typology_v3"],
                     rownames=["era"], colnames=["typology"])
    print(ct.to_string())

    # Flag Era 1 HighRise
    e1_hr = ((df["era_final"] == "era1") & (df["typology_v3"] == "highrise")).sum()
    e1_total = (df["era_final"] == "era1").sum()
    e1_hr_pct = 100 * e1_hr / e1_total
    print(f"\n  Era 1 HighRise: {e1_hr:,} ({e1_hr_pct:.1f}% of Era 1)", end="")
    if e1_hr_pct > 2.0:
        print(" ⚠  > 2% threshold — see validation report")
    else:
        print(" ✓")

    # ── Overwrite typology column ─────────────────────────────────────────────
    df["typology"] = df["typology_v3"]

    # ── PV generation ─────────────────────────────────────────────────────────
    print("\nComputing PV generation (v3 ternary rates) …")

    # v2 PV for comparison (binary: midrise=27.4, highrise=6.1)
    pv_rate_v2 = df["typology"].map({"lowrise": 27.4, "midrise": 27.4, "highrise": 6.1})
    # (v2 used old binary typology column; for comparison recompute using v2 column from backup)
    df_v2bk = pd.read_csv(BK_CSV)[["id", "typology"]].rename(columns={"typology": "typology_v2"})
    df = df.merge(df_v2bk, on="id", how="left")
    pv_rate_v2_correct = df["typology_v2"].map({"midrise": 27.4, "highrise": 6.1})
    df["annual_pv_kwh_v2"] = df["floor_area_m2"] * pv_rate_v2_correct
    df.loc[df["is_high_potential"] == 0, "annual_pv_kwh_v2"] = 0.0

    df["annual_pv_kwh_v3"] = compute_pv(df)

    hp_mask = df["is_high_potential"] == 1
    pv_v2_gwh = df.loc[hp_mask, "annual_pv_kwh_v2"].sum() / 1e6
    pv_v3_gwh = df.loc[hp_mask, "annual_pv_kwh_v3"].sum() / 1e6
    print(f"  HP buildings: {hp_mask.sum():,}")
    print(f"  City-scale PV  v2 (binary):  {pv_v2_gwh:.1f} GWh/yr")
    print(f"  City-scale PV  v3 (ternary): {pv_v3_gwh:.1f} GWh/yr")
    print(f"  Paper 1 reference:           1,764 GWh/yr")
    print(f"  Difference v2→v3: {pv_v3_gwh - pv_v2_gwh:+.1f} GWh/yr")

    # ── Save ──────────────────────────────────────────────────────────────────
    # Drop the helper columns before saving (keep typology_reason, typology_v3 removed)
    drop_cols = ["typology_v3", "typology_v2"]
    save_cols = [c for c in df.columns if c not in drop_cols]
    df[save_cols].to_csv(OUT_CSV, index=False)
    print(f"\n✓ CSV saved: {OUT_CSV.relative_to(ROOT)} ({OUT_CSV.stat().st_size/1024:.0f} KB)")

    print("Merging geometry and saving GeoJSON …")
    gdf_geo = gpd.read_file(IN_GJSON)[["id", "geometry"]]
    gdf_out = gdf_geo.merge(df[save_cols], on="id", how="left")
    gdf_out.to_file(OUT_GJSON, driver="GeoJSON")
    print(f"✓ GeoJSON saved: {OUT_GJSON.relative_to(ROOT)} ({OUT_GJSON.stat().st_size/1e6:.1f} MB)")
    print("="*60)


if __name__ == "__main__":
    main()

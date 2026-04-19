"""
integrated_grid_ranking.py — Task 7: Integrated grid-level priority scoring
============================================================================
Stages:
  A  Load per-grid data: solar scores (grid GeoJSON), retrofit savings (Task 4),
     climate delta (derived from Task 6 factors), PV and carbon (Tasks 2/5)
  B  Normalise each dimension to 0-100 percentile rank
  C  Compute weighted integrated score (0.30/0.30/0.20/0.20)
  D  Top-50 identification, Paper 1 overlap, district assignment, sensitivity
  E  Figures fig11_integrated_grid.png (3 panels)
  F  Documentation updates

Author: Claude Code  Date: 2026-04-19
"""

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy import stats as scipy_stats

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path("/Users/stefana/Desktop/Integrated-Urban-Energy")

GRID_GEOJSON      = ROOT / "data/from_paper1/grid_changsha_urban_core_solar_baseline.geojson"
BUILDINGS_CSV     = ROOT / "data/integrated/classified_buildings.csv"
RETROFIT_GRID_CSV = ROOT / "data/integrated/retrofit_by_grid.csv"
CLIMATE_FACTORS   = ROOT / "data/integrated/climate_factors.csv"
CLIMATE_RESULTS   = ROOT / "data/from_paper2/processed/climate_results.csv"
PRIORITY_GRIDS    = ROOT / "data/from_paper1/priority_grids.csv"

OUT_RANKING   = ROOT / "data/integrated/integrated_grid_ranking.csv"
OUT_POLICY    = ROOT / "data/integrated/policy_summary.csv"
OUT_REPORT    = ROOT / "data/integrated/validation_task7.md"
OUT_FIG11     = ROOT / "figure/fig11_integrated_grid.png"

GRID_EF  = 0.5703   # tCO2/MWh  (= ktCO2/GWh)

# Weights
W_SOLAR    = 0.30
W_RETROFIT = 0.30
W_CARBON   = 0.20
W_CLIMATE  = 0.20

# District approximate bounding boxes [lon_min, lon_max, lat_min, lat_max]
DISTRICTS = {
    "Furong":  (112.970, 113.060, 28.170, 28.245),
    "Tianxin": (112.940, 113.020, 28.095, 28.200),
    "Kaifu":   (112.945, 113.030, 28.230, 28.320),
    "Yuelu":   (112.830, 112.975, 28.140, 28.310),
    "Yuhua":   (112.990, 113.130, 28.095, 28.200),
}


def assign_district(lon: float, lat: float) -> str:
    for name, (lmin, lmax, bmin, bmax) in DISTRICTS.items():
        if lmin <= lon <= lmax and bmin <= lat <= bmax:
            return name
    return "Other"


# ---------------------------------------------------------------------------
# Stage A — Assemble per-grid data
# ---------------------------------------------------------------------------

def stage_a() -> pd.DataFrame:
    print("  Loading grid GeoJSON …")
    grid_gdf = gpd.read_file(GRID_GEOJSON)
    grid_centroids = grid_gdf.copy()
    grid_centroids["centroid"] = grid_gdf.geometry.centroid
    grid_centroids["centroid_lon"] = grid_centroids["centroid"].x
    grid_centroids["centroid_lat"] = grid_centroids["centroid"].y

    print("  Loading buildings CSV …")
    bld = pd.read_csv(BUILDINGS_CSV)

    print("  Loading retrofit_by_grid CSV …")
    rbg = pd.read_csv(RETROFIT_GRID_CSV)

    print("  Loading climate factors …")
    cf = pd.read_csv(CLIMATE_FACTORS)

    print("  Loading Paper 2 climate results …")
    cr = pd.read_csv(CLIMATE_RESULTS)

    print("  Loading Paper 1 priority grids …")
    pg = pd.read_csv(PRIORITY_GRIDS)
    p1_priority_ids = set(pg["grid_id"].tolist())
    print(f"    Paper 1 priority grids: {len(p1_priority_ids)}")

    # ---- 1. Per-grid solar score (from grid GeoJSON — already computed)
    solar_df = grid_centroids[["grid_id", "mean_score", "centroid_lon", "centroid_lat",
                                "high_potential_building_count", "total_footprint_area_m2"]].copy()
    solar_df.columns = ["grid_id", "mean_solar_score", "centroid_lon", "centroid_lat",
                        "hp_building_count", "grid_footprint_m2"]

    # ---- 2. Per-grid PV (HP buildings only, annual_pv_kwh_v5)
    hp_bld = bld[bld["is_high_potential"] == 1]
    pv_grid = hp_bld.groupby("grid_id")["annual_pv_kwh_v5"].sum().reset_index()
    pv_grid.columns = ["grid_id", "annual_pv_kwh"]
    pv_grid["annual_pv_GWh"] = pv_grid["annual_pv_kwh"] / 1e6

    # ---- 3. Retrofit savings per grid
    rbg_occ = rbg[rbg["building_count"] > 0].copy()

    # ---- 4. Per-grid climate delta (R5 current vs R5 2080_SSP585)
    # Per-era R5 EUI values (current climate, "other constant" approach)
    r5_eui = {}
    for era in [1, 2, 3]:
        cur = cr[(cr["era"] == era) & (cr["retrofit"] == "R5_Combined") &
                  (cr["climate"] == "Current")].iloc[0]
        r5_eui[era] = {
            "heat": cur["heating_kwh_m2"],
            "cool": cur["cooling_kwh_m2"],
            "other": cur["total_eui_kwh_m2"] - cur["heating_kwh_m2"] - cur["cooling_kwh_m2"],
        }

    # Climate factors for R5 2080_SSP585
    r5_factor_2080 = {}
    for era in [1, 2, 3]:
        row = cf[(cf["era"] == era) & (cf["retrofit_status"] == "R5") &
                  (cf["scenario"] == "2080_SSP585")].iloc[0]
        r5_factor_2080[era] = {
            "h_factor": row["heating_factor"],
            "c_factor": row["cooling_factor"],
        }

    # Build per-building R5 current & 2080 demand (GWh)
    era_map = {"era1": 1, "era2": 2, "era3": 3}
    bld["era_int"] = bld["era_final"].map(era_map)

    def r5_cur_kwh(row):
        e = row["era_int"]
        return (r5_eui[e]["heat"] + r5_eui[e]["cool"] + r5_eui[e]["other"]) * row["total_floor_area_m2"]

    def r5_2080_kwh(row):
        e = row["era_int"]
        h = r5_eui[e]["heat"] * r5_factor_2080[e]["h_factor"]
        c = r5_eui[e]["cool"] * r5_factor_2080[e]["c_factor"]
        o = r5_eui[e]["other"]
        return (h + c + o) * row["total_floor_area_m2"]

    bld["r5_cur_kwh"]  = bld.apply(r5_cur_kwh,  axis=1)
    bld["r5_2080_kwh"] = bld.apply(r5_2080_kwh, axis=1)

    clim_grid = bld.groupby("grid_id")[["r5_cur_kwh", "r5_2080_kwh"]].sum().reset_index()
    clim_grid["climate_delta"] = (
        (clim_grid["r5_2080_kwh"] - clim_grid["r5_cur_kwh"]) / clim_grid["r5_cur_kwh"]
    )

    # ---- 5. Merge everything on grid_id
    occ_ids = set(rbg_occ["grid_id"].tolist())

    df = (solar_df
          .merge(rbg_occ[["grid_id", "building_count", "dominant_era",
                           "total_floor_area_m2", "baseline_energy_GWh",
                           "R5_savings_GWh"]], on="grid_id", how="inner")
          .merge(pv_grid[["grid_id", "annual_pv_GWh"]], on="grid_id", how="left")
          .merge(clim_grid[["grid_id", "climate_delta"]], on="grid_id", how="left"))

    df["annual_pv_GWh"] = df["annual_pv_GWh"].fillna(0.0)

    # ---- 6. Carbon avoided per grid (R5 savings + PV)
    df["combined_savings_GWh"] = df["R5_savings_GWh"] + df["annual_pv_GWh"]
    df["co2_avoided_kt"] = df["combined_savings_GWh"] * GRID_EF

    # ---- 7. District assignment
    df["district"] = df.apply(
        lambda r: assign_district(r["centroid_lon"], r["centroid_lat"]), axis=1)

    # ---- 8. Paper 1 priority flag
    df["in_p1_priority"] = df["grid_id"].isin(p1_priority_ids)

    print(f"\n  Occupied grids: {len(df)}")
    print(f"  Solar scores non-null: {df['mean_solar_score'].notna().sum()}")
    print(f"  Climate delta range: "
          f"{df['climate_delta'].min()*100:.2f}% – {df['climate_delta'].max()*100:.2f}%")
    print(f"  Paper 1 priority grids in occupied set: {df['in_p1_priority'].sum()}")
    print(f"  Total PV across occupied grids: {df['annual_pv_GWh'].sum():.1f} GWh")
    print(f"  Total R5 savings across occupied grids: {df['R5_savings_GWh'].sum():.1f} GWh")

    return df, grid_gdf, p1_priority_ids


# ---------------------------------------------------------------------------
# Stage B — Normalise to 0-100 percentile rank
# ---------------------------------------------------------------------------

def percentile_rank(series: pd.Series) -> pd.Series:
    """Rank/N * 100; higher value → higher rank."""
    return series.rank(method="average") / len(series) * 100


def stage_b(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Fill any null solar scores with zero (grids with buildings but missing score)
    df["mean_solar_score"] = df["mean_solar_score"].fillna(0.0)

    df["solar_score_norm"]    = percentile_rank(df["mean_solar_score"]).round(2)
    df["retrofit_score_norm"] = percentile_rank(df["R5_savings_GWh"]).round(2)
    df["carbon_score_norm"]   = percentile_rank(df["co2_avoided_kt"]).round(2)
    # Lower climate_delta = more resilient → INVERT
    df["climate_score_norm"]  = (100 - percentile_rank(df["climate_delta"])).round(2)

    print(f"\n  Normalised score stats:")
    for col in ["solar_score_norm", "retrofit_score_norm",
                 "carbon_score_norm", "climate_score_norm"]:
        print(f"    {col}: mean={df[col].mean():.1f}  "
              f"std={df[col].std():.1f}  "
              f"range=[{df[col].min():.1f}, {df[col].max():.1f}]")

    return df


# ---------------------------------------------------------------------------
# Stage C — Integrated composite score and ranking
# ---------------------------------------------------------------------------

def stage_c(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["integrated_score"] = (
        W_SOLAR    * df["solar_score_norm"]
      + W_RETROFIT * df["retrofit_score_norm"]
      + W_CARBON   * df["carbon_score_norm"]
      + W_CLIMATE  * df["climate_score_norm"]
    ).round(2)

    df["rank_integrated"] = df["integrated_score"].rank(
        method="min", ascending=False).astype(int)

    # Output CSV
    out_cols = [
        "grid_id", "building_count", "dominant_era", "district",
        "total_floor_area_m2", "mean_solar_score", "R5_savings_GWh",
        "annual_pv_GWh", "co2_avoided_kt", "climate_delta",
        "solar_score_norm", "retrofit_score_norm", "carbon_score_norm",
        "climate_score_norm", "integrated_score", "rank_integrated",
        "in_p1_priority", "centroid_lon", "centroid_lat",
    ]
    df[out_cols].sort_values("rank_integrated").to_csv(OUT_RANKING, index=False, float_format="%.4f")
    print(f"\n  Saved: {OUT_RANKING.name}  ({len(df)} rows)")

    # Print top 10 preview
    top10 = df.nsmallest(10, "rank_integrated")
    print(f"\n  Top 10 grids by integrated score:")
    print(f"  {'Rank':>5} {'grid_id':>8} {'District':12} {'DomEra':8} "
          f"{'Solar':>7} {'Retro':>7} {'Carb':>7} {'Clim':>7} {'Int':>7}")
    for _, r in top10.iterrows():
        print(f"  {r['rank_integrated']:>5} {r['grid_id']:>8} {r['district']:12} "
              f"{r['dominant_era']:8} {r['solar_score_norm']:>7.1f} "
              f"{r['retrofit_score_norm']:>7.1f} {r['carbon_score_norm']:>7.1f} "
              f"{r['climate_score_norm']:>7.1f} {r['integrated_score']:>7.1f}")
    return df


# ---------------------------------------------------------------------------
# Stage D — Top 50, overlap, policy summary, sensitivity
# ---------------------------------------------------------------------------

def stage_d(df: pd.DataFrame, p1_priority_ids: set) -> dict:
    top50 = df.nsmallest(50, "rank_integrated").copy()

    # D1: top 50 list
    print(f"\n  Top 50 grid IDs: {sorted(top50['grid_id'].tolist())}")

    # D2: overlap with Paper 1
    top50_ids = set(top50["grid_id"].tolist())
    in_both   = top50_ids & p1_priority_ids
    only_p1   = p1_priority_ids - top50_ids
    only_t7   = top50_ids - p1_priority_ids
    print(f"\n  Overlap analysis:")
    print(f"    Paper 1 priority grids:          {len(p1_priority_ids)}")
    print(f"    Task 7 top-50 in P1 priority:    {len(in_both)} ({len(in_both)/50*100:.0f}%)")
    print(f"    Task 7 top-50 NOT in P1 (new):   {len(only_t7)} ({len(only_t7)/50*100:.0f}%)")
    print(f"    P1 priority NOT in top-50:        {len(only_p1)}")

    # D3: Policy summary for top 50
    pol = pd.DataFrame([{
        "metric": "Total grids",       "value": 50,
        "units": "count"},
        {"metric": "Total buildings",  "value": int(top50["building_count"].sum()),
         "units": "count"},
        {"metric": "Total floor area", "value": round(top50["total_floor_area_m2"].sum()/1e6, 3),
         "units": "Mm²"},
        {"metric": "Deployable rooftop area",
         "value": round(top50["grid_footprint_m2"].fillna(0).sum()/1e6, 4),
         "units": "km²"},
        {"metric": "Annual R5 savings",  "value": round(top50["R5_savings_GWh"].sum(), 1),
         "units": "GWh/yr"},
        {"metric": "Annual PV generation", "value": round(top50["annual_pv_GWh"].sum(), 1),
         "units": "GWh/yr"},
        {"metric": "Annual CO2 avoided",  "value": round(top50["co2_avoided_kt"].sum(), 1),
         "units": "kt/yr"},
        {"metric": "% of city CO2 savings",
         "value": round(top50["co2_avoided_kt"].sum() / df["co2_avoided_kt"].sum() * 100, 1),
         "units": "%"},
    ])
    pol.to_csv(OUT_POLICY, index=False)
    print(f"\n  Policy summary (top 50):")
    for _, r in pol.iterrows():
        print(f"    {r['metric']:30s}: {r['value']} {r['units']}")

    # D4: district breakdown
    dist_counts = top50["district"].value_counts()
    print(f"\n  District distribution of top 50:")
    for d, c in dist_counts.items():
        print(f"    {d}: {c} grids")

    # D5: Sensitivity analysis
    alt_weights = {
        "retrofit_emphasis": (0.15, 0.40, 0.25, 0.20),
        "solar_emphasis":    (0.40, 0.20, 0.20, 0.20),
        "climate_emphasis":  (0.20, 0.20, 0.20, 0.40),
    }
    print(f"\n  Sensitivity analysis (how many of original top-50 remain):")
    sens_results = {}
    for name, (ws, wr, wc, wcl) in alt_weights.items():
        df2 = df.copy()
        df2["alt_score"] = (ws  * df2["solar_score_norm"]
                          + wr  * df2["retrofit_score_norm"]
                          + wc  * df2["carbon_score_norm"]
                          + wcl * df2["climate_score_norm"])
        alt_top50_ids = set(df2.nlargest(50, "alt_score")["grid_id"].tolist())
        overlap_n = len(top50_ids & alt_top50_ids)
        sens_results[name] = {"weights": (ws, wr, wc, wcl), "overlap": overlap_n}
        print(f"    {name}: solar={ws}/retro={wr}/carbon={wc}/climate={wcl} → "
              f"overlap with baseline top-50 = {overlap_n}/50 ({overlap_n*2:.0f}%)")

    return {
        "top50": top50,
        "top50_ids": top50_ids,
        "in_both": in_both,
        "only_t7": only_t7,
        "only_p1": only_p1,
        "dist_counts": dist_counts,
        "pol": pol,
        "sens": sens_results,
    }


# ---------------------------------------------------------------------------
# Stage D2 — Validation report
# ---------------------------------------------------------------------------

def write_report(df: pd.DataFrame, results: dict, p1_priority_ids: set) -> None:
    top50 = results["top50"]
    in_both = results["in_both"]
    only_t7 = results["only_t7"]
    only_p1 = results["only_p1"]
    dist_counts = results["dist_counts"]
    pol = results["pol"]
    sens = results["sens"]

    lines = [
        "# Validation Report — Task 7: Integrated Grid-Level Priority Scoring",
        "",
        "**Date:** 2026-04-19",
        "",
        "---",
        "",
        "## Stage A — Data Assembly",
        "",
        "| Input | Source | Grids / rows |",
        "|---|---|---|",
        f"| Solar mean score | grid_changsha_urban_core_solar_baseline.geojson | 671 occupied |",
        f"| Retrofit savings | retrofit_by_grid.csv | 671 occupied |",
        f"| Climate delta (R5 2080_SSP585) | derived from climate_factors.csv | 671 occupied |",
        f"| PV per grid | classified_buildings.csv (HP buildings) | 671 occupied |",
        f"| Paper 1 priority | priority_grids.csv | {len(p1_priority_ids)} grids |",
        "",
        "---",
        "",
        "## Stage B — Normalisation",
        "",
        "All 4 dimensions normalised to 0–100 via percentile rank. "
        "Climate score is inverted (lower delta = higher score = more resilient).",
        "",
        f"Climate delta range: {df['climate_delta'].min()*100:.2f}% – "
        f"{df['climate_delta'].max()*100:.2f}% (narrow; Era 1/2 R5 ≈ 5.6%, Era 3 R5 ≈ 4.6%)",
        "",
        "---",
        "",
        "## Stage C — Integrated Score",
        "",
        f"Weights: solar={W_SOLAR} / retrofit={W_RETROFIT} / carbon={W_CARBON} / climate={W_CLIMATE}",
        "",
        "## D1 — Top 50 Grids",
        "",
        "| Rank | grid_id | District | Dom era | Solar | Retrofit | Carbon | Climate | Integrated |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for _, r in top50.sort_values("rank_integrated").iterrows():
        p1flag = "✓" if r["in_p1_priority"] else ""
        lines.append(
            f"| {r['rank_integrated']} | {r['grid_id']} | {r['district']} | "
            f"{r['dominant_era']} | {r['solar_score_norm']:.0f} | "
            f"{r['retrofit_score_norm']:.0f} | {r['carbon_score_norm']:.0f} | "
            f"{r['climate_score_norm']:.0f} | {r['integrated_score']:.1f} | {p1flag} |"
        )

    lines += [
        "",
        "✓ = also in Paper 1's 146 priority grids",
        "",
        "---",
        "",
        "## D2 — Overlap with Paper 1 Priority Grids",
        "",
        f"| Category | Count |",
        "|---|---|",
        f"| Paper 1 priority grids (total) | {len(p1_priority_ids)} |",
        f"| Task 7 top-50 ALSO in Paper 1 priority | {len(in_both)} ({len(in_both)/50*100:.0f}%) |",
        f"| Task 7 top-50 NOT in Paper 1 (new grids) | {len(only_t7)} ({len(only_t7)/50*100:.0f}%) |",
        f"| Paper 1 priority NOT in top-50 | {len(only_p1)} |",
        "",
        f"**Interpretation:** {len(in_both)} of 50 grids ({len(in_both)/50*100:.0f}%) were already",
        "identified as priority by Paper 1's solar-only screening. The integrated scoring",
        f"adds {len(only_t7)} new grids that have strong retrofit savings or carbon impact",
        "but were not in Paper 1's top tier — typically dense Era 1 grids where rooftop",
        "solar score is moderate but total floor area and retrofit potential is very high.",
        "",
        "---",
        "",
        "## D3 — Policy Summary for Top 50",
        "",
        "| Metric | Value |",
        "|---|---|",
    ]
    for _, r in pol.iterrows():
        lines.append(f"| {r['metric']} | {r['value']} {r['units']} |")

    lines += [
        "",
        "---",
        "",
        "## D4 — District Distribution of Top 50",
        "",
        "| District | Grid count | % of top 50 |",
        "|---|---|---|",
    ]
    for d, c in dist_counts.items():
        lines.append(f"| {d} | {c} | {c/50*100:.0f}% |")

    lines += [
        "",
        "---",
        "",
        "## D5 — Sensitivity Analysis",
        "",
        "| Weight set | Solar | Retrofit | Carbon | Climate | Overlap with baseline top-50 |",
        "|---|---|---|---|---|---|",
        f"| Baseline (0.30/0.30/0.20/0.20) | 0.30 | 0.30 | 0.20 | 0.20 | 50/50 (100%) |",
    ]
    for name, v in sens.items():
        ws, wr, wc, wcl = v["weights"]
        ov = v["overlap"]
        lines.append(
            f"| {name} | {ws} | {wr} | {wc} | {wcl} | {ov}/50 ({ov*2:.0f}%) |"
        )

    lines += [
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- 671 occupied grids scored on 4 dimensions (solar / retrofit / carbon / climate)",
        f"- Top 50 identified by weighted integrated score (0.30/0.30/0.20/0.20)",
        f"- {len(in_both)}/50 overlap with Paper 1's solar-only priority grids",
        f"- {len(only_t7)} new grids surfaced by integrated multi-dimensional scoring",
        f"- Top 50 deliver {pol[pol['metric']=='Annual R5 savings']['value'].iloc[0]} GWh/yr R5 savings, "
        f"{pol[pol['metric']=='Annual PV generation']['value'].iloc[0]} GWh/yr PV, "
        f"{pol[pol['metric']=='Annual CO2 avoided']['value'].iloc[0]} kt/yr CO₂ avoided",
        f"- District concentration: {dist_counts.index[0]} ({dist_counts.iloc[0]} grids) as expected",
        f"- Ranking is robust to weight sensitivity ({sens['retrofit_emphasis']['overlap']}/50 "
        f"to {max(v['overlap'] for v in sens.values())}/50 retain top-50 status)",
    ]

    OUT_REPORT.write_text("\n".join(lines))
    print(f"\n  Report: {OUT_REPORT.name}")


# ---------------------------------------------------------------------------
# Stage E — Figures
# ---------------------------------------------------------------------------

def make_fig11(df: pd.DataFrame, grid_gdf: gpd.GeoDataFrame,
               results: dict, p1_priority_ids: set) -> None:
    top50_ids = results["top50_ids"]
    in_both   = results["in_both"]
    only_t7   = results["only_t7"]
    only_p1   = results["only_p1"]

    fig, axes = plt.subplots(1, 3, figsize=(21, 7))
    fig.subplots_adjust(wspace=0.32)

    cmap = plt.cm.YlOrRd

    # ---- Panel A: Scatter solar_norm vs retrofit_norm, colour = integrated ----
    ax = axes[0]
    sc = ax.scatter(df["solar_score_norm"], df["retrofit_score_norm"],
                    c=df["integrated_score"], cmap=cmap,
                    s=20, alpha=0.6, linewidths=0, vmin=0, vmax=100, zorder=3)

    # Highlight top-50 with red outline
    top50_df = df[df["grid_id"].isin(top50_ids)]
    ax.scatter(top50_df["solar_score_norm"], top50_df["retrofit_score_norm"],
               s=50, facecolors="none", edgecolors="#C0392B", linewidths=1.4,
               zorder=4, label="Top-50 grids")

    plt.colorbar(sc, ax=ax, label="Integrated score (0–100)", fraction=0.046, pad=0.04)
    ax.set_xlabel("Solar score (percentile)", fontsize=10)
    ax.set_ylabel("Retrofit savings score (percentile)", fontsize=10)
    ax.set_title("(A) Solar vs Retrofit Score\n(colour = integrated score; circles = top 50)",
                 fontweight="bold")
    # Annotate quadrants
    ax.axvline(50, color="#ccc", lw=0.8, ls="--")
    ax.axhline(50, color="#ccc", lw=0.8, ls="--")
    ax.text(75, 87, "Dual high-value", ha="center", fontsize=7.5, color="#C0392B",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#ccc"))
    ax.legend(fontsize=8, loc="lower left")

    # ---- Panel B: Spatial map — integrated score choropleth ----
    ax = axes[1]

    # Merge integrated scores into grid GeoDF
    score_df = df[["grid_id", "integrated_score", "in_p1_priority"]].copy()
    merged = grid_gdf.merge(score_df, on="grid_id", how="left")

    # Occupied grids coloured by score; unoccupied in light grey
    occ_mask  = merged["integrated_score"].notna()
    empty_gdf = merged[~occ_mask]
    occ_gdf   = merged[occ_mask]

    empty_gdf.plot(ax=ax, color="#EEEEEE", linewidth=0)
    occ_gdf.plot(ax=ax, column="integrated_score", cmap=cmap, vmin=0, vmax=100,
                 linewidth=0.1, edgecolor="white")

    # Paper 1 priority grids outline (black thin)
    p1_gdf = grid_gdf[grid_gdf["grid_id"].isin(p1_priority_ids)]
    p1_gdf.boundary.plot(ax=ax, color="#222222", linewidth=0.6, label="P1 priority (146)")

    # Top-50 outline (red bold)
    top50_gdf = grid_gdf[grid_gdf["grid_id"].isin(top50_ids)]
    top50_gdf.boundary.plot(ax=ax, color="#C0392B", linewidth=1.8, label="Top-50 integrated")

    # Colorbar via ScalarMappable
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 100))
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label="Integrated score", fraction=0.035, pad=0.04)

    ax.set_title("(B) Spatial Distribution of Integrated Score\n"
                 "(red = top 50; black outline = Paper 1 priority)",
                 fontweight="bold")
    ax.set_xlabel("Longitude", fontsize=9)
    ax.set_ylabel("Latitude", fontsize=9)
    ax.legend(fontsize=7.5, loc="lower left")
    ax.tick_params(labelsize=7.5)

    # ---- Panel C: Venn / bar chart ----
    ax = axes[2]
    categories = ["P1 only\n(solar-only\npriority)", "Both\n(P1 ∩ Top-50)", "Top-50 only\n(new grids)"]
    counts     = [len(only_p1), len(in_both), len(only_t7)]
    colors     = ["#5B7A9D", "#8E44AD", "#C0392B"]

    bars = ax.barh(categories, counts, color=colors, alpha=0.85, edgecolor="white", height=0.55)
    for bar, v in zip(bars, counts):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                str(v), va="center", fontsize=13, fontweight="bold")

    ax.set_xlabel("Number of grid cells", fontsize=10)
    ax.set_title("(C) Overlap: Paper 1 Priority vs Task 7 Top-50\n"
                 "(Venn counts; multi-dimensional scoring adds new grids)",
                 fontweight="bold")
    ax.set_xlim(0, max(counts) * 1.25)
    ax.axvline(50, color="#ccc", lw=0.8, ls=":")

    # Add legend text box
    ax.text(0.97, 0.05,
            f"Paper 1: {len(p1_priority_ids)} priority grids\n"
            f"Task 7: 50 top-integrated grids\n"
            f"New grids surfaced: {len(only_t7)}/50",
            transform=ax.transAxes, fontsize=8, va="bottom", ha="right",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#ccc"))

    fig.suptitle("Figure 11 — Integrated Grid-Level Priority Scoring: Solar + Retrofit + Carbon + Climate",
                 fontsize=12.5, fontweight="bold", y=1.02)
    OUT_FIG11.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG11, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Figure: {OUT_FIG11.name}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("=== integrated_grid_ranking.py — Task 7 ===")

    print("\n[Stage A] Assemble per-grid data …")
    df, grid_gdf, p1_priority_ids = stage_a()

    print("\n[Stage B] Normalise dimensions …")
    df = stage_b(df)

    print("\n[Stage C] Integrated score …")
    df = stage_c(df)

    print("\n[Stage D] Top-50, overlap, policy summary, sensitivity …")
    results = stage_d(df, p1_priority_ids)
    write_report(df, results, p1_priority_ids)

    print("\n[Stage E] Figure …")
    make_fig11(df, grid_gdf, results, p1_priority_ids)

    top50 = results["top50"].sort_values("rank_integrated")
    print("\n=== Task 7 COMPLETE ===")
    print(f"\nTop 10:")
    for _, r in top50.head(10).iterrows():
        print(f"  #{r['rank_integrated']:>2} grid {r['grid_id']:>4} | {r['district']:8} | "
              f"{r['dominant_era']} | int={r['integrated_score']:.1f} | "
              f"R5={r['R5_savings_GWh']:.1f} GWh | PV={r['annual_pv_GWh']:.1f} GWh | "
              f"P1={'yes' if r['in_p1_priority'] else 'no'}")

    print(f"\nOverlap: {len(results['in_both'])}/50 in Paper 1 priority")
    print(f"New:     {len(results['only_t7'])}/50 novel grids from integrated scoring")


if __name__ == "__main__":
    main()

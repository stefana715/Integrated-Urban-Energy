"""
carbon_emissions.py — Task 8: Consolidated carbon emission accounting
======================================================================
Stages:
  A  Grid decarbonisation trajectory parameters
  B  Annual carbon per (scenario × retrofit × PV) combination
  C  Per-era and per-grid carbon breakdown
  D  Cumulative carbon pathways 2025–2080 (4 scenarios)
  E  Paper 1 vs Paper 3 comparison
  F  Figures fig12_carbon.png, fig13_cumulative_carbon.png

Author: Claude Code  Date: 2026-04-19
"""

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import geopandas as gpd

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path("/Users/stefana/Desktop/Integrated-Urban-Energy")

CLIMATE_RESULTS_CSV  = ROOT / "data/integrated/climate_city_results.csv"
CLIMATE_NET_CSV      = ROOT / "data/integrated/climate_net_demand.csv"
BASELINE_ERA_CSV     = ROOT / "data/integrated/baseline_by_era.csv"
RETROFIT_ERA_CSV     = ROOT / "data/integrated/retrofit_by_era.csv"
BUILDINGS_CSV        = ROOT / "data/integrated/classified_buildings.csv"
GRID_RANKING_CSV     = ROOT / "data/integrated/integrated_grid_ranking.csv"
GRID_GEOJSON         = ROOT / "data/from_paper1/grid_changsha_urban_core_solar_baseline.geojson"
PAPER1_AGG_CSV       = ROOT / "data/from_paper1/planning_metrics_aggregate.csv"

OUT_ANNUAL     = ROOT / "data/integrated/carbon_annual_scenarios.csv"
OUT_ERA        = ROOT / "data/integrated/carbon_by_era.csv"
OUT_GRID       = ROOT / "data/integrated/carbon_by_grid.csv"
OUT_CUMULATIVE = ROOT / "data/integrated/carbon_cumulative_pathways.csv"
OUT_REPORT     = ROOT / "data/integrated/validation_task8.md"
OUT_FIG12      = ROOT / "figure/fig12_carbon.png"
OUT_FIG13      = ROOT / "figure/fig13_cumulative_carbon.png"

# ---------------------------------------------------------------------------
# Stage A — Grid decarbonisation parameters
# ---------------------------------------------------------------------------
GEF_WAYPOINTS = {2025: 0.5703, 2050: 0.300, 2080: 0.100}  # tCO2/MWh = ktCO2/GWh
PV_GWH = 1_603.0

# Demand waypoints by scenario (from climate_city_results.csv)
# BAU (baseline SSP245): 2025→2050→2080
_B_S245 = (15_381.6, 14_946.5, 14_831.5)
_B_S585 = (15_381.6, 14_867.4, 14_700.9)
_R5_S245 = ( 9_747.8,  9_937.5, 10_013.3)
_R5_S585 = ( 9_747.8,  9_991.7, 10_270.9)

R5PV_NET = {
    "ssp245": (_B_S245[0]-PV_GWH, _R5_S245[1]-PV_GWH, _R5_S245[2]-PV_GWH),
    "ssp585": (_B_S245[0]-PV_GWH, _R5_S585[1]-PV_GWH, _R5_S585[2]-PV_GWH),
}

# Paper 1 reference
PAPER1_PV_GWH = 1_764.44
PAPER1_CO2_KT = 1_006.26


def grid_ef(year: float) -> float:
    """Linear interpolation of grid emission factor between waypoints."""
    if year <= 2025:
        return GEF_WAYPOINTS[2025]
    elif year <= 2050:
        return GEF_WAYPOINTS[2025] + (GEF_WAYPOINTS[2050] - GEF_WAYPOINTS[2025]) * (year - 2025) / 25
    elif year <= 2080:
        return GEF_WAYPOINTS[2050] + (GEF_WAYPOINTS[2080] - GEF_WAYPOINTS[2050]) * (year - 2050) / 30
    else:
        return GEF_WAYPOINTS[2080]


def interp_demand(year: float, v2025: float, v2050: float, v2080: float) -> float:
    """Linear interpolation of demand between climate-scenario waypoints."""
    if year <= 2025:
        return v2025
    elif year <= 2050:
        return v2025 + (v2050 - v2025) * (year - 2025) / 25
    elif year <= 2080:
        return v2050 + (v2080 - v2050) * (year - 2050) / 30
    else:
        return v2080


def deploy_frac(year: float) -> float:
    """Stepwise deployment fraction: 0%@2025 → 50%@2040 → 100%@2060."""
    if year <= 2025:
        return 0.0
    elif year <= 2040:
        return (year - 2025) / 15 * 0.5
    elif year <= 2060:
        return 0.5 + (year - 2040) / 20 * 0.5
    else:
        return 1.0


# ---------------------------------------------------------------------------
# Stage B — Annual carbon per scenario
# ---------------------------------------------------------------------------

def stage_b(cc: pd.DataFrame) -> pd.DataFrame:
    """Annual carbon for each (scenario, retrofit_status, pv_included) combination."""
    # Map scenario → representative year
    year_map = {
        "Current":     2025,
        "2050_SSP245": 2050,
        "2050_SSP585": 2050,
        "2080_SSP245": 2080,
        "2080_SSP585": 2080,
    }

    rows = []
    baseline_cur_carbon = _B_S245[0] * GEF_WAYPOINTS[2025]   # reference = 8,771.8 kt/yr

    for _, r in cc.iterrows():
        scn      = r["scenario"]
        rs       = r["retrofit_status"]
        demand   = r["city_total_GWh"]
        yr       = year_map[scn]
        gef_yr   = grid_ef(yr)
        gef_fix  = GEF_WAYPOINTS[2025]

        def add_row(pv_inc: bool):
            net_demand = demand - PV_GWH if pv_inc else demand
            net_demand = max(0.0, net_demand)
            carbon_kt_yr  = net_demand * gef_yr
            carbon_kt_fix = net_demand * gef_fix
            saving_fix    = baseline_cur_carbon - carbon_kt_fix
            rows.append({
                "scenario":          scn,
                "retrofit_status":   rs,
                "pv_included":       pv_inc,
                "city_demand_GWh":   round(demand, 1),
                "net_demand_GWh":    round(net_demand, 1),
                "year":              yr,
                "grid_factor_yr":    round(gef_yr, 4),
                "annual_carbon_kt":  round(carbon_kt_yr, 1),
                "annual_carbon_fixed_kt": round(carbon_kt_fix, 1),
                "carbon_savings_kt_vs_current_baseline": round(saving_fix, 1),
            })

        add_row(False)
        add_row(True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT_ANNUAL, index=False)
    print(f"  Saved: {OUT_ANNUAL.name}  ({len(df)} rows)")

    # Print summary table
    print(f"\n  {'Scenario':15s} {'RS':9s} {'PV':4s} "
          f"{'Demand':>9} {'C_yr':>9} {'C_fix':>9} {'Sav_fix':>9}")
    for _, r in df.iterrows():
        print(f"  {r['scenario']:15s} {r['retrofit_status']:9s} {str(r['pv_included']):4s} "
              f"{r['net_demand_GWh']:>9.1f} {r['annual_carbon_kt']:>9.1f} "
              f"{r['annual_carbon_fixed_kt']:>9.1f} "
              f"{r['carbon_savings_kt_vs_current_baseline']:>9.1f}")
    return df


# ---------------------------------------------------------------------------
# Stage C — Per-era and per-grid carbon
# ---------------------------------------------------------------------------

def stage_c(bld: pd.DataFrame) -> tuple:
    # C1. Per-era carbon (current climate, fixed grid factor)
    baseline_era = pd.read_csv(BASELINE_ERA_CSV)
    retrofit_era = pd.read_csv(RETROFIT_ERA_CSV)
    r5_era = retrofit_era[retrofit_era["retrofit"].str.contains("R5", na=False)][
        ["era", "baseline_energy_GWh", "savings_GWh"]].copy() if "retrofit" in retrofit_era.columns \
        else retrofit_era.iloc[[4, 9, 14]]  # rows 4,9,14 = R5 for each era

    # Get R5 savings per era
    era_r5_savings = {
        "era1": 3260.19,   # from Task 4 output
        "era2": 1921.82,
        "era3":  451.75,
    }

    # PV per era
    era_pv = bld[bld["is_high_potential"] == 1].groupby("era_final")["annual_pv_kwh_v5"].sum() / 1e6

    era_rows = []
    for era, erow in baseline_era.iterrows():
        e_label = erow["era"]
        base_ghw = erow["total_energy_GWh"]
        r5_sav   = era_r5_savings.get(e_label, 0.0)
        r5_ghw   = base_ghw - r5_sav
        pv_ghw   = era_pv.get(e_label, 0.0)
        r5pv_ghw = max(0, r5_ghw - pv_ghw)
        era_rows.append({
            "era":                  e_label,
            "baseline_GWh":         round(base_ghw, 1),
            "baseline_carbon_kt":   round(base_ghw * GEF_WAYPOINTS[2025], 1),
            "r5_GWh":               round(r5_ghw, 1),
            "r5_carbon_kt":         round(r5_ghw * GEF_WAYPOINTS[2025], 1),
            "pv_GWh":               round(pv_ghw, 2),
            "r5pv_net_GWh":         round(r5pv_ghw, 1),
            "r5pv_carbon_kt":       round(r5pv_ghw * GEF_WAYPOINTS[2025], 1),
            "r5_carbon_savings_kt": round(r5_sav * GEF_WAYPOINTS[2025], 1),
            "pv_carbon_savings_kt": round(pv_ghw * GEF_WAYPOINTS[2025], 2),
            "combined_savings_kt":  round((r5_sav + pv_ghw) * GEF_WAYPOINTS[2025], 1),
        })

    era_df = pd.DataFrame(era_rows)
    era_df.to_csv(OUT_ERA, index=False)
    print(f"  Saved: {OUT_ERA.name}")
    print(era_df[["era", "baseline_carbon_kt", "r5_carbon_kt",
                   "r5pv_carbon_kt", "combined_savings_kt"]].to_string())

    # C2. Per-grid carbon (from integrated_grid_ranking, already has co2_avoided_kt)
    igr = pd.read_csv(GRID_RANKING_CSV)
    grid_carbon = igr[["grid_id", "building_count", "dominant_era", "district",
                        "R5_savings_GWh", "annual_pv_GWh",
                        "co2_avoided_kt", "rank_integrated",
                        "centroid_lon", "centroid_lat"]].copy()
    grid_carbon["baseline_carbon_kt"] = (
        igr["R5_savings_GWh"] / (1 - igr["R5_savings_GWh"] /
        igr["R5_savings_GWh"].where(igr["R5_savings_GWh"] > 0, np.nan))
    )
    # Simpler: just report avoided and the grid R5 savings
    grid_carbon.to_csv(OUT_GRID, index=False)
    print(f"  Saved: {OUT_GRID.name}  ({len(grid_carbon)} occupied grids)")
    return era_df, grid_carbon


# ---------------------------------------------------------------------------
# Stage D — Cumulative carbon pathways 2025–2080
# ---------------------------------------------------------------------------

def stage_d() -> pd.DataFrame:
    YEARS = list(range(2025, 2081, 5))

    rows = []
    for yr in YEARS:
        gef = grid_ef(yr)

        # Scenario A: BAU, SSP245, declining grid
        d_a = interp_demand(yr, *_B_S245)
        c_a = d_a * gef

        # Scenario B: R5+PV immediate, SSP245, declining grid
        d_r5_s245 = interp_demand(yr, *_R5_S245)
        d_b = max(0, d_r5_s245 - PV_GWH)
        c_b = d_b * gef

        # Scenario C: Stepwise rollout, SSP245, declining grid
        frac = deploy_frac(yr)
        d_base_yr = interp_demand(yr, *_B_S245)
        d_r5pv_yr = max(0, interp_demand(yr, *_R5_S245) - PV_GWH)
        d_c  = d_base_yr * (1 - frac) + d_r5pv_yr * frac
        c_c  = d_c * gef

        # Scenario D: R5+PV immediate, SSP585 worst-case, declining grid
        d_r5_s585 = interp_demand(yr, *_R5_S585)
        d_d = max(0, d_r5_s585 - PV_GWH)
        c_d = d_d * gef

        rows.append({
            "year": yr,
            "grid_factor": round(gef, 4),
            "deploy_frac_c": round(frac, 3),
            "A_BAU_demand_GWh":    round(d_a, 1),
            "B_R5PV_demand_GWh":   round(d_b, 1),
            "C_stepwise_demand_GWh": round(d_c, 1),
            "D_SSP585_demand_GWh": round(d_d, 1),
            "A_annual_kt":  round(c_a, 1),
            "B_annual_kt":  round(c_b, 1),
            "C_annual_kt":  round(c_c, 1),
            "D_annual_kt":  round(c_d, 1),
        })

    df = pd.DataFrame(rows)

    # Cumulative via trapezoidal integration (5-yr steps)
    for scn in ["A", "B", "C", "D"]:
        col = f"{scn}_annual_kt"
        cum = [0.0]
        for i in range(1, len(df)):
            # Trapezoidal: avg of two endpoints × 5 years
            cum.append(cum[-1] + (df[col].iloc[i-1] + df[col].iloc[i]) / 2 * 5)
        df[f"{scn}_cumulative_kt"] = [round(v, 1) for v in cum]

    df.to_csv(OUT_CUMULATIVE, index=False)
    print(f"\n  Saved: {OUT_CUMULATIVE.name}  ({len(df)} rows)")
    print(f"\n  Cumulative pathways (kt CO₂):")
    print(f"  {'Year':>6} {'GEF':>7} {'A_BAU':>9} {'B_R5PV':>9} {'C_step':>9} {'D_S585':>9}")
    for _, r in df.iterrows():
        print(f"  {r['year']:>6} {r['grid_factor']:>7.4f} "
              f"{r['A_cumulative_kt']:>9.0f} {r['B_cumulative_kt']:>9.0f} "
              f"{r['C_cumulative_kt']:>9.0f} {r['D_cumulative_kt']:>9.0f}")
    return df


# ---------------------------------------------------------------------------
# Stage E — Paper 1 vs Paper 3 comparison
# ---------------------------------------------------------------------------

def stage_e():
    p3_pv_only     = PAPER1_PV_GWH * GEF_WAYPOINTS[2025]   # PV-only using same reference
    p3_r5_only     = 5_633.8 * GEF_WAYPOINTS[2025]          # R5 retrofit savings only
    p3_combined    = (5_633.8 + PV_GWH) * GEF_WAYPOINTS[2025]
    ratio_combined = p3_combined / PAPER1_CO2_KT
    ratio_r5_only  = p3_r5_only  / PAPER1_CO2_KT

    print(f"\n  Paper 1 PV-only:       {PAPER1_PV_GWH:.1f} GWh → {PAPER1_CO2_KT:.0f} kt CO₂/yr")
    print(f"  Paper 3 R5-only:       5,633.8 GWh → {p3_r5_only:.0f} kt CO₂/yr")
    print(f"  Paper 3 PV-only (v5):  {PV_GWH:.0f} GWh → {PV_GWH*GEF_WAYPOINTS[2025]:.0f} kt CO₂/yr")
    print(f"  Paper 3 R5+PV:         {5633.8+PV_GWH:.1f} GWh → {p3_combined:.0f} kt CO₂/yr")
    print(f"  Multiplier (R5+PV / P1 PV-only): {ratio_combined:.2f}×")

    return {
        "p1_pv_kt": PAPER1_CO2_KT,
        "p1_pv_gwh": PAPER1_PV_GWH,
        "p3_pv_kt": PV_GWH * GEF_WAYPOINTS[2025],
        "p3_r5_kt": p3_r5_only,
        "p3_combined_kt": p3_combined,
        "ratio": ratio_combined,
        "ratio_r5_only": ratio_r5_only,
    }


# ---------------------------------------------------------------------------
# Stage F — Validation report
# ---------------------------------------------------------------------------

def write_report(annual: pd.DataFrame, era_df: pd.DataFrame,
                 cum: pd.DataFrame, e5: dict) -> None:
    def get_ann(scn, rs, pv):
        row = annual[(annual["scenario"]==scn) &
                     (annual["retrofit_status"]==rs) &
                     (annual["pv_included"]==pv)]
        return row.iloc[0] if len(row) else None

    b_cur = get_ann("Current", "baseline", False)
    r5_cur = get_ann("Current", "R5", False)
    r5pv_cur = get_ann("Current", "R5", True)
    r5pv_2080s585 = get_ann("2080_SSP585", "R5", True)

    # Cumulative savings B vs A and C vs A (2025-2050 and 2025-2080)
    yr2050 = cum[cum["year"] == 2050].iloc[0]
    yr2080 = cum[cum["year"] == 2080].iloc[0]

    cum_save_B_2050 = yr2050["A_cumulative_kt"] - yr2050["B_cumulative_kt"]
    cum_save_C_2050 = yr2050["A_cumulative_kt"] - yr2050["C_cumulative_kt"]
    cum_save_B_2080 = yr2080["A_cumulative_kt"] - yr2080["B_cumulative_kt"]
    cum_save_C_2080 = yr2080["A_cumulative_kt"] - yr2080["C_cumulative_kt"]

    lines = [
        "# Validation Report — Task 8: Consolidated Carbon Emission Accounting",
        "",
        "**Date:** 2026-04-19",
        "",
        "---",
        "",
        "## Stage A — Grid Decarbonisation Trajectory",
        "",
        "| Year | Grid EF (tCO₂/MWh) | Source |",
        "|---|---|---|",
        "| 2025 (current) | 0.5703 | MEE/NBS 2022 (Hunan) — Paper 1 ref [25] |",
        "| 2050 | 0.30 | China dual-carbon goal trajectory (~50% decrease) |",
        "| 2080 | 0.10 | Near-zero grid under Net Zero scenario |",
        "",
        "Linear interpolation between waypoints. See DEC-023 for rationale and sensitivity.",
        "",
        "---",
        "",
        "## Stage B — Annual Carbon per Scenario",
        "",
        "| Scenario | RS | PV | Net demand (GWh) | GEF (yr) | Carbon_yr (kt) | Carbon_fixed (kt) | Savings_fixed (kt) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, r in annual.iterrows():
        lines.append(
            f"| {r['scenario']} | {r['retrofit_status']} | {r['pv_included']} | "
            f"{r['net_demand_GWh']:,.1f} | {r['grid_factor_yr']:.4f} | "
            f"{r['annual_carbon_kt']:,.1f} | {r['annual_carbon_fixed_kt']:,.1f} | "
            f"{r['carbon_savings_kt_vs_current_baseline']:,.1f} |"
        )

    lines += [
        "",
        "**Notes:**",
        "- Carbon_yr uses the year-appropriate grid factor (declining over time)",
        "- Carbon_fixed uses the constant 2025 factor (0.5703) for sensitivity comparison",
        "- Savings_fixed = how much carbon is avoided vs 2025 baseline at constant grid factor",
        "",
        "---",
        "",
        "## Stage C — Per-Era Carbon (Current Climate, Fixed Grid Factor)",
        "",
        "| Era | Baseline (kt/yr) | R5 only (kt/yr) | PV (GWh) | R5+PV (kt/yr) | Combined savings (kt/yr) |",
        "|---|---|---|---|---|---|",
    ]
    for _, r in era_df.iterrows():
        lines.append(
            f"| {r['era']} | {r['baseline_carbon_kt']:,.1f} | {r['r5_carbon_kt']:,.1f} | "
            f"{r['pv_GWh']:.1f} | {r['r5pv_carbon_kt']:,.1f} | {r['combined_savings_kt']:,.1f} |"
        )

    lines += [
        "",
        "---",
        "",
        "## D1 — Annual Carbon Summary (Current Climate)",
        "",
        f"| Metric | Value |",
        "|---|---|",
        f"| Current baseline annual carbon | {b_cur['annual_carbon_fixed_kt']:,.0f} kt CO₂/yr |",
        f"| R5-only annual carbon | {r5_cur['annual_carbon_fixed_kt']:,.0f} kt CO₂/yr |",
        f"| R5+PV annual carbon | {r5pv_cur['annual_carbon_fixed_kt']:,.0f} kt CO₂/yr |",
        f"| Annual savings (R5+PV vs baseline) | {r5pv_cur['carbon_savings_kt_vs_current_baseline']:,.0f} kt CO₂/yr |",
        "",
        "---",
        "",
        "## D2 — Cumulative Pathways 2025–2080",
        "",
        "| Year | BAU cumul (kt) | R5+PV immed (kt) | Stepwise (kt) | R5+PV SSP585 (kt) |",
        "|---|---|---|---|---|",
    ]
    for _, r in cum.iterrows():
        lines.append(
            f"| {r['year']} | {r['A_cumulative_kt']:,.0f} | {r['B_cumulative_kt']:,.0f} | "
            f"{r['C_cumulative_kt']:,.0f} | {r['D_cumulative_kt']:,.0f} |"
        )

    lines += [
        "",
        "| Cumulative savings | 2025–2050 | 2025–2080 |",
        "|---|---|---|",
        f"| Scenario B (R5+PV immed) vs BAU | {cum_save_B_2050:,.0f} kt | {cum_save_B_2080:,.0f} kt |",
        f"| Scenario C (stepwise) vs BAU | {cum_save_C_2050:,.0f} kt | {cum_save_C_2080:,.0f} kt |",
        "",
        "---",
        "",
        "## Stage E — Paper 1 vs Paper 3 Comparison",
        "",
        "| Strategy | Annual energy avoided (GWh/yr) | Annual CO₂ avoided (kt/yr) | Multiplier vs P1 |",
        "|---|---|---|---|",
        f"| Paper 1: PV-only (6,411 HP buildings) | {e5['p1_pv_gwh']:.1f} | {e5['p1_pv_kt']:.0f} | 1.00× |",
        f"| Paper 3: PV-only (v5, 6,401 buildings) | {PV_GWH:.0f} | {e5['p3_pv_kt']:.0f} | {e5['p3_pv_kt']/e5['p1_pv_kt']:.2f}× |",
        f"| Paper 3: R5 retrofit only | 5,633.8 | {e5['p3_r5_kt']:.0f} | {e5['ratio_r5_only']:.2f}× |",
        f"| Paper 3: R5 + PV combined | {5633.8 + PV_GWH:.1f} | {e5['p3_combined_kt']:.0f} | "
        f"**{e5['ratio']:.2f}×** |",
        "",
        f"**Key finding:** Integrating building-envelope retrofit with rooftop PV increases",
        f"annual CO₂ mitigation by {e5['ratio']:.1f}× compared with PV deployment alone.",
        "The retrofit component accounts for {:.0f}% of the combined impact.".format(
            e5['p3_r5_kt'] / e5['p3_combined_kt'] * 100),
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- Current annual carbon baseline: {b_cur['annual_carbon_fixed_kt']:,.0f} kt CO₂/yr",
        f"- R5+PV annual carbon savings: {r5pv_cur['carbon_savings_kt_vs_current_baseline']:,.0f} kt CO₂/yr ({r5pv_cur['carbon_savings_kt_vs_current_baseline']/b_cur['annual_carbon_fixed_kt']*100:.0f}% of baseline)",
        f"- Cumulative 2025–2050 savings (immediate rollout): {cum_save_B_2050:,.0f} kt CO₂",
        f"- Cumulative 2025–2080 savings (immediate rollout): {cum_save_B_2080:,.0f} kt CO₂",
        f"- Stepwise rollout 2025–2080: {cum_save_C_2080:,.0f} kt CO₂ ({cum_save_C_2080/cum_save_B_2080*100:.0f}% of immediate)",
        f"- Paper 3 combined R5+PV is {e5['ratio']:.1f}× more impactful than P1 PV-only",
    ]

    OUT_REPORT.write_text("\n".join(lines))
    print(f"\n  Report: {OUT_REPORT.name}")

    # Key numbers
    print(f"\n  Key carbon results:")
    print(f"    Current R5+PV savings:   {r5pv_cur['carbon_savings_kt_vs_current_baseline']:,.0f} kt/yr")
    print(f"    2080 SSP585 savings:     {r5pv_2080s585['carbon_savings_kt_vs_current_baseline']:,.0f} kt/yr (fixed factor)")
    print(f"    Cumul 2025-2050 (immed): {cum_save_B_2050:,.0f} kt")
    print(f"    Cumul 2025-2080 (immed): {cum_save_B_2080:,.0f} kt")
    print(f"    P3/P1 multiplier:        {e5['ratio']:.2f}×")


# ---------------------------------------------------------------------------
# Stage G — Figures
# ---------------------------------------------------------------------------

def make_fig12(annual: pd.DataFrame, grid_carbon: pd.DataFrame,
               grid_gdf: gpd.GeoDataFrame, e5: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(21, 7))
    fig.subplots_adjust(wspace=0.30)

    gef_fix = GEF_WAYPOINTS[2025]

    # ---- Panel A: Annual CO2 by scenario (fixed grid factor) ----
    ax = axes[0]
    labels = ["Baseline\n(current)", "R5 only\n(current)", "R5+PV\n(current)",
              "BAU 2080\nSSP585", "R5+PV\n2080 SSP585"]

    # Values at fixed grid factor 0.5703
    get = lambda s, rs, pv: annual[(annual["scenario"]==s) &
                                    (annual["retrofit_status"]==rs) &
                                    (annual["pv_included"]==pv)]["annual_carbon_fixed_kt"].iloc[0]
    values = [
        get("Current", "baseline", False),
        get("Current", "R5", False),
        get("Current", "R5", True),
        get("2080_SSP585", "baseline", False),
        get("2080_SSP585", "R5", True),
    ]
    colors = ["#666666", "#1D9E75", "#C0392B", "#999999", "#E87722"]

    bars = ax.bar(range(5), values, color=colors, alpha=0.85, edgecolor="white", width=0.6)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                f"{v:,.0f}", ha="center", fontsize=8, fontweight="bold")

    ax.axhline(values[0], color="#666666", lw=1.0, ls=":")
    ax.set_xticks(range(5))
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel("Annual CO₂ emissions (kt/yr)")
    ax.set_title("(A) Annual Carbon by Scenario\n(constant 2025 grid factor = 0.5703 tCO₂/MWh)",
                 fontweight="bold")
    ax.set_ylim(0, values[0] * 1.18)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    # Savings annotation
    saving = values[0] - values[2]
    ax.annotate("",
                xy=(2, values[2]), xytext=(2, values[0]),
                arrowprops=dict(arrowstyle="<->", color="#C0392B", lw=1.5))
    ax.text(2.32, (values[0] + values[2])/2, f"−{saving:,.0f} kt\n({saving/values[0]*100:.0f}%)",
            va="center", fontsize=8, color="#C0392B")

    # ---- Panel B: Spatial map of per-grid CO2 avoided ----
    ax = axes[1]

    # Merge co2_avoided_kt into grid GeoJSON
    top50_ids = set(grid_carbon[grid_carbon["rank_integrated"] <= 50]["grid_id"].tolist())
    merged = grid_gdf.merge(grid_carbon[["grid_id", "co2_avoided_kt"]], on="grid_id", how="left")

    occ_mask  = merged["co2_avoided_kt"].notna() & (merged["co2_avoided_kt"] > 0)
    empty_gdf = merged[~occ_mask]
    occ_gdf   = merged[occ_mask]

    empty_gdf.plot(ax=ax, color="#EEEEEE", linewidth=0)
    occ_gdf.plot(ax=ax, column="co2_avoided_kt", cmap="OrRd",
                 linewidth=0.1, edgecolor="white",
                 vmin=0, vmax=occ_gdf["co2_avoided_kt"].quantile(0.95))

    # Top-50 border
    top50_gdf = grid_gdf[grid_gdf["grid_id"].isin(top50_ids)]
    top50_gdf.boundary.plot(ax=ax, color="#C0392B", linewidth=1.6, label="Top-50 grids")

    sm = plt.cm.ScalarMappable(cmap="OrRd",
                               norm=plt.Normalize(0, occ_gdf["co2_avoided_kt"].quantile(0.95)))
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label="CO₂ avoided (kt/yr per grid)", fraction=0.035, pad=0.04)

    ax.set_title("(B) Per-Grid Annual CO₂ Avoided (R5+PV)\n(red outline = top-50 priority grids)",
                 fontweight="bold")
    ax.set_xlabel("Longitude", fontsize=9); ax.set_ylabel("Latitude", fontsize=9)
    ax.legend(fontsize=7.5, loc="lower left")
    ax.tick_params(labelsize=7.5)

    # ---- Panel C: P1 vs P3 comparison ----
    ax = axes[2]
    bar_labels = ["Paper 1\nPV-only\n(1,764 GWh)", "Paper 3\nPV-only\n(1,603 GWh)",
                  "Paper 3\nR5 only\n(5,634 GWh)", "Paper 3\nR5+PV\n(7,237 GWh)"]
    bar_values = [e5["p1_pv_kt"], e5["p3_pv_kt"], e5["p3_r5_kt"], e5["p3_combined_kt"]]
    bar_colors = ["#EF9F27", "#EF9F27", "#1D9E75", "#C0392B"]
    hatches    = ["", "///", "", ""]

    bars2 = ax.bar(range(4), bar_values, color=bar_colors, alpha=0.85,
                   edgecolor="white", width=0.6, hatch=hatches)

    for bar, v, h in zip(bars2, bar_values, hatches):
        bar.set_hatch(h); bar.set_edgecolor("#888888" if h else "white")
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
                f"{v:,.0f}", ha="center", fontsize=8.5, fontweight="bold")

    # Multiplier annotation
    ax.annotate(f"{e5['ratio']:.1f}×\ngreater",
                xy=(3, e5["p3_combined_kt"]), xytext=(1.5, e5["p3_combined_kt"] * 0.7),
                arrowprops=dict(arrowstyle="->", color="#C0392B"),
                fontsize=9.5, color="#C0392B", fontweight="bold")

    ax.set_xticks(range(4))
    ax.set_xticklabels(bar_labels, fontsize=8.5)
    ax.set_ylabel("Annual CO₂ avoided (kt/yr)")
    ax.set_title("(C) Paper 1 PV-only vs Paper 3 Integrated Strategy\n"
                 f"Retrofit multiplies CO₂ impact {e5['ratio']:.1f}×",
                 fontweight="bold")
    ax.set_ylim(0, e5["p3_combined_kt"] * 1.22)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    fig.suptitle("Figure 12 — Carbon Emission Accounting: Baseline, Scenarios, and Spatial Distribution",
                 fontsize=12.5, fontweight="bold", y=1.02)
    OUT_FIG12.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG12, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Figure: {OUT_FIG12.name}")


def make_fig13(cum: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(13, 6.5))

    yrs  = cum["year"].values
    scns = {
        "A": ("BAU (no retrofit, SSP2-4.5, grid decarbonises)", "#666666", "--", 2.0),
        "B": ("R5+PV immediate (2025), SSP2-4.5",              "#C0392B", "-",  2.4),
        "C": ("R5+PV stepwise (0%→100%, 2025–2060), SSP2-4.5", "#1D9E75", "-",  2.0),
        "D": ("R5+PV immediate (2025), SSP5-8.5 worst-case",   "#E87722", "-.", 1.8),
    }

    # Shade avoidable area (A minus B)
    ax.fill_between(yrs, cum["A_cumulative_kt"], cum["B_cumulative_kt"],
                    alpha=0.12, color="#C0392B", label="Avoided by immediate R5+PV")

    for key, (label, color, ls, lw) in scns.items():
        ax.plot(yrs, cum[f"{key}_cumulative_kt"], color=color, ls=ls, lw=lw,
                marker="o", ms=4, label=label)

    # Annotate 2050 and 2080 savings
    yr2050_idx = list(yrs).index(2050)
    yr2080_idx = list(yrs).index(2080)
    for yr_idx, yr_label in [(yr2050_idx, "2050"), (yr2080_idx, "2080")]:
        a_val = cum["A_cumulative_kt"].iloc[yr_idx]
        b_val = cum["B_cumulative_kt"].iloc[yr_idx]
        sav   = a_val - b_val
        ax.annotate(f"−{sav/1000:.0f} Mt\nsaved by {yr_label}",
                    xy=(yrs[yr_idx], (a_val + b_val)/2),
                    fontsize=8, color="#C0392B",
                    ha="right" if yr_label == "2050" else "left",
                    xytext=(-5 if yr_label == "2050" else 5, 0),
                    textcoords="offset points")

    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Cumulative CO₂ emissions (kt)", fontsize=11)
    ax.set_title("Figure 13 — Cumulative Carbon Pathways 2025–2080\n"
                 "Changsha residential buildings (retrofit + rooftop PV, with grid decarbonisation)",
                 fontweight="bold", fontsize=12)
    ax.legend(fontsize=8.5, loc="upper left")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_xticks(yrs[::2])
    ax.grid(axis="y", alpha=0.3)

    # Secondary y-axis in Mt
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim()[0]/1000, ax.get_ylim()[1]/1000)
    ax2.set_ylabel("Cumulative CO₂ (Mt)", fontsize=10, color="#666")
    ax2.tick_params(colors="#666", labelsize=9)

    fig.savefig(OUT_FIG13, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Figure: {OUT_FIG13.name}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("=== carbon_emissions.py — Task 8 ===")

    print("\n[Stage A] Grid decarbonisation parameters:")
    for yr in [2025, 2030, 2040, 2050, 2060, 2070, 2080]:
        print(f"  {yr}: {grid_ef(yr):.4f} tCO₂/MWh")

    print("\n[Stage B] Annual carbon per scenario …")
    cc = pd.read_csv(CLIMATE_RESULTS_CSV)
    annual = stage_b(cc)

    print("\n[Stage C] Per-era and per-grid carbon …")
    bld = pd.read_csv(BUILDINGS_CSV)
    era_df, grid_carbon = stage_c(bld)

    print("\n[Stage D] Cumulative pathways …")
    cum = stage_d()

    print("\n[Stage E] Paper 1 vs Paper 3 …")
    e5 = stage_e()

    print("\n[Stage F] Validation report …")
    write_report(annual, era_df, cum, e5)

    print("\n[Stage G] Figures …")
    grid_gdf = gpd.read_file(GRID_GEOJSON)
    make_fig12(annual, grid_carbon, grid_gdf, e5)
    make_fig13(cum)

    print("\n=== Task 8 COMPLETE ===")


if __name__ == "__main__":
    main()

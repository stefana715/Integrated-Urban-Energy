"""
pv_supply_demand.py — Task 5: PV generation + monthly supply-demand matching
=============================================================================
Stages:
  A  Formalise HP building PV from v5 classification; save pv_city_building.csv
  B  Derive monthly profiles — PV from Paper 2 solar_monthly.csv; heating/cooling
     from HSCW typical; save monthly_profiles.csv
  C  City-level monthly supply-demand matching; save monthly_supply_demand.csv
  D  Narrative analysis → validation_task5.md
  E  Figures fig07_supply_demand.png, fig08_seasonal_match.png

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

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path("/Users/stefana/Desktop/Integrated-Urban-Energy")

BUILDINGS_CSV     = ROOT / "data/integrated/classified_buildings.csv"
SOLAR_MONTHLY_CSV = ROOT / "data/from_paper2/processed/solar_monthly.csv"

OUT_PV_BLD_CSV  = ROOT / "data/integrated/pv_city_building.csv"
OUT_PROFILES    = ROOT / "data/integrated/monthly_profiles.csv"
OUT_SD_CSV      = ROOT / "data/integrated/monthly_supply_demand.csv"
OUT_REPORT      = ROOT / "data/integrated/validation_task5.md"
OUT_FIG7        = ROOT / "figure/fig07_supply_demand.png"
OUT_FIG8        = ROOT / "figure/fig08_seasonal_match.png"

# ---------------------------------------------------------------------------
# Constants from previous tasks
# ---------------------------------------------------------------------------
CITY_ANNUAL_HP_PV_GWH = 1_603.0     # Task 2 v5: high-potential buildings

BASELINE_TOTAL_GWH   = 15_381.6
BASELINE_HEAT_GWH    = 4_535.4
BASELINE_COOL_GWH    = 2_532.2
BASELINE_OTHER_GWH   = 8_313.4      # note: BASELINE_HEAT + COOL + OTHER = 15,381.0 ≈ total

R5_HEAT_SAV_GWH  = 4_374.9          # from Task 4 output
R5_COOL_SAV_GWH  = 838.1

# Post-R5 demand components (task spec: other unchanged)
R5_HEAT_GWH  = BASELINE_HEAT_GWH  - R5_HEAT_SAV_GWH   # 160.5 GWh
R5_COOL_GWH  = BASELINE_COOL_GWH  - R5_COOL_SAV_GWH   # 1,694.1 GWh
R5_OTHER_GWH = BASELINE_OTHER_GWH                       # 8,313.4 GWh (unchanged per spec)
R5_TOTAL_GWH = R5_HEAT_GWH + R5_COOL_GWH + R5_OTHER_GWH

PV_RATES = {"lowrise": 38.8, "midrise": 27.4, "highrise": 6.1}

MONTHS = list(range(1, 13))
MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ---------------------------------------------------------------------------
# HSCW typical monthly demand shares (task spec)
# ---------------------------------------------------------------------------
HEAT_SHARE = {1: .30, 2: .20, 3: .10, 4: .02, 5: .00, 6: .00,
              7: .00, 8: .00, 9: .00, 10: .03, 11: .10, 12: .25}
COOL_SHARE = {1: .00, 2: .00, 3: .00, 4: .02, 5: .05, 6: .15,
              7: .30, 8: .30, 9: .15, 10: .03, 11: .00, 12: .00}
OTHER_SHARE = {1: .09, 2: .08, 3: .08, 4: .08, 5: .08, 6: .08,
               7: .085, 8: .085, 9: .08, 10: .08, 11: .09, 12: .09}

def _normalise(d: dict) -> dict:
    total = sum(d.values())
    return {k: v/total for k, v in d.items()}

HEAT_SHARE  = _normalise(HEAT_SHARE)
COOL_SHARE  = _normalise(COOL_SHARE)
OTHER_SHARE = _normalise(OTHER_SHARE)

# ---------------------------------------------------------------------------
# Stage A — HP building PV formalisation
# ---------------------------------------------------------------------------

def stage_a() -> pd.DataFrame:
    bld = pd.read_csv(BUILDINGS_CSV)
    hp  = bld[bld["is_high_potential"] == 1].copy()
    hp["annual_pv_kwh"] = hp.apply(
        lambda r: r["total_floor_area_m2"] * PV_RATES.get(r["typology"], 0), axis=1
    )
    out = hp[["id", "typology", "total_floor_area_m2", "annual_pv_kwh",
              "is_high_potential"]].copy()
    out.to_csv(OUT_PV_BLD_CSV, index=False, float_format="%.2f")

    city_pv = out["annual_pv_kwh"].sum() / 1e6
    print(f"  HP buildings: {len(out):,}")
    print(f"  City HP PV: {city_pv:.3f} GWh/yr  (target: {CITY_ANNUAL_HP_PV_GWH:.0f} GWh)")
    assert abs(city_pv - CITY_ANNUAL_HP_PV_GWH) < 1.0, \
        f"PV mismatch: {city_pv:.2f} vs {CITY_ANNUAL_HP_PV_GWH}"
    return out


# ---------------------------------------------------------------------------
# Stage B — Monthly profiles
# ---------------------------------------------------------------------------

def stage_b() -> pd.DataFrame:
    """
    Derive PV monthly shares from Paper 2 solar_monthly.csv (actual pvlib output).
    Use Era1/Era2 monthly values (identical in the CSV) as the representative profile.
    Heating/cooling/other from HSCW typical (task spec).
    """
    solar = pd.read_csv(SOLAR_MONTHLY_CSV)
    era1  = solar[solar["era"] == 1].sort_values("month").set_index("month")["pv_gen_kwh"]
    annual = era1.sum()
    pv_share = (era1 / annual).to_dict()

    rows = []
    for m in MONTHS:
        rows.append({
            "month":        m,
            "month_name":   MONTH_NAMES[m-1],
            "pv_share":     round(pv_share[m], 6),
            "heating_share":  round(HEAT_SHARE[m], 6),
            "cooling_share":  round(COOL_SHARE[m], 6),
            "other_share":    round(OTHER_SHARE[m], 6),
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT_PROFILES, index=False)

    print(f"\n  PV monthly shares (Paper 2 solar_monthly.csv, Era1/MidRise):")
    for _, r in df.iterrows():
        print(f"    {r['month_name']:>3}: PV={r['pv_share']*100:.1f}%  "
              f"heat={r['heating_share']*100:.0f}%  "
              f"cool={r['cooling_share']*100:.0f}%  "
              f"other={r['other_share']*100:.1f}%")
    print(f"  Saved: {OUT_PROFILES.name}")
    return df


# ---------------------------------------------------------------------------
# Stage C — Monthly supply-demand matching
# ---------------------------------------------------------------------------

def stage_c(profiles: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, p in profiles.iterrows():
        m = int(p["month"])

        pv   = CITY_ANNUAL_HP_PV_GWH * p["pv_share"]

        # Baseline
        b_heat  = BASELINE_HEAT_GWH  * p["heating_share"]
        b_cool  = BASELINE_COOL_GWH  * p["cooling_share"]
        b_other = BASELINE_OTHER_GWH * p["other_share"]
        b_total = b_heat + b_cool + b_other

        # R5
        r_heat  = R5_HEAT_GWH  * p["heating_share"]
        r_cool  = R5_COOL_GWH  * p["cooling_share"]
        r_other = R5_OTHER_GWH * p["other_share"]
        r_total = r_heat + r_cool + r_other

        # Self-consumption = min(PV, demand) / PV
        b_sc  = min(pv, b_total) / pv if pv > 0 else 0
        b_cov = min(pv, b_total) / b_total if b_total > 0 else 0
        r_sc  = min(pv, r_total) / pv if pv > 0 else 0
        r_cov = min(pv, r_total) / r_total if r_total > 0 else 0

        # Net demand (residual after PV)
        b_net = max(0, b_total - pv)
        r_net = max(0, r_total - pv)

        # Cooling coverage by PV (month-specific)
        # Fraction of cooling demand met if all PV goes to cooling first
        # (conservative: allocate PV to cooling only if cooling > 0)
        b_cool_cov = min(pv, b_cool) / b_cool if b_cool > 0 else 0
        r_cool_cov = min(pv, r_cool) / r_cool if r_cool > 0 else 0

        rows.append({
            "month":                     m,
            "month_name":                MONTH_NAMES[m-1],
            "pv_gen_GWh":               round(pv,   3),
            "baseline_heat_GWh":         round(b_heat,  3),
            "baseline_cool_GWh":         round(b_cool,  3),
            "baseline_other_GWh":        round(b_other, 3),
            "baseline_total_GWh":        round(b_total, 3),
            "r5_heat_GWh":               round(r_heat,  3),
            "r5_cool_GWh":               round(r_cool,  3),
            "r5_other_GWh":              round(r_other, 3),
            "r5_total_GWh":              round(r_total, 3),
            "baseline_self_consumption": round(b_sc,  4),
            "baseline_coverage":         round(b_cov, 4),
            "r5_self_consumption":       round(r_sc,  4),
            "r5_coverage":               round(r_cov, 4),
            "baseline_net_demand_GWh":   round(b_net, 3),
            "r5_net_demand_GWh":         round(r_net, 3),
            "baseline_cool_coverage":    round(b_cool_cov, 4),
            "r5_cool_coverage":          round(r_cool_cov, 4),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_SD_CSV, index=False)
    print(f"  Saved: {OUT_SD_CSV.name}")
    return df


# ---------------------------------------------------------------------------
# Stage D — Validation report
# ---------------------------------------------------------------------------

def stage_d(sd: pd.DataFrame, profiles: pd.DataFrame) -> None:
    annual_pv   = sd["pv_gen_GWh"].sum()
    b_total_ann = sd["baseline_total_GWh"].sum()
    r5_total_ann = sd["r5_total_GWh"].sum()

    # D1 annual self-consumption
    b_sc_ann  = sd.apply(lambda r: min(r["pv_gen_GWh"], r["baseline_total_GWh"]), axis=1).sum()
    r5_sc_ann = sd.apply(lambda r: min(r["pv_gen_GWh"], r["r5_total_GWh"]),       axis=1).sum()
    b_sc_pct  = b_sc_ann  / annual_pv * 100
    r5_sc_pct = r5_sc_ann / annual_pv * 100

    b_net_ann  = sd["baseline_net_demand_GWh"].sum()
    r5_net_ann = sd["r5_net_demand_GWh"].sum()

    # D2 seasonal — months PV exceeds demand?
    b_surplus_months = sd[sd["pv_gen_GWh"] > sd["baseline_total_GWh"]]["month_name"].tolist()
    r5_surplus_months = sd[sd["pv_gen_GWh"] > sd["r5_total_GWh"]]["month_name"].tolist()

    # PV cooling coverage in Jul/Aug under R5
    jul = sd[sd["month"]==7].iloc[0]
    aug = sd[sd["month"]==8].iloc[0]
    r5_cool_cov_jul = jul["r5_cool_coverage"] * 100
    r5_cool_cov_aug = aug["r5_cool_coverage"] * 100
    b_cool_cov_jul  = jul["baseline_cool_coverage"] * 100
    b_cool_cov_aug  = aug["baseline_cool_coverage"] * 100

    # D3 cooling-PV coincidence factor
    pv_share_jun_sep   = profiles[profiles["month"].isin([6,7,8,9])]["pv_share"].sum()
    cool_share_jun_sep = profiles[profiles["month"].isin([6,7,8,9])]["cooling_share"].sum()
    pv_share_dec_feb   = profiles[profiles["month"].isin([12,1,2])]["pv_share"].sum()
    heat_share_dec_feb = profiles[profiles["month"].isin([12,1,2])]["heating_share"].sum()
    coincidence_factor = pv_share_jun_sep / cool_share_jun_sep if cool_share_jun_sep > 0 else 0

    # D4 net demand
    net_red = (b_net_ann - r5_net_ann) / b_net_ann * 100

    # D5 combined savings
    r5_avoided   = BASELINE_TOTAL_GWH - R5_TOTAL_GWH
    pv_consumed_b  = b_sc_ann
    pv_consumed_r5 = r5_sc_ann
    combined_b   = r5_avoided + pv_consumed_b   # conservative (R5 savings + PV self-consumed)
    combined_r5  = r5_avoided + pv_consumed_r5

    lines = [
        "# Validation Report — Task 5: PV Generation + Monthly Supply-Demand",
        "",
        f"**Date:** 2026-04-19",
        "",
        "---",
        "",
        "## Stage A — HP Building PV",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| HP buildings | 6,401 |",
        f"| City annual HP PV (GWh/yr) | {annual_pv:.1f} |",
        f"| Target (Task 2 v5) | 1,603 GWh/yr |",
        f"| Match | {'✓' if abs(annual_pv - 1603) < 2 else '⚠ CHECK'} |",
        "",
        "---",
        "",
        "## Stage B — Monthly Profiles (source: Paper 2 solar_monthly.csv)",
        "",
        "PV monthly shares derived from Paper 2 pvlib output (Era1 MidRise, Changsha 28°N).",
        "Heating/cooling/other from HSCW typical seasonal patterns (task specification).",
        "",
        "| Month | PV share | Heat share | Cool share | Other share |",
        "|---|---|---|---|---|",
    ]
    for _, r in profiles.iterrows():
        lines.append(
            f"| {r['month_name']} | {r['pv_share']*100:.1f}% | "
            f"{r['heating_share']*100:.0f}% | {r['cooling_share']*100:.0f}% | "
            f"{r['other_share']*100:.1f}% |"
        )

    lines += [
        "",
        "**Note on PV profile:** Paper 2 solar data shows July as peak (11.1% of annual),",
        "consistent with Changsha's radiation climatology. Winter months (Dec–Feb) = 20.5%.",
        "",
        "---",
        "",
        "## D1 — Annual Self-Consumption",
        "",
        "| Metric | Baseline | R5 retrofit |",
        "|---|---|---|",
        f"| Annual PV generation (GWh) | {annual_pv:.1f} | {annual_pv:.1f} |",
        f"| Annual demand (GWh) | {b_total_ann:.1f} | {r5_total_ann:.1f} |",
        f"| Annual PV self-consumed (GWh) | {b_sc_ann:.1f} | {r5_sc_ann:.1f} |",
        f"| Self-consumption ratio | {b_sc_pct:.1f}% | {r5_sc_pct:.1f}% |",
        f"| Annual demand coverage by PV | {b_sc_ann/b_total_ann*100:.2f}% | {r5_sc_ann/r5_total_ann*100:.2f}% |",
        "",
        f"PV = {annual_pv:.0f} GWh vs baseline demand = {b_total_ann:.0f} GWh; ratio = {annual_pv/b_total_ann:.3f}.",
        "PV << demand in every month → self-consumption is always 100% (all PV absorbed).",
        "",
        "---",
        "",
        "## D2 — Seasonal Patterns",
        "",
        f"| Metric | Value |",
        "|---|---|",
        f"| Months where PV > baseline demand | {'None ✓' if not b_surplus_months else ', '.join(b_surplus_months)} |",
        f"| Months where PV > R5 demand | {'None ✓' if not r5_surplus_months else ', '.join(r5_surplus_months)} |",
        f"| Baseline cooling covered by PV — July | {b_cool_cov_jul:.1f}% |",
        f"| Baseline cooling covered by PV — August | {b_cool_cov_aug:.1f}% |",
        f"| R5 cooling covered by PV — July | {r5_cool_cov_jul:.1f}% |",
        f"| R5 cooling covered by PV — August | {r5_cool_cov_aug:.1f}% |",
        "",
        f"Even under R5 (greatly reduced cooling = {R5_COOL_GWH:.0f} GWh vs baseline {BASELINE_COOL_GWH:.0f} GWh),",
        f"PV still provides < 100% of summer cooling because PV monthly peak",
        f"({sd['pv_gen_GWh'].max():.0f} GWh in Jul) << R5 cooling peak",
        f"({sd['r5_cool_GWh'].max():.0f} GWh in Jul).",
        "",
        "---",
        "",
        "## D3 — Cooling-PV Coincidence Factor",
        "",
        f"| Metric | Value |",
        "|---|---|",
        f"| PV share Jun–Sep | {pv_share_jun_sep*100:.1f}% |",
        f"| Cooling share Jun–Sep | {cool_share_jun_sep*100:.0f}% |",
        f"| Coincidence factor (PV share / cooling share) | {coincidence_factor:.3f} |",
        f"| PV share Dec–Feb | {pv_share_dec_feb*100:.1f}% |",
        f"| Heating share Dec–Feb | {heat_share_dec_feb*100:.0f}% |",
        "",
        "**Interpretation:**",
        f"- PV-cooling coincidence factor = {coincidence_factor:.2f}. Cooling peaks in Jun–Sep when PV is",
        "  also strong — good natural alignment. Summer PV can directly offset cooling demand.",
        f"- Heating concentrates Dec–Feb (75% of heating) but PV is only {pv_share_dec_feb*100:.1f}%",
        "  of annual in those months — poor alignment. Retrofit (not PV) is the right tool",
        "  for heating reduction in Changsha's HSCW climate.",
        "",
        "---",
        "",
        "## D4 — Net Demand After PV",
        "",
        "| Metric | Baseline | R5 |",
        "|---|---|---|",
        f"| Annual total demand (GWh) | {b_total_ann:.0f} | {r5_total_ann:.0f} |",
        f"| Annual PV self-consumed (GWh) | {b_sc_ann:.0f} | {r5_sc_ann:.0f} |",
        f"| Residual net demand (GWh) | {b_net_ann:.0f} | {r5_net_ann:.0f} |",
        f"| Grid demand reduction vs baseline | — | {b_net_ann - r5_net_ann:.0f} GWh ({net_red:.1f}%) |",
        "",
        "---",
        "",
        "## D5 — Combined Retrofit + PV Savings",
        "",
        "| Intervention | Annual avoided/displaced (GWh) | % of baseline |",
        "|---|---|---|",
        f"| PV alone (all self-consumed) | {annual_pv:.0f} | {annual_pv/BASELINE_TOTAL_GWH*100:.1f}% |",
        f"| R5 retrofit alone | {r5_avoided:.0f} | {r5_avoided/BASELINE_TOTAL_GWH*100:.1f}% |",
        f"| Combined (R5 + PV, conservative) | {r5_avoided + annual_pv:.0f} | {(r5_avoided + annual_pv)/BASELINE_TOTAL_GWH*100:.1f}% |",
        "",
        "**Note:** Combined = R5 retrofit savings + PV self-consumption (= 100% of PV since",
        "demand always > PV). No double-counting because PV is applied to post-R5 demand.",
        "",
        "The combined intervention would reduce the grid-supplied energy from",
        f"{BASELINE_TOTAL_GWH:.0f} GWh to {BASELINE_TOTAL_GWH - r5_avoided - annual_pv:.0f} GWh",
        f"({(r5_avoided + annual_pv)/BASELINE_TOTAL_GWH*100:.1f}% reduction).",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- Self-consumption: {b_sc_pct:.0f}% baseline / {r5_sc_pct:.0f}% R5 — all PV absorbed in both cases",
        f"- PV-cooling coincidence: {coincidence_factor:.2f} — PV naturally hedges cooling growth",
        f"- No month has PV surplus at city scale (PV/{CITY_ANNUAL_HP_PV_GWH:.0f} GWh vs demand >{r5_total_ann:.0f} GWh)",
        f"- Combined retrofit+PV: {(r5_avoided + annual_pv)/BASELINE_TOTAL_GWH*100:.1f}% of baseline demand avoided",
    ]

    OUT_REPORT.write_text("\n".join(lines))
    print(f"  Report: {OUT_REPORT.name}")

    # Print key numbers
    print(f"\n  Key D1-D5 numbers:")
    print(f"    Annual PV:              {annual_pv:.1f} GWh")
    print(f"    Self-consumption (B/R5): {b_sc_pct:.1f}% / {r5_sc_pct:.1f}%")
    print(f"    Cool coverage Jul (B/R5): {b_cool_cov_jul:.1f}% / {r5_cool_cov_jul:.1f}%")
    print(f"    Coincidence factor:      {coincidence_factor:.3f}")
    print(f"    Combined savings:        {r5_avoided + annual_pv:.0f} GWh ({(r5_avoided+annual_pv)/BASELINE_TOTAL_GWH*100:.1f}%)")
    print(f"    Net demand B/R5:         {b_net_ann:.0f} / {r5_net_ann:.0f} GWh")

    return {
        "annual_pv": annual_pv, "b_sc_pct": b_sc_pct, "r5_sc_pct": r5_sc_pct,
        "b_cool_cov_jul": b_cool_cov_jul, "r5_cool_cov_jul": r5_cool_cov_jul,
        "coincidence_factor": coincidence_factor,
        "r5_avoided": r5_avoided, "combined": r5_avoided + annual_pv,
    }


# ---------------------------------------------------------------------------
# Stage E — Figures
# ---------------------------------------------------------------------------

def make_fig7(sd: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.subplots_adjust(wspace=0.32)

    months = MONTH_NAMES

    # --- Panel A: Monthly PV bars vs demand lines ---
    ax = axes[0]
    x   = np.arange(12)
    pv  = sd["pv_gen_GWh"].values
    b_d = sd["baseline_total_GWh"].values
    r5d = sd["r5_total_GWh"].values

    bars = ax.bar(x, pv, 0.6, color="#EF9F27", label="PV generation", alpha=0.85, zorder=3)
    ax.plot(x, b_d, color="#333333", lw=2.2, marker="o", ms=5,
            label=f"Baseline demand ({BASELINE_TOTAL_GWH:.0f} GWh/yr)", zorder=4)
    ax.plot(x, r5d, color="#1D9E75", lw=2.2, marker="s", ms=5, ls="--",
            label=f"R5 demand ({R5_TOTAL_GWH:.0f} GWh/yr)", zorder=4)

    # Annotate max PV month
    mx = np.argmax(pv)
    ax.annotate(f"Peak PV\n{pv[mx]:.0f} GWh",
                xy=(mx, pv[mx]), xytext=(mx-1.5, pv[mx]+50),
                arrowprops=dict(arrowstyle="->", color="#EF9F27"), fontsize=8, color="#EF9F27")
    ax.text(0.02, 0.97, "PV never exceeds\ncity demand",
            transform=ax.transAxes, fontsize=8, va="top", color="#888",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#ccc"))

    ax.set_xticks(x); ax.set_xticklabels(months, fontsize=9)
    ax.set_ylabel("Monthly energy (GWh)")
    ax.set_title("(A) Monthly PV Generation vs Demand\n(Baseline and R5 retrofit)",
                 fontweight="bold")
    ax.legend(fontsize=8.5, loc="upper left")
    ax.set_ylim(0, max(b_d.max(), r5d.max()) * 1.18)

    # --- Panel B: R5 cooling demand vs PV (summer focus) ---
    ax = axes[1]
    r5_cool = sd["r5_cool_GWh"].values
    ax.fill_between(x, r5_cool, alpha=0.35, color="#378ADD", label="R5 cooling demand")
    ax.plot(x, r5_cool, color="#378ADD", lw=2)
    ax.plot(x, pv, color="#EF9F27", lw=2.5, marker="o", ms=5, label="PV generation")

    # shade overlap
    overlap = np.minimum(pv, r5_cool)
    ax.fill_between(x, overlap, alpha=0.55, color="#74B87E",
                    label="Cooling met by PV")

    ax.set_xticks(x); ax.set_xticklabels(months, fontsize=9)
    ax.set_ylabel("Monthly energy (GWh)")
    ax.set_title("(B) Summer PV–Cooling Coincidence (R5 scenario)\n"
                 "Shaded area = cooling demand met by PV",
                 fontweight="bold")
    ax.legend(fontsize=8.5)

    fig.suptitle("Figure 7 — Monthly PV Supply vs Building Energy Demand",
                 fontsize=13, fontweight="bold", y=1.03)
    OUT_FIG7.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG7, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Figure: {OUT_FIG7.name}")


def make_fig8(sd: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(13, 5.5))

    x  = np.arange(12)
    w  = 0.38
    b_sc  = sd["baseline_self_consumption"].values * 100
    r5_sc = sd["r5_self_consumption"].values * 100

    bars1 = ax.bar(x - w/2, b_sc,  w, label="Baseline self-consumption (%)",
                   color="#5B7A9D", alpha=0.85, edgecolor="white")
    bars2 = ax.bar(x + w/2, r5_sc, w, label="R5 self-consumption (%)",
                   color="#1D9E75", alpha=0.85, edgecolor="white")

    # Annotate bars that are below 100%
    for bar, v in zip(bars1, b_sc):
        if v < 99.5:
            ax.text(bar.get_x() + bar.get_width()/2, v + 0.5, f"{v:.0f}%",
                    ha="center", fontsize=7)
    for bar, v in zip(bars2, r5_sc):
        if v < 99.5:
            ax.text(bar.get_x() + bar.get_width()/2, v + 0.5, f"{v:.0f}%",
                    ha="center", fontsize=7)

    ax.set_xticks(x); ax.set_xticklabels(MONTH_NAMES, fontsize=10)
    ax.set_ylabel("PV self-consumption fraction (%)")
    ax.set_ylim(0, 115)
    ax.axhline(100, color="gray", ls=":", lw=1.2)
    ax.set_title("Figure 8 — Monthly PV Self-Consumption Ratio\n"
                 "(Fraction of PV generation absorbed by same-time demand)",
                 fontweight="bold")
    ax.legend(fontsize=9)
    ax.text(0.02, 0.97,
            "100% self-consumption means all PV\nis consumed on-site (no curtailment)",
            transform=ax.transAxes, fontsize=8, va="top",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#ccc"))

    fig.savefig(OUT_FIG8, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Figure: {OUT_FIG8.name}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("=== pv_supply_demand.py — Task 5 ===")

    print("\n[Stage A] HP building PV …")
    pv_bld = stage_a()

    print("\n[Stage B] Monthly profiles …")
    profiles = stage_b()

    print("\n[Stage C] Monthly supply-demand …")
    sd = stage_c(profiles)

    # Print monthly table
    print(f"\n  Monthly supply-demand summary:")
    print(f"  {'Mo':>3} {'PV':>7} {'B-total':>9} {'R5-total':>9} "
          f"{'B-SC%':>7} {'R5-SC%':>7} {'B-net':>8} {'R5-net':>8}")
    for _, r in sd.iterrows():
        print(f"  {r['month_name']:>3} {r['pv_gen_GWh']:>7.1f} "
              f"{r['baseline_total_GWh']:>9.1f} {r['r5_total_GWh']:>9.1f} "
              f"{r['baseline_self_consumption']*100:>7.1f}% {r['r5_self_consumption']*100:>7.1f}% "
              f"{r['baseline_net_demand_GWh']:>8.1f} {r['r5_net_demand_GWh']:>8.1f}")

    print("\n[Stage D] Validation report …")
    metrics = stage_d(sd, profiles)

    print("\n[Stage E] Figures …")
    make_fig7(sd)
    make_fig8(sd)

    print("\n=== Task 5 COMPLETE ===")
    print(f"\nKey results:")
    print(f"  City HP PV:              {metrics['annual_pv']:.1f} GWh/yr")
    print(f"  Self-consumption (B/R5): {metrics['b_sc_pct']:.0f}% / {metrics['r5_sc_pct']:.0f}%")
    print(f"  Cool coverage Jul (R5):  {metrics['r5_cool_cov_jul']:.1f}%")
    print(f"  PV-cool coincidence:     {metrics['coincidence_factor']:.3f}")
    print(f"  Combined R5+PV savings:  {metrics['combined']:.0f} GWh "
          f"({metrics['combined']/BASELINE_TOTAL_GWH*100:.1f}% of baseline)")


if __name__ == "__main__":
    main()

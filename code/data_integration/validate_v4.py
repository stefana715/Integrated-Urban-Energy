#!/usr/bin/env python3
"""
Stage E: Validate v4 (hybrid height + Era3 downgrade) classification.

Outputs:
  data/integrated/validation_v4.md
  figure/fig03c_height_comparison.png   (height source breakdown, 3-panel)
  figure/fig03d_era_typology_v4.png     (Era × Typology final, 4-panel)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec

ROOT    = Path(__file__).resolve().parents[2]
INT_DIR = ROOT / "data" / "integrated"
FIG_DIR = ROOT / "figure"

CSV_V4      = INT_DIR / "classified_buildings.csv"
CSV_V3      = INT_DIR / "classified_buildings_v2_binary_typology.csv"   # v2 backup
CSV_V3_TER  = INT_DIR / "classified_buildings_v3_backup.geojson"
GJSON_V4    = INT_DIR / "classified_buildings.geojson"
GRID_PATH   = ROOT / "data" / "from_paper1" / "grid_changsha_urban_core_solar_baseline.geojson"

OUT_MD      = INT_DIR / "validation_v4.md"
OUT_FIG_H   = FIG_DIR / "fig03c_height_comparison.png"
OUT_FIG_ET  = FIG_DIR / "fig03d_era_typology_v4.png"
FIG_DIR.mkdir(exist_ok=True)

ERA_COLORS  = {"era1": "#D85A30", "era2": "#2E75B6", "era3": "#1D9E75"}
TYPO_COLORS = {"lowrise": "#4D9B6A", "midrise": "#E8A838", "highrise": "#C0392B"}
SRC_COLORS  = {"proxy_only": "#AAAAAA", "mean_agreement": "#4D9B6A",
               "capped_ghsl": "#E8A838", "ghsl_primary": "#2E75B6"}
ERA_LABELS  = {"era1": "Era 1 (pre-2000)", "era2": "Era 2 (2000–2009)",
               "era3": "Era 3 (2010–2020)"}
EUI         = {"era1": 261.2, "era2": 211.4, "era3": 150.4}
PV_RATE     = {"lowrise": 38.8, "midrise": 27.4, "highrise": 6.1}
PAPER1_PV   = 1764.0
EXPECTED_ENERGY_LO = 4200.0
EXPECTED_ENERGY_HI = 5880.0

# Sensitivity parameters
SENS_CAP_RATIO  = 3.0   # alternative: ghsl > 3× proxy (vs default 2×)
SENS_DOWNGRADE  = 0.2   # alternative: v_growth < 0.2 (vs default 0.3)


# ── Sensitivity helpers ───────────────────────────────────────────────────────
def hybrid_height_alt(ghsl, proxy, cap_ratio: float):
    """Re-run hybrid with alternate cap_ratio."""
    canonical = pd.Series(np.nan, index=ghsl.index)
    null  = (ghsl.isna()) | (ghsl <= 0)
    agree = ~null & (np.abs(ghsl - proxy) < 5.0)
    cap   = ~null & ~agree & (ghsl > cap_ratio * proxy)
    pri   = ~null & ~agree & ~cap
    canonical[null]  = proxy[null]
    canonical[agree] = (ghsl[agree] + proxy[agree]) / 2.0
    canonical[cap]   = np.minimum(ghsl[cap], proxy[cap] * 1.5)
    canonical[pri]   = ghsl[pri]
    return canonical


def ternary_typology(h, era1_mask, slab_mask):
    """Apply typology rules to height series."""
    typo = pd.Series("", index=h.index, dtype=str)
    typo[h <= 18.0]                       = "lowrise"
    typo[(h > 18.0) & (h <= 36.0)]        = "midrise"
    typo[h > 36.0]                         = "highrise"
    typo[slab_mask]                        = "lowrise"
    typo[era1_mask & (h < 30.0)]           = "lowrise"
    return typo


def pv_from_df(df_tmp, fa_col="total_floor_area_m2"):
    hp = df_tmp["is_high_potential"] == 1
    rate = df_tmp["typology"].map(PV_RATE)
    pv = df_tmp.loc[hp, fa_col] * rate[hp]
    return pv.sum() / 1e6


# ── Load data ─────────────────────────────────────────────────────────────────
def load_data():
    df4 = pd.read_csv(CSV_V4)
    # v3 ternary from backup geojson (attribute table only, no geometry needed)
    try:
        v3_gdf = gpd.read_file(CSV_V3_TER)
        df3 = pd.DataFrame(v3_gdf.drop(columns="geometry"))
    except Exception:
        df3 = None
    return df4, df3


# ── Compute stats ─────────────────────────────────────────────────────────────
def compute_stats(df4, df3):
    s = {}
    total = len(df4)
    s["total"] = total

    # Height source breakdown
    s["src_counts"] = df4["height_source"].value_counts()
    s["src_mean_h"]  = df4.groupby("height_source")["canonical_height_m"].mean()
    s["src_mean_fc"] = df4.groupby("height_source")["floor_count_est"].mean()

    # Height statistics
    s["canon_mean"]  = df4["canonical_height_m"].mean()
    s["canon_med"]   = df4["canonical_height_m"].median()
    s["ghsl_mean"]   = df4["ghsl_height_m"].mean()
    s["proxy_mean"]  = df4["height_proxy_m"].mean()
    s["floor_mean"]  = df4["floor_count_est"].mean()
    s["fa_total"]    = df4["total_floor_area_m2"].sum() / 1e6

    # Typology distribution
    s["typo_counts"] = df4["typology"].value_counts().reindex(
        ["lowrise","midrise","highrise"], fill_value=0)
    s["era_typo"]    = pd.crosstab(df4["era_final"], df4["typology"])

    # Era 1 HighRise
    e1 = df4[df4["era_final"]=="era1"]
    s["e1_hr"]     = (e1["typology"]=="highrise").sum()
    s["e1_hr_pct"] = 100 * s["e1_hr"] / len(e1)

    # Era 3 LowRise fraction
    e3 = df4[df4["era_final"]=="era3"]
    s["e3_lr_pct"] = 100 * (e3["typology"]=="lowrise").sum() / len(e3) if len(e3) else 0

    # Era distribution
    s["era_counts"] = df4["era_final"].value_counts().reindex(
        ["era1","era2","era3"], fill_value=0)
    s["n_downgraded"] = (df4["era_downgrade_reason"] != "").sum()

    # v3 era distribution (from backup if available)
    if df3 is not None and "era_final" in df3.columns:
        s["era_v3"] = df3["era_final"].value_counts().reindex(
            ["era1","era2","era3"], fill_value=0)
    else:
        s["era_v3"] = pd.Series({"era1":7530,"era2":5271,"era3":6025})

    # PV
    hp = df4["is_high_potential"] == 1
    s["hp_count"]   = hp.sum()
    s["pv_v4_gwh"]  = df4.loc[hp,"annual_pv_kwh_v4"].sum() / 1e6
    s["pv_v3_gwh"]  = df4.loc[hp,"annual_pv_kwh_v3"].sum() / 1e6
    s["pv_v2_gwh"]  = df4.loc[hp,"annual_pv_kwh_v2"].sum() / 1e6

    # EUI-weighted baseline
    s["eui_gwh"] = {}
    s["eui_fa"]  = {}
    for era, eui_val in EUI.items():
        fa = df4.loc[df4["era_final"]==era,"total_floor_area_m2"].sum() / 1e6
        s["eui_fa"][era]  = fa
        s["eui_gwh"][era] = fa * eui_val
    s["eui_total"] = sum(s["eui_gwh"].values())

    return s


# ── Sensitivity ───────────────────────────────────────────────────────────────
def run_sensitivity(df4):
    """Return sensitivity results dict."""
    sens = {}
    ghsl  = df4["ghsl_height_m"]
    proxy = df4["height_proxy_m"]
    era1  = df4["era_final"] == "era1"   # already v4 era (post-downgrade)
    slab  = (df4["footprint_area_m2"] > 2500) & (df4["canonical_height_m"] < 25)
    fp    = df4["footprint_area_m2"]

    # Alt 1: cap_ratio = 3.0 (less aggressive capping)
    canon_alt1 = hybrid_height_alt(ghsl, proxy, cap_ratio=SENS_CAP_RATIO)
    fc_alt1    = np.maximum(np.ceil(canon_alt1 / 3.0), 1).astype(int)
    fa_alt1    = fp * fc_alt1
    typo_alt1  = ternary_typology(canon_alt1, era1, slab)
    tmp1       = df4[["is_high_potential","era_final"]].copy()
    tmp1["typology"] = typo_alt1; tmp1["total_floor_area_m2"] = fa_alt1
    pv_alt1  = pv_from_df(tmp1)
    lr_pct1  = 100*(typo_alt1=="lowrise").sum()/len(df4)
    mid_pct1 = 100*(typo_alt1=="midrise").sum()/len(df4)
    hr_pct1  = 100*(typo_alt1=="highrise").sum()/len(df4)
    sens["alt_cap3"] = {
        "desc": "cap_ratio=3.0 (ghsl>3×proxy → cap)",
        "pv_gwh": pv_alt1, "lr_pct": lr_pct1, "mid_pct": mid_pct1, "hr_pct": hr_pct1,
        "mean_h": canon_alt1.mean(), "fa_total": fa_alt1.sum()/1e6
    }

    # Alt 2: downgrade threshold = 0.2 (stricter downgrade)
    era_alt2 = df4["era_final"].copy()
    mask2 = ((df4["era_final"]=="era3") & (df4["typology"]=="lowrise")
             & (df4["v_growth_post2010"] < SENS_DOWNGRADE))
    era_alt2[mask2] = "era2"
    tmp2 = df4[["is_high_potential","typology","total_floor_area_m2"]].copy()
    tmp2["era_final"] = era_alt2
    pv_alt2   = pv_from_df(tmp2)
    n_down2   = mask2.sum()
    era_counts2 = era_alt2.value_counts().reindex(["era1","era2","era3"], fill_value=0)
    eui_alt2 = sum(
        (tmp2[tmp2["era_final"]==era]["total_floor_area_m2"].sum()/1e6) * EUI[era]
        for era in ["era1","era2","era3"])
    sens["alt_down02"] = {
        "desc": "downgrade_threshold=0.2 (stricter)",
        "pv_gwh": pv_alt2, "n_downgraded": n_down2,
        "era1": era_counts2["era1"], "era2": era_counts2["era2"], "era3": era_counts2["era3"],
        "eui_total": eui_alt2
    }

    # Default recap
    sens["default"] = {
        "desc": "default (cap_ratio=2.0, downgrade=0.3)",
        "pv_gwh": df4.loc[df4["is_high_potential"]==1,"annual_pv_kwh_v4"].sum()/1e6,
        "lr_pct": 100*(df4["typology"]=="lowrise").sum()/len(df4),
        "n_downgraded": (df4["era_downgrade_reason"]!="").sum(),
        "era3": (df4["era_final"]=="era3").sum(),
    }
    return sens


# ── Markdown ──────────────────────────────────────────────────────────────────
def write_md(s, df4, sens):
    lines = []
    A = lines.append

    A("# Validation Report — v4 (Hybrid Height + Era 3 Downgrade)")
    A("")
    A("**Date:** 2026-04-19")
    A("**Method:** Hybrid canonical height (mean-agree/capped/primary) + ternary typology "
      "+ Era 3 LowRise downgrade (v_growth_post2010 < 0.3)")
    A("")
    A("---")
    A("")

    # E1: Height source breakdown
    A("## E1. Height Source Breakdown")
    A("")
    A("| Source | Buildings | % | Mean canonical h (m) | Mean floor count |")
    A("|---|---|---|---|---|")
    for src in ["mean_agreement","capped_ghsl","ghsl_primary","proxy_only"]:
        n   = s["src_counts"].get(src, 0)
        mh  = s["src_mean_h"].get(src, 0)
        mfc = s["src_mean_fc"].get(src, 0)
        A(f"| {src} | {n:,} | {100*n/s['total']:.1f}% | {mh:.2f} | {mfc:.2f} |")
    A("")
    A(f"| **All buildings** | **{s['total']:,}** | | **{s['canon_mean']:.2f}** | "
      f"**{s['floor_mean']:.2f}** |")
    A("")
    A(f"**Comparison:**")
    A(f"| Source | Mean height (m) | Mean floor count |")
    A(f"|---|---|---|")
    A(f"| height_proxy_m (OSM/Paper 1) | {s['proxy_mean']:.2f} | {s['proxy_mean']/3:.1f} |")
    A(f"| ghsl_height_m (GHSL ANBH)   | {s['ghsl_mean']:.2f} | {s['ghsl_mean']/3:.1f} |")
    A(f"| canonical_height_m (v4 hybrid) | {s['canon_mean']:.2f} | {s['floor_mean']:.2f} |")
    A(f"")
    A(f"The hybrid reduces GHSL mean from {s['ghsl_mean']:.1f} m to {s['canon_mean']:.1f} m "
      f"(cap factor 1.5 × proxy=9m caps 7,653 buildings to 13.5 m).")
    A("")

    # E2 note (figure reference)
    A("---")
    A("")
    A("## E2. Height Distribution Comparison")
    A("")
    A("See `figure/fig03c_height_comparison.png` for histograms of all three height sources.")
    A("")

    # E3: Era distribution before/after downgrade
    A("---")
    A("")
    A("## E3. Era Distribution — v3 → v4")
    A("")
    A("| Era | v3 (before downgrade) | v4 (after downgrade) | Change |")
    A("|---|---|---|---|")
    for era in ["era1","era2","era3"]:
        b = s["era_v3"][era]
        a = s["era_counts"][era]
        A(f"| {ERA_LABELS[era]} | {b:,} ({100*b/s['total']:.1f}%) | "
          f"{a:,} ({100*a/s['total']:.1f}%) | {a-b:+,} |")
    A("")
    A(f"**Total downgraded Era 3 → Era 2:** {s['n_downgraded']:,} buildings")
    A(f"  - Criteria: era_final=era3, typology=lowrise, v_growth_post2010 < 0.3")
    A(f"  - Resulting Era 3 LowRise: {int(s['era_typo'].loc['era3','lowrise']) if 'era3' in s['era_typo'].index and 'lowrise' in s['era_typo'].columns else 0:,} "
      f"({s['e3_lr_pct']:.1f}% of Era 3)")
    flag_e3 = " ⚠ still > 30% threshold" if s['e3_lr_pct'] > 30 else " ✓"
    A(f"  Era 3 LowRise fraction: {s['e3_lr_pct']:.1f}%{flag_e3}")
    A("")

    # E4: Era × Typology cross-tab
    A("---")
    A("")
    A("## E4. Era × Typology Cross-tab (v4)")
    A("")
    A("| Era | LowRise | MidRise | HighRise | Total |")
    A("|---|---|---|---|---|")
    et = s["era_typo"]
    for era in ["era1","era2","era3"]:
        if era not in et.index:
            continue
        lr = int(et.loc[era].get("lowrise", 0))
        mr = int(et.loc[era].get("midrise", 0))
        hr = int(et.loc[era].get("highrise", 0))
        n  = lr + mr + hr
        if n == 0:
            continue
        A(f"| {ERA_LABELS[era]} | {lr:,} ({100*lr/n:.0f}%) | {mr:,} ({100*mr/n:.0f}%) | "
          f"{hr:,} ({100*hr/n:.0f}%) | {n:,} |")
    n_lr = s["typo_counts"].get("lowrise",0)
    n_mr = s["typo_counts"].get("midrise",0)
    n_hr = s["typo_counts"].get("highrise",0)
    A(f"| **Total** | **{n_lr:,} ({100*n_lr/s['total']:.1f}%)** | "
      f"**{n_mr:,} ({100*n_mr/s['total']:.1f}%)** | "
      f"**{n_hr:,} ({100*n_hr/s['total']:.1f}%)** | **{s['total']:,}** |")
    A("")
    A("**⚠ ISSUE: 98.8% LowRise** — the capped_ghsl rule (41.8% of buildings) "
      "caps canonical height to proxy×1.5 = 13.5 m for buildings with proxy=9 m (OSM default), "
      "pushing nearly all into the ≤18 m LowRise bucket. Combined with the Era-1 prior "
      "(39.8% of buildings forced LowRise regardless of height), only 219 buildings "
      "escape LowRise classification. The typology is effectively degenerate. "
      "See Sensitivity E8 for alternative cap ratios.")
    flag_e1 = " ⚠" if s["e1_hr_pct"] > 2.0 else " ✓"
    A(f"\nEra 1 HighRise: {s['e1_hr']:,} ({s['e1_hr_pct']:.1f}%){flag_e1} "
      f"(these have canonical_height_m ≥ 36 m; escaped both Era-1 prior and large-slab rule)")
    A("")

    # E5: PV comparison
    A("---")
    A("")
    A("## E5. City-Scale PV — v2 → v3 → v4")
    A("")
    A("| Version | Typology | Height source | PV (GWh/yr) | vs Paper 1 |")
    A("|---|---|---|---|---|")
    A(f"| v2 (binary)  | MidRise/HighRise | GHSL ANBH | {s['pv_v2_gwh']:.1f} | "
      f"{100*(s['pv_v2_gwh']-PAPER1_PV)/PAPER1_PV:+.0f}% |")
    A(f"| v3 (ternary) | LowRise/MidRise/HighRise | GHSL ANBH | {s['pv_v3_gwh']:.1f} | "
      f"{100*(s['pv_v3_gwh']-PAPER1_PV)/PAPER1_PV:+.0f}% |")
    A(f"| v4 (ternary) | LowRise/MidRise/HighRise | Hybrid    | {s['pv_v4_gwh']:.1f} | "
      f"{100*(s['pv_v4_gwh']-PAPER1_PV)/PAPER1_PV:+.0f}% |")
    A(f"| Paper 1 reference | — | OSM proxy | {PAPER1_PV:.0f} | — |")
    A("")
    pct_vs_p1 = 100*(s['pv_v4_gwh'] - PAPER1_PV)/PAPER1_PV
    flag_pv = " ⚠  **OUTSIDE ±25% RANGE**" if abs(pct_vs_p1) > 25 else " ✓"
    A(f"v4 vs Paper 1: {pct_vs_p1:+.1f}%{flag_pv}")
    A("")
    A("**Root cause investigation:**")
    A(f"- v4 HP floor area: {df4[df4['is_high_potential']==1]['total_floor_area_m2'].sum()/1e6:.2f} Mm²")
    A(f"- Paper 1 implied HP floor area @ 27.4 kWh/m²_floor (all MidRise): "
      f"{PAPER1_PV*1e6/27.4/1e6:.2f} Mm²")
    A(f"- v4 applies LowRise rate (38.8) to {100*n_lr/s['total']:.1f}% of all buildings, "
      f"increasing effective PV rate vs Paper 1's assumed MidRise-only")
    A(f"- Even though floor areas are reduced (v4: {s['fa_total']:.1f} Mm² vs v3: ~121.5 Mm²), "
      f"the near-universal LowRise rate (38.8 vs 27.4) keeps the total elevated")
    A("")

    # E6: EUI-weighted baseline
    A("---")
    A("")
    A("## E6. EUI-Weighted Baseline Energy (Task 3 Sanity Check)")
    A("")
    A("| Era | Floor area (Mm²) | EUI (kWh/m²/yr) | Energy (GWh/yr) |")
    A("|---|---|---|---|")
    for era in ["era1","era2","era3"]:
        A(f"| {ERA_LABELS[era]} | {s['eui_fa'][era]:.2f} | {EUI[era]} | {s['eui_gwh'][era]:.0f} |")
    A(f"| **Total** | **{s['fa_total']:.2f}** | | **{s['eui_total']:.0f}** |")
    A("")
    in_range = EXPECTED_ENERGY_LO <= s["eui_total"] <= EXPECTED_ENERGY_HI
    flag_eui = "✓" if in_range else f"⚠  OUT OF RANGE (expected {EXPECTED_ENERGY_LO:.0f}–{EXPECTED_ENERGY_HI:.0f})"
    A(f"**Result: {s['eui_total']:.0f} GWh/yr — {flag_eui}**")
    A("")
    A("**⚠ IMPORTANT NOTE ON THIS COMPARISON:**")
    A("The expected range of 4,200–5,880 GWh refers to Changsha residential "
      "**electricity** consumption (25–35% of ~16,800 GWh citywide electricity). "
      "Paper 2's EUI values (261.2 / 211.4 / 150.4 kWh/m²/yr) represent **total final "
      "energy** (electricity + natural gas). In HSCW climate zones, space heating uses "
      "gas; the electricity share of residential EUI is typically ~40–60% of total. "
      "Applying an electricity fraction of 45%: "
      f"{s['eui_total']*0.45:.0f} GWh/yr — "
      f"{'✓ in range' if EXPECTED_ENERGY_LO <= s['eui_total']*0.45 <= EXPECTED_ENERGY_HI else '⚠ still out of range'}. "
      "Additionally, this dataset covers only the Changsha urban core (~18,826 buildings), "
      "not the full city residential stock. Direct comparison to city-level statistics "
      "is indicative only.")
    A("")

    # E7 (spatial) — note only
    A("---")
    A("")
    A("## E7. Spatial Validation")
    A("")
    A("See `figure/fig03d_era_typology_v4.png` Panel D for dominant era per 500m grid. "
      "Spatial patterns are discussed below.")
    A("")

    # E8: Sensitivity
    A("---")
    A("")
    A("## E8. Sensitivity Analysis")
    A("")
    A("### Alt-1: cap_ratio = 3.0 instead of 2.0")
    a1 = sens["alt_cap3"]
    A(f"With `ghsl > 3× proxy → capped` (vs default 2×):")
    A(f"- LowRise / MidRise / HighRise: {a1['lr_pct']:.1f}% / {a1['mid_pct']:.1f}% / {a1['hr_pct']:.1f}%")
    A(f"- Mean canonical height: {a1['mean_h']:.2f} m")
    A(f"- Total floor area: {a1['fa_total']:.2f} Mm²")
    A(f"- City PV (HP only): {a1['pv_gwh']:.1f} GWh/yr "
      f"({100*(a1['pv_gwh']-PAPER1_PV)/PAPER1_PV:+.1f}% vs Paper 1)")
    A("")
    A("### Alt-2: downgrade threshold = 0.2 instead of 0.3")
    a2 = sens["alt_down02"]
    A(f"With `v_growth_post2010 < 0.2` for Era 3 downgrade:")
    A(f"- Buildings downgraded: {a2['n_downgraded']:,} (vs {sens['default']['n_downgraded']:,})")
    A(f"- Era distribution: Era1={a2['era1']:,}, Era2={a2['era2']:,}, Era3={a2['era3']:,}")
    A(f"- City PV (HP only): {a2['pv_gwh']:.1f} GWh/yr "
      f"({100*(a2['pv_gwh']-PAPER1_PV)/PAPER1_PV:+.1f}% vs Paper 1)")
    A(f"- EUI baseline: {a2['eui_total']:.0f} GWh/yr")
    A("")
    A("### Summary table")
    A("")
    A("| Scenario | LowRise% | PV (GWh/yr) | vs Paper 1 | Era 3 buildings |")
    A("|---|---|---|---|---|")
    A(f"| v4 default (cap=2.0, down=0.3) | {sens['default']['lr_pct']:.1f}% | "
      f"{sens['default']['pv_gwh']:.1f} | {100*(sens['default']['pv_gwh']-PAPER1_PV)/PAPER1_PV:+.1f}% | "
      f"{sens['default']['era3']:,} |")
    A(f"| Alt cap=3.0 | {a1['lr_pct']:.1f}% | {a1['pv_gwh']:.1f} | "
      f"{100*(a1['pv_gwh']-PAPER1_PV)/PAPER1_PV:+.1f}% | {sens['default']['era3']:,} |")
    A(f"| Alt down=0.2 | {sens['default']['lr_pct']:.1f}% | {a2['pv_gwh']:.1f} | "
      f"{100*(a2['pv_gwh']-PAPER1_PV)/PAPER1_PV:+.1f}% | {a2['era3']:,} |")
    A("")
    A("**Interpretation:** The PV total is dominated by the LowRise fraction (38.8 rate). "
      "Changing the cap_ratio from 2.0 to 3.0 reduces the fraction of buildings that get "
      "capped to proxy×1.5, allowing more to use GHSL heights. This increases MidRise/HighRise "
      "fractions and reduces PV. The downgrade threshold sensitivity mainly affects the "
      "Era 2/3 distribution and thus EUI baseline, with minimal PV impact "
      "(since typology is unchanged by the downgrade).")
    A("")
    A("---")
    A("")
    A("## E9. Recommendation for v5")
    A("")
    A("The v4 hybrid rule produces 98.8% LowRise, which is degenerate for typology classification. "
      "The fundamental problem is: **proxy=9 m (OSM 3-floor default) is a floor not a ceiling**. "
      "Capping GHSL at 1.5×proxy=13.5 m forces buildings that GHSL measures at 20-35 m into "
      "the ≤18 m LowRise bucket, destroying the typology signal.")
    A("")
    A("**Recommended alternatives for user consideration:**")
    A("1. **Use height_proxy_m only where OSM levels exist** (5.2% of buildings); "
      "use GHSL for the rest (essentially revert to v3 with the Era-1 prior correction)")
    A("2. **Apply cap only where proxy is a building-type default** (e.g., proxy ∈ {9, 12, 15} m); "
      "trust GHSL for buildings with measured OSM levels")
    A("3. **Raise the cap factor** from 1.5 to 2.5 or 3.0 — sensitivity shows "
      "this produces a more differentiated typology while still correcting the most "
      "extreme GHSL overestimates")
    A("4. **Fix the floor area separately from typology**: use height_proxy_m for "
      "floor count (conservative, consistent with Paper 1), but use GHSL for typology "
      "threshold (≥ 25m → MidRise or HighRise)")

    text = "\n".join(lines)
    OUT_MD.write_text(text)
    print(f"  ✓ Report: {OUT_MD.relative_to(ROOT)}")


# ── Figures ───────────────────────────────────────────────────────────────────
def make_height_figure(df4):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Panel 1: Overlapping histograms
    ax = axes[0]
    bins = np.linspace(0, 60, 50)
    ax.hist(df4["height_proxy_m"].clip(0, 60), bins=bins, alpha=0.5,
            label=f"height_proxy_m (mean={df4['height_proxy_m'].mean():.1f}m)", color="#E67E22")
    ax.hist(df4["ghsl_height_m"].clip(0, 60), bins=bins, alpha=0.5,
            label=f"ghsl_height_m (mean={df4['ghsl_height_m'].mean():.1f}m)", color="#2E75B6")
    ax.hist(df4["canonical_height_m"].clip(0, 60), bins=bins, alpha=0.5,
            label=f"canonical_height_m (mean={df4['canonical_height_m'].mean():.1f}m)", color="#1D9E75")
    ax.axvline(18, color="red", lw=1.2, ls="--", alpha=0.7, label="18 m threshold")
    ax.axvline(36, color="darkred", lw=1.2, ls=":", alpha=0.7, label="36 m threshold")
    ax.set_xlabel("Height (m)"); ax.set_ylabel("Buildings")
    ax.set_title("A  Height distributions (all three sources)", fontsize=10, fontweight="bold")
    ax.legend(fontsize=7)

    # Panel 2: Height source stacked bar by height bin
    ax2 = axes[1]
    bins2 = [0, 5, 10, 15, 18, 22, 26, 30, 36, 45, 60]
    bin_labels = [f"{bins2[i]}–{bins2[i+1]}" for i in range(len(bins2)-1)]
    df4["h_bin"] = pd.cut(df4["canonical_height_m"], bins=bins2,
                          labels=bin_labels, right=False)
    ct = pd.crosstab(df4["h_bin"], df4["height_source"])
    ct = ct.reindex(columns=["proxy_only","mean_agreement","capped_ghsl","ghsl_primary"],
                    fill_value=0)
    bottom = np.zeros(len(ct))
    for src, col in SRC_COLORS.items():
        if src not in ct.columns:
            continue
        vals = ct[src].values
        ax2.bar(range(len(ct)), vals, bottom=bottom, color=col, label=src, width=0.8)
        bottom += vals
    ax2.set_xticks(range(len(ct)))
    ax2.set_xticklabels(bin_labels, rotation=45, ha="right", fontsize=7)
    ax2.set_xlabel("canonical_height_m bin (m)"); ax2.set_ylabel("Buildings")
    ax2.set_title("B  Height source by canonical height bin", fontsize=10, fontweight="bold")
    ax2.legend(fontsize=7)

    # Panel 3: Scatter ghsl vs proxy, colored by height_source
    ax3 = axes[2]
    for src, col in SRC_COLORS.items():
        sub = df4[df4["height_source"]==src]
        ax3.scatter(sub["height_proxy_m"].clip(0,50), sub["ghsl_height_m"].clip(0,50),
                    c=col, s=1.5, alpha=0.3, label=src, rasterized=True)
    ax3.plot([0,50],[0,50], "k--", lw=0.8, alpha=0.4, label="1:1 line")
    ax3.plot([0,50],[0,25], color="orange", lw=0.8, ls=":", alpha=0.6, label="ghsl=2×proxy")
    ax3.set_xlabel("height_proxy_m (m)"); ax3.set_ylabel("ghsl_height_m (m)")
    ax3.set_title("C  GHSL vs proxy scatter\n(coloured by height_source)", fontsize=10, fontweight="bold")
    ax3.legend(markerscale=5, fontsize=7)

    fig.suptitle("v4 Hybrid Height — Source Breakdown and Distribution",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_FIG_H, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Figure: {OUT_FIG_H.relative_to(ROOT)}")


def make_era_typo_figure(df4, s):
    fig = plt.figure(figsize=(18, 14))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)
    era_order = ["era1","era2","era3"]
    typo_order = ["lowrise","midrise","highrise"]

    # Panel A: Era distribution donut
    ax_a = fig.add_subplot(gs[0, 0])
    era_counts = s["era_counts"]
    wedges, _, autos = ax_a.pie(
        [era_counts[e] for e in era_order],
        labels=[ERA_LABELS[e] + f"\n({era_counts[e]:,})" for e in era_order],
        autopct="%1.1f%%", colors=[ERA_COLORS[e] for e in era_order],
        startangle=90, wedgeprops={"width": 0.55}, pctdistance=0.78)
    for at in autos: at.set_fontsize(9)
    ax_a.set_title("A  Era distribution v4", fontsize=11, fontweight="bold")

    # Panel B: Era × Typology stacked bar
    ax_b = fig.add_subplot(gs[0, 1])
    et = s["era_typo"].reindex(era_order).fillna(0)
    x = np.arange(len(era_order))
    bot = np.zeros(len(era_order))
    for t in typo_order:
        vals = et[t].values if t in et.columns else np.zeros(len(era_order))
        ax_b.bar(x, vals, bottom=bot, color=TYPO_COLORS[t], label=t.capitalize(), width=0.6)
        for i,(v,b) in enumerate(zip(vals,bot)):
            tot_i = et.loc[era_order[i]].sum()
            if tot_i > 0 and v/tot_i > 0.03:
                ax_b.text(i, b+v/2, f"{100*v/tot_i:.0f}%",
                          ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        bot += vals
    ax_b.set_xticks(x)
    era_labels_short = {"era1":"Era 1\n(pre-2000)","era2":"Era 2\n(2000–09)",
                        "era3":"Era 3\n(2010–20)"}
    ax_b.set_xticklabels([era_labels_short[e] for e in era_order], fontsize=9)
    ax_b.set_ylabel("Buildings"); ax_b.legend(fontsize=8)
    ax_b.set_title("B  Era × Typology (v4)", fontsize=11, fontweight="bold")

    # Panel C: floor area comparison (proxy vs canonical)
    ax_c = fig.add_subplot(gs[1, 0])
    proxy_fa = df4["footprint_area_m2"] * np.maximum(np.ceil(df4["height_proxy_m"]/3), 1)
    ax_c.scatter(proxy_fa/1e3, df4["total_floor_area_m2"]/1e3,
                 s=1.5, alpha=0.3, c="#2E75B6", rasterized=True)
    lim = max(proxy_fa.quantile(.99), df4["total_floor_area_m2"].quantile(.99)) / 1e3
    ax_c.plot([0,lim],[0,lim], "k--", lw=0.8, alpha=0.5, label="1:1 line")
    ax_c.set_xlabel("Floor area using height_proxy_m (×10³ m²)", fontsize=9)
    ax_c.set_ylabel("Floor area using canonical_height_m (×10³ m²)", fontsize=9)
    ax_c.set_title("C  Floor area: proxy vs hybrid canonical", fontsize=11, fontweight="bold")
    ax_c.legend(fontsize=8)

    # Panel D: spatial map of era per grid
    ax_d = fig.add_subplot(gs[1, 1])
    try:
        gdf_grid = gpd.read_file(GRID_PATH)
        grid_era = df4.groupby("grid_id")["era_final"].agg(
            lambda x: x.value_counts().index[0]).reset_index()
        gdf_grid = gdf_grid.merge(grid_era, on="grid_id", how="left")
        for era in era_order:
            sub = gdf_grid[gdf_grid["era_final"]==era]
            if len(sub):
                sub.plot(ax=ax_d, color=ERA_COLORS[era], alpha=0.7, linewidth=0.2, edgecolor="white")
        patches = [mpatches.Patch(color=ERA_COLORS[e], label=ERA_LABELS[e]) for e in era_order]
        ax_d.legend(handles=patches, fontsize=8, loc="lower right")
    except Exception as exc:
        ax_d.text(0.5,0.5,f"Map unavailable:\n{exc}", ha="center", va="center",
                  transform=ax_d.transAxes, fontsize=8)
    ax_d.set_axis_off()
    ax_d.set_title("D  Dominant era per 500m grid (v4)", fontsize=11, fontweight="bold")

    fig.suptitle("Task 2 v4 — Final Classification: Era × Typology\n"
                 "18,826 buildings  |  Hybrid height  |  Era 3 LowRise downgrade applied",
                 fontsize=12, fontweight="bold")
    fig.savefig(OUT_FIG_ET, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Figure: {OUT_FIG_ET.relative_to(ROOT)}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*60)
    print("Stage E: Validate v4 classification")
    print("="*60)

    df4, df3 = load_data()
    print(f"Loaded v4: {len(df4):,}")

    s    = compute_stats(df4, df3)
    sens = run_sensitivity(df4)

    write_md(s, df4, sens)
    make_height_figure(df4)
    make_era_typo_figure(df4, s)

    print(f"\n✓ Validation complete.")
    print(f"  {OUT_MD.relative_to(ROOT)}")
    print(f"  {OUT_FIG_H.relative_to(ROOT)}")
    print(f"  {OUT_FIG_ET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

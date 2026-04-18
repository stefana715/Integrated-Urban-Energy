#!/usr/bin/env python3
"""
Stage D v3: Validate ternary typology classification.

Outputs:
  data/integrated/typology_validation_v3.md
  figure/fig03c_stock_classification_v3.png   (7-panel)
"""

from pathlib import Path
import textwrap
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

CSV_V3    = INT_DIR / "classified_buildings.csv"
CSV_V2    = INT_DIR / "classified_buildings_v2_binary_typology.csv"
GJSON_V3  = INT_DIR / "classified_buildings.geojson"
GRID_PATH = ROOT / "data" / "from_paper1" / "grid_changsha_urban_core_solar_baseline.geojson"

OUT_MD  = INT_DIR / "typology_validation_v3.md"
OUT_FIG = FIG_DIR / "fig03c_stock_classification_v3.png"
FIG_DIR.mkdir(exist_ok=True)

ERA_COLORS  = {"era1": "#D85A30", "era2": "#2E75B6", "era3": "#1D9E75"}
TYPO_COLORS = {"lowrise": "#4D9B6A", "midrise": "#E8A838", "highrise": "#C0392B"}
ERA_LABELS  = {
    "era1": "Era 1 (pre-2000)",
    "era2": "Era 2 (2000–2009)",
    "era3": "Era 3 (2010–2020)",
}
PV_RATE = {"lowrise": 38.8, "midrise": 27.4, "highrise": 6.1}
PAPER1_PV_GWH = 1764.0


# ── Stats ─────────────────────────────────────────────────────────────────────
def compute_stats(df: pd.DataFrame, df_v2: pd.DataFrame) -> dict:
    s = {}
    total = len(df)
    s["total"] = total

    # Typology distribution
    s["typo_counts"] = df["typology"].value_counts().reindex(
        ["lowrise", "midrise", "highrise"], fill_value=0)

    # Era × typology crosstab
    s["era_typo"] = pd.crosstab(df["era_final"], df["typology"])

    # Rule breakdown
    s["rule_counts"] = df["typology_reason"].value_counts()

    # Era 1 HighRise flag
    e1 = df[df["era_final"] == "era1"]
    s["e1_total"] = len(e1)
    s["e1_highrise"] = (e1["typology"] == "highrise").sum()
    s["e1_highrise_pct"] = 100 * s["e1_highrise"] / s["e1_total"]

    # Era 1 HighRise buildings detail (top 20 by ghsl height)
    e1_hr = df[(df["era_final"] == "era1") & (df["typology"] == "highrise")]
    s["e1_hr_detail"] = e1_hr[["id", "ghsl_height_m", "footprint_area_m2",
                                "building_category"]].sort_values(
        "ghsl_height_m", ascending=False).head(20)

    # PV comparison
    hp = df[df["is_high_potential"] == 1]
    s["hp_count"]    = len(hp)
    s["pv_v3_gwh"]   = hp["annual_pv_kwh_v3"].sum() / 1e6
    s["pv_v2_gwh"]   = hp["annual_pv_kwh_v2"].sum() / 1e6

    # Paper 1 floor area comparison
    s["floor_area_total_mm2"]  = df["floor_area_m2"].sum() / 1e6
    s["floor_area_hp_mm2"]     = hp["floor_area_m2"].sum() / 1e6
    s["floor_area_v3_pv_mm2"]  = hp["floor_area_m2"].sum() / 1e6  # same as above

    # GHSL height distribution by typology
    s["height_by_typo"] = {}
    for t in ["lowrise", "midrise", "highrise"]:
        h = df[df["typology"] == t]["ghsl_height_m"]
        s["height_by_typo"][t] = h

    # v2 vs v3 typology comparison
    df_cmp = df[["id", "typology"]].merge(
        df_v2[["id", "typology"]].rename(columns={"typology": "typology_v2"}),
        on="id", how="left")
    s["typo_change"] = pd.crosstab(df_cmp["typology_v2"], df_cmp["typology"],
                                   rownames=["v2 binary"], colnames=["v3 ternary"])

    # HP by era/typology
    s["hp_by_era"] = df.groupby("era_final")["is_high_potential"].sum()
    s["hp_era_typo"] = df[df["is_high_potential"] == 1].groupby(
        ["era_final", "typology"]).size().unstack(fill_value=0)

    return s


# ── Markdown report ──────────────────────────────────────────────────────────
def write_md(s: dict, df: pd.DataFrame) -> None:
    total = s["total"]
    lines = []
    A = lines.append

    A("# Typology Validation Report — v3 (Ternary Classification)")
    A("")
    A("**Date:** 2026-04-19")
    A("**Method:** LowRise/MidRise/HighRise with Era-1 prior + footprint sanity + GHSL ANBH thresholds")
    A("")
    A("---")
    A("")

    # V1: Typology distribution
    A("## V1. Typology Distribution")
    A("")
    A("### Overall")
    A("")
    A("| Typology | Count | % |")
    A("|---|---|---|")
    for t in ["lowrise", "midrise", "highrise"]:
        n = s["typo_counts"].get(t, 0)
        A(f"| {t.capitalize()} | {n:,} | {100*n/total:.1f}% |")
    A("")
    A("### By Era")
    A("")
    A("| Era | LowRise | MidRise | HighRise | Total |")
    A("|---|---|---|---|---|")
    era_typo = s["era_typo"]
    for era in ["era1", "era2", "era3"]:
        row = era_typo.loc[era] if era in era_typo.index else pd.Series({})
        lr = int(row.get("lowrise", 0))
        mr = int(row.get("midrise", 0))
        hr = int(row.get("highrise", 0))
        n  = lr + mr + hr
        A(f"| {ERA_LABELS[era]} | {lr:,} ({100*lr/n:.0f}%) | {mr:,} ({100*mr/n:.0f}%) | {hr:,} ({100*hr/n:.0f}%) | {n:,} |")
    A("")
    A("**Expected ranges (from historical context):**")
    A("- Era 1: ~95% LowRise, ~5% MidRise, ~0% HighRise")
    A("- Era 2: ~40% LowRise, ~45% MidRise, ~15% HighRise")
    A("- Era 3: ~20% LowRise, ~40% MidRise, ~40% HighRise")
    A("")
    e1_hr_pct = s["e1_highrise_pct"]
    flag = " ⚠  **FLAGGED** — above 2% review threshold" if e1_hr_pct > 2.0 else " ✓"
    A(f"**Era 1 HighRise:** {s['e1_highrise']:,} buildings ({e1_hr_pct:.1f}% of Era 1){flag}")
    A("")
    if e1_hr_pct > 2.0:
        A("These are Era 1 buildings with GHSL ANBH ≥ 30 m (escaped the Era-1 prior). Likely candidates:")
        A("- Pre-2000 hotel/office towers in the historic city core")
        A("- GHSL cell averaging effects (a tall post-2000 tower pulls up the 100m cell average)")
        A("- Commercial/industrial buildings not corrected by the footprint rule (<2500 m²)")
        A("")
        A("**Top 20 Era 1 HighRise buildings by GHSL height:**")
        A("")
        A(s["e1_hr_detail"].to_markdown(index=False))
    A("")

    # V2: Rule breakdown
    A("---")
    A("")
    A("## V2. Rule Usage Breakdown")
    A("")
    A("| Rule | Buildings | % |")
    A("|---|---|---|")
    rule_labels = {
        "era1_prior": "Era-1 prior (h < 30 m → LowRise)",
        "large_footprint_shallow": "Large-footprint slab (fp > 2500 m², h < 25 m → LowRise)",
        "ghsl_height_low": "GHSL primary: ≤ 18 m → LowRise",
        "ghsl_height_mid": "GHSL primary: 18–36 m → MidRise",
        "ghsl_height_high": "GHSL primary: > 36 m → HighRise",
        "height_proxy_fallback": "Height-proxy fallback (GHSL = 0)",
    }
    for rule, n in s["rule_counts"].items():
        label = rule_labels.get(rule, rule)
        A(f"| {label} | {n:,} | {100*n/total:.1f}% |")
    A("")
    A("**Interpretation:** The Era-1 prior and GHSL-low together account for the LowRise majority. "
      "The large-footprint slab rule corrects ~644 commercial/industrial buildings whose GHSL ANBH "
      "overstates height due to grid-cell averaging with adjacent towers.")
    A("")

    # V3: PV impact
    A("---")
    A("")
    A("## V3. City-Scale PV Comparison (HP Buildings Only)")
    A("")
    A("| Version | Typology scheme | HP buildings | Total PV (GWh/yr) |")
    A("|---|---|---|---|")
    A(f"| v2 (binary)  | MidRise / HighRise         | {s['hp_count']:,} | {s['pv_v2_gwh']:.1f} |")
    A(f"| v3 (ternary) | LowRise / MidRise / HighRise | {s['hp_count']:,} | {s['pv_v3_gwh']:.1f} |")
    A(f"| Paper 1 reference | — | 6,411 | {PAPER1_PV_GWH:.0f} |")
    A("")
    delta = s["pv_v3_gwh"] - s["pv_v2_gwh"]
    p1_delta_pct = 100 * (s["pv_v3_gwh"] - PAPER1_PV_GWH) / PAPER1_PV_GWH
    A(f"- v3 vs v2: **{delta:+.1f} GWh/yr** ({100*delta/s['pv_v2_gwh']:+.0f}%) — driven by Era 1 "
      f"LowRise reclassification from HighRise (38.8 vs 6.1 kWh/m²_floor)")
    A(f"- v3 vs Paper 1: **{s['pv_v3_gwh'] - PAPER1_PV_GWH:+.1f} GWh/yr** ({p1_delta_pct:+.0f}%)")
    A("")

    # V4: Paper 1 comparison breakdown
    A("---")
    A("")
    A("## V4. Comparison with Paper 1 Reference (1,764 GWh/yr)")
    A("")
    hp = df[df["is_high_potential"] == 1]
    fa_total = hp["floor_area_m2"].sum()
    A(f"**v3 HP floor area total:** {fa_total/1e6:.2f} Mm²")
    A(f"**Paper 1 implied HP floor area:** {PAPER1_PV_GWH*1e6 / 27.4 / 1e6:.2f} Mm² "
      f"(if all HP were MidRise at 27.4 kWh/m²_floor)")
    A("")
    A("**Root cause of the {:.0f}% gap:**".format(p1_delta_pct))
    A("")

    # Average floor count and footprint comparison
    avg_floors_v3 = hp["floor_count_est"].mean()
    avg_fp_v3 = hp["footprint_area_m2"].mean()
    A(f"| Metric | v3 (GHSL heights) | Implied Paper 1 |")
    A(f"|---|---|---|")
    A(f"| Avg floor count (HP) | {avg_floors_v3:.1f} | ~3.5 (height_proxy_m ÷ 3) |")
    A(f"| Avg footprint (HP) | {avg_fp_v3:.0f} m² | same dataset |")
    A(f"| Avg floor area / building | {hp['floor_area_m2'].mean():.0f} m² | ~2,200 m² est. |")
    A(f"| HP count | {len(hp):,} | 6,411 |")
    A("")
    A("The v3 estimate is higher than Paper 1 primarily because **floor areas are computed using GHSL ANBH "
      "heights (mean 17.9 m → ~6 floors)** instead of Paper 1's OSM-derived height_proxy_m (mean 10.6 m → ~4 floors). "
      "GHSL ANBH may overstate individual building heights because it represents the 100m cell average "
      "(which includes taller neighbours). This height inflation carries through to floor_area_m2 and thus PV. "
      "The discrepancy is a **known limitation** (see DEC-010) and should be discussed in the manuscript.")
    A("")
    A("> **Recommendation for Task 5:** Recompute floor_area_m2 using height_proxy_m for buildings where "
      "GHSL ANBH > 2× height_proxy_m, or apply a correction factor. Alternatively, cap floor_count_est "
      "at a physically plausible maximum by building category. Flag for user review.")
    A("")

    # V5: Height distribution by typology
    A("---")
    A("")
    A("## V5. GHSL Height Distribution by Typology")
    A("")
    A("| Typology | Min (m) | P25 (m) | Median (m) | P75 (m) | Max (m) | N |")
    A("|---|---|---|---|---|---|---|")
    for t in ["lowrise", "midrise", "highrise"]:
        h = s["height_by_typo"][t]
        if len(h) == 0:
            continue
        A(f"| {t.capitalize()} | {h.min():.1f} | {h.quantile(.25):.1f} | "
          f"{h.median():.1f} | {h.quantile(.75):.1f} | {h.max():.1f} | {len(h):,} |")
    A("")
    A("**Overlap check:** LowRise includes Era-1-prior buildings with heights up to 29.9 m — "
      "the Era-1 prior does significant work in this range. The MidRise and HighRise distributions "
      "should be well-separated (18–36 m vs >36 m) since those rely purely on GHSL thresholds. "
      "Any LowRise buildings with GHSL > 18 m are accounted for by either the Era-1 prior or "
      "the large-footprint slab rule.")
    A("")

    # V6: Typology change v2→v3
    A("---")
    A("")
    A("## V6. Typology Change v2 (Binary) → v3 (Ternary)")
    A("")
    A("```")
    A(s["typo_change"].to_string())
    A("```")
    A("")
    A("*(Rows = v2 binary label; columns = v3 ternary label)*")
    A("")

    # HP by era×typology
    A("---")
    A("")
    A("## V7. High-Potential Buildings by Era × Typology (v3)")
    A("")
    A("| Era | LowRise HP | MidRise HP | HighRise HP | Total HP |")
    A("|---|---|---|---|---|")
    hp_et = s["hp_era_typo"]
    for era in ["era1", "era2", "era3"]:
        if era not in hp_et.index:
            continue
        row = hp_et.loc[era]
        lr = int(row.get("lowrise", 0))
        mr = int(row.get("midrise", 0))
        hr = int(row.get("highrise", 0))
        A(f"| {ERA_LABELS[era]} | {lr:,} | {mr:,} | {hr:,} | {lr+mr+hr:,} |")
    A("")

    text = "\n".join(lines)
    OUT_MD.write_text(text)
    print(f"  ✓ Report: {OUT_MD.relative_to(ROOT)}")


# ── Figure ───────────────────────────────────────────────────────────────────
def make_figure(df: pd.DataFrame, df_v2: pd.DataFrame, s: dict) -> None:
    fig = plt.figure(figsize=(20, 22))
    gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.45, wspace=0.35)

    era_order  = ["era1", "era2", "era3"]
    typo_order = ["lowrise", "midrise", "highrise"]
    era_labels_short = {"era1": "Era 1\n(pre-2000)", "era2": "Era 2\n(2000–09)",
                        "era3": "Era 3\n(2010–20)"}

    # ── Panel A: Era distribution donut ──────────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    era_counts = df["era_final"].value_counts().reindex(era_order, fill_value=0)
    colors_a = [ERA_COLORS[e] for e in era_order]
    wedges, texts, autotexts = ax_a.pie(
        era_counts.values,
        labels=[ERA_LABELS[e] for e in era_order],
        autopct="%1.1f%%",
        colors=colors_a,
        startangle=90,
        wedgeprops={"width": 0.55},
        pctdistance=0.75,
    )
    for at in autotexts:
        at.set_fontsize(9)
    ax_a.set_title("A  Era distribution (v2 calibrated, 40/28/32)", fontsize=11, fontweight="bold")

    # ── Panel B: Era × Typology stacked bar (ternary) ────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    era_typo = df.groupby("era_final")["typology"].value_counts().unstack(fill_value=0)
    era_typo = era_typo.reindex(era_order).fillna(0)
    x = np.arange(len(era_order))
    bottom = np.zeros(len(era_order))
    for t in typo_order:
        vals = era_typo[t].values if t in era_typo.columns else np.zeros(len(era_order))
        ax_b.bar(x, vals, bottom=bottom, color=TYPO_COLORS[t], label=t.capitalize(), width=0.6)
        # Add percentage label
        for i, (v, b) in enumerate(zip(vals, bottom)):
            total_i = era_typo.loc[era_order[i]].sum()
            if v / total_i > 0.05:
                ax_b.text(i, b + v/2, f"{100*v/total_i:.0f}%",
                          ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        bottom += vals
    ax_b.set_xticks(x)
    ax_b.set_xticklabels([era_labels_short[e] for e in era_order], fontsize=9)
    ax_b.set_ylabel("Buildings")
    ax_b.set_title("B  Era × Typology (v3 ternary)", fontsize=11, fontweight="bold")
    ax_b.legend(loc="upper right", fontsize=8)

    # ── Panel C: GHSL height scatter coloured by ternary typology ─────────────
    ax_c = fig.add_subplot(gs[1, 0])
    for t in typo_order:
        sub = df[df["typology"] == t]
        ax_c.scatter(sub["height_proxy_m"], sub["ghsl_height_m"],
                     c=TYPO_COLORS[t], s=1.5, alpha=0.3, label=t.capitalize(), rasterized=True)
    ax_c.set_xlabel("height_proxy_m (OSM-derived, m)", fontsize=9)
    ax_c.set_ylabel("GHSL ANBH (m)", fontsize=9)
    ax_c.set_title("C  Height: OSM proxy vs GHSL ANBH\n(coloured by v3 typology)", fontsize=11, fontweight="bold")
    ax_c.axhline(18, color="grey", lw=0.8, ls="--", alpha=0.6, label="18 m / 36 m thresholds")
    ax_c.axhline(36, color="grey", lw=0.8, ls=":", alpha=0.6)
    ax_c.legend(markerscale=5, fontsize=8, loc="upper left")

    # ── Panel D: Recency score histogram ─────────────────────────────────────
    ax_d = fig.add_subplot(gs[1, 1])
    rs = df["recency_score"].values
    q_bounds = np.quantile(rs, [0, 0.40, 0.68, 1.0])
    ax_d.hist(rs, bins=80, color="#888888", alpha=0.6, edgecolor="none")
    era_cols = [ERA_COLORS["era1"], ERA_COLORS["era2"], ERA_COLORS["era3"]]
    span_labels = ["Era 1 (40%)", "Era 2 (28%)", "Era 3 (32%)"]
    for i in range(3):
        ax_d.axvspan(q_bounds[i], q_bounds[i+1], alpha=0.15, color=era_cols[i], label=span_labels[i])
    for b in q_bounds[1:3]:
        ax_d.axvline(b, color="black", lw=1, ls="--", alpha=0.5)
    ax_d.set_xlabel("recency_score", fontsize=9)
    ax_d.set_ylabel("Buildings")
    ax_d.set_title("D  recency_score distribution\n(era quantile boundaries shaded)", fontsize=11, fontweight="bold")
    ax_d.legend(fontsize=8)

    # ── Panel E: Spatial map — dominant typology per grid ────────────────────
    ax_e = fig.add_subplot(gs[2, 0])
    try:
        gdf_grid = gpd.read_file(GRID_PATH)
        gdf = gpd.read_file(GJSON_V3)[["id", "geometry", "typology", "grid_id"]]
        # Dominant typology per grid
        grid_typo = df.groupby("grid_id")["typology"].agg(
            lambda x: x.value_counts().index[0]).reset_index()
        gdf_grid = gdf_grid.merge(grid_typo, on="grid_id", how="left")
        for t, col in TYPO_COLORS.items():
            sub = gdf_grid[gdf_grid["typology"] == t]
            if len(sub):
                sub.plot(ax=ax_e, color=col, alpha=0.7, linewidth=0.2, edgecolor="white")
        patches = [mpatches.Patch(color=TYPO_COLORS[t], label=t.capitalize()) for t in typo_order]
        ax_e.legend(handles=patches, fontsize=8, loc="lower right")
    except Exception as exc:
        ax_e.text(0.5, 0.5, f"Map unavailable:\n{exc}", ha="center", va="center",
                  transform=ax_e.transAxes, fontsize=8)
    ax_e.set_axis_off()
    ax_e.set_title("E  Dominant typology per 500m grid cell", fontsize=11, fontweight="bold")

    # ── Panel F: v2 binary → v3 ternary transition heatmap ───────────────────
    ax_f = fig.add_subplot(gs[2, 1])
    cmp = df[["id", "typology"]].merge(
        df_v2[["id", "typology"]].rename(columns={"typology": "typology_v2"}), on="id", how="left")
    cm = pd.crosstab(cmp["typology_v2"], cmp["typology"])
    cm = cm.reindex(index=["midrise", "highrise"],
                    columns=["lowrise", "midrise", "highrise"], fill_value=0)
    im = ax_f.imshow(cm.values, cmap="Blues", aspect="auto")
    ax_f.set_xticks(range(len(cm.columns)))
    ax_f.set_yticks(range(len(cm.index)))
    ax_f.set_xticklabels([c.capitalize() for c in cm.columns], fontsize=9)
    ax_f.set_yticklabels([r.capitalize() for r in cm.index], fontsize=9)
    ax_f.set_xlabel("v3 ternary", fontsize=9)
    ax_f.set_ylabel("v2 binary", fontsize=9)
    ax_f.set_title("F  Typology reclassification v2 → v3", fontsize=11, fontweight="bold")
    total_cells = cm.values.sum()
    for i in range(len(cm.index)):
        for j in range(len(cm.columns)):
            v = cm.values[i, j]
            ax_f.text(j, i, f"{v:,}\n({100*v/total_cells:.0f}%)",
                      ha="center", va="center", fontsize=8,
                      color="white" if cm.values[i, j] > cm.values.max()*0.5 else "black")
    plt.colorbar(im, ax=ax_f, shrink=0.7)

    # ── Panel G: Classification rule pie ─────────────────────────────────────
    ax_g = fig.add_subplot(gs[3, :])
    rule_counts = s["rule_counts"]
    rule_labels_short = {
        "era1_prior": "Era-1 prior\n(h<30m → LowRise)",
        "large_footprint_shallow": "Large-footprint slab\n(fp>2500m², h<25m)",
        "ghsl_height_low": "GHSL ≤ 18m\n(LowRise)",
        "ghsl_height_mid": "GHSL 18–36m\n(MidRise)",
        "ghsl_height_high": "GHSL > 36m\n(HighRise)",
        "height_proxy_fallback": "Height-proxy fallback\n(GHSL = 0)",
    }
    rule_colors = {
        "era1_prior": ERA_COLORS["era1"],
        "large_footprint_shallow": "#7B68EE",
        "ghsl_height_low": TYPO_COLORS["lowrise"],
        "ghsl_height_mid": TYPO_COLORS["midrise"],
        "ghsl_height_high": TYPO_COLORS["highrise"],
        "height_proxy_fallback": "#AAAAAA",
    }
    labels_g = [rule_labels_short.get(r, r) for r in rule_counts.index]
    colors_g = [rule_colors.get(r, "#CCCCCC") for r in rule_counts.index]
    wedges_g, texts_g, autotexts_g = ax_g.pie(
        rule_counts.values,
        labels=labels_g,
        autopct=lambda p: f"{p:.1f}%\n({int(p/100*s['total']):,})",
        colors=colors_g,
        startangle=120,
        pctdistance=0.78,
        labeldistance=1.12,
    )
    for at in autotexts_g:
        at.set_fontsize(8)
    for t in texts_g:
        t.set_fontsize(9)
    ax_g.set_title("G  Classification rule breakdown (18,826 buildings)", fontsize=11, fontweight="bold")

    fig.suptitle(
        "Task 2 v3 — Ternary Typology Classification: LowRise / MidRise / HighRise\n"
        "Changsha urban core, 18,826 buildings  |  Era calibration 40/28/32",
        fontsize=13, fontweight="bold", y=1.01
    )
    fig.savefig(OUT_FIG, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Figure: {OUT_FIG.relative_to(ROOT)}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*60)
    print("Stage D v3: Validate ternary typology classification")
    print("="*60)

    df    = pd.read_csv(CSV_V3)
    df_v2 = pd.read_csv(CSV_V2)
    print(f"Loaded v3: {len(df):,} | v2 backup: {len(df_v2):,}")

    s = compute_stats(df, df_v2)
    write_md(s, df)
    make_figure(df, df_v2, s)
    print(f"\n✓ Validation complete.")
    print(f"  {OUT_MD.relative_to(ROOT)}")
    print(f"  {OUT_FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

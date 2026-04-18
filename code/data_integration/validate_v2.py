#!/usr/bin/env python3
"""
Stage D: Validate v2 calibrated classification.

Outputs:
  data/integrated/classification_validation_v2.md
  figure/fig03b_stock_classification_v2.png  (6-panel)
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
import matplotlib.colors as mcolors
from scipy import stats

ROOT     = Path(__file__).resolve().parents[2]
INT_DIR  = ROOT / "data" / "integrated"
FIG_DIR  = ROOT / "figure"

CSV_PATH  = INT_DIR / "classified_buildings.csv"
GJSON_PATH= INT_DIR / "classified_buildings.geojson"
GRID_PATH = ROOT / "data" / "from_paper1" / "grid_changsha_urban_core_solar_baseline.geojson"
V1_CSV    = INT_DIR / "classified_buildings_v1_ghs_age_only.csv"
OUT_MD    = INT_DIR / "classification_validation_v2.md"
OUT_FIG   = FIG_DIR / "fig03b_stock_classification_v2.png"

FIG_DIR.mkdir(exist_ok=True)

ERA_COLORS = {"era1": "#D85A30", "era2": "#2E75B6", "era3": "#1D9E75"}
ERA_LABELS = {"era1": "Era 1 (pre-2000)", "era2": "Era 2 (2000–2009)",
              "era3": "Era 3 (2010–2020)"}
TARGETS    = {"era1": 0.40, "era2": 0.28, "era3": 0.32}


# ── Stats ─────────────────────────────────────────────────────────────────────
def compute_stats(df: pd.DataFrame, df_v1: pd.DataFrame) -> dict:
    s = {"total": len(df)}
    for label, col in [("v2_final", "era_final"), ("v2_prov", "era_provisional")]:
        s[f"era_counts_{label}"] = df[col].value_counts().reindex(
            ["era1","era2","era3"], fill_value=0)
    s["era_counts_v1"] = df_v1["era"].value_counts().reindex(
        ["era1","era2","era3"], fill_value=0)
    s["typo_counts"] = df["typology"].value_counts()
    s["crosstab_era_typo"] = pd.crosstab(df["era_final"], df["typology"])
    s["cm_v1_v2"] = pd.crosstab(df_v1.set_index("id")["era"],
                                 df.set_index("id")["era_final"],
                                 rownames=["v1 (GHS-AGE)"],
                                 colnames=["v2 (calibrated)"])
    s["cm_prov_v2"] = pd.crosstab(df["era_provisional"], df["era_final"],
                                   rownames=["v2_provisional"], colnames=["v2_final"])
    n_rb2000 = df["likely_rebuilt_post2000"].sum()
    n_rb2010 = df["likely_rebuilt_post2010"].sum()
    s["n_rebuilt_2000"] = int(n_rb2000)
    s["n_rebuilt_2010"] = int(n_rb2010)
    # HP by era
    s["hp_by_era"] = df[df["is_high_potential"]==1].groupby("era_final").size().reindex(
        ["era1","era2","era3"], fill_value=0)
    # Floor area
    s["floor_area"] = df.groupby("era_final")["floor_area_m2"].sum() / 1e6
    # Height r (GHSL vs proxy)
    mask = df["ghsl_height_m"].notna() & (df["ghsl_height_m"] > 0) & df["height_proxy_m"].notna()
    if mask.sum() > 10:
        r, p = stats.pearsonr(df.loc[mask,"height_proxy_m"], df.loc[mask,"ghsl_height_m"])
        s["height_r"] = r; s["height_p"] = p; s["height_n"] = mask.sum()
        s["h_x"] = df.loc[mask,"height_proxy_m"].values
        s["h_y"] = df.loc[mask,"ghsl_height_m"].values
        s["h_era"] = df.loc[mask,"era_final"].values
    else:
        s["height_r"] = np.nan; s["height_n"] = mask.sum()
    # Sensitivity: alternate splits
    n = len(df)
    for split, proportions in [("50/25/25", (0.50,0.25,0.25)),
                                ("30/30/40", (0.30,0.30,0.40))]:
        n1,n2,n3 = [int(round(n*p)) for p in proportions]
        n3 = n - n1 - n2
        s[f"alt_{split}"] = {"era1": n1, "era2": n2, "era3": n3}
    # Top volume-growth buildings
    df_s = df.copy()
    df_s["v_abs_growth"] = df_s["v2020"] - df_s["v2000"]
    s["top10_growth"] = df_s.nlargest(10, "v_abs_growth")[
        ["id","era_final","v2000","v2020","v_abs_growth","recency_score"]]
    return s


def write_md(s: dict, df: pd.DataFrame):
    total = s["total"]
    lines = [
        "# Classification Validation Report — v2 (Calibrated)",
        "",
        f"**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}",
        f"**Method:** GHS-BUILT-V peak_growth_epoch + quantile calibration to 40/28/32 targets",
        "",
        "---",
        "",
        "## 1. Era Distribution — Before / After Comparison",
        "",
        "| Era | v1 (GHS-AGE) | v2 provisional (peak_growth) | v2 final (calibrated) | Target |",
        "|---|---|---|---|---|",
    ]
    for era in ["era1","era2","era3"]:
        n_v1   = s["era_counts_v1"].get(era,0)
        n_prov = s["era_counts_v2_prov"].get(era,0)
        n_fin  = s["era_counts_v2_final"].get(era,0)
        tgt_pct= int(TARGETS[era]*100)
        lines.append(f"| {ERA_LABELS[era]} "
                     f"| {n_v1:,} ({100*n_v1/total:.1f}%) "
                     f"| {n_prov:,} ({100*n_prov/total:.1f}%) "
                     f"| {n_fin:,} ({100*n_fin/total:.1f}%) "
                     f"| {tgt_pct}% |")

    lines += [
        "",
        "## 2. Era × Typology Crosstab (v2 final, GHSL-height typology)",
        "",
        "| Era | MidRise | HighRise | Total |",
        "|---|---|---|---|",
    ]
    ct = s["crosstab_era_typo"]
    for era in ["era1","era2","era3"]:
        mr = int(ct.get("midrise", pd.Series()).get(era, 0))
        hr = int(ct.get("highrise", pd.Series()).get(era, 0))
        flag = " ⚠" if era == "era1" and hr > 0.05 * total else ""
        lines.append(f"| {ERA_LABELS[era]} | {mr:,} | {hr:,} | {mr+hr:,}{flag} |")

    lines += [
        "",
        "## 3. Typology Distribution (v2 final)",
        "",
        "| Typology | Count | % |",
        "|---|---|---|",
    ]
    for t in ["midrise","highrise"]:
        n = s["typo_counts"].get(t, 0)
        lines.append(f"| {t.capitalize()} (GHSL ANBH {'≤' if t=='midrise' else '>'}18 m) "
                     f"| {n:,} | {100*n/total:.1f}% |")

    lines += [
        "",
        "## 4. Concordance — v1 vs v2 Final",
        "",
        "```",
    ]
    lines.append(s["cm_v1_v2"].to_string())
    lines += [
        "```",
        "",
        f"Buildings that **stayed** in same era: "
        f"{(s['cm_v1_v2'].values * np.eye(3, dtype=int)).sum():,}",
        "",
        "## 5. Concordance — v2 Provisional vs v2 Final",
        "",
        "```",
    ]
    lines.append(s["cm_prov_v2"].to_string())
    lines += ["```", ""]

    lines += [
        "## 6. Rebuild Detection Summary",
        "",
        f"- Buildings with >50% volume growth post-2000: "
        f"**{s['n_rebuilt_2000']:,}** ({100*s['n_rebuilt_2000']/total:.1f}%)",
        f"- Buildings with >50% volume growth post-2010: "
        f"**{s['n_rebuilt_2010']:,}** ({100*s['n_rebuilt_2010']/total:.1f}%)",
        f"- Buildings with v2020 > 3 × v2000: "
        f"**{(df['v2020'] > 3*df['v2000'].clip(lower=1)).sum():,}**",
        "",
        "**Top 10 buildings by absolute volume growth (v2000→v2020):**",
        "",
        s["top10_growth"].to_markdown(index=False),
        "",
        "## 7. HP Flag vs Era (v2 final)",
        "",
        "| Era | HP buildings | % of era | % of total HP |",
        "|---|---|---|---|",
    ]
    total_hp = s["hp_by_era"].sum()
    era_counts_fin = s["era_counts_v2_final"]
    for era in ["era1","era2","era3"]:
        n_era = era_counts_fin.get(era,0)
        n_hp  = int(s["hp_by_era"].get(era,0))
        p_era = 100*n_hp/n_era if n_era else 0
        p_tot = 100*n_hp/total_hp if total_hp else 0
        lines.append(f"| {ERA_LABELS[era]} | {n_hp:,} | {p_era:.1f}% | {p_tot:.1f}% |")

    lines += [
        "",
        "## 8. Floor Area by Era (v2 final)",
        "",
        "| Era | Floor area (Mm²) | % total |",
        "|---|---|---|",
    ]
    fa_total = s["floor_area"].sum()
    for era in ["era1","era2","era3"]:
        fa = s["floor_area"].get(era,0)
        lines.append(f"| {ERA_LABELS[era]} | {fa:.2f} | {100*fa/fa_total:.1f}% |")

    lines += [
        "",
        "## 9. Height Cross-Validation (height_proxy_m vs GHSL ANBH)",
        "",
        f"- Pearson r = **{s.get('height_r', np.nan):.3f}**"
        f" (n={s.get('height_n',0):,})",
        "",
        "## 10. Sensitivity — Alternate Era Splits",
        "",
        "| Scenario | Era 1 | Era 2 | Era 3 |",
        "|---|---|---|---|",
        f"| **Adopted (40/28/32)** | {era_counts_fin.get('era1',0):,} | "
        f"{era_counts_fin.get('era2',0):,} | {era_counts_fin.get('era3',0):,} |",
    ]
    for split in ["50/25/25","30/30/40"]:
        alt = s[f"alt_{split}"]
        lines.append(f"| Alt {split} | {alt['era1']:,} | {alt['era2']:,} | {alt['era3']:,} |")

    lines += [
        "",
        "## 11. Notes",
        "",
        "- Calibration uses recency_score quantile ranking; relative ordering is",
        "  satellite-derived (GHS-BUILT-V) but absolute proportions come from",
        "  Changsha land-use studies (Zhang et al. 2025, doi:10.1038/s41598-025-93689-9).",
        "- Typology now uses GHSL ANBH height (not OSM default), improving HighRise detection.",
        "- GHS-BUILT-V nodata (v=0 all epochs) treated as Era 1 (conservative assignment).",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✓ Report: {OUT_MD.relative_to(ROOT)}")


def make_figure(df: pd.DataFrame, df_v1: pd.DataFrame, s: dict):
    fig = plt.figure(figsize=(18, 14))
    gs  = fig.add_gridspec(3, 2, hspace=0.45, wspace=0.35)

    # ── Panel A: Side-by-side pie v1 vs v2_final ─────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    total = s["total"]
    era_order = ["era1","era2","era3"]
    colors    = [ERA_COLORS[e] for e in era_order]
    sizes_v1  = [s["era_counts_v1"].get(e,0) for e in era_order]
    sizes_v2  = [s["era_counts_v2_final"].get(e,0) for e in era_order]
    labs      = [f"{ERA_LABELS[e].split('(')[0].strip()}\n({100*n/total:.0f}%)"
                 for e, n in zip(era_order, sizes_v2)]
    # Donut-style: outer=v2, inner=v1
    w = dict(edgecolor="white", linewidth=1.5)
    ax_a.pie(sizes_v2, colors=colors, radius=1.0, wedgeprops={**w,"width":0.4},
             startangle=90)
    ax_a.pie(sizes_v1, colors=colors, radius=0.6, wedgeprops={**w,"width":0.4},
             startangle=90)
    ax_a.text(0, 0, "outer=v2\ninner=v1", ha="center", va="center", fontsize=7)
    patches = [mpatches.Patch(color=ERA_COLORS[e], label=ERA_LABELS[e]) for e in era_order]
    ax_a.legend(handles=patches, fontsize=7.5, loc="lower left",
                bbox_to_anchor=(-0.05, -0.15))
    ax_a.set_title("(A) Era distribution: v1 (inner) vs v2 (outer)",
                   fontweight="bold", fontsize=9.5)

    # ── Panel B: Era × typology stacked bar (v2_final) ───────────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    ct = s["crosstab_era_typo"]
    mr_v = [ct.get("midrise",pd.Series()).get(e,0) for e in era_order]
    hr_v = [ct.get("highrise",pd.Series()).get(e,0) for e in era_order]
    x = np.arange(3)
    ax_b.bar(x, mr_v, 0.5, color=colors, alpha=0.85, label="MidRise")
    ax_b.bar(x, hr_v, 0.5, bottom=mr_v, color=colors, alpha=0.5,
             hatch="///", label="HighRise")
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(["Era 1","Era 2","Era 3"], fontsize=9)
    ax_b.set_ylabel("Building count", fontsize=9)
    ax_b.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{int(v):,}"))
    ax_b.set_title("(B) Era × Typology (v2 final, GHSL height)",
                   fontweight="bold", fontsize=9.5)
    ax_b.legend(fontsize=8)
    for i,(mr,hr) in enumerate(zip(mr_v,hr_v)):
        if mr>100: ax_b.text(i,mr/2,f"{int(mr):,}",ha="center",va="center",
                              fontsize=7,color="white",fontweight="bold")
        if hr>100: ax_b.text(i,mr+hr/2,f"{int(hr):,}",ha="center",va="center",
                              fontsize=7,color="white",fontweight="bold")

    # ── Panel C: Height scatter ───────────────────────────────────────────────
    ax_c = fig.add_subplot(gs[1, 0])
    r = s.get("height_r", np.nan)
    if not np.isnan(r) and s["height_n"] > 10:
        for era in era_order:
            m = s["h_era"] == era
            ax_c.scatter(s["h_x"][m], s["h_y"][m], c=ERA_COLORS[era],
                         s=3, alpha=0.3, linewidths=0, label=ERA_LABELS[era])
        lim = max(s["h_x"].max(), s["h_y"].max()) * 1.05
        ax_c.plot([0,lim],[0,lim],"k--",lw=1.2,label="1:1")
        ax_c.set_xlim(0,lim); ax_c.set_ylim(0,lim)
        ax_c.set_xlabel("height_proxy_m (OSM default, m)", fontsize=8.5)
        ax_c.set_ylabel("GHSL ANBH (m)", fontsize=8.5)
        ax_c.legend(fontsize=7, markerscale=2)
        ax_c.set_title(f"(C) Height proxy vs GHSL ANBH  r={r:.3f}",
                       fontweight="bold", fontsize=9.5)
    else:
        ax_c.text(0.5,0.5,"No data",ha="center",va="center",transform=ax_c.transAxes)
        ax_c.set_title("(C) Height cross-validation", fontweight="bold", fontsize=9.5)

    # ── Panel D: Recency score histogram with era boundaries ─────────────────
    ax_d = fig.add_subplot(gs[1, 1])
    rs = df["recency_score"].values
    bounds = np.quantile(rs, [0, TARGETS["era1"], TARGETS["era1"]+TARGETS["era2"], 1.0])
    ax_d.hist(rs, bins=80, color="#888888", alpha=0.7, edgecolor="none")
    era_cols_list = [ERA_COLORS["era1"], ERA_COLORS["era2"], ERA_COLORS["era3"]]
    labels_d = ["Era 1 boundary", "Era 2 boundary"]
    for i, b in enumerate(bounds[1:3]):
        ax_d.axvline(b, color=era_cols_list[i+1], lw=2, linestyle="--",
                     label=f"{labels_d[i]}  ({b:.2f})")
    ax_d.set_xlabel("Recency score (higher = more recent)", fontsize=8.5)
    ax_d.set_ylabel("Building count", fontsize=8.5)
    ax_d.set_title("(D) Recency score distribution with era boundaries",
                   fontweight="bold", fontsize=9.5)
    ax_d.legend(fontsize=7.5)
    ax_d.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{int(v):,}"))
    # Shade era regions
    ax_d.axvspan(rs.min(), bounds[1], alpha=0.08, color=ERA_COLORS["era1"])
    ax_d.axvspan(bounds[1], bounds[2], alpha=0.08, color=ERA_COLORS["era2"])
    ax_d.axvspan(bounds[2], rs.max(), alpha=0.08, color=ERA_COLORS["era3"])

    # ── Panel E: Spatial map of dominant era per 500m grid ───────────────────
    ax_e = fig.add_subplot(gs[2, 0])
    try:
        grid = gpd.read_file(GRID_PATH)
        era_by_grid = df.groupby("grid_id")["era_final"].agg(
            lambda x: x.value_counts().index[0])
        grid["dominant_era"] = grid["grid_id"].map(era_by_grid)
        grid_valid = grid[grid["dominant_era"].notna()].copy()

        cmap_vals = {"era1": 0, "era2": 0.5, "era3": 1.0}
        grid_valid["_cv"] = grid_valid["dominant_era"].map(cmap_vals)
        from matplotlib.colors import ListedColormap
        era_cmap = ListedColormap([ERA_COLORS["era1"], ERA_COLORS["era2"], ERA_COLORS["era3"]])
        grid_valid.plot(column="_cv", ax=ax_e, cmap=era_cmap, vmin=0, vmax=1,
                        linewidth=0.1, edgecolor="white", alpha=0.85)
        for era in era_order:
            ax_e.add_patch(mpatches.Patch(color=ERA_COLORS[era], label=ERA_LABELS[era], alpha=0.85))
        ax_e.legend(fontsize=7.5, loc="lower right")
        ax_e.set_xlabel("Longitude (°E)", fontsize=8); ax_e.set_ylabel("Latitude (°N)", fontsize=8)
        ax_e.tick_params(labelsize=7)
        ax_e.set_title("(E) Dominant era per 500m grid (v2 final)",
                       fontweight="bold", fontsize=9.5)
    except Exception as ex:
        ax_e.text(0.5,0.5,f"Map unavailable:\n{ex}",ha="center",va="center",
                  transform=ax_e.transAxes, fontsize=8)
        ax_e.set_title("(E) Spatial map", fontweight="bold", fontsize=9.5)

    # ── Panel F: Flow chart v1 → v2_final (confusion matrix as heatmap) ──────
    ax_f = fig.add_subplot(gs[2, 1])
    cm = s["cm_v1_v2"].reindex(index=era_order, columns=era_order, fill_value=0)
    # Normalise by v1 row total
    cm_norm = cm.div(cm.sum(axis=1), axis=0) * 100
    im = ax_f.imshow(cm_norm.values, cmap="Blues", vmin=0, vmax=100, aspect="auto")
    ax_f.set_xticks([0,1,2])
    ax_f.set_yticks([0,1,2])
    ax_f.set_xticklabels(["→Era1","→Era2","→Era3"], fontsize=8.5)
    ax_f.set_yticklabels(["v1 Era1","v1 Era2","v1 Era3"], fontsize=8.5)
    ax_f.set_title("(F) Era reassignment: v1 → v2  (% of v1 row)",
                   fontweight="bold", fontsize=9.5)
    for i in range(3):
        for j in range(3):
            val_pct = cm_norm.values[i,j]
            val_n   = int(cm.values[i,j])
            col = "white" if val_pct > 60 else "black"
            ax_f.text(j,i,f"{val_pct:.0f}%\n({val_n:,})",ha="center",va="center",
                      fontsize=7.5, color=col)
    plt.colorbar(im, ax=ax_f, fraction=0.04, label="%")

    fig.suptitle("Building Stock Classification — v2 Calibrated (40/28/32)\nChangsha Urban Core, 18,855 buildings",
                 fontsize=12, fontweight="bold", y=0.995)
    fig.savefig(OUT_FIG, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Figure: {OUT_FIG.relative_to(ROOT)}")


def main():
    print("\n" + "="*60)
    print("Stage D: Validate v2 calibrated classification")
    print("="*60)

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Missing: {CSV_PATH}. Run calibrate_and_finalize.py first.")
    if not V1_CSV.exists():
        raise FileNotFoundError(f"Missing v1 CSV: {V1_CSV}")

    df    = pd.read_csv(CSV_PATH)
    df_v1 = pd.read_csv(V1_CSV).drop_duplicates(subset="id", keep="first")
    print(f"Loaded v2: {len(df):,} | v1 (deduped): {len(df_v1):,}")

    s = compute_stats(df, df_v1)
    write_md(s, df)
    make_figure(df, df_v1, s)
    print(f"\n✓ Validation complete.")
    print(f"  {OUT_MD.relative_to(ROOT)}")
    print(f"  {OUT_FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

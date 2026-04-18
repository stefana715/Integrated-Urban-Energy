#!/usr/bin/env python3
"""
Step 3: Validate and visualise the building era + typology classification.

Outputs:
  data/integrated/classification_validation.md  — statistics report
  figure/fig03_stock_classification.png          — 4-panel figure

Panel A: Pie chart — building count by era
Panel B: Stacked bar — building count by era × typology
Panel C: Scatter — height_proxy_m vs ghsl_height_m, coloured by era, 1:1 line
Panel D: Spatial density hex-map of building centroids coloured by era
         (or district bar chart if GADM is available)
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
from scipy import stats

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parents[2]
CSV_PATH  = ROOT / "data" / "integrated" / "classified_buildings.csv"
GJSON_PATH= ROOT / "data" / "integrated" / "classified_buildings.geojson"
GADM_PATH = ROOT / "data" / "auxiliary_rasters" / "gadm" / "gadm41_CHN.gpkg"
OUT_MD    = ROOT / "data" / "integrated" / "classification_validation.md"
OUT_FIG   = ROOT / "figure" / "fig03_stock_classification.png"

# ── Colour scheme ─────────────────────────────────────────────────────────────
ERA_COLORS = {"era1": "#D85A30", "era2": "#2E75B6", "era3": "#1D9E75"}
ERA_LABELS = {"era1": "Era 1 (pre-2000)", "era2": "Era 2 (2000–2009)", "era3": "Era 3 (2010–2020)"}
TYPO_HATCHES = {"midrise": "", "highrise": "///"}

(ROOT / "figure").mkdir(exist_ok=True)
(ROOT / "data" / "integrated").mkdir(exist_ok=True)


def load_data():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded CSV: {len(df):,} buildings, columns: {list(df.columns)}")
    return df


def compute_stats(df: pd.DataFrame) -> dict:
    total = len(df)
    stats_dict = {"total": total}

    # Era distribution
    era_counts = df["era"].value_counts().reindex(["era1", "era2", "era3"], fill_value=0)
    stats_dict["era_counts"] = era_counts

    # Typology distribution
    typo_counts = df["typology"].value_counts()
    stats_dict["typo_counts"] = typo_counts

    # Era × typology
    ct = pd.crosstab(df["era"], df["typology"])
    stats_dict["crosstab"] = ct

    # Era source
    src_counts = df["era_source"].value_counts()
    stats_dict["era_source"] = src_counts

    # High-potential per era
    hp_by_era = df.groupby("era")["is_high_potential"].sum().reindex(
        ["era1", "era2", "era3"], fill_value=0
    )
    stats_dict["hp_by_era"] = hp_by_era

    # GHS-AGE epoch distribution
    epoch_counts = df["ghs_age_epoch_label"].value_counts()
    stats_dict["epoch_counts"] = epoch_counts

    # Height cross-validation
    mask = df["ghsl_height_m"].notna() & df["height_proxy_m"].notna()
    mask &= (df["ghsl_height_m"] > 0) & (df["height_proxy_m"] > 0)
    if mask.sum() > 10:
        x = df.loc[mask, "height_proxy_m"].values
        y = df.loc[mask, "ghsl_height_m"].values
        r, p = stats.pearsonr(x, y)
        stats_dict["height_r"] = r
        stats_dict["height_p"] = p
        stats_dict["height_n"] = mask.sum()
        stats_dict["height_x"] = x
        stats_dict["height_y"] = y
        stats_dict["height_mask_era"] = df.loc[mask, "era"].values
    else:
        stats_dict["height_r"] = np.nan
        stats_dict["height_n"] = mask.sum()

    # Floor area by era
    stats_dict["floor_area_by_era"] = df.groupby("era")["floor_area_m2"].sum() / 1e6  # million m²

    # Grid coverage
    n_grids = df["grid_id"].nunique()
    stats_dict["n_grids"] = n_grids

    return stats_dict


def write_md(stats_dict: dict, df: pd.DataFrame) -> None:
    total = stats_dict["total"]
    era_counts = stats_dict["era_counts"]
    typo_counts = stats_dict["typo_counts"]
    ct = stats_dict["crosstab"]
    src = stats_dict["era_source"]
    hp = stats_dict["hp_by_era"]
    fa = stats_dict["floor_area_by_era"]

    lines = [
        "# Classification Validation Report",
        "",
        f"**Date generated:** {pd.Timestamp.now().strftime('%Y-%m-%d')}",
        f"**Input:** `data/from_paper1/buildings_changsha_urban_core_solar_baseline.geojson`",
        f"**Era source:** GHS-AGE R2025A 100m (10-year epochs 1980–2020) with height-proxy fallback",
        "",
        "---",
        "",
        "## 1. Era Distribution",
        "",
        f"Total buildings: **{total:,}**",
        "",
        "| Era | Count | % total | Total floor area (M m²) |",
        "|---|---|---|---|",
    ]
    for era in ["era1", "era2", "era3"]:
        n = era_counts.get(era, 0)
        fa_val = fa.get(era, 0)
        lines.append(f"| {ERA_LABELS[era]} | {n:,} | {100*n/total:.1f}% | {fa_val:.1f} |")
    lines += [
        "",
        "## 2. Typology Distribution",
        "",
        "| Typology | Count | % total |",
        "|---|---|---|",
    ]
    for typ in ["midrise", "highrise"]:
        n = typo_counts.get(typ, 0)
        lines.append(f"| {typ.capitalize()} (height_proxy {'≤' if typ=='midrise' else '>'}18 m) | {n:,} | {100*n/total:.1f}% |")

    lines += [
        "",
        "## 3. Era × Typology Crosstab",
        "",
        "| Era | MidRise | HighRise | Total |",
        "|---|---|---|---|",
    ]
    for era in ["era1", "era2", "era3"]:
        mr = ct.get("midrise", pd.Series()).get(era, 0)
        hr = ct.get("highrise", pd.Series()).get(era, 0)
        lines.append(f"| {ERA_LABELS[era]} | {int(mr):,} | {int(hr):,} | {int(mr+hr):,} |")

    lines += [
        "",
        "## 4. Era Source Breakdown",
        "",
        "| Source | Count | % total |",
        "|---|---|---|",
    ]
    for src_name, n in src.items():
        lines.append(f"| {src_name} | {n:,} | {100*n/total:.1f}% |")

    lines += [
        "",
        "## 5. GHS-AGE Epoch Distribution",
        "",
        "| Epoch label | Count | % total | → Era |",
        "|---|---|---|---|",
    ]
    epoch_to_era = {
        "pre-1980": "Era 1", "1980-1989": "Era 1", "1990-1999": "Era 1",
        "2000-2009": "Era 2", "2010-2020": "Era 3", "nodata": "height fallback",
    }
    for ep_label, cnt in stats_dict["epoch_counts"].sort_index().items():
        era_lab = epoch_to_era.get(ep_label, "—")
        lines.append(f"| {ep_label} | {int(cnt):,} | {100*cnt/total:.1f}% | {era_lab} |")

    lines += [
        "",
        "## 6. High-Potential Building Distribution by Era",
        "",
        "| Era | HP buildings | % of era | % of total HP |",
        "|---|---|---|---|",
    ]
    total_hp = hp.sum()
    for era in ["era1", "era2", "era3"]:
        n_era = era_counts.get(era, 0)
        n_hp = int(hp.get(era, 0))
        pct_era = 100 * n_hp / n_era if n_era > 0 else 0
        pct_total = 100 * n_hp / total_hp if total_hp > 0 else 0
        lines.append(f"| {ERA_LABELS[era]} | {n_hp:,} | {pct_era:.1f}% | {pct_total:.1f}% |")

    lines += [
        "",
        "## 7. Height Cross-Validation (height_proxy_m vs GHSL ANBH)",
        "",
    ]
    r = stats_dict.get("height_r", np.nan)
    n_h = stats_dict.get("height_n", 0)
    if not np.isnan(r):
        lines.append(f"- Pearson r = **{r:.3f}** (n={n_h:,} buildings with valid GHSL height)")
        lines.append(f"- p-value: {stats_dict['height_p']:.2e}")
        lines.append("")
        if r > 0.7:
            lines.append("✓ Strong positive correlation — height_proxy_m is a reliable proxy.")
        elif r > 0.4:
            lines.append("⚠ Moderate correlation — some divergence expected (OSM vs GHSL 2018).")
        else:
            lines.append("⚠ Weak correlation — review height_proxy_m assumptions.")
    else:
        lines.append(f"- Too few buildings with valid GHSL height for correlation ({n_h}).")

    lines += [
        "",
        "## 8. Spatial Coverage",
        "",
        f"- Buildings assigned to a grid cell: {df['grid_id'].notna().sum():,} / {total:,}",
        f"- Unique grid cells with ≥1 building: {stats_dict['n_grids']}",
        "",
        "## 9. Notes and Caveats",
        "",
        "- OSM `start_date` tag coverage: **0%** — era assignment relies entirely on GHS-AGE.",
        "- GHS-AGE captures dominant epoch of 100 m grid cell; single-building resolution",
        "  is approximate when multiple construction epochs overlap in one cell.",
        "- Height fallback rule (>30 m→era3, 15–30 m→era2, else era1) applied to buildings",
        "  in cells with no GHS-AGE built-up signal.",
        "- Typology threshold: 18 m (6 floors × 3 m/floor) per DEC-002.",
    ]

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✓ Validation report: {OUT_MD.relative_to(ROOT)}")


def make_figure(df: pd.DataFrame, stats_dict: dict) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    fig.suptitle(
        "Building Stock Classification — Changsha Urban Core (18,855 buildings)",
        fontsize=13, fontweight="bold", y=0.98,
    )
    (ax_a, ax_b), (ax_c, ax_d) = axes

    era_counts = stats_dict["era_counts"]
    total = stats_dict["total"]

    # ── Panel A: Pie chart ────────────────────────────────────────────────────
    labels = [ERA_LABELS[e] for e in ["era1", "era2", "era3"]]
    sizes  = [era_counts.get(e, 0) for e in ["era1", "era2", "era3"]]
    colors = [ERA_COLORS[e] for e in ["era1", "era2", "era3"]]
    wedge_props = {"edgecolor": "white", "linewidth": 1.5}
    ax_a.pie(
        sizes, labels=labels, colors=colors,
        autopct=lambda p: f"{p:.1f}%\n({int(round(p*total/100)):,})",
        startangle=90, wedgeprops=wedge_props,
        textprops={"fontsize": 8.5},
    )
    ax_a.set_title("(A) Building count by era", fontweight="bold", fontsize=10)

    # ── Panel B: Stacked bar — era × typology ─────────────────────────────────
    ct = stats_dict["crosstab"]
    era_order = ["era1", "era2", "era3"]
    mr_vals = [ct.get("midrise",  pd.Series()).get(e, 0) for e in era_order]
    hr_vals = [ct.get("highrise", pd.Series()).get(e, 0) for e in era_order]

    x = np.arange(3)
    w = 0.55
    bars_mr = ax_b.bar(x, mr_vals, w, color=[ERA_COLORS[e] for e in era_order],
                       label="MidRise (≤18 m)", alpha=0.85)
    bars_hr = ax_b.bar(x, hr_vals, w, bottom=mr_vals,
                       color=[ERA_COLORS[e] for e in era_order],
                       hatch="///", alpha=0.55, label="HighRise (>18 m)")
    ax_b.set_xticks(x)
    ax_b.set_xticklabels([ERA_LABELS[e].split(" (")[0] for e in era_order], fontsize=9)
    ax_b.set_ylabel("Building count", fontsize=9)
    ax_b.set_title("(B) Building count by era × typology", fontweight="bold", fontsize=10)
    ax_b.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}"))
    # Add value labels
    for i, (mr, hr) in enumerate(zip(mr_vals, hr_vals)):
        if mr > 50:
            ax_b.text(i, mr/2, f"{int(mr):,}", ha="center", va="center",
                      fontsize=7.5, color="white", fontweight="bold")
        if hr > 50:
            ax_b.text(i, mr + hr/2, f"{int(hr):,}", ha="center", va="center",
                      fontsize=7.5, color="white", fontweight="bold")
    ax_b.legend(fontsize=8, loc="upper right")

    # ── Panel C: Height scatter ───────────────────────────────────────────────
    r = stats_dict.get("height_r", np.nan)
    if not np.isnan(r) and stats_dict["height_n"] > 10:
        x_h = stats_dict["height_x"]
        y_h = stats_dict["height_y"]
        era_h = stats_dict["height_mask_era"]
        for era in ["era1", "era2", "era3"]:
            m = era_h == era
            ax_c.scatter(x_h[m], y_h[m], c=ERA_COLORS[era], s=4, alpha=0.35,
                         label=ERA_LABELS[era], linewidths=0)
        lim_max = max(x_h.max(), y_h.max()) * 1.05
        ax_c.plot([0, lim_max], [0, lim_max], "k--", lw=1.2, label="1:1 line")
        ax_c.set_xlabel("Paper 1 height_proxy_m (m)", fontsize=9)
        ax_c.set_ylabel("GHSL ANBH height (m)", fontsize=9)
        ax_c.set_title(
            f"(C) Height proxy vs GHSL ANBH  |  r = {r:.3f}  (n={stats_dict['height_n']:,})",
            fontweight="bold", fontsize=10,
        )
        ax_c.legend(fontsize=7.5, markerscale=2, loc="upper left")
        ax_c.set_xlim(0, lim_max)
        ax_c.set_ylim(0, lim_max)
    else:
        ax_c.text(0.5, 0.5, "Insufficient GHSL height data\n(all buildings have 0 or nodata)",
                  ha="center", va="center", transform=ax_c.transAxes, fontsize=10)
        ax_c.set_title("(C) Height cross-validation", fontweight="bold", fontsize=10)

    # ── Panel D: Spatial density map ─────────────────────────────────────────
    # Try to use GADM for district outlines; else plain scatter
    gadm_available = GADM_PATH.exists()
    gdf_geo = None
    try:
        gdf_full = gpd.read_file(GJSON_PATH)
        gdf_full = gdf_full.set_crs("EPSG:4326", allow_override=True)
        gdf_geo = gdf_full
    except Exception:
        pass

    if gdf_geo is not None:
        centroids = gdf_geo.geometry.centroid
        gdf_geo = gdf_geo.copy()
        gdf_geo["cx"] = centroids.x
        gdf_geo["cy"] = centroids.y

        if gadm_available:
            try:
                gadm = gpd.read_file(GADM_PATH, layer="ADM_ADM_3")
                changsha = gadm[gadm["NAME_2"].str.contains("Changsha", na=False)]
                if len(changsha) == 0:
                    changsha = gadm[gadm["VARNAME_2"].str.contains("Changsha", na=False)]
                changsha.boundary.plot(ax=ax_d, color="gray", linewidth=0.5, zorder=1)
            except Exception as e:
                print(f"  ⚠ GADM district outlines failed ({e}); using plain scatter")

        for era in ["era1", "era2", "era3"]:
            sub = gdf_geo[gdf_geo["era"] == era]
            ax_d.scatter(sub["cx"], sub["cy"], c=ERA_COLORS[era],
                         s=1.2, alpha=0.3, linewidths=0, label=ERA_LABELS[era])

        ax_d.set_xlabel("Longitude (°E)", fontsize=9)
        ax_d.set_ylabel("Latitude (°N)", fontsize=9)
        ax_d.set_title("(D) Spatial distribution of building eras", fontweight="bold", fontsize=10)
        legend_handles = [
            mpatches.Patch(color=ERA_COLORS[e], label=ERA_LABELS[e])
            for e in ["era1", "era2", "era3"]
        ]
        ax_d.legend(handles=legend_handles, fontsize=7.5, loc="lower right")
        ax_d.tick_params(labelsize=7.5)
    else:
        ax_d.text(0.5, 0.5, "GeoJSON not available for spatial plot",
                  ha="center", va="center", transform=ax_d.transAxes)
        ax_d.set_title("(D) Spatial distribution", fontweight="bold", fontsize=10)

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUT_FIG, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Figure saved: {OUT_FIG.relative_to(ROOT)}")


def main():
    print("\n" + "=" * 60)
    print("Step 3: Validate building era classification")
    print("=" * 60)

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Classified buildings CSV not found: {CSV_PATH}\n"
            "Run classify_era.py first."
        )

    df = load_data()
    stats_dict = compute_stats(df)

    print("\nWriting validation report …")
    write_md(stats_dict, df)

    print("Generating figure …")
    make_figure(df, stats_dict)

    print("\n✓ Validation complete.")
    print(f"  Report:  {OUT_MD.relative_to(ROOT)}")
    print(f"  Figure:  {OUT_FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

"""
generate_all_figures.py — Regenerate all 14 publication-quality figures for Paper 3.

Usage:
    python code/postprocessing/generate_all_figures.py

Outputs saved to figure/ (creates directory if missing).
Contact sheet saved to figure/all_figures_contact.png.
"""

import os
import sys

# Make project root importable
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POSTPROC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, POSTPROC_DIR)

import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")   # force non-interactive backend before pyplot import

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from matplotlib.colors import Normalize, LogNorm
from matplotlib.cm import ScalarMappable
import matplotlib.ticker as ticker

# Load unified style
from style import (
    apply_style, savefig,
    FIGSIZE_SINGLE, FIGSIZE_WIDE, FIGSIZE_MAP, FIGSIZE_TALL, FIGSIZE_FLOW,
    ERA_COLORS, ERA_LABELS, TYPOLOGY_COLORS,
    RETROFIT_COLORS, SCENARIO_ORDER, SCENARIO_LABELS, SCENARIO_COLORS,
    HEATING_COLOR, COOLING_COLOR, OTHER_COLOR, PV_COLOR, NET_COLOR,
    CARBON_BASELINE_COLOR, CARBON_R5PV_COLOR, CARBON_STEP_COLOR, CARBON_SSP585_COLOR,
    GRID_FACE_COLOR, HIGHLIGHT_COLOR,
    FONT_SIZE_BASE, FONT_SIZE_LABEL, FONT_SIZE_TITLE, FONT_SIZE_LEGEND,
    FONT_SIZE_ANNOT, DPI_PRINT, label_bar, despine,
)

apply_style()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
FIG_DIR  = os.path.join(ROOT, "figure")
DATA_INT = os.path.join(ROOT, "data", "integrated")
DATA_P1  = os.path.join(ROOT, "data", "from_paper1")
os.makedirs(FIG_DIR, exist_ok=True)

def p1(f): return os.path.join(DATA_P1, f)
def di(f): return os.path.join(DATA_INT, f)

# ---------------------------------------------------------------------------
# Lazy-load shared data (cached once)
# ---------------------------------------------------------------------------
_cache = {}

def load(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]

def get_buildings():
    return load("bld", lambda: gpd.read_file(
        os.path.join(ROOT, "data", "integrated", "classified_buildings.geojson")))

def get_grid_geo():
    return load("grid_geo", lambda: gpd.read_file(p1("grid_changsha_urban_core_solar_baseline.geojson")))

def get_study_area():
    return load("sa", lambda: gpd.read_file(p1("study_area_changsha_urban_core.geojson")))

def get_grid_ranking():
    return load("grank", lambda: pd.read_csv(di("integrated_grid_ranking.csv")))

def get_baseline_era():
    return load("bera", lambda: pd.read_csv(di("baseline_by_era.csv")))

def get_retrofit_totals():
    return load("rtot", lambda: pd.read_csv(di("retrofit_city_totals.csv")))

def get_retrofit_era():
    return load("rera", lambda: pd.read_csv(di("retrofit_by_era.csv")))

def get_monthly():
    return load("month", lambda: pd.read_csv(di("monthly_supply_demand.csv")))

def get_climate():
    return load("clim", lambda: pd.read_csv(di("climate_city_results.csv")))

def get_carbon_ann():
    return load("cann", lambda: pd.read_csv(di("carbon_annual_scenarios.csv")))

def get_carbon_cum():
    return load("ccum", lambda: pd.read_csv(di("carbon_cumulative_pathways.csv")))

def get_carbon_era():
    return load("cera", lambda: pd.read_csv(di("carbon_by_era.csv")))

def get_carbon_grid():
    return load("cgrid", lambda: pd.read_csv(di("carbon_by_grid.csv")))

def get_climate_factors():
    return load("cfact", lambda: pd.read_csv(di("climate_factors.csv")))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def _add_north_arrow(ax, x=0.95, y=0.92, size=0.04):
    ax.annotate("N", xy=(x, y), xycoords="axes fraction",
                fontsize=FONT_SIZE_ANNOT + 1, fontweight="bold",
                ha="center", va="bottom")
    ax.annotate("", xy=(x, y + size), xytext=(x, y - size),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.2))

def _add_scalebar_km(ax, km=5, lon0=112.855, lat0=28.108):
    """Approximate scale bar in geographic coords (EPSG:4326)."""
    deg_per_km = 1 / 111.0  # rough
    dx = km * deg_per_km
    ax.plot([lon0, lon0 + dx], [lat0, lat0], color="black", lw=2, transform=ax.transData)
    ax.text(lon0 + dx / 2, lat0 - 0.005, f"{km} km",
            ha="center", va="top", fontsize=FONT_SIZE_ANNOT - 1, transform=ax.transData)

# Simplified mainland China boundary polygon (WGS84, ~25 vertices)
# Hardcoded to avoid external data dependency; sufficient for geographic context inset.
_CHINA_COORDS = [
    (73.5, 39.5), (80.2, 35.5), (78.0, 26.5), (82.5, 27.9), (89.5, 27.5),
    (97.3, 24.7), (100.2, 21.5), (104.0, 22.5), (108.1, 21.5), (110.2, 21.0),
    (113.5, 22.2), (117.4, 23.5), (120.5, 27.5), (121.9, 30.9), (121.5, 37.4),
    (122.0, 41.8), (130.6, 42.4), (134.8, 48.4), (126.0, 53.3), (119.0, 53.5),
    (109.5, 53.3), (100.0, 42.0), (89.5, 48.0), (80.7, 43.2), (73.5, 39.5),
]

# ===========================================================================
# FIG 01 — Study area map (buildings coloured by era) — single panel + inset
# ===========================================================================

def fig01_study_area():
    bld = get_buildings()
    sa  = get_study_area()

    fig, ax = plt.subplots(1, 1, figsize=(10.0, 8.0))

    # ---- Main map: building footprints coloured by era -------------------
    era_map = {"era1": ERA_COLORS["era1"], "era2": ERA_COLORS["era2"], "era3": ERA_COLORS["era3"]}
    colors = bld["era_final"].map(era_map).fillna("#CCCCCC")

    bld.plot(ax=ax, color=colors.values, linewidth=0, markersize=0.2, zorder=2)
    sa.boundary.plot(ax=ax, color="black", linewidth=1.0, zorder=3)

    # legend bottom-left
    patches = [mpatches.Patch(facecolor=v, label=ERA_LABELS[k]) for k, v in era_map.items()]
    ax.legend(handles=patches, loc="lower left", fontsize=FONT_SIZE_LEGEND + 1,
              framealpha=0.9, edgecolor="gray", title="Construction era",
              title_fontsize=FONT_SIZE_LEGEND)

    ax.set_xlabel("Longitude (°E)", fontsize=FONT_SIZE_LABEL + 1)
    ax.set_ylabel("Latitude (°N)", fontsize=FONT_SIZE_LABEL + 1)
    ax.tick_params(labelsize=FONT_SIZE_BASE)
    _add_north_arrow(ax, x=0.96, y=0.93)
    _add_scalebar_km(ax, km=3, lon0=113.015, lat0=28.104)

    ax.set_title(
        "Study area: Changsha urban residential core\n"
        "18,826 buildings · 671 occupied 500-m grid cells · Hunan Province, China",
        fontsize=FONT_SIZE_TITLE + 1, fontweight="bold", pad=8)

    # ---- China context inset (top-right, axes-fraction coords) ----------
    from matplotlib.patches import Polygon as MplPolygon
    # [x0, y0, width, height] in axes fraction (0-1)
    ax_in = ax.inset_axes([0.72, 0.68, 0.26, 0.30])
    china_patch = MplPolygon(_CHINA_COORDS, closed=True,
                             facecolor="#DDDDDD", edgecolor="#888888", linewidth=0.5)
    ax_in.add_patch(china_patch)
    ax_in.plot(112.93, 28.23, "o", color="#D94F3D", markersize=5, zorder=5)
    ax_in.text(112.93, 26.8, "Changsha", ha="center", va="top",
               fontsize=FONT_SIZE_ANNOT - 1, color="#D94F3D", fontweight="bold")
    ax_in.set_xlim(72, 137)
    ax_in.set_ylim(17, 55)
    ax_in.set_aspect("auto")
    ax_in.set_xticks([]); ax_in.set_yticks([])
    for spine in ax_in.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.8)
        spine.set_edgecolor("black")
    ax_in.patch.set_facecolor("white")

    fig.subplots_adjust(left=0.08, right=0.97, bottom=0.07, top=0.91)
    out = os.path.join(FIG_DIR, "fig01_study_area.png")
    fig.savefig(out, dpi=DPI_PRINT)
    plt.close(fig)
    return out


# ===========================================================================
# FIG 02 — Methodology flowchart (3-section vertical layout)
# ===========================================================================

def fig02_methodology_flowchart():
    fig, ax = plt.subplots(figsize=(9.0, 6.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    def box(ax, x, y, w, h, text, fc="#EFF3FF", ec="#4393C3",
            fs=FONT_SIZE_ANNOT, bold=False):
        rect = mpatches.FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.12",
            facecolor=fc, edgecolor=ec, linewidth=0.9, zorder=2)
        ax.add_patch(rect)
        ax.text(x, y, text, ha="center", va="center", fontsize=fs,
                fontweight="bold" if bold else "normal",
                multialignment="center", zorder=3)

    def arrow(ax, x0, y0, x1, y1, lw=1.2):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color="#444444", lw=lw))

    def section_label(ax, y, text):
        ax.text(-0.3, y, text, ha="left", va="center",
                fontsize=FONT_SIZE_ANNOT - 1, color="#888888",
                rotation=90, transform=ax.transData)

    # ── Section 1: INPUT DATA (y=8.5–9.5) ─────────────────────────────────
    ax.text(5.0, 9.85, "① Input data", ha="center", va="center",
            fontsize=FONT_SIZE_ANNOT, color="#888888", style="italic")
    box(ax, 2.5, 9.1, 4.0, 1.0,
        "Paper 1 — OSM Solar Screening\n18,826 buildings  |  1,764 GWh PV potential",
        fc="#FFF5EB", ec=ERA_COLORS["era1"], fs=FONT_SIZE_ANNOT, bold=False)
    box(ax, 7.5, 9.1, 4.0, 1.0,
        "Paper 2 — EnergyPlus Archetypes\n3 eras × 5 retrofit measures × 5 climate scenarios",
        fc="#EFF3FF", ec=ERA_COLORS["era3"], fs=FONT_SIZE_ANNOT, bold=False)

    # ── Section 2: ANALYSIS (y=2.5–8.0) ──────────────────────────────────
    ax.text(5.0, 8.0, "② Analysis", ha="center", va="center",
            fontsize=FONT_SIZE_ANNOT, color="#888888", style="italic")

    # Row A: T1-T2 integration
    box(ax, 5.0, 7.3, 5.5, 0.85,
        "T1–T2: Building stock integration & classification\n"
        "v5: 18,826 buildings  |  Era 1/2/3: 40/38/22%  |  72.05 Mm² floor area",
        fc="#F7F7F7", ec="#666666", fs=FONT_SIZE_ANNOT, bold=True)
    arrow(ax, 2.5, 8.6, 3.8, 7.75)
    arrow(ax, 7.5, 8.6, 6.2, 7.75)

    # Row B: T3–T5
    arrow(ax, 5.0, 6.88, 5.0, 6.55)
    row_b = [(2.0, "T3: City-scale\nbaseline\n15,382 GWh/yr"),
             (5.0, "T4: R5 retrofit\nsavings\n−36.6% | 5,634 GWh"),
             (8.0, "T5: PV supply-\ndemand match\n1,603 GWh HP PV")]
    for x, lab in row_b:
        box(ax, x, 6.0, 2.7, 1.0, lab, fc="#FFFFD4", ec="#AA8800", fs=FONT_SIZE_ANNOT - 1)
        if x != 5.0:
            arrow(ax, 5.0, 6.88, x, 6.5)

    # Row C: T6–T8
    arrow(ax, 2.0, 5.5, 2.0, 4.8); arrow(ax, 5.0, 5.5, 5.0, 4.8); arrow(ax, 8.0, 5.5, 8.0, 4.8)
    row_c = [(2.0, "T6: Climate\nchange scenarios\n5 futures × 2 states"),
             (5.0, "T7: Integrated\ngrid priority\ntop-50 grids"),
             (8.0, "T8: Carbon\naccounting\n4,127 kt CO₂/yr")]
    for x, lab in row_c:
        box(ax, x, 4.25, 2.7, 1.0, lab, fc="#E8F4FD", ec="#2E75B6", fs=FONT_SIZE_ANNOT - 1)

    # ── Section 3: OUTPUT (y=2.2–3.1) ─────────────────────────────────────
    ax.text(5.0, 3.55, "③ Output", ha="center", va="center",
            fontsize=FONT_SIZE_ANNOT, color="#888888", style="italic")
    for x in [2.0, 5.0, 8.0]:
        arrow(ax, x, 3.75, 5.0, 3.2, lw=1.0)
    box(ax, 5.0, 2.6, 8.0, 1.0,
        "Paper 3: City-scale integrated building retrofit + rooftop PV assessment\n"
        "Changsha, China  ·  115 Mt CO₂ avoided (2025–2080)  ·  4.1× over PV-only screening",
        fc="#E5F5E0", ec="#31A354", fs=FONT_SIZE_ANNOT, bold=True)

    ax.set_title("Paper 3 methodology overview",
                 fontsize=FONT_SIZE_TITLE + 1, fontweight="bold", pad=6)
    fig.subplots_adjust(left=0.03, right=0.97, bottom=0.02, top=0.94)
    out = os.path.join(FIG_DIR, "fig02_methodology_flowchart.png")
    fig.savefig(out, dpi=DPI_PRINT)
    plt.close(fig)
    return out


# ===========================================================================
# FIG 03 — Building stock classification (era × typology)
# ===========================================================================

def fig03_era_typology():
    bld = get_buildings()

    fig, axes = plt.subplots(1, 3, figsize=(FIGSIZE_WIDE[0], 4.0))

    eras   = ["era1", "era2", "era3"]
    typos_key   = ["lowrise", "midrise", "highrise"]   # GeoJSON stores lowercase
    typos_label = ["LowRise", "MidRise", "HighRise"]
    total_bld = len(bld)

    # ---- panel a: era bar ------------------------------------------------
    ax = axes[0]
    counts = [len(bld[bld["era_final"] == e]) for e in eras]
    xpos_a = np.arange(len(eras))
    bars = ax.bar(xpos_a, counts, color=[ERA_COLORS[e] for e in eras], width=0.5, zorder=2)
    ax.set_ylabel("Building count", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(a) Era distribution", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.set_ylim(0, max(counts) * 1.30)
    ax.set_xticks(xpos_a)
    ax.set_xticklabels(["Era 1", "Era 2", "Era 3"], fontsize=FONT_SIZE_BASE)
    for bar, cnt in zip(bars, counts):
        pct = cnt / total_bld * 100
        ax.text(bar.get_x() + bar.get_width() / 2, cnt + 60,
                f"{cnt:,} ({pct:.1f}%)", ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    # ---- panel b: typology bar -------------------------------------------
    ax = axes[1]
    tcounts = [len(bld[bld["typology"] == t]) for t in typos_key]
    xpos_b = np.arange(len(typos_key))
    tbars = ax.bar(xpos_b, tcounts, color=[TYPOLOGY_COLORS[t] for t in typos_label],
                   width=0.5, zorder=2)
    ax.set_ylabel("Building count", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(b) Typology distribution", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.set_ylim(0, max(tcounts) * 1.30)
    ax.set_xticks(xpos_b)
    ax.set_xticklabels(typos_label, fontsize=FONT_SIZE_BASE)
    for bar, cnt in zip(tbars, tcounts):
        pct = cnt / total_bld * 100
        ax.text(bar.get_x() + bar.get_width() / 2, cnt + 60,
                f"{cnt:,} ({pct:.1f}%)", ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    # ---- panel c: era × typology stacked ---------------------------------
    ax = axes[2]
    xpos_c = np.arange(len(eras))
    bottoms = np.zeros(len(eras))
    for tk, tl in zip(typos_key, typos_label):
        vals = np.array([len(bld[(bld["era_final"] == e) & (bld["typology"] == tk)]) for e in eras])
        ax.bar(xpos_c, vals, bottom=bottoms, label=tl,
               color=TYPOLOGY_COLORS[tl], width=0.5, zorder=2)
        bottoms += vals
    ax.set_xticks(xpos_c)
    ax.set_xticklabels(["Era 1", "Era 2", "Era 3"], fontsize=FONT_SIZE_BASE)
    ax.set_ylabel("Building count", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(c) Era × typology", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, loc="upper right", framealpha=0.85, edgecolor="none")
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    fig.suptitle("Building stock classification  (18,826 buildings, Changsha urban core)",
                 fontsize=FONT_SIZE_TITLE + 1, fontweight="bold")
    fig.subplots_adjust(left=0.07, right=0.97, bottom=0.12, top=0.88, wspace=0.38)
    out = os.path.join(FIG_DIR, "fig03_era_typology.png")
    fig.savefig(out, dpi=DPI_PRINT)
    plt.close(fig)
    return out


# ===========================================================================
# FIG 04 — City-scale baseline energy by era
# ===========================================================================

def fig04_city_baseline():
    bera = get_baseline_era()
    eras = ["era1", "era2", "era3"]
    eras_present = bera["era"].tolist()

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)

    # ---- panel a: stacked bar (H / C / Other) per era -------------------
    ax = axes[0]
    h_vals = [bera.loc[bera["era"] == e, "heating_GWh"].values[0] for e in eras]
    c_vals = [bera.loc[bera["era"] == e, "cooling_GWh"].values[0] for e in eras]
    o_vals = [bera.loc[bera["era"] == e, "other_GWh"].values[0] for e in eras]
    xlabels = [ERA_LABELS[e].split(" (")[0] for e in eras]
    xpos = np.arange(len(eras))

    ax.bar(xpos, h_vals, color=HEATING_COLOR, label="Heating", zorder=2, width=0.5)
    ax.bar(xpos, c_vals, bottom=h_vals, color=COOLING_COLOR, label="Cooling", zorder=2, width=0.5)
    ax.bar(xpos, o_vals, bottom=[h + c for h, c in zip(h_vals, c_vals)],
           color=OTHER_COLOR, label="Other (lighting/DHW)", zorder=2, width=0.5)
    totals = [h + c + o for h, c, o in zip(h_vals, c_vals, o_vals)]
    for x, tot in zip(xpos, totals):
        ax.text(x, tot + 30, f"{tot:.0f} GWh", ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT)
    ax.set_xticks(xpos)
    ax.set_xticklabels(xlabels)
    ax.set_ylabel("Annual energy (GWh/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(a) Energy by era and end-use", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, loc="upper right", framealpha=0.85, edgecolor="none")
    ax.set_ylim(0, max(totals) * 1.18)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    # ---- panel b: EUI per era -------------------------------------------
    ax = axes[1]
    euis = [bera.loc[bera["era"] == e, "eui_kwh_m2"].values[0] for e in eras]
    bars = ax.bar(xpos, euis, color=[ERA_COLORS[e] for e in eras], width=0.5, zorder=2)
    for bar, eui in zip(bars, euis):
        ax.text(bar.get_x() + bar.get_width() / 2, eui + 1,
                f"{eui:.1f}", ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT)
    ax.set_xticks(xpos)
    ax.set_xticklabels(xlabels)
    ax.set_ylabel("EUI (kWh/m²/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(b) Energy use intensity by era", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.set_ylim(0, max(euis) * 1.20)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    # city total annotation
    axes[0].annotate("City total: 15,382 GWh/yr\n(EUI = 213.5 kWh/m²/yr)",
                     xy=(0.5, 0.96), xycoords="figure fraction",
                     ha="center", fontsize=FONT_SIZE_ANNOT, style="italic",
                     color="#444444")
    plt.tight_layout()
    out = os.path.join(FIG_DIR, "fig04_city_baseline.png")
    savefig(fig, out)
    return out


# ===========================================================================
# FIG 05 — Retrofit savings by measure
# ===========================================================================

def fig05_city_retrofit():
    rtot = get_retrofit_totals()
    rera = get_retrofit_era()

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)

    # ---- panel a: city-total savings per retrofit measure ----------------
    ax = axes[0]
    measures = ["R1_Wall", "R2_Window", "R3_Roof", "R4_Infiltration", "R5_Combined"]
    labels   = [rtot.loc[rtot["retrofit"] == m, "label"].values[0] for m in measures]
    savings  = [rtot.loc[rtot["retrofit"] == m, "total_savings_GWh"].values[0] for m in measures]
    colors   = [RETROFIT_COLORS[m] for m in measures]
    xpos = np.arange(len(measures))
    bars = ax.bar(xpos, savings, color=colors, width=0.55, zorder=2)
    ax.set_xticks(xpos)
    ax.set_xticklabels([l.split(": ")[1] for l in labels], fontsize=FONT_SIZE_BASE)
    ax.set_ylabel("Annual savings (GWh/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(a) City-scale savings by retrofit measure", fontsize=FONT_SIZE_TITLE, pad=4)
    for bar, s in zip(bars, savings):
        pct = rtot.loc[rtot["retrofit"] == measures[bars.patches.index(bar)],
                       "savings_vs_baseline_pct"].values[0]
        ax.text(bar.get_x() + bar.get_width() / 2, s + 20,
                f"{s:.0f}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT)
    ax.set_ylim(0, max(savings) * 1.30)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    # ---- panel b: R5 savings per era (total) ----------------------------
    ax = axes[1]
    r5 = rera[rera["retrofit"] == "R5_Combined"].copy()
    eras = ["era1", "era2", "era3"]
    r5 = r5.set_index("era")
    sav = [r5.loc[e, "savings_GWh"] if e in r5.index else 0 for e in eras]
    pct_list = [r5.loc[e, "savings_pct"] if e in r5.index else 0 for e in eras]
    xpos = np.arange(len(eras))
    bars2 = ax.bar(xpos, sav, color=[ERA_COLORS[e] for e in eras], width=0.45, zorder=2)
    for x, s, pct in zip(xpos, sav, pct_list):
        ax.text(x, s + 20, f"{s:.0f} GWh\n({pct:.0f}%)",
                ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT)
    ax.set_xticks(xpos)
    ax.set_xticklabels([ERA_LABELS[e].split(" (")[0] for e in eras])
    ax.set_ylabel("Annual savings (GWh/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(b) R5 savings by era", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.set_ylim(0, max(sav) * 1.28)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    plt.tight_layout()
    out = os.path.join(FIG_DIR, "fig05_city_retrofit.png")
    savefig(fig, out)
    return out


# ===========================================================================
# FIG 06 — PV spatial distribution (HP-only map + typology bar chart)
# ===========================================================================

def fig06_pv_spatial():
    grid_geo = get_grid_geo()
    bld_gpd  = get_buildings()

    # PV aggregated to grid — HP buildings only
    hp = bld_gpd[bld_gpd["is_high_potential"] == 1]
    hp_pv_grid = hp.groupby("grid_id")["annual_pv_kwh_v5"].sum().reset_index()
    hp_pv_grid["annual_pv_GWh"] = hp_pv_grid["annual_pv_kwh_v5"] / 1e6

    gdf = grid_geo.merge(hp_pv_grid, on="grid_id", how="left")
    gdf["annual_pv_GWh"] = gdf["annual_pv_GWh"].fillna(0)
    gdf_hp = gdf[gdf["annual_pv_GWh"] > 0]

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_MAP)

    # ---- panel a: HP-only grid choropleth --------------------------------
    ax = axes[0]
    gdf[gdf["annual_pv_GWh"] == 0].plot(ax=ax, color="#EEEEEE", linewidth=0.2, edgecolor="#CCCCCC")
    vmax = gdf_hp["annual_pv_GWh"].quantile(0.97)
    gdf_hp.plot(ax=ax, column="annual_pv_GWh", cmap="YlOrRd",
                vmin=0, vmax=vmax, linewidth=0.2, edgecolor="#AAAAAA55")
    get_study_area().boundary.plot(ax=ax, color="black", linewidth=0.8, zorder=4)
    plt.colorbar(ScalarMappable(norm=Normalize(0, vmax), cmap="YlOrRd"),
                 ax=ax, label="Annual PV (GWh/yr)", shrink=0.75, pad=0.02)
    ax.set_title("(a) Annual PV generation by grid\n(high-potential buildings, GWh/yr)",
                 fontsize=FONT_SIZE_TITLE, pad=4)
    ax.set_xlabel("Longitude (°E)", fontsize=FONT_SIZE_LABEL)
    ax.set_ylabel("Latitude (°N)", fontsize=FONT_SIZE_LABEL)
    ax.tick_params(labelsize=FONT_SIZE_BASE - 1)
    _add_north_arrow(ax)
    _add_scalebar_km(ax, km=3, lon0=113.01, lat0=28.103)

    # ---- panel b: PV by typology bar + HP fraction line ------------------
    ax = axes[1]
    bld_csv = pd.read_csv(di("classified_buildings.csv"))
    typos_key   = ["lowrise", "midrise", "highrise"]
    typos_label = ["LowRise", "MidRise", "HighRise"]
    hp_csv = bld_csv[bld_csv["is_high_potential"] == 1]

    pv_typ  = [hp_csv[hp_csv["typology"] == t]["annual_pv_kwh_v5"].sum() / 1e6 for t in typos_key]
    cnt_all = [len(bld_csv[bld_csv["typology"] == t]) for t in typos_key]
    cnt_hp  = [len(hp_csv[hp_csv["typology"] == t]) for t in typos_key]
    hp_frac = [h / a * 100 if a > 0 else 0 for h, a in zip(cnt_hp, cnt_all)]

    xpos = np.arange(len(typos_key))
    bars = ax.bar(xpos, pv_typ, color=[TYPOLOGY_COLORS[t] for t in typos_label],
                  width=0.5, zorder=2)
    for bar, pv, frac, cnt in zip(bars, pv_typ, hp_frac, cnt_hp):
        ax.text(bar.get_x() + bar.get_width() / 2, pv + 8,
                f"{pv:.0f} GWh\n({cnt:,} HP bldgs)",
                ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT)

    # HP fraction as secondary y-axis line
    ax2 = ax.twinx()
    ax2.plot(xpos, hp_frac, color="#555555", linewidth=1.5,
             marker="D", markersize=5, label="HP fraction (%)", zorder=5)
    ax2.set_ylim(0, max(hp_frac) * 1.5)
    ax2.set_ylabel("HP building fraction (%)", fontsize=FONT_SIZE_LABEL)
    ax2.tick_params(labelsize=FONT_SIZE_BASE - 1)
    for s in ["top"]:
        ax2.spines[s].set_visible(False)

    ax.set_xticks(xpos)
    ax.set_xticklabels(typos_label, fontsize=FONT_SIZE_BASE)
    ax.set_ylabel("Annual PV generation (GWh/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(b) PV generation by building typology\n(high-potential buildings)",
                 fontsize=FONT_SIZE_TITLE, pad=4)
    ax.set_ylim(0, max(pv_typ) * 1.35)
    despine(ax)

    # Combined legend
    h1 = mpatches.Patch(facecolor="#DDDDDD", label="HP fraction (right axis)")
    line_handle = Line2D([0], [0], color="#555555", marker="D", markersize=5,
                         label="HP fraction (%)")
    ax.legend(handles=[line_handle], loc="upper right", fontsize=FONT_SIZE_LEGEND,
              framealpha=0.85, edgecolor="none")

    fig.suptitle("Rooftop PV generation potential  (6,401 high-potential buildings, 1,603 GWh/yr)",
                 fontsize=FONT_SIZE_TITLE + 1, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = os.path.join(FIG_DIR, "fig06_pv_spatial.png")
    savefig(fig, out)
    return out


# ===========================================================================
# FIG 07 — Monthly supply-demand matching
# ===========================================================================

def fig07_supply_demand():
    df = get_monthly()

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)

    # ---- panel a: monthly demand stacks + PV line -----------------------
    ax = axes[0]
    months = np.arange(1, 13)
    ax.bar(months, df["baseline_heat_GWh"], color=HEATING_COLOR, label="Heating",
           zorder=2, width=0.7)
    ax.bar(months, df["baseline_cool_GWh"], bottom=df["baseline_heat_GWh"],
           color=COOLING_COLOR, label="Cooling", zorder=2, width=0.7)
    ax.bar(months, df["baseline_other_GWh"],
           bottom=df["baseline_heat_GWh"] + df["baseline_cool_GWh"],
           color=OTHER_COLOR, label="Other", zorder=2, width=0.7)
    ax.plot(months, df["pv_gen_GWh"], color=PV_COLOR, linewidth=2.0,
            marker="o", markersize=4, label="PV generation", zorder=5)
    ax.set_xticks(months)
    ax.set_xticklabels(MONTH_NAMES, fontsize=FONT_SIZE_BASE - 1)
    ax.set_ylabel("Energy (GWh)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(a) Monthly energy demand vs PV supply\n(baseline)", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, loc="upper left", framealpha=0.85, edgecolor="none",
              ncol=2)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    # ---- panel b: R5 demand vs PV, showing net -------------------------
    ax = axes[1]
    ax.bar(months, df["r5_heat_GWh"], color=HEATING_COLOR, label="R5 heating",
           zorder=2, width=0.7)
    ax.bar(months, df["r5_cool_GWh"], bottom=df["r5_heat_GWh"],
           color=COOLING_COLOR, label="R5 cooling", zorder=2, width=0.7)
    ax.bar(months, df["r5_other_GWh"],
           bottom=df["r5_heat_GWh"] + df["r5_cool_GWh"],
           color=OTHER_COLOR, label="R5 other", zorder=2, width=0.7, alpha=0.7)
    ax.plot(months, df["pv_gen_GWh"], color=PV_COLOR, linewidth=2.0,
            marker="o", markersize=4, label="PV generation", zorder=5)
    ax.set_xticks(months)
    ax.set_xticklabels(MONTH_NAMES, fontsize=FONT_SIZE_BASE - 1)
    ax.set_ylabel("Energy (GWh)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(b) Monthly energy demand vs PV supply\n(R5 retrofit)", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, loc="upper left", framealpha=0.85, edgecolor="none",
              ncol=2)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    fig.suptitle("Monthly PV supply-demand matching  (HP buildings, 1,603 GWh PV, 100% SC)",
                 fontsize=FONT_SIZE_TITLE + 1, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = os.path.join(FIG_DIR, "fig07_supply_demand.png")
    savefig(fig, out)
    return out


# ===========================================================================
# FIG 08 — Seasonal PV-cooling coincidence (panel b: active season only)
# ===========================================================================

def fig08_seasonal_match():
    df = get_monthly()

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)

    months = np.arange(1, 13)

    # ---- panel a: PV coverage fraction (PV/total demand) ----------------
    ax = axes[0]
    base_cov = df["baseline_coverage"]
    r5_cov   = df["r5_coverage"]
    ax.bar(months - 0.2, base_cov * 100, width=0.38, color="#CCCCCC",
           label="Baseline", zorder=2)
    ax.bar(months + 0.2, r5_cov * 100, width=0.38, color=PV_COLOR,
           label="R5 retrofit", zorder=2)
    ax.set_xticks(months)
    ax.set_xticklabels(MONTH_NAMES, fontsize=FONT_SIZE_BASE - 1)
    ax.set_ylabel("PV coverage (% of total demand)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(a) Monthly PV coverage fraction\n(% of total demand covered by PV)",
                 fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, framealpha=0.85, edgecolor="none")
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    # ---- panel b: cooling-PV coincidence (active season only) -----------
    # Threshold: baseline cooling < 5% of annual (2532 GWh * 0.05 = 126.6 GWh)
    ax = axes[1]
    cool_threshold = df["baseline_cool_GWh"].sum() * 0.05
    active = df["baseline_cool_GWh"] >= cool_threshold

    cool_cov_base = df["baseline_cool_coverage"].copy().astype(float)
    cool_cov_r5   = df["r5_cool_coverage"].copy().astype(float)

    # For inactive months: draw a hatched "N/A" bar instead of a value bar
    inactive_months = months[~active.values]
    active_months   = months[active.values]

    # Plot active months first
    for m, cb, cr in zip(active_months,
                         cool_cov_base[active].values,
                         cool_cov_r5[active].values):
        ax.bar(m - 0.2, cb * 100, width=0.38, color=COOLING_COLOR, alpha=0.65,
               label="Baseline" if m == active_months[0] else "_", zorder=2)
        ax.bar(m + 0.2, cr * 100, width=0.38, color=COOLING_COLOR,
               label="R5 retrofit" if m == active_months[0] else "_", zorder=2)

    # Inactive months: light grey hatched bars to show "undefined"
    for m in inactive_months:
        ax.bar(m, 5, width=0.7, color="#DDDDDD", hatch="///", edgecolor="#AAAAAA",
               linewidth=0.5, zorder=2)

    ax.text(0.5, 0.92,
            "Jan–Mar, Nov–Dec: cooling demand ≈ 0\ncoverage ratio undefined",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=FONT_SIZE_ANNOT - 1, color="#777777", style="italic",
            bbox=dict(fc="white", ec="none", alpha=0.7))

    ax.set_xticks(months)
    ax.set_xticklabels(MONTH_NAMES, fontsize=FONT_SIZE_BASE - 1)
    ax.set_ylabel("PV coverage of cooling demand (%)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(b) PV coverage of cooling demand\n(active cooling season: Apr–Oct)",
                 fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, framealpha=0.85, edgecolor="none")
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    fig.text(0.5, -0.01,
             "PV–cooling coincidence factor: 0.425  (Jun–Sep PV share 38.3% / cooling share 90%)",
             ha="center", fontsize=FONT_SIZE_ANNOT, style="italic", color="#444444")
    plt.tight_layout()
    out = os.path.join(FIG_DIR, "fig08_seasonal_match.png")
    savefig(fig, out)
    return out


# ===========================================================================
# FIG 09 — Climate scenario city-scale energy
# ===========================================================================

def fig09_climate_city():
    clim = get_climate()

    scenarios = SCENARIO_ORDER

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)

    def _get_total(scenario, retrofit_status):
        row = clim[(clim["scenario"] == scenario) & (clim["retrofit_status"] == retrofit_status)]
        if len(row) == 0:
            return None, None, None
        return row["city_heating_GWh"].values[0], row["city_cooling_GWh"].values[0], row["city_other_GWh"].values[0]

    # ---- panel a: baseline demand across scenarios ----------------------
    ax = axes[0]
    xpos = np.arange(len(scenarios))
    h_b = [_get_total(s, "baseline")[0] for s in scenarios]
    c_b = [_get_total(s, "baseline")[1] for s in scenarios]
    o_b = [_get_total(s, "baseline")[2] for s in scenarios]
    ax.bar(xpos, h_b, color=HEATING_COLOR, label="Heating", width=0.55, zorder=2)
    ax.bar(xpos, c_b, bottom=h_b, color=COOLING_COLOR, label="Cooling", width=0.55, zorder=2)
    ax.bar(xpos, o_b, bottom=[h + c for h, c in zip(h_b, c_b)],
           color=OTHER_COLOR, label="Other", width=0.55, zorder=2)
    totals_b = [h + c + o for h, c, o in zip(h_b, c_b, o_b)]
    for x, tot in zip(xpos, totals_b):
        ax.text(x, tot + 50, f"{tot:.0f}", ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT - 1)
    ax.set_xticks(xpos)
    ax.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios], rotation=25, ha="right",
                       fontsize=FONT_SIZE_BASE - 1)
    ax.set_ylabel("Annual energy (GWh/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(a) Baseline demand by climate scenario", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, loc="upper right", framealpha=0.85, edgecolor="none")
    ax.set_ylim(0, max(totals_b) * 1.18)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    # ---- panel b: R5 demand vs baseline current -------------------------
    ax = axes[1]
    h_r5 = [_get_total(s, "R5")[0] for s in scenarios]
    c_r5 = [_get_total(s, "R5")[1] for s in scenarios]
    o_r5 = [_get_total(s, "R5")[2] for s in scenarios]
    totals_r5 = [h + c + o for h, c, o in zip(h_r5, c_r5, o_r5)]
    ax.plot(xpos, totals_b, color=CARBON_BASELINE_COLOR, linewidth=1.5,
            marker="s", markersize=5, label="Baseline", zorder=4)
    ax.plot(xpos, totals_r5, color=CARBON_R5PV_COLOR, linewidth=1.5,
            marker="o", markersize=5, label="R5 retrofit", zorder=4)
    # shade region
    ax.fill_between(xpos, totals_r5, totals_b, alpha=0.15, color=CARBON_R5PV_COLOR)
    ax.set_xticks(xpos)
    ax.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios], rotation=25, ha="right",
                       fontsize=FONT_SIZE_BASE - 1)
    ax.set_ylabel("Annual energy (GWh/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(b) Baseline vs R5 demand across scenarios", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, framealpha=0.85, edgecolor="none")
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)
    ax.annotate("H/C tipping\n2050 SSP5-8.5", xy=(2, totals_r5[2]), xytext=(2.6, totals_r5[2] + 300),
                arrowprops=dict(arrowstyle="->", color="#555555"), fontsize=FONT_SIZE_ANNOT - 1)

    plt.tight_layout()
    out = os.path.join(FIG_DIR, "fig09_climate_city.png")
    savefig(fig, out)
    return out


# ===========================================================================
# FIG 10 — Heating/cooling shift under climate change
# ===========================================================================

def fig10_hc_shift():
    clim = get_climate()
    scenarios = SCENARIO_ORDER

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)

    def _hc(scenario, retrofit):
        r = clim[(clim["scenario"] == scenario) & (clim["retrofit_status"] == retrofit)]
        if len(r) == 0:
            return np.nan, np.nan
        return r["city_heating_GWh"].values[0], r["city_cooling_GWh"].values[0]

    # ---- panel a: H/C ratio across scenarios ----------------------------
    ax = axes[0]
    hc_base = []
    hc_r5   = []
    for s in scenarios:
        h, c = _hc(s, "baseline")
        hc_base.append(h / c if c > 0 else np.nan)
        h, c = _hc(s, "R5")
        hc_r5.append(h / c if c > 0 else np.nan)
    xpos = np.arange(len(scenarios))
    ax.plot(xpos, hc_base, color=CARBON_BASELINE_COLOR, linewidth=2.0,
            marker="s", markersize=6, label="Baseline")
    ax.plot(xpos, hc_r5,   color=CARBON_R5PV_COLOR,     linewidth=2.0,
            marker="o", markersize=6, label="R5 retrofit")
    ax.axhline(1.0, color="black", lw=0.8, linestyle="--", label="H/C = 1 (tipping)")
    ax.set_xticks(xpos)
    ax.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios], rotation=25, ha="right",
                       fontsize=FONT_SIZE_BASE - 1)
    ax.set_ylabel("Heating/Cooling ratio", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(a) Heating-to-cooling ratio shift", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, framealpha=0.85, edgecolor="none")
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)
    # annotate tipping point
    tip_x = scenarios.index("2050_SSP585")
    ax.annotate("Tipping\npoint", xy=(tip_x, hc_base[tip_x]),
                xytext=(tip_x + 0.5, hc_base[tip_x] + 0.12),
                arrowprops=dict(arrowstyle="->", color="#555555"),
                fontsize=FONT_SIZE_ANNOT - 1)

    # ---- panel b: absolute heating & cooling per scenario ---------------
    ax = axes[1]
    width = 0.22
    xpos = np.arange(len(scenarios))
    h_b = [_hc(s, "baseline")[0] for s in scenarios]
    c_b = [_hc(s, "baseline")[1] for s in scenarios]
    h_r = [_hc(s, "R5")[0] for s in scenarios]
    c_r = [_hc(s, "R5")[1] for s in scenarios]
    ax.bar(xpos - 1.5 * width, h_b, width=width, color=HEATING_COLOR, alpha=0.75,
           label="Baseline heating", zorder=2)
    ax.bar(xpos - 0.5 * width, c_b, width=width, color=COOLING_COLOR, alpha=0.75,
           label="Baseline cooling", zorder=2)
    ax.bar(xpos + 0.5 * width, h_r, width=width, color=HEATING_COLOR,
           label="R5 heating", zorder=2, linewidth=0.5, edgecolor="white")
    ax.bar(xpos + 1.5 * width, c_r, width=width, color=COOLING_COLOR,
           label="R5 cooling", zorder=2, linewidth=0.5, edgecolor="white")
    ax.set_xticks(xpos)
    ax.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios], rotation=25, ha="right",
                       fontsize=FONT_SIZE_BASE - 1)
    ax.set_ylabel("Annual energy (GWh/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(b) Heating vs cooling by scenario", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND - 1, framealpha=0.85, edgecolor="none", ncol=2)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    plt.tight_layout()
    out = os.path.join(FIG_DIR, "fig10_hc_shift.png")
    savefig(fig, out)
    return out


# ===========================================================================
# FIG 11 — Integrated grid-level priority map (3 panels)
# ===========================================================================

def fig11_integrated_grid():
    grid_geo  = get_grid_geo()
    grank     = get_grid_ranking()
    sa        = get_study_area()

    # Load Paper 1 priority grid IDs
    p1_priority_ids = set(
        pd.read_csv(p1("priority_grids.csv"))["grid_id"].tolist())

    # Merge ranking onto geometry
    gdf = grid_geo.merge(grank, on="grid_id", how="left")
    gdf["integrated_score"] = gdf["integrated_score"].fillna(0)
    gdf["rank_integrated"]  = gdf["rank_integrated"].fillna(999)

    top50    = gdf[gdf["rank_integrated"] <= 50]
    occupied = gdf[gdf["integrated_score"] > 0]
    inactive = gdf[gdf["integrated_score"] == 0]

    # Paper 1 overlap counts
    top50_ids   = set(top50["grid_id"].tolist())
    both        = len(top50_ids & p1_priority_ids)        # 28
    p1_only     = len(p1_priority_ids - top50_ids)        # 118
    p3_new      = len(top50_ids - p1_priority_ids)        # 22

    fig, axes = plt.subplots(1, 3, figsize=(11.0, 5.0))

    # ---- panel a: score choropleth + red top-50 outlines -----------------
    ax = axes[0]
    inactive.plot(ax=ax, color="#EEEEEE", linewidth=0.1, edgecolor="none")
    occupied.plot(ax=ax, column="integrated_score", cmap="Blues", vmin=0, vmax=100,
                  alpha=0.7, linewidth=0.1, edgecolor="none")
    # Red outlines for top-50 drawn as a second layer
    top50.plot(ax=ax, facecolor="none", edgecolor="#C0392B", linewidth=2.0, zorder=4)
    sa.boundary.plot(ax=ax, color="black", linewidth=0.7, zorder=5)
    plt.colorbar(ScalarMappable(norm=Normalize(0, 100), cmap="Blues"),
                 ax=ax, label="Integrated score", shrink=0.72, pad=0.02)
    ax.annotate("Top 50 grids\n(red outline)",
                xy=(0.03, 0.05), xycoords="axes fraction",
                fontsize=FONT_SIZE_ANNOT - 1, color="#C0392B",
                bbox=dict(fc="white", ec="none", alpha=0.8))
    ax.set_title("(a) Integrated priority score\n(blue gradient; top-50 = red outline)",
                 fontsize=FONT_SIZE_TITLE, pad=4)
    ax.set_xlabel("Longitude (°E)", fontsize=FONT_SIZE_LABEL)
    ax.set_ylabel("Latitude (°N)", fontsize=FONT_SIZE_LABEL)
    ax.tick_params(labelsize=FONT_SIZE_BASE - 1)
    _add_north_arrow(ax)

    # ---- panel b: top-50 coloured by dominant era -----------------------
    ax = axes[1]
    inactive.plot(ax=ax, color="#EEEEEE", linewidth=0.1, edgecolor="none")
    occupied[occupied["rank_integrated"] > 50].plot(ax=ax, color="#DDDDDD",
                                                     linewidth=0.1, edgecolor="none")
    for era, color in ERA_COLORS.items():
        subset = top50[top50["dominant_era"] == era]
        if len(subset) > 0:
            subset.plot(ax=ax, color=color, linewidth=0.3, edgecolor="black",
                        label=ERA_LABELS[era])
    sa.boundary.plot(ax=ax, color="black", linewidth=0.7, zorder=5)
    handles = [mpatches.Patch(facecolor=v, label=ERA_LABELS[k])
               for k, v in ERA_COLORS.items()]
    ax.legend(handles=handles, loc="lower left", fontsize=FONT_SIZE_LEGEND,
              framealpha=0.85, edgecolor="none")
    ax.set_title("(b) Top-50 grids by dominant era\n(28 in P1 priority, 22 new)",
                 fontsize=FONT_SIZE_TITLE, pad=4)
    ax.set_xlabel("Longitude (°E)", fontsize=FONT_SIZE_LABEL)
    ax.set_ylabel("Latitude (°N)", fontsize=FONT_SIZE_LABEL)
    ax.tick_params(labelsize=FONT_SIZE_BASE - 1)
    _add_north_arrow(ax)

    # ---- panel c: Paper1 vs Paper3 overlap bar chart --------------------
    ax = axes[2]
    bar_labels = ["Paper 1\npriority only\n(118 grids)", "In BOTH\n(28 grids)",
                  "Paper 3\nnew top-50\n(22 grids)"]
    bar_vals   = [p1_only, both, p3_new]
    bar_colors = ["#2E75B6", HIGHLIGHT_COLOR, "#C0392B"]
    xpos = np.arange(3)
    bars = ax.bar(xpos, bar_vals, color=bar_colors, width=0.55, zorder=2,
                  edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, bar_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5,
                str(val), ha="center", va="bottom",
                fontsize=FONT_SIZE_ANNOT + 1, fontweight="bold")
    ax.set_xticks(xpos)
    ax.set_xticklabels(bar_labels, fontsize=FONT_SIZE_BASE)
    ax.set_ylabel("Grid count", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(c) Priority grid overlap\nwith Paper 1 solar-only screening",
                 fontsize=FONT_SIZE_TITLE, pad=4)
    ax.set_ylim(0, max(bar_vals) * 1.30)
    ax.annotate("44% of Paper 3\ntop-50 are NEW",
                xy=(2, p3_new), xytext=(1.5, p3_new + 15),
                arrowprops=dict(arrowstyle="->", color="#555555"),
                fontsize=FONT_SIZE_ANNOT - 1, color="#C0392B")
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    fig.suptitle(
        "Integrated grid-level priority scoring  "
        "(671 grids; weights: solar/retrofit/carbon/climate = 0.30/0.30/0.20/0.20)",
        fontsize=FONT_SIZE_TITLE, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = os.path.join(FIG_DIR, "fig11_integrated_grid.png")
    savefig(fig, out)
    return out


# ===========================================================================
# FIG 12 — Annual carbon accounting
# ===========================================================================

def fig12_carbon():
    cann = get_carbon_ann()
    cera = get_carbon_era()

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)

    # ---- panel a: carbon by scenario (current year, fixed EF) -----------
    ax = axes[0]
    # Show current year only, fixed grid EF, baseline vs R5 vs R5+PV
    cur = cann[cann["scenario"] == "Current"]
    bau_no_pv = cur.loc[(cur["retrofit_status"] == "baseline") & (~cur["pv_included"]),
                        "annual_carbon_kt"].values[0]
    bau_pv    = cur.loc[(cur["retrofit_status"] == "baseline") & (cur["pv_included"]),
                        "annual_carbon_kt"].values[0]
    r5_no_pv  = cur.loc[(cur["retrofit_status"] == "R5") & (~cur["pv_included"]),
                        "annual_carbon_kt"].values[0]
    r5_pv     = cur.loc[(cur["retrofit_status"] == "R5") & (cur["pv_included"]),
                        "annual_carbon_kt"].values[0]

    categories  = ["Baseline\n(no PV)", "Baseline\n+ PV", "R5 retrofit\n(no PV)", "R5 + PV"]
    values      = [bau_no_pv, bau_pv, r5_no_pv, r5_pv]
    bar_colors  = [CARBON_BASELINE_COLOR, COOLING_COLOR, "#74ADD1", CARBON_R5PV_COLOR]
    bars = ax.bar(categories, values, color=bar_colors, width=0.55, zorder=2)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 20,
                f"{val:.0f}", ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT)
    # savings annotation
    ax.annotate("", xy=(3, r5_pv), xytext=(0, bau_no_pv),
                arrowprops=dict(arrowstyle="-[,widthB=0.5", color="#555555", lw=0.8))
    ax.text(1.5, (bau_no_pv + r5_pv) / 2 + 100,
            f"Saved: {bau_no_pv - r5_pv:.0f} kt CO₂/yr\n({(bau_no_pv - r5_pv)/bau_no_pv*100:.0f}%)",
            ha="center", fontsize=FONT_SIZE_ANNOT, color="#444444",
            bbox=dict(fc="white", ec="none", alpha=0.7))
    ax.set_ylabel("Annual CO₂ emissions (kt/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(a) Annual carbon — current climate\n(grid EF = 0.5703 tCO₂/MWh)", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.set_ylim(0, bau_no_pv * 1.22)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    # ---- panel b: per-era combined savings breakdown --------------------
    ax = axes[1]
    eras = ["era1", "era2", "era3"]
    r5_sav  = [cera.loc[cera["era"] == e, "r5_carbon_savings_kt"].values[0] for e in eras]
    pv_sav  = [cera.loc[cera["era"] == e, "pv_carbon_savings_kt"].values[0] for e in eras]
    xpos = np.arange(len(eras))
    ax.bar(xpos, r5_sav, color="#74ADD1", label="R5 retrofit savings", width=0.45, zorder=2)
    ax.bar(xpos, pv_sav, bottom=r5_sav, color=PV_COLOR, label="PV savings", width=0.45, zorder=2)
    totals = [r + p for r, p in zip(r5_sav, pv_sav)]
    for x, tot in zip(xpos, totals):
        pct = tot / sum(totals) * 100
        ax.text(x, tot + 20, f"{tot:.0f} kt\n({pct:.0f}%)",
                ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT)
    ax.set_xticks(xpos)
    ax.set_xticklabels([ERA_LABELS[e].split(" (")[0] for e in eras])
    ax.set_ylabel("Annual CO₂ savings (kt/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(b) Per-era combined savings\n(R5 retrofit + PV)", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, framealpha=0.85, edgecolor="none")
    ax.set_ylim(0, max(totals) * 1.28)
    despine(ax)
    ax.grid(axis="y", lw=0.4, alpha=0.5)

    plt.tight_layout()
    out = os.path.join(FIG_DIR, "fig12_carbon.png")
    savefig(fig, out)
    return out


# ===========================================================================
# FIG 13 — Cumulative carbon pathways 2025–2080
# ===========================================================================

def fig13_cumulative_carbon():
    cum = get_carbon_cum()

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)

    years = cum["year"].values

    # ---- panel a: annual carbon under 4 scenarios ----------------------
    ax = axes[0]
    ax.plot(years, cum["A_annual_kt"], color=CARBON_BASELINE_COLOR, lw=2.0,
            marker="o", markersize=3, label="A: BAU SSP2-4.5")
    ax.plot(years, cum["B_annual_kt"], color=CARBON_R5PV_COLOR, lw=2.0,
            marker="s", markersize=3, label="B: R5+PV immediate SSP2-4.5")
    ax.plot(years, cum["C_annual_kt"], color=CARBON_STEP_COLOR, lw=1.8, ls="--",
            marker="^", markersize=3, label="C: Stepwise SSP2-4.5")
    ax.plot(years, cum["D_annual_kt"], color=CARBON_SSP585_COLOR, lw=1.8, ls=":",
            marker="D", markersize=3, label="D: R5+PV SSP5-8.5")
    ax.fill_between(years, cum["B_annual_kt"], cum["A_annual_kt"],
                    alpha=0.12, color=CARBON_R5PV_COLOR)
    ax.set_xlabel("Year", fontsize=FONT_SIZE_LABEL)
    ax.set_ylabel("Annual CO₂ (kt/yr)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(a) Annual carbon emission pathways", fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, framealpha=0.85, edgecolor="none")
    despine(ax)
    ax.grid(lw=0.4, alpha=0.5)

    # ---- panel b: cumulative emissions ----------------------------------
    ax = axes[1]
    ax.plot(years, cum["A_cumulative_kt"] / 1e3, color=CARBON_BASELINE_COLOR, lw=2.0,
            marker="o", markersize=3, label="A: BAU")
    ax.plot(years, cum["B_cumulative_kt"] / 1e3, color=CARBON_R5PV_COLOR, lw=2.0,
            marker="s", markersize=3, label="B: R5+PV immediate")
    ax.plot(years, cum["C_cumulative_kt"] / 1e3, color=CARBON_STEP_COLOR, lw=1.8, ls="--",
            marker="^", markersize=3, label="C: Stepwise (0→100% by 2060)")
    ax.plot(years, cum["D_cumulative_kt"] / 1e3, color=CARBON_SSP585_COLOR, lw=1.8, ls=":",
            marker="D", markersize=3, label="D: SSP5-8.5 immediate")
    ax.fill_between(years, cum["B_cumulative_kt"] / 1e3, cum["A_cumulative_kt"] / 1e3,
                    alpha=0.12, color=CARBON_R5PV_COLOR)
    # Endpoint annotations
    for col, color, suffix in [("A_cumulative_kt", CARBON_BASELINE_COLOR, ""),
                                ("B_cumulative_kt", CARBON_R5PV_COLOR, ""),
                                ("C_cumulative_kt", CARBON_STEP_COLOR, ""),
                                ("D_cumulative_kt", CARBON_SSP585_COLOR, "")]:
        val = cum[col].iloc[-1] / 1e3
        ax.text(2082, val, f"{val:.0f} Mt", va="center", fontsize=FONT_SIZE_ANNOT - 1,
                color=color)
    ax.set_xlim(2023, 2092)
    ax.set_xlabel("Year", fontsize=FONT_SIZE_LABEL)
    ax.set_ylabel("Cumulative CO₂ (Mt)", fontsize=FONT_SIZE_LABEL)
    ax.set_title("(b) Cumulative carbon 2025–2080\n(grid decarbonisation trajectory)",
                 fontsize=FONT_SIZE_TITLE, pad=4)
    ax.legend(fontsize=FONT_SIZE_LEGEND, framealpha=0.85, edgecolor="none")
    despine(ax)
    ax.grid(lw=0.4, alpha=0.5)
    # Savings annotation
    sav_b = (cum["A_cumulative_kt"].iloc[-1] - cum["B_cumulative_kt"].iloc[-1]) / 1e3
    ax.annotate(f"B saves\n{sav_b:.0f} Mt vs A",
                xy=(2080, cum["B_cumulative_kt"].iloc[-1] / 1e3),
                xytext=(2062, (cum["A_cumulative_kt"].iloc[-1] + cum["B_cumulative_kt"].iloc[-1]) / 2e3),
                arrowprops=dict(arrowstyle="->", color="#555555"),
                fontsize=FONT_SIZE_ANNOT - 1, color="#444444")

    plt.tight_layout()
    out = os.path.join(FIG_DIR, "fig13_cumulative_carbon.png")
    savefig(fig, out)
    return out


# ===========================================================================
# FIG 14 — Policy summary dashboard (redesigned 2-row layout)
# ===========================================================================

def fig14_policy_summary():
    gr   = get_grid_ranking()
    cera = get_carbon_era()
    grid_geo = get_grid_geo()
    sa       = get_study_area()

    # Merge top-50 geometry
    gdf = grid_geo.merge(gr, on="grid_id", how="left")
    gdf["rank_integrated"]  = gdf["rank_integrated"].fillna(999)
    gdf["integrated_score"] = gdf["integrated_score"].fillna(0)
    top50_gdf = gdf[gdf["rank_integrated"] <= 50]
    other_gdf = gdf[gdf["rank_integrated"] > 50]

    fig = plt.figure(figsize=(13.0, 9.5))

    # GridSpec: row 0 = 3 big KPI cards; row 1 = 4 top-50 stat cards (full width);
    #           row 2 = 3 panels (map, top-10 bar, comparison bar)
    gs_outer = gridspec.GridSpec(3, 1, figure=fig,
                                 height_ratios=[1.3, 0.8, 3.2],
                                 hspace=0.10, left=0.06, right=0.97,
                                 top=0.93, bottom=0.05)

    # ── ROW 0 — Big number cards ──────────────────────────────────────────
    gs_row0 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs_outer[0],
                                               wspace=0.12)
    card_data = [
        ("18,826", "buildings in\nChangsha urban core", "#FEE5D9", ERA_COLORS["era1"]),
        ("−44.3%\nnet demand", "R5 retrofit\n+ rooftop PV", "#EDF8E9", "#31A354"),
        ("4,127 kt CO₂/yr\navoided", "4.1× over\nPV-only screening", "#EFF3FF", ERA_COLORS["era3"]),
    ]
    for i, (val, lab, bg, accent) in enumerate(card_data):
        ax_c = fig.add_subplot(gs_row0[0, i])
        ax_c.set_facecolor(bg)
        ax_c.spines["bottom"].set_color(accent)
        ax_c.spines["bottom"].set_linewidth(2.5)
        for s in ["top", "left", "right"]:
            ax_c.spines[s].set_color("#CCCCCC")
            ax_c.spines[s].set_linewidth(0.6)
        ax_c.set_xticks([]); ax_c.set_yticks([])
        ax_c.text(0.5, 0.62, val, ha="center", va="center",
                  fontsize=22, fontweight="bold", color=accent,
                  transform=ax_c.transAxes, multialignment="center")
        ax_c.text(0.5, 0.16, lab, ha="center", va="center",
                  fontsize=FONT_SIZE_ANNOT + 1, color="#444444",
                  transform=ax_c.transAxes, multialignment="center")

    # ── ROW 1 — Top-50 stats (4 cells) ────────────────────────────────────
    gs_row1 = gridspec.GridSpecFromSubplotSpec(1, 4, subplot_spec=gs_outer[1],
                                               wspace=0.10)
    top50_stats = [
        ("1,339", "buildings\n(7.1% of stock)"),
        ("16.9 Mm²", "floor area\n(23.5% of city)"),
        ("879 kt CO₂/yr", "CO₂ savings\n(21.3% of city total)"),
        ("2.46 km²", "deployable\nrooftop area"),
    ]
    ax_hdr = fig.add_subplot(gs_outer[1])
    ax_hdr.axis("off")
    ax_hdr.text(0.5, 1.08,
                "Top 50 integrated-priority grids: disproportionate impact",
                ha="center", va="bottom", fontsize=FONT_SIZE_TITLE - 1,
                fontweight="bold", color="#333333",
                transform=ax_hdr.transAxes)
    for j, (val, lab) in enumerate(top50_stats):
        ax_s = fig.add_subplot(gs_row1[0, j])
        ax_s.set_facecolor("#FFFDE7")
        for s in ["top", "left", "right"]:
            ax_s.spines[s].set_color("#CCCCCC")
            ax_s.spines[s].set_linewidth(0.5)
        ax_s.spines["bottom"].set_color(HIGHLIGHT_COLOR)
        ax_s.spines["bottom"].set_linewidth(2.0)
        ax_s.set_xticks([]); ax_s.set_yticks([])
        ax_s.text(0.5, 0.62, val, ha="center", va="center",
                  fontsize=14, fontweight="bold", color="#2C3E6B",
                  transform=ax_s.transAxes, multialignment="center")
        ax_s.text(0.5, 0.15, lab, ha="center", va="center",
                  fontsize=FONT_SIZE_ANNOT, color="#555555",
                  transform=ax_s.transAxes, multialignment="center")

    # ── ROW 2 — Three analysis panels ─────────────────────────────────────
    gs_row2 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs_outer[2],
                                               wspace=0.32)

    # (a) Top-50 spatial map
    ax_map = fig.add_subplot(gs_row2[0, 0])
    other_gdf[other_gdf["integrated_score"] > 0].plot(
        ax=ax_map, color="#DDDDDD", linewidth=0.1, edgecolor="none")
    gdf[gdf["integrated_score"] == 0].plot(
        ax=ax_map, color="#EEEEEE", linewidth=0.1, edgecolor="none")
    for era, color in ERA_COLORS.items():
        sub = top50_gdf[top50_gdf["dominant_era"] == era]
        if len(sub) > 0:
            sub.plot(ax=ax_map, color=color, linewidth=0.4, edgecolor="black",
                     label=ERA_LABELS[era])
    sa.boundary.plot(ax=ax_map, color="black", linewidth=0.6, zorder=5)
    handles = [mpatches.Patch(facecolor=v, label=ERA_LABELS[k])
               for k, v in ERA_COLORS.items()]
    ax_map.legend(handles=handles, loc="lower left", fontsize=FONT_SIZE_LEGEND - 1,
                  framealpha=0.85, edgecolor="none")
    ax_map.set_title("(a) Top-50 priority grids", fontsize=FONT_SIZE_TITLE - 1, pad=4)
    ax_map.set_xlabel("Longitude (°E)", fontsize=FONT_SIZE_LABEL - 1)
    ax_map.set_ylabel("Latitude (°N)", fontsize=FONT_SIZE_LABEL - 1)
    ax_map.tick_params(labelsize=FONT_SIZE_BASE - 1)
    _add_north_arrow(ax_map)

    # (b) Top-10 grids horizontal bar chart
    ax_bar = fig.add_subplot(gs_row2[0, 1])
    top10 = gr.nsmallest(10, "rank_integrated").reset_index(drop=True)
    ytick_labels = [
        f"#{int(r['rank_integrated'])} Grid {int(r['grid_id'])}\n({r['district']}, {ERA_LABELS[r['dominant_era']].split(' (')[0]})"
        for _, r in top10.iterrows()
    ]
    bar_colors10 = [ERA_COLORS.get(top10.iloc[i]["dominant_era"], "#888888")
                    for i in range(len(top10))]
    ypos = np.arange(len(top10))
    ax_bar.barh(ypos, top10["integrated_score"].values,
                color=bar_colors10, height=0.65, zorder=2)
    # Value labels right of each bar
    for y, val in zip(ypos, top10["integrated_score"].values):
        ax_bar.text(val + 0.3, y, f"{val:.1f}", va="center",
                    fontsize=FONT_SIZE_ANNOT - 1, color="#333333")
    ax_bar.set_yticks(ypos)
    ax_bar.set_yticklabels(ytick_labels, fontsize=FONT_SIZE_ANNOT - 1)
    ax_bar.set_xlim(60, 100)
    ax_bar.invert_yaxis()
    ax_bar.set_xlabel("Integrated score", fontsize=FONT_SIZE_LABEL - 1)
    ax_bar.set_title("(b) Top-10 priority grids", fontsize=FONT_SIZE_TITLE - 1, pad=4)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)
    ax_bar.grid(axis="x", lw=0.4, alpha=0.5)

    # (c) Paper 1 vs Paper 3 comparison bar
    ax_cmp = fig.add_subplot(gs_row2[0, 2])
    vals_cmp   = [1006, 4127]
    labels_cmp = ["Paper 1\n(PV only)", "Paper 3\n(R5 + PV)"]
    colors_cmp = [PV_COLOR, CARBON_R5PV_COLOR]
    bars_cmp = ax_cmp.bar(labels_cmp, vals_cmp, color=colors_cmp, width=0.5, zorder=2)
    for bar, val in zip(bars_cmp, vals_cmp):
        ax_cmp.text(bar.get_x() + bar.get_width() / 2, val + 40,
                    f"{val:,}\nkt CO₂/yr", ha="center", va="bottom",
                    fontsize=FONT_SIZE_ANNOT, fontweight="bold")
    ax_cmp.set_ylim(0, 5300)
    ax_cmp.set_ylabel("Annual CO₂ savings (kt/yr)", fontsize=FONT_SIZE_LABEL - 1)
    ax_cmp.set_title("(c) Paper 1 vs Paper 3\ncarbon savings comparison",
                     fontsize=FONT_SIZE_TITLE - 1, pad=4)
    # 4.10× bracket annotation
    ax_cmp.annotate("", xy=(1, vals_cmp[1] * 0.95), xytext=(0, vals_cmp[0] * 1.05),
                    arrowprops=dict(arrowstyle="<->", color="#555555", lw=1.0))
    ax_cmp.text(0.5, (vals_cmp[0] + vals_cmp[1]) / 2, "4.10×",
                ha="center", va="center", fontsize=FONT_SIZE_TITLE - 1,
                fontweight="bold", color="#2C3E6B",
                bbox=dict(fc="white", ec="#CCCCCC", boxstyle="round,pad=0.2"))
    despine(ax_cmp)
    ax_cmp.grid(axis="y", lw=0.4, alpha=0.5)

    fig.suptitle(
        "Paper 3 policy summary: integrated retrofit + rooftop PV, Changsha residential core",
        fontsize=FONT_SIZE_TITLE + 1, fontweight="bold", y=0.97)
    out = os.path.join(FIG_DIR, "fig14_policy_summary.png")
    fig.savefig(out, dpi=DPI_PRINT)
    plt.close(fig)
    return out


# ===========================================================================
# Contact sheet
# ===========================================================================

def make_contact_sheet(figure_paths):
    """Tile all 14 figures into a single overview image."""
    from PIL import Image
    imgs = []
    for fp in figure_paths:
        if os.path.exists(fp):
            imgs.append(Image.open(fp))
        else:
            # placeholder
            img = Image.new("RGB", (710, 320), color=(240, 240, 240))
            imgs.append(img)

    ncols = 4
    nrows = (len(imgs) + ncols - 1) // ncols
    thumb_w, thumb_h = 710, 320
    canvas = Image.new("RGB", (ncols * thumb_w + (ncols + 1) * 10,
                                nrows * thumb_h + (nrows + 1) * 10 + 30),
                       color=(255, 255, 255))
    for i, img in enumerate(imgs):
        r, c = divmod(i, ncols)
        thumb = img.resize((thumb_w, thumb_h), Image.LANCZOS)
        x = c * (thumb_w + 10) + 10
        y = r * (thumb_h + 10) + 10 + 30
        canvas.paste(thumb, (x, y))

    out = os.path.join(FIG_DIR, "all_figures_contact.png")
    canvas.save(out, dpi=(150, 150))
    return out


# ===========================================================================
# Main
# ===========================================================================

FIGURE_FUNCS = [
    ("fig01_study_area.png",          fig01_study_area),
    ("fig02_methodology_flowchart.png", fig02_methodology_flowchart),
    ("fig03_era_typology.png",         fig03_era_typology),
    ("fig04_city_baseline.png",        fig04_city_baseline),
    ("fig05_city_retrofit.png",        fig05_city_retrofit),
    ("fig06_pv_spatial.png",           fig06_pv_spatial),
    ("fig07_supply_demand.png",        fig07_supply_demand),
    ("fig08_seasonal_match.png",       fig08_seasonal_match),
    ("fig09_climate_city.png",         fig09_climate_city),
    ("fig10_hc_shift.png",             fig10_hc_shift),
    ("fig11_integrated_grid.png",      fig11_integrated_grid),
    ("fig12_carbon.png",               fig12_carbon),
    ("fig13_cumulative_carbon.png",    fig13_cumulative_carbon),
    ("fig14_policy_summary.png",       fig14_policy_summary),
]

if __name__ == "__main__":
    generated = []
    failed    = []

    for fname, fn in FIGURE_FUNCS:
        print(f"  Generating {fname} ...", end=" ", flush=True)
        try:
            path = fn()
            size_kb = os.path.getsize(path) / 1024
            print(f"OK  ({size_kb:.0f} kB)")
            generated.append((fname, path, size_kb))
        except Exception as e:
            print(f"FAILED: {e}")
            failed.append((fname, str(e)))

    print(f"\n{len(generated)}/14 figures generated.")

    # Contact sheet (requires Pillow)
    print("  Building contact sheet ...", end=" ", flush=True)
    try:
        paths = [p for _, p, _ in generated]
        cs = make_contact_sheet(paths)
        print(f"OK  ({os.path.getsize(cs)/1024:.0f} kB)")
    except Exception as e:
        print(f"FAILED (contact sheet): {e}")

    if failed:
        print("\nFailed figures:")
        for f, e in failed:
            print(f"  {f}: {e}")

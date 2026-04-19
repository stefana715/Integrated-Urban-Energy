"""
style.py — Unified style constants for Paper 3 publication figures.

All generate_all_figures.py modules import from here to ensure visual
consistency across all 14 figures.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Font / global rcParams
# ---------------------------------------------------------------------------
FONT_FAMILY = "Arial"
FONT_SIZE_BASE = 9        # axis tick labels
FONT_SIZE_LABEL = 10      # axis labels
FONT_SIZE_TITLE = 11      # panel / figure titles
FONT_SIZE_LEGEND = 8
FONT_SIZE_ANNOT = 8       # annotations, data labels

DPI_SCREEN = 150
DPI_PRINT = 300

def apply_style():
    """Call once at the top of generate_all_figures.py."""
    mpl.rcParams.update({
        "font.family": FONT_FAMILY,
        "font.size": FONT_SIZE_BASE,
        "axes.labelsize": FONT_SIZE_LABEL,
        "axes.titlesize": FONT_SIZE_TITLE,
        "legend.fontsize": FONT_SIZE_LEGEND,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.minor.visible": False,
        "ytick.minor.visible": False,
        "figure.dpi": DPI_SCREEN,
        "savefig.dpi": DPI_PRINT,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
        "pdf.fonttype": 42,        # embeds fonts in PDF
        "ps.fonttype": 42,
    })

# ---------------------------------------------------------------------------
# Figure sizes  (width × height in inches; journal 1-col ≈ 3.5", 2-col ≈ 7.1")
# ---------------------------------------------------------------------------
FIGSIZE_SINGLE = (3.5, 3.0)
FIGSIZE_WIDE   = (7.1, 3.2)
FIGSIZE_MAP    = (7.1, 5.0)
FIGSIZE_TALL   = (7.1, 5.5)
FIGSIZE_FLOW   = (7.1, 4.5)

# ---------------------------------------------------------------------------
# Color palettes
# ---------------------------------------------------------------------------

# Era colours (warm → cool, early → recent)
ERA_COLORS = {
    "era1": "#D94F3D",   # deep red
    "era2": "#F0A500",   # amber
    "era3": "#3A86C8",   # steel blue
}
ERA_LABELS = {
    "era1": "Era 1 (pre-2000)",
    "era2": "Era 2 (2000–09)",
    "era3": "Era 3 (2010–20)",
}

# Typology colours
TYPOLOGY_COLORS = {
    "LowRise":  "#7BBFA5",   # teal-green
    "MidRise":  "#4A90D9",   # mid blue
    "HighRise": "#2C3E6B",   # dark navy
}

# Retrofit measure colours (R1–R5)
RETROFIT_COLORS = {
    "R1_Wall":         "#ABDDA4",
    "R2_Window":       "#FDAE61",
    "R3_Roof":         "#74ADD1",
    "R4_Infiltration": "#D73027",
    "R5_Combined":     "#4D4D4D",
}

# Climate scenario order and colours
SCENARIO_ORDER  = ["Current", "2050_SSP245", "2050_SSP585", "2080_SSP245", "2080_SSP585"]
SCENARIO_LABELS = {
    "Current":     "Current",
    "2050_SSP245": "2050 SSP2-4.5",
    "2050_SSP585": "2050 SSP5-8.5",
    "2080_SSP245": "2080 SSP2-4.5",
    "2080_SSP585": "2080 SSP5-8.5",
}
SCENARIO_COLORS = {
    "Current":     "#555555",
    "2050_SSP245": "#6BAED6",
    "2050_SSP585": "#08519C",
    "2080_SSP245": "#FD8D3C",
    "2080_SSP585": "#BD0026",
}

# Energy end-use
HEATING_COLOR = "#4575B4"
COOLING_COLOR = "#D73027"
OTHER_COLOR   = "#878787"
PV_COLOR      = "#F9C74F"
NET_COLOR     = "#577590"

# Carbon / pathway colours
CARBON_BASELINE_COLOR = "#D73027"
CARBON_R5PV_COLOR     = "#2CA02C"
CARBON_STEP_COLOR     = "#FF7F0E"
CARBON_SSP585_COLOR   = "#9467BD"

# Neutral
GRID_FACE_COLOR = "#F5F5F5"
HIGHLIGHT_COLOR = "#FFD700"  # gold — for top-50 grids

# ---------------------------------------------------------------------------
# Discrete colormaps (for choropleth maps)
# ---------------------------------------------------------------------------
from matplotlib.colors import ListedColormap

ERA_CMAP = ListedColormap([ERA_COLORS["era1"], ERA_COLORS["era2"], ERA_COLORS["era3"]])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def savefig(fig, path, dpi=DPI_PRINT):
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def label_bar(ax, bars, fmt="{:.0f}", fontsize=FONT_SIZE_ANNOT, color="black", pad=0.5):
    """Add value labels above each bar."""
    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + pad,
            fmt.format(h),
            ha="center", va="bottom",
            fontsize=fontsize, color=color,
        )


def despine(ax, spines=("top", "right")):
    for s in spines:
        ax.spines[s].set_visible(False)

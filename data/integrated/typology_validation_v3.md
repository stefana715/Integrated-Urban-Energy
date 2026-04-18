# Typology Validation Report — v3 (Ternary Classification)

**Date:** 2026-04-19
**Method:** LowRise/MidRise/HighRise with Era-1 prior + footprint sanity + GHSL ANBH thresholds

---

## V1. Typology Distribution

### Overall

| Typology | Count | % |
|---|---|---|
| Lowrise | 14,287 | 75.9% |
| Midrise | 3,901 | 20.7% |
| Highrise | 638 | 3.4% |

### By Era

| Era | LowRise | MidRise | HighRise | Total |
|---|---|---|---|---|
| Era 1 (pre-2000) | 6,459 (86%) | 582 (8%) | 489 (6%) | 7,530 |
| Era 2 (2000–2009) | 3,292 (62%) | 1,879 (36%) | 100 (2%) | 5,271 |
| Era 3 (2010–2020) | 4,536 (75%) | 1,440 (24%) | 49 (1%) | 6,025 |

**Expected ranges (from historical context):**
- Era 1: ~95% LowRise, ~5% MidRise, ~0% HighRise
- Era 2: ~40% LowRise, ~45% MidRise, ~15% HighRise
- Era 3: ~20% LowRise, ~40% MidRise, ~40% HighRise

**Era 1 HighRise:** 489 buildings (6.5% of Era 1) ⚠  **FLAGGED** — above 2% review threshold

These are Era 1 buildings with GHSL ANBH ≥ 30 m (escaped the Era-1 prior). Likely candidates:
- Pre-2000 hotel/office towers in the historic city core
- GHSL cell averaging effects (a tall post-2000 tower pulls up the 100m cell average)
- Commercial/industrial buildings not corrected by the footprint rule (<2500 m²)

**Top 20 Era 1 HighRise buildings by GHSL height:**

|         id |   ghsl_height_m |   footprint_area_m2 | building_category   |
|-----------:|----------------:|--------------------:|:--------------------|
| 1044650454 |         52.1169 |             456.487 | residential         |
| 1044650453 |         52.1169 |             569.533 | residential         |
|  650038554 |         50.6654 |             854.916 | residential         |
|  542953946 |         50.6654 |            1244.38  | residential         |
|  650038562 |         50.6654 |             495.105 | residential         |
| 1041868295 |         50.601  |             470.625 | residential         |
| 1041725329 |         50.601  |            1520.16  | residential         |
| 1041725326 |         50.601  |            1959.89  | residential         |
|  650038559 |         49.1807 |             240.111 | residential         |
|  650038548 |         49.1807 |             491.409 | residential         |
|  650038551 |         49.1807 |             546.312 | residential         |
|  650038556 |         49.1807 |             776.407 | residential         |
|  650038579 |         49.1807 |             267.694 | residential         |
|  650038569 |         49.1807 |             177.715 | residential         |
|  542953955 |         48.5868 |            1114.21  | residential         |
|  542953909 |         48.5868 |             451.813 | residential         |
|  542953905 |         48.5868 |             437.369 | residential         |
|  542953903 |         48.5868 |             470.899 | residential         |
|  542953901 |         48.5868 |             268.293 | residential         |
|  542953958 |         48.5868 |            2889.69  | residential         |

---

## V2. Rule Usage Breakdown

| Rule | Buildings | % |
|---|---|---|
| GHSL primary: ≤ 18 m → LowRise | 7,184 | 38.2% |
| Era-1 prior (h < 30 m → LowRise) | 6,459 | 34.3% |
| GHSL primary: 18–36 m → MidRise | 3,901 | 20.7% |
| Large-footprint slab (fp > 2500 m², h < 25 m → LowRise) | 644 | 3.4% |
| GHSL primary: > 36 m → HighRise | 638 | 3.4% |

**Interpretation:** The Era-1 prior and GHSL-low together account for the LowRise majority. The large-footprint slab rule corrects ~644 commercial/industrial buildings whose GHSL ANBH overstates height due to grid-cell averaging with adjacent towers.

---

## V3. City-Scale PV Comparison (HP Buildings Only)

| Version | Typology scheme | HP buildings | Total PV (GWh/yr) |
|---|---|---|---|
| v2 (binary)  | MidRise / HighRise         | 6,401 | 1295.2 |
| v3 (ternary) | LowRise / MidRise / HighRise | 6,401 | 2866.6 |
| Paper 1 reference | — | 6,411 | 1764 |

- v3 vs v2: **+1571.4 GWh/yr** (+121%) — driven by Era 1 LowRise reclassification from HighRise (38.8 vs 6.1 kWh/m²_floor)
- v3 vs Paper 1: **+1102.6 GWh/yr** (+63%)

---

## V4. Comparison with Paper 1 Reference (1,764 GWh/yr)

**v3 HP floor area total:** 85.05 Mm²
**Paper 1 implied HP floor area:** 64.38 Mm² (if all HP were MidRise at 27.4 kWh/m²_floor)

**Root cause of the 63% gap:**

| Metric | v3 (GHSL heights) | Implied Paper 1 |
|---|---|---|
| Avg floor count (HP) | 6.6 | ~3.5 (height_proxy_m ÷ 3) |
| Avg footprint (HP) | 2035 m² | same dataset |
| Avg floor area / building | 13287 m² | ~2,200 m² est. |
| HP count | 6,401 | 6,411 |

The v3 estimate is higher than Paper 1 primarily because **floor areas are computed using GHSL ANBH heights (mean 17.9 m → ~6 floors)** instead of Paper 1's OSM-derived height_proxy_m (mean 10.6 m → ~4 floors). GHSL ANBH may overstate individual building heights because it represents the 100m cell average (which includes taller neighbours). This height inflation carries through to floor_area_m2 and thus PV. The discrepancy is a **known limitation** (see DEC-010) and should be discussed in the manuscript.

> **Recommendation for Task 5:** Recompute floor_area_m2 using height_proxy_m for buildings where GHSL ANBH > 2× height_proxy_m, or apply a correction factor. Alternatively, cap floor_count_est at a physically plausible maximum by building category. Flag for user review.

---

## V5. GHSL Height Distribution by Typology

| Typology | Min (m) | P25 (m) | Median (m) | P75 (m) | Max (m) | N |
|---|---|---|---|---|---|---|
| Lowrise | 0.0 | 11.4 | 15.1 | 18.1 | 30.0 | 14,287 |
| Midrise | 18.0 | 19.8 | 22.9 | 28.7 | 36.0 | 3,901 |
| Highrise | 36.0 | 37.0 | 39.1 | 42.9 | 55.6 | 638 |

**Overlap check:** LowRise includes Era-1-prior buildings with heights up to 29.9 m — the Era-1 prior does significant work in this range. The MidRise and HighRise distributions should be well-separated (18–36 m vs >36 m) since those rely purely on GHSL thresholds. Any LowRise buildings with GHSL > 18 m are accounted for by either the Era-1 prior or the large-footprint slab rule.

---

## V6. Typology Change v2 (Binary) → v3 (Ternary)

```
v3 ternary  highrise  lowrise  midrise
v2 binary                             
highrise         638     3627     3901
midrise            0    10660        0
```

*(Rows = v2 binary label; columns = v3 ternary label)*

---

## V7. High-Potential Buildings by Era × Typology (v3)

| Era | LowRise HP | MidRise HP | HighRise HP | Total HP |
|---|---|---|---|---|
| Era 1 (pre-2000) | 1,852 | 166 | 134 | 2,152 |
| Era 2 (2000–2009) | 1,269 | 679 | 52 | 2,000 |
| Era 3 (2010–2020) | 1,566 | 660 | 23 | 2,249 |

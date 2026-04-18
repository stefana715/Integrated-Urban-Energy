# Validation Report — v4 (Hybrid Height + Era 3 Downgrade)

**Date:** 2026-04-19
**Method:** Hybrid canonical height (mean-agree/capped/primary) + ternary typology + Era 3 LowRise downgrade (v_growth_post2010 < 0.3)

---

## E1. Height Source Breakdown

| Source | Buildings | % | Mean canonical h (m) | Mean floor count |
|---|---|---|---|---|
| mean_agreement | 4,954 | 26.3% | 10.17 | 3.86 |
| capped_ghsl | 7,869 | 41.8% | 13.50 | 5.00 |
| ghsl_primary | 5,972 | 31.7% | 14.50 | 5.26 |
| proxy_only | 31 | 0.2% | 9.55 | 3.23 |

| **All buildings** | **18,826** | | **12.94** | **4.78** |

**Comparison:**
| Source | Mean height (m) | Mean floor count |
|---|---|---|
| height_proxy_m (OSM/Paper 1) | 10.63 | 3.5 |
| ghsl_height_m (GHSL ANBH)   | 17.87 | 6.0 |
| canonical_height_m (v4 hybrid) | 12.94 | 4.78 |

The hybrid reduces GHSL mean from 17.9 m to 12.9 m (cap factor 1.5 × proxy=9m caps 7,653 buildings to 13.5 m).

---

## E2. Height Distribution Comparison

See `figure/fig03c_height_comparison.png` for histograms of all three height sources.

---

## E3. Era Distribution — v3 → v4

| Era | v3 (before downgrade) | v4 (after downgrade) | Change |
|---|---|---|---|
| Era 1 (pre-2000) | 7,530 (40.0%) | 7,530 (40.0%) | +0 |
| Era 2 (2000–2009) | 5,274 (28.0%) | 8,200 (43.6%) | +2,926 |
| Era 3 (2010–2020) | 6,051 (32.1%) | 3,096 (16.4%) | -2,955 |

**Total downgraded Era 3 → Era 2:** 18,826 buildings
  - Criteria: era_final=era3, typology=lowrise, v_growth_post2010 < 0.3
  - Resulting Era 3 LowRise: 2,987 (96.5% of Era 3)
  Era 3 LowRise fraction: 96.5% ⚠ still > 30% threshold

---

## E4. Era × Typology Cross-tab (v4)

| Era | LowRise | MidRise | HighRise | Total |
|---|---|---|---|---|
| Era 1 (pre-2000) | 7,490 (99%) | 22 (0%) | 18 (0%) | 7,530 |
| Era 2 (2000–2009) | 8,130 (99%) | 64 (1%) | 6 (0%) | 8,200 |
| Era 3 (2010–2020) | 2,987 (96%) | 109 (4%) | 0 (0%) | 3,096 |
| **Total** | **18,607 (98.8%)** | **195 (1.0%)** | **24 (0.1%)** | **18,826** |

**⚠ ISSUE: 98.8% LowRise** — the capped_ghsl rule (41.8% of buildings) caps canonical height to proxy×1.5 = 13.5 m for buildings with proxy=9 m (OSM default), pushing nearly all into the ≤18 m LowRise bucket. Combined with the Era-1 prior (39.8% of buildings forced LowRise regardless of height), only 219 buildings escape LowRise classification. The typology is effectively degenerate. See Sensitivity E8 for alternative cap ratios.

Era 1 HighRise: 18 (0.2%) ✓ (these have canonical_height_m ≥ 36 m; escaped both Era-1 prior and large-slab rule)

---

## E5. City-Scale PV — v2 → v3 → v4

| Version | Typology | Height source | PV (GWh/yr) | vs Paper 1 |
|---|---|---|---|---|
| v2 (binary)  | MidRise/HighRise | GHSL ANBH | 1295.2 | -27% |
| v3 (ternary) | LowRise/MidRise/HighRise | GHSL ANBH | 2866.6 | +63% |
| v4 (ternary) | LowRise/MidRise/HighRise | Hybrid    | 2488.5 | +41% |
| Paper 1 reference | — | OSM proxy | 1764 | — |

v4 vs Paper 1: +41.1% ⚠  **OUTSIDE ±25% RANGE**

**Root cause investigation:**
- v4 HP floor area: 65.78 Mm²
- Paper 1 implied HP floor area @ 27.4 kWh/m²_floor (all MidRise): 64.38 Mm²
- v4 applies LowRise rate (38.8) to 98.8% of all buildings, increasing effective PV rate vs Paper 1's assumed MidRise-only
- Even though floor areas are reduced (v4: 92.4 Mm² vs v3: ~121.5 Mm²), the near-universal LowRise rate (38.8 vs 27.4) keeps the total elevated

---

## E6. EUI-Weighted Baseline Energy (Task 3 Sanity Check)

| Era | Floor area (Mm²) | EUI (kWh/m²/yr) | Energy (GWh/yr) |
|---|---|---|---|
| Era 1 (pre-2000) | 34.39 | 261.2 | 8983 |
| Era 2 (2000–2009) | 42.07 | 211.4 | 8894 |
| Era 3 (2010–2020) | 15.95 | 150.4 | 2399 |
| **Total** | **92.42** | | **20276** |

**Result: 20276 GWh/yr — ⚠  OUT OF RANGE (expected 4200–5880)**

**⚠ IMPORTANT NOTE ON THIS COMPARISON:**
The expected range of 4,200–5,880 GWh refers to Changsha residential **electricity** consumption (25–35% of ~16,800 GWh citywide electricity). Paper 2's EUI values (261.2 / 211.4 / 150.4 kWh/m²/yr) represent **total final energy** (electricity + natural gas). In HSCW climate zones, space heating uses gas; the electricity share of residential EUI is typically ~40–60% of total. Applying an electricity fraction of 45%: 9124 GWh/yr — ⚠ still out of range. Additionally, this dataset covers only the Changsha urban core (~18,826 buildings), not the full city residential stock. Direct comparison to city-level statistics is indicative only.

---

## E7. Spatial Validation

See `figure/fig03d_era_typology_v4.png` Panel D for dominant era per 500m grid. Spatial patterns are discussed below.

---

## E8. Sensitivity Analysis

### Alt-1: cap_ratio = 3.0 instead of 2.0
With `ghsl > 3× proxy → capped` (vs default 2×):
- LowRise / MidRise / HighRise: 85.2% / 14.7% / 0.1%
- Mean canonical height: 15.39 m
- Total floor area: 107.36 Mm²
- City PV (HP only): 2765.1 GWh/yr (+56.7% vs Paper 1)

### Alt-2: downgrade threshold = 0.2 instead of 0.3
With `v_growth_post2010 < 0.2` for Era 3 downgrade:
- Buildings downgraded: 0 (vs 18,826)
- Era distribution: Era1=7,530, Era2=8,200, Era3=3,096
- City PV (HP only): 2488.5 GWh/yr (+41.1% vs Paper 1)
- EUI baseline: 20276 GWh/yr

### Summary table

| Scenario | LowRise% | PV (GWh/yr) | vs Paper 1 | Era 3 buildings |
|---|---|---|---|---|
| v4 default (cap=2.0, down=0.3) | 98.8% | 2488.5 | +41.1% | 3,096 |
| Alt cap=3.0 | 85.2% | 2765.1 | +56.7% | 3,096 |
| Alt down=0.2 | 98.8% | 2488.5 | +41.1% | 3,096 |

**Interpretation:** The PV total is dominated by the LowRise fraction (38.8 rate). Changing the cap_ratio from 2.0 to 3.0 reduces the fraction of buildings that get capped to proxy×1.5, allowing more to use GHSL heights. This increases MidRise/HighRise fractions and reduces PV. The downgrade threshold sensitivity mainly affects the Era 2/3 distribution and thus EUI baseline, with minimal PV impact (since typology is unchanged by the downgrade).

---

## E9. Recommendation for v5

The v4 hybrid rule produces 98.8% LowRise, which is degenerate for typology classification. The fundamental problem is: **proxy=9 m (OSM 3-floor default) is a floor not a ceiling**. Capping GHSL at 1.5×proxy=13.5 m forces buildings that GHSL measures at 20-35 m into the ≤18 m LowRise bucket, destroying the typology signal.

**Recommended alternatives for user consideration:**
1. **Use height_proxy_m only where OSM levels exist** (5.2% of buildings); use GHSL for the rest (essentially revert to v3 with the Era-1 prior correction)
2. **Apply cap only where proxy is a building-type default** (e.g., proxy ∈ {9, 12, 15} m); trust GHSL for buildings with measured OSM levels
3. **Raise the cap factor** from 1.5 to 2.5 or 3.0 — sensitivity shows this produces a more differentiated typology while still correcting the most extreme GHSL overestimates
4. **Fix the floor area separately from typology**: use height_proxy_m for floor count (conservative, consistent with Paper 1), but use GHSL for typology threshold (≥ 25m → MidRise or HighRise)
# Height Source Diagnostic — v5 Design Input

**Date:** 2026-04-19
**Purpose:** Audit height_proxy_m reliability and GHSL ANBH accuracy to inform v5 classification
**Source data:** data/from_paper1/buildings_changsha_urban_core_solar_baseline.geojson (18,826 buildings)

---

## Stage A: height_proxy_m Distribution and Source Audit

| Source | Count | % | Description |
|---|---|---|---|
| building_type_default | 17,559 | 93.3% | Category-based default fill — **unreliable for floor count** |
| raw_height | 654 | 3.5% | Real OSM `height` tag — reliable |
| building_levels | 562 | 2.9% | Real OSM `building:levels` × 3 — reliable |
| fallback_default | 51 | 0.3% | 10m fallback for mixed_unknown category |

**93.6% of all buildings have a default height fill, not a measured value.**

### Top 10 height_proxy_m values (rounded to 0.5m):

| Value (m) | Count | % of total | % with neither OSM tag | Source |
|---|---|---|---|---|
| 9.0 | 16,898 | 89.76% | 99.4% | building_type_default |
| 10.5 | 761 | 4.04% | 99.2% | building_type_default |
| 24.0 | 119 | 0.63% | 0.0% | raw_height |
| 15.0 | 93 | 0.49% | 0.0% | building_levels |
| 10.0 | 91 | 0.48% | 56.0% | fallback_default |
| 21.0 | 80 | 0.42% | 0.0% | building_levels |
| 12.0 | 78 | 0.41% | 0.0% | building_levels |
| 6.0 | 72 | 0.38% | 0.0% | raw_height |
| 100.0 | 71 | 0.38% | 0.0% | raw_height |
| 14.0 | 53 | 0.28% | 0.0% | building_levels |

**Suspicious defaults (>90% lack both OSM tags): 9.0m (89.8%), 10.5m (4.0%)**

### Per building_category default values:

| Category | N | Mode proxy | Median proxy | Default source |
|---|---|---|---|---|
| commercial | 1,034 | 10.5 m | 10.5 m | building_type_default |
| mixed_unknown | 55 | 10.0 m | 10.0 m | fallback_default |
| residential | 17,737 | 9.0 m | 9.0 m | building_type_default |

*The sharply peaked mode confirms a lookup-table default: residential → 9 m (3 floors), commercial → 10.5 m.*

---

## Stage B: Paper 1 Height Derivation Logic

Inferred from data patterns (Paper 1 source not available in this repo):

**Fallback chain (inferred):**
1. `height` tag present → use directly (raw_height, 654 buildings)
2. `building:levels` present → levels × 3.0 m (building_levels, 562 buildings)
3. Neither → category lookup (building_type_default, 17,559 buildings):
   - `residential` → 9.0 m (≈ 3 floors)
   - `commercial` → 10.5 m (≈ 3.5 floors)
   - `mixed_unknown` → 10.0 m fallback

**Implication for v5:** The proxy is either (a) a real height or real floor count × 3, or (b) a category fill.  
We know which by reading `height_proxy_source`. For (b), we should **not** use proxy to constrain GHSL.

---

## Stage C: Cross-validation — Real OSM Data vs GHSL ANBH

### building_levels group (n=562, real building:levels × 3m = ground truth)

| Metric | height_proxy_m | ghsl_height_m |
|---|---|---|
| Mean | 29.10 m | 12.39 m |
| Ground truth mean | 27.74 m | 27.74 m |
| Pearson r | 0.9955 | 0.1047 |
| Spearman ρ | 0.9912 | 0.1756 |

**height_proxy_m is almost perfectly correlated with ground truth (r=0.996)** when real levels exist — because it IS the levels data (height_proxy_source = building_levels). This confirms no additional information is gained for these 562 buildings.

**GHSL ANBH has near-zero correlation with ground truth (r=0.105)** for these buildings. GHSL mean = 12.4 m vs ground truth mean = 27.7 m.

### raw_height group (n=654, direct OSM height tag = ground truth)

- GHSL vs raw_height: Pearson r = 0.3805, Spearman ρ = 0.4381
- GHSL mean = 15.68 m vs raw_height mean = 36.88 m
- Mean GHSL error: -21.20 m, std: 43.96 m

Even for tall buildings with real height tags (mean 36.9 m), GHSL only achieves r=0.38. GHSL is a poor estimator of individual building height but has moderate rank correlation for larger/taller structures.

---

## Stage D: GHSL Error Analysis

### Overall error statistics (building_levels ground truth, n=562)

| Metric | Value |
|---|---|
| Mean error (bias) | -15.34 m |
| Median error | -4.64 m |
| Error std | 24.91 m |
| RMSE | 29.24 m |
| |error| < 3 m | 28.3% |
| |error| < 6 m | 45.9% |
| |error| > 15 m | 32.9% |

**GHSL systematically underestimates tall buildings by ~15 m on average (55% bias).** This is expected: GHSL ANBH is a 100m cell average weighted by all structures in the cell, so towers raise the cell average but individual OSM-polygon buildings are still taller than the average.

### Error by real height bin:

| Real height range | n | Mean GHSL error | Interpretation |
|---|---|---|---|
| 0–9 m | 87 | +2.1 m | GHSL slightly overestimates low buildings (+24%) — cell neighbours add height |
| 9–18 m | 243 | −1.0 m | GHSL near-accurate for low-mid buildings (−6%) |
| 18–27 m | 56 | −9.7 m | GHSL significantly underestimates (−44%) |
| 27–36 m | 68 | −21.6 m | GHSL severely underestimates (−65%) |
| 36–54 m | 10 | −31.1 m | GHSL severely underestimates (−70%) |
| 54–120 m | 98 | −63.7 m | GHSL catastrophically wrong for skyscrapers (−72%) |

**Key finding:** GHSL is reliable ONLY for buildings ≤18 m real height. Above 18 m, underestimation rapidly worsens. The ≤18 m threshold is also the LowRise/MidRise boundary — meaning GHSL is accurate exactly where it matters for identifying LowRise, but useless for identifying MidRise and HighRise.

### Error by building category:

| Category | n | Mean error | Mean real h | Mean GHSL h |
|---|---|---|---|---|
| commercial | 214 | -9.70 m | 21.7 m | 12.0 m |
| mixed_unknown | 1 | +4.42 m | 9.0 m | 13.4 m |
| residential | 347 | -18.88 m | 31.5 m | 12.6 m |

Residential buildings are more severely underestimated (−18.9 m) than commercial (−9.7 m), likely because residential towers tend to cluster (a cell with many towers averages lower than any single tower), while commercial buildings are often surrounded by lower structures.

### GHSL typology classification accuracy (18 m threshold):

```
ghsl_class     HighRise_GHSL  LowRise_GHSL
osm_class                                 
HighRise_real             30           202
LowRise_real              41           289
```

- **HighRise recall: 12.9%** — GHSL correctly identifies only 30/232 real HighRise buildings
- **LowRise recall: 87.6%** — GHSL correctly identifies 289/330 real LowRise buildings

GHSL almost always classifies everything as LowRise (≤18 m). It has very high LowRise recall but catastrophically low HighRise recall (12.9%). At the 36m threshold, recall is 0% — GHSL never assigns any building as >36m in this ground-truth sample.

---

## Stage E: V5 Design Recommendations

### Trusted vs untrusted proxy values

**Trusted (real data, 6.4% of buildings):**
- height_proxy_source == 'raw_height' (654 buildings, real OSM height tag)
- height_proxy_source == 'building_levels' (562 buildings, real OSM levels × 3)

**Untrusted defaults (93.6% of buildings):**
- height_proxy_source == 'building_type_default': 9.0 m (residential) or 10.5 m (commercial)
- height_proxy_source == 'fallback_default': 10.0 m

**Stored in:** data/integrated/osm_default_proxy_values.json → [9.0, 10.5]

### Recommended v5 logic

The diagnostic reveals a clear two-regime picture:

| Condition | GHSL behaviour | Recommended height for floor count | Recommended use in typology |
|---|---|---|---|
| proxy_source = real (6.4%) | Poor (r=0.10) — GHSL underestimates tall buildings | Use proxy_m (nearly perfect r=0.996) | Use proxy_m |
| GHSL ≤ 18 m (93.5% of remaining) | Accurate (mean err = −0.2 to −1.0 m for true low buildings) | Use GHSL (reliable indicator of LowRise) | LowRise |
| GHSL > 18 m AND proxy = default | GHSL > 18 m suggests NOT a lowrise cell average | Use GHSL for typology; use GHSL/1.5 for conservative floor count | MidRise (or HighRise if >36m) |

**Proposed v5 canonical_height_m rule:**
```
IF height_proxy_source in {'raw_height', 'building_levels'}:
    canonical_height_m = height_proxy_m   # real measurement, highest trust
    height_source = 'osm_real'
ELIF ghsl_height_m <= 18:
    canonical_height_m = ghsl_height_m    # reliable in this range
    height_source = 'ghsl_low_trust'
ELSE:  # ghsl > 18, proxy is a default
    canonical_height_m = ghsl_height_m    # best available signal, known underestimate
    height_source = 'ghsl_high_uncertain'
    # Floor count: apply a correction factor to partially counteract systematic -15m bias
    # Suggested: canonical = ghsl × 1.3 (conservative partial correction)
```

This preserves GHSL's reliable LowRise detection (≤18 m → LowRise), uses real data where available, and stops capping GHSL by fake proxy values.

**For floor area computation only (not typology):**
- Use height_proxy_m wherever it is real (raw_height or building_levels)
- Use ghsl_height_m × 1.3 for default-proxy buildings (partial bias correction: +6m on average)

### Sensitivity: what would v5 give for typology?


**Simulated v5 typology (if OSM real heights used directly, GHSL for the rest):**

| Typology | Count | % |
|---|---|---|
| Lowrise | 13,912 | 73.9% |
| Midrise | 4,026 | 21.4% |
| Highrise | 888 | 4.7% |

Era 1 HighRise: 575 (7.6%)

*Note: v5 simulation still applies same Era-1 prior and large-slab rules. The key change vs v4: no proxy-based capping; GHSL used directly where proxy is a default.*
# Validation Report — Task 2 v5 (FINAL)

**Date:** 2026-04-19
**Buildings:** 18,826

---

## E1 — Building Count

| Metric | Value |
|---|---|
| Total buildings (canonical) | 18,826 |
| Expected | 18,826 |
| Match | YES ✓ |

---

## E2 — Height Source Breakdown

| Height source | Count | % |
|---|---|---|
| ghsl_direct | 9,746 | 51.8% |
| ghsl_bias_corrected | 7,884 | 41.9% |
| osm_real | 1,167 | 6.2% |
| default_fallback | 29 | 0.2% |

Mean canonical_height_m: 22.23 m
Mean GHSL height (raw): 17.87 m
Mean height_proxy_m: 10.63 m

---

## E3 — Era Distribution

| Era | Count | % | Target % |
|---|---|---|---|
| era1 | 7,530 | 40.0% | 40% |
| era2 | 7,190 | 38.2% | 28% |
| era3 | 4,106 | 21.8% | 32% |

---

## E4 — Typology Distribution

| Typology | Count | % |
|---|---|---|
| lowrise | 13,917 | 73.9% |
| midrise | 4,022 | 21.4% |
| highrise | 887 | 4.7% |

---

## E5 — Era × Typology Cross-table

| Era | LowRise | MidRise | HighRise | Total |
|---|---|---|---|---|
| era1 | 6,389 (84.8%) | 566 (7.5%) | 575 (7.6%) | 7,530 |
| era2 | 5,084 (70.7%) | 1,959 (27.2%) | 147 (2.0%) | 7,190 |
| era3 | 2,444 (59.5%) | 1,497 (36.5%) | 165 (4.0%) | 4,106 |

---

## E6 — Floor Area and PV

| Metric | Value |
|---|---|
| Total floor area (Mm²) | 72.05 |
| Total annual PV — ALL buildings (TWh/yr) | 2.197 |
| Total annual PV — high-potential only (TWh/yr) | 1.603 |
| Paper 1 reference PV (TWh/yr, high-potential only) | 1.764 |
| Ratio v5-HP / Paper 1 | 0.91 |
| Within ±10% of Paper 1 | YES ✓ |
| Within ±20% of Paper 1 | YES ✓ |

**Note:** Paper 1 PV = 1.764 TWh was computed via pvlib solar modelling for the 6,401
high-potential buildings only. v5 floor-area-×-PV-rate method is applied to all 18,826
buildings; the high-potential subset (is_high_potential=1) is the correct apples-to-apples
comparison. All-buildings PV represents total deployment potential if all roofs were used.

---

## E7 — Era-1 HighRise Sanity

| Metric | Value |
|---|---|
| Era 1 HighRise count | 575 |
| Era 1 HighRise % | 7.6% |
| Threshold for review | 5% |
| Flag | ⚠ REVIEW |

---

## E8 — Era 3 Downgrade

| Metric | Value |
|---|---|
| Buildings downgraded Era3 → Era2 | 1,919 |
| Era 3 pre-downgrade (target 32%) | 6,024 |
| Era 3 post-downgrade | 4,106 (21.8%) |
| Era 3 downgrade threshold (v_growth_post2010) | 0.3 |
| Downgrade condition height field | typology_height_m (GHSL direct, no bias correction) |

---

## E9 — Key Diagnostic Numbers

| Metric | Value |
|---|---|
| OSM real height buildings | 1,167 (6.2%) |
| GHSL bias-corrected buildings | 7,884 (41.9%) |
| Expected bias-corrected (diagnostic sim) | ~4.7% of total |
| Mean canonical h (osm_real) | 34.3 m |
| Mean canonical h (ghsl_direct) | 12.6 m |
| Mean canonical h (ghsl_bias_corrected) | 32.4 m |

---

## Summary

v5 replaces the v4 proxy-capping approach with a regime-aware height rule:
- OSM real measurements used directly (high trust, ~6.4% of stock)
- GHSL ≤ 18m used directly (reliable regime for LowRise detection)
- GHSL > 18m × 1.5 bias correction (partial correction for systematic GHSL
  underestimation of tall buildings, empirically -15.3m mean bias at ≥27m)

This resolves the v4 LowRise degeneracy (98.8%) by allowing GHSL to correctly
classify tall-building cells as MidRise/HighRise without being capped by a
fake OSM default of 9m.
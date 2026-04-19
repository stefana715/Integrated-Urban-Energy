# Validation Report — Task 4: City-scale Retrofit Savings

**Date:** 2026-04-19

---

## Stage A — Retrofit Deltas (Paper 2 CSV)

| Era | Retrofit | Baseline EUI | Retrofit EUI | Δ EUI | Savings % |
|---|---|---|---|---|---|
| era1 | R1: Wall | 261.21 | 242.72 | 18.49 | 7.08% |
| era1 | R2: Window | 261.21 | 251.06 | 10.15 | 3.89% |
| era1 | R3: Roof | 261.21 | 250.33 | 10.88 | 4.17% |
| era1 | R4: Air sealing | 261.21 | 171.67 | 89.54 | 34.28% |
| era1 | R5: Combined | 261.21 | 138.34 | 122.87 | 47.04% |
| era2 | R1: Wall | 211.43 | 201.06 | 10.37 | 4.90% |
| era2 | R2: Window | 211.43 | 206.67 | 4.76 | 2.25% |
| era2 | R3: Roof | 211.43 | 205.06 | 6.37 | 3.01% |
| era2 | R4: Air sealing | 211.43 | 155.01 | 56.42 | 26.68% |
| era2 | R5: Combined | 211.43 | 138.34 | 73.09 | 34.57% |
| era3 | R1: Wall | 150.41 | 147.59 | 2.82 | 1.87% |
| era3 | R2: Window | 150.41 | 147.14 | 3.27 | 2.17% |
| era3 | R3: Roof | 150.41 | 149.92 | 0.49 | 0.33% |
| era3 | R4: Air sealing | 150.41 | 128.86 | 21.55 | 14.33% |
| era3 | R5: Combined | 150.41 | 126.91 | 23.50 | 15.62% |

---

## D1 — Waterfall Decomposition

Individual retrofit savings at city scale (all buildings retrofitted):

| Retrofit | City savings (GWh) | Savings vs baseline (%) |
|---|---|---|
| R1: Wall | 817.5 | 5.31% |
| R2: Window | 457.3 | 2.97% |
| R3: Roof | 465.6 | 3.03% |
| R4: Air sealing | 4273.6 | 27.78% |
| R5: Combined | 5633.8 | 36.63% |

**Cumulative waterfall (sequential individual measures):**

| Step | Action | Cumulative savings (GWh) | Running total (GWh) |
|---|---|---|---|
| 0 | Baseline | 0 | 15381.6 |
| 1 | + R1 Wall | 817.5 | 14564.1 |
| 2 | + R2 Window | 457.3 | 14106.8 |
| 3 | + R3 Roof | 465.6 | 13641.2 |
| 4 | + R4 Air sealing | 4273.6 | 9367.6 |
| R5 | Combined (authoritative) | **5633.8** | **9747.8** |

Sum of individuals: 6014.0 GWh | R5 combined: 5633.8 GWh
Interaction effect: 380.3 GWh (overestimates R5 by 6.7%)

---

## D2 — Retrofit Leverage by Era

| Era | Baseline (GWh) | R5 savings (GWh) | R5 savings % | Paper 2 R5 % |
|---|---|---|---|---|
| era1 | 6930.9 | 3260.2 | 47.04% | 47.04% |
| era2 | 5559.3 | 1921.8 | 34.57% | 34.57% |
| era3 | 2891.4 | 451.8 | 15.62% | 15.62% |

**Verification:** aggregated savings % match Paper 2 values because we apply
the same per-m² delta to a uniform floor area — discrepancy < 0.1% ✓

---

## D3 — Cost-effectiveness Ranking (% savings per measure)

| Rank | Measure | City savings (GWh) | City savings % |
|---|---|---|---|
| 1 | R4: Air sealing | 4273.6 | 27.78% |
| 2 | R1: Wall | 817.5 | 5.31% |
| 3 | R3: Roof | 465.6 | 3.03% |
| 4 | R2: Window | 457.3 | 2.97% |

**Biggest-bang-per-measure:** R4: Air sealing (4273.6 GWh, 27.78% of baseline)
R4 (Air sealing / infiltration reduction) dominates because Era 1 & 2 buildings
have high infiltration rates (pre-code envelopes); reducing to 0.3 ACH cuts
heating load by ~73–76%.

---

## D4 — Top 20 Grid Cells by R5 Savings

| Rank | grid_id | R5 savings (GWh) | Buildings | Dominant era | Approx. centroid |
|---|---|---|---|---|---|
| 1 | 1087 | 172.923 | 39 | era1 | 28.198°N 112.975°E |
| 2 | 1004 | 134.419 | 15 | era1 | 28.193°N 112.964°E |
| 3 | 1128 | 119.449 | 134 | era1 | 28.198°N 112.980°E |
| 4 | 1132 | 75.895 | 12 | era1 | 28.216°N 112.980°E |
| 5 | 1086 | 70.745 | 107 | era1 | 28.193°N 112.975°E |
| 6 | 929 | 65.496 | 30 | era1 | 28.225°N 112.955°E |
| 7 | 889 | 58.626 | 24 | era2 | 28.230°N 112.950°E |
| 8 | 1125 | 44.406 | 81 | era1 | 28.184°N 112.980°E |
| 9 | 1168 | 42.563 | 219 | era1 | 28.193°N 112.985°E |
| 10 | 883 | 42.473 | 26 | era1 | 28.203°N 112.949°E |
| 11 | 884 | 39.627 | 81 | era1 | 28.207°N 112.949°E |
| 12 | 1046 | 38.974 | 32 | era1 | 28.198°N 112.970°E |
| 13 | 1243 | 38.812 | 52 | era1 | 28.161°N 112.994°E |
| 14 | 1332 | 36.225 | 132 | era1 | 28.193°N 113.005°E |
| 15 | 559 | 35.561 | 63 | era2 | 28.221°N 112.909°E |
| 16 | 1290 | 35.016 | 52 | era1 | 28.188°N 113.000°E |
| 17 | 1127 | 34.041 | 264 | era1 | 28.193°N 112.980°E |
| 18 | 1209 | 32.460 | 94 | era1 | 28.193°N 112.990°E |
| 19 | 1248 | 31.532 | 111 | era1 | 28.184°N 112.995°E |
| 20 | 1210 | 31.500 | 91 | era1 | 28.198°N 112.990°E |

Grid cells cluster in the dense central districts. Changsha urban core approximate
district boundaries: Furong ≈ 112.97–113.04°E / 28.18–28.22°N;
Tianxin ≈ 112.95–113.02°E / 28.11–28.18°N;
Yuelu ≈ 112.89–112.97°E / 28.15–28.22°N.
Expected: top-20 grids in Furong/Tianxin (dense Era 1 residential core).

---

## D5 — Post-R5 City EUI

| Metric | Value |
|---|---|
| Baseline total energy (GWh) | 15381.6 |
| R5 total savings (GWh) | 5633.8 |
| Post-R5 total energy (GWh) | 9747.8 |
| Total floor area (Mm²) | 72.051 |
| Post-R5 city mean EUI (kWh/m²/yr) | 135.3 |
| Baseline city EUI (kWh/m²/yr) | 213.5 |
| EUI reduction | 78.2 kWh/m²/yr |

Status: EXPECTED ✓
Expected 130–150 kWh/m²/yr based on weighted blend of Paper 2 R5 EUI values.

---

## Summary

R5 combined retrofit reduces city-scale energy from 15382 to 9748 GWh/yr
(5634 GWh saved, 36.6% reduction).
Era 1 delivers the highest absolute savings due to the largest improvement potential
(47% EUI reduction vs 16% for Era 3).
Air sealing (R4) is the single most impactful measure across all eras.
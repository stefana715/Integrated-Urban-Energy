# Validation Report — Task 6: Climate Change Scenario Analysis

**Date:** 2026-04-19

---

## Overview

30 EnergyPlus simulations (3 eras × 2 retrofit_status × 5 climate scenarios) from Paper 2
scaled to 18,826 buildings via per-era heating/cooling factors.
Constant PV = 1603 GWh/yr assumed across all scenarios (temperature penalty
−0.4%/K is negligible at city scale; see DEC-021).

**Notable data observation:** Era 1 R5 and Era 2 R5 share identical EUI values in
climate_results.csv across all 5 scenarios. This is expected: Paper 2 used the same
MidRise R5 archetype for both eras (retrofit flattens era-specific differences).
  Identical factors confirmed: True

---

## Stage A — Climate Factors

| Era | Retrofit | Scenario | Heat EUI cur | Heat EUI scn | h_factor | Cool EUI cur | Cool EUI scn | c_factor |
|---|---|---|---|---|---|---|---|---|
| 1 | baseline | Current | 99.61 | 99.61 | 1.0000 | 44.46 | 44.46 | 1.0000 |
| 1 | baseline | 2050_SSP245 | 99.61 | 77.34 | 0.7764 | 44.46 | 56.22 | 1.2645 |
| 1 | baseline | 2050_SSP585 | 99.61 | 72.18 | 0.7246 | 44.46 | 59.34 | 1.3347 |
| 1 | baseline | 2080_SSP245 | 99.61 | 70.06 | 0.7033 | 44.46 | 60.52 | 1.3612 |
| 1 | baseline | 2080_SSP585 | 99.61 | 51.61 | 0.5181 | 44.46 | 74.29 | 1.6709 |
| 1 | R5 | Current | 2.97 | 2.97 | 1.0000 | 25.17 | 25.17 | 1.0000 |
| 1 | R5 | 2050_SSP245 | 2.97 | 1.62 | 0.5455 | 25.17 | 29.26 | 1.1625 |
| 1 | R5 | 2050_SSP585 | 2.97 | 1.34 | 0.4512 | 25.17 | 30.34 | 1.2054 |
| 1 | R5 | 2080_SSP245 | 2.97 | 1.24 | 0.4175 | 25.17 | 30.75 | 1.2217 |
| 1 | R5 | 2080_SSP585 | 2.97 | 0.52 | 0.1751 | 25.17 | 35.39 | 1.4060 |
| 2 | baseline | Current | 60.96 | 60.96 | 1.0000 | 36.16 | 36.16 | 1.0000 |
| 2 | baseline | 2050_SSP245 | 60.96 | 46.13 | 0.7567 | 36.16 | 45.16 | 1.2489 |
| 2 | baseline | 2050_SSP585 | 60.96 | 42.71 | 0.7006 | 36.16 | 47.55 | 1.3150 |
| 2 | baseline | 2080_SSP245 | 60.96 | 41.33 | 0.6780 | 36.16 | 48.47 | 1.3404 |
| 2 | baseline | 2080_SSP585 | 60.96 | 29.35 | 0.4815 | 36.16 | 59.05 | 1.6330 |
| 2 | R5 | Current | 2.97 | 2.97 | 1.0000 | 25.17 | 25.17 | 1.0000 |
| 2 | R5 | 2050_SSP245 | 2.97 | 1.62 | 0.5455 | 25.17 | 29.26 | 1.1625 |
| 2 | R5 | 2050_SSP585 | 2.97 | 1.34 | 0.4512 | 25.17 | 30.34 | 1.2054 |
| 2 | R5 | 2080_SSP245 | 2.97 | 1.24 | 0.4175 | 25.17 | 30.75 | 1.2217 |
| 2 | R5 | 2080_SSP585 | 2.97 | 0.52 | 0.1751 | 25.17 | 35.39 | 1.4060 |
| 3 | baseline | Current | 15.06 | 15.06 | 1.0000 | 20.90 | 20.90 | 1.0000 |
| 3 | baseline | 2050_SSP245 | 15.06 | 10.61 | 0.7045 | 20.90 | 25.20 | 1.2057 |
| 3 | baseline | 2050_SSP585 | 15.06 | 9.57 | 0.6355 | 20.90 | 26.35 | 1.2608 |
| 3 | baseline | 2080_SSP245 | 15.06 | 9.16 | 0.6082 | 20.90 | 26.82 | 1.2833 |
| 3 | baseline | 2080_SSP585 | 15.06 | 5.77 | 0.3831 | 20.90 | 31.79 | 1.5211 |
| 3 | R5 | Current | 0.19 | 0.19 | 1.0000 | 18.96 | 18.96 | 1.0000 |
| 3 | R5 | 2050_SSP245 | 0.19 | 0.06 | 0.3158 | 18.96 | 21.43 | 1.1303 |
| 3 | R5 | 2050_SSP585 | 0.19 | 0.04 | 0.2105 | 18.96 | 22.07 | 1.1640 |
| 3 | R5 | 2080_SSP245 | 0.19 | 0.03 | 0.1579 | 18.96 | 22.35 | 1.1788 |
| 3 | R5 | 2080_SSP585 | 0.19 | 0.00 | 0.0000 | 18.96 | 25.01 | 1.3191 |

**Sanity checks passed:**
- All h_factors < 1.0 (warming reduces heating) ✓
- All c_factors > 1.0 (warming increases cooling) ✓
- 2080 SSP585 shows largest magnitude changes ✓
- R5 factors (relative) show smaller absolute change than baseline → climate resilience ✓

---

## D1 — Climate Resilience of R5 Combined Strategy (2080 SSP5-8.5)

| Scenario | Gross demand (GWh) | vs current (%) | Net demand (GWh) |
|---|---|---|---|
| Baseline — Current | 15,381.6 | +0.00% | 13,778.6 |
| Baseline — 2050_SSP245 | 14,946.5 | -2.83% | 13,343.5 |
| Baseline — 2050_SSP585 | 14,867.4 | -3.34% | 13,264.4 |
| Baseline — 2080_SSP245 | 14,831.5 | -3.58% | 13,228.5 |
| Baseline — 2080_SSP585 | 14,700.9 | -4.43% | 13,097.9 |
|  |  |  |  |
| R5 — Current | 9,747.8 | +0.00% | 8,144.8 |
| R5 — 2050_SSP245 | 9,937.5 | +1.95% | 8,334.5 |
| R5 — 2050_SSP585 | 9,991.7 | +2.50% | 8,388.7 |
| R5 — 2080_SSP245 | 10,013.3 | +2.72% | 8,410.3 |
| R5 — 2080_SSP585 | 10,270.9 | +5.37% | 8,667.9 |

**Baseline current → 2080 SSP585:** 15,381.6 → 14,700.9 GWh (-4.4%)
**R5 current → 2080 SSP585:** 9,747.8 → 10,270.9 GWh (+5.4%)

**Interpretation:** Under 2080 SSP5-8.5, the unretrofitted city demand actually
decreases slightly in total because the massive heating reduction (Era 1: −48.2%,
Era 2: −51.8%) exceeds the cooling increase (Era 1: +67.1%, Era 2: +63.3%) in
absolute kWh/m² terms — Changsha's current stock is so heating-heavy that warming
delivers a perverse net energy benefit. This changes post-retrofit: under R5 the
heating demand is already near-zero, so the remaining cooling increase dominates,
and total demand rises by +5.4% under 2080 SSP585.

---

## D2 — Heating-to-Cooling Tipping Point

Heating-to-cooling energy ratio at city scale (baseline, unretrofitted):

| Scenario | City heating (GWh) | City cooling (GWh) | H/C ratio |
|---|---|---|---|
| Current | 4,535.4 | 2,532.2 | 1.791 |
| 2050_SSP245 | 3,469.0 | 3,163.6 | 1.097 |
| 2050_SSP585 | 3,222.2 | 3,331.3 | 0.967 ← TIPPING |
| 2080_SSP245 | 3,121.8 | 3,395.9 | 0.919 |
| 2080_SSP585 | 2,252.0 | 4,135.0 | 0.545 |

**Tipping point:** 2050_SSP585 — first scenario where cooling demand exceeds heating.
Physical explanation: Changsha's HSCW climate has ~2.5× more heating than cooling
in current conditions (H/C = 1.79). Moderate SSP2-4.5 warming is sufficient to
erode most of the heating surplus, but the tipping point requires SSP5-8.5 forcing.

---

## D3 — R5 Climate Resilience

Under R5, heating is already near-zero at current climate:

| Component | R5 current (GWh) | R5 2080 SSP585 (GWh) | Change (GWh) |
|---|---|---|---|
| Heating | 160.6 | 27.5 | -133.1 |
| Cooling | 1,694.1 | 2,350.3 | +656.2 |
| Other   | 7,893.1 | 7,893.1 | 0.0 (assumed) |
| **Total** | **9,747.8** | **10,270.9** | **+523.1** |

**Key insight:** R5 retrofit effectively decouples the city from heating-climate
sensitivity (heating near-zero in all scenarios). The only remaining climate exposure
is cooling. PV peak coincidence (Jun–Sep) naturally hedges this cooling growth:
PV Jun–Sep share is 38.3%, while cooling concentrates 90% in Jun–Sep.

Net R5+PV demand under 2080 SSP585: 8,667.9 GWh
(vs current R5+PV net: 8,144.8 GWh; change: +523.1 GWh / +6.4%)

---

## D4 — Carbon Implications Preview

Grid emission factor: 0.5703 tCO₂/MWh (Hunan 2022).
Combined R5+PV savings = (baseline gross) − (R5 gross − PV offset).
= R5 retrofit avoided + PV self-consumed

| Scenario | Baseline gross (GWh) | R5+PV net (GWh) | Combined savings (GWh) | CO₂ avoided (kt/yr) |
|---|---|---|---|---|
| Current | 15,381.6 | 8,144.8 | 7,236.8 | 4,127 |
| 2050_SSP245 | 14,946.5 | 8,334.5 | 6,612.0 | 3,771 |
| 2050_SSP585 | 14,867.4 | 8,388.7 | 6,478.7 | 3,695 |
| 2080_SSP245 | 14,831.5 | 8,410.3 | 6,421.2 | 3,662 |
| 2080_SSP585 | 14,700.9 | 8,667.9 | 6,033.0 | 3,441 |

**Current R5+PV CO₂ avoided:** 4,127 kt/yr
**2080 SSP585 R5+PV CO₂ avoided:** 3,441 kt/yr

Note: Under 2080 SSP585, baseline demand falls while R5+PV net rises slightly,
so the combined savings shrink modestly. However, R5+PV remains the dominant
decarbonisation strategy across all scenarios.

---

## D5 — 2050 Policy-Relevant Sensitivity

| Metric | 2050 SSP2-4.5 | 2050 SSP5-8.5 | 2080 SSP5-8.5 |
|---|---|---|---|
| Baseline gross (GWh) | 14,946.5 | 14,867.4 | 14,700.9 |
| R5 gross (GWh) | 9,937.5 | 9,991.7 | 10,270.9 |
| Combined savings (GWh) | 6,612 | 6,479 | 6,033 |

R5+PV delivers strong savings across all scenarios. The spread between moderate
(2050 SSP245) and extreme (2080 SSP585) scenarios in combined savings is small
(579 GWh, 8.8%),
showing the strategy is robust to emissions pathway uncertainty.

---

## Summary

- Baseline 2080 SSP585 total demand: 14,700.9 GWh (-4.4% vs current — slight decrease due to heating dominance)
- R5+PV 2080 SSP585 net demand: 8,667.9 GWh (+6.4% vs current R5+PV)
- H/C tipping point: 2050_SSP585 (first scenario cooling > heating at city scale)
- R5 heating under 2080 SSP585: 27.5 GWh (≈0% of demand — retrofit eliminates heating climate sensitivity)
- CO₂ avoided (current R5+PV): 4,127 kt/yr
- CO₂ avoided (2080 SSP585 R5+PV vs same-period baseline): 3,441 kt/yr
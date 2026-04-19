# Validation Report — Task 8: Consolidated Carbon Emission Accounting

**Date:** 2026-04-19

---

## Stage A — Grid Decarbonisation Trajectory

| Year | Grid EF (tCO₂/MWh) | Source |
|---|---|---|
| 2025 (current) | 0.5703 | MEE/NBS 2022 (Hunan) — Paper 1 ref [25] |
| 2050 | 0.30 | China dual-carbon goal trajectory (~50% decrease) |
| 2080 | 0.10 | Near-zero grid under Net Zero scenario |

Linear interpolation between waypoints. See DEC-023 for rationale and sensitivity.

---

## Stage B — Annual Carbon per Scenario

| Scenario | RS | PV | Net demand (GWh) | GEF (yr) | Carbon_yr (kt) | Carbon_fixed (kt) | Savings_fixed (kt) |
|---|---|---|---|---|---|---|---|
| Current | baseline | False | 15,381.6 | 0.5703 | 8,772.1 | 8,772.1 | 0.0 |
| Current | baseline | True | 13,778.6 | 0.5703 | 7,857.9 | 7,857.9 | 914.2 |
| 2050_SSP245 | baseline | False | 14,946.5 | 0.3000 | 4,483.9 | 8,524.0 | 248.1 |
| 2050_SSP245 | baseline | True | 13,343.5 | 0.3000 | 4,003.0 | 7,609.8 | 1,162.3 |
| 2050_SSP585 | baseline | False | 14,867.4 | 0.3000 | 4,460.2 | 8,478.9 | 293.2 |
| 2050_SSP585 | baseline | True | 13,264.4 | 0.3000 | 3,979.3 | 7,564.7 | 1,207.4 |
| 2080_SSP245 | baseline | False | 14,831.5 | 0.1000 | 1,483.2 | 8,458.4 | 313.7 |
| 2080_SSP245 | baseline | True | 13,228.5 | 0.1000 | 1,322.9 | 7,544.2 | 1,227.9 |
| 2080_SSP585 | baseline | False | 14,700.9 | 0.1000 | 1,470.1 | 8,383.9 | 388.2 |
| 2080_SSP585 | baseline | True | 13,097.9 | 0.1000 | 1,309.8 | 7,469.7 | 1,302.4 |
| Current | R5 | False | 9,747.8 | 0.5703 | 5,559.2 | 5,559.2 | 3,213.0 |
| Current | R5 | True | 8,144.8 | 0.5703 | 4,645.0 | 4,645.0 | 4,127.1 |
| 2050_SSP245 | R5 | False | 9,937.5 | 0.3000 | 2,981.2 | 5,667.4 | 3,104.8 |
| 2050_SSP245 | R5 | True | 8,334.5 | 0.3000 | 2,500.3 | 4,753.2 | 4,019.0 |
| 2050_SSP585 | R5 | False | 9,991.7 | 0.3000 | 2,997.5 | 5,698.3 | 3,073.9 |
| 2050_SSP585 | R5 | True | 8,388.7 | 0.3000 | 2,516.6 | 4,784.1 | 3,988.1 |
| 2080_SSP245 | R5 | False | 10,013.3 | 0.1000 | 1,001.3 | 5,710.6 | 3,061.5 |
| 2080_SSP245 | R5 | True | 8,410.3 | 0.1000 | 841.0 | 4,796.4 | 3,975.7 |
| 2080_SSP585 | R5 | False | 10,270.9 | 0.1000 | 1,027.1 | 5,857.5 | 2,914.6 |
| 2080_SSP585 | R5 | True | 8,667.9 | 0.1000 | 866.8 | 4,943.3 | 3,828.8 |

**Notes:**
- Carbon_yr uses the year-appropriate grid factor (declining over time)
- Carbon_fixed uses the constant 2025 factor (0.5703) for sensitivity comparison
- Savings_fixed = how much carbon is avoided vs 2025 baseline at constant grid factor

---

## Stage C — Per-Era Carbon (Current Climate, Fixed Grid Factor)

| Era | Baseline (kt/yr) | R5 only (kt/yr) | PV (GWh) | R5+PV (kt/yr) | Combined savings (kt/yr) |
|---|---|---|---|---|---|
| era1 | 3,952.7 | 2,093.4 | 505.8 | 1,804.9 | 2,147.8 |
| era2 | 3,170.5 | 2,074.5 | 634.1 | 1,712.8 | 1,457.6 |
| era3 | 1,649.0 | 1,391.3 | 462.8 | 1,127.4 | 521.6 |

---

## D1 — Annual Carbon Summary (Current Climate)

| Metric | Value |
|---|---|
| Current baseline annual carbon | 8,772 kt CO₂/yr |
| R5-only annual carbon | 5,559 kt CO₂/yr |
| R5+PV annual carbon | 4,645 kt CO₂/yr |
| Annual savings (R5+PV vs baseline) | 4,127 kt CO₂/yr |

---

## D2 — Cumulative Pathways 2025–2080

| Year | BAU cumul (kt) | R5+PV immed (kt) | Stepwise (kt) | R5+PV SSP585 (kt) |
|---|---|---|---|---|
| 2025.0 | 0 | 0 | 0 | 0 |
| 2030.0 | 41,670 | 22,173 | 40,140 | 22,187 |
| 2035.0 | 78,980 | 42,232 | 73,230 | 42,286 |
| 2040.0 | 111,979 | 60,157 | 100,037 | 60,269 |
| 2045.0 | 140,714 | 75,927 | 121,544 | 76,110 |
| 2050.0 | 165,230 | 89,522 | 138,615 | 89,784 |
| 2055.0 | 186,392 | 101,337 | 152,218 | 101,699 |
| 2060.0 | 205,040 | 111,778 | 163,208 | 112,270 |
| 2065.0 | 221,181 | 120,841 | 172,270 | 121,482 |
| 2070.0 | 234,821 | 128,521 | 179,950 | 129,319 |
| 2075.0 | 245,967 | 134,814 | 186,244 | 135,766 |
| 2080.0 | 254,625 | 139,716 | 191,145 | 140,806 |

| Cumulative savings | 2025–2050 | 2025–2080 |
|---|---|---|
| Scenario B (R5+PV immed) vs BAU | 75,709 kt | 114,909 kt |
| Scenario C (stepwise) vs BAU | 26,616 kt | 63,480 kt |

---

## Stage E — Paper 1 vs Paper 3 Comparison

| Strategy | Annual energy avoided (GWh/yr) | Annual CO₂ avoided (kt/yr) | Multiplier vs P1 |
|---|---|---|---|
| Paper 1: PV-only (6,411 HP buildings) | 1764.4 | 1006 | 1.00× |
| Paper 3: PV-only (v5, 6,401 buildings) | 1603 | 914 | 0.91× |
| Paper 3: R5 retrofit only | 5,633.8 | 3213 | 3.19× |
| Paper 3: R5 + PV combined | 7236.8 | 4127 | **4.10×** |

**Key finding:** Integrating building-envelope retrofit with rooftop PV increases
annual CO₂ mitigation by 4.1× compared with PV deployment alone.
The retrofit component accounts for 78% of the combined impact.

---

## Summary

- Current annual carbon baseline: 8,772 kt CO₂/yr
- R5+PV annual carbon savings: 4,127 kt CO₂/yr (47% of baseline)
- Cumulative 2025–2050 savings (immediate rollout): 75,709 kt CO₂
- Cumulative 2025–2080 savings (immediate rollout): 114,909 kt CO₂
- Stepwise rollout 2025–2080: 63,480 kt CO₂ (55% of immediate)
- Paper 3 combined R5+PV is 4.1× more impactful than P1 PV-only
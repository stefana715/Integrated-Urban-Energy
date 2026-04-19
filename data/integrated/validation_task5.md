# Validation Report — Task 5: PV Generation + Monthly Supply-Demand

**Date:** 2026-04-19

---

## Stage A — HP Building PV

| Metric | Value |
|---|---|
| HP buildings | 6,401 |
| City annual HP PV (GWh/yr) | 1603.0 |
| Target (Task 2 v5) | 1,603 GWh/yr |
| Match | ✓ |

---

## Stage B — Monthly Profiles (source: Paper 2 solar_monthly.csv)

PV monthly shares derived from Paper 2 pvlib output (Era1 MidRise, Changsha 28°N).
Heating/cooling/other from HSCW typical seasonal patterns (task specification).

| Month | PV share | Heat share | Cool share | Other share |
|---|---|---|---|---|
| Jan | 7.1% | 30% | 0% | 9.0% |
| Feb | 6.3% | 20% | 0% | 8.0% |
| Mar | 7.5% | 10% | 0% | 8.0% |
| Apr | 8.0% | 2% | 2% | 8.0% |
| May | 9.2% | 0% | 5% | 8.0% |
| Jun | 8.2% | 0% | 15% | 8.0% |
| Jul | 11.1% | 0% | 30% | 8.5% |
| Aug | 9.7% | 0% | 30% | 8.5% |
| Sep | 9.3% | 0% | 15% | 8.0% |
| Oct | 9.0% | 3% | 3% | 8.0% |
| Nov | 7.6% | 10% | 0% | 9.0% |
| Dec | 7.1% | 25% | 0% | 9.0% |

**Note on PV profile:** Paper 2 solar data shows July as peak (11.1% of annual),
consistent with Changsha's radiation climatology. Winter months (Dec–Feb) = 20.5%.

---

## D1 — Annual Self-Consumption

| Metric | Baseline | R5 retrofit |
|---|---|---|
| Annual PV generation (GWh) | 1603.0 | 1603.0 |
| Annual demand (GWh) | 15381.0 | 10168.0 |
| Annual PV self-consumed (GWh) | 1603.0 | 1603.0 |
| Self-consumption ratio | 100.0% | 100.0% |
| Annual demand coverage by PV | 10.42% | 15.77% |

PV = 1603 GWh vs baseline demand = 15381 GWh; ratio = 0.104.
PV << demand in every month → self-consumption is always 100% (all PV absorbed).

---

## D2 — Seasonal Patterns

| Metric | Value |
|---|---|
| Months where PV > baseline demand | None ✓ |
| Months where PV > R5 demand | None ✓ |
| Baseline cooling covered by PV — July | 23.4% |
| Baseline cooling covered by PV — August | 20.5% |
| R5 cooling covered by PV — July | 34.9% |
| R5 cooling covered by PV — August | 30.6% |

Even under R5 (greatly reduced cooling = 1694 GWh vs baseline 2532 GWh),
PV still provides < 100% of summer cooling because PV monthly peak
(178 GWh in Jul) << R5 cooling peak
(508 GWh in Jul).

---

## D3 — Cooling-PV Coincidence Factor

| Metric | Value |
|---|---|
| PV share Jun–Sep | 38.2% |
| Cooling share Jun–Sep | 90% |
| Coincidence factor (PV share / cooling share) | 0.425 |
| PV share Dec–Feb | 20.5% |
| Heating share Dec–Feb | 75% |

**Interpretation:**
- PV-cooling coincidence factor = 0.42. Cooling peaks in Jun–Sep when PV is
  also strong — good natural alignment. Summer PV can directly offset cooling demand.
- Heating concentrates Dec–Feb (75% of heating) but PV is only 20.5%
  of annual in those months — poor alignment. Retrofit (not PV) is the right tool
  for heating reduction in Changsha's HSCW climate.

---

## D4 — Net Demand After PV

| Metric | Baseline | R5 |
|---|---|---|
| Annual total demand (GWh) | 15381 | 10168 |
| Annual PV self-consumed (GWh) | 1603 | 1603 |
| Residual net demand (GWh) | 13778 | 8565 |
| Grid demand reduction vs baseline | — | 5213 GWh (37.8%) |

---

## D5 — Combined Retrofit + PV Savings

| Intervention | Annual avoided/displaced (GWh) | % of baseline |
|---|---|---|
| PV alone (all self-consumed) | 1603 | 10.4% |
| R5 retrofit alone | 5214 | 33.9% |
| Combined (R5 + PV, conservative) | 6817 | 44.3% |

**Note:** Combined = R5 retrofit savings + PV self-consumption (= 100% of PV since
demand always > PV). No double-counting because PV is applied to post-R5 demand.

The combined intervention would reduce the grid-supplied energy from
15382 GWh to 8565 GWh
(44.3% reduction).

---

## Summary

- Self-consumption: 100% baseline / 100% R5 — all PV absorbed in both cases
- PV-cooling coincidence: 0.42 — PV naturally hedges cooling growth
- No month has PV surplus at city scale (PV/1603 GWh vs demand >10168 GWh)
- Combined retrofit+PV: 44.3% of baseline demand avoided
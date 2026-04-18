# Decision Log — Paper 3

Tracks key methodological decisions, their rationale, and any alternatives considered.

---

## DEC-001 — Building Era Classification Method

**Date:** 2026-04-19
**Decision:** Use OSM `start_date` tag as primary source for building era assignment. Where the tag is absent, infer era from a combination of: building type (`building=apartments` vs `building=residential`), height/floor-count proxy (from Paper 1), and location within known urban development zones (Changsha's phased spatial expansion).

**Rationale:** OSM age coverage in Chinese cities is incomplete; a fallback rule is required for a majority of buildings. Height and spatial zone are the two strongest proxies available without additional field surveys.

**Alternatives considered:**
- Assign all untagged buildings to a default era (rejected — introduces systematic bias toward the most common era)
- Use satellite imagery or NDVI change-detection to date construction (requires additional remote sensing pipeline, out of scope)

**Impact:** Affects Task 2 and propagates into all downstream energy/PV estimates.

---

## DEC-002 — MidRise vs HighRise Classification

**Date:** 2026-04-19
**Decision:** Use 6-floor threshold: ≤6 floors = MidRise (Era 1 & 2 archetype), >6 floors = HighRise (Era 3 archetype). Floor count is derived from the height proxy computed in Paper 1 (building height / assumed floor-to-floor height of 3.0 m).

**Rationale:** Chinese residential building codes and urban form in Changsha align with this boundary. Era 3 stock is predominantly high-rise towers post-2005; Era 1/2 stock is predominantly walk-up and low-rise apartment blocks.

**Alternatives considered:**
- Use absolute height thresholds directly (e.g., >18 m = high-rise): equivalent but less interpretable; floor count preferred for reporting.

---

## DEC-003 — Archetype-to-Stock Transferability

**Date:** 2026-04-19
**Decision:** Paper 2 per-m² EUI values (baseline and retrofit) are applied uniformly to all buildings classified into the same era × typology cell. PV generation values (kWh/m²_floor) are likewise applied uniformly by MidRise/HighRise.

**Rationale:** No building-specific measured data are available for the 18,855-building stock. Archetype-based scale-up is standard practice in urban building energy modelling (UBEM). Uncertainty is acknowledged and addressed via sensitivity analysis on era classification proportions.

**Limitations:** Ignores within-class variation in envelope condition, occupancy, and orientation. Addressed partially by era stratification.

---

## DEC-004 — Data Status at Initialisation

**Date:** 2026-04-19

### Paper 1 — PRESENT
- `planning_metrics_summary.csv` — per-building metrics (primary database)
- `planning_metrics_aggregate.csv` — grid-level aggregates
- `priority_grids.csv` — 146 priority grids
- `sensitivity/` — 6 sensitivity analysis CSVs
- `validation/` — 9 validation files including `buildings_pvlib_benchmark_zones.geojson`

### Paper 1 — NOTE
- `figures/` and `tables/` directories are empty (contain only `.gitkeep`)
- No standalone full-coverage building GeoJSON at top level; geometry available in `validation/buildings_pvlib_benchmark_zones.geojson` (benchmark subset only). Confirm whether `planning_metrics_summary.csv` contains all geometry columns needed for Task 1.

### Paper 2 — PRESENT
- `climate/` — baseline TMYx EPW + 4 future EPW files (2050/2080 × SSP245/SSP585)
- `models/` — 26 IDF files (3 era baselines + 15 retrofit variants + ASHRAE references)
- `processed/` — 9 processed CSVs (baseline, retrofit, solar, climate, Morris SA)
- `results/all_results_tables.md`
- `figure/` — 8 publication figures
- `simulation/` — 50 EnergyPlus output directories

### Paper 2 — NOTE
- All expected simulation outputs are present. Key files for Paper 3 are `processed/baseline_results.csv`, `processed/retrofit_results.csv`, `processed/solar_results.csv`, `processed/solar_monthly.csv`, and `processed/climate_results.csv`.

---

## DEC-005 — Climate Scenario Scope

**Date:** 2026-04-19
**Decision:** Report results for all four future scenarios (2050 SSP245, 2050 SSP585, 2080 SSP245, 2080 SSP585) plus current baseline. Headline comparison uses 2080 SSP5-8.5 (+4.04°C) as the high-end stress test.

**Rationale:** All four EPW files are available from Paper 2. Reporting all scenarios supports journal requirements for climate resilience framing and provides policy-relevant differentiation between mitigation pathways.

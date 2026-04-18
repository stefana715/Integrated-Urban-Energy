# Decision Log — Paper 3

Tracks key methodological decisions, their rationale, and any alternatives considered.

---

## DEC-001 — Building Era Classification Method (SUPERSEDED by DEC-006)

**Date:** 2026-04-19 (initial) / Updated 2026-04-19 (Task 2 implementation)
**Original decision:** Use OSM `start_date` tag as primary. Superseded because `start_date` = 0% coverage in Changsha OSM data — not a single building tagged.
**See DEC-006 for the implemented approach (GHS-AGE).**

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

---

## DEC-006 — Era Classification Primary Source: GHS-AGE R2025A

**Date:** 2026-04-19
**Decision:** Use JRC GHS-AGE R2025A (100m, 10-year epochs 1980–2020) as the primary era classification source. Each building's centroid is reprojected to Mollweide (ESRI:54009) and the raster value at that point gives the dominant construction epoch of the 100m cell.

**Dataset:**
- Source: Uhl, Politis, Pesaresi (2025). GHS-AGE R2025A. European Commission, JRC. doi:10.2905/d503bb56-9884-4e4d-bb8f-d86711d9f749
- URL: `https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_AGE_GLOBE_R2025A/V1-0/GHS_AGE_1980102020_GLOBE_R2025A_54009_100_V1_0.zip`
- Downloaded: global 100m ZIP (608 MB) → cropped to Changsha bbox + 2 km buffer → `data/integrated/ghs_age_changsha.tif` (24 KB, 344×254 px) → global deleted

**GHS-BUILT-H cross-validation:**
- Tile R6_C29 covers x=[9,959,000–10,959,000], y=[3,020,000–4,020,000] in Mollweide (20–30°N, ~110–120°E); confirmed to cover Changsha.
- URL: `.../GHS_BUILT_H_ANBH_E2018_GLOBE_R2023A_54009_100/V1-0/tiles/...R6_C29.zip` (41 MB tile)
- Citation: Pesaresi, Politis (2023). GHS-BUILT-H R2023A. JRC. doi:10.2905/85005901-3A49-48DD-9D19-6261354F56FE

**Why NOT GHS-OBAT / Overture Buildings:** Overture coverage known to be incomplete in China per Florio et al. (2025); OSM building age tags are 0% in Changsha.

**Era epoch mapping:**
| GHS-AGE epoch | Meaning | → Paper 2 era |
|---|---|---|
| 1 | built pre-1980 | Era 1 |
| 2 | built 1980–1989 | Era 1 |
| 3 | built 1990–1999 | Era 1 |
| 4 | built 2000–2009 | Era 2 |
| 5 | built 2010–2020 | Era 3 |
| 0 / nodata | no built-up detected | height fallback |

**Rationale:** Era 1 in Paper 2 represents pre-2000 low-standard residential construction (GBSC <1986 + GB50176-93 period). Era 2 represents 2000–2010 transitional standard. Era 3 represents post-2010 modern standard (GB50176-2016 regime). The GHS-AGE 10-year epochs map cleanly to this three-era scheme.

**Fallback rule (32 buildings, 0.2%):** where epoch = nodata → `height_proxy_m > 30 m` → era3; `> 15 m` → era2; else → era1. Source flagged as `era_source = "height_fallback"`.

**Folder naming:** `data/auxiliary_rasters/` used instead of `data/climate_auxiliary/` for clarity. `data/climate/` is reserved for EPW weather files.

---

## DEC-007 — Typology Threshold (confirmed from DEC-002)

**Date:** 2026-04-19
**Decision confirmed:** 18 m (≈ 6 floors × 3 m/floor) as MidRise/HighRise boundary, applied to `height_proxy_m` from Paper 1.

**Caveat identified in Task 2:** Height cross-validation showed Pearson r = 0.002 (p = 0.76) between `height_proxy_m` (Paper 1) and GHSL ANBH (satellite-derived 2018 heights). Mean height_proxy_m = 10.6 m vs mean GHSL ANBH = 17.9 m. The near-zero correlation confirms that `height_proxy_m` is largely derived from building-type default rules (not measured heights), as OSM `building:levels` coverage was only 5.2%. The 18 m threshold is retained because it correctly separates the dominant walk-up residential type (assigned default ~10.5 m) from known high-rise stock (assigned higher defaults), but the typology split should be interpreted as an approximation: **96.6% MidRise, 3.4% HighRise**. This may undercount actual HighRise stock and should be discussed as a limitation.

---

## DEC-008 — Pre-1980 Dominance in GHS-AGE (Flagged for User Review)

**Date:** 2026-04-19
**Finding:** GHS-AGE classifies 54.3% of Changsha's 18,855 buildings as built pre-1980 (epoch 1). Total Era 1 = 79.4%, Era 2 = 16.0%, Era 3 = 4.6%.

**Possible explanations:**
1. GHS-AGE 100m cells capture dominant epoch of the entire 1 ha cell; in Changsha's dense urban core, pre-existing urban fabric anchors many cells to epoch 1 even where individual buildings are newer.
2. Changsha's historic urban core (Furong, Tianxin districts) genuinely has extensive pre-reform-era built stock from the socialist period (danwei compounds, work-unit housing).
3. GHS-BUILT-S (built surface) in these areas may reflect the period when the cell first became built-up, not when individual structures were last replaced.

**Impact:** High Era 1 proportion increases the city-scale energy estimate (Era 1 EUI = 261.2 kWh/m²). The era distribution should be validated against Changsha housing census data or remote sensing change detection before finalising Task 3. **Flagged for user review before proceeding to Task 3.**

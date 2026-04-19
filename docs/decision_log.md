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

---

## DEC-009 — Era Calibration to Target 40/28/32 Proportions (v2)

**Date:** 2026-04-19
**Decision:** Override the raw GHS-AGE-derived era proportions (79.4/16.0/4.6) with calibrated proportions of 40% Era 1 / 28% Era 2 / 32% Era 3 using a recency-score quantile assignment.

**Calibration method:**
- Rank all 18,826 buildings by `recency_score` (ascending = older).
- Assign: lowest 40% → Era 1, next 28% → Era 2, top 32% → Era 3.
- Ties broken by building ID for reproducibility.

**Target proportions rationale:**
- Zhang et al. (2025) document that Changsha's construction land more than tripled between 2000 and 2020, implying that ≥60% of the current built floor stock was constructed post-2000.
- Expert adjustment for urban core bias: the Paper 1 dataset is the Changsha urban core (not peri-urban), where historic stock is higher; Era 1 adjusted to 40% (not the citywide 36% from Census).
- Proportions used by Paper 2 archetype simulation framework: Era 1 = pre-2000, Era 2 = 2000–2009, Era 3 = 2010–present.

**recency_score definition:** `(v2020 − v2000) / max(v2020, 1) + 0.3 × (v2020 − v1990) / max(v2020, 1)`, clipped to [−2, 2]. Higher score = more volume built recently relative to total 2020 volume.

**Concordance with v1 (GHS-AGE):** 44.6% of buildings received the same era label. The 55.4% change is expected given the large shift in target proportions.

**Alternative proportions tested (sensitivity):** 50/25/25 and 30/30/40 — see `classification_validation_v2.md`.

---

## DEC-010 — GHSL ANBH as Canonical Building Height (v2)

**Date:** 2026-04-19
**Decision:** In v2, replace `height_proxy_m` (Paper 1, OSM-derived) with `ghsl_height_m` (GHSL ANBH 2018) as the canonical `building_height_m` for typology assignment and floor area calculation. Fall back to `height_proxy_m` only where GHSL ANBH is null or zero (31 buildings, 0.2%).

**Rationale:** GHS-BUILT-H R2023A ANBH is derived from global building height estimates (Pesaresi & Politis 2023) and provides continuous values for 99.8% of buildings (18,795 of 18,826). The DEC-007 cross-validation showed height_proxy_m has near-zero correlation (r = 0.002) with GHSL; GHSL ANBH is more plausible as an independent satellite-derived estimate. Mean GHSL ANBH = 17.9 m vs mean height_proxy_m = 10.6 m; the GHSL value produces a more credible high-rise share.

**Typology threshold:** 18 m (≈6 floors) retained from DEC-002/DEC-007.

**New typology split (v2):** To be recorded after validate_v2.py run. (v1 was 96.6% MidRise / 3.4% HighRise using height_proxy_m.)

---

## DEC-011 — GHS-BUILT-V Rebuild Detection (v2)

**Date:** 2026-04-19
**Decision:** Use GHS-BUILT-V R2023A 5-epoch time series (1975, 1990, 2000, 2010, 2020; 100m Mollweide) to compute rebuild-detection metrics and `recency_score` for era calibration.

**Dataset:**
- Source: Pesaresi et al. (2023). GHS-BUILT-V R2023A (built volume). JRC. doi:10.2905/C1B94E34-A29D-46A4-8D4A-99BD8D7ECEA5
- Tile R6_C29, 5 epochs. Downloaded via JRC FTP (14–46 MB ZIP each), cropped to Changsha bbox + 2 km buffer, stored as `data/integrated/ghs_built_v_changsha_{YEAR}.tif` (53–200 KB each; 0.7 MB total).

**Metrics computed:**
- `v{1975,1990,2000,2010,2020}`: sampled built volume (m³) at building centroid for each epoch.
- `first_builtup_epoch`: earliest epoch ≥ 100 m³ threshold.
- `peak_growth_epoch`: epoch whose preceding 15-yr interval had the largest absolute volume jump.
- `v_growth_post2000`, `v_growth_post2010`: relative volume growth ratios.
- `likely_rebuilt_post2000/2010`: flag for >50% volume growth.
- `recency_score`: composite index (see DEC-009).

**Key findings (18,826 buildings):**
- Likely rebuilt post-2000 (>50% growth): 4,522 buildings (24.0%)
- Likely rebuilt post-2010 (>50% growth): 1,108 buildings (5.9%)
- No volume signal (all epochs below 100 m³): 103 buildings (0.5%)
- Peak growth epoch distribution: Era 1-equivalent (≤2000) = 78.4%, Era 2 = 15.2%, Era 3 = 6.4% (provisional, before calibration)

**Why BUILT-V over GHS-AGE alone:** GHS-AGE records when a cell *first* became built-up, not when it was last substantially rebuilt. In urban cores where redevelopment is common, BUILT-V volume jumps more reliably detect the *current* building generation. The recency_score thus captures post-2000 intensification that GHS-AGE missed.

---

## DEC-012 — Typology Refinement v3: Ternary Classification (LowRise/MidRise/HighRise)

**Date:** 2026-04-19
**Decision:** Replace the binary MidRise/HighRise typology (v2) with a ternary LowRise/MidRise/HighRise typology using Era-prior constraints and footprint sanity checks.

**Problem with v2 binary typology:**
- v2 gave 43.4% HighRise overall, including **60% HighRise for Era 1 (pre-2000)**
- This contradicts Changsha building history: pre-2000 Changsha had almost no highrise residential
- Root cause 1: GHSL ANBH is a 100m grid-cell average, not per-building. In mixed-density cells containing both old lowrise stock and newer towers, the cell average (~18m) causes the lowrise buildings to be misclassified
- Root cause 2: The 18m binary threshold sits exactly on the mode of the ANBH distribution (mean = 17.9m), causing mass category flipping from a small height measurement error

**Solution — four prioritised rules (first match wins):**

| Rule | Condition | Typology | Rationale |
|---|---|---|---|
| 1. Era-1 prior | era_final = era1 AND h_eff < 30 m | LowRise | Pre-2000 Changsha had minimal highrise residential; override GHSL unless height is unambiguously highrise |
| 2. Large-footprint slab | footprint > 2500 m² AND h_eff < 25 m | LowRise | Commercial/industrial slabs (school, mall, factory) are lowrise for PV purposes |
| 3a. GHSL primary low | h_eff ≤ 18 m | LowRise | Standard 6-floor boundary |
| 3b. GHSL primary mid | 18 < h_eff ≤ 36 m | MidRise | 7–12 floors |
| 3c. GHSL primary high | h_eff > 36 m | HighRise | 13+ floors — unambiguous highrise |
| 4. Null fallback | ghsl_height_m = 0 | use height_proxy_m | 31 buildings only |

where h_eff = ghsl_height_m if > 0, else height_proxy_m.

**Results (18,826 buildings):**
- LowRise: 14,287 (75.9%) — Era-1 prior: 6,459; GHSL ≤18m: 7,184; large-slab: 644
- MidRise: 3,901 (20.7%) — all GHSL 18–36m
- HighRise: 638 (3.4%) — all GHSL >36m
- Era 1 HighRise: 489 (6.5% of Era 1) — ⚠ above 2% review threshold; these are buildings with GHSL ≥30m in Era 1 cells (likely pre-2000 hotel/office towers or GHSL overestimates)

**Flagged issue:** Era 1 HighRise remains at 6.5% (not ~0% as expected). These 489 buildings have GHSL ANBH ≥ 30m and escaped the Era-1 prior (which caps at 30m). See typology_validation_v3.md for the full list of top-20 buildings.

---

## DEC-013 — LowRise PV Generation Parameter Derivation

**Date:** 2026-04-19
**Decision:** Use 38.8 kWh/m²_floor/yr as the PV generation rate for LowRise buildings.

**Derivation (preserving Paper 2's physical assumptions):**
Paper 2 implies a roof-level PV productivity of ~239 kWh/m²_roof/yr:
- MidRise cross-check: 27.4 kWh/m²_floor × (3,135 m²_floor / 360 m²_roof) ≈ 239 kWh/m²_roof
- HighRise cross-check: 6.1 kWh/m²_floor × (7,836 m²_floor / 200 m²_roof) ≈ 239 kWh/m²_roof

LowRise assumptions:
- Representative LowRise archetype: 4-floor residential block, 500 m² footprint
- Total floor area = 4 × 500 = 2,000 m²
- Roof area = 500 m² (flat/nearly flat roof)
- Usable roof fraction = 65% (shading, access, HVAC obstructions) → 325 m² usable
- PV production = 325 m² × 239 kWh/m²_roof = 77,675 kWh/yr
- Per m²_floor: 77,675 / 2,000 = **38.8 kWh/m²_floor/yr**

This is physically consistent: LowRise has a higher roof-to-floor area ratio than MidRise or HighRise, so it generates more PV per floor m². The parameter preserves the same roof productivity (239 kWh/m²_roof) as Paper 2.

---

## DEC-014 — Hybrid Canonical Height (v4)

**Date:** 2026-04-19
**Decision:** Compute `canonical_height_m` as a hybrid of GHSL ANBH and height_proxy_m using four rules:

| Rule | Condition | canonical_height_m | height_source |
|---|---|---|---|
| 1 | ghsl null or ≤ 0 | height_proxy_m | proxy_only |
| 2 | \|ghsl − proxy\| < 5 m | (ghsl + proxy) / 2 | mean_agreement |
| 3 | ghsl > 2 × proxy | min(ghsl, proxy × 1.5) | capped_ghsl |
| 4 | otherwise | ghsl_height_m | ghsl_primary |

**Applied outcome (18,826 buildings):**
- proxy_only: 31 (0.2%), mean h = 9.5 m
- mean_agreement: 4,954 (26.3%), mean h = 10.2 m
- capped_ghsl: 7,869 (41.8%), mean h = 13.5 m
- ghsl_primary: 5,972 (31.7%), mean h = 14.5 m
- **Overall mean canonical_height_m: 12.94 m** (vs GHSL 17.9 m, proxy 10.6 m)

**Issue identified:** The `capped_ghsl` rule dominates (41.8%). Because proxy=9m is the OSM default for most buildings, `proxy × 1.5 = 13.5 m`. This caps 7,653 buildings to 13.5 m, all falling ≤18 m → LowRise. Combined with the Era-1 prior, the result is 98.8% LowRise — a degenerate typology. See DEC-015 for context and validation_v4.md (E9) for recommended alternatives.

**Rationale for keeping v4 as-is:** The result is scientifically documented and the issue is fully diagnosed. v4 is the canonical output for this iteration; v5 should address the degenerate typology before Task 3.

---

## DEC-015 — Era 3 LowRise Downgrade (v4)

**Date:** 2026-04-19
**Decision:** Downgrade Era 3 LowRise buildings to Era 2 when `v_growth_post2010 < 0.3`, on the basis that a building in a cell with no strong post-2010 volume growth was unlikely built in 2010–2020.

**Applied outcome:**
- 2,929 buildings downgraded from Era 3 → Era 2
- Era 3 reduced from 6,025 → 3,096 (16.4% of total)
- Era 2 increased from 5,271 → 8,200 (43.6%)

**New era distribution (v4, post-downgrade):**
- Era 1: 7,530 (40.0%) — unchanged
- Era 2: 8,200 (43.6%) — increased from 28.0%
- Era 3: 3,096 (16.4%) — decreased from 32.0%

**Note:** This deliberately breaks the 40/28/32 calibration target (DEC-009). Physical consistency of Era × Typology takes precedence over matching the target distribution when evidence (BUILT-V growth signal) contradicts the calibrated label. The shift is larger than anticipated because the v4 typology (98.8% LowRise) means nearly all Era 3 buildings are LowRise and subject to the downgrade rule.

**Sensitivity:** Using threshold 0.2 instead of 0.3 gives fewer downgrades — see validation_v4.md E8.

---

## DEC-016 — v5 Selective Height Rule for Typology (CANONICAL)

**Date:** 2026-04-19
**Decision:** Split canonical height into two fields to resolve v4's LowRise degeneracy (98.8%) without inflating floor areas or PV.

**Three-tier canonical height rule:**

| Tier | Condition | canonical_height_m (floor area) | typology_height_m (typology) | height_source |
|---|---|---|---|---|
| 1 | proxy NOT in [9.0, 10.5] | height_proxy_m | height_proxy_m | osm_real |
| 2a | proxy IS default, GHSL ≤ 18 m | GHSL | GHSL | ghsl_direct |
| 2b | proxy IS default, GHSL > 18 m | GHSL × 1.3 | GHSL | ghsl_bias_corrected |
| 2c | proxy IS default, GHSL null | proxy_m | proxy_m | default_fallback |

**Key design split (from diagnostic Stage E):**
- `typology_height_m` = GHSL direct (no bias correction) for LowRise/MidRise/HighRise thresholds
- `canonical_height_m` = GHSL × 1.3 bias-corrected for reference/sensitivity (stored, not used for floor count)
- `floor_count_est` = `height_proxy_m / 3` — uses Paper 1's original floor-count methodology, keeping floor area consistent with Paper 1 (72 Mm²)

**Why NOT use canonical_height_m for floor count:** Applying ×1.3 bias correction for floor count inflates floor area to ~141 Mm² (2× Paper 1) and PV to ~4.3 TWh (2.5× Paper 1). Using height_proxy_m for floor count gives floor area = 72 Mm² (Paper 1-consistent) and high-potential PV = 1.603 TWh (0.91× Paper 1, within ±10%).

**Height source breakdown (18,826 buildings):**
- ghsl_direct: 9,746 (51.8%)
- ghsl_bias_corrected: 7,884 (41.9%)
- osm_real: 1,167 (6.2%)
- default_fallback: 29 (0.2%)

**OSM default values identified:** [9.0, 10.5] — cover 93.8% of buildings; stored in `data/integrated/osm_default_proxy_values.json`

---

## DEC-017 — v5 Era Distribution and Downgrade (CANONICAL)

**Date:** 2026-04-19
**Decision:** Era calibration uses same 40/28/32 quantile starting point as v2–v4. Era 3 downgrade condition uses `typology_height_m ≤ 18` (GHSL direct ≤ 18m) AND `v_growth_post2010 < 0.3` — replaces v4's `typology == lowrise` condition.

**Rationale for using typology_height_m instead of typology label:** In v4, nearly all buildings were LowRise (98.8%), inflating the downgrade count to 2,929. In v5, using the continuous GHSL-direct height (≤ 18m threshold) as the physical criterion for the downgrade is more precise and independent of typology classification.

**Results:**

| Era | Post-downgrade | % |
|---|---|---|
| Era 1 | 7,530 | 40.0% |
| Era 2 | 7,190 | 38.2% |
| Era 3 | 4,106 | 21.8% |

- Downgraded (Era 3 → Era 2): 1,919 buildings
- Era 3 reduction: 6,025 → 4,106 (32.0% → 21.8%)
- Era 2 increase: 5,271 → 7,190 (28.0% → 38.2%)

**Comparison to v4:** v4 downgraded 2,929 buildings (47% more) because v4's 98.8% LowRise typology inflated the eligible pool. v5's 1,919 downgrades are more targeted (buildings in genuinely low-height cells with weak post-2010 growth signal).

**Note:** Era 3 at 21.8% is higher than v4's 16.4% but still below the 32.0% calibration target. Physical consistency (GHSL growth signal) continues to take precedence over exact target matching. Era 1 is exactly at target (40.0%) because the downgrade only affects Era 3 buildings.

---

## DEC-018 — Task 3 Baseline Energy: EUI Scaling and Validation

**Date:** 2026-04-19
**Decision:** Apply Paper 2 archetype EUI values (heating + cooling + other) to v5 floor areas via simple multiplication: `annual_energy_kwh = total_floor_area_m2 × EUI`.

**EUI values used (from data/from_paper2/processed/baseline_results.csv):**
| Era | Total EUI | Heating | Cooling | Other |
|---|---|---|---|---|
| Era 1 | 261.21 | 99.61 | 44.46 | 117.13 |
| Era 2 | 211.43 | 60.96 | 36.16 | 114.30 |
| Era 3 | 150.41 | 15.06 | 20.90 | 114.45 |

**City-scale results:**
- Total baseline energy: 15,382 GWh/yr
- City mean EUI: 213.5 kWh/m²/yr
- Heating / Cooling / Other: 4,535 / 2,532 / 8,313 GWh
- H/C ratio: 1.79 (within expected 1.3–1.8 HSCW range ✓)
- Era 1 energy share: 45.1% (expected dominant ✓)

**Known limitation (D1/D2 sanity flags):** The total energy estimate (~15,382 GWh) is higher than a naive comparison to Changsha's citywide residential electricity would suggest. This reflects three issues: (1) Paper 2 EUI values are EnergyPlus design-condition outputs, known to overestimate real-world consumption by 1.5–3× in Chinese stock literature; (2) the building stock includes commercial and institutional buildings, not just residential; (3) the "other" end-use category (117 kWh/m²/yr for Era 1) includes plug loads and DHW calibrated to design conditions. For Paper 3, EUI values are used for RELATIVE comparisons (era-to-era ratios, retrofit savings shares) rather than absolute city totals — framing results as 'simulated baseline' mitigates this limitation.

**Scripts:** `code/analysis/baseline_city.py`
**Outputs:** `data/integrated/archetype_eui.csv`, `baseline_city_building.csv`, `baseline_city_totals.csv`, `baseline_by_era.csv`, `baseline_by_grid.csv`, `validation_task3.md`, `figure/fig04_city_baseline.png`

---

## DEC-019 — Task 4 Retrofit Savings: Archetype Scaling Assumption

**Date:** 2026-04-19
**Decision:** Apply Paper 2's per-m² EUI delta values directly to all buildings in the same era: `savings_kwh = total_floor_area_m2 × delta_eui[era, retrofit]`.

**Retrofit delta EUI values (kWh/m²/yr, from Paper 2 baseline_results.csv + retrofit_results.csv):**
| Era | R1 Wall | R2 Window | R3 Roof | R4 Air seal | R5 Combined |
|---|---|---|---|---|---|
| Era 1 | 18.49 (7.1%) | 10.15 (3.9%) | 10.88 (4.2%) | 89.54 (34.3%) | 122.87 (47.0%) |
| Era 2 | 10.37 (4.9%) | 4.76 (2.2%) | 6.37 (3.0%) | 56.42 (26.7%) | 73.09 (34.6%) |
| Era 3 | 2.82 (1.9%) | 3.27 (2.2%) | 0.49 (0.3%) | 21.55 (14.3%) | 23.50 (15.6%) |

**City-scale R5 results:**
- Total savings: 5,634 GWh/yr (36.6% of 15,382 GWh baseline)
- Heating savings: 4,375 GWh (dominant — 77.6% of total R5 savings)
- Cooling savings: 838 GWh
- Post-R5 city total: 9,748 GWh/yr
- Post-R5 city mean EUI: 135.3 kWh/m²/yr (vs baseline 213.5)

**Era R5 savings:** Era 1 = 3,260 GWh (57.9% of total savings); Era 2 = 1,922 GWh (34.1%); Era 3 = 452 GWh (8.0%)

**Scaling assumption (limitation):** Per-m² savings are uniform within each era regardless of typology (LowRise/MidRise/HighRise). Paper 2 simulated only one archetype per era. Within-era heterogeneity (building form, vintage sub-era, orientation, urban shading) is not captured. This is a standard limitation of archetype-based UBEM; cite accordingly in manuscript.

**Air sealing dominance:** R4 (infiltration to 0.3 ACH) delivers 27.8% of baseline energy on its own — driven by Era 1's high initial infiltration rate. This finding is physically significant for Changsha's pre-code stock (air-tight construction was not standard before ~2000).

**Scripts:** `code/analysis/retrofit_city.py`
**Outputs:** `retrofit_deltas.csv`, `retrofit_city_building.csv`, `retrofit_city_totals.csv`, `retrofit_by_era.csv`, `retrofit_by_grid.csv`, `validation_task4.md`, `figure/fig05_city_retrofit.png`

---

## DEC-020 — Task 5 PV Monthly Profiles: Source and Self-Consumption Logic

**Date:** 2026-04-19

**Decision (monthly PV profile):** Derive monthly PV fractions from Paper 2 `processed/solar_monthly.csv` (actual pvlib simulation output, Era1 MidRise archetype, Changsha 28°N TMYx). Use Era 1 data as the representative city-wide PV profile.

**Actual monthly PV fractions (Paper 2 pvlib):**
Jan=7.1%, Feb=6.3%, Mar=7.5%, Apr=8.0%, May=9.2%, Jun=8.2%, Jul=11.1%, Aug=9.7%, Sep=9.3%, Oct=9.0%, Nov=7.6%, Dec=7.1%
Summer (Jul peak) as expected for Changsha's radiation climatology.

**Rationale:** Using Paper 2's actual pvlib output is more defensible than generic irradiance fractions. Era 1 MidRise profile selected as representative of the HP building stock (6,401 buildings, majority LowRise/MidRise). Era 1 and Era 2 monthly profiles are effectively identical in the CSV (same Changsha TMYx weather file used across eras; only panel area differs).

**Decision (demand profiles):** Heating/cooling/other monthly shares use HSCW typical seasonal patterns (task specification) rather than EnergyPlus monthly outputs, which are not available at city-scale resolution.

**Decision (self-consumption calculation):** `SC_ratio = min(PV_month, Demand_month) / PV_month`. Since annual city HP PV (1,603 GWh) << annual demand in both baseline (15,382 GWh) and R5 (10,167 GWh), PV is well below demand in every month → SC = 100% in all 12 months for both scenarios.

**Limitation:** Monthly profiles use normalised annual fractions applied to building-level archetypes. No sub-monthly or diurnal resolution. Actual instantaneous self-consumption may be lower due to peak-hour mismatch; this analysis is at monthly city-scale. This is a standard limitation for city-scale supply-demand studies without hourly metered data.

**Key results:**
- Self-consumption: 100% (baseline and R5) — all PV absorbed in every month
- PV-cooling coincidence factor: 0.425 (PV Jun–Sep share 38.3% / cooling Jun–Sep share 90%)
- Cooling coverage by PV in July: 23.4% (baseline), 34.9% (R5)
- Combined R5+PV savings: 6,817 GWh/yr (44.3% of baseline)
- No month has PV surplus at city scale

**Scripts:** `code/analysis/pv_supply_demand.py`
**Outputs:** `pv_city_building.csv`, `monthly_profiles.csv`, `monthly_supply_demand.csv`, `validation_task5.md`, `figure/fig07_supply_demand.png`, `figure/fig08_seasonal_match.png`

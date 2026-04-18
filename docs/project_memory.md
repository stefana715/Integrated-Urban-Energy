# Project Memory — Paper 3: Integrated Urban Retrofit + Solar Deployment under Climate Change

**Project title:** City-scale assessment of integrated building retrofit and rooftop solar deployment potential under climate change: Changsha, China

**Target journal:** Applied Energy / Energy and Buildings / Sustainable Cities and Society

**Study area:** Changsha, Hunan, China — Hot Summer Cold Winter (HSCW) climate zone, 28°N

---

## Data Inventory

### data/from_paper1/ — Solar Screening Outputs

**Top-level files (PRESENT):**
- `planning_metrics_aggregate.csv` — aggregated grid-level planning metrics
- `planning_metrics_summary.csv` — building-level summary with PV metrics (723 KB, main building database)
- `priority_grids.csv` — 146 priority 500 m grid cells with composite scores

**sensitivity/ (PRESENT):**
- `category_ablation_results.csv`
- `grid_size_comparison.csv`
- `height_proxy_comparison.csv`
- `threshold_comparison.csv`
- `weight_sensitivity_pairwise_rho.csv`
- `weight_sensitivity_results.csv`

**validation/ (PRESENT):**
- `benchmark_parameter_sensitivity.csv`
- `benchmark_robustness_results.csv`
- `buildings_pvlib_benchmark_zones.geojson` — buildings with PV benchmark zones
- `gsa_comparison.csv`
- `osm_quality_results.csv`
- `osm_quality_summary.csv`
- `pvlib_benchmark_validation_results.csv`
- `random_baseline_results.csv`
- `random_baseline_zone_detail.csv`

**figures/ — EMPTY** (only .gitkeep)
**tables/ — EMPTY** (only .gitkeep)

> **Note:** No standalone building-geometry GeoJSON at top level. `planning_metrics_summary.csv` is the primary per-building database; `buildings_pvlib_benchmark_zones.geojson` contains geometry for the benchmark subset. Check column headers before Task 1 to confirm OSM IDs, footprint areas, heights, and grid assignments are present.

---

### data/from_paper2/ — Retrofit Simulation Outputs

**climate/ (PRESENT — 11 files):**
- `CHN_HN_Changsha.576870_TMYx.2007-2021.epw` — baseline TMYx weather file
- `CHN_HN_Changsha.576870_TMYx.2007-2021.clm/.ddy/.stat/.wea/.pvsyst/.rain` — auxiliary climate files
- `Changsha_2050_SSP245.epw` / `Changsha_2050_SSP585.epw`
- `Changsha_2080_SSP245.epw` / `Changsha_2080_SSP585.epw`

**models/ (PRESENT — 26 IDF files):**
- `changsha_era1.idf`, `changsha_era2.idf`, `changsha_era3.idf` — baseline archetypes
- `changsha_era1_v26.idf`, `changsha_era2_v26.idf`, `changsha_era3_v26.idf` — v26 variants
- `retrofit_1_R1_Wall.idf` … `retrofit_1_R5_Combined.idf` — Era 1 retrofit packages
- `retrofit_2_R1_Wall.idf` … `retrofit_2_R5_Combined.idf` — Era 2 retrofit packages
- `retrofit_3_R1_Wall.idf` … `retrofit_3_R5_Combined.idf` — Era 3 retrofit packages
- `ASHRAE901_ApartmentHighRise_STD2004_base.idf` / `_STD2019_Atlanta.idf` — reference models
- `ASHRAE901_ApartmentMidRise_Pre1980_base.idf` / `_STD2004_Atlanta.idf` / `_STD2019_Atlanta.idf`

**processed/ (PRESENT — 9 CSV files):**
- `baseline_results.csv` — EUI by era under current climate
- `retrofit_results.csv` — EUI and savings by era × retrofit package
- `solar_results.csv` — PV generation per m²_floor by typology
- `solar_monthly.csv` — monthly PV generation profiles
- `climate_results.csv` — EUI under future climate scenarios
- `morris_results.csv` / `morris_results_era1/2/3.csv` — Morris sensitivity analysis

**results/ (PRESENT):**
- `all_results_tables.md` — compiled results tables

**figure/ (PRESENT — 8 PNG figures):**
- `fig01_morris_scatter.png`, `fig02_morris_bar.png`
- `fig04_baseline_eui.png`, `fig05_morris_sa.png`, `fig05b_morris_bar.png`
- `fig07_retrofit_savings.png`, `fig08_solar_pv.png`, `fig09_climate_impact.png`

**docs/ (PRESENT):**
- `project_memory.md`, `paper_plan.md`, `decision_log.md`, `claude_code_instruction.md`

**simulation/ (PRESENT — 50 EnergyPlus output directories):**
- Era baseline: `Era1_1980s_MidRise`, `Era2_2000s_MidRise`, `Era3_2010s_HighRise`
- Retrofit variants: `retrofit_1_R1_Wall` … `retrofit_3_R5_Combined` (15 dirs)
- Climate scenarios: `climate_Era1_*` / `climate_Era2_*` / `climate_Era3_*` × {Current, 2050_SSP245, 2050_SSP585, 2080_SSP245, 2080_SSP585} = 30 dirs

---

## Task Checklist

- [ ] **Task 1:** Data integration — merge Paper 1 building database with Paper 2 archetype results
- [x] **Task 2:** Building stock classification — assign era and typology to 18,826 buildings ✓ v1 (2026-04-19), ✓ v2 calibrated (2026-04-19), ✓ v3 ternary typology (2026-04-19)
- [ ] **Task 3:** City-scale baseline energy estimation
- [ ] **Task 4:** City-scale retrofit savings calculation
- [ ] **Task 5:** PV generation mapping to building stock
- [ ] **Task 6:** Monthly supply-demand matching analysis
- [ ] **Task 7:** Climate scenario scaling
- [ ] **Task 8:** Integrated grid-level scoring and priority ranking
- [ ] **Task 9:** Carbon emission calculations
- [ ] **Task 10:** Generate all figures (target: 14)
- [ ] **Task 11:** Write manuscript draft

---

## Key Parameters and Assumptions

### Building Stock
| Parameter | Value | Source |
|---|---|---|
| Total buildings, urban core (canonical) | 18,826 | Paper 1, OSM (29 dup IDs removed) |
| High-potential buildings | 6,401 (34%) | Paper 1 (recounted on 18,826 deduped) |
| Priority grid cells (500 m) | 146 / 671 total | Paper 1 |

### Era × Typology Classification v1 (GHS-AGE R2025A, superseded)
| Era | Buildings | % | MidRise | HighRise | Total floor area |
|---|---|---|---|---|---|
| Era 1 (pre-2000) | 14,977 | 79.4% | 14,567 | 410 | 55.46 Mm² |
| Era 2 (2000–2009) | 3,011 | 16.0% | 2,847 | 164 | 13.98 Mm² |
| Era 3 (2010–2020) | 867 | 4.6% | 799 | 68 | 3.15 Mm² |
| **Total** | **18,855** | | **18,213** | **642** | **72.59 Mm²** |

- ⚠ Superseded by v2 below. Pre-1980 epoch dominated at 54.3% (see DEC-008).

### Era × Typology Classification **v2** (BUILT-V calibrated, 40/28/32, canonical)
| Era | Buildings | % | MidRise | HighRise | Total floor area |
|---|---|---|---|---|---|
| Era 1 (pre-2000) | 7,530 | 40.0% | 3,008 | 4,522 | 49.39 Mm² |
| Era 2 (2000–2009) | 5,271 | 28.0% | 3,200 | 2,071 | 34.95 Mm² |
| Era 3 (2010–2020) | 6,025 | 32.0% | 4,452 | 1,573 | 37.16 Mm² |
| **Total** | **18,826** | | **10,660** | **8,166** | **121.50 Mm²** |

- Canonical unique buildings: 18,826 (29 OSM duplicate IDs removed from v1's 18,855)
- Era method: recency_score quantile calibration using GHS-BUILT-V 1975–2020 time series (see DEC-009, DEC-011)
- Height/typology method: GHSL ANBH (>18 m = HighRise); fallback to height_proxy_m for 31 buildings (see DEC-010)
- ⚠ Superseded by v3 typology below (binary gave 60% Era 1 HighRise — historically implausible)
- Concordance v1→v2: 44.6% same era label

### Era × Typology Classification **v3** (ternary: LowRise/MidRise/HighRise, canonical)
| Era | Buildings | % | LowRise | MidRise | HighRise | Total floor area |
|---|---|---|---|---|---|---|
| Era 1 (pre-2000) | 7,530 | 40.0% | 6,459 | 582 | 489 | — |
| Era 2 (2000–2009) | 5,271 | 28.0% | 3,292 | 1,879 | 100 | — |
| Era 3 (2010–2020) | 6,025 | 32.0% | 4,536 | 1,440 | 49 | — |
| **Total** | **18,826** | | **14,287 (75.9%)** | **3,901 (20.7%)** | **638 (3.4%)** | **—** |

- Era calibration (40/28/32) unchanged from v2
- Typology rules: Era-1 prior (<30m → LowRise); large-footprint slab (fp>2500m², h<25m → LowRise); GHSL thresholds (≤18m LowRise, ≤36m MidRise, >36m HighRise) — see DEC-012
- PV rates: LowRise=38.8, MidRise=27.4, HighRise=6.1 kWh/m²_floor/yr — see DEC-013
- Rebuild detection: 4,522 likely rebuilt post-2000 (24.0%), 1,108 post-2010 (5.9%)
- High-potential buildings by era: Era 1 = 2,152; Era 2 = 2,000; Era 3 = 2,249
- ⚠ Era 1 HighRise = 489 (6.5% of Era 1) — above 2% review threshold; see typology_validation_v3.md
- ⚠ City-scale PV: v3 = 2,867 GWh/yr vs Paper 1 reference 1,764 GWh/yr (+63%) — difference driven by GHSL height inflation in floor area calculation; investigate before Task 5

### Baseline Energy Use Intensity (current climate)
| Era | Description | EUI (kWh/m²/yr) |
|---|---|---|
| Era 1 | Pre-1980s / 1980s, MidRise | 261.2 |
| Era 2 | 2000s, MidRise | 211.4 |
| Era 3 | 2010s, HighRise | 150.4 |

### R5 Combined Retrofit Results
| Era | Post-retrofit EUI (kWh/m²/yr) | Savings |
|---|---|---|
| Era 1 | 138.3 | 47% |
| Era 2 | 138.3 | 35% |
| Era 3 | 126.9 | 16% |

### PV Generation (per m² of floor area)
| Typology | Generation | Basis |
|---|---|---|
| LowRise (≤6 floors, ≤18m) | 38.8 kWh/m²_floor/yr | DEC-013 derivation (4F×500m², 65% roof util.) |
| MidRise (7–12 floors, 18–36m) | 27.4 kWh/m²_floor/yr | Paper 2 original (72 kWp system) |
| HighRise (>12 floors, >36m) | 6.1 kWh/m²_floor/yr | Paper 2 original (40 kWp system) |

### Climate Change
| Scenario | Temperature change | Source |
|---|---|---|
| 2080 SSP5-8.5 | +4.04°C annual | Paper 2, CMIP6 morphing |

### Carbon & Grid
| Parameter | Value |
|---|---|
| Hunan grid emission factor | 0.5703 tCO₂/MWh (2022) |
| Changsha total electricity | ~16,800 GWh (2022) |

### Classification Rules
- **MidRise**: ≤6 floors — height proxy from Paper 1 (Era 1 & Era 2 archetypes)
- **HighRise**: >6 floors — height proxy from Paper 1 (Era 3 archetype)
- **Era assignment**: OSM `start_date` tag preferred; infer from building type + height + urban development zone where tag absent
- **Scale-up assumption**: Paper 2 per-m² EUI and PV generation values are transferable to classified building stock via floor-area weighting

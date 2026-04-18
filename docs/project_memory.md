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
- [ ] **Task 2:** Building stock classification — assign era and typology to 18,855 buildings
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
| Total buildings, urban core | 18,855 | Paper 1, OSM |
| High-potential buildings | 6,411 (34%) | Paper 1 |
| Priority grid cells (500 m) | 146 / 671 total | Paper 1 |

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
| Typology | Generation | System size |
|---|---|---|
| MidRise (≤6 floors) | 27.4 kWh/m²_floor/yr | 72 kWp |
| HighRise (>6 floors) | 6.1 kWh/m²_floor/yr | 40 kWp |

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

# Paper Plan — Paper 3

**Title:** City-scale assessment of integrated building retrofit and rooftop solar deployment potential under climate change: Changsha, China

**Target journal:** Applied Energy / Energy and Buildings / Sustainable Cities and Society

**Target length:** ~10,750 words body text

---

## Abstract (~250 words)

Urban buildings account for a substantial share of municipal energy consumption and carbon emissions in Chinese cities, yet the combined potential of envelope retrofit and rooftop photovoltaic (PV) deployment at city scale remains poorly quantified under realistic climate change trajectories. This study presents an integrated city-scale assessment for Changsha, China (28°N, Hot Summer Cold Winter zone), combining open-data solar potential screening (Paper 1, 18,855 OSM buildings) with EnergyPlus archetype simulations across three building eras and five retrofit packages (Paper 2). Buildings are classified by construction era and height typology; per-unit archetype results are scaled to the full stock via floor-area weighting. Under current climate, the baseline city-scale energy demand is estimated and disaggregated by era. Application of the R5 combined retrofit package (wall insulation + window upgrade + roof insulation + infiltration reduction) yields demand reductions of 47%, 35%, and 16% for Era 1, 2, and 3 stock respectively. Rooftop PV mapped to 6,411 high-potential buildings generates sufficient electricity to offset a significant fraction of post-retrofit demand, with monthly supply-demand matching revealing summer surpluses and winter deficits. Under the 2080 SSP5-8.5 scenario (+4.04°C), cooling demand increases partially erode retrofit savings, underscoring the importance of climate-proofing interventions. An integrated grid-level scoring framework identifies 146 priority 500 m cells where retrofit and PV co-deployment yields maximum carbon abatement per unit cost. Total carbon reduction potential is quantified using the Hunan provincial grid emission factor (0.5703 tCO₂/MWh). Findings provide actionable spatial priorities for municipal energy planners and demonstrate a replicable open-data methodology for HSCW cities.

**Keywords:** urban building energy; rooftop solar PV; building retrofit; climate change; city-scale; Changsha; HSCW; carbon reduction

---

## 1. Introduction (~1,500 words)

### 1.1 Context and motivation
- Global urbanisation and building sector emissions; China's dual-carbon targets (peak 2030, neutral 2060)
- Changsha as representative of rapidly urbanising HSCW Tier-2 cities (GDP, population, building stock growth)
- Two parallel levers: demand reduction (retrofit) and supply-side decarbonisation (rooftop PV)

### 1.2 The integration gap
- Existing studies treat retrofit and solar deployment as separate problems
- City-scale analyses rarely combine open-data building databases with physics-based archetype simulation
- Climate change is often ignored or treated as a sensitivity rather than a core scenario axis
- **Gap statement:** No study has simultaneously (a) mapped solar potential for an entire urban building stock from open data, (b) applied calibrated EnergyPlus archetype results to classify and scale that stock, and (c) evaluated combined retrofit + PV performance under multiple CMIP6 climate scenarios at city scale for a Chinese HSCW city.

### 1.3 Objectives
1. Classify 18,855 OSM buildings into era × typology cells using available metadata
2. Estimate city-scale baseline and post-retrofit energy demand by era
3. Map rooftop PV generation to the high-potential building subset and quantify monthly supply-demand matching
4. Assess how 2050/2080 SSP245/SSP585 climate change alters retrofit effectiveness and PV–demand balance
5. Produce an integrated grid-level priority ranking for co-deployment of retrofit and PV

### 1.4 Contributions
- First city-scale integration of open-data solar screening and archetype retrofit simulation for Changsha
- Temporal (monthly) supply-demand matching framework at grid level
- Climate-adjusted priority scoring transferable to other HSCW cities

### 1.5 Paper structure
Overview of remaining sections.

---

## 2. Literature Review (~1,500 words)

### 2.1 Urban-scale building energy modelling (UBEM)
- Archetype-based vs bottom-up stock models; key studies (Reinhart & Cerezo Davila 2016; Quan et al. 2020; Hong et al. 2020)
- Chinese UBEM studies: focus on commercial/office; residential stock underrepresented
- Limitations of national-level vs city-level analyses

### 2.2 Rooftop solar deployment at urban scale
- GIS-based solar resource mapping; LiDAR vs OSM approaches
- Large-scale PV potential studies (Bódis et al. 2019; Gagnon et al. 2016; Liu et al. 2021 for Chinese cities)
- Open-data approaches: pvlib, PVGIS; accuracy benchmarking

### 2.3 Climate-resilient urban energy
- IPCC AR6 building sector findings; morphed weather files; CMIP6 downscaling
- Retrofit performance under climate change: cooling load penalty vs heating load savings
- Gap: most retrofit + climate studies are single-building or limited stock samples

### 2.4 Integrated retrofit + solar approaches
- Few integrated studies: Ferrara et al. (net-zero districts); Lim et al. (Korean apartment blocks)
- No city-scale open-data integrated study for Chinese HSCW cities identified
- Policy context: China's "urban renewal" programme; 14th Five-Year Plan solar targets

---

## 3. Methodology (~2,500 words)

### 3.1 Study area — Changsha, HSCW zone, 28°N
- Administrative boundary; urban core definition (18,855-building footprint)
- Climate characterisation: CDD/HDD, solar irradiance, seasonal patterns
- Building stock overview: dominant residential typologies, era distribution
- 671 planning grid cells (500 m × 500 m) covering urban core

### 3.2 Data sources
| Dataset | Source | Coverage | Key variables |
|---|---|---|---|
| Building footprints & metadata | OSM via Paper 1 | 18,855 buildings | Geometry, height proxy, `start_date`, `building` tag |
| Grid-level PV metrics | Paper 1 (`planning_metrics_summary.csv`, `priority_grids.csv`) | 671 grids / 6,411 high-potential bldgs | PV score, annual kWh/m²_floor |
| Archetype EUI (baseline) | Paper 2 (`processed/baseline_results.csv`) | 3 eras × MidRise/HighRise | kWh/m²/yr by end-use |
| Archetype retrofit savings | Paper 2 (`processed/retrofit_results.csv`) | 3 eras × 5 packages | Absolute & % EUI reduction |
| Monthly PV generation | Paper 2 (`processed/solar_monthly.csv`) | MidRise, HighRise | Monthly kWh/m²_floor |
| Climate scenarios | Paper 2 (`climate/`) | Current + 2050/2080 SSP245/SSP585 | EPW morphed files |
| Climate EUI results | Paper 2 (`processed/climate_results.csv`) | 3 eras × 5 scenarios | EUI by scenario |
| Hunan grid emission factor | National Energy Administration (2022) | Provincial | 0.5703 tCO₂/MWh |

### 3.3 Building stock classification — assigning era and typology
- Step 1: Extract OSM `start_date` tags; map to Era 1 (≤1990), Era 2 (1991–2005), Era 3 (>2005)
- Step 2: For untagged buildings, rule-based inference (building type tag + height proxy + spatial development zone)
- Step 3: Assign typology — MidRise (≤6 floors) vs HighRise (>6 floors) from height proxy
- Step 4: Compute floor area per building (footprint × floors)
- Validation: compare era distribution against Changsha statistical yearbook building-age data

### 3.4 Archetype-to-stock mapping
- Map each classified building to its corresponding Paper 2 archetype cell (era × typology)
- Assign baseline EUI [kWh/m²/yr] and per-typology PV yield [kWh/m²_floor/yr]
- Floor-area weighting to derive building-level annual energy demand and PV generation
- Aggregate to grid level for spatial analysis

### 3.5 City-scale retrofit impact estimation
- Apply R5 combined retrofit EUI values to classified stock
- Compute absolute savings [kWh/yr] and percentage savings per building and per grid
- Sensitivity: vary era classification proportions ±10% to bound uncertainty
- Note: R1–R4 individual packages also reported for policy cost-tiering analysis

### 3.6 Rooftop PV integration
- Restrict PV mapping to 6,411 high-potential buildings (Paper 1 threshold)
- Apply MidRise/HighRise specific annual PV yield [kWh/m²_floor]
- Compute net annual balance: PV generation − post-retrofit demand (per building, per grid)
- Express as Self-Sufficiency Ratio (SSR) and Feed-in Excess Ratio (FER)

### 3.7 Supply-demand temporal matching
- Use monthly PV generation profiles (`solar_monthly.csv`) and monthly end-use demand proportions (from EnergyPlus simulation outputs)
- Compute monthly surplus/deficit per grid
- Metrics: monthly coverage fraction, peak-summer excess, winter deficit
- Aggregate to city level for seasonal storage or grid export implications

### 3.8 Climate change scenario analysis
- Apply climate-adjusted EUI values from `climate_results.csv` for each scenario × era cell
- Recalculate city-scale demand, retrofit savings, and net PV balance for each scenario
- Compute climate penalty: additional cooling demand vs preserved heating savings under SSP585-2080
- Report delta-EUI relative to current climate for baseline and R5-retrofit conditions

### 3.9 Grid-level integrated scoring and priority ranking
- Composite score per 500 m grid:
  `Score = w₁ × NormRetrofitSaving + w₂ × NormPVGeneration + w₃ × NormNetBalance + w₄ × NormCarbonReduction`
- Default weights equal (0.25 each); sensitivity tested with Paper 1 weight sensitivity framework
- Rank 671 grids; identify top-tier priority cells (top 20% ≈ 146 grids, consistent with Paper 1)
- Map spatial distribution of priority zones relative to urban development patterns

---

## 4. Results (~3,000 words)

### 4.1 Building stock classification outcome
- Era distribution (count and floor area) for 18,855 buildings
- OSM tag coverage rate; proportion requiring rule-based inference
- Typology split: MidRise vs HighRise by era
- Table: Building stock summary by era × typology

### 4.2 City-scale baseline energy demand
- Total annual electricity demand [GWh] by era and end-use (heating, cooling, lighting, equipment)
- Spatial distribution: demand density map [kWh/m²_footprint] by 500 m grid
- Comparison context: city-reported 16,800 GWh total electricity (2022)

### 4.3 City-scale retrofit savings
- R5 total demand reduction [GWh/yr] and percentage
- Breakdown by era; identify which era offers greatest absolute saving vs greatest relative saving
- Map: retrofit saving density by grid
- R1–R4 stacked contribution to R5 savings (waterfall chart)

### 4.4 PV generation vs post-retrofit demand
- Total annual PV generation potential [GWh] from 6,411 high-potential buildings
- Net annual balance [GWh]: surplus or deficit at city and grid level
- SSR distribution histogram
- Map: net balance by grid (surplus in green, deficit in red)

### 4.5 Seasonal supply-demand matching
- Monthly city-level PV generation vs demand (stacked area chart)
- Summer (Jun–Aug): PV surplus characterisation; winter (Dec–Feb): deficit characterisation
- Monthly coverage fraction by building typology
- Implication for grid-export or storage sizing

### 4.6 Climate change impact on retrofit effectiveness
- EUI change under 2080 SSP5-8.5 vs current: by era and by end-use
- Cooling load increase vs heating load decrease: net effect on annual EUI
- Residual retrofit saving under each scenario (does R5 remain cost-effective under +4°C?)
- Table: EUI (baseline and R5) × era × scenario

### 4.7 Priority grid identification and spatial patterns
- Distribution of integrated scores across 671 grids
- Top 146 priority grids: spatial clusters, overlap with paper 1 priority zones
- Characterisation of top grids: era composition, retrofit saving, PV yield
- Map: priority tier map (high / medium / low / inactive)

### 4.8 Carbon reduction potential
- Baseline carbon emissions [tCO₂/yr]: total and per-capita
- R5 retrofit reduction [tCO₂/yr]
- PV offsetting [tCO₂/yr]
- Combined R5 + PV reduction [tCO₂/yr] and as % of Changsha building sector
- Climate scenario impact on carbon balance (2080 SSP5-8.5)

---

## 5. Discussion (~1,500 words)

### 5.1 Interpretation of key findings
- Era 1 stock as highest-priority retrofit target (47% savings, oldest stock)
- PV generation concentrated in mid-rise stock due to more favourable floor-area ratio
- Summer surplus as a grid management challenge; winter deficit drives heating dependence

### 5.2 Climate change implications
- Partial erosion of retrofit savings under SSP5-8.5 reinforces the need for cooling-focused measures
- Climate-adjusted priority ranking shifts relative to current-climate analysis
- Policy implication: design retrofit packages for future climate, not historical norms

### 5.3 Integrated vs sequential planning
- Co-location of retrofit and PV in priority grids reduces implementation overhead
- Comparison: optimising retrofit alone vs PV alone vs integrated — carbon abatement per unit cost

### 5.4 Limitations
- Archetype transferability: within-class variation unresolved
- OSM building-age coverage in Changsha (~X% tagged) — quantify
- PV yield assumes flat roofs; complex roof forms excluded
- No occupant behaviour variation; HVAC system efficiency held constant
- City-level electricity total from statistical yearbook; sector breakdown estimated

### 5.5 Transferability to other HSCW cities
- Replicable open-data workflow (OSM + pvlib + EnergyPlus archetypes)
- Key inputs needed for other cities: OSM coverage quality, era proportions, local grid factor
- Brief comparison to Wuhan, Nanjing, Chongqing as comparable HSCW cities

---

## 6. Conclusion (~500 words)

- Summary of integrated approach and city-scale findings for Changsha
- Quantified headline results: total retrofit saving [GWh, %], PV generation [GWh], carbon reduction [tCO₂]
- Climate robustness: R5 retrofit remains beneficial under all scenarios; PV–demand balance worsens modestly under SSP5-8.5
- 146 priority grids identified for co-deployment — actionable for municipal government
- Methodological contribution: replicable open-data UBEM + solar screening integration framework
- Future work: (a) incorporate measured building-level data as it becomes available; (b) add cost-benefit analysis; (c) extend to commercial stock

---

## Target Figures (14 total)

| # | Description | Key data sources |
|---|---|---|
| 1 | Study area map: Changsha urban core, 671 grid cells, building footprints | OSM, Paper 1 |
| 2 | Building stock classification: era × typology distribution (treemap or bar) | Task 2 output |
| 3 | City-scale baseline EUI map (500 m grid, kWh/m²) | Task 3 output |
| 4 | Retrofit savings by era × package (waterfall / grouped bar) | Task 4 output |
| 5 | Retrofit saving density map (500 m grid) | Task 4 output |
| 6 | PV generation potential map (500 m grid, GWh/yr) | Task 5 output |
| 7 | Net annual PV–demand balance map (surplus / deficit) | Task 5 output |
| 8 | Monthly supply-demand matching (stacked area, city level) | Task 6 output |
| 9 | Monthly coverage fraction by typology (heatmap) | Task 6 output |
| 10 | Climate impact: EUI change by era × scenario (grouped bar) | Task 7 output |
| 11 | Climate-adjusted retrofit effectiveness (line chart, 5 scenarios) | Task 7 output |
| 12 | Integrated priority score map (4 tiers) | Task 8 output |
| 13 | Carbon reduction decomposition (stacked bar: retrofit + PV, by era) | Task 9 output |
| 14 | Scenario comparison: carbon balance under 4 climate futures | Task 9 output |

---

## Target Tables (6 total)

| # | Description |
|---|---|
| T1 | Building stock summary by era × typology (count, floor area, % of total) |
| T2 | Baseline EUI by era × end-use (kWh/m²/yr) |
| T3 | Retrofit results: EUI and savings for R1–R5 × 3 eras |
| T4 | Climate scenario EUI: baseline and R5, 5 scenarios × 3 eras |
| T5 | Grid-level integrated scoring weights and sensitivity |
| T6 | Carbon reduction summary: baseline, R5, PV, combined (current + 2080 SSP5-8.5) |

# Paper 3 — Comprehensive Project Summary

**Title:** City-scale assessment of integrated building retrofit and rooftop solar deployment potential under climate change: Changsha, China

**Date:** 2026-04-19  
**Status:** Analysis complete (Tasks 1–9). Manuscript writing (Task 10) pending.  
**Author:** Stefana  
**Repository:** `/Users/stefana/Desktop/Integrated-Urban-Energy`

---

## 1. Project Status Summary

All analytical tasks are complete. The paper integrates two prior studies:

- **Paper 1** — OSM-based solar screening of 18,826 residential buildings in Changsha's urban core, identifying 6,401 high-potential rooftop PV candidates (1.764 TWh/yr combined potential).
- **Paper 2** — EnergyPlus archetype simulation of 3 construction eras × 3 typologies × 5 retrofit measures × 5 climate scenarios for Changsha residential stock.

Paper 3 applies Paper 2's per-m² EUI and climate factors to Paper 1's building stock at city scale, adding a grid-level integrated priority scoring framework that jointly optimises solar, retrofit, carbon, and climate dimensions.

### Task checklist

| Task | Description | Status |
|------|-------------|--------|
| Task 1 | Data integration | ✅ Complete |
| Task 2 | Building stock classification v1–v5 | ✅ Complete (v5 canonical) |
| Task 3 | City-scale baseline energy estimation | ✅ Complete |
| Task 4 | City-scale retrofit savings calculation | ✅ Complete |
| Task 5 | PV generation + monthly supply-demand | ✅ Complete |
| Task 6 | Climate change scenario analysis | ✅ Complete |
| Task 7 | Integrated grid-level priority scoring | ✅ Complete |
| Task 8 | Consolidated carbon emission accounting | ✅ Complete |
| Task 9 | Unified publication figure generation | ✅ Complete (14 figures) |
| Task 10 | Manuscript writing | ⬜ Pending |

---

## 2. Headline Numbers

These are the key findings for the abstract and conclusion.

### Building stock
| Metric | Value |
|--------|-------|
| Total buildings | 18,826 |
| High-potential PV buildings | 6,401 (34%) |
| Total floor area | 72.05 Mm² |
| Era 1 (pre-2000) | 7,530 buildings (40.0%) |
| Era 2 (2000–2009) | 7,190 buildings (38.2%) |
| Era 3 (2010–2020) | 4,106 buildings (21.8%) |
| LowRise typology | 13,917 (73.9%) |
| MidRise typology | 4,022 (21.4%) |
| HighRise typology | 887 (4.7%) |

### Baseline energy (Task 3)
| Metric | Value |
|--------|-------|
| City total annual energy | 15,382 GWh/yr |
| City mean EUI | 213.5 kWh/m²/yr |
| Heating / Cooling / Other | 4,535 / 2,532 / 8,313 GWh |
| H/C ratio | 1.79 (heating-dominant HSCW climate) |
| Era 1 share | 45.1% of city baseline |

### Retrofit savings (Task 4)
| Metric | Value |
|--------|-------|
| R5 (combined) total savings | 5,634 GWh/yr (−36.6%) |
| Post-R5 city EUI | 135.3 kWh/m²/yr |
| Best single measure | R4 air sealing: −27.8% |
| Era 1 savings share | 57.9% (3,260 GWh) |
| Era 2 savings share | 34.1% (1,922 GWh) |
| Era 3 savings share | 8.0% (452 GWh) |

### Rooftop PV (Task 5)
| Metric | Value |
|--------|-------|
| HP buildings annual PV | 1,603 GWh/yr |
| Self-consumption rate | 100% (all 12 months) |
| PV-cooling coincidence factor | 0.425 |
| PV cooling coverage (July, baseline) | 23.4% |
| PV cooling coverage (July, R5) | 34.9% |

### Combined R5 + PV (Task 5)
| Metric | Value |
|--------|-------|
| Combined savings | 6,817 GWh/yr |
| Net demand reduction | −44.3% vs baseline |
| R5 retrofit component | 5,214 GWh (76%) |
| PV self-consumed component | 1,603 GWh (24%) |

### Climate change (Task 6)
| Metric | Value |
|--------|-------|
| Baseline 2080 SSP5-8.5 | 14,701 GWh/yr (−4.4% vs current) |
| H/C tipping point | 2050 SSP5-8.5 (H/C = 0.97 < 1) |
| R5 heating under 2080 SSP5-8.5 | 27.5 GWh ≈ 0% |
| R5+PV net demand 2080 SSP5-8.5 | 8,668 GWh/yr (+6.4% vs current R5+PV) |
| Warming sensitivity of combined strategy | +579 GWh spread across all future scenarios (8.8%) |

### Grid priority (Task 7)
| Metric | Value |
|--------|-------|
| Total occupied grids | 671 |
| Top-50 buildings | 1,339 |
| Top-50 floor area | 16.9 Mm² |
| Top-50 R5 savings | 1,199 GWh/yr |
| Top-50 PV generation | 343 GWh/yr |
| Top-50 CO₂ avoided | 879 kt/yr (21.3% of city) |
| Paper 1 overlap | 28/50 (56%) |
| New grids surfaced | 22/50 (44%) |
| #1 grid | 933 (Kaifu, Era 2; score 91.1) |
| Dominant district | Yuelu (31/50 grids) |

### Carbon accounting (Task 8)
| Metric | Value |
|--------|-------|
| Current baseline CO₂ | 8,772 kt/yr |
| R5+PV CO₂ | 4,645 kt/yr |
| Annual avoided CO₂ (current) | **4,127 kt/yr (−47%)** |
| Per-era split (Era 1/2/3) | 2,148 / 1,458 / 522 kt/yr (52/35/13%) |
| Cumulative 2025–2080 (immediate) | **114,909 kt CO₂ (115 Mt)** |
| Stepwise 0→100% by 2060 | 63,480 kt (55% of immediate) |
| Paper 3 vs Paper 1 PV-only | **4.10× more carbon impact** |
| Retrofit fraction of combined | 78% (3,213 / 4,127 kt) |

---

## 3. Methodology Overview

### 3.1 Building stock classification (v5, canonical)

1. **Geometry:** 18,826 deduplicated OSM buildings from Paper 1 GeoJSON.
2. **Era classification:** GHS-AGE R2025A (100m, JRC) for initial epoch → calibrated to 40/28/32% via GHS-BUILT-V recency score quantile ranking. Era 3 buildings with GHSL height ≤ 18m AND v_growth_post2010 < 0.3 downgraded to Era 2 (1,919 buildings).
3. **Typology classification:** `typology_height_m` = GHSL ANBH direct. Thresholds: ≤18m → LowRise, 18–36m → MidRise, >36m → HighRise.
4. **Floor area:** `height_proxy_m / 3` (Paper 1 methodology; floor-to-floor 3m) × footprint. Total = 72.05 Mm².
5. **High-potential flag:** Transferred from Paper 1 `is_high_potential` field (1 = HP, 0 = standard).

### 3.2 City-scale energy scaling

All city-scale energy estimates use archetype EUI (kWh/m²/yr) × building floor area:

```
building_energy = archetype_EUI[era, typology] × floor_area_m2
city_energy = Σ building_energy
```

Paper 2 archetype EUI values are EnergyPlus design-condition outputs — known to overestimate real-world consumption by 1.5–3× in Chinese residential stock. Results are used for **relative comparisons** (savings fractions, era ratios, scenario deltas) rather than absolute totals.

### 3.3 PV generation

PV rates (kWh/m²_floor/yr) from Paper 2 pvlib simulation:
- LowRise: 38.8 (derived from roof productivity = 239 kWh/m²_roof/yr × 65% usable × 500m² roof / 2000m² floor)
- MidRise: 27.4
- HighRise: 6.1

Applied only to high-potential buildings (is_high_potential = 1). Annual HP total = 1,603 GWh/yr.

### 3.4 Climate scaling

Per-scenario, per-era heating/cooling factors from Paper 2 `climate_results.csv`:
- `h_factor = heat_EUI[scenario] / heat_EUI[current]`  
- `c_factor = cool_EUI[scenario] / cool_EUI[current]`

Factors applied to the baseline heating/cooling components at building level. "Other" (lighting/appliances/DHW) held constant. PV assumed constant across scenarios (−0.4%/K temperature penalty → −1.6% for +4°C → negligible at city scale).

### 3.5 Integrated grid scoring

Four dimensions normalised to 0–100 via percentile rank, then combined with equal-pair weights:
- **Solar score (0.30):** Mean Paper 1 solar screening score per 500m grid cell
- **Retrofit score (0.30):** Total R5 savings (GWh) per grid — captures building stock density × era composition
- **Carbon score (0.20):** Combined R5 + PV CO₂ avoided per grid (ktCO₂)
- **Climate score (0.20):** Inverted relative R5 demand increase under 2080 SSP5-8.5 (lower delta = more resilient = higher score)

Top-50 grids identified by integrated score. Overlap with Paper 1's 146 solar-priority grids computed.

---

## 4. Results by Task

### 4.1 Building Stock Classification (Task 2)

Five classification iterations produced v5 as the canonical final output. The key challenge was that raw GHS-AGE classified 79.4% of buildings as pre-1980 (Era 1) due to its "first-built" semantics in urban cells with long occupation history. The v5 solution uses GHS-BUILT-V volume time series to compute a recency score, enabling calibration to physically plausible proportions.

**v5 era distribution:** Era 1 = 40.0%, Era 2 = 38.2%, Era 3 = 21.8%  
**v5 typology distribution:** LowRise = 73.9%, MidRise = 21.4%, HighRise = 4.7%  
**Known limitation:** Era 1 HighRise = 7.6% (>5% review threshold) — these 575 buildings have GHSL ANBH ≥ 30m but are classified pre-2000, possibly due to hotel/office towers or GHSL overestimates in dense cells.

### 4.2 Baseline Energy (Task 3)

City total: **15,382 GWh/yr** — Era 1 dominates at 45.1% despite being only 40% of buildings, because its EUI (261.2 kWh/m²/yr) is 74% higher than Era 3 (150.4 kWh/m²/yr). H/C ratio 1.79 is consistent with Changsha's HSCW (Hot Summer Cold Winter) climate.

### 4.3 Retrofit Savings (Task 4)

R4 (air sealing to 0.3 ACH) delivers 27.8% savings on its own — driven by Era 1's uncontrolled infiltration. Combined R5 achieves 36.6% city savings.

**Post-R5 EUI by era:** Era 1 = 138.3, Era 2 = 138.3, Era 3 = 126.9 kWh/m²/yr  
**Note:** Era 1 and Era 2 post-R5 EUI are identical because Paper 2 used the same MidRise R5 archetype for both eras.

### 4.4 PV Supply-Demand Matching (Task 5)

HP PV (1,603 GWh/yr) is well below city demand in every month, guaranteeing 100% self-consumption. The PV-cooling coincidence factor (0.425) means PV aligns reasonably well with peak cooling demand (Jun–Sep), though PV can only offset ~23% of July cooling even at baseline.

Combined R5+PV reduces net demand by **44.3%** — with retrofit accounting for 76% of the combined impact and PV 24%.

### 4.5 Climate Change Analysis (Task 6)

The key finding is that **baseline total demand slightly decreases** under climate warming (−4.4% by 2080 SSP5-8.5) because Changsha's heating-heavy stock (H/C = 1.79) loses more heating demand than it gains in cooling. This "perverse" result reverses post-retrofit: under R5, heating is near-zero and the remaining cooling growth causes demand to rise (+5.4% by 2080 SSP5-8.5).

The H/C tipping point — where cooling first exceeds heating at city scale — occurs at **2050 SSP5-8.5** (H/C = 0.97). R5 is already at this tipping point under current climate (heating near-zero by design).

### 4.6 Integrated Grid Priority Scoring (Task 7)

The multi-dimensional scoring surfaces 22 grids (44% of top-50) that are NOT in Paper 1's solar-only top tier. These are dense Era 1 grids (e.g., #929 in Yuelu with 65.5 GWh R5 savings, #1004 in Tianxin with 134.4 GWh) where rooftop solar scores are moderate but retrofit potential is very high.

Top-50 grids deliver **21.3% of city CO₂ savings** while covering only 7.1% of buildings — indicating these grids are highly leveraged intervention points. Yuelu district dominates (31/50), reflecting its concentration of both newer high-solar-score stock and dense older retrofit-priority stock.

Ranking is robust to weight sensitivity: 39–42/50 retain top-50 status under alternative weights. Climate score has lowest discriminatory power (scores range only 4.6–5.6%) because Era 1/2 post-retrofit climate factors are identical.

### 4.7 Carbon Accounting (Task 8)

Annual avoided CO₂ = **4,127 kt/yr** under current R5+PV. This is **4.10× more** than Paper 1's PV-only pathway (1,006 kt/yr), with retrofit alone (3,213 kt/yr) accounting for 78% of the combined impact.

The declining grid emission factor (0.5703 → 0.30 → 0.10 tCO₂/MWh by 2025/2050/2080) reflects China's dual-carbon trajectory and is the key methodological choice for cumulative projections. Under this trajectory, **immediate deployment saves 115 Mt CO₂** (2025–2080) vs BAU; delayed stepwise deployment (0→100% by 2060) saves only 63.5 Mt (55% of immediate).

The 115 Mt figure should be a headline for the manuscript — it contextualises the scale of the opportunity at city level.

---

## 5. Key Design Decisions

The following decisions have the most bearing on interpreting the results. Full rationale is in `docs/decision_log.md`.

| ID | Decision | Impact |
|----|----------|--------|
| DEC-016 | v5 uses `height_proxy_m / 3` for floor count (not GHSL×1.3) | Keeps floor area at 72 Mm² — Paper 1-consistent. Using bias-corrected GHSL height would inflate floor area to 141 Mm² and PV to 4.3 TWh. |
| DEC-017 | Era 3 downgrade uses GHSL height ≤ 18m AND v_growth_post2010 < 0.3 | 1,919 buildings downgraded Era 3→2; Era 3 at 21.8% (below 32% calibration target). Physical consistency over target matching. |
| DEC-018 | EUI scaling uses design-condition EnergyPlus outputs | City total (15,382 GWh) overestimates real metered consumption by 1.5–3×. Paper frames results as simulated baseline; ratio comparisons (savings %, era shares) are valid. |
| DEC-019 | Uniform per-m² savings within each era for all typologies | No typology-level retrofit differentiation; Paper 2 simulated one archetype per era. Standard UBEM limitation. |
| DEC-020 | Monthly PV profiles from Paper 2 pvlib (Era 1 MidRise TMYx) | More defensible than generic irradiance fractions. Self-consumption 100% confirmed by city-scale PV << monthly demand in all months. |
| DEC-021 | PV held constant across climate scenarios (no temperature penalty) | Conservative: −1.6% for 2080 SSP5-8.5 (+4°C) is negligible vs 523 GWh demand increase. |
| DEC-022 | Equal 30/30/20/20 weights for solar/retrofit/carbon/climate | Solar+retrofit are primary deployment metrics; carbon/climate are derived (slightly downweighted). Robust under sensitivity (33–42/50 retain top-50). |
| DEC-023 | Declining grid EF: 0.5703 → 0.30 → 0.10 tCO₂/MWh (2025/2050/2080) | Reduces cumulative savings from 238 Mt (constant EF) to 115 Mt (declining). More realistic and avoids overstating late-century benefit. |
| DEC-013 | LowRise PV rate = 38.8 kWh/m²_floor/yr (derived from 239 kWh/m²_roof × 65% usable) | Consistent with Paper 2's MidRise/HighRise implicit roof productivity. LowRise generates more PV per floor m² due to high roof-to-floor ratio. |

---

## 6. Chinese Spoken Version (Supervisor Meeting Notes)

本文是一篇城市尺度的建筑节能与屋顶光伏综合评估研究，研究区域为长沙市城市核心住宅建筑群。

**主要结论（用于汇报）：**

- 研究纳入18,826栋建筑，总建筑面积7,205万平方米
- 当前基准能耗：15,382 GWh/年，单位面积能耗213.5 kWh/m²/年
- R5综合改造方案可节能5,634 GWh/年（降低36.6%）
- 高潜力屋顶光伏总发电量：1,603 GWh/年，光伏自消纳率100%
- R5改造+光伏综合净需求降低44.3%
- 年减碳量：**4,127 kt CO₂**（约412.7万吨），是Paper 1仅光伏方案的4.10倍
- 累计2025–2080年立即实施可减碳**115 Mt**（1.15亿吨）
- 综合优先网格分析识别出50个重点500m网格，占全市碳减排效益的21.3%
- 其中22个新网格（44%）是多维度评分独有发现——这些网格仅靠太阳能筛查会被忽视

**气候变化关键发现：**
- 长沙采暖主导（H/C=1.79）：气候变暖会小幅降低未改造建筑总能耗（−4.4%）
- H/C临界点出现在2050年SSP5-8.5情景下
- R5改造后，采暖需求接近零，城市能耗对气候变化更敏感于制冷需求（+5.4%至2080年）

---

## 7. Deliverables Index

### Data files (`data/integrated/`)

| File | Rows | Size | Content |
|------|------|------|---------|
| classified_buildings.csv | 18,826 | 6.2 MB | Canonical v5 building stock (no geometry) |
| classified_buildings.geojson | 18,826 | 25 MB | Canonical v5 with geometry |
| archetype_eui.csv | 3 | 4 kB | Per-era EUI values from Paper 2 |
| baseline_city_building.csv | 18,826 | 1.4 MB | Per-building baseline energy |
| baseline_city_totals.csv | 1 | 4 kB | City-level totals |
| baseline_by_era.csv | 3 | 4 kB | Baseline grouped by era |
| baseline_by_grid.csv | 1,722 | 72 kB | Baseline aggregated to 500m grids |
| retrofit_deltas.csv | 15 | 4 kB | Per-era per-measure EUI savings |
| retrofit_city_building.csv | 18,826 | 2.0 MB | Per-building retrofit savings |
| retrofit_city_totals.csv | 5 | 4 kB | City-level totals per measure |
| retrofit_by_era.csv | 15 | 4 kB | Retrofit grouped by era × measure |
| retrofit_by_grid.csv | 1,722 | 60 kB | Retrofit aggregated to grids |
| pv_city_building.csv | 6,401 | 240 kB | Per-HP-building PV generation |
| monthly_profiles.csv | 12 | 4 kB | Monthly PV fractions (Paper 2 pvlib) |
| monthly_supply_demand.csv | 12 | 4 kB | Monthly PV vs demand (baseline + R5) |
| climate_factors.csv | 30 | 4 kB | Per-era per-scenario heating/cooling factors |
| climate_city_results.csv | 10 | 4 kB | City demand by scenario (baseline + R5) |
| climate_net_demand.csv | 10 | 4 kB | Net demand after PV offset by scenario |
| integrated_grid_ranking.csv | 671 | 88 kB | Full grid scores and top-50 flag |
| policy_summary.csv | 8 | 4 kB | Summary statistics for top-50 grids |
| carbon_annual_scenarios.csv | 20 | 4 kB | Annual CO₂ by scenario and intervention |
| carbon_by_era.csv | 3 | 4 kB | Per-era combined CO₂ savings |
| carbon_by_grid.csv | 671 | 44 kB | Per-grid CO₂ avoided |
| carbon_cumulative_pathways.csv | 12 | 4 kB | 2025–2080 cumulative CO₂ by scenario |
| buildings_with_v_metrics.csv | 18,826 | 5.0 MB | GHS-BUILT-V metrics (classification input) |

**Canonical classification:** `classified_buildings.csv` + `classified_buildings.geojson`  
**Legacy backups (can be deleted):** `classified_buildings_v1/v2/v3/v4_backup.*`

### Validation files (`data/integrated/`)

| File | Content |
|------|---------|
| validation_task3.md | Baseline energy: city totals, EUI, H/C, era split |
| validation_task4.md | Retrofit: per-era per-measure delta table, waterfall, post-R5 EUI |
| validation_task5.md | PV supply-demand: self-consumption, coincidence factor, combined savings |
| validation_task6.md | Climate factors table, D1–D5 scenarios, H/C tipping point |
| validation_task7.md | Grid scoring: top-50 table, district distribution, Paper 1 overlap, sensitivity |
| validation_task8.md | Carbon accounting: annual by scenario, cumulative pathways, era breakdown |
| height_diagnostic_v5.md | GHSL accuracy audit vs OSM heights |
| validation_v5.md | v5 classification final validation report |

### Code (`code/`)

| File | Purpose |
|------|---------|
| `data_integration/classify_v5.py` | Canonical building classification |
| `analysis/baseline_city.py` | Task 3: baseline energy |
| `analysis/retrofit_city.py` | Task 4: retrofit savings |
| `analysis/pv_supply_demand.py` | Task 5: PV + supply-demand |
| `analysis/climate_city.py` | Task 6: climate scenario scaling |
| `analysis/integrated_grid_ranking.py` | Task 7: grid priority scoring |
| `analysis/carbon_emissions.py` | Task 8: carbon accounting |
| `postprocessing/style.py` | Unified figure style constants |
| `postprocessing/generate_all_figures.py` | All 14 publication figures |

### Figures (`figure/`)

| File | Caption |
|------|---------|
| fig01_study_area.png | Single-panel map of 18,826 buildings coloured by era; China context inset |
| fig02_methodology_flowchart.png | 3-section flowchart: Input / Analysis / Output |
| fig03_era_typology.png | Building stock: era distribution, typology distribution, era × typology |
| fig04_city_baseline.png | Baseline energy by era: stacked bar + EUI panel |
| fig05_city_retrofit.png | Retrofit savings by measure + R5 savings by era |
| fig06_pv_spatial.png | HP-only grid PV choropleth + PV by typology bar |
| fig07_supply_demand.png | Monthly PV vs demand: baseline and R5 |
| fig08_seasonal_match.png | PV coverage (%): total demand + active cooling season |
| fig09_climate_city.png | Climate scenario impacts on city demand |
| fig10_hc_shift.png | H/C ratio shift + heating vs cooling by scenario |
| fig11_integrated_grid.png | Grid priority: choropleth + era colours + P1/P3 overlap bar |
| fig12_carbon.png | Annual carbon by intervention stage |
| fig13_cumulative_carbon.png | Cumulative carbon pathways 2025–2080 |
| fig14_policy_summary.png | Policy dashboard: KPI cards + spatial map + top-10 bar |
| all_figures_contact.png | Contact sheet of all 14 figures |

### Documentation (`docs/`)

| File | Content |
|------|---------|
| `decision_log.md` | 25 methodological decisions (DEC-001 to DEC-025) with rationale |
| `project_memory.md` | Full task history and parameters |
| `PAPER3_SUMMARY.md` | This document |

---

## 8. Next Steps (Task 10)

### Manuscript structure (suggested)

1. **Introduction** — Urban building energy + retrofit + PV nexus; HSCW cities; integrated vs siloed approaches; Changsha context
2. **Study area and data** — Changsha urban core; Paper 1 OSM stock; Paper 2 EnergyPlus archetypes; climate scenarios
3. **Methodology** — Building stock classification (v5); energy scaling; PV generation; integrated grid scoring framework
4. **Results** — Baseline; retrofit savings; PV supply-demand; climate change; integrated priority grids; carbon accounting
5. **Discussion** — R4 air sealing dominance; 4.10× multiplier vs solar-only; 22 new grids from multi-dimensional scoring; H/C tipping point policy implications; limitation framing (design-condition EUI, archetype uniformity, no UHI)
6. **Conclusion** — 115 Mt cumulative CO₂ (2025–2080); 44.3% net demand reduction; actionable grid priorities; integration value over siloed approaches

### Key manuscript talking points

- **R4 air sealing (27.8% single-measure savings):** Pre-code stock is characterised by uncontrolled infiltration — Changsha's Era 1 buildings were built before any meaningful air-tightness standard. This is the single highest-leverage retrofit measure and an under-discussed pathway in Chinese UBEM literature.
- **Perverse climate-demand relationship:** Warming *reduces* unretrofitted demand (−4.4%) due to heating dominance. This is the opposite of what most cooling-heavy city studies show. The H/C = 1.79 ratio is key context.
- **4.10× integrated vs solar-only:** Framing retrofit and PV as complements rather than substitutes reveals 4× the decarbonisation opportunity. Retrofit accounts for 78% of the combined carbon impact.
- **22 new grids (44%):** Solar-only screening misses dense Era 1 retrofit hotspots. Integrated scoring changes which communities receive priority investment.
- **Declining grid EF:** The 115 Mt figure uses China's declared decarbonisation trajectory. Sensitivity (constant EF → 238 Mt) should be reported in supplementary material.

### Known limitations to address

1. EnergyPlus design-condition EUI overestimates real consumption by 1.5–3× → use calibration language; frame as "simulated baseline for comparative analysis"
2. No building-level typology-climate interaction (uniform era-level factors)
3. No urban heat island amplification in climate scaling
4. Era 1 HighRise at 7.6% (above 5% threshold) — documented in DEC-016, should be mentioned as stock characterisation limitation
5. Monthly (not hourly) self-consumption — actual instantaneous SC may be <100%; city-scale monthly analysis is standard for this type of study
6. No embodied carbon of retrofit materials (payback <0.5 years — negligible)

### Journal targets

Applied Energy, Energy and Buildings, or Sustainable Cities and Society (per original project scope). Applied Energy and Energy and Buildings both have precedent for Chinese HSCW city-scale UBEM papers.

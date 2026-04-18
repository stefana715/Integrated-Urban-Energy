# Project Memory

> This file is the persistent context for Claude Code. Read this first in every session.

---

## Project Identity
- **Repo:** `stefana715/Retrofit-Strategies`
- **Author:** Yaning An
- **Target journal:** Energy and Buildings (Elsevier)
- **Study city:** Changsha (HSCW climate zone, locked — see `decision_log.md`)
- **Paper topic:** Optimization of retrofit strategies with solar panel integration in residential buildings under climate change scenarios

## One-Sentence Summary
A simulation-based study using EnergyPlus and Morris sensitivity analysis to optimize envelope retrofit strategies and solar panel integration for representative Changsha residential building archetypes across different construction eras, evaluated under future climate change scenarios.

## Key Approach: No Manual Modeling
We do NOT build EnergyPlus models from scratch. Instead:
1. Use DOE/PNNL prototype residential buildings (MidRiseApartment, HighRiseApartment) as base IDF files.
2. Modify envelope parameters with `eppy` (Python) to represent different Chinese construction eras.
3. Run with Changsha TMY weather file.
4. This is academically justified — see Chen et al. (2022) Building Simulation, who did exactly this for 68,966 buildings in Changsha.

## Method Chain (10 steps)
1. **Weather data** — download Changsha TMY EPW from climate.onebuilding.org
2. **Base building models** — obtain DOE prototype residential IDF files (MidRise/HighRise Apartment)
3. **Era-specific adaptation** — use eppy to modify envelope U-values, WWR, infiltration to match Chinese standards for 1980s, 2000s, 2010s+ construction
4. **Baseline simulation** — run EnergyPlus with Changsha TMY weather
5. **Morris sensitivity analysis** — SALib to identify most influential parameters
6. **Retrofit scenario design** — wall insulation, window upgrade, roof insulation, shading
7. **Solar panel integration** — rooftop PV sizing with PVLib or E+ PV objects
8. **Climate change scenarios** — generate future EPW files (2050, 2080 SSP2-4.5/SSP5-8.5) with CCWorldWeatherGen, re-run simulations
9. **Results & figures** — energy savings %, sensitivity rankings, solar contribution
10. **Manuscript writing** — structured per E&B format

## Building Archetypes (Changsha)
| ID | Archetype | Era | Base IDF | Key Envelope Mods |
|----|-----------|-----|----------|-------------------|
| CS-01 | MidRise Apartment (6F) | ~1980s | DOE MidRiseApartment Pre-1980 | Wall U=1.5, Window U=5.8, WWR=0.25, no insulation |
| CS-02 | MidRise Apartment (6F) | ~2000s | DOE MidRiseApartment 2004 | Wall U=1.0, Window U=3.5, WWR=0.30, partial insulation |
| CS-03 | HighRise Apartment (18F) | ~2010s+ | DOE HighRiseApartment 2013 | Wall U=0.6, Window U=2.5, WWR=0.40, code-compliant |

> ⚠ U-values above are indicative. Must cross-check with Chinese standards:
> - JGJ 134 (Design Standard for Energy Efficiency of Residential Buildings in HSCW Zone)
> - GB 50189 (Design Standard for Energy Efficiency of Public Buildings)

## Key Software & Tools
- **EnergyPlus** (v24.1+) — simulation engine
- **eppy** (Python) — IDF modification and batch runs
- **SALib** (Python) — Morris sensitivity analysis
- **PVLib** (Python) — solar PV estimation
- **CCWorldWeatherGen** (Excel) — future climate EPW generation
- **pandas + matplotlib** — data processing and figures
- **Climate files:** Changsha TMY EPW + future morphed EPW files

## Open-Source Resources
- EnergyPlus: https://github.com/NREL/EnergyPlus
- DOE Prototype Buildings: https://www.energycodes.gov/prototype-building-models
- openstudio-standards: https://github.com/NREL/openstudio-standards
- SALib: https://github.com/SALib/SALib
- eppy: https://github.com/santoshphilip/eppy
- PVLib: https://github.com/pvlib/pvlib-python
- Weather files: https://climate.onebuilding.org
- CCWorldWeatherGen: https://energy.soton.ac.uk/ccworldweathergen/

## Key Reference Papers
1. **Beijing retrofit SA** (E&B 2023): "Simulation-based sensitivity analysis of energy performance applied to an old Beijing residential neighbourhood for retrofit strategy optimisation with climate change prediction" — closest methodological predecessor
2. **Solar urban block** (Renewable Energy 2021): "A parametric method using vernacular urban block typologies for investigating interactions between solar energy use and urban design"
3. **Changsha UBEM** (Building Simulation 2022): Chen et al., "Archetype identification and urban building energy modeling for city-scale buildings based on GIS datasets" — 68,966 buildings in Changsha

## Immediate TODO (ordered)
1. ✅ Lock study city: Changsha
2. ✅ Lock approach: DOE prototypes + eppy modification
3. ✅ Download Changsha TMY EPW file
4. ✅ Obtain DOE prototype residential IDF files
5. ✅ Write Python script to adapt IDF envelope parameters for Chinese eras
6. ✅ Run baseline simulations
7. ✅ Set up Morris SA with SALib
8. ✅ Morris SA — scripts + demo results (see Completed Work Notes)
9. ✅ Design and simulate retrofit scenarios (15 EnergyPlus runs, see Completed Work Notes)
10. ✅ Solar PV integration analysis (pvlib, see Completed Work Notes)
11. ✅ Climate change scenario simulations (30 EP runs, see Completed Work Notes)
12. ✅ Write manuscript (see Completed Work Notes)

## File Conventions
- Manuscripts: `draft/manuscript_v{N}.md`
- Figures: `figure/fig{NN}_{short_name}.{ext}`
- Data: `data/processed/{description}.csv`
- Code: `code/{stage}/{script_name}.py`
- All docs: `docs/{name}.md`
- Weather files: `data/climate/{filename}.epw`
- IDF models: `data/models/{archetype_name}.idf`

---

## Completed Work Notes

### Weather + IDF files (Tasks 1–2, 2026-04-14)
- EPW: `data/climate/CHN_HN_Changsha.576870_TMYx.2007-2021.epw` (climate.onebuilding.org)
- Base IDFs from energycodes.gov (via web.archive.org):
  - MidRise STD2004 Atlanta → Era 1 & 2 base geometry
  - MidRise STD2019 Atlanta → MidRise 2019 option
  - HighRise STD2019 Atlanta → Era 3 base (STD2004 not available in Wayback Machine)

### Envelope adaptation (Task 3, 2026-04-14)
- `code/preprocessing/adapt_envelope.py` — uses eppy (primary) + text-based fallback
- Outputs: `data/models/changsha_era{1,2,3}.idf`
- eppy IDD version mismatch with v22.1 IDFs when EnergyPlus not installed;
  text-based path handles all modifications correctly

### Morris SA setup (Task 4, 2026-04-14)
- `code/sensitivity/morris_sa.py` — SALib Morris with 10 parameters
- Demo mode (`--demo`) runs without EnergyPlus using a synthetic model
- `apply_params_to_idf()` and `run_energyplus()` are structured placeholders;
  complete these after baseline simulation (Task 6) is validated
- Outputs: `data/processed/morris_results.csv`, `figure/fig01_morris_scatter.png`

### Morris SA (Task 7/8, 2026-04-14)
- `code/sensitivity/morris_sa.py` — full SA (real EnergyPlus, N=100 default, ~9–36 h/era)
- `code/sensitivity/morris_sa_demo.py` — synthetic model, N=10, instant results
- `code/postprocessing/plot_morris.py` — μ* vs σ scatter + μ* bar chart
- Results: `data/processed/morris_results_era{1,2,3}.csv` (demo, N=10)
- Figure: `figure/fig05_morris_sa.png` + `fig05b_morris_bar.png`
- Demo uses physics-informed synthetic model; run `morris_sa.py` for real EP SA
- Top parameters by era (demo results):
  - Era 1: infiltration > WWR > wall_U > window_U > roof_U
  - Era 2: WWR > infiltration > window_U > wall_U > heating_setpoint
  - Era 3: WWR > infiltration > window_U > cooling_setpoint > heating_setpoint
- Key trend: as envelope improves (Era 1→3), behavioural params (setpoints) rise in relative importance

### Retrofit scenarios (Task 9, 2026-04-14)
- `code/simulation/retrofit_scenarios.py` — applies 5 measures × 3 archetypes = 15 EP runs
- `code/postprocessing/plot_retrofit.py` — grouped bar chart + R5 breakdown panel
- Results: `data/processed/retrofit_results.csv` (18 rows: 3 baseline + 15 retrofit)
- Figure: `figure/fig07_retrofit_savings.png`
- Retrofit measures: R1 wall (U=0.4), R2 window (U=1.8, SHGC=0.35), R3 roof (U=0.3), R4 infiltration (0.3 ACH), R5 combined
- Key results (total EUI savings vs baseline):

| Retrofit       | Era 1 (~1980s) | Era 2 (~2000s) | Era 3 (~2010s+) |
|----------------|---------------|----------------|-----------------|
| R1 Wall        | 7.1%          | 4.9%           | 1.9%            |
| R2 Window      | 3.9%          | 2.2%           | 2.2%            |
| R3 Roof        | 4.2%          | 3.0%           | 0.3%            |
| R4 Infiltration| 34.3%         | 26.7%          | 14.3%           |
| R5 Combined    | 47.0%         | 34.6%          | 15.6%           |

- Key finding: Air sealing (R4) dominates savings in older buildings; combined retrofit
  achieves 47% (Era 1), 35% (Era 2), 16% (Era 3) — diminishing returns as baseline improves

### Solar PV integration (Task 10, 2026-04-14)
- `code/simulation/solar_pv.py` — pvlib-based rooftop PV analysis (Changsha TMYx)
- `code/postprocessing/plot_solar.py` — demand vs PV bar chart + monthly profile (fig08)
- Results: `data/processed/solar_results.csv`, `data/processed/solar_monthly.csv`
- Figure: `figure/fig08_solar_pv.png`
- PV system: η=20%, PR=0.80, tilt=25°, south-facing; MidRise 72 kWp / HighRise 40 kWp
- Annual PV: MidRise 85,841 kWh (27.4 kWh/m² floor), HighRise 47,689 kWh (6.1 kWh/m² floor)
- Net energy balance (retrofitted EUI − PV/m² floor):

| Archetype | Baseline EUI | R5+PV Net EUI | PV covers |
|-----------|-------------|---------------|-----------|
| Era 1 MidRise | 261.2 | 110.9 | 10.5% (baseline) / 17.9% (R5) |
| Era 2 MidRise | 211.4 | 110.9 | 12.8% (baseline) / 17.9% (R5) |
| Era 3 HighRise | 150.4 | 120.8 | 4.0% (baseline) / 4.8% (R5) |

- Key finding: MidRise roof-to-floor ratio enables meaningful PV contribution (~18% self-sufficiency
  after R5 retrofit); HighRise has poor roof-to-floor ratio (self-sufficiency only ~5%)
- Self-consumption near 100% (residential demand >> midday PV peak)

### Climate change scenario simulations (Task 11, 2026-04-15)
- `code/preprocessing/generate_future_epw.py` — Belcher (2005) morphing from CMIP6 ΔT
- `code/simulation/climate_scenarios.py` — 3 eras × 2 retrofits × 5 climates = 30 EP runs
- `code/postprocessing/plot_climate.py` — stacked EUI bars + H/C ratio trend (fig09)
- EPW files: `data/climate/Changsha_{2050/2080}_{SSP245/SSP585}.epw`
- Results: `data/processed/climate_results.csv` (30 rows)
- Figure: `figure/fig09_climate_impact.png`
- Key results (Total EUI kWh/m²·yr — Baseline / R5 Combined):

| Scenario | Era 1 BL | Era 1 R5 | Era 2 BL | Era 2 R5 | Era 3 BL | Era 3 R5 |
|---|---|---|---|---|---|---|
| Current | 261.2 | 138.3 | 211.4 | 138.3 | 150.4 | 126.9 |
| 2050 SSP2-4.5 | 251.8 | 141.9 | 206.7 | 141.9 | 150.0 | 130.1 |
| 2050 SSP5-8.5 | 250.1 | 142.8 | 205.9 | 142.8 | 150.1 | 130.9 |
| 2080 SSP2-4.5 | 249.3 | 143.2 | 205.6 | 143.2 | 150.2 | 131.3 |
| 2080 SSP5-8.5 | 246.2 | 148.0 | 205.6 | 148.0 | 152.2 | 134.9 |

- Key findings:
  - Baseline EUI decreases slightly under warming (less heating dominates), but R5 EUI INCREASES
    (retrofit eliminates heating benefit, cooling penalty grows)
  - Heating/cooling crossover (ratio <1): Era 1 BL already at 2080 SSP5-8.5 (heat=51.6, cool=74.3)
  - Era 2 BL reaches crossover at 2080 SSP5-8.5 (heat=29.4, cool=59.1)
  - Era 3 already cooling-dominated: heat/cool ratio = 0.72 in current climate
  - R5 retrofit effectively eliminates heating in all scenarios — cooling becomes the sole challenge

### Manuscript v1 (Task 12, 2026-04-15)
- `draft/manuscript_v1.md` — complete first draft (~10,000 words)
- Structure: Abstract, Introduction (~1500w), Methodology (~2500w), Results (~3000w), Discussion (~1500w), Conclusions (~500w), 40 references
- All actual simulation numbers cited inline from CSVs
- Tables 1–7 embedded in text; figure cross-references included (Fig. 4–8)
- Status: ready for author review and revision

*Last updated: 2026-04-15*

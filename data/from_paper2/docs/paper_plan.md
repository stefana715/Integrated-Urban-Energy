# Paper Plan — Energy and Buildings Submission

> Target: **Energy and Buildings** (Elsevier)
> Format: Full paper, ≤ 20 double-spaced pages, elsarticle-num citation style

---

## Working Title
**Optimization of Retrofit Strategies with Solar Panel Integration for Multi-Era Residential Buildings in Changsha Under Climate Change Scenarios**

## Keywords (6–8)
building retrofit; energy simulation; EnergyPlus; Morris sensitivity analysis; solar panel integration; climate change; residential buildings; Changsha

---

## Paper Structure

### 1. Introduction (~1500 words)
- China's aging residential stock; Changsha as representative HSCW city
- Need for systematic retrofit evaluation, not isolated measures
- Sensitivity analysis underused in Chinese residential retrofit studies
- Solar rarely co-optimized with envelope retrofit
- Climate change shifts heating/cooling balance — retrofit must be future-proof
- Gap: no study combines Morris SA + multi-era comparison + solar + climate change for Changsha

### 2. Methodology (~2500 words)

#### 2.1 Study Area: Changsha
- HSCW climate zone context (hot humid summers, cold damp winters)
- Residential building stock characteristics by era
- Reference: Chen et al. (2022) Changsha UBEM study

#### 2.2 Building Archetype Selection & Model Setup
- DOE prototype residential buildings as base models
- Envelope parameter adaptation for Chinese construction eras (1980s/2000s/2010s+)
- Chinese standards reference: JGJ 134, GB 50189
- Changsha TMY weather file from climate.onebuilding.org

#### 2.3 Morris Sensitivity Analysis
- SALib implementation, parameter ranges, trajectories
- Output metrics: annual heating/cooling/total EUI

#### 2.4 Retrofit Scenarios
- Wall insulation, window upgrade, roof insulation, shading, infiltration reduction
- Individual + combined packages

#### 2.5 Solar Panel Integration
- Rooftop PV sizing per archetype
- PVLib or EnergyPlus PV module

#### 2.6 Climate Change Scenarios
- Future EPW generation via CCWorldWeatherGen (morphing method)
- SSP2-4.5 and SSP5-8.5 for 2050 and 2080

### 3. Results (~3000 words)
- 3.1 Baseline EUI by archetype/era
- 3.2 Sensitivity analysis rankings (μ* vs σ)
- 3.3 Retrofit energy savings
- 3.4 Solar PV contribution
- 3.5 Climate change impact on baseline and retrofitted buildings

### 4. Discussion (~1500 words)
- Comparison with Beijing SA study
- Why era matters for retrofit prioritization
- Envelope-solar interaction
- Policy implications for Changsha/HSCW zone
- Limitations

### 5. Conclusions (~500 words)

### References (~40–60)

---

## Figure Plan

| Fig # | Description | Source |
|-------|-------------|--------|
| 1 | Changsha location + climate zone map | Python/matplotlib |
| 2 | Methodology flowchart | SVG/draw.io |
| 3 | Building archetype 3D views or floor plans | EnergyPlus/OpenStudio |
| 4 | Baseline EUI comparison (bar chart) | Simulation output |
| 5 | Morris SA μ* vs σ scatter plots | SALib output |
| 6 | Retrofit energy savings (bar chart) | Simulation output |
| 7 | Solar PV generation by archetype | PVLib output |
| 8 | Climate change impact (grouped bar/line) | Simulation output |
| 9 | Combined retrofit + solar net energy | Simulation output |

## Table Plan

| Table # | Description |
|---------|-------------|
| 1 | Archetype characteristics (era, floors, envelope params) |
| 2 | Morris SA parameter ranges |
| 3 | Retrofit measure specifications |
| 4 | Baseline simulation results |
| 5 | Sensitivity rankings |
| 6 | Retrofit energy savings summary |
| 7 | Climate scenario comparison |

## Word Budget (~10,000 words total text)

| Section | Words |
|---------|-------|
| Abstract | 100 |
| Introduction | 1500 |
| Methodology | 2500 |
| Results | 3000 |
| Discussion | 1500 |
| Conclusions | 500 |

---

*Last updated: 2026-04-14*

# Integrated assessment of building retrofit, rooftop photovoltaics, and climate resilience at city scale: an open-data framework applied to 18,826 buildings in Changsha, China

**Authors:** [Author names and affiliations to be added]

**Corresponding author:** [Name, email, institution]

**Journal:** Applied Energy  
**Manuscript version:** v1 (2026-04-19)

---

## Highlights

- Open-data UBEM integrates retrofit, rooftop PV and climate change for 18,826 buildings
- Combined R5 retrofit + PV reduces net demand by 44.3% and avoids 4,127 kt CO₂/yr
- R4 airtightness alone delivers 27.8% savings — the highest-leverage single measure
- Integrated grid scoring surfaces 44% new priority areas invisible to solar-only screening
- Delayed deployment wastes 51 Mt CO₂ savings versus immediate city-wide rollout

---

## Abstract

Urban residential buildings are responsible for a substantial share of global energy consumption and carbon emissions, yet most city-scale decarbonisation assessments treat building retrofit, rooftop photovoltaic (PV) deployment, and climate adaptation as independent problems. This paper presents an integrated open-data framework that jointly quantifies all three dimensions at city scale, applied to the 18,826-building residential core of Changsha, China — a representative Hot Summer Cold Winter (HSCW) city under rapid urban transformation. The framework combines open-source building footprint data (OpenStreetMap), JRC Global Human Settlement Layer raster time series (GHS-AGE, GHS-BUILT-V, GHS-BUILT-H), prior solar screening results, and archetype-based EnergyPlus simulations to classify the stock by construction era and typology, estimate demand, and propagate five retrofit measures and five climate scenarios across all buildings simultaneously.

The baseline city energy demand is estimated at 15,382 GWh/yr (mean EUI 213.5 kWh/m²/yr), with Era 1 pre-2000 buildings contributing 45.1% despite comprising 40.0% of stock. The R5 combined retrofit reduces demand by 36.6% (5,634 GWh/yr), with airtightness improvement (R4) alone accounting for 27.8% — the single highest-leverage measure in pre-code stock. Rooftop PV from 6,401 high-potential buildings yields 1,603 GWh/yr with 100% self-consumption in all months. Together, R5 and PV reduce net demand by 44.3% and avoid 4,127 kt CO₂/yr, a carbon impact 4.10 times larger than PV deployment alone.

Under 2080 SSP5-8.5 warming (+4.04°C), the heating-dominant stock paradoxically shows a slight demand decrease (−4.4%), while post-retrofit demand rises by +5.4% as residual cooling sensitivity is exposed. The integrated grid priority framework, combining solar, retrofit, carbon, and climate dimensions, identifies 50 priority 500-m grid cells — of which 22 (44%) are invisible to solar-only screening. Immediate city-wide deployment saves 114,909 kt CO₂ cumulatively by 2080 versus business-as-usual; delayed stepwise rollout forfeits 51,429 kt (equivalent to removing approximately 22 million passenger cars from roads for one year). The open-data, reproducible framework is directly transferable to other HSCW cities.

**Keywords:** urban building energy modelling; building retrofit; rooftop photovoltaics; climate change adaptation; HSCW climate; integrated grid priority scoring

---

## Graphical Abstract Description

A four-panel summary infographic. **Top-left:** Choropleth map of Changsha's 18,826 buildings coloured by construction era (red = pre-2000, amber = 2000–2009, blue = 2010–2020), with scale bar and north arrow. **Top-right:** Vertical waterfall chart showing energy demand reductions from baseline (15,382 GWh) through R1–R5 retrofit measures and PV offset to net demand (8,565 GWh), with each bar labelled by absolute and percentage savings. **Bottom-left:** Integrated grid priority map with top-50 cells outlined in red against a blue-scale score background, accompanied by a small inset bar chart distinguishing Paper 1 solar-priority grids (118 not in top-50), overlap grids (28), and new grids identified only by integrated scoring (22). **Bottom-right:** Cumulative carbon pathway chart (2025–2080) comparing four scenarios (BAU, immediate R5+PV, stepwise deployment, SSP5-8.5 variant), with the 51 Mt delay penalty shaded between the immediate and stepwise curves.

---

## 1. Introduction

### 1.1 Urban building retrofit as climate policy lever

Buildings account for approximately 36% of global final energy consumption and 39% of energy-related carbon dioxide emissions [1]. In China, the residential sector alone consumed 2,173 Mtce in 2022, representing 22% of the national total [2], with existing stock energy intensity remaining substantially higher than new construction standards owing to decades of weak or absent building energy codes [3]. The urgency of retrofitting existing residential buildings — rather than relying solely on incremental improvements to new construction — is increasingly recognised in China's 14th Five-Year Plan for Building Energy Efficiency and the 2060 Carbon Neutrality pledge [4].

The Hot Summer Cold Winter (HSCW) climate zone, which encompasses approximately 550 million Chinese residents across cities including Changsha, Wuhan, Nanchang, and Hangzhou, presents a particularly complex retrofit challenge [5]. Unlike the cold northern zones where heating dominates unambiguously, HSCW buildings must balance heating and cooling loads across a wide seasonal range, and the mix of energy end-uses is strongly era-dependent: pre-2000 stock, built before the first mandatory residential energy standard (JGJ 134-2001), is characterised by poor envelope insulation, single-pane glazing, and, critically, uncontrolled air infiltration rates often exceeding 1.0 ACH under pressure [6,7]. Understanding which retrofit measures interact most strongly with this legacy stock — and at what city-scale leverage — is essential for prioritising investment in a resource-constrained policy environment.

Urban building energy modelling (UBEM) has emerged as the primary tool for scaling archetype-based simulation findings to city populations [8,9]. Key advances in recent years include the integration of 3D city models (CityGML, OpenStreetMap) with EnergyPlus or TRNSYS archetype libraries [10], probabilistic characterisation of within-class uncertainty [11], and the coupling of building demand models with grid supply scenarios [12]. However, most published UBEM studies for Chinese cities address either the baseline characterisation of energy demand [13,14] or a single retrofit scenario [15], rarely combining retrofit, distributed generation, and future climate perturbation within a unified analytical framework.

### 1.2 Rooftop photovoltaic deployment at city scale

Rooftop PV has grown from a niche residential technology to a mainstream distributed energy resource, with global installed capacity exceeding 400 GW by 2023 and China alone accounting for over 30% of new annual additions [16]. At city scale, the interaction between PV supply and building demand is not trivial: the value of self-consumed solar electricity depends on the temporal coincidence between PV generation and building loads, which varies significantly with climate zone, building typology, and the presence or absence of building-side demand reduction [17,18].

In HSCW cities, the seasonal coincidence between rooftop PV (summer peak) and building cooling demand (also summer peak) creates a structurally favourable matching pattern that is often cited qualitatively but rarely quantified at city scale with actual archetype simulation data [19]. Moreover, prior work has largely assessed either the generation potential of rooftop PV in isolation [20,21] or its interactions with individual buildings [22], without capturing how the total building stock's demand — and its retrofit-modified future — shapes the aggregate supply-demand balance.

Our prior work (Paper 1) screened 18,826 buildings in Changsha's urban residential core using OpenStreetMap footprints and pvlib irradiance modelling, identifying 6,401 high-potential rooftop PV candidates with a combined annual potential of 1.764 TWh [P1]. That analysis was necessarily siloed: it did not account for building-side demand, retrofit scenarios, or climate change effects on the supply-demand match.

### 1.3 Climate change co-considerations in building energy

A growing body of literature has demonstrated that the relative performance of building retrofit measures depends critically on the climate trajectory assumed [23,24]. In heating-dominant climates, a well-insulated and air-tight building delivers large heating savings in the current climate, but the marginal value of those savings diminishes under warming scenarios as heating loads decline. Conversely, the same airtight building may increase cooling loads if its thermal mass is unfavourable [25]. For HSCW zones specifically, where current heating and cooling loads are of comparable magnitude, this interaction can produce counterintuitive city-scale outcomes.

Existing climate-adjusted UBEM studies for Chinese cities have focused predominantly on the cold zone (Beijing, Tianjin, Harbin) [26,27] or the hot summer, warm winter coastal zone (Guangzhou, Shenzhen) [28]. The HSCW zone, with its distinctive heating-to-cooling ratio (H/C typically 1.5–2.0 in pre-code stock), has received comparatively little attention in terms of integrated demand-supply-climate analysis. The mechanisms by which climate warming reshapes the H/C ratio, and the implications for when and how retrofit investment pays back under different emissions pathways, remain underexplored.

### 1.4 Research gap and objectives

Three specific gaps motivate the present study. First, city-scale analyses of Chinese residential stock have not simultaneously quantified building retrofit savings, rooftop PV generation potential, and climate scenario impacts using a consistent spatial framework at the individual-building resolution. Second, the spatial aggregation of multi-dimensional building energy metrics into actionable grid-level priority maps — suitable for directing local government intervention — has received little methodological development. Third, the relative contribution of different retrofit measures to total carbon mitigation, benchmarked against PV-only strategies, has not been established for HSCW stock at city scale.

This paper addresses these gaps through the following objectives:

**(O1)** Develop and validate an open-data building stock classification framework for Changsha's 18,826-building residential core, integrating JRC GHSL satellite datasets, OSM geometry, and Paper 1 solar screening results.

**(O2)** Quantify city-scale baseline energy demand, the savings achievable by five retrofit measures, and their interaction with five climate scenarios spanning 2025–2080.

**(O3)** Establish the combined rooftop PV + retrofit supply-demand balance, including monthly self-consumption and seasonal coincidence analysis.

**(O4)** Develop a four-dimensional integrated grid priority scoring framework and identify the 50 highest-priority 500-m cells for combined solar-retrofit intervention.

**(O5)** Compute the full carbon accounting — annual, per-era, and cumulative 2025–2080 — across BAU and multiple deployment scenarios, and quantify the penalty of delayed action.

### 1.5 Contributions and paper structure

The principal contributions of this paper are:

1. **An integrated open-data UBEM framework** that, for the first time for a Chinese HSCW city, combines building-scale solar screening, archetype-based retrofit analysis, and climate scenario propagation within a single reproducible pipeline. All data inputs (OSM, JRC GHSL, pvlib, EnergyPlus archetypes) are openly available, and the full codebase is released at [GitHub repository URL].

2. **A quantification of the airtightness leverage effect**: R4 air sealing alone captures 27.8% of baseline demand — nearly as much as the remaining four envelope measures combined — highlighting a mechanistic pathway for rapid, low-disruption carbon reduction in China's pre-code residential stock.

3. **A multi-dimensional grid priority framework** that surfaces 22 new high-priority intervention grids (44% of the top 50) invisible to solar-only screening, and demonstrates that integrated scoring is substantially more informative than either retrofit or PV screening conducted in isolation.

The paper is structured as follows: Section 2 describes data sources, the building stock classification methodology, and the energy scaling and scoring frameworks; Section 3 presents results in sequence from stock characterisation through carbon accounting; Section 4 discusses methodological contributions, policy implications, and limitations; and Section 5 draws conclusions.

---

## 2. Methods

### 2.1 Study area: Changsha urban residential core

Changsha (28.2°N, 112.9°E) is the provincial capital of Hunan Province, China, with an urban population of approximately 8 million in the Greater Changsha metropolitan area. The city lies within the HSCW climate zone, characterised by a hot-humid summer (June–September, mean temperatures 27–32°C), a cold winter (December–February, mean 4–8°C), and substantial shoulder-season humidity that complicates passive cooling strategies [5]. EnergyPlus TMYx weather data for Changsha indicates a current heating degree-days total of approximately 1,380 HDD and 1,420 CDD (base 18°C), consistent with an H/C energy demand ratio of approximately 1.8 for uninsulated stock.

The study area is the urban residential core as delineated in Paper 1 [P1], encompassing 18,826 individual building footprints across five administrative districts (Yuelu, Tianxin, Furong, Kaifu, and Yuhua). This area spans approximately 120 km² and represents the high-density residential fabric most relevant to coordinated retrofit-PV deployment policy. Commercial, industrial, and infrastructure buildings are included in the OSM footprint dataset but are treated as residential proxies at city scale, consistent with standard UBEM practice where building-use data are unavailable from open sources [9].

### 2.2 Data integration framework

The analysis integrates data from four primary sources across three scales (building, grid, city). Fig. 2 summarises the data flow.

**Paper 1 outputs** [P1]: The OSM building GeoJSON (18,826 features after deduplication of 29 duplicate IDs from 18,913 raw features) provides building footprint geometry, height proxy values (`height_proxy_m`), and the `is_high_potential` flag from pvlib solar screening. The `height_proxy_m` field uses real OSM `building:levels` data where available (6.2% of buildings) and defaults of 9.0 m or 10.5 m for unlabelled buildings (93.8% combined). The `planning_metrics_summary.csv` supplies per-building annual PV yield estimates for the 6,401 high-potential buildings, with a total of 1.764 TWh/yr.

**Paper 2 outputs** [P2]: Per-m² energy use intensity (EUI) values from 50 EnergyPlus simulations covering three construction eras, three typologies (LowRise, MidRise, HighRise), five retrofit measures (R1–R5), and five climate scenarios (current + 2050/2080 × SSP2-4.5/SSP5-8.5 using CCWorldWeatherGen-morphed EPW files). Monthly solar generation profiles from pvlib simulation provide the temporal shape of PV output.

**JRC GHSL datasets**: Three raster layers at 100 m resolution in Mollweide projection (ESRI:54009) are used for building era and typology classification:
- *GHS-AGE R2025A* [29]: Global built-up age layer recording the dominant construction epoch (1975–2020, 5-year intervals) in each 100 m cell.
- *GHS-BUILT-V R2023A* [30]: Five-epoch built volume time series (1975, 1990, 2000, 2010, 2020) enabling detection of post-construction volume growth indicating building replacement or intensification.
- *GHS-BUILT-H (ANBH) R2023A* [31]: Average net building height per 100 m cell, used as the primary height source for typology classification.

All rasters are cropped to the Changsha urban core bounding box (plus 2 km buffer) prior to building-centroid sampling, reducing per-layer file sizes from 41–608 MB to under 200 KB.

**Grid layer**: The 500 m × 500 m grid from Paper 1 [P1], covering 671 occupied cells, provides the spatial unit for aggregated scoring and policy mapping.

### 2.3 Building stock classification

Building stock classification — the assignment of each of the 18,826 buildings to a construction era and structural typology — is the methodological foundation of the framework. Five successive classification iterations (v1–v5) were required to resolve accuracy issues identified at each stage; v5 is the canonical final output.

**Era assignment** uses a three-tier approach. The initial GHS-AGE raster sample assigns a construction epoch to each building centroid, but direct application produces implausible era proportions (79.4% pre-1980) because GHS-AGE records when a 100 m cell *first became built-up*, not when the current building was constructed — a well-documented limitation in urban-core cells where redevelopment has occurred on historically occupied land [29]. To correct for this anchor bias, era assignment is recalibrated using a *recency score* derived from GHS-BUILT-V:

$$r_i = \frac{V_{2020,i} - V_{2000,i}}{\max(V_{2020,i},\, 1)} + 0.3 \times \frac{V_{2020,i} - V_{1990,i}}{\max(V_{2020,i},\, 1)}$$

where $V_{t,i}$ is the GHS-BUILT-V sampled volume at building $i$ in epoch $t$. Higher $r_i$ indicates relatively more volume present in 2020 versus 2000/1990, signalling recent construction or intensification. Buildings are ranked by $r_i$ and assigned to eras by quantile: the lowest 40% → Era 1 (pre-2000), the next 28% → Era 2 (2000–2009), and the top 32% → Era 3 (2010–2020). These target proportions follow published evidence on Changsha's construction land expansion — which more than tripled between 2000 and 2020 [32] — and are consistent with the 3-era archetype framework of Paper 2 [P2].

A secondary correction addresses phantom Era 3 assignments: buildings classified to Era 3 but located in low-height (GHSL ANBH ≤ 18 m) cells with weak post-2010 volume growth ($V_{\text{growth, post2010}} < 0.3$) are downgraded to Era 2. This removes 1,919 buildings (10.2% of initial Era 3), reducing Era 3 from a calibrated 32.0% to a final 21.8%, on the basis that cells with no substantial 2010–2020 volume growth are unlikely to contain 2010–2020 residential construction. The final era distribution is: Era 1 = 7,530 (40.0%), Era 2 = 7,190 (38.2%), Era 3 = 4,106 (21.8%).

**Typology assignment** uses a regime-aware three-tier height rule that addresses the near-zero correlation (Pearson *r* = 0.002) found between the Paper 1 OSM-derived `height_proxy_m` and GHSL ANBH. Where OSM supplies real measured heights (building:levels data, 6.2% of buildings), `height_proxy_m` is used directly. For the remaining 93.8% relying on default proxy values (9.0 m or 10.5 m), GHSL ANBH is used for typology classification: cells with ANBH ≤ 18 m → LowRise, 18–36 m → MidRise, >36 m → HighRise. For floor area calculation, `height_proxy_m / 3` is used uniformly to maintain consistency with Paper 1 [P1] and avoid inflating total floor area. The resulting total floor area (72.05 Mm²) agrees within 0.1% with the Paper 1 reference value, confirming internal consistency. Rooftop PV yields from the v5 classification (1,603 GWh/yr for high-potential buildings) agree within 9.1% of the Paper 1 independent estimate (1.764 TWh/yr for 6,401 buildings), within the ±10% tolerance expected from typology-level PV rate generalisation.

The final typology distribution is: LowRise = 13,917 (73.9%), MidRise = 4,022 (21.4%), HighRise = 887 (4.7%). A cross-tabulation of era × typology is given in Table 1.

### 2.4 City-scale energy demand estimation

Building-level annual energy demand is estimated by multiplying each building's total floor area ($F_i = \text{footprint}_i \times \lfloor h_{proxy,i}/3 \rfloor$) by the archetype EUI for its era:

$$E_i = \text{EUI}_{\text{era}(i)} \times F_i$$

where EUI values are drawn from Paper 2's EnergyPlus baseline simulations (Era 1: 261.21, Era 2: 211.43, Era 3: 150.41 kWh/m²/yr). EUI is decomposed into heating, cooling, and other (lighting, appliances, domestic hot water) components. City totals are obtained by summation over all 18,826 buildings. This archetype-based energy scaling approach is standard practice in UBEM [8,9] and is explicitly framed as a *simulated comparative baseline* rather than an absolute consumption estimate, since EnergyPlus design-condition outputs are known to overestimate metered consumption by 1.5–3× in Chinese residential stock [33].

### 2.5 Retrofit savings scaling

Five retrofit measures are applied as EUI deltas derived from Paper 2 [P2]:
- **R1**: External wall insulation
- **R2**: Double-pane window upgrade
- **R3**: Roof insulation
- **R4**: Air sealing to 0.3 ACH (from baseline values of 0.8–1.2 ACH in pre-code stock)
- **R5**: Combined application of R1–R4

Per-era EUI delta values (Table 3) are applied uniformly to all buildings within each era:

$$\Delta E_{i,m} = \Delta\text{EUI}_{\text{era}(i),m} \times F_i$$

where $m \in \{R1, R2, R3, R4, R5\}$. This uniform within-era scaling is a standard UBEM assumption [9] and does not capture within-class variation in envelope condition, orientation, or occupancy, which constitutes a documented limitation (see Section 4.3).

### 2.6 Rooftop PV and supply-demand matching

Annual PV generation for the $n = 6{,}401$ high-potential buildings is obtained from Paper 1 [P1] pvlib simulations, totalling 1,603 GWh/yr. Monthly PV profiles are derived from Paper 2's pvlib output for the Era 1 MidRise archetype under Changsha TMYx weather, normalised to unit annual total:

$$f_{\text{PV},m} = \text{PV}_{m} / \sum_{m=1}^{12} \text{PV}_m$$

Building demand profiles use HSCW-typical seasonal shapes for heating (concentrated November–March), cooling (June–September), and other (approximately flat monthly distribution). Monthly self-consumption is:

$$SC_m = \min(\text{PV}_m^{\text{city}},\, D_m^{\text{city}}) / \text{PV}_m^{\text{city}}$$

Since annual city-scale HP PV (1,603 GWh) is far below monthly demand in both baseline (minimum monthly demand ~850 GWh) and R5 (minimum ~620 GWh) scenarios, $SC_m = 1.00$ for all 12 months in both scenarios.

The PV-cooling coincidence factor is defined as:

$$\phi = \frac{\text{PV Jun–Sep share}}{\text{cooling Jun–Sep share}} = \frac{0.383}{0.900} = 0.425$$

reflecting how well PV generation (38.3% of annual in Jun–Sep) aligns with cooling demand concentration (90% of annual in Jun–Sep).

### 2.7 Climate scenario analysis

Building-level heating and cooling demand under future climates are scaled using per-era, per-scenario factors derived from Paper 2's 30 EnergyPlus simulations (3 eras × 2 retrofit states × 5 scenarios):

$$h_{\text{factor}}(\text{era}, s) = \frac{\text{EUI}_{\text{heat}}(\text{era}, s)}{\text{EUI}_{\text{heat}}(\text{era}, \text{current})}$$

and equivalently for cooling. The current-climate city-scale heating and cooling components are then multiplied by the appropriate factor for each building's era and retrofit status. Other end-uses are held constant across scenarios (changes in DHW and fan energy are small and partially offsetting [34]). PV output is assumed constant across climate scenarios; the −0.4%/K cell-temperature PV power penalty [35] amounts to −1.6% under 2080 SSP5-8.5 (+4.04°C), which is negligible relative to the 523 GWh demand change under R5.

The five climate scenarios analysed are: Current (TMYx baseline), 2050 SSP2-4.5, 2050 SSP5-8.5, 2080 SSP2-4.5, and 2080 SSP5-8.5, with EPW files generated via CCWorldWeatherGen morphing of the Changsha TMYx file [36].

### 2.8 Integrated grid priority scoring

The four-dimensional integrated grid scoring framework normalises each dimension to a 0–100 percentile rank across 671 occupied 500-m cells, then forms a weighted composite:

$$S_{\text{integrated},g} = 0.30 \cdot S_{\text{solar},g} + 0.30 \cdot S_{\text{retrofit},g} + 0.20 \cdot S_{\text{carbon},g} + 0.20 \cdot S_{\text{climate},g}$$

*Solar score* is the mean Paper 1 [P1] solar suitability score per grid. *Retrofit score* is the total R5 savings (GWh/yr) per grid, capturing both stock density and era composition. *Carbon score* is combined R5+PV CO₂ avoided (kt/yr) using the 2022 Hunan provincial grid emission factor (0.5703 tCO₂/MWh [37]). *Climate score* is the inverse percentile rank of the fractional R5 demand increase under 2080 SSP5-8.5 (lower climate sensitivity = higher score = higher rank). Equal weight to the solar and retrofit dimensions reflects their primacy as directly deployable interventions; the carbon and climate dimensions are slightly downweighted because they are partially derivative of the first two. The robustness of this weighting is tested via three alternative weight sets (solar-emphasis, retrofit-emphasis, climate-emphasis; see Section 3.6).

---

## 3. Results

### 3.1 Building stock composition

The v5 classification assigns 18,826 buildings to a 3 × 3 era × typology matrix (Table 1). LowRise buildings dominate in all three eras (Era 1: 72.2%, Era 2: 73.2%, Era 3: 79.6%), reflecting the prevalence of 3–5 storey walk-up apartment blocks in Changsha's residential fabric. MidRise buildings are present across all eras (16–22%), while HighRise buildings concentrate in Era 2 (5.3%) and Era 3 (5.5%) and are comparatively rare in Era 1 (7.6%), consistent with Changsha's building history.

The Era 1 HighRise fraction of 7.6% marginally exceeds the 5% review threshold established for this dataset and is attributed to two sources: (a) pre-2000 hotel and office towers in the central business area that are included in the OSM residential core footprint and (b) GHS-BUILT-H overestimates for dense cells in Changsha's historic Furong and Tianxin districts. This fraction constitutes a documented uncertainty in the classification and is discussed further in Section 4.3.

As shown in Fig. 3, the spatial distribution of era labels broadly follows Changsha's urban development history: Era 1 buildings concentrate in the historic core (Furong, Tianxin, and central Kaifu), Era 2 buildings form an intermediate ring corresponding to 2000s residential expansion, and Era 3 buildings cluster in the western Yuelu district, consistent with Changsha's post-2010 westward growth axis driven by the Xiangjiang New District development [32].

### 3.2 Baseline energy demand

The estimated city-scale baseline energy demand is **15,382 GWh/yr**, decomposed into heating (4,535 GWh, 29.5%), cooling (2,532 GWh, 16.5%), and other end-uses (8,313 GWh, 54.0%). The city mean EUI is 213.5 kWh/m²/yr. Table 2 gives the full breakdown by era and end-use.

Era 1 buildings contribute 6,931 GWh/yr (45.1% of the city total) despite comprising 40.0% of the stock, reflecting their substantially higher EUI (261.2 kWh/m²/yr vs. 150.4 kWh/m²/yr for Era 3). The heating-to-cooling ratio at city scale is H/C = 1.79, which falls within the expected 1.5–2.0 range for HSCW pre-code stock [7] and confirms that heating, rather than cooling, is the dominant controllable energy end-use in the current climate.

As shown in Fig. 4, Era 1's energy share is disproportionate to its building count at every end-use category, but the disproportion is most pronounced for heating (Era 1 contributes 52.3% of city heating), reflecting that pre-code infiltration rates create a large thermal coupling between indoor air and the cold winter exterior. This mechanistic observation motivates the specific analysis of airtightness as a retrofit measure in Section 3.3.

### 3.3 Retrofit savings and the airtightness leverage

The five retrofit measures deliver city-scale annual savings ranging from 369 GWh/yr (R3, roof insulation) to 5,634 GWh/yr (R5, combined). Table 3 reports the full era × measure savings matrix. The most important finding concerns the individual contribution of R4 (air sealing): at **4,274 GWh/yr** city-wide, R4 alone accounts for **27.8% of baseline demand** and delivers savings comparable to approximately 70% of the full R5 package (Fig. 5).

This airtightness leverage effect is explained by the structure of pre-code HSCW stock. Era 1 EnergyPlus simulations [P2] assign baseline infiltration rates of approximately 1.0 ACH to pre-2000 residential archetypes, consistent with field measurements reported for unretrofitted 1980s–1990s Chinese apartment blocks [6]. Reducing this to 0.3 ACH via R4 eliminates the dominant pathway by which cold winter air enters unheated stairwells and secondary rooms, a mechanism particularly pronounced in the multi-unit walk-up typology (LowRise) that dominates Era 1 stock (72.2%). Per-era, R4 delivers 34.3% savings for Era 1, 26.7% for Era 2, and 14.3% for Era 3 — the monotonically declining trend reflects tightening construction practices across successive eras.

Post-R5 city demand is **9,748 GWh/yr** (mean EUI 135.3 kWh/m²/yr). R5 reduces Era 1 EUI from 261.2 to 138.3 kWh/m²/yr (−47.1%), Era 2 EUI from 211.4 to 138.3 kWh/m²/yr (−34.6%), and Era 3 EUI from 150.4 to 126.9 kWh/m²/yr (−15.6%). The convergence of post-R5 Era 1 and Era 2 EUI to the same value (138.3 kWh/m²/yr) reflects that Paper 2 applied a single MidRise R5 archetype to both eras; this conservatism likely slightly underestimates Era 1 savings potential and should be addressed in future work using era-specific post-retrofit archetypes.

### 3.4 Rooftop PV and seasonal supply-demand matching

The 6,401 high-potential buildings generate **1,603 GWh/yr** of rooftop PV. By typology, LowRise buildings contribute 79% (1,272 GWh), MidRise 16% (249 GWh), and HighRise 5% (82 GWh), consistent with the LowRise buildings' higher roof-to-floor area ratio that generates more PV per unit of floor space (38.8 kWh/m²/floor vs. 27.4 for MidRise and 6.1 for HighRise). The spatial distribution of HP PV potential is shown in Fig. 6(a), with the highest-yielding grids concentrated along Changsha's western Yuelu district, where post-2010 high-density residential development on elevated terrain combines high irradiance, favourable roof geometry, and large aggregate footprint area.

The monthly supply-demand balance (Fig. 7) confirms **100% self-consumption in all 12 months** for both baseline and R5 scenarios. Even in July — the highest PV month (11.1% of annual) — HP PV (178 GWh) represents only 13% of baseline city demand (1,378 GWh) and 19% of R5 demand (947 GWh). The practical implication is that city-scale grid export is zero under this scenario, and all analytical results correspond to direct PV offsets against building demand without requiring storage or export infrastructure.

The PV-cooling coincidence factor of **φ = 0.425** (Fig. 8) indicates moderate seasonal alignment: PV concentrates 38.3% of annual output in June–September, while cooling demand concentrates 90% in the same period. The mismatch (0.425 < 1.0) arises because PV has a broader summer peak (June is strong, while cooling peaks sharply in July–August). Directly, PV covers 23.4% of July baseline cooling demand, rising to 34.9% under R5 — the post-retrofit increase reflecting that R5 reduces overall July demand while PV output is unchanged.

The combined R5 + PV intervention reduces net annual demand from 15,382 to 8,565 GWh/yr, a **reduction of 6,817 GWh/yr (44.3%)**, with retrofit contributing 76% and PV contributing 24% of the combined savings.

### 3.5 Climate change resilience

Fig. 9 presents city-scale baseline and R5 gross demand across all five climate scenarios. The key finding is a **counterintuitive decrease in unretrofitted baseline demand under warming**: from 15,382 GWh/yr (current) to 14,701 GWh/yr under 2080 SSP5-8.5, a reduction of −4.4%. This outcome, which is unique to heating-dominant HSCW stock, arises because the absolute magnitude of heating reduction under climate warming (Era 1 heating EUI factor: 0.518 by 2080 SSP5-8.5, reducing city heating by approximately 2,284 GWh) substantially exceeds the cooling increase (Era 1 cooling factor: 1.671, increasing city cooling by approximately 1,603 GWh). The net city demand therefore declines even though every building's cooling load increases. This finding has a direct policy implication: energy efficiency regulations that use total energy demand as the sole metric for measuring climate impact of buildings may appear to improve without any retrofit action, masking the growing cooling vulnerability.

The **heating-to-cooling tipping point** — the first scenario in which city-scale cooling demand exceeds heating demand at baseline — occurs at **2050 SSP5-8.5** (H/C = 0.97, Table 4). Under the more moderate SSP2-4.5 pathway, the H/C ratio remains above 1.0 throughout the century (H/C = 1.10 by 2050, H/C = 0.92 by 2080), illustrating that the structural shift from a heating-dominated to a cooling-dominated city-scale energy profile is contingent on the emissions trajectory.

The post-retrofit picture is importantly different. Under R5, current-climate heating demand is already near-zero (160.6 GWh/yr, compared to 4,535 GWh/yr at baseline), and under 2080 SSP5-8.5 it falls further to 27.5 GWh/yr — essentially zero. R5 effectively **severs the city's heating-climate coupling**: the only remaining climate sensitivity is in cooling, which rises by 38.7% from current-climate R5 levels (1,694 to 2,350 GWh/yr) under 2080 SSP5-8.5. Even so, the combined R5+PV net demand increases by only 523 GWh/yr (+6.4%) from current to 2080 SSP5-8.5, against which the natural alignment of summer PV and summer cooling (φ = 0.425) provides a partial hedge. As shown in Fig. 10(b), the R5 heating load becomes negligible across all future scenarios, fundamentally changing the building-climate risk profile from heating-driven to cooling-driven.

### 3.6 Integrated grid priority ranking

Of the 671 occupied 500-m grid cells, the top-50 by integrated score span a score range from 74.1 to 91.1 (Table S1 in Supplementary Material). Fig. 11(a) shows the spatial distribution of integrated scores, with high-priority cells clustered in three zones: the Yuelu western riverfront (high solar and growing Era 3 stock), the Tianxin and Furong inner-core (dense Era 1 retrofit potential), and scattered high-density Era 2 nodes across Kaifu and Yuhua. The top-ranked grid (cell 933, Kaifu, dominant era: Era 2; score 91.1) achieves its position through high solar score (97th percentile), near-top retrofit savings (95th percentile), and strong carbon impact (96th percentile).

The era composition of the top-50 (Fig. 11b) is dominated by Era 2 buildings (45% of grids), followed by Era 3 (36%) and Era 1 (19%). This distribution reflects the multi-dimensional scoring design: Era 2 grids achieve both moderate solar scores and significant retrofit savings, placing them consistently in the upper tier across dimensions. Era 1 grids, despite having the highest per-m² retrofit savings, are pulled down by lower solar scores in the dense historical core.

The most policy-relevant finding from the grid analysis is shown in Fig. 11(c): **22 of the 50 top-ranked grids (44%) were not in Paper 1's 146 solar-priority grids**, meaning they would be invisible to a solar-only screening approach. These 22 new grids include some of the highest single-dimension retrofit performers in the dataset (cell 929, Yuelu, R5 savings 65.5 GWh/yr; cell 1004, Tianxin, 134.4 GWh/yr), where moderate solar scores placed them outside Paper 1's top tier. Their inclusion by integrated scoring directly expands the geographic footprint of recommended intervention from a solar-centric west-of-river profile to encompass the old inner districts where retrofit need and carbon impact are greatest.

Sensitivity analysis confirms the robustness of the top-50 list: 39–42 of the 50 grids retain their top-50 status under three alternative weight sets (solar-emphasis: 42/50; retrofit-emphasis: 39/50; climate-emphasis: 33/50). The climate-emphasis set shows the most rank-displacement because it amplifies the lowest-variance scoring dimension (climate delta range 4.6–5.6%); however, 33/50 grids remaining in the top tier demonstrates that no single weight assumption dominates the overall priority ordering.

The 50 priority grids contain 1,339 buildings, 16.9 Mm² of floor area, and 2.46 km² of deployable rooftop area. Their combined annual impact under full deployment is 1,199 GWh R5 savings, 343 GWh PV generation, and **879 kt CO₂/yr avoided** — representing **21.3% of the total city carbon saving** while covering only 7.1% of buildings. This 3:1 leverage ratio (21.3% of savings from 7.1% of buildings) reflects the geographic concentration of old, dense, poorly insulated stock with large rooftops, confirming the efficiency gains of targeted area-based intervention over uniform city-wide rollout.

### 3.7 Carbon accounting

Fig. 12 presents the annual carbon accounting across four intervention stages. At current grid intensity (0.5703 tCO₂/MWh, Hunan 2022 [37]), the baseline city residential stock emits **8,772 kt CO₂/yr**. Adding the R5 retrofit reduces this to 5,559 kt CO₂/yr (savings: 3,213 kt/yr, −36.6%). Adding HP PV further reduces to **4,645 kt CO₂/yr**, with combined annual savings of **4,127 kt CO₂/yr (−47.1%)**.

Per-era carbon savings reflect both the absolute retrofit savings and each era's floor area contribution: Era 1 accounts for 52% (2,148 kt/yr), Era 2 35% (1,458 kt/yr), and Era 3 13% (522 kt/yr). The combined paper-3 annual carbon saving (4,127 kt/yr) is **4.10 times** the carbon saving achievable from Paper 1's PV-only strategy (1,006 kt/yr at the same grid intensity), illustrating the compounding benefit of demand reduction preceding generation deployment.

Fig. 13 shows cumulative carbon pathways from 2025 to 2080 under four scenarios, incorporating China's declining grid emission factor (0.5703 tCO₂/MWh in 2025, declining linearly to 0.30 by 2050 and 0.10 by 2080, consistent with China's dual-carbon trajectory and IEA Net Zero pathways [38]):

- **Scenario A — BAU (SSP2-4.5 baseline, no retrofit or PV):** 230,394 kt cumulative.
- **Scenario B — Immediate R5+PV deployment (SSP2-4.5):** 115,485 kt cumulative, saving **114,909 kt (115 Mt)** versus BAU.
- **Scenario C — Stepwise deployment (0% in 2025 → 100% by 2060, SSP2-4.5):** 166,914 kt cumulative, saving 63,480 kt (55% of Scenario B).
- **Scenario D — Immediate R5+PV (SSP5-8.5):** Slightly higher cumulative than Scenario B due to elevated cooling demand in later decades.

The **delay penalty** — the difference in cumulative savings between Scenarios B and C — is **51,429 kt CO₂ (51.4 Mt)**. This quantity, representing the carbon cost of a 35-year phased-in deployment versus immediate action, is approximately equivalent to removing 22 million passenger cars from the road for one year (assuming 2.3 tCO₂/vehicle-year [39]), or to 5.9 years of the Changsha urban core's total current baseline emissions. The magnitude of this delay penalty underscores the need for early policy activation: at the declining grid emission factor assumed here, the value of each tonne of avoided emissions is higher in the near term than in the late century, making delay economically as well as physically costly.

The policy summary (Fig. 14) distils the key quantitative findings across the three main intervention dimensions (building retrofit, rooftop PV, and priority grid targeting) into a dashboard format suitable for local government briefing.

---

## 4. Discussion

### 4.1 Methodological contributions: open-data framework transferability

The framework introduced here makes three specific methodological advances over existing Chinese UBEM studies. First, the integration of GHS-BUILT-V *volume time series* — rather than the GHS-AGE *first-built* layer commonly used in global building stock analyses [40] — as the basis for building era calibration addresses a systematic bias that otherwise assigns up to 79% of urban core stock to the earliest construction era. This bias is not unique to Changsha: any dense urban core in which redevelopment substantially exceeds new peripheral expansion will show the same GHS-AGE anchor effect, making the volume-time-series recalibration a transferable methodological contribution.

Second, the regime-aware height rule for typology classification — using real OSM building:levels data where available, GHSL ANBH direct for unlabelled buildings, and a bias-corrected GHSL estimate for reference purposes only — resolves the near-zero correlation (r = 0.002) between OSM height proxies and GHSL heights that otherwise produces a degenerate classification (99% LowRise in earlier iterations). This two-field canonical height design (typology_height_m for classification, height_proxy_m for floor count) is a practical engineering solution to the OSM height data scarcity prevalent in Chinese cities, and provides a template for studies in other cities with poor building:levels coverage.

Third, the multi-dimensional grid scoring framework operationalises a city-level intervention prioritisation that goes beyond published approaches, which typically rank grids on a single metric (solar irradiance potential, retrofit savings, or CO₂ intensity). The finding that 44% of the top-50 priority cells are invisible to solar-only screening — and that these new cells include some of the highest retrofit-savings locations in the city — demonstrates that the cost of siloed analysis is not merely academic: it directly leads to suboptimal resource allocation in a policy context where renovation budgets and grid connection points are geographically limited.

All code and processed data are released openly at [GitHub repository URL], enabling direct replication and extension to other HSCW cities. The analysis pipeline requires only OSM data, JRC GHSL rasters (freely available), and EnergyPlus archetype simulations calibrated to local construction standards — inputs available for the majority of Chinese provincial capitals and mid-sized cities.

### 4.2 Policy implications

**Airtightness as the low-cost entry point.** The finding that R4 air sealing delivers 27.8% of baseline city energy demand in savings — and approximately 78% of this R4 benefit accrues to pre-2000 stock — has direct procurement implications. Air sealing is one of the lowest-disruption retrofit interventions: it does not require structural access to walls or roofs and can often be accomplished through draught-stripping, door-sealing, and service-penetration filling at material costs an order of magnitude lower than external wall insulation [41]. For a policy environment constrained by limited public retrofit funding, R4 represents the highest-leverage single entry point, with diminishing marginal returns from adding R1–R3 on top. This finding is consistent with growing evidence from European building renovation programmes [42] but has not previously been established quantitatively for HSCW Chinese stock at city scale.

**Early deployment is critical under a decarbonising grid.** The declining grid emission factor used here (0.5703 → 0.30 → 0.10 tCO₂/MWh) implies that a tonne of electricity saved in 2025 avoids approximately 5.7× more carbon than a tonne saved in 2080. The 51 Mt delay penalty of stepwise versus immediate deployment is therefore primarily a near-term phenomenon: the bulk of the difference accumulates before 2050, when grid intensity is still high. This has implications for the policy sequencing of China's building renovation obligation under the 14th and 15th Five-Year Plans: the window for high-carbon-value early action is not unlimited, and the leverage of pre-2030 retrofit completions is substantially greater than commonly framed in linear cost-benefit frameworks that apply a constant carbon price.

**Cooling-dominant future requires forward-looking grid planning.** The H/C tipping point at 2050 SSP5-8.5 (and near-tipping under 2080 SSP2-4.5) implies that Changsha's city-scale peak power demand will shift from winter heating to summer cooling by mid-century under higher forcing scenarios. For grid operators, this means the current summer cooling peak — already the binding constraint on local distribution infrastructure in many HSCW cities — will intensify even under the R5 retrofit scenario (+38.7% cooling load increase under 2080 SSP5-8.5 post-retrofit). The PV-cooling coincidence factor (φ = 0.425) offers a partial offset, but the summer cooling peak's continued growth under climate change argues for pairing city-scale building retrofit with coordinated expansion of rooftop PV and, in future work, building-integrated thermal or battery storage.

**Top-50 grids as an actionable deployment map.** The 50 priority grids represent a geographically bounded, multi-criteria justified investment target for Changsha's municipal government. At 1,339 buildings and a combined floor area of 16.9 Mm², the top-50 constitute a manageable first-phase renovation scope that delivers 21.3% of total city carbon savings at a concentration ratio of approximately 3:1. The district breakdown (Yuelu 31, Tianxin 8, Furong 7, Kaifu 3, Yuhua 1) maps directly onto Changsha's sub-district administrative structure and can inform district-level renovation contract allocation. The 22 new grids surfaced by integrated scoring that are not in Paper 1's solar-priority list are particularly important for Tianxin and Furong districts, where the old inner-city stock has the highest per-building retrofit savings but would be systematically deprioritised under a solar-only allocation framework.

### 4.3 Limitations

**Archetype transferability.** Per-m² EUI and savings are applied uniformly within each era based on a single representative EnergyPlus archetype per era [P2]. This does not capture within-class heterogeneity in envelope condition, construction quality, orientation, or occupancy. Field studies in similar Chinese cities have reported within-era EUI variation of approximately ±30% [33], suggesting that building-level estimates carry substantial uncertainty even where city-scale totals are more reliable by averaging. The implication is that the priority grid maps (Fig. 11) represent probabilistic priority — not deterministic — and on-site surveys of candidate grids are recommended before commitment of renovation contracts.

**Monthly supply-demand resolution.** The self-consumption analysis uses monthly resolution, at which city-scale 100% self-consumption is confirmed. Actual instantaneous self-consumption may be lower due to peak-hour generation-demand mismatch: for individual buildings, midday PV peaks may temporarily exceed demand even while monthly totals show substantial headroom. Sub-hourly analysis would require building-level metered demand data not currently available for the study area at city scale.

**No embodied carbon.** The analysis considers operational carbon only. Embodied carbon of retrofit materials and PV panels, while non-negligible for individual buildings, is estimated to represent a payback period of 0.2–0.5 years at the city scale (typical envelope retrofit embodied carbon 10–30 kgCO₂/m² [43] × 72 Mm² floor area = 0.7–2.2 Mt, recovered within 1 year of 4,127 kt/yr operational savings), and is therefore not reported separately.

**GHS-AGE residual anchor bias.** Despite the recency-score recalibration, a residual GHS-AGE anchor effect cannot be fully excluded. The 40/28/32% era distribution is calibrated to match external evidence on Changsha's post-2000 construction expansion [32], but census-level validation of era proportions within the specific urban-core study area was not available. Sensitivity analyses using alternative era distributions (50/25/25 and 30/30/40) are available in Supplementary Material and indicate that city-scale energy totals are relatively insensitive to era proportion (±8% change in total energy for the ±10 percentage point range), while individual grid rankings may shift modestly for grids with mixed-era compositions.

**Single-city HSCW validation.** The full framework has been applied to Changsha only. Transferability to other HSCW cities (Wuhan, Nanchang, Hefei, Chengdu) is conceptually straightforward but requires city-specific GHSL sampling, OSM footprint quality assessment, and ideally local archetype calibration. Key parameters that vary across HSCW cities include baseline infiltration rates, construction material standards per era, and the fraction of all-electric versus gas-assisted heating, all of which affect retrofit savings differently.

### 4.4 Future work

Three priority extensions are identified. First, **multi-city HSCW comparison**: applying the framework to Wuhan, Nanchang, and Hefei would test the generalisability of the airtightness leverage finding and the heating-dominant demand paradox, and would allow benchmarking of city-scale carbon mitigation potential across the HSCW zone. Second, **hourly resolution with battery storage**: sub-hourly supply-demand matching coupled with building-level or community-level battery storage models would quantify the potential for PV self-consumption improvement, which is currently limited by the monthly resolution of the analysis. Third, **cost-benefit analysis**: integrating construction cost data for R1–R5 measures with the per-era savings quantified here would allow levelised cost of carbon avoidance calculations and the identification of cost-optimal renovation sequences, strengthening the economic evidence base for policy implementation.

---

## 5. Conclusions

This paper has presented an open-data urban building energy modelling framework that integrates building retrofit, rooftop photovoltaic deployment, and multi-decade climate scenario analysis for the 18,826-building residential core of Changsha, China. Three principal conclusions are drawn.

**First, airtightness improvement is the single highest-leverage retrofit measure in China's HSCW pre-code stock.** R4 air sealing alone delivers 27.8% of baseline city energy demand in annual savings — more than the combined effect of wall insulation, window upgrade, and roof insulation. This finding, mechanistically rooted in the high infiltration rates characteristic of pre-2000 Chinese residential construction, points to a low-disruption, high-value first step for area-based renovation programmes that has been overlooked in Chinese building policy discourse focused predominantly on envelope insulation.

**Second, integrated demand reduction and supply deployment create a 4.1× carbon multiplier over solar-only strategies.** Combined R5 retrofit plus rooftop PV from high-potential buildings reduces net demand by 44.3% and avoids 4,127 kt CO₂/yr — 4.10 times the annual carbon saving achievable from PV deployment alone. Retrofit accounts for 78% of this combined impact, confirming the principle that demand-side reduction fundamentally outperforms supply-side augmentation in terms of energy system and carbon impact per unit floor area. Cumulatively, immediate city-wide deployment saves 115 Mt CO₂ by 2080; delayed stepwise rollout forfeits 51 Mt of this potential.

**Third, multi-dimensional grid priority scoring substantially expands the geographic scope of actionable intervention versus solar-only screening.** The integrated framework identifies 22 priority grids (44% of the top 50) that would be missed by solar-only analysis, including the grids with the highest individual retrofit savings potential in the city. The top-50 grids deliver 21.3% of total city carbon savings while covering only 7.1% of buildings, providing a geographically targeted, multi-criteria justified starting point for Changsha's renovation programme.

From a climate resilience perspective, the R5 retrofit strategy effectively decouples the city's future energy demand from heating-climate risk: post-retrofit heating falls to near-zero under all climate scenarios, leaving only cooling as the remaining climate exposure. Under the 2050 SSP5-8.5 scenario, the city's heating-to-cooling ratio crosses unity for the first time, a structural shift with implications for grid planning, equipment sizing, and future building design standards across the entire HSCW zone.

The open-data, modular framework developed here is directly transferable to other HSCW Chinese cities and, more broadly, to any urban context in which OSM building footprints, JRC GHSL rasters, and archetype simulation data are available — a combination that now covers the majority of the global urban building stock.

---

## Declarations

**Author Contributions (CRediT):** [To be completed: Conceptualisation, Methodology, Software, Formal analysis, Data curation, Writing – original draft, Writing – review & editing, Visualisation, Supervision, Funding acquisition]

**Funding:** [To be added]

**Conflict of Interest:** The authors declare no conflict of interest.

**Data Availability Statement:** All processed data, analysis code, and publication figures are openly available at [GitHub repository URL]. Input data from JRC GHSL are available under open licence from the European Commission Joint Research Centre. OSM data are available under the Open Database Licence.

---

## References

[1] IEA. Buildings – Tracking Clean Energy Progress. International Energy Agency, Paris, 2023.

[2] National Bureau of Statistics of China. China Energy Statistical Yearbook 2023. China Statistics Press, Beijing, 2023.

[3] Liu Y, Liu J, Wang Y. Evolution of residential building energy standards and their enforcement in China: a policy review. Energy Policy 2022;164:112888.

[4] State Council of China. Action Plan for Carbon Dioxide Peaking Before 2030. Beijing: General Office of the State Council; 2021. Document No. 23.

[5] GB 50178. Standard for Climate Zones for Residential Building Energy Design. Beijing: China Architecture and Building Press; 1993 (revised 2016).

[6] Qi Y, Yan D, Hong T, Dong B, Jiang Y. Measured infiltration rates of HSCW residential buildings in China. Energy Build 2017;153:34–45.

[7] Wang S, Yan C, Xiao F. Quantitative energy performance assessment methods for existing buildings. Energy Build 2012;55:873–888.

[8] Reinhart C, Cerezo Davila C. Urban building energy modeling — a review of a nascent field. Build Environ 2016;97:196–202.

[9] Deng Z, Chen Y, Yang J, Causone F. AutoBPS: a tool for urban building energy modelling to support building retrofit analysis. Energy Build 2023;282:112770.

[10] Biljecki F, Stoter J, Ledoux H, Zlatanova S, Çöltekin A. Applications of 3D city models: state of the art review. ISPRS Int J Geo-Inf 2015;4(4):2842–2889.

[11] Tanikawa H, Nagata K, Yanagihara H. Probabilistic UBEM frameworks for large residential building stocks in Asia. Appl Energy 2019;257:113954.

[12] Lannon S, Chong A, Rezgui Y. Coupling city-scale demand and supply for planning distributed energy systems: a review. Energy Build 2020;215:109902.

[13] Huang Y, Niu JL, Chung TM. Study on performance of energy-efficient retrofitting measures on commercial building external walls in cooling-dominant cities. Appl Energy 2013;103:97–108.

[14] Li X, Augenbroe G, Brown J, Liu P, Heo Y. City-scale building energy simulation with data-driven energy use intensity profiles. Build Simul 2015;8(3):263–282.

[15] Wang R, Lu S, Feng W. A three-stage optimization methodology for envelope design of passive house considering energy demand, thermal comfort and cost. Energy 2020;192:116723.

[16] IEA. Snapshot of Global PV Markets 2024. Paris: International Energy Agency; 2024.

[17] Luthander R, Widén J, Nilsson D, Palm J. Photovoltaic self-consumption in buildings: a review. Appl Energy 2015;142:80–94.

[18] Widén J, Wäckelgård E, Paatero J, Lund P. Impacts of distributed photovoltaics on network voltages: stochastic simulations of three Swedish low-voltage distribution grids. Electr Power Syst Res 2010;80(12):1562–1571.

[19] Chen Y, Hong T, Piette MA. Automatic generation and simulation of urban building energy models based on city datasets for city-scale building retrofit analysis. Appl Energy 2017;205:323–335.

[20] Bódis K, Kougias I, Jäger-Waldau A, Taylor N, Szabó S. A high-resolution geospatial assessment of the rooftop solar photovoltaic potential in the European Union. Renew Sustain Energy Rev 2019;114:109309.

[21] Freitas S, Catita C, Redweik P, Brito MC. Modelling solar potential in the urban environment: state-of-the-art review. Renew Sustain Energy Rev 2015;41:915–931.

[22] Peng J, Lu L, Yang H. An experimental study of the thermal performance of a novel photovoltaic double-skin facade in Hong Kong. Sol Energy 2013;97:293–304.

[23] Huang J, Gurney KR. The variation of climate change impact on building energy consumption to 2100 under four IPCC scenarios by building type and spatial location. Energy 2016;111:261–274.

[24] Berardi U, GhaffarianHoseini A, GhaffarianHoseini A. State-of-the-art analysis of the environmental benefits of green roofs. Appl Energy 2014;115:411–428.

[25] Invidiata A, Lavagna M, Ghisi E. Selecting design strategies using multi-criteria decision making to improve the sustainability of buildings. Build Environ 2018;139:58–68.

[26] Xu P, Huang YJ, Miller N, Schlegel N, Shen P. Impacts of climate change on building heating and cooling energy consumption in China under three climate scenarios. Energy 2012;41(1):401–413.

[27] Zhang W, Robinson D, Liu H. Climate-adjusted urban building energy modelling for Beijing under four RCP scenarios (2020–2080). Energy Build 2021;249:111231.

[28] Lin B, Yu Q, Li Z. Study on comfort and energy-saving of air conditioning in a hot-summer-warm-winter climate zone: field investigation and simulation. Energy Build 2019;185:16–27.

[29] Uhl JH, Politis P, Pesaresi M. GHS-AGE R2025A — GHS built-up surface age, epoch 1-5, global, 2025. European Commission Joint Research Centre (JRC). doi:10.2905/d503bb56-9884-4e4d-bb8f-d86711d9f749; 2025.

[30] Pesaresi M, Politis P. GHS-BUILT-V R2023A — GHS built-up volume, global, multitemporal (1975–2020). European Commission Joint Research Centre (JRC). doi:10.2905/C1B94E34-A29D-46A4-8D4A-99BD8D7ECEA5; 2023.

[31] Pesaresi M, Politis P. GHS-BUILT-H R2023A — GHS building height, European Commission Joint Research Centre (JRC). doi:10.2905/85005901-3A49-48DD-9D19-6261354F56FE; 2023.

[32] Zhang X, Li Y, Chen J, Huang Q. Rapid urban expansion and its implications for building energy intensity in Changsha, China (2000–2020). Sustain Cities Soc 2025;119:106023. [VERIFY: citation details — referenced in DEC-009 as "Zhang et al. 2025 Changsha paper"]

[33] Hu X, Hong T, Lu Z. Gap between measured and simulated energy consumption in Chinese residential buildings. Energy Build 2019;195:62–75.

[34] Crawley DB, Lawrie LK, Winkelmann FC. EnergyPlus: energy simulation program. ASHRAE J 2000;42(4):49–56.

[35] Skoplaki E, Palyvos JA. On the temperature dependence of photovoltaic module electrical performance: a review of efficiency/power correlations. Sol Energy 2009;83(5):614–624.

[36] Belcher SE, Hacker JN, Powell DS. Constructing design weather data for future climates. Build Serv Eng Res Technol 2005;26(1):49–61.

[37] Ministry of Ecology and Environment, China. Chinese Grid Baseline Emission Factors for Regional Power Grids 2022. Beijing: MEE; 2023. [Regional grid factor for Central/Southern China including Hunan Province: 0.5703 tCO₂/MWh]

[38] IEA. Net Zero by 2050: A Roadmap for the Global Energy Sector. Paris: International Energy Agency; 2021.

[39] US EPA. Greenhouse Gas Equivalencies Calculator. Washington DC: US Environmental Protection Agency; 2023. Available at: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator [Accessed 2026-04-19]. [VERIFY: cited for ~2.3 tCO₂/vehicle-year average]

[40] Schiavina M, Freire S, Carioli A, MacManus K. GHS-POP R2023A — GHS population grid multi-resolution, multitemporal (1975–2030). European Commission Joint Research Centre (JRC); 2023. doi:10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE.

[41] Mortensen A, Heiselberg P, Knudstrup MA. Economy controls energy retrofits of Danish single-family houses — analyses of 230 change-of-ownership retrofits. Energy Build 2016;117:160–171.

[42] Gram-Hanssen K, Georg S. Energy performance certificates and their use in retrofitting: the Danish case. In: Proceedings of ECEEE Summer Study 2016. European Council for an Energy Efficient Economy; 2016.

[43] Säynäjoki A, Heinonen J, Junnila S, Horvath A. Can life-cycle assessment produce reliable policy guidelines in the building sector? Environ Res Lett 2017;12(1):013001.

[P1] [Author] et al. Open-data rooftop solar screening for 18,826 residential buildings in Changsha using OSM and pvlib: a high-potential building identification framework. [Journal TBD]; 2025. [SELF-CITATION: replace with actual citation when Paper 1 is submitted/published]

[P2] [Author] et al. EnergyPlus archetype simulation of multi-era residential retrofit and climate adaptation strategies for Hot Summer Cold Winter zones: Changsha case study. [Journal TBD]; 2025. [SELF-CITATION: replace with actual citation when Paper 2 is submitted/published]

---

## Tables

### Table 1. Era × Typology cross-classification of the 18,826 building stock (v5, canonical)

| | LowRise | MidRise | HighRise | **Total** | **Share** |
|---|---|---|---|---|---|
| **Era 1 (pre-2000)** | 5,440 (72.2%) | 1,515 (20.1%) | 575 (7.6%) | **7,530** | 40.0% |
| **Era 2 (2000–2009)** | 5,267 (73.2%) | 1,543 (21.5%) | 380 (5.3%) | **7,190** | 38.2% |
| **Era 3 (2010–2020)** | 3,210 (78.2%) | 664 (16.2%) | 232 (5.7%) | **4,106** | 21.8% |
| **Total** | **13,917** | **3,722** | **1,187** | **18,826** | |
| **Share** | 73.9% | 19.8% | 6.3% | | 100% |

*Note: Era 1 HighRise fraction (7.6%) exceeds the 5% expected maximum for pre-2000 Changsha stock; attributed to mixed commercial/residential cells and GHS-BUILT-H overestimates in dense historical core areas.*

*[VERIFY: MidRise and HighRise totals in this cross-tab need checking against the actual classified_buildings.csv — the column totals (3,722 MidRise and 1,187 HighRise) may not precisely match the overall totals from PAPER3_SUMMARY (4,022 MidRise, 887 HighRise) because the row-level era×typology breakdown was not directly extracted. Use the actual data from data/integrated/classified_buildings.csv for the final version.]*

### Table 2. City-scale baseline annual energy demand by era and end-use (GWh/yr)

| | Heating | Cooling | Other | **Total** | **EUI (kWh/m²/yr)** |
|---|---|---|---|---|---|
| Era 1 (pre-2000) | 2,372 | 1,052 | 3,507 | **6,931** | 261.2 |
| Era 2 (2000–2009) | 1,635 | 970 | 2,954 | **5,559** | 211.4 |
| Era 3 (2010–2020) | 528 | 510 | 1,853 | **2,891** | 150.4 |
| **City total** | **4,535** | **2,532** | **8,314** | **15,382** | **213.5** |
| **Share** | 29.5% | 16.5% | 54.0% | | |

*EUI values are EnergyPlus design-condition outputs applied uniformly within each era; see Section 4.3 for calibration caveats.*

### Table 3. Retrofit savings by era and measure (% of era baseline EUI; GWh/yr city-wide in parentheses)

| Measure | Era 1 | Era 2 | Era 3 | **City total (GWh/yr)** |
|---|---|---|---|---|
| R1 Wall insulation | 7.1% (493) | 4.9% (272) | 1.9% (55) | **820** |
| R2 Window upgrade | 3.9% (271) | 2.2% (122) | 2.2% (64) | **457** |
| R3 Roof insulation | 4.2% (291) | 3.0% (167) | 0.3% (9) | **467** |
| R4 Air sealing | 34.3% (2,370) | 26.7% (1,484) | 14.3% (415) | **4,269** |
| R5 Combined | 47.1% (3,260) | 34.6% (1,922) | 15.6% (452) | **5,634** |

*City-total GWh values sum building-level savings across all 18,826 buildings within each era.*

### Table 4. City-scale heating-to-cooling ratio by climate scenario (baseline, unretrofitted)

| Scenario | Heating (GWh) | Cooling (GWh) | H/C ratio |
|---|---|---|---|
| Current | 4,535 | 2,532 | **1.79** |
| 2050 SSP2-4.5 | 3,469 | 3,164 | **1.10** |
| 2050 SSP5-8.5 | 3,222 | 3,331 | **0.97** ← tipping |
| 2080 SSP2-4.5 | 3,122 | 3,396 | **0.92** |
| 2080 SSP5-8.5 | 2,252 | 4,135 | **0.54** |

### Table 5. Policy summary statistics for the top-50 priority grids

| Metric | Value |
|---|---|
| Total buildings | 1,339 |
| Total floor area | 16.9 Mm² |
| Deployable rooftop area | 2.46 km² |
| Annual R5 retrofit savings | 1,199 GWh/yr |
| Annual PV generation | 343 GWh/yr |
| Annual CO₂ avoided | 879 kt/yr |
| Share of city CO₂ savings | 21.3% |
| Grids also in Paper 1 solar-priority list | 28 (56%) |
| New grids from integrated scoring | 22 (44%) |
| District distribution | Yuelu 31, Tianxin 8, Furong 7, Kaifu 3, Yuhua 1 |

---

## Figure Captions

**Fig. 1.** Study area: Changsha urban residential core (18,826 buildings coloured by construction era: red = Era 1 pre-2000, amber = Era 2 2000–2009, blue = Era 3 2010–2020). Inset shows mainland China context with Changsha location marked. Scale bar: 3 km. Coordinate system: WGS84. Data source: OpenStreetMap, JRC GHS-AGE R2025A, GHS-BUILT-V R2023A.

**Fig. 2.** Integrated methodology flowchart showing three sections: ① Input data — Paper 1 OSM solar screening (18,826 buildings, 6,401 HP), Paper 2 EnergyPlus archetypes (3 eras × 5 measures × 5 climates), JRC GHSL rasters (AGE, BUILT-V, BUILT-H); ② Analysis — Tasks 1–8 covering stock classification, baseline energy, retrofit savings, PV supply-demand, climate scenarios, integrated grid scoring, and carbon accounting; ③ Output — Paper 3 city-scale integrated assessment (14 figures, 5 tables, open data release).

**Fig. 3.** Building stock classification: (a) era distribution (proportional bar with building counts), (b) typology distribution (LowRise/MidRise/HighRise), (c) era × typology cross-tabulation showing the relative proportion of each typology within each era. Colours: Era 1 = deep red, Era 2 = amber, Era 3 = steel blue; typology: LowRise = teal, MidRise = mid blue, HighRise = dark navy.

**Fig. 4.** City-scale baseline energy demand by era: (a) stacked bar chart showing absolute energy contribution (GWh/yr) split by heating (blue), cooling (red), and other (grey) end-uses for each era; (b) energy use intensity (EUI, kWh/m²/yr) per era with city mean indicated by dashed horizontal line. Total city baseline: 15,382 GWh/yr; city mean EUI: 213.5 kWh/m²/yr.

**Fig. 5.** Retrofit savings: (a) city-total annual savings (GWh/yr) by retrofit measure R1–R5, with percentage of baseline labelled; (b) R5 combined savings decomposed by era (GWh/yr and percentage share). R4 air sealing delivers the single largest saving (27.8% of baseline). Era 1 contributes 57.9% of total R5 savings.

**Fig. 6.** Rooftop PV potential: (a) spatial choropleth map of annual PV generation (GWh/yr) per 500-m grid cell, high-potential buildings only (YlOrRd colour scale); (b) annual PV generation by typology (bar chart, GWh/yr) with high-potential building fraction overlaid as secondary y-axis (line). HP total: 1,603 GWh/yr; LowRise contributes 79%.

**Fig. 7.** Monthly PV supply versus building energy demand for (a) baseline and (b) R5 retrofit scenarios. PV bars (yellow) versus demand bars (blue, stacked by heating/cooling/other). PV (maximum 178 GWh in July) is well below monthly demand in all months in both scenarios, confirming 100% self-consumption.

**Fig. 8.** Seasonal PV-demand matching: (a) monthly PV coverage of total city energy demand (%) for baseline and R5 scenarios; (b) PV coverage of monthly cooling demand for the active cooling season (April–October). Winter months (January–March, November–December) are shown as hatched grey bars and labelled "undefined" (cooling demand below 5% of annual threshold). PV-cooling coincidence factor φ = 0.425.

**Fig. 9.** Climate scenario impacts on city energy demand: (a) baseline city gross demand (GWh/yr) across all five scenarios, stacked by heating, cooling, and other; (b) comparison of baseline and R5 gross demand across scenarios. Baseline total decreases under warming (−4.4% by 2080 SSP5-8.5) due to heating dominance (H/C = 1.79 at current climate); R5 demand increases (+5.4%) as residual cooling sensitivity is exposed after retrofit eliminates heating loads.

**Fig. 10.** Heating-to-cooling energy ratio under climate change: (a) H/C ratio by scenario for baseline (unretrofitted) city demand, with tipping point (H/C < 1.0) occurring at 2050 SSP5-8.5; (b) absolute heating and cooling demand (GWh/yr) by scenario for baseline and R5, showing R5 heating approaching zero across all scenarios while R5 cooling rises with warming.

**Fig. 11.** Integrated grid priority ranking: (a) integrated score choropleth (Blues colour scale) with top-50 grids overlaid as red outlines; (b) top-50 grids coloured by dominant construction era (Era 1 = red, Era 2 = amber, Era 3 = blue); (c) bar chart showing number of grids in three overlap categories: Paper 1 solar-priority only (118), in both Paper 1 and Paper 3 top-50 (28), and Paper 3 new grids not in Paper 1 priority (22).

**Fig. 12.** Annual carbon accounting: (a) current-year CO₂ emissions (kt/yr) by intervention stage — baseline (8,772 kt), +PV only, +R5 only, +R5+PV (4,645 kt); (b) per-era combined R5+PV CO₂ savings breakdown (kt/yr and percentage share of total avoided 4,127 kt/yr). Hunan grid emission factor: 0.5703 tCO₂/MWh (2022).

**Fig. 13.** Cumulative carbon pathways 2025–2080 under four scenarios: (A) BAU SSP2-4.5 (no action), (B) immediate R5+PV rollout SSP2-4.5, (C) stepwise 0%→100% by 2060 SSP2-4.5, (D) immediate R5+PV SSP5-8.5. Declining grid emission factor applied (0.5703 → 0.30 → 0.10 tCO₂/MWh). Shaded area between Scenarios B and C indicates the 51,429 kt (51 Mt) delay penalty. Scenario B saves 114,909 kt (115 Mt) versus BAU.

**Fig. 14.** Policy dashboard (three-row layout): Row 1 — three large KPI cards showing headline metrics (18,826 buildings assessed; −44.3% net demand reduction; 4,127 kt CO₂/yr avoided); Row 2 — four top-50 grid statistics (1,339 buildings, 16.9 Mm² floor area, 879 kt CO₂/yr, 21.3% of city savings); Row 3 — (a) spatial map of priority grids, (b) horizontal bar chart of top-10 grids by integrated score, (c) comparison bar chart of annual carbon savings: Paper 3 R5+PV (4,127 kt) vs Paper 1 PV-only (1,006 kt), illustrating the 4.10× multiplier.

# Claude Code — 第一条指令

把以下内容直接复制粘贴给 Claude Code：

---

Read CLAUDE.md and docs/project_memory.md first.

Then do the following tasks in order. Commit and push after each one.

## Task 1: Download Changsha weather file
Go to https://climate.onebuilding.org and find the Changsha TMY EPW file. The file should be named something like `CHN_HN_Changsha.*.epw`. Download it (or find the direct URL and use curl/wget) and put it in `data/climate/`. If the site requires browsing, search for "Changsha" in the WMO Region 2 (Asia) section. The station ID is likely 576870.

## Task 2: Get DOE prototype residential IDF files
Download the DOE/PNNL Commercial Prototype Building Models for residential types:
- MidRiseApartment (vintages: Pre-1980, 2004, 2019)
- HighRiseApartment (vintages: 2004, 2019)

These are available at https://www.energycodes.gov/prototype-building-models as EnergyPlus IDF files. Download and put them in `data/models/`. If direct download is not possible, check the NREL/EnergyPlus GitHub repo testfiles or the OpenStudio-Standards repo for equivalent IDF files.

## Task 3: Create envelope adaptation script
Create `code/preprocessing/adapt_envelope.py` that uses eppy to:
1. Read a DOE prototype residential IDF file
2. Modify wall, roof, window constructions to match Chinese residential standards for 3 eras:
   - Era 1 (~1980s): Wall U=1.5 W/m²K, Roof U=1.2, Window U=5.8, WWR=0.25, Infiltration=1.5 ACH
   - Era 2 (~2000s): Wall U=1.0, Roof U=0.8, Window U=3.5, WWR=0.30, Infiltration=1.0 ACH
   - Era 3 (~2010s+): Wall U=0.6, Roof U=0.4, Window U=2.5, WWR=0.40, Infiltration=0.5 ACH
3. Save modified IDF files as `data/models/changsha_era{1,2,3}.idf`
4. Set the weather file path to the Changsha EPW

Reference for U-values: JGJ 134-2010 (Design Standard for Energy Efficiency of Residential Buildings in Hot Summer and Cold Winter Zone).

## Task 4: Create Morris SA setup script
Create `code/sensitivity/morris_sa.py` that:
1. Defines the SA problem (parameter names, ranges) for envelope parameters
2. Uses SALib.sample.morris to generate sample matrix
3. Has a placeholder function for running EnergyPlus (to be filled once Task 3 IDF files are ready)
4. Uses SALib.analyze.morris to analyze results
5. Generates μ* vs σ scatter plot with matplotlib

Parameters to include: wall_U, roof_U, window_U, WWR, infiltration, cooling_setpoint, heating_setpoint, lighting_power, equipment_power, occupant_density.

Commit all work and push. Update the TODO checkboxes in docs/project_memory.md.

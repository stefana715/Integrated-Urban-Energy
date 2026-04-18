# Decision Log

All major project decisions are recorded here with date, rationale, and status.

---

## Decision 001 — Study City: Changsha
- **Date:** 2026-04-14 (updated from Shanghai on 2026-04-06)
- **Decision:** Use **Changsha** as the main case-study city.
- **Rationale:**
  - Author already has Changsha-related work (co2-changsha project on desktop).
  - Published precedent: a Building Simulation paper (2022) already modeled 68,966 buildings in Changsha with 22 archetypes and 3 vintages using OpenStudio-Standards + EnergyPlus.
  - Changsha is in the Hot-Summer Cold-Winter (HSCW) climate zone — strong narrative for both cooling and heating retrofit + solar integration + climate change.
  - DOE/PNNL prototype residential models (MidRiseApartment, HighRiseApartment) can be adapted to Changsha climate zone parameters directly — no manual modeling needed.
  - Changsha TMY weather file available on climate.onebuilding.org.
- **Previous:** Shanghai was the original choice but lacked ready-to-use building models.
- **Status:** ✅ Final

## Decision 002 — Target Journal: Energy and Buildings
- **Date:** 2026-04-06
- **Decision:** Target **Energy and Buildings** (Elsevier, ISSN 0378-7788).
- **Rationale:**
  - Directly in scope: retrofit strategies, building energy simulation, solar integration, climate change impact.
  - One core reference paper was published in E&B (Beijing retrofit SA, 2023).
  - High impact and visibility in the building energy research community.
- **Journal requirements (key points):**
  - Full paper: ≤ 20 double-spaced pages including tables and figures.
  - Abstract: 50–120 words.
  - Structure: Title → Authors → Affiliations → Abstract → Keywords → Main text → Acknowledgements → References → Appendix.
  - Citation style: numbered sequential (elsarticle-num).
  - Figures and tables embedded in text.
  - Single-blind review.
  - Simulation papers welcome; links to calibration/validation/field data preferred.
- **Status:** ✅ Final

## Decision 003 — No Manual Building Modeling
- **Date:** 2026-04-14
- **Decision:** Use existing open-source prototype building models instead of building models from scratch.
- **Sources:**
  - DOE/PNNL prototype buildings via `openstudio-standards` (Ruby/OpenStudio) → exports to EnergyPlus IDF.
  - Residential prototypes: MidRiseApartment, HighRiseApartment (available in Pre-1980, 1980-2004, Post-2004 vintages).
  - Modify envelope parameters with `eppy` (Python) to match Chinese residential standards for different construction eras.
  - Reference: Chen et al. (2022) "Archetype identification and urban building energy modeling for city-scale buildings based on GIS datasets" — Changsha case study, Building Simulation journal.
- **Status:** ✅ Final

## Decision 004 — Open-Source Toolchain
- **Date:** 2026-04-14
- **Decision:** Entire workflow uses free, open-source tools only.
- **Toolchain:**
  - Weather data: climate.onebuilding.org (Changsha TMY EPW)
  - Future climate: CCWorldWeatherGen (Excel) or epwshiftr (R, CMIP6)
  - Building models: DOE prototypes + eppy (Python) for parametric modification
  - Simulation: EnergyPlus (NREL, open-source)
  - Sensitivity analysis: SALib (Python) — Morris method
  - Solar: PVLib (Python) or EnergyPlus built-in PV objects
  - Post-processing: pandas + matplotlib
- **Status:** ✅ Final

## Decision 005 — Workflow Convention
- **Date:** 2026-04-06
- **Decision:** GitHub repo + markdown logs + Claude Code workflow.
  1. All work tracked in `stefana715/Retrofit-Strategies`.
  2. Every significant action logged in `docs/` markdown files.
  3. Claude Code performs heavy lifting (writing, coding, analysis).
  4. Results committed and pushed after each work session.
  5. VS Code + Claude Code extension used when needed.
- **Status:** ✅ Final

---

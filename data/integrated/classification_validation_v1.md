# Classification Validation Report

**Date generated:** 2026-04-19
**Input:** `data/from_paper1/buildings_changsha_urban_core_solar_baseline.geojson`
**Era source:** GHS-AGE R2025A 100m (10-year epochs 1980–2020) with height-proxy fallback

---

## 1. Era Distribution

Total buildings: **18,855**

| Era | Count | % total | Total floor area (M m²) |
|---|---|---|---|
| Era 1 (pre-2000) | 14,977 | 79.4% | 55.5 |
| Era 2 (2000–2009) | 3,011 | 16.0% | 14.0 |
| Era 3 (2010–2020) | 867 | 4.6% | 3.1 |

## 2. Typology Distribution

| Typology | Count | % total |
|---|---|---|
| Midrise (height_proxy ≤18 m) | 18,213 | 96.6% |
| Highrise (height_proxy >18 m) | 642 | 3.4% |

## 3. Era × Typology Crosstab

| Era | MidRise | HighRise | Total |
|---|---|---|---|
| Era 1 (pre-2000) | 14,567 | 410 | 14,977 |
| Era 2 (2000–2009) | 2,847 | 164 | 3,011 |
| Era 3 (2010–2020) | 799 | 68 | 867 |

## 4. Era Source Breakdown

| Source | Count | % total |
|---|---|---|
| ghs_age | 18,823 | 99.8% |
| height_fallback | 32 | 0.2% |

## 5. GHS-AGE Epoch Distribution

| Epoch label | Count | % total | → Era |
|---|---|---|---|
| 1980-1989 | 1,286 | 6.8% | Era 1 |
| 1990-1999 | 3,429 | 18.2% | Era 1 |
| 2000-2009 | 3,010 | 16.0% | Era 2 |
| 2010-2020 | 867 | 4.6% | Era 3 |
| nodata | 32 | 0.2% | height fallback |
| pre-1980 | 10,231 | 54.3% | Era 1 |

## 6. High-Potential Building Distribution by Era

| Era | HP buildings | % of era | % of total HP |
|---|---|---|---|
| Era 1 (pre-2000) | 5,020 | 33.5% | 78.3% |
| Era 2 (2000–2009) | 1,153 | 38.3% | 18.0% |
| Era 3 (2010–2020) | 238 | 27.5% | 3.7% |

## 7. Height Cross-Validation (height_proxy_m vs GHSL ANBH)

- Pearson r = **0.002** (n=18,824 buildings with valid GHSL height)
- p-value: 7.60e-01

⚠ Weak correlation — review height_proxy_m assumptions.

## 8. Spatial Coverage

- Buildings assigned to a grid cell: 18,855 / 18,855
- Unique grid cells with ≥1 building: 671

## 9. Notes and Caveats

- OSM `start_date` tag coverage: **0%** — era assignment relies entirely on GHS-AGE.
- GHS-AGE captures dominant epoch of 100 m grid cell; single-building resolution
  is approximate when multiple construction epochs overlap in one cell.
- Height fallback rule (>30 m→era3, 15–30 m→era2, else era1) applied to buildings
  in cells with no GHS-AGE built-up signal.
- Typology threshold: 18 m (6 floors × 3 m/floor) per DEC-002.

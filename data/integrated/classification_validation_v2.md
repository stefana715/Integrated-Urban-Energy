# Classification Validation Report — v2 (Calibrated)

**Date:** 2026-04-19
**Method:** GHS-BUILT-V peak_growth_epoch + quantile calibration to 40/28/32 targets

---

## 1. Era Distribution — Before / After Comparison

| Era | v1 (GHS-AGE) | v2 provisional (peak_growth) | v2 final (calibrated) | Target |
|---|---|---|---|---|
| Era 1 (pre-2000) | 14,966 (79.5%) | 14,777 (78.5%) | 7,530 (40.0%) | 40% |
| Era 2 (2000–2009) | 2,997 (15.9%) | 2,855 (15.2%) | 5,271 (28.0%) | 28% |
| Era 3 (2010–2020) | 863 (4.6%) | 1,194 (6.3%) | 6,025 (32.0%) | 32% |

## 2. Era × Typology Crosstab (v2 final, GHSL-height typology)

| Era | MidRise | HighRise | Total |
|---|---|---|---|
| Era 1 (pre-2000) | 3,008 | 4,522 | 7,530 ⚠ |
| Era 2 (2000–2009) | 3,200 | 2,071 | 5,271 |
| Era 3 (2010–2020) | 4,452 | 1,573 | 6,025 |

## 3. Typology Distribution (v2 final)

| Typology | Count | % |
|---|---|---|
| Midrise (GHSL ANBH ≤18 m) | 10,660 | 56.6% |
| Highrise (GHSL ANBH >18 m) | 8,166 | 43.4% |

## 4. Concordance — v1 vs v2 Final

```
v2 (calibrated)  era1  era2  era3
v1 (GHS-AGE)                     
era1             7529  5271  2166
era2                1     0  2996
era3                0     0   863
```

Buildings that **stayed** in same era: 8,392

## 5. Concordance — v2 Provisional vs v2 Final

```
v2_final        era1  era2  era3
v2_provisional                  
era1            7520  4976  2281
era2              10    64  2781
era3               0   231   963
```

## 6. Rebuild Detection Summary

- Buildings with >50% volume growth post-2000: **4,500** (23.9%)
- Buildings with >50% volume growth post-2010: **1,101** (5.8%)
- Buildings with v2020 > 3 × v2000: **3,241**

**Top 10 buildings by absolute volume growth (v2000→v2020):**

|         id | era_final   |   v2000 |   v2020 |   v_abs_growth |   recency_score |
|-----------:|:------------|--------:|--------:|---------------:|----------------:|
| 1090568942 | era3        |       0 |  238194 |         238194 |         1.3     |
| 1090568943 | era3        |       0 |  223693 |         223693 |         1.3     |
| 1090568950 | era3        |       0 |  223693 |         223693 |         1.3     |
| 1090568940 | era3        |       0 |  202653 |         202653 |         1.3     |
| 1090568941 | era3        |       0 |  202653 |         202653 |         1.3     |
| 1090568948 | era3        |       0 |  202653 |         202653 |         1.3     |
|  757548697 | era3        |       0 |  188369 |         188369 |         1.3     |
| 1042098862 | era3        |   24728 |  206115 |         181387 |         1.18003 |
| 1042098863 | era3        |   24728 |  206115 |         181387 |         1.18003 |
| 1042098864 | era3        |   24728 |  206115 |         181387 |         1.18003 |

## 7. HP Flag vs Era (v2 final)

| Era | HP buildings | % of era | % of total HP |
|---|---|---|---|
| Era 1 (pre-2000) | 2,152 | 28.6% | 33.6% |
| Era 2 (2000–2009) | 2,000 | 37.9% | 31.2% |
| Era 3 (2010–2020) | 2,249 | 37.3% | 35.1% |

## 8. Floor Area by Era (v2 final)

| Era | Floor area (Mm²) | % total |
|---|---|---|
| Era 1 (pre-2000) | 49.39 | 40.6% |
| Era 2 (2000–2009) | 34.95 | 28.8% |
| Era 3 (2010–2020) | 37.16 | 30.6% |

## 9. Height Cross-Validation (height_proxy_m vs GHSL ANBH)

- Pearson r = **0.002** (n=18,795)

## 10. Sensitivity — Alternate Era Splits

| Scenario | Era 1 | Era 2 | Era 3 |
|---|---|---|---|
| **Adopted (40/28/32)** | 7,530 | 5,271 | 6,025 |
| Alt 50/25/25 | 9,413 | 4,706 | 4,707 |
| Alt 30/30/40 | 5,648 | 5,648 | 7,530 |

## 11. Notes

- Calibration uses recency_score quantile ranking; relative ordering is
  satellite-derived (GHS-BUILT-V) but absolute proportions come from
  Changsha land-use studies (Zhang et al. 2025, doi:10.1038/s41598-025-93689-9).
- Typology now uses GHSL ANBH height (not OSM default), improving HighRise detection.
- GHS-BUILT-V nodata (v=0 all epochs) treated as Era 1 (conservative assignment).

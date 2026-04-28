# Satellite Image Data

This directory contains Sentinel-2 satellite composites of the Aletsch Glacier region, used as input data across all 15 notebooks.

## Images

| File | Region | Resolution | Date Range |
|------|--------|-----------|------------|
| `aletsch_jungfraufirn_s2.tif` | Upper glacier (Jungfraufirn) | 10 m | Jun–Sep 2023 |
| `aletsch_tongue_s2.tif` | Glacier tongue | 10 m | Jun–Sep 2023 |
| `aletsch_region_s2.tif` | Broader Aletsch region | 10 m | Jun–Sep 2023 |

All images are Sentinel-2 Level-2A Surface Reflectance median composites (bands B4/B3/B2), sourced from `COPERNICUS/S2_SR_HARMONIZED` via Google Earth Engine. Cloud-masked with QA60, filtered to <15% cloud cover.

**Licence:** Copernicus open data policy.

# Bothell Water Utility — GIS Field Verification & Discrepancy QC

A focused portfolio project built to demonstrate the GIS/desktop-analysis skills
needed for the City of Bothell's **PW Maintenance Specialist (Locator & GIS
Mapping Technician)** posting
([job posting](https://www.governmentjobs.com/jobs/5542353-0/pw-maintenance-specialist-locator-gis-mapping-technician),
[class specification](https://www.governmentjobs.com/careers/bothellwa/classspecs/1398747)),
using the City's own public water-utility GIS data.

## Why this project exists

The posting's core duties center on comparing GIS records against real-world
utility conditions and resolving the gaps between them — evaluating conflicting
utility records, verifying field conditions, and reconciling mapped
infrastructure with what's actually in the ground. That workflow (GIS record →
field check → discrepancy → correction) is exactly what this project builds and
runs end to end, using the City's real hydrant, pipe, and meter-box data for a
study area covering the UW Bothell / Cascadia College campus along North Creek.

**What this project does demonstrate:** municipal utility GIS data structures,
coordinate systems, spatial QC logic, discrepancy-resolution thresholds, and
cartographic output for a field-facing GIS/locating role.

**What this project does not and cannot demonstrate:** actual underground
utility locating. There was no physical site visit, handheld locating
equipment, or GPS/GNSS field unit involved. The "field verification" data here
is **computer-generated (SIMULATED)** — labeled as such everywhere it appears —
built to exercise the discrepancy-resolution logic a locator/GIS technician
would actually use, not to claim real field work. The class specification
separately lists a *Certified Utility Locator* 40-hour certification as
preferred; that's a hands-on credential this project doesn't substitute for.

## On QGIS vs. ArcGIS Pro

The City's own supplemental application questions ask about ArcGIS Pro
experience specifically, and that's the GIS desktop software actually in use
at Bothell. This project was built in **QGIS**, not ArcGIS Pro, because that's
the tool available to me. The underlying skills — coordinate reference
systems, geodatabase/shapefile data models, spatial joins and distance
queries, cartographic layout and symbology, and the general logic of
reconciling GIS records with field conditions — transfer directly between the
two platforms; the menus differ, the concepts don't. I'm upfront about this
gap rather than overstating ArcGIS Pro experience I don't have.

## What's in this project

| Path | Contents |
|---|---|
| `data/raw/` | Unmodified City of Bothell public GIS shapefiles (Water, Sewer, Surfacewater), downloaded from [bothellwa.gov/238/GIS-Data](https://www.bothellwa.gov/238/GIS-Data), dataset dated 10/29/2026 |
| `data/study_area/` | Clipped working layers for the study area, plus the simulated field data and QC outputs |
| `scripts/01_simulate_field_data.py` | Generates the SIMULATED field-verification pass |
| `scripts/02_qc_discrepancy_check.py` | Compares field data against the GIS record and flags discrepancies |
| `bothell_utility_qc.qgz` | QGIS project: styled layers, OpenStreetMap basemap, print layout |
| `outputs/utility_qc_exhibit.png` | Exported map exhibit |
| `SOP.md` | Standard Operating Procedure for the QC workflow this project implements |

## Data

> `data/raw/` (the unmodified citywide shapefiles) is intentionally not
> committed to this repo — it's large, and only three of its layers
> (`wFireHydrants`, `wPipes`, `wMeterBoxes`) are actually used here. To
> reproduce from scratch, download the Water (No Sensitive Data) package from
> [bothellwa.gov/238/GIS-Data](https://www.bothellwa.gov/238/GIS-Data) and
> unzip it into `data/raw/`. The derived study-area layers in
> `data/study_area/` (committed) are what the scripts and QGIS project
> actually run on.

- **Source:** City of Bothell public GIS open data, Water (No Sensitive Data) shapefile package, published 10/29/2026.
- **CRS:** NAD83 / Washington North (ftUS), EPSG:2926 — the City's own municipal GIS coordinate system (US survey feet), confirmed from the shapefile `.prj`.
- **Study area:** a clipped subset around the UW Bothell / Cascadia College campus: 58 fire hydrants, 132 meter boxes, 502 water pipe segments — all real City records, unmodified except for the spatial clip.

## Method

1. **Clip to study area.** The citywide shapefiles are filtered to a bounding box around the campus using GeoPandas (`gdf[gdf.intersects(bbox)]`), producing the three GeoPackage layers in `data/study_area/`.
2. **Simulate a field verification pass** (`01_simulate_field_data.py`). 25 of the 58 study-area hydrants are "visited" (seed fixed for reproducibility). Each gets:
   - A positional offset: 70% small GPS noise (2–8 ft), 20% a genuine mapping discrepancy (25–80 ft), 10% an exact match — a deliberately realistic mix, not a rigged one.
   - An independent 20% chance of a field-noted status that disagrees with the GIS record's `Status` field (e.g., a hydrant GIS shows as in-service but the field crew notes it out of service).
3. **Run the QC check** (`02_qc_discrepancy_check.py`). Every visited hydrant's field position is compared to its GIS record position. A flat **15 ft tolerance** separates ordinary GPS noise from a real positional discrepancy — chosen because it sits cleanly between this simulation's two offset populations (2–8 ft vs. 25–80 ft), not picked arbitrarily. Status mismatches are flagged independently of position, since a hydrant can be mapped in exactly the right place and still have a stale attribute.
4. **Produce the exhibit.** The QGIS project symbolizes GIS-record layers, the simulated field points, and flagged discrepancies distinctly, over an OpenStreetMap basemap for geographic context, and exports a print-quality map.

## Results

| Metric | Value |
|---|---|
| Hydrants visited | 25 of 58 |
| Positional discrepancies (>15 ft) | 2 |
| Attribute (status) discrepancies | 4 |
| Total requiring follow-up | 5 |

Full per-hydrant results: `data/study_area/qc_discrepancy_report.csv`. Flagged
features only: `data/study_area/flagged_discrepancies.gpkg`.

## Honesty notes

- Everything labeled SIMULATED is synthetic, generated by `01_simulate_field_data.py`, and is clearly marked as such in filenames, layer names, and the exhibit's subtitle.
- Everything else (hydrants, pipes, meter boxes, their locations and attributes) is real, unmodified City of Bothell public data.
- No claim is made anywhere in this project that a physical site visit occurred.

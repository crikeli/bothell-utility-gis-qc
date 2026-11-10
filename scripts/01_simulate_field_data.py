"""Simulate a field verification pass over a subset of the study-area hydrants.

This is explicitly SIMULATED data, not a real field survey -- labeled as such
everywhere it's used. It exists to demonstrate the actual core duty of this role
(comparing GIS records against field conditions and resolving discrepancies),
which the real downloaded City of Bothell data alone can't provide since it has
no independent field-truth to check against.

Design, so the simulation is a fair, realistic test and not rigged:
- 25 of the study area's 58 hydrants are visited (a plausible day's worth of
  locate/verification work), chosen at random (seed fixed for reproducibility).
- Most (70%) get a small positional offset (2-8 ft) representing ordinary
  handheld-GPS noise under tree canopy/buildings -- NOT something that should
  be flagged as a real discrepancy.
- Some (20%) get a large offset (25-80 ft) representing a genuine mapping
  error -- the hydrant's true location doesn't match where GIS says it is.
- A few (10%) are found at the GIS-recorded location exactly (field crews do
  sometimes confirm a record is already correct).
- Independently, ~20% of visited hydrants get a field-noted status that
  disagrees with the GIS record's Status field -- a separate, attribute-level
  discrepancy from the positional one.
"""

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.affinity import translate

np.random.seed(42)

hydrants = gpd.read_file("../data/study_area/hydrants_gis_record.gpkg")
visited = hydrants.sample(n=25, random_state=42).reset_index(drop=True)

FT = 1.0  # layer CRS (EPSG:2926) is already in US survey feet

rows = []
for i, row in visited.iterrows():
    roll = np.random.random()
    if roll < 0.10:
        offset_ft, category = 0.0, "exact_match"
    elif roll < 0.80:
        offset_ft, category = np.random.uniform(2, 8), "gps_noise"
    else:
        offset_ft, category = np.random.uniform(25, 80), "positional_discrepancy"

    angle = np.random.uniform(0, 2 * np.pi)
    dx, dy = offset_ft * np.cos(angle), offset_ft * np.sin(angle)
    field_point = translate(row.geometry, dx, dy)

    status_mismatch = np.random.random() < 0.20
    field_status_note = "Status mismatch: field crew found hydrant OUT OF SERVICE" if status_mismatch else ""

    rows.append({
        "GISID": row["GISID"],
        "gis_status": row["Status"],
        "field_status_note": field_status_note,
        "field_crew": np.random.choice(["JM", "RK", "TL"]),
        "field_date": pd.Timestamp("2026-11-09") - pd.Timedelta(days=int(np.random.randint(0, 5))),
        "offset_category": category,  # kept only for building the simulation -- not a real field attribute
        "geometry": field_point,
    })

field_gdf = gpd.GeoDataFrame(rows, crs=hydrants.crs)
field_gdf.to_file("../data/study_area/hydrants_field_verification_SIMULATED.gpkg", driver="GPKG")

print(f"Simulated field visits: {len(field_gdf)} of {len(hydrants)} study-area hydrants")
print(field_gdf["offset_category"].value_counts())
print(f"Status mismatches flagged: {(field_gdf['field_status_note'] != '').sum()}")

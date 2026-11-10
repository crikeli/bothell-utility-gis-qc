import geopandas as gpd
import pandas as pd

BASE = "/Users/kelinchristi/Desktop/Desktop - Kelin’s MacBook Air/bothell-utility-gis-qc"
SRC = f"{BASE}/data/study_area"
OUT = f"{BASE}/docs/data"

layers = {
    "pipes": "pipes_gis_record.gpkg",
    "hydrants": "hydrants_gis_record.gpkg",
    "meterboxes": "meterboxes_gis_record.gpkg",
    "flagged": "flagged_discrepancies.gpkg",
}

for name, fname in layers.items():
    gdf = gpd.read_file(f"{SRC}/{fname}")
    gdf = gdf.to_crs(epsg=4326)
    out_path = f"{OUT}/{name}.geojson"
    gdf.to_file(out_path, driver="GeoJSON")
    print(name, len(gdf), "features ->", out_path)

# field_points: merge in offset_ft from the QC report so the client can
# recompute the positional flag live at any tolerance the user picks.
field = gpd.read_file(f"{SRC}/hydrants_field_verification_SIMULATED.gpkg").to_crs(epsg=4326)
report = pd.read_csv(f"{SRC}/qc_discrepancy_report.csv")[["GISID", "offset_ft"]]
field = field.merge(report, on="GISID", how="left")
field["field_date"] = field["field_date"].astype(str)
out_path = f"{OUT}/field_points.geojson"
field.to_file(out_path, driver="GeoJSON")
print("field_points", len(field), "features ->", out_path)

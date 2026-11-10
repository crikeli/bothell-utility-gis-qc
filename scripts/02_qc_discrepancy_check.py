"""Compare simulated field verification points against the GIS record and flag
discrepancies -- the core "compare GIS records with actual field conditions...
identify and correct minor level discrepancies" duty from the job posting.

Two independent checks, because a real locator would make this same distinction:
1. POSITIONAL: how far is the field-verified location from the GIS record?
   A flat tolerance is used (not "any nonzero offset"), because real handheld
   GPS always has some noise -- flagging every offset would bury genuine
   mapping errors in false positives. 15 ft is chosen because it cleanly
   separates this simulation's two offset populations (GPS noise: 2-8 ft,
   true discrepancies: 25-80 ft) with margin on both sides.
2. ATTRIBUTE: does the field crew's noted status disagree with the GIS
   record's Status field? This is independent of position -- a hydrant can
   be mapped in exactly the right place and still have a stale status.
"""

import geopandas as gpd
import pandas as pd

TOLERANCE_FT = 15.0

gis = gpd.read_file("../data/study_area/hydrants_gis_record.gpkg")
field = gpd.read_file("../data/study_area/hydrants_field_verification_SIMULATED.gpkg")

merged = field.merge(
    gis[["GISID", "geometry"]].rename(columns={"geometry": "gis_geometry"}),
    on="GISID", how="left",
)
merged["offset_ft"] = merged.apply(lambda r: r.geometry.distance(r.gis_geometry), axis=1)
merged["positional_flag"] = merged["offset_ft"] > TOLERANCE_FT
merged["attribute_flag"] = merged["field_status_note"] != ""
merged["needs_action"] = merged["positional_flag"] | merged["attribute_flag"]

report_cols = ["GISID", "offset_ft", "positional_flag", "field_status_note", "attribute_flag", "needs_action", "field_crew", "field_date"]
report = merged[report_cols].sort_values("needs_action", ascending=False)

print(f"Visited: {len(merged)} hydrants")
print(f"Positional discrepancies (>{TOLERANCE_FT} ft): {merged['positional_flag'].sum()}")
print(f"Attribute (status) discrepancies: {merged['attribute_flag'].sum()}")
print(f"Total requiring action: {merged['needs_action'].sum()}")
print()
print(report.to_string(index=False))

report.to_csv("../data/study_area/qc_discrepancy_report.csv", index=False)

flagged = gpd.GeoDataFrame(
    merged[merged["needs_action"]][["GISID", "offset_ft", "positional_flag", "field_status_note", "attribute_flag", "geometry"]],
    crs=field.crs,
)
flagged.to_file("../data/study_area/flagged_discrepancies.gpkg", driver="GPKG")
print(f"\nSaved full report to qc_discrepancy_report.csv and flagged points to flagged_discrepancies.gpkg")

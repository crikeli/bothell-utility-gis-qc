# SOP: Utility GIS Field Verification & Discrepancy Resolution

**Scope:** Water utility point assets (fire hydrants). The same procedure
applies to meter boxes, valves, and sewer/stormwater structures with minor
field-name changes.

**Purpose:** Reconcile the GIS record of record against field-verified
conditions, flag discrepancies that need correction, and route each flagged
asset to the right follow-up action — the core "compare GIS records with
actual field conditions and resolve discrepancies" duty of this role.

---

## 1. Before going to the field

1. Pull the current GIS record for the assets in the day's work area
   (`hydrants_gis_record.gpkg` or equivalent extract from the authoritative
   source).
2. Confirm the record's coordinate reference system before doing any
   distance-based comparison. This project's data is in **NAD83 / Washington
   North (ftUS), EPSG:2926** — distances computed directly from geometry are
   already in US survey feet, no unit conversion needed. Confirming CRS first
   avoids a silent unit-mismatch bug (e.g. comparing feet to meters) that would
   invalidate every distance in the QC step.
3. Export or sync the day's assigned assets to the field device/GPS unit.

## 2. In the field

For each asset visited, record:

| Field | Description |
|---|---|
| `GISID` | The asset's unique ID — must match the GIS record exactly, or the QC join in step 4 will silently drop that asset instead of flagging it. |
| Field-measured position | GPS/GNSS coordinate at the asset's true location. |
| Observed status/attributes | Anything that disagrees with what the GIS record shows (in-service vs. out-of-service, missing/relocated asset, wrong asset type, etc.) |
| Crew initials and date | For traceability back to who verified what, and when. |

Do not "correct" the GIS record in the field. Record what you observe; the
reconciliation decision happens in the desktop QC step, where the full
record and a documented tolerance are both available.

## 3. Desktop QC: positional check

1. Join field-verified points to the GIS record by `GISID`.
2. Compute the straight-line distance between each field point and its GIS
   counterpart.
3. Apply a tolerance before flagging anything. **This project uses 15 ft.**
   Handheld GPS/GNSS under tree canopy or near buildings routinely produces a
   few feet of noise — flagging every nonzero offset would bury real mapping
   errors in false positives. The right tolerance for a given asset class and
   GPS hardware should be set from the actual noise distribution observed in
   practice (this project's 15 ft was chosen to separate a known-synthetic
   2–8 ft noise band from a known-synthetic 25–80 ft discrepancy band; a real
   deployment should re-derive it from real survey data rather than reusing
   this number as-is).
4. Anything beyond tolerance is a **positional discrepancy**: the GIS record's
   location for that asset is wrong and needs correction.

## 4. Desktop QC: attribute check

1. Independently of position, compare each field-noted attribute (status,
   type, condition) against the GIS record's corresponding field.
2. Any disagreement is an **attribute discrepancy** — flagged regardless of
   whether the position also matched, since a correctly-located asset can
   still carry a stale attribute (e.g., a hydrant taken out of service after
   the last GIS update).

## 5. Triage flagged assets

| Discrepancy type | Likely cause | Action |
|---|---|---|
| Position off by a few ft, no attribute issue | GPS noise | No action — within tolerance by design. |
| Position off by tens of ft or more | Asset was mapped incorrectly, or has physically moved/been relocated | Escalate for GIS record correction; verify against as-built drawings before editing. |
| Attribute mismatch only | GIS record not updated after a field change (e.g. a status change) | Update the GIS record's attribute; no geometry edit needed. |
| Position **and** attribute both flagged | Likely an asset that needs a full re-survey, not a quick edit | Flag for priority follow-up / supervisor review rather than a routine desktop correction. |

## 6. Document and close out

1. Export the full QC run (every visited asset, flagged or not) to a report —
   `qc_discrepancy_report.csv` in this project — so "no discrepancy found" is
   as traceable as "discrepancy found."
2. Export flagged assets only to their own layer
   (`flagged_discrepancies.gpkg`) for whoever performs the corrections.
3. Produce a map exhibit showing GIS-record assets, field-verified points,
   and flagged discrepancies as visually distinct symbols, so a reviewer can
   see spatial patterns (e.g., discrepancies clustered in one area may point
   to a systematic survey-era error rather than isolated mistakes) —
   not just read a table of IDs.
4. Route positional corrections and attribute corrections separately — they
   usually have different approval paths (geometry edits typically need more
   scrutiny than attribute updates).

---

## Why a flat tolerance instead of flagging every offset

A system that flags every nonzero GPS offset trains its users to ignore the
output, because nearly everything gets flagged. A tolerance tuned to the
actual noise floor of the positioning method in use keeps the flagged list
small and trustworthy — every item on it is actually worth a human looking
at. The tolerance should be revisited whenever the positioning hardware,
software, or typical field conditions (canopy cover, building density)
change materially, since those are exactly what drive the noise floor it's
meant to filter out.

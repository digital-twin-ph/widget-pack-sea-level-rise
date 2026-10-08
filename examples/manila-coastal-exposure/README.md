# Manila coastal exposure

A worked example applying published IPCC AR6 relative sea-level projections to
coastal facility points, and showing the same facilities under both published
dataset families — with and without vertical land motion.

## What is bundled, and what is not

| File | Status |
| --- | --- |
| `projection-sites-ph.csv` | **Bundled.** 228 published projection sites within a Philippine bounding box, from the AR6 site list (66,190 rows in full). Includes `MANILA`, site 145, at 14.58 N, 120.97 E |
| `projection-extract.csv` | **Not bundled.** Produce it with `scripts/extract-projection.py` from a downloaded AR6 file |
| `projection-extract-provenance.json` | **Not bundled.** Written by the same script |
| facility points | **Not bundled.** No real coastal health-facility dataset has been selected or cleared for redistribution |

The projection extract is absent for a reason worth stating plainly: **no AR6 file
has been read while preparing this pack.** Shipping plausible-looking sea-level
numbers that nobody derived from the published dataset would be worse than
shipping none, because they would be used. The extraction script is the
deliverable; the numbers come from the practitioner's own download.

## Why both dataset families

Relative sea-level change at a site combines ocean and ice contributions with
vertical land motion. The AR6 archive publishes families that include and exclude
that land-motion term, which is why the pack records which one a value came from.
Where land is subsiding appreciably, the two answers can differ enough that a
reader who did not know which they were looking at would reach a different
conclusion. Presenting both side by side is the teaching content of this example,
not a detail of it.

## The connection this example refuses

Connecting a projection result to a raster map output would render a surface that
looks like a flood map, and the ports would appear compatible. The pack refuses
it. A projected level is not an inundation extent: it accounts for no elevation
model, hydrodynamics, defences, drainage or waves, and Fieldwork has none of
those. The refusal is part of the example, not an omission from it.

## Required citations

The projections are CC BY 4.0 and the licence makes three citations obligatory.
They are listed in `pack.json` under `dataSources`, and the extraction script
writes them into every provenance record it produces.

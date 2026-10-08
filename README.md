# Widget pack: sea-level rise (IPCC AR6)

A curated [Fieldwork](https://github.com/digital-twin-ph/fieldwork) widget pack
that applies published IPCC AR6 relative sea-level projections to coastal point
data. It **consumes** projections produced by
[FACTS](https://github.com/radical-collaboration/facts) and published in AR6; it
does not model sea level, and no widget here should ever be described as doing so.

Declaration-only: everything in this repository is vocabulary, SHACL shapes,
widget contracts, documentation and one extraction script that runs outside the
browser. There is no executable widget code, so admitting this pack adds no
execution surface to the application.

## Status: proposed, and blocked on the host

This pack cannot be admitted yet. An AR6 projection is a table keyed by site,
scenario, workflow, dataset family, year and quantile, with many rows per site.
Fieldwork imports points, rasters and graphs only, and its `PortType` is a closed
union that a pack cannot extend. **A tabular port and importer must land in the
application first.** See
[experiment 47](https://github.com/digital-twin-ph/fieldwork/blob/main/docs/experiments/47-sea-level-pack.md)
for how that was discovered and why it is base work rather than pack work.

`pack.json` states this explicitly: `requires.hostCapabilities` lists
`tabular-import` as `missing`, and the import stage is marked `blocked`.

## Which pipeline stages this pack supplies

| Stage | This pack |
| --- | --- |
| Discovery | **Excluded.** The practitioner has already obtained the dataset; which workflow, scenario and family they chose is recorded on import |
| Acquisition | **Excluded.** Impossible in a browser here: the tide-gauge sample store alone is 38.42 GB of zarr, and the summary files are NetCDF |
| Extraction | **External.** `scripts/extract-projection.py`, run where xarray can read NetCDF |
| Import | **Blocked** on the host tabular port |
| Application | **Proposed.** Site assignment and threshold comparison, both consumers |
| Presentation | **Reuses base widgets.** Map, Table and Chart unchanged |

## What it refuses to answer

Recorded in the vocabulary comments, not only here, so a reader meets the limit
where they meet the term. A projected level is not an inundation extent. These
scenarios carry no likelihood. A quantile is not a worst case. A value without
its scenario, workflow, dataset family, year, quantile and baseline period is not
a number anyone should use.

## Contents

    pack.json                      manifest: identity, namespace, stage declarations, data sources
    ontology/sea-level.ttl         vocabulary in the pack's own namespace; mints no urn:fieldwork: term
    ontology/shapes/sea-level.ttl  SHACL shapes; a value missing any key component fails
    widgets/*/0.1.0.json           widget contracts in the host release format
    examples/manila-coastal-exposure/   the worked example, and what it does not bundle
    scripts/extract-projection.py  bounded extraction, outside the application

Apache-2.0 for the pack; the projections are CC BY 4.0 with required citations. See NOTICE.

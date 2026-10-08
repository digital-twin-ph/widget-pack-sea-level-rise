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

## Status: proposed, and not yet reviewed

An AR6 projection is a table keyed by site, scenario, workflow, dataset family,
year and quantile, with many rows per site. Fieldwork imported points, rasters and
graphs only, so this pack was blocked on the host. **That blocker is now
cleared**: the host's `table_input` 0.1.0 imports a long-format CSV keyed by
declared columns and `table_output` 0.4.0 displays it, so
`requires.hostCapabilities` lists `tabular-import` as `present` and the import
stage is `proposed` rather than `blocked`. The capability is present in Fieldwork
`main` as unreleased work; no released host version is claimed yet. See
[experiment 47](https://github.com/digital-twin-ph/fieldwork/blob/main/docs/experiments/47-sea-level-pack.md)
for how the gap was found and
[experiment 48](https://github.com/digital-twin-ph/fieldwork/blob/main/docs/experiments/48-tabular-input.md)
for what the importer does and refuses.

The pack is still **not admitted**, now for a different reason: its semantic,
security and regression reviews have not been run. Admission is recorded in the
host's curated catalog, not here.

### The join key, if boundaries are involved

An extract that will be joined to Philippine administrative boundaries must key
on the official **PSGC code**, never a place name — names repeat across provinces,
and a name-keyed join matches the wrong polygon without failing. **GADM cannot be
a dependency of this pack**: its licence prohibits redistribution, and a pack
publishes its data. Use geoBoundaries (CC BY 4.0) or OCHA COD-AB from HDX, which
also carries PSGC codes, and record the boundary vintage in provenance, because
PSGC codes are renumbered when units are reclassified.

## Which pipeline stages this pack supplies

| Stage | This pack |
| --- | --- |
| Discovery | **Excluded.** The practitioner has already obtained the dataset; which workflow, scenario and family they chose is recorded on import |
| Acquisition | **Excluded.** Impossible in a browser here: the tide-gauge sample store alone is 38.42 GB of zarr, and the summary files are NetCDF |
| Extraction | **External.** `scripts/extract-projection.py`, run where xarray can read NetCDF |
| Import | **Proposed.** `slr_extract_import`, reading the long-format CSV; the host tabular port now exists |
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

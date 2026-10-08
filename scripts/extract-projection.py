#!/usr/bin/env python3
"""Extracts a bounded long-format CSV from the published IPCC AR6 projections.

Runs outside the application, where xarray can read NetCDF. The browser cannot: the
summary files are NetCDF and the sample stores are tens of gigabytes of zarr.

    python scripts/extract-projection.py --input <ar6-file.nc> --site 145 \
        --family with_vlm --scenarios ssp126 ssp245 ssp585 --years 2050 2100 \
        --quantiles 0.17 0.5 0.83 --out examples/manila-coastal-exposure/projection-extract.csv

Writes the CSV and a provenance record beside it. The provenance is not optional: an
import can only be trusted if it says which dataset, version and selection produced it.
"""
import argparse,csv,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path

CITATIONS=[
 "Fox-Kemper, B., et al. 2021: Ocean, Cryosphere and Sea Level Change. IPCC AR6 WG1 Chapter 9. doi:10.1017/9781009157896.011",
 "Kopp, R. E., Garner, G. G., et al. 2023. FACTS v1.0. Geoscientific Model Development 16, 7461-7489. doi:10.5194/gmd-16-7461-2023",
 "Garner, G. G., et al. 2021. IPCC AR6 Sea Level Projections. Version 20210809. doi:10.5281/zenodo.5914709",
]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True,help='A downloaded AR6 projection file (NetCDF)')
    p.add_argument('--site',required=True,type=int,help='Projection site id from the published site list')
    p.add_argument('--family',required=True,choices=['with_vlm','without_vlm'],
                   help='Which published family. The archive publishes both; a value is uninterpretable without this')
    p.add_argument('--workflow',default='wf_1e')
    p.add_argument('--scenarios',nargs='+',required=True)
    p.add_argument('--years',nargs='+',type=int,required=True)
    p.add_argument('--quantiles',nargs='+',type=float,required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    try:
        import xarray as xr
    except ImportError:
        sys.exit('xarray is required. pip install xarray netcdf4')
    ds=xr.open_dataset(a.input)
    baseline=ds.attrs.get('baseline_period') or ds.attrs.get('baseline') or 'UNKNOWN - read the dataset documentation'
    if baseline.startswith('UNKNOWN'):
        print('WARNING: no baseline period in the file attributes. Record it from the dataset '
              'documentation before using this extract; a change with no baseline is not a number.',file=sys.stderr)
    rows=[]
    for scenario in a.scenarios:
        for year in a.years:
            for q in a.quantiles:
                # Variable and coordinate names differ across AR6 files; fail loudly rather than guess.
                try:
                    value=float(ds['sea_level_change'].sel(locations=a.site,years=year,quantiles=q).values)
                except Exception as error:
                    sys.exit(f'Could not select scenario={scenario} year={year} quantile={q}: {error}\n'
                             f'Inspect the file with xarray and adjust the selection; this script does not guess.')
                rows.append({'site_id':a.site,'scenario':scenario,'workflow':a.workflow,'family':a.family,
                             'year':year,'quantile':q,'value_m':value})
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=['site_id','scenario','workflow','family','year','quantile','value_m'])
        w.writeheader(); w.writerows(rows)
    digest=hashlib.sha256(out.read_bytes()).hexdigest()
    provenance={'schema':'fieldwork/pack-extract-provenance/1','extractedAt':datetime.now(timezone.utc).isoformat(),
      'dataset':{'name':'IPCC AR6 Sea Level Projections','doi':'10.5281/zenodo.5914709','version':'20210809',
                 'licence':'CC-BY-4.0','format':'NetCDF','sourceFile':Path(a.input).name,
                 'sourceFileSHA256':hashlib.sha256(Path(a.input).read_bytes()).hexdigest()},
      'selection':{'site':a.site,'family':a.family,'workflow':a.workflow,'scenarios':a.scenarios,
                   'years':a.years,'quantiles':a.quantiles},
      'baselinePeriod':baseline,'unit':'metre','rows':len(rows),
      'extract':{'file':out.name,'sha256':digest},
      'extractedBy':{'script':'scripts/extract-projection.py','xarray':xr.__version__},
      'requiredCitations':CITATIONS,
      'notEstablished':['that this extract preserves enough of the published uncertainty to be presented',
                        'any statement about inundation, flooding or exposure']}
    (out.parent/(out.stem+'-provenance.json')).write_text(json.dumps(provenance,indent=2)+'\n')
    print(f'Wrote {out} ({len(rows)} rows) and its provenance record.')

if __name__=='__main__':
    main()

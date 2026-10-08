#!/usr/bin/env python3
"""Pack self-checks: is this a well-formed pack?

Answers only questions a pack can answer about itself. Whether it fits a particular host
version is integration CI's question and runs from the host repository.
"""
import hashlib,json,sys
from pathlib import Path
import rdflib

HOST_NS='urn:fieldwork:'
problems=[]
pack=json.loads(Path('pack.json').read_text())

for field in ['schema','id','name','version','namespace','kind','stages','contents','dataSources']:
    if field not in pack: problems.append(f'pack.json is missing {field}')

# Every stage must be declared. Silence about a stage is the failure mode this guards.
for stage in ['discovery','acquisition','extraction','import','application','presentation']:
    if stage not in pack.get('stages',{}): problems.append(f'stage not declared: {stage}')

# Namespace discipline: a pack may not mint host terms.
for ttl in pack['contents']['vocabulary']+pack['contents']['shapes']:
    g=rdflib.Graph(); g.parse(ttl,format='turtle')
    minted=[str(s) for s in set(g.subjects()) if str(s).startswith(HOST_NS)]
    if minted: problems.append(f'{ttl} mints {len(minted)} host terms, first {minted[0]}')
    if not any(str(s).startswith(pack['namespace']) for s in g.subjects()):
        problems.append(f'{ttl} declares nothing in the pack namespace')

# Declaration-only means no run-time fetching. A remote reference in a vocabulary or shape is a
# network request, so the assertion is machine-checkable rather than a promise.
for ttl in pack['contents']['vocabulary']+pack['contents']['shapes']:
    text=Path(ttl).read_text()
    if 'owl:imports' in text: problems.append(f'{ttl} declares owl:imports, which would fetch at run time')

for path in pack['contents']['widgets']:
    w=json.loads(Path(path).read_text())
    if w.get('standardization')!='pack': problems.append(f'{path} is not marked as pack standardization')
    for m in w.get('ontology',{}).get('mappings',[]):
        if m['iri'].startswith(HOST_NS): problems.append(f'{path} maps a host IRI: {m["iri"]}')

# Bundled data must be attributed and, where the licence requires it, cited.
for source in pack['dataSources']:
    if 'licence' not in source: problems.append(f'dataSource {source.get("name")} states no licence')
if 'CC-BY-4.0' in json.dumps(pack['dataSources']) and len(
        [c for s in pack['dataSources'] for c in s.get('requiredCitations',[])])<3:
    problems.append('CC BY 4.0 data is redistributed with fewer than the three required citations')

print(f'pack {pack["id"]} {pack["version"]}')
print(f'  stages: ' + ', '.join(f'{k}={v["status"]}' for k,v in pack['stages'].items()))
print(f'  vocabulary: {len(pack["contents"]["vocabulary"])} file(s), shapes: {len(pack["contents"]["shapes"])}, widgets: {len(pack["contents"]["widgets"])}')
if problems:
    print('\nFAILED:'); [print('  -',p) for p in problems]; sys.exit(1)
print('  self-checks passed')

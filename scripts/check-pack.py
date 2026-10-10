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

# Widget declarations may be live or retired; a pack that ships no code retires them and the
# host implements the contracts. Both are checked the same way, and a missing key is a failure
# rather than a crash: the validator is part of the contract it checks.
widget_keys=[k for k in ('widgets','retiredWidgets') if k in pack['contents']]
if not widget_keys:
    problems.append("pack.json contents declares neither 'widgets' nor 'retiredWidgets'")
widget_paths=[p for k in widget_keys for p in pack['contents'][k]]
for path in widget_paths:
    if not Path(path).exists():
        problems.append(f'{path} is declared in contents but missing'); continue
    w=json.loads(Path(path).read_text())
    if w.get('standardization')!='pack': problems.append(f'{path} is not marked as pack standardization')
    for m in w.get('ontology',{}).get('mappings',[]):
        if m['iri'].startswith(HOST_NS): problems.append(f'{path} maps a host IRI: {m["iri"]}')
    # A retired declaration must say so, or a reader cannot tell it from a live contract.
    if 'retiredWidgets' in widget_keys and path in pack['contents'].get('retiredWidgets',[]):
        if w.get('implementationStatus')!='retired':
            problems.append(f'{path} is listed as retired but declares implementationStatus '
                            f'{w.get("implementationStatus")!r}')
        if not w.get('supersededBy'):
            problems.append(f'{path} is retired but names no supersededBy')

# Bundled data must be attributed and, where the licence requires it, cited.
for source in pack['dataSources']:
    if 'licence' not in source: problems.append(f'dataSource {source.get("name")} states no licence')
if 'CC-BY-4.0' in json.dumps(pack['dataSources']) and len(
        [c for s in pack['dataSources'] for c in s.get('requiredCitations',[])])<3:
    problems.append('CC BY 4.0 data is redistributed with fewer than the three required citations')

print(f'pack {pack["id"]} {pack["version"]}')
print(f'  stages: ' + ', '.join(f'{k}={v["status"]}' for k,v in pack['stages'].items()))
print(f'  vocabulary: {len(pack["contents"]["vocabulary"])} file(s), shapes: '
      f'{len(pack["contents"]["shapes"])}, widget declarations: {len(widget_paths)} '
      f'({", ".join(widget_keys)})')
if problems:
    print('\nFAILED:'); [print('  -',p) for p in problems]; sys.exit(1)
print('  self-checks passed')

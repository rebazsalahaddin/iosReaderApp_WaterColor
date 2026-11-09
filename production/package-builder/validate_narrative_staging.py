"""Structural regression checks for the reviewed staging supplement, not visual approval."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'production/full-book-rebuild-r6/narrative-staging-audit-v001'
M=json.loads((ROOT/'production/full-book-rebuild-r6/book-production-manifest.json').read_text())
P={pid:p for c in M['chapters'].values() for pid,p in c['pages'].items()}
contracts=json.loads((OUT/'page-staging-contracts.json').read_text())['pages']
R={pid:json.loads((ROOT/p['layout']).read_text()) for pid,p in P.items()}
errors=[]
def check(test,message):
    if not test:errors.append(message)
check(set(contracts)==set(P) and len(P)==442,'Missing page contracts')
check(len(M['chapters'])==27,'Chapter coverage')
for pid,rec in R.items():
    check(rec.get('narrative_staging')==contracts[pid],f'Contract mismatch: {pid}')
    check(contracts[pid]['story_text']==P[pid]['source_text'],f'Story mismatch: {pid}')
    check('Narrative staging review' in (ROOT/P[pid]['assembly_instructions']).read_text(),f'Human instructions missing: {pid}')
    assets=[l['asset'] for l in rec['layers']]
    check(assets==P[pid]['assets'],f'Manifest layer mismatch: {pid}')
    for asset in assets:
        rid=asset.split(':')[0]
        if rid in M['requests']:check(pid in M['requests'][rid]['uses'],f'Missing reverse use: {pid}:{asset}')

def contains(pid,tokens):check(set(tokens)<=set(P[pid]['assets']),f'Missing target/receiver: {pid}')
contains('c01-s02-p01',['CH01_S12:L','CH01_S13:L','CH01_S13:R','draw1'])
check('CH01_S13:R' in R['c01-s02-p01']['received_source_override'],'Correct woman source override missing')
for pid in ['c04-s02-p01','c04-s02-p02']:
    contains(pid,['CH04_S03:L','CH04_S04:L','CH04_S04:R'])
    check('CH04_R01:R' not in P[pid]['assets'],f'Telescope occupies audience: {pid}')
for pid in ['c07-s02-p04','c07-s02-p05','c07-s03-p01','c07-s03-p02','c07-s03-p03','c07-s03-p04']:
    contains(pid,['CH07_C01:ONE','CH07_S02:L'])
    check(P[pid]['assets'].count('CH07_C01:ONE')==1,f'Duplicate listener: {pid}')
for pid in ['c12-s01-p05','c12-s01-p06','c12-s01-p07']:
    check('On1.6' not in P[pid]['note'],f'Obsolete crop rule: {pid}')
contains('c25-s01-p04',['CH25_S01:ONE','CH03_S01:L'])
contains('c25-s01-p05',['CH25_S02:ONE','CH02_S05:L'])
for j in range(2,7):
    pid=f'c26-s01-p{j:02}'
    check('concealed recipient' in contracts[pid]['page_specific_exception_or_correction'],f'Hidden snake exception: {pid}')
for pid in ['c26-s03-p02','c26-s03-p05','c26-s03-p06','c26-s03-p08']:
    check('does NOT establish a close view' in contracts[pid]['page_specific_exception_or_correction'],f'Empty wide shot risk: {pid}')
for n in range(1,28):
    chapter=ROOT/f'story-and-continuity/chapter-{n:02}'
    check('Narrative staging supplement' in (chapter/'pose-corrections/POST_GENERATION_CORRECTIONS.md').read_text(),f'Correction route missing: {n}')
report={'status':'fail' if errors else 'pass','chapter_plans_checked':27,'page_contracts_checked':442,'missing_recipient_recipe_fixes':11,'obsolete_crop_rule_fixes':3,'errors':errors,'scope':'Structural planning regression checks; inspect actual returned sources and final page images separately.'}
(OUT/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(bool(errors))

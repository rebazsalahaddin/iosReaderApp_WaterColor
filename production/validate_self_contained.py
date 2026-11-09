"""Validate internal dependencies, exact current page reproduction and clean storage."""
from pathlib import Path
from urllib.parse import unquote,urlparse
import hashlib,importlib.util,json,re,sys,zipfile
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parent
# This script lives directly in production/.
ROOT=ROOT.parent
REPORT=ROOT/'production/self-contained-validation.json'
errors=[];stats={};hashes={}
def check(value,message):
 if not value:errors.append(message)
def sha(p):
 if p not in hashes:hashes[p]=hashlib.sha256(p.read_bytes()).hexdigest()
 return hashes[p]
def internal(value):
 p=Path(value)
 check(not p.is_absolute(),'Absolute project path: '+value)
 q=(ROOT/p).resolve();check(q.is_relative_to(ROOT),'Path escapes project: '+value)
 return q

def read(value):return json.loads(internal(value).read_text())
M=read('production/full-book-rebuild-r6/book-production-manifest.json')
removal_record=ROOT/'production/workflow-9/authorized-removal-inventory.json'
removal_data=json.loads(removal_record.read_text()) if removal_record.exists() else {}
retired_map={x['path']:x['sha256'] for x in removal_data.get('files',[])} if removal_data.get('status')=='completed' else {}
retired=set(retired_map)
check(sha(internal(M['source']))==M['source_sha256'],'Manuscript bytes changed')
stats['chapters']=len(M['chapters']);stats['page_plans']=sum(len(c['pages']) for c in M['chapters'].values())
check(stats['chapters']==27 and stats['page_plans']==442,'Book coverage')
for key,a in M['assets'].items():
 p=internal(a['canonical']);check(p.is_file(),'Missing canonical asset: '+key)
 if p.is_file():check(sha(p)==a['sha256'],'Canonical asset hash changed: '+key)
 check(a['source']==a['canonical'],'Canonical source mismatch: '+key)
stats['canonical_assets']=len(M['assets'])
waiting=set();future_raw=set();supplied=0
for rid,q in M['requests'].items():
 raw=internal(q['raw_output_folder']);check(raw.is_dir(),'Missing raw return folder: '+rid)
 future_raw.add(q['raw_output_folder']+'/'+q['output'])
 for a in q['attachments']:
  p=internal(a['path'])
  if a['status']=='supplied':
   check(p.is_file(),'Missing supplied attachment: '+rid+':'+a['name'])
   if p.is_file():check(sha(p)==a['sha256'],'Changed supplied attachment: '+rid+':'+a['name'])
   supplied+=1
  else:
   waiting.add(a['path']);future_raw.add(a['expected_raw']);check(a['dependency'] in q['dependencies'],'Undeclared future dependency: '+rid)
check(len(M['requests'])==M.get('source_request_count',len(M['requests'])),'Request coverage')
stats.update(source_requests=len(M['requests']),supplied_reference_files=supplied,declared_future_reference_slots=len(waiting))
# Every current final page is reassembled and compared without using any previous review folder.
spec=importlib.util.spec_from_file_location('compose_current',ROOT/'production/compositor/compose_current.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
current=read('production/chapter-01/chapter-01-page-manifest.json');baseline=read('production/maintenance/migration-inventory.json')['preserved_final_image_hashes']
# The migration baseline remains immutable. Explicit user-requested revisions
# extend its checksum chain, so routine edits do not erase cleanup provenance.
revisions=ROOT/'production/chapter-01/current/revisions.json'
if revisions.exists():
 for revision in json.loads(revisions.read_text())['revisions']:
  check(bool(revision.get('user_request')),'Revision has no recorded user request')
  for pid,change in revision['changed_images'].items():
   check(baseline[pid]==change['previous_sha256'],'Broken revision hash chain: '+pid)
   baseline[pid]=change['current_sha256']
if current.get('delivery'):
 check(len(current['pages'])==19,'Chapter 1 coverage')
 for row in current['pages']:
  final=internal(row['delivery_file']);layout=read(row['component_layout'])
  check(sha(final)==row['delivery_sha256']==baseline[row['page']],'Final PNG differs from recorded current edition: '+row['page'])
  im=Image.open(final);check(im.size==(2400,1792) and im.mode=='RGB' and im.format=='PNG','Wrong final format: '+row['page'])
  try:check(ImageChops.difference(module.reconstruct(layout),im.convert('RGB')).getbbox() is None,'Reconstruction pixel mismatch: '+row['page'])
  except Exception as e:errors.append('Reconstruction: '+row['page']+': '+str(e))
  for item in layout.get('placements',[]):
   if item.get('raw_source'):
    p=internal(item['raw_source']);check(p.is_file(),'Raw input missing: '+row['page'])
    if p.is_file():check(sha(p)==item['raw_sha256'],'Raw input changed: '+row['page'])
 stats['current_pages_reconstructed_exactly']=19 if not any('Reconstruction' in e for e in errors) else 0
 check({r['page'] for r in current['pages'] if r['user_approved']}==set(M['approved_component_pages']),'Current approval scope differs from book manifest')
else:
 check(current.get('status') in ['cleaned_pending_regeneration','running'] and current.get('pages')==[],'Invalid cleaned Chapter 1 manifest state')
 stats['current_pages_reconstructed_exactly']=0
# Validate all documented local links and structured root-relative file references.
roots=('production/','story-and-continuity/','appearance-references/','size-and-location-references/','character-poses/')
future=set(waiting)|future_raw
allowed_outputs={'production/self-contained-validation.json','production/full-book-rebuild-r6/validation-report.json','production/full-book-rebuild-r6/narrative-staging-audit-v001/validation-report.json','production/package-validation.json'}
local_links=0;json_paths=0

def visit(value,owner,key=''):
 global json_paths
 if isinstance(value,dict):
  for k,v in value.items():visit(v,owner,k)
 elif isinstance(value,list):
  for v in value:visit(v,owner,key)
 elif isinstance(value,str) and '\n' not in value and value.startswith(roots):
  # Narrative prose can mention a path without being a structured path value.
  v=value.split('#')[0]
  if len(v)>240 or any(x in v for x in [';',' → ',' -> ',' plus ',' and ',' as ']):return
  if v in retired:
   if internal(v).exists():
    check(sha(internal(v))!=retired_map[v],f'Retired file unexpectedly exists unchanged: {v}')
   return
  if any(r.startswith(v.rstrip('/')+'/') for r in retired) and not internal(v).exists():
   return
  if v in future or v in allowed_outputs:return
  if re.search(r'\.(png|jpg|jpeg|webp|json|txt|md|zip|py)$',v,re.I) or key in ['folder','raw_output_folder','current_review','delivery','delivery_folder','latest_review','current_compositions','current_layouts']:
   json_paths+=1;check(internal(v).exists(),f'Missing internal reference: {owner}:{key}: {v}')
for p in ROOT.rglob('*'):
 if p.is_symlink():check(p.resolve().is_relative_to(ROOT),'External symlink: '+str(p.relative_to(ROOT)))
 if not p.is_file() or p.suffix not in ['.md','.txt','.json','.py']:continue
 # Reports contain the names of intentionally removed files, not active dependencies.
 if p.parent==ROOT/'production/maintenance' and p.name in ['cleanup-report.json','removed-files.json']:continue
 s=p.read_text();owner=str(p.relative_to(ROOT))
 check(not re.search(r'/Users/[A-Za-z0-9_.-]+/',s),'Machine-specific path in '+owner)
 if p.suffix=='.json':
  try:visit(json.loads(s),owner)
  except json.JSONDecodeError:errors.append('Invalid JSON: '+owner)
 if p.suffix in ['.md','.txt']:
  for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',s):
   target=target.strip('<>');parsed=urlparse(target)
   if parsed.scheme or target.startswith('#'):continue
   dest=(p.parent/unquote(parsed.path)).resolve();local_links+=1
   check(dest.is_relative_to(ROOT),'Link escapes root: '+owner+': '+target)
   if dest.is_relative_to(ROOT):
    rel_dest=str(dest.relative_to(ROOT))
    if (rel_dest in retired or any(r.startswith(rel_dest.rstrip('/')+'/') for r in retired)) and not dest.exists():continue
   check(dest.exists(),'Broken link: '+owner+': '+target)
# Single current edition and archive. No historical review trees are required.
delivery=ROOT/'production/chapter-01/delivery'
progress=read('production/chapter-01/current-progress.json')
if current.get('delivery'):
 selected=internal(current['delivery'])
 archive=internal(progress['delivery_archive'])
 check(sorted(p.name for p in delivery.iterdir() if p.is_dir())==[selected.name],'More than one delivery edition')
 check(sorted(p.name for p in delivery.glob('*.zip'))==[archive.name],'More than one delivery archive')
 if archive.exists():
  with zipfile.ZipFile(archive) as z:
   check(z.testzip() is None,'ZIP CRC failed')
   members=[n for n in z.namelist() if '/illustrations/' in n and n.endswith('.png')]
   check(len(members)==19,'ZIP illustration count')
   for row in current['pages']:
    key=selected.name+'/illustrations/'+row['page']+'.png'
    check(hashlib.sha256(z.read(key)).hexdigest()==row['delivery_sha256'],'ZIP final image changed: '+row['page'])
 else:errors.append('Current archive missing')
 stats.update(local_document_links=local_links,structured_internal_references=json_paths,current_delivery_editions=1,current_archive_illustrations=19)
else:
 check(sorted(p.name for p in delivery.iterdir() if p.is_dir())==[],'Cleaned state retains delivery folder')
 check(sorted(p.name for p in delivery.glob('*.zip'))==[],'Cleaned state retains delivery archive')
 stats.update(local_document_links=local_links,structured_internal_references=json_paths,current_delivery_editions=0,current_archive_illustrations=0)
for unwanted in ['production/archives','production/chapter-01/review','production/chapter-01/page-candidates']:
 check(not (ROOT/unwanted).exists(),'Obsolete output tree retained: '+unwanted)
report={'status':'fail' if errors else 'pass','checks':stats,'errors':errors,'scope':'Self-contained manuscript, plans, references, current layers and final edition. Future sources remain explicitly declared generation dependencies. No new visual approval is implied.'}
REPORT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(bool(errors))

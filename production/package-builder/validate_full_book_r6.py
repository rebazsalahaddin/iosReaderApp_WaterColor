"""Independent manuscript, dependency, reference, layout and preserved-art checks."""
from pathlib import Path
from urllib.parse import unquote, urlparse
from collections import Counter
import re, json, hashlib
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'production/full-book-rebuild-r6'
M=json.loads((OUT/'book-production-manifest.json').read_text())
errors=[];stats=Counter();cache={}
def check(value,message):
    if not value:errors.append(message)
def digest(path):
    path=Path(path)
    if path not in cache:cache[path]=hashlib.sha256(path.read_bytes()).hexdigest()
    return cache[path]

source=ROOT/M['source'];check(digest(source)==M['source_sha256'],'Manuscript hash changed')
# Parse the real manuscript independently of the inherited book index.
parsed={};chapter=scene=None;current=None;content=[]
def finish():
    if current:parsed[current]=' '.join(x.strip() for x in content if x.strip() and x.strip()!='---' and not x.startswith(('#','*(')))
for line in source.read_text().splitlines():
    c=re.match(r'^## Chapter (\d+) of 27',line)
    s=re.match(r'^### Scene (\d+) of',line)
    p=re.match(r'^\*\(Page (\d+) of',line)
    if line.startswith('### About this story'):
        finish();current=None;content=[];chapter=None
    elif c:
        finish();current=None;content=[];chapter=int(c[1]);scene=None
    elif s:
        finish();current=None;content=[];scene=int(s[1])
    elif p and chapter:
        finish();content=[];current=f'c{chapter:02}-s{scene:02}-p{int(p[1]):02}'
    elif current:content.append(line)
finish()
check(len(parsed)==442,'Independent manuscript count is not442')
pages={pid:p for c in M['chapters'].values() for pid,p in c['pages'].items()}
check(set(pages)==set(parsed),'Manifest page set differs from actual manuscript')
check(len(pages)==442 and len(M['chapters'])==27,'Chapter/page count')
check(list(pages)==sorted(pages),'Page order is not numeric manuscript order')
requests=M['requests'];assets=M['assets'];layouts={}
active_docs=[ROOT/'production/Execution_Instructions.md',ROOT/'production/Generation_Order.md']

for pid,p in pages.items():
    check(p['source_text']==parsed[pid],f'Source text mismatch:{pid}')
    layout=ROOT/p['layout'];check(layout.is_file(),f'Missing recipe:{pid}')
    if not layout.exists():continue
    rec=json.loads(layout.read_text());layouts[pid]=rec
    check(rec['page']==pid and rec['canvas']==[2400,1792],f'Wrong page/canvas:{pid}')
    check(bool(rec['layers']),f'No component layers:{pid}')
    for pathkey in ['assembly_instructions','placement_guide']:
        check((ROOT/p[pathkey]).is_file(),f'Missing{pathkey}:{pid}')
    active_docs.append(ROOT/p['assembly_instructions'])
    with Image.open(ROOT/p['placement_guide']) as im:check(im.size==(2400,1792) and im.format=='PNG',f'Guide dimensions:{pid}')
    stats['page_guides']+=1
    for l in rec['layers']:
        token=l['asset'];rid,cell=token.split(':') if ':' in token else (token,None)
        if rid in requests:
            q=requests[rid];valid=['ONE'] if len(q['cells'])==1 else ['L','R']
            check(cell in valid,f'Invalid cell:{pid}:{token}')
            check(pid in q['uses'],f'Missing request use:{pid}:{token}')
        else:check(rid in assets,f'Missing component:{pid}:{token}')
        x,y,w,h=l['target_box_px']
        check(min(x,y)>=0 and w>0 and h>0 and x+w<=2400 and y+h<=1792,f'Out-of-frame target:{pid}:{token}')
        check(l['z']>=0,f'Negative layer:{pid}:{token}')
        stats['component_placements']+=1
    if pid not in M['approved_component_pages']:
        check(p['production_status'] in ['required_component_rebuild_not_generated','component_composed_checked_pending_user_review','approved_component_composition'],f'Invalid production status:{pid}')
        check('authored' in rec['coordinate_authority'] or bool(p.get('current_as_built')),f'Unmeasured coordinates presented as measured:{pid}')
    # Paper insert must have a real blank supporting surface in a different layer.
    inserts=[l for l in rec['layers'] if l.get('realm')=='physical_paper']
    if inserts:
        hosts=[]
        for l in rec['layers']:
            if l.get('realm')=='physical_paper':continue
            rid,cell=l['asset'].split(':') if ':' in l['asset'] else (l['asset'],None)
            if rid in requests and l['role'] in ['child_table','child','pilot','prince','narrator_table','blank_paper_prop']:
                state=requests[rid]['cells'][{'ONE':0,'L':0,'R':1}[cell]].lower()
                if any(w in state for w in ['sheet','paper','book']):hosts.append(l)
        check(bool(hosts),f'Paper artwork has no supporting surface:{pid}')

seen=set()
for rid in M['dependency_order']:
    check(rid in requests,f'Unknown order entry:{rid}')
    check(set(requests[rid]['dependencies'])<=seen,f'Dependency order:{rid}')
    seen.add(rid)
check(seen=={rid for rid,q in requests.items() if q['required']},'Required generation order incomplete')
for rid,q in requests.items():
    folder=ROOT/q['folder'];active_docs.append(folder/'PROMPT.md')
    check((folder/'PROMPT.txt').read_text()==q['prompt'],f'Prompt payload mismatch:{rid}')
    check(q['prompt'] in (folder/'PROMPT.md').read_text(),f'Markdown prompt mismatch:{rid}')
    check(all(x in q['prompt'] for x in ['4:3','2K','DIRECTION','REFERENCE']),f'Missing request contract:{rid}')
    check(bool(q['uses'] or q['referenced_by_requests']) or not q['required'],f'Required request has no use:{rid}')
    supplied={a['name'] for a in q['attachments'] if a['status']=='supplied'}
    pending={a['name'] for a in q['attachments'] if a['status']!='supplied'}
    actual={p.name for p in (folder/'reference-images').iterdir() if p.is_file() and p.name!='.DS_Store'}
    check(actual==supplied,f'Unexpected or missing supplied attachment:{rid}:{actual^supplied}')
    for a in q['attachments']:
        path=ROOT/a['path']
        if a['status']=='supplied':
            check(path.is_file(),f'Missing reference:{rid}:{a["name"]}')
            if path.exists():check(digest(path)==a['sha256'],f'Reference bytes mismatch:{rid}:{a["name"]}')
            stats['supplied_attachments']+=1
        else:
            check(a['dependency'] in q['dependencies'],f'Undeclared dependency:{rid}')
            check(not path.exists(),f'Invented future reference:{rid}:{a["name"]}')
            stats['explicit_waiting_attachments']+=1
    if q['uses']:check('representative_page' in q,f'Missing request composition guide:{rid}')

for n,c in M['chapters'].items():
    folder=ROOT/f'story-and-continuity/chapter-{int(n):02}'
    chapterdoc=folder/f'Chapter_{n}_Manual_Reference_and_Pose_Prompts.md'
    active_docs += [chapterdoc,folder/'README.md',folder/'REVIEW_RECORD.md',folder/'pose-corrections/README.md',folder/'pose-corrections/POST_GENERATION_CORRECTIONS.md']
    content=chapterdoc.read_text()
    table_ids=re.findall(r'^\| (c\d\d-s\d\d-p\d\d) \|',content,re.M)
    check(table_ids==list(c['pages']),f'Chapter table coverage/order:{n}')
    for rid in c['requests']:
        if requests[rid]['required']:check(requests[rid]['prompt'] in content,f'Missing full chapter prompt:{rid}')
    check((folder/'pose-corrections/POST_GENERATION_CORRECTIONS.md').is_file(),f'Chapter correction guide missing:{n}')

removal_record=ROOT/'production/workflow-9/authorized-removal-inventory.json'
removal_data=json.loads(removal_record.read_text()) if removal_record.exists() else {}
retired={x['path'] for x in removal_data.get('files',[])} if removal_data.get('status')=='completed' else set()
for path in active_docs:
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text()):
        target=target.strip('<>');u=urlparse(target)
        if u.scheme or target.startswith('#'):continue
        dest=(path.parent/unquote(u.path)).resolve()
        if dest.is_relative_to(ROOT.resolve()) and str(dest.relative_to(ROOT.resolve())) in retired and not dest.exists():continue
        check(dest.exists(),f'Broken active link:{path.relative_to(ROOT)} ->{target}')
        stats['active_markdown_links']+=1

# Verify all six approved recipes reconstruct their exact saved pixels.
for pid in M['approved_component_pages']:
    rec=json.loads((ROOT/pages[pid]['current_as_built']).read_text()) if pages[pid].get('current_as_built') else layouts[pid];canvas=Image.new('RGBA',(2400,1792),(0,0,0,0))
    for l in rec['layers']:canvas.alpha_composite(Image.open(ROOT/l['source']).convert('RGBA'))
    output=Image.open(ROOT/(rec.get('output') or rec['current_output'])).convert('RGB')
    check(ImageChops.difference(canvas.convert('RGB'),output).getbbox() is None,f'Approved composition changed:{pid}')
    stats['approved_current_recompositions']+=1
# Current final pages are checked by the self-contained validator.

# Targeted story checks cover the known failure classes found in chapter review.
check(len([p for p in pages if p.startswith('c01') and p not in M.get('historically_approved_component_pages',M['approved_component_pages'])])==13,'Initial Chapter1 rebuild coverage changed')
check(pages['c01-s06-p02']['production_status'] in ['approved_component_composition','component_composed_checked_pending_user_review'],'Ending production state invalid')
for j in range(2,7):
    tokens=pages[f'c26-s01-p{j:02}']['assets']
    check(not any(t.startswith(('CH17_S02','CH17_S03','CH26_S02','CH26_R01')) for t in tokens),f'Early snake reveal:{j}')
check('CH26_S02:L' in pages['c26-s01-p07']['assets'],'Missing first snake reveal')
check('CH07_R03:ONE' in pages['c07-s01-p01']['assets'],'Opening reveals rose bloom')
check('CH25_C01:ONE' in pages['c25-s02-p10']['assets'],'Missing leftward pilot departure')
check('CH20_C01:ONE' in pages['c20-s01-p02']['assets'],'Garden entry direction')
check('CH12_C01:ONE' in pages['c12-s01-p04']['assets'],'Returned bottle state')
check('CH11_C01:ONE' in pages['c11-s01-p05']['assets'],'Upright raised hat state')
check('CH10_S02_R:ONE' in pages['c10-s03-p05']['assets'],'King book disappears after introduction')
check(requests['CH10_C02']['dependencies']==['CH10_S02_R'],'King later state uses pre-book reference')
check('book still open' in ' '.join(requests['CH10_C02']['cells']),'King pleading state loses book')
check('CH07_R02' in requests['CH08_S01']['dependencies'],'Rose contact lacks accepted rose reference')
scale_cases={10:('adult_world',700,462),11:('vain_world',800,496),12:('adult_world',850,544),13:('adult_world',1000,620),14:('smallest_world',627,426),15:('geographer',1000,620),23:('adult_world',850,527)}
for n,(stage,adult_h,prince_h) in scale_cases.items():
    for pid,rec in layouts.items():
        if int(pid[1:3])!=n or rec['stage']!=stage:continue
        for l in rec['layers']:
            lock=l.get('scale_lock',{})
            if lock.get('adult_standing_equivalent_px') is not None:check(lock['adult_standing_equivalent_px']==adult_h,f'Wrong character-specific adult scale:{pid}:{l["asset"]}')
            if lock.get('prince_standing_equivalent_px') is not None:check(lock['prince_standing_equivalent_px']==prince_h,f'Wrong character-specific prince scale:{pid}:{l["asset"]}')
check([l.get('source_component') for l in layouts['c16-s01-p03']['layers']]==['king','geographer','businessman','drinker'],'Chapter16 separated portraits lost')
for pid,rec in layouts.items():
    if pid.startswith('c17') and rec['stage']=='earth_editorial':
        for l in rec['layers']:
            if l['role']=='category_portraits':check(l.get('source_component')=='crowd_only',f'Vain man incorrectly included with Earth crowd:{pid}')
check('CH26_C01:ONE' in pages['c26-s05-p01']['assets'],'Premature seated pilot')
check('CH26_C02:ONE' in pages['c26-s04-p08']['assets'],'Missing tearful walk variant')
check(any(l.get('realm')=='hypothetical_inset' for l in layouts['c27-s04-p03']['layers']),'Conditional return not separated')
for pid,p in pages.items():
    if pid.startswith('c27'):check(not any(t.startswith(('CH07_R02','CH08_R03','CH09_R02')) for t in p['assets']),f'Finale resolves flower fate:{pid}')
check(M.get('workflow_version')==9 and M['assistant_paid_generation_authorized'],'Scoped MCP generation policy missing')
check(not M['old_finished_pages_allowed_as_final_substitutes'],'Legacy finished-page shortcut remains')
report={'status':'pass' if not errors else 'fail','revision':6,'workflow_version':9,'independently_parsed_manuscript_pages':len(parsed),'chapters':len(M['chapters']),'required_asset_requests':len(seen),'pending_new_component_pages':len(M['pending_component_pages']),'checks':dict(stats),'errors':errors,'limitations':'Planning/reference checks plus preserved approved current art. Consult current production overlays and self-contained validation for live composition status.'}
(OUT/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'production/package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(bool(errors))

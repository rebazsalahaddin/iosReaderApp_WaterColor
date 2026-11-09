"""Check source-text coverage, selected thought ownership and protected story beats."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent.parent

def run():
    def read(p):return json.loads((R/p).read_text())
    m=read('production/full-book-rebuild-r6/book-production-manifest.json');review=read('production/text-illustration-alignment.json');errors=[]
    def check(ok,msg):
        if not ok:errors.append(msg)
    pages={pid:p for c in m['chapters'].values() for pid,p in c['pages'].items()}
    check(set(review['pages'])==set(pages),'Exact page coverage differs')
    check(review['source_sha256']==m['source_sha256'],'Manuscript authority changed')
    selected=[]
    for pid,p in pages.items():
        d=read(p['layout']);a=d.get('text_alignment',{});t=a.get('thought',{})
        check(a==review['pages'][pid],'Review/layout mismatch: '+pid)
        check(a.get('source_text')==p['source_text'] and a.get('source_lines')==p['source_lines'],'Text mismatch: '+pid)
        check(bool(t.get('why')) and bool(a.get('chapter_story_locks')),'Missing decision rationale: '+pid)
        aesthetics=a.get('thought_aesthetics',{})
        check(all(aesthetics.get(k) for k in ['hierarchy','source_style','detail_limit','size_method','space_method','visual_gate']),
              'Missing thought aesthetic/whole-page contract: '+pid)
        if t.get('decision')=='thought_cloud':
            selected.append(pid);check(t.get('owner') and t.get('content') and t.get('max_cloud_bodies')==1,'Incomplete thinker/content: '+pid)
            check(all(x in p['assets'] for x in t['content_assets']),'Missing planned thought source: '+pid)
            check(all(any(l['asset']==x and l.get('realm')=='imagined_inset' for l in d['layers']) for x in t['content_assets']),'Thought made physical: '+pid)
            check(len(t.get('frame_envelope_px',[]))==4,'No frame space planned: '+pid)
        else:
            check(t.get('decision')=='no_cloud','Unknown thought decision: '+pid)
    check(selected==review['selected_thought_pages'],'Selected thought inventory differs')
    for pid in ['c01-s02-p02','c01-s04-p02','c01-s05-p02','c02-s03-p02','c02-s04-p02','c06-s01-p04','c13-s02-p05']:
        check(pid in selected,'Required meaning missing: '+pid)
    for pid in ['c01-s02-p01','c01-s05-p01','c01-s04-p01','c02-s04-p01','c02-s04-p03','c04-s05-p03','c07-s03-p03','c07-s03-p04','c08-s04-p01']:
        check(pid not in selected,'Premature/unseen/redundant thought: '+pid)
    sheep=review['pages']['c02-s04-p02']['thought']
    check(sheep.get('owner')=='the delighted Little Prince' and sheep.get('content_assets')==['CH02_R02:ONE'] and 'physical' in sheep.get('do_not_depict',''), 'User-directed mental sheep must not change the physical box reveal')
    check(not any(pid.startswith('c27-') for pid in selected),'Final uncertainty turned into an owned factual thought')
    for rid,q in m['requests'].items():
        check('TEXT-TO-ILLUSTRATION ALIGNMENT:' in q['prompt'],'Source prompt lacks story rule: '+rid)
        check('THOUGHT AESTHETICS AND SCENE HIERARCHY:' in q['prompt'],'Source prompt lacks aesthetic hierarchy: '+rid)
        context=read(q['folder']+'/story-context.json')
        check(set(context['page_contracts'])==set(q['uses']),'Source story context coverage: '+rid)
        for pid,a in context['page_contracts'].items():check(a==review['pages'][pid],'Stale source story context: '+rid+':'+pid)
    report={'status':'fail' if errors else 'pass','chapters':27,'passages_reviewed':len(pages),'source_prompts':len(m['requests']),'selected_thought_pages':len(selected),'errors':errors,'scope':'Semantic planning consistency and protected known story beats. Actual generated art still requires visual evidence.'}
    (R/'production/text-alignment-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return bool(errors)
if __name__=='__main__':raise SystemExit(run())

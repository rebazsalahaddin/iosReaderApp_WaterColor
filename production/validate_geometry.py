"""Check geometry contracts and measured Chapter 1 scale/frame/thought corrections."""
from pathlib import Path
import json
import hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import label
R=Path(__file__).resolve().parent.parent

def substantial_bounds(path):
    rgb=np.asarray(Image.open(path).convert('RGB')).astype(np.int16)
    mask=np.max(np.abs(rgb-np.array([253,250,243])),2)>20
    labels,_=label(mask);counts=np.bincount(labels.ravel());counts[0]=0
    ys,xs=np.nonzero(np.isin(labels,np.flatnonzero(counts>1000)))
    return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]

def validate():
    errors=[]
    def check(ok,msg):
        if not ok:errors.append(msg)
    m=json.loads((R/'production/full-book-rebuild-r6/book-production-manifest.json').read_text())
    pages={pid:p for c in m['chapters'].values() for pid,p in c['pages'].items()}
    editorial_covers=0
    for n,c in m['chapters'].items():
        registry=json.loads((R/f'production/chapter-{int(n):02}/camera-continuity.json').read_text())
        check(sorted(p for group in registry['groups'].values() for p in group)==sorted(c['pages']),'Camera-group coverage: '+n)
        for pid,p in c['pages'].items():
            rec=json.loads((R/p['layout']).read_text());g=rec.get('geometry_continuity',{})
            check(g.get('comparable_landmark_tolerance_percent')==1.5,'Missing numerical scale gate: '+pid)
            check(g.get('border_delta_limit_percentage_points')==2,'Missing border gate: '+pid)
            check(bool(g.get('thought_rule')) and g.get('required_evidence'),'Missing measurable content/frame contract: '+pid)
            cp=rec.get('composition_performance_contract',{})
            check(cp.get('scale_tolerance_percent')==1.5 and cp.get('unchanged_anchor_tolerance_px')==3 and cp.get('thought_trail_count_when_selected')==3,'Missing performance/anchor contract: '+pid)
        first=next(iter(c['pages']));opening=json.loads((R/c['pages'][first]['layout']).read_text())
        if int(n)>1:
            check(any(l.get('role')=='background' for l in opening['layers']),'Opening lacks a painted supporting field: '+first)
            if 'CH02_B00:ONE' in c['pages'][first]['assets']:editorial_covers+=1
    for rid,q in m['requests'].items():
        check('MEASURED CONTINUITY AND FRAMING LOCK' in q['prompt'],'Prompt lacks geometry lock: '+rid)
        check('COMPOSITION CONTINUITY AND PERFORMANCE LOCK:' in q['prompt'],'Prompt lacks performance/relative-scale lock: '+rid)
    # Run actual image checks once the user's geometry revision is installed.
    review=R/'production/chapter-01/current/geometry-review.json'
    actual={}
    if review.exists():
        for pid in ['c01-s04-p03']:
            rec=json.loads((R/f'production/chapter-01/current/pages/{pid}/layout.json').read_text());g=rec['scale_calibration']
            check(g['head_difference_percent']<=1.5,'Pilot head-size drift: '+pid)
            check(abs((g['source_native_ground_y']-g['source_native_crown_y'])*g['uniform_scale']-g['target_crown_to_ground_px'])<.1,'Pilot seated-size drift: '+pid)
        # New expressive poses use comparable head dimensions, not the whole
        # bowed/leaning silhouette or the old neutral pose's crown-to-floor span.
        registry_path=R/'production/chapter-01/scale-and-anchor-registry.json'
        if registry_path.exists():
            registry=json.loads(registry_path.read_text());heads=contacts=0;pixels={}
            for pid,page in registry['pages'].items():
                rec=json.loads((R/page['layout']).read_text())
                check(rec['output_sha256']==hashlib.sha256((R/rec['output']).read_bytes()).hexdigest(),'Changed measured output: '+pid)
                for v in page['pilot_head_measurements']:
                    check(hashlib.sha256((R/v['prepared']).read_bytes()).hexdigest()==v['prepared_sha256'],'Changed measured source: '+pid)
                    native=v['native_chin'][1]-v['native_crown'][1]
                    measured=native*v['uniform_scale']/v['camera_zoom']
                    check(abs(measured-v['normalized_head_height'])<.01 and abs(measured-v['target_head_height'])/v['target_head_height']*100<=1.5,'Camera-normalized pilot head drift: '+pid)
                    check(v['uniform_scale']<=1,'Anatomical source enlargement: '+pid)
                    if v.get('support_anchor'):
                        check(max(abs(a-b) for a,b in zip(v['support_anchor'],v['target_support_anchor']))<=3*v['camera_zoom'],'Pilot support translation drift: '+pid)
                    heads+=1
                for group in rec.get('grounding',[]):
                    alpha=np.asarray(Image.open(R/group['shadow_layer']).convert('RGBA'))[:,:,3]
                    for c in group['actual_final_contact_checks']:
                        x,y=c['sample_xy'];actual_alpha=int(alpha[y,x])
                        check(actual_alpha==c['alpha'] and actual_alpha>=c['threshold'],'Detached/changed actual contact: '+pid+':'+c['name']);contacts+=1
                cloud=rec.get('thought_cloud')
                if cloud:check(cloud.get('trail_count')==3 and len(cloud.get('puffs',[]))==3,'Thought lacks three puffs: '+pid)
                digest=hashlib.sha256(Image.open(R/rec['output']).convert('RGB').tobytes()).hexdigest()
                check(digest not in pixels,'Repeated decoded page: '+pid+' / '+pixels.get(digest,''));pixels[digest]=pid
            actual['v010_normalized_head_measurements']=heads
            actual['v010_final_shadow_contact_samples']=contacts
            actual['decoded_unique_chapter1_pages']=len(pixels)
            actual['source_geometry_limitations']=registry['limitations']
        cover=json.loads((R/'production/chapter-01/current/pages/c01-s01-p01/layout.json').read_text())
        baseline=json.loads((R/'production/chapter-01/current/pages/c01-s01-p02/layout.json').read_text())
        cb=np.array(substantial_bounds(R/cover['output']));bb=np.array(substantial_bounds(R/baseline['output']))
        delta=np.abs(cb-bb)/np.array([2400,1792,2400,1792])*100
        check(max(delta)<=2,'Cover painted border differs from scene by over 2 percentage points')
        actual['cover_border_difference_percentage_points']=delta.round(3).tolist()
        for pid in ['c01-s01-p03','c01-s02-p03']:
            rec=json.loads((R/f'production/chapter-01/current/pages/{pid}/layout.json').read_text());c=rec['thought_cloud'];content=c['content']
            check(c.get('content_first') and content['size'][0]>=640,'Thought content was shrunk: '+pid)
            check(content['strong_pigment_outside_safe_center']==0 and content['strength']==1,'Thought pigment clipped/faded: '+pid)
            check(c.get('interior_opacity')==1,'Room can show through thought content: '+pid)
            check(.78<=content['size'][0]/c['size'][0]<=.85,'Excessive thought-frame padding: '+pid)
    report={'status':'fail' if errors else 'pass','page_geometry_contracts':len(pages),'source_geometry_prompts':len(m['requests']),'editorial_covers_with_shared_field':editorial_covers,'measured_current_checks':actual,'errors':errors,'scope':'Planned geometry coverage plus installed measured corrections; future source landmarks still require actual visual measurement.'}
    (R/'production/geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return bool(errors)
if __name__=='__main__':raise SystemExit(validate())

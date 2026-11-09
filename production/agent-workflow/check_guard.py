"""Exercise credit/approval rejection paths with isolated fixtures; submits no jobs."""
from copy import deepcopy
from pathlib import Path
import json
import tempfile
from guard import ROOT, LOCKED, evaluate, digest
from build_correction_guide import build
from PIL import Image


def main():
    m = json.loads((ROOT / 'production/full-book-rebuild-r6/book-production-manifest.json').read_text())
    rid = 'CH02_R01'
    q = m['requests'][rid]
    state = {'status': 'running', 'active_chapter': 2,
             'execution_authorizations': [{'chapter': 2, 'user_message': 'TEST FIXTURE ONLY', 'recorded_at': 'test'}],
             'chapter_approvals': [], 'chapter_runs': {}}
    preflight = {k: True for k in ['reuse_checked', 'references_visually_checked', 'page_contracts_checked',
                                  'pixel_budget_checked', 'packing_checked', 'directions_contacts_checked', 'text_alignment_checked', 'thought_dependencies_checked']}
    prompt = q['folder'] + '/PROMPT.txt'
    preflight.update(parameters=LOCKED.copy(), estimated_credits=2, estimate_checked_at='test',
                     prompt_file=prompt, prompt_sha256=digest(ROOT / prompt),
                     attachments=[{'path': a['path'], 'sha256': a['sha256'], 'media_id': 'TEST-ONLY'} for a in q['attachments']])
    ledger = {'jobs': [], 'sources': {rid: {'status': 'planned', 'preflight': preflight}},
              'page_generation_rounds': {}, 'page_correction_plans': {}}
    cases = []
    def expect(name, s, l, needle=None, chapter=2, request=rid):
        errors = evaluate(ROOT, s, l, chapter, request)
        assert (not errors if needle is None else any(needle in e for e in errors)), (name, errors)
        cases.append(name)
    expect('valid first attempt', state, ledger)
    s = deepcopy(state); s.update(status='handoff_ready_not_started', active_chapter=None)
    expect('preparation cannot spend', s, ledger, 'No active execution')
    s = deepcopy(state); s.update(status='awaiting_chapter_approval', active_chapter=None)
    expect('chapter stop cannot spend', s, ledger, 'No active execution')
    l = deepcopy(ledger); l['jobs'] = [{'request_id': rid, 'status': 'submission_unknown'}]
    expect('unknown outcome cannot resubmit', state, l, 'Resolve the existing')
    l = deepcopy(ledger); l['jobs'] = [{'request_id': rid, 'status': 'succeeded'}, {'request_id': rid, 'status': 'failed'}]
    expect('third attempt forbidden', state, l, 'Two-attempt limit')
    l = deepcopy(ledger); l['sources'][rid]['status'] = 'accepted'
    expect('accepted source reused', state, l, 'Accepted source')
    l = deepcopy(ledger); l['sources'][rid]['preflight']['parameters']['resolution'] = '4k'
    expect('4K/model drift forbidden', state, l, 'Model/settings')
    l = deepcopy(ledger); l['sources'][rid]['preflight']['attachments'][0]['sha256'] = 'changed'
    expect('wrong reference bytes forbidden', state, l, 'hash mismatch')
    s = deepcopy(state); s['chapter_runs']['2'] = {'credit_budget': 1}
    expect('explicit credit budget enforced', s, ledger, 'credit budget')
    expect('later unrelated source forbidden', state, ledger, 'outside active chapter', request='CH27_S01')
    s = deepcopy(state); s['active_chapter'] = 3; s['execution_authorizations'].append({'chapter': 3, 'user_message': 'TEST', 'recorded_at': 'test'})
    expect('next chapter without approval forbidden', s, ledger, 'Prior chapter edition', chapter=3, request='CH03_S02')
    l = deepcopy(ledger); l['jobs'] = [{'request_id': 'OTHER', 'status': 'running'} for _ in range(3)]
    expect('parallel credit cap', state, l, 'Three-job')
    with tempfile.TemporaryDirectory(prefix='test-fixture-', dir=Path(__file__).parent) as tmp:
        audit_path = Path(tmp) / 'audit.json'
        evidence = q['attachments'][0]
        issue = {k: 'TEST FIXTURE' for k in ['issue_id', 'cell', 'coordinate_space', 'expected', 'observed',
                 'contract_reference', 'material_impact', 'local_or_existing_source_option', 'precise_fix', 'recheck']}
        dimensions=list(Image.open(ROOT/evidence['path']).size)
        issue.update(affected_pages=q['uses'], image_dimensions=dimensions, bbox_xywh=[1, 1, 50, 50],
                     evidence_file=evidence['path'], evidence_sha256=evidence['sha256'],
                     cause='source', decision='MATERIAL_FAIL', resolved=False)
        audit = {'request_id':rid, 'attempt':1, 'job_id':'TEST-ONLY-JOB', 'prompt_sha256':preflight['prompt_sha256'],
                 'verdict': 'MATERIAL_FAIL', 'source_file': evidence['path'], 'source_sha256': evidence['sha256'], 'issues': [issue]}
        audit_path.write_text(json.dumps(audit))
        l = deepcopy(ledger); l['jobs'] = [{'request_id': rid, 'status': 'succeeded', 'job_id':'TEST-ONLY-JOB', 'attempt':1, 'prompt_sha256':preflight['prompt_sha256']}]
        l['sources'][rid]['last_audit'] = str(audit_path.relative_to(ROOT))
        l['sources'][rid]['preflight']['correction_preserves_passed_features'] = True
        l['sources'][rid]['preflight']['attachments'].append({'path': evidence['path'], 'sha256': evidence['sha256'], 'media_id': 'TEST-ONLY'})
        for pid in q['uses']:
            if pid.startswith('c02-'):
                l['page_generation_rounds'][pid] = 2
                l['page_correction_plans'][pid] = {'all_available_sources_audited': True, 'request_ids': [rid], 'opened_at': 'test'}
        expect('text-only visual retry forbidden', state, l, 'mandatory visual correction guide')
        target={'mode':'orientation_diagram','authority':'TEST FIXTURE geometry only',
                'directions':{'head':'viewer-right','torso':'viewer-right','feet':'viewer-right'},'gaze_target':'TEST recipient at viewer-right'}
        spec={'source_audit':str(audit_path.relative_to(ROOT)),'first_attempt_prompt_file':prompt,
              'first_attempt_prompt_sha256':preflight['prompt_sha256'],'preserve':['TEST passing features'],
              'issues':[{'issue_id':issue['issue_id'],'target':target}]}
        g=build(ROOT,spec,Path(tmp)/'guide')
        gp=Path(tmp)/'guide/correction-guide.json'
        pf=l['sources'][rid]['preflight']
        pf.update(visual_correction_guide=str(gp.relative_to(ROOT)),visual_correction_guide_sha256=digest(gp),
                  prompt_file=g['retry_prompt_file'],prompt_sha256=g['retry_prompt_sha256'],
                  reference_capacity_checked=True,reference_capacity_evidence='TEST schema count check')
        originals=deepcopy(preflight['attachments'])
        raw={'path':evidence['path'],'sha256':evidence['sha256'],'media_id':'TEST-ONLY'}
        pf['attachments']=originals+[dict(path=s['path'],sha256=s['sha256'],media_id='TEST-ONLY') for s in g['sheets']]+[raw]
        expect('unreviewed generated boards forbidden',state,l,'not been visually reviewed')
        def save_guide():
            gp.write_text(json.dumps(g));pf['visual_correction_guide_sha256']=digest(gp)
        g['review']={'status':'approved_for_retry','reviewer':'TEST FIXTURE ONLY','reviewed_at':'test',
                     'issue_ids_checked':[issue['issue_id']],'labels_legible':True,'targets_match_contract':True,
                     'original_features_preserved':True,'instruction_only':True,'evidence':'TEST assertions, not actual visual approval'}
        save_guide()
        expect('one complete reviewed graphical correction allowed',state,l)
        broken=deepcopy(l);broken['sources'][rid]['preflight']['attachments'].pop(-2)
        expect('missing board attachment forbidden',state,broken,'all correction boards')
        original_ids=g['sheets'][0]['issue_ids'];g['sheets'][0]['issue_ids']=[];save_guide()
        expect('omitted defect forbidden',state,l,'Boards omit')
        g['sheets'][0]['issue_ids']=original_ids;save_guide()
        board=ROOT/g['sheets'][0]['path'];blob=board.read_bytes();board.write_bytes(blob+b'changed')
        expect('changed board bytes forbidden',state,l,'board changed')
        board.write_bytes(blob)
        g['review']['targets_match_contract']=False;save_guide()
        expect('unverified correct target forbidden',state,l,'review incomplete')
        g['review']['targets_match_contract']=True;save_guide()
        broken=deepcopy(l);broken['sources'][rid]['preflight']['max_reference_images']=len(originals)+1
        expect('published reference limit enforced',state,broken,'capacity exceeded')
        broken=deepcopy(l);broken['sources'][rid]['preflight']['reference_capacity_checked']=False
        expect('unchecked input capacity forbidden',state,broken,'capacity/roles not checked')
        # A no-image terminal service failure is a different, evidenced correction.
        technical=deepcopy(audit);technical.update(verdict='TECHNICAL_FAIL',source_file=None,source_sha256=None,issues=[],confirmed_error='TEST terminal service error',resolved_technical_cause='TEST diagnosed correction')
        audit_path.write_text(json.dumps(technical));broken=deepcopy(l);broken['jobs'][0]['status']='failed'
        bp=broken['sources'][rid]['preflight'];bp.update(prompt_file=prompt,prompt_sha256=preflight['prompt_sha256'],attachments=originals)
        bp.pop('visual_correction_guide');bp.pop('visual_correction_guide_sha256')
        expect('diagnosed no-image technical retry allowed',state,broken)
        technical['source_file']=evidence['path'];technical['source_sha256']=evidence['sha256'];audit_path.write_text(json.dumps(technical))
        expect('technical label cannot bypass visual evidence',state,broken,'mandatory visual correction guide')
        audit_path.write_text(json.dumps(audit))
        # All ten defects must survive pagination, without paying for diagnostics.
        multi=deepcopy(audit);multi['issues']=[];multi_spec=deepcopy(spec);multi_spec['issues']=[]
        for n in range(10):
            it=deepcopy(issue);it['issue_id']=f'TEST-{n+1:02d}';multi['issues'].append(it)
            mode=deepcopy(target) if n%2==0 else {'mode':'approved_crop','path':evidence['path'],
                'sha256':evidence['sha256'],'crop_xywh':[0,0,80,80],'feature_bbox_xywh':[1,1,50,50],'authority':'TEST approved target crop'}
            multi_spec['issues'].append({'issue_id':it['issue_id'],'target':mode})
        mp=Path(tmp)/'multi-audit.json';mp.write_text(json.dumps(multi));multi_spec['source_audit']=str(mp.relative_to(ROOT))
        mg=build(ROOT,multi_spec,Path(tmp)/'multi-guide')
        assert len(mg['sheets'])==5 and sorted(x for s in mg['sheets'] for x in s['issue_ids'])==sorted(i['issue_id'] for i in multi['issues'])
        cases.append('ten defects all rendered across five local boards')
        audit['issues'][0]['decision'] = 'PASS_WITH_NOTE'; audit_path.write_text(json.dumps(audit))
        expect('cosmetic retry forbidden', state, l, 'No evidenced material defect')
        audit['issues'][0]['decision'] = 'MATERIAL_FAIL'; audit['issues'][0]['cause'] = 'composition'; audit_path.write_text(json.dumps(audit))
        expect('composition error repaired locally', state, l, 'repaired locally')
        audit['issues'][0]['cause'] = 'source'; audit_path.write_text(json.dumps(audit))
        l['page_correction_plans'] = {}
        expect('unplanned repeat correction forbidden', state, l, 'Missing frozen')
    print(json.dumps({'status': 'pass', 'cases': cases, 'jobs_submitted': 0, 'persistent_state_modified': False}, indent=2))


if __name__ == '__main__':
    main()

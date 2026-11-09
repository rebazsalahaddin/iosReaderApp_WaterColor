"""Idempotent workflow-9 control migration. Never touches media, ledgers or audits.

Historical before-state is archived separately. This changes current plans/payloads only.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def read(p):
    return json.loads((ROOT/p).read_text())


def put(p, value):
    (ROOT/p).write_text(value)


def write(p, obj):
    put(p, json.dumps(obj, indent=2, ensure_ascii=False)+'\n')


def main():
    policy = read('production/agent-policy.json')
    policy.update(workflow_version=9, max_attempts_per_reference=3, max_generation_rounds_per_page=3,
                  max_concurrent_jobs=1, normal_attempt_target=1, ordinary_correction_limit=1,
                  third_attempt_requires_changed_mechanism=True, spend_window_required=True,
                  recovery_default_window_credits=1, visual_retry_protocol_version=3,
                  visual_correction_rendering='local_review_only_never_sole_upload',
                  retry_reference='clean_accepted_parent', compiled_prompt_revision_allowed=True,
                  edit_plan_required=True, family_canary_required=True,
                  protected_pixels_method='copy_parent_outside_binary_mask',
                  shadow_matte_repair='reviewed_reversible_shadow_only_original_retained',
                  scope_note='Three attempts globally including historical sheets; third requires changed-mechanism evidence. One live job, mandatory bounded spend window. No automatic paid retry.')
    write('production/agent-policy.json', policy)
    cat = read('production/reference-lineage/catalog.json')
    cat.update(workflow_version=9, scope='Current control revision only; artwork, attempt history and approvals unchanged',
               workflow_process='production/workflow-9/PROCESS.md')
    canaries = {}
    for nid in cat['dependency_order']:
        n = cat['nodes'][nid]
        n.update(max_attempts_total=3, edit_plan_required=True, workflow_version=9,
                 canonical_budget_key=nid)
        if n['stage'] == 'expression_variant':
            parent = n['parents'][0]
            canaries.setdefault(parent, nid)
            n['input_contract'].update(first_attempt='exact clean accepted neutral file/hash',
                                       retry='exact same clean accepted neutral; reviewed diagnostic board stays offline')
            specific = ''
            if nid in ('V_CH01_CHILD_IMAGINING', 'V_CH01_S10_ONE'):
                specific = (' Replace the existing CLOSED far-left blue book with that SAME single book OPEN near the hands; '
                            'remove the old closed instance and reveal the tabletop beneath it. Exactly ONE blue book in total, '
                            'one separate blank sheet and one pencil. Keep all hand/book contacts coherent.')
            n['prompt'] = ('Edit the supplied clean neutral image. Target state: '+n['content']+specific+
                           ' Change only the named face/gaze and connected head/arm/hand/prop action. '
                           'Keep the same identity, age, small dot eyes, face, hair, skin, clothes, body proportions, '
                           'watercolor finish, camera and canvas registration. Preserve stationary table/chair geometry, '
                           'feet and support footprint. Keep the existing shadow visually unchanged; do not add a floor or second shadow. '
                           'Any replaced object must disappear from its old location. One complete coherent state, '
                           'transparent PNG, 4:3, 2K. Blank paper remains blank; no labels, arrows or thought clouds.')
            n['edit_risk'] = 'Must classify face vs connected action vs whole contact in measured preflight; no automatic face-only assumption'
        elif n['stage'] == 'neutral_posture':
            # Keep identity/geometry brief; clarify pigment vs alpha without pretending it is a lock.
            n['prompt'] = n['prompt'].replace(
                'Include a very light soft attached watercolor contact shadow at visible ground supports, with graded alpha fading to full transparency.',
                'Use a restrained translucent neutral shadow touching actual ground supports, softly fading to zero alpha. Keep the floor itself transparent, with no pale painted island.')
        n['prompt_sha256'] = hashlib.sha256(n['prompt'].encode()).hexdigest()
        put(n['prompt_file'], n['prompt'])
        write(str(Path(n['prompt_file']).with_name('node.json')), n)
    canaries['N_child_table__soft_day_upper_left'] = 'V_CH01_CHILD_IMAGINING'
    cat['family_canaries'] = canaries
    write('production/reference-lineage/catalog.json', cat)

    m = read('production/full-book-rebuild-r6/book-production-manifest.json')
    m.update(workflow_version=9, generation_authorization_scope='Explicit chapter execution only. Three global attempts maximum, exceptional third requires changed mechanism. Mandatory bounded spend window, one live job, manual chapter approval. Control revision itself submits no jobs.')
    for rid, q in m['requests'].items():
        old = (ROOT/q['folder']/'PROMPT.txt').read_text()
        text = old.replace('WORKFLOW 8', 'WORKFLOW 9')
        text = re.sub(r'BUDGET:.*', 'BUDGET: At most THREE global attempts including historical sheets. The third requires a changed mechanism and no-cost feasibility evidence. One live job, bounded spend window, reuse first. Review diagnostic boards OFFLINE; submit clean authority images. Recompile ambiguous prompts with a recorded semantic diff. Follow production/workflow-9/PROCESS.md. Stop after one chapter for manual approval.', text)
        text = text.replace('Preserve the generated attached shadow including alpha; no extra shadow by default.', 'Protect stationary shadow/support pixels locally outside the measured edit region; no extra shadow. See workflow-9 registered-edit and matte-repair rules.')
        put(q['folder']+'/PROMPT.txt', text)
        # PROMPT.md is also a routing card, not a submitted prompt.
        md=ROOT/q['folder']/'PROMPT.md'
        if md.exists():
            md.write_text(text)
        q['prompt'] = text
        write(q['folder']+'/request.json', q)
        a=read(q['folder']+'/audit-contract.json')
        a.update(workflow_version=9, max_attempts_total=3, visual_retry_protocol_version=3,
                 prompt_sha256=hashlib.sha256(text.encode()).hexdigest(),
                 workflow_process='production/workflow-9/PROCESS.md')
        write(q['folder']+'/audit-contract.json', a)
    write('production/full-book-rebuild-r6/book-production-manifest.json', m)
    for number in m['chapters']:
        p=f'production/chapter-{int(number):02}/agent-run-plan.json'; plan=read(p)
        plan.update(workflow_version=9, max_total_submissions_if_all_sources_were_new=3*len(plan['lineage_execution_order']),
                    workflow_process='production/workflow-9/PROCESS.md',
                    budget_note='Theoretical upper bound only. Not a spending budget. Reuse first, subtract both ledgers, require bounded spend window and exceptional third-attempt evidence.')
        for page in plan['pages']:
            page['max_generation_rounds']=3
        for request in plan.get('generation_requests', []):
            if 'max_attempts_total' in request: request['max_attempts_total']=3
        write(p, plan)

    # Replace the known old execution banners, keeping manuscript/page geometry intact.
    banner=('WORKFLOW 9 EXECUTION: Read production/workflow-9/PROCESS.md. Reuse before spending; clean accepted parents, '
            'reviewed object-state/edit boundaries, exact local preservation outside edits. Three global attempts maximum; '
            'third requires changed-mechanism evidence. One live job and bounded spend window. '
            'Current measured layouts override provisional targets. Final chapter needs visual review and manual approval.')
    paths=list((ROOT/'story-and-continuity').rglob('*.md'))+list((ROOT/'story-and-continuity').rglob('*.txt'))
    paths += list((ROOT/'production').glob('chapter-*/START_HERE.txt'))
    for p in paths:
        if 'manuscript' in p.parts or any(part in ('revision-audit','delivery','runs','current') for part in p.parts): continue
        s=p.read_text()
        if 'WORKFLOW 8' in s or 'workflow 8' in s:
            s=re.sub(r'^WORKFLOW 8 EXECUTION:.*$',banner,s,flags=re.M)
            s=s.replace('WORKFLOW 8','WORKFLOW 9').replace('workflow 8','workflow 9')
            # The central process supersedes lower-level prose; don't silently reinterpret story text.
            if 'production/workflow-9/PROCESS.md' not in s:
                s='WORKFLOW 9 CONTROL AUTHORITY: production/workflow-9/PROCESS.md supersedes older retry/input mechanics below.\n\n'+s
            p.write_text(s)

    for filename in ('production/maintenance/build_reference_lineage.py',
                     'production/maintenance/update_lineage_instructions.py',
                     'production/agent-workflow/build_handoff.py'):
        p=ROOT/filename;s=p.read_text()
        marker='raise SystemExit("Retired workflow-8 writer: preserve current authored workflow-9 controls; do not rebuild from this historical script.")\n'
        if not s.startswith(marker):p.write_text(marker+s)
    print(json.dumps({'workflow_version':9,'nodes':len(cat['nodes']),'families':len(canaries),'requests':len(m['requests']),'chapters':len(m['chapters'])}))


if __name__ == '__main__':
    main()

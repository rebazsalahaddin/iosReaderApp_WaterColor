"""Validate handoff coverage and persistent execution/delivery gates, without MCP."""
from collections import Counter
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import zipfile
from PIL import Image, ImageChops
from guard import counted, internal, LIVE

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate():
    errors = []
    stats = Counter()
    def check(ok, message):
        if not ok:
            errors.append(message)
    def read(rel):
        return json.loads(internal(ROOT, rel).read_text())
    m = read('production/full-book-rebuild-r6/book-production-manifest.json')
    policy = read('production/agent-policy.json')
    state = read('production/agent-state.json')
    ledger = read('production/agent-ledger.json')
    check(policy['max_attempts_per_reference'] == 3 and policy['max_generation_rounds_per_page'] == 3,
          'Attempt/round policy changed')
    check(policy.get('visual_retry_requires_reviewed_graphics') is True
          and policy.get('visual_retry_protocol_version') == 3
          and internal(ROOT, policy.get('visual_correction_guide')).is_file(),
          'Mandatory graphical retry policy missing')
    check(policy['chapter_approval_required'] and not policy['cosmetic_regeneration']
          and not policy['whole_page_paid_generation'], 'Quality/approval/credit policy changed')
    check(policy['model'] == {'id': 'gpt_image_2_6_flare', 'resolution': '2k', 'quality': 'medium', 'aspect_ratio': '4:3', 'batch_size': 1, 'output_format': 'png', 'background': 'transparent'}, 'Model/settings drift')
    check(policy.get('expression_model') == dict(policy['model'], id='gpt_image_2_6'), 'Precision-edit model route drift')
    check(m['assistant_paid_generation_authorized'] and m.get('workflow_version') == 9,
          'Book manifest does not authorize the scoped MCP workflow')
    for rid, q in m['requests'].items():
        contract = read(q['folder'] + '/audit-contract.json')
        check(contract['request_id'] == rid and contract['max_attempts_total'] == 3, 'Request identity/cap: ' + rid)
        check(contract.get('visual_retry_requires_reviewed_graphics') is True
              and contract.get('visual_retry_protocol_version') == 3
              and contract.get('visual_correction_guide') == policy['visual_correction_guide'],
              'Missing graphical retry contract: ' + rid)
        check(contract['prompt_sha256'] == sha(ROOT / q['folder'] / 'PROMPT.txt'), 'Stale audit prompt: ' + rid)
        for ck, qk in [('expected_cells', 'cells'), ('required_state_direction_contact', 'details'),
                       ('references', 'attachments'), ('dependencies', 'dependencies'),
                       ('affected_pages', 'uses'), ('placement_targets', 'placement_targets')]:
            check(contract[ck] == q[qk], 'Stale specific source contract: ' + rid + ':' + ck)
        check(read(q['folder'] + '/request.json') == q, 'Request copy differs from book manifest: ' + rid)
        stats['source_audit_contracts'] += 1
    for n, chapter in m['chapters'].items():
        plan = read(f'production/chapter-{int(n):02}/agent-run-plan.json')
        check(plan['page_order'] == list(chapter['pages']) and plan['page_count'] == len(chapter['pages']), 'Run plan page coverage: ' + n)
        needed = {a.split(':')[0] for p in chapter['pages'].values() for a in p['assets']
                  if a.split(':')[0] in m['requests']}
        while True:
            expanded = needed | {d for rid in needed for d in m['requests'][rid]['dependencies']}
            if expanded == needed:
                break
            needed = expanded
        check(set(plan['dependency_order']) == needed, 'Over/under-scoped chapter requests: ' + n)
        seen = set()
        for rid in plan['dependency_order']:
            check(set(m['requests'][rid]['dependencies']) <= seen, 'Chapter dependency ordering: ' + n + ':' + rid)
            seen.add(rid)
        check(plan['manual_approval_required_after_delivery'], 'Missing chapter stop: ' + n)
        check(plan.get('visual_retry_requires_reviewed_graphics') is True
              and plan.get('visual_correction_guide') == policy['visual_correction_guide'],
              'Missing chapter graphical retry rule: ' + n)
        check(all(p['max_generation_rounds'] == 3 for p in plan['pages']), 'Missing page correction limit: ' + n)
        stats['chapter_run_plans'] += 1
        stats['covered_pages'] += len(chapter['pages'])
    # Active text must not give the former manual-only generation prohibition.
    obsolete = ['no paid retry or upscale by the agent', 'ready_for_manual_generation',
                'image generation itself remains manual', 'User manually generates in Higgsfield',
                'The user manually generates in Higgsfield', 'User performs generation.',
                'future generation remains manual', 'must not submit, retry, upscale, spend credits']
    for path in ROOT.rglob('*'):
        if not path.is_file() or path.suffix not in ['.txt', '.md', '.json'] or 'maintenance' in path.parts:
            continue
        text = path.read_text()
        check(not any(term in text for term in obsolete), 'Obsolete manual-only authority: ' + str(path.relative_to(ROOT)))
    attempts = Counter()
    job_ids = set()
    for job in ledger['jobs']:
        rid = job.get('request_id')
        check(rid in m['requests'], 'Noncanonical request ID in attempt ledger')
        if counted(job):
            attempts[rid] += 1
            check(job.get('attempt') == attempts[rid] <= 2, 'Attempt overflow/order: ' + str(rid))
        if job.get('job_id'):
            check(job['job_id'] not in job_ids, 'Duplicate job receipt counted twice')
            job_ids.add(job['job_id'])
        check(job.get('status') in LIVE | {'succeeded', 'failed', 'rejected_before_submission'}, 'Unknown job state')
        check(job.get('prompt_sha256') and job.get('parameters') and job.get('reserved_at'), 'Incomplete generation receipt')
        check(any(a.get('chapter') == job.get('chapter') and a.get('user_message')
                  for a in state['execution_authorizations']), 'Job has no recorded chapter authorization')
        if job.get('chapter'):
            plan = read(f"production/chapter-{job['chapter']:02}/agent-run-plan.json")
            check(rid in plan['dependency_order'], 'Job outside chapter dependency closure')
    check(sum(j.get('status') in LIVE for j in ledger['jobs']) <= 3, 'Concurrent-job cap exceeded')
    for rid, source in ledger['sources'].items():
        check(rid in m['requests'], 'Source registered under noncanonical request')
        if source.get('status') not in ['accepted', 'partially_accepted']:
            continue
        cells = source.get('accepted_cells', [])
        check(bool(cells), 'Accepted source has no accepted cells: ' + rid)
        expected_cells = {'ONE'} if len(m['requests'][rid]['cells']) == 1 else {'L', 'R'}
        check({c['cell'] for c in cells} <= expected_cells, 'Unknown accepted cell: ' + rid)
        if source.get('status') == 'accepted':
            check({c['cell'] for c in cells} == expected_cells, 'Full acceptance omits required cells: ' + rid)
        for cell in cells:
            raw = internal(ROOT, cell['source_file'])
            prepared = internal(ROOT, cell['prepared_file'])
            check(sha(raw) == cell['source_sha256'] and sha(prepared) == cell['prepared_sha256'],
                  'Accepted cell source/preparation hash changed: ' + rid)
            check(internal(ROOT, cell['preparation_record']).is_file(), 'Accepted cell lacks extraction measurements: ' + rid)
            audit = read(cell['audit_file'])
            check(audit.get('request_id') == rid and cell['cell'] in audit.get('accepted_cells', [])
                  and audit.get('source_sha256') == cell['source_sha256'] and not audit.get('template_only'),
                  'Cell is not covered by its source audit: ' + rid)
            check(audit.get('reviewer') and audit.get('reviewed_at'), 'Accepted source lacks visual reviewer/time: ' + rid)
            cell_audit = audit.get('cell_audits', {}).get(cell['cell'])
            check(cell_audit is not None, 'Accepted cell lacks its own visual audit: ' + rid + ':' + cell['cell'])
            for key in read('production/agent-workflow/templates/source-audit.json')['checks']:
                result = (cell_audit or {}).get('checks', {}).get(key, {})
                check(result.get('verdict') in ['PASS', 'PASS_WITH_NOTE'] and result.get('evidence'),
                      'Accepted source lacks visual evidence: ' + rid + ':' + key)
            check(not any(i.get('cell') == cell['cell'] and i.get('decision') in ['MATERIAL_FAIL', 'LOCAL_FIX', 'BLOCKED']
                          and not i.get('resolved') for i in audit.get('issues', [])), 'Accepted cell has unresolved defect: ' + rid)
    for pid, round_number in ledger['page_generation_rounds'].items():
        check(round_number in [1, 2], 'Page generation round overflow: ' + pid)
    active = state.get('active_chapter')
    if state['status'] == 'running':
        check(active in range(1, 28), 'Running state missing valid active chapter')
        check(any(a.get('chapter') == active and a.get('user_message') and a.get('recorded_at')
                  for a in state['execution_authorizations']), 'Missing start instruction')
        if active and active > 2:
            previous = state['chapter_runs'].get(str(active - 1), {})
            check(any(a.get('chapter') == active - 1 and a.get('continue_to_chapter') == active
                      and a.get('user_message') and a.get('approved_delivery_sha256')
                      and a['approved_delivery_sha256'] == previous.get('delivery_sha256')
                      for a in state['chapter_approvals']), 'Next chapter lacks manual approval of delivered edition')
    if state['status'] in ['handoff_ready_not_started', 'awaiting_chapter_approval']:
        check(active is None, 'Inactive approval/preparation state has active chapter')
        check(not any(j.get('status') in LIVE for j in ledger['jobs']), 'Jobs remain queued during required stop')
    # Future delivered chapters receive exact output, audit and archive validation.
    spec = importlib.util.spec_from_file_location('current_compositor', ROOT / 'production/compositor/compose_current.py')
    compositor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compositor)
    for n, run in state['chapter_runs'].items():
        if run.get('status') not in ['awaiting_chapter_approval', 'approved']:
            continue
        manifest = read(run['page_manifest'])
        expected = list(m['chapters'][n]['pages'])
        check([p['page'] for p in manifest['pages']] == expected, 'Delivered page coverage/order: ' + n)
        audits = [read(p) for p in run['page_audits']]
        check([a['page'] for a in audits] == expected, 'Individual page audits missing/out of order: ' + n)
        by_page = {a['page']: a for a in audits}
        archive = internal(ROOT, run['archive'])
        delivery = internal(ROOT, run['delivery'])
        check(sha(archive) == run['delivery_sha256'], 'Delivered archive hash mismatch: ' + n)
        check(sorted(p.name for p in delivery.parent.iterdir() if p.is_dir()) == [delivery.name], 'Multiple final editions: ' + n)
        check(list(delivery.parent.glob('*.zip')) == [archive], 'Multiple final archives: ' + n)
        with zipfile.ZipFile(archive) as z:
            check(z.testzip() is None, 'Archive CRC: ' + n)
            members = [v for v in z.namelist() if '/illustrations/' in v and v.endswith('.png')]
            check(len(members) == len(expected), 'Archive illustration count: ' + n)
            for row in manifest['pages']:
                pid = row['page']
                output = internal(ROOT, row['delivery_file'])
                audit = by_page.get(pid, {})
                check(sha(output) == row['delivery_sha256'] == audit.get('output_sha256'), 'Final/audit hash mismatch: ' + pid)
                check(audit.get('verdict') in ['PASS', 'PASS_WITH_NOTE'] and not audit.get('template_only'), 'Unreviewed page: ' + pid)
                check(audit.get('reviewer') and audit.get('reviewed_at'), 'Missing visual reviewer/time: ' + pid)
                required_checks = read('production/agent-workflow/templates/page-audit.json')['checks']
                for key in required_checks:
                    result = audit.get('checks', {}).get(key, {})
                    check(result.get('verdict') in ['PASS', 'PASS_WITH_NOTE'] and result.get('evidence'), 'Missing visual evidence: ' + pid + ':' + key)
                check(not any(i.get('decision') in ['MATERIAL_FAIL', 'LOCAL_FIX', 'BLOCKED'] and not i.get('resolved')
                              for i in audit.get('issues', [])), 'Unresolved page issue: ' + pid)
                im = Image.open(output)
                check(im.size == (2400, 1792) and im.mode == 'RGB' and im.format == 'PNG', 'Final format: ' + pid)
                layout = read(row['component_layout'])
                check(ImageChops.difference(compositor.reconstruct(layout), im).getbbox() is None, 'Reconstruction: ' + pid)
                key = delivery.name + '/illustrations/' + pid + '.png'
                check(hashlib.sha256(z.read(key)).hexdigest() == row['delivery_sha256'], 'ZIP pixels: ' + pid)
                stats['new_delivered_pages_verified'] += 1
    stats['counted_mcp_attempts'] = sum(attempts.values())
    report = {'status': 'fail' if errors else 'pass', 'workflow_version': 9,
              'checks': dict(stats), 'errors': errors,
              'scope': 'Handoff coverage, policy and recorded execution gates. Visual truth and genuine user approval require actual inspection/conversation evidence.'}
    (ROOT / 'production/agent-workflow/validation-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    try:
        result = validate()
    except (KeyError, OSError, ValueError, TypeError) as exc:
        result = {'status': 'fail', 'errors': ['Invalid/missing execution record: ' + str(exc)]}
    print(json.dumps(result, indent=2))
    raise SystemExit(result['status'] != 'pass')

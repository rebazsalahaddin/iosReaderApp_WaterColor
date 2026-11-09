"""Validate the prompt graph and inactive execution gates; never render or submit images."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'production/agent-workflow'))
from lineage_guard import evaluate, inherited_jobs, internal


def validate():
    errors = []
    stats = Counter()

    def check(value, message):
        if not value:
            errors.append(message)

    def read(rel):
        return json.loads(internal(ROOT, rel).read_text())

    catalog = read('production/reference-lineage/catalog.json')
    manifest = read('production/full-book-rebuild-r6/book-production-manifest.json')
    nodes = catalog['nodes']
    locked = dict(model='gpt_image_2_6_flare', quality='medium', resolution='2k',
                  aspect_ratio='4:3', batch_size=1, output_format='png', background='transparent')
    check(catalog['workflow_version'] == 9 and catalog['model'] == locked, 'Catalog model/workflow drift')
    check(catalog.get('expression_model') == dict(locked, model='gpt_image_2_6'), 'Precision-edit model route drift')
    check(len(catalog['dependency_order']) == len(nodes)
          and set(catalog['dependency_order']) == set(nodes), 'Duplicate or missing ordered node')
    seen = set()
    for nid in catalog['dependency_order']:
        node = nodes[nid]
        check(node['id'] == nid and set(node['parents']) <= seen, 'Parent ordering/cycle: ' + nid)
        seen.add(nid)
        expected = dict(locked)
        if node['stage'] == 'expression_variant':
            expected['model'] = 'gpt_image_2_6'
        if node['stage'] == 'background_plate':
            expected['background'] = 'opaque'
        check(node['parameters'] == expected, 'Wrong node output settings: ' + nid)
        check(node['max_attempts_total'] == 3 and node['reuse_first'], 'Reuse/attempt limit missing: ' + nid)
        prompt_file = internal(ROOT, node['prompt_file'])
        check(prompt_file.read_text() == node['prompt'], 'Prompt/catalog mismatch: ' + nid)
        check(hashlib.sha256(prompt_file.read_bytes()).hexdigest() == node['prompt_sha256'], 'Prompt hash mismatch: ' + nid)
        check(read(str(prompt_file.with_name('node.json').relative_to(ROOT))) == node, 'Node copy differs: ' + nid)
        check(len(node['prompt'].split()) <= 300, 'Long model payload: ' + nid)
        inputs = node['input_contract']
        if node['stage'] == 'expression_variant':
            check(len(node['parents']) == 1 and nodes[node['parents'][0]]['stage'] == 'neutral_posture', 'Expression not from one neutral: ' + nid)
            check(inputs.get('exact_images') == 1 and inputs.get('sole_appearance_authority') == node['parents'][0], 'Wrong sole authority: ' + nid)
            check('expression_variant' in inputs.get('forbidden_parents', []), 'Expression chaining not forbidden: ' + nid)
            check(node['shadow_mode'] == 'preserve_parent' and all(t in node['prompt'] for t in ['shadow visually unchanged', 'dot', 'identity', 'camera', 'registration']), 'Variant protection missing: ' + nid)
        if node['stage'] == 'neutral_posture':
            check(all(nodes[p]['stage'] == 'identity_turnaround' for p in node['parents']), 'Neutral has nonidentity parent: ' + nid)
            check(1 <= inputs.get('max_images', 0) <= 3 and inputs.get('no_style_bundle'), 'Foundation bundle limit: ' + nid)
            check(inputs.get('required_identity_parents') == node['parents'], 'Foundation identity contract: ' + nid)
        if node['stage'] == 'local_assembly':
            check(inputs.get('submission_forbidden') and inputs.get('max_images') == 0, 'Local assembly exposed as a paid job: ' + nid)
            check('DO NOT SUBMIT' in node['prompt'] and node['shadow_mode'] == 'none_editorial', 'Editorial crop instructions incomplete: ' + nid)
        stats[node['stage']] += 1

    all_pages = {pid: page for chapter in manifest['chapters'].values() for pid, page in chapter['pages'].items()}
    check(set(catalog['page_asset_routes']) == set(all_pages) and len(all_pages) == 442, 'Page route coverage')
    for rid, request in manifest['requests'].items():
        cells = ['ONE'] if len(request['cells']) == 1 else ['L', 'R']
        check(request.get('generation_route') == 'lineage_nodes_only'
              and request.get('attachment_usage') == 'offline_audit_only_not_submission_manifest', 'Legacy bundle still executable: ' + rid)
        for cell in cells:
            nid = request['lineage_nodes'][cell]
            check(catalog['legacy_asset_routes'].get(rid + ':' + cell) == nid, 'Legacy mapping differs: ' + rid)
            check(nodes[nid].get('legacy_request') == rid and nodes[nid].get('legacy_cell') == cell, 'Lost attempt bridge: ' + nid)
    for number, chapter in manifest['chapters'].items():
        plan = read(f'production/chapter-{int(number):02}/agent-run-plan.json')
        needed = set()

        def include(nid):
            if nid in needed:
                return
            needed.add(nid)
            for parent in nodes[nid]['parents']:
                include(parent)

        for pid, page in chapter['pages'].items():
            routes = catalog['page_asset_routes'][pid]
            expected_tokens = {token for token in page['assets'] if token in catalog['legacy_asset_routes']}
            check(set(routes) == expected_tokens, 'Missing/extraneous page source: ' + pid)
            check(page.get('reference_lineage') == routes, 'Manifest routes differ: ' + pid)
            layout = read(page['layout'])
            check(layout.get('reference_lineage', {}).get('asset_nodes') == routes, 'Layout routes differ: ' + pid)
            check(layout['source_text'] == page['source_text'] if 'source_text' in layout else True, 'Story changed: ' + pid)
            text = internal(ROOT, page['assembly_instructions']).read_text()
            check('WORKFLOW 7 EXECUTION' not in text and 'Add one restrained local grounding shadow' not in text, 'Obsolete page procedure: ' + pid)
            for nid in routes.values():
                check(nid in nodes and pid in nodes[nid].get('affected_pages', []), 'Node use missing: ' + pid + ':' + nid)
                include(nid)
        check(plan['lineage_execution_order'] == [nid for nid in catalog['dependency_order'] if nid in needed], 'Chapter lineage closure/order: ' + number)
        check(plan.get('generation_route') == 'lineage_nodes_only' and plan['manual_approval_required_after_delivery'], 'Chapter execution route/stop: ' + number)
        for page in plan['pages']:
            check(page['reference_lineage'] == catalog['page_asset_routes'][page['page']], 'Stale run-plan page mapping: ' + page['page'])
    child_parent = 'N_child_table__soft_day_upper_left'
    for nid in ['V_CH01_S10_ONE', 'V_CH01_CHILD_IMAGINING', 'V_CH01_S11_ONE', 'V_CH01_S15_ONE', 'V_CH01_S16_ONE']:
        check(nodes[nid]['parents'] == [child_parent], 'Child table expressions diverge: ' + nid)
    check(catalog['page_asset_routes']['c01-s01-p03']['CH01_S10:ONE'] == 'V_CH01_CHILD_IMAGINING', 'Imagining repeats reading state')

    # Exercise rejection boundaries in memory, with real plans and no fake image acceptance.
    state = read('production/agent-state.json')
    ledger = read('production/reference-lineage/ledger.json')
    legacy = read('production/agent-ledger.json')
    nid = 'V_CH02_S02_L'
    if state.get('status') != 'running':
        check(any('No active chapter' in e for e in evaluate(ROOT, state, ledger, 2, nid, legacy)), 'Maintenance can execute')
        stats['guard_rejection_checks'] += 1
    scenarios = [
        ('inherited three-attempt cap', {'jobs': [{'request_id': 'CH02_S02', 'status': 'succeeded'}, {'request_id': 'CH02_S02', 'status': 'failed'}, {'request_id': 'CH02_S02', 'status': 'failed'}]}, 'Three-attempt limit'),
        ('unknown submission', {'jobs': [{'request_id': 'CH02_S02', 'status': 'submission_unknown'}]}, 'live/unknown/reserved'),
        ('global concurrency cap', {'jobs': [{'request_id': 'OTHER', 'status': 'running'}]}, 'One-job concurrency'),
    ]
    for label, fixture, message in scenarios:
        found = evaluate(ROOT, state, ledger, 2, nid, fixture)
        check(any(message in e for e in found), 'Guard failed: ' + label)
        stats['guard_rejection_checks'] += 1
    check(bool(evaluate(ROOT, state, ledger, 2, 'CH02_S02', legacy)), 'Old request card can bypass lineage')
    stats['guard_rejection_checks'] += 1
    check(len(inherited_jobs(nodes['V_CH02_S02_L'], legacy)) == len(inherited_jobs(nodes['V_CH02_S02_R'], legacy)), 'Old sheet count not inherited by both cells')
    report = dict(status='fail' if errors else 'pass', workflow_version=9, chapters=len(manifest['chapters']),
                  page_routes=len(all_pages), legacy_requests=len(manifest['requests']), logical_states=len(catalog['legacy_asset_routes']),
                  checks=dict(stats), errors=errors,
                  scope='Prompt graph, chapter closure and read-only rejection checks. No jobs, rendering or visual approval.')
    (ROOT / 'production/reference-lineage/validation-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(validate())

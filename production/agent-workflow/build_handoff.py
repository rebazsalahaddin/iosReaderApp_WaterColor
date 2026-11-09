raise SystemExit("Retired workflow-8 writer: preserve current authored workflow-9 controls; do not rebuild from this historical script.")
"""Derive chapter-scoped run plans and source audit contracts; never generate art."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'production/full-book-rebuild-r6/book-production-manifest.json'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def closure(requests, initial):
    result = set()
    def add(rid):
        if rid in result:
            return
        result.add(rid)
        for dependency in requests[rid]['dependencies']:
            add(dependency)
    for rid in initial:
        add(rid)
    return result


def main():
    m = json.loads(MANIFEST.read_text())
    requests = m['requests']
    catalog = json.loads((ROOT / 'production/reference-lineage/catalog.json').read_text())
    for rid, q in requests.items():
        contract = {
            'workflow_version': 8, 'request_id': rid,
            'prompt_file': q['folder'] + '/PROMPT.txt',
            'prompt_sha256': hashlib.sha256(q['prompt'].encode()).hexdigest(),
            'expected_cells': q['cells'], 'required_state_direction_contact': q['details'],
            'isolation_key': q['key'], 'light': q['light'],
            'dependencies': q['dependencies'],
            'references': q['attachments'], 'attachment_usage': 'offline_audit_only_not_submission_manifest',
            'lineage_nodes': q['lineage_nodes'], 'generation_route': 'lineage_nodes_only', 'affected_pages': q['uses'],
            'placement_targets': q['placement_targets'],
            'audit_guide': 'production/Visual_Audit_and_Retry.md',
            'visual_correction_guide': 'production/Visual_Correction_Guide.txt',
            'visual_retry_protocol_version': 2,
            'visual_retry_requires_reviewed_graphics': True,
            'geometry_guide': 'production/Geometry_and_Frame_Continuity.md',
            'composition_performance_guide': 'production/Composition_Continuity_and_Performance.md',
            'required_placement_evidence': ['two measured comparable native landmarks and uniform scale', 'relative anatomy/prop ratios at shared depth', 'stationary support and background anchor comparison', 'actual bearing-edge shadow attachment', 'reading-size face/gaze/gesture toward recipient', 'meaningful unique page and coherent camera', 'three owner-linked thought puffs where selected'],
            'text_alignment_guide': 'production/Text_to_Illustration_Alignment.md',
            'story_context': q['folder'] + '/story-context.json',
            'max_attempts_total': 2,
            'required_evidence': ['actual cell bounds and full source dimensions',
                'identity/style compared offline with canonical turnaround; single neutral parent for variants',
                'independent body/feet/chair/head/gaze and expression checks',
                'counts, states, contacts, native pixels and proposed uniform scale',
                'extraction on diagnostic and intended backgrounds',
                'reading-size and native-size verdicts with concrete observations'],
            'retry_gate': 'Material source defect only. Two attempts INCLUDING historical sheet submissions for each derived cell. Before attempt two prepare ONE reviewed local board: dominant intact neutral authority plus every issue diagnostic and positive target. Upload that board alone for variant retry, preserve full original short prompt and exact fixes, then recheck all issues and passing features. No third attempt.',
        }
        write(ROOT / q['folder'] / 'audit-contract.json', contract)
    for n, chapter in m['chapters'].items():
        number = int(n)
        direct = {token.split(':')[0] for p in chapter['pages'].values()
                  for token in p['assets'] if token.split(':')[0] in requests}
        required = closure(requests, direct)
        order = [rid for rid in m['dependency_order'] if rid in required]
        assert set(order) == required
        plan = {
            'workflow_version': 8, 'chapter': number, 'title': chapter['title'],
            'page_count': len(chapter['pages']), 'page_order': list(chapter['pages']),
            'status': 'plan_only_check_current_overlays_and_accepted_sources',
            'chapter_notes': chapter['notes'],
            'manual_approval_required_after_delivery': True,
            'composition_performance_guide': 'production/Composition_Continuity_and_Performance.md',
            'scale_and_anchor_registry_required_before_composition': True,
            'decoded_pixel_and_semantic_duplicate_checks_required': True,
            'visual_correction_guide': 'production/Visual_Correction_Guide.txt',
            'visual_retry_requires_reviewed_graphics': True,
            'direct_source_requests': sorted(direct),
            'dependency_order': order,
            'later_owned_required_sources': [rid for rid in order if requests[rid]['chapter'] > number],
            'possible_initial_jobs_before_reuse': len(order),
            'max_total_submissions_if_all_sources_were_new': len(order) * 2,
            'budget_note': 'Upper bounds, not a spending target or permission. Deduct accepted sources and global attempts already used. Quote live costs; correct only material failures.',
            'generation_requests': [{
                'request_id': rid, 'owner_chapter': requests[rid]['chapter'],
                'prompt_file': requests[rid]['folder'] + '/PROMPT.txt',
                'audit_contract': requests[rid]['folder'] + '/audit-contract.json',
                'dependencies': requests[rid]['dependencies'],
                'active_page_uses': [pid for pid in requests[rid]['uses'] if pid in chapter['pages']],
                'dependency_only': rid not in direct,
            } for rid in order],
            'pages': [{
                'page': pid, 'assets': page['assets'], 'story_text': page['source_text'],
                'assembly_instructions': page['assembly_instructions'],
                'layout': page['layout'], 'placement_guide': page['placement_guide'],
                'max_generation_rounds': 2,
                'geometry_contract': page['layout'],
                'text_alignment_contract': page['layout'],
            } for pid, page in chapter['pages'].items()],
            'policy': 'production/agent-policy.json',
            'audit_template': 'production/agent-workflow/templates/page-audit.json',
        }
        direct_nodes = {nid for mapping in catalog['page_asset_routes'].items() if mapping[0] in chapter['pages'] for nid in mapping[1].values()}
        required_nodes = set()
        def add_node(nid):
            if nid in required_nodes: return
            required_nodes.add(nid)
            for parent in catalog['nodes'][nid]['parents']: add_node(parent)
        for nid in direct_nodes: add_node(nid)
        plan['lineage_execution_order'] = [nid for nid in catalog['dependency_order'] if nid in required_nodes]
        plan['generation_route'] = 'lineage_nodes_only'
        plan['legacy_dependency_usage'] = 'offline_audit_and_historical_attempt_traceability'
        plan['lineage_catalog'] = 'production/reference-lineage/catalog.json'
        plan['possible_initial_jobs_before_reuse'] = sum(catalog['nodes'][nid]['stage'] != 'local_assembly' for nid in required_nodes)
        plan['max_total_submissions_if_all_sources_were_new'] = 2 * plan['possible_initial_jobs_before_reuse']
        plan['budget_note'] = 'Ceiling only, never a spending target. Audit/reuse existing identities, neutral masters and variants first; subtract all historical and lineage attempts. Generate only the active chapter missing states after live estimate and guard.'
        for page in plan['pages']:
            page['reference_lineage'] = catalog['page_asset_routes'][page['page']]
        write(ROOT / f'production/chapter-{number:02}/agent-run-plan.json', plan)
    print(f'Updated 27 chapter dependency plans and {len(requests)} exact source audit contracts. No generation jobs submitted.')


if __name__ == '__main__':
    main()

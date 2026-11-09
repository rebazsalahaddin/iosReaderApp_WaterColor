"""Check active workflow controls and unchanged historical art; never approve visuals."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent.parent


def main():
    errors = []
    def read(p):
        return json.loads((ROOT/p).read_text())
    def check(ok, message):
        if not ok:
            errors.append(message)
    policy = read('production/agent-policy.json')
    check(policy.get('workflow_version') == 9, 'Wrong active workflow')
    check(policy.get('max_attempts_per_reference') == 3 and policy.get('max_concurrent_jobs') == 1, 'Attempt/concurrency drift')
    for key in ('third_attempt_requires_changed_mechanism', 'spend_window_required', 'chapter_credit_budget_required', 'edit_plan_required', 'family_canary_required'):
        check(policy.get(key) is True, 'Missing policy gate: ' + key)
    cat = read('production/reference-lineage/catalog.json')
    for p in (ROOT/'production').glob('chapter-*/agent-run-plan.json'):
        plan = json.loads(p.read_text())
        for parent, node in plan.get('family_canaries', {}).items():
            check(node in plan['lineage_execution_order'] and cat['nodes'][node]['parents'] == [parent], 'Unreachable/wrong canary: ' + str(p.relative_to(ROOT)))
        used = {cat['nodes'][n]['parents'][0] for n in plan['lineage_execution_order'] if cat['nodes'][n]['stage'] == 'expression_variant'}
        check(used == set(plan.get('family_canaries', {})), 'Missing family canary in active chapter plan')
    protected = read('production/workflow-9/protected-files-before.json')
    removal_path = ROOT/'production/workflow-9/authorized-removal-inventory.json'
    removal = json.loads(removal_path.read_text()) if removal_path.exists() else {}
    retired = {x['path']: x['sha256'] for x in removal.get('files', [])} if removal.get('status') == 'completed' else {}
    active_state_files = {
        'production/agent-ledger.json',
        'production/agent-state.json',
        'production/chapter-01/current-progress.json',
        'production/chapter-02/current-progress.json',
        'production/reference-lineage/ledger.json',
    }
    check(len(read('production/agent-ledger.json').get('jobs', [])) >= 20, 'Historical legacy jobs removed')
    check(len(read('production/reference-lineage/ledger.json').get('jobs', [])) >= 7, 'Historical lineage jobs removed')
    for name, digest in protected.items():
        p = ROOT/name
        if name in active_state_files:
            check(p.is_file(), 'Missing active state/ledger file: ' + name)
        elif name in retired:
            check(retired[name] == digest, 'Authorized removal record mismatch: ' + name)
            if name.startswith(('production/chapter-01/current/', 'production/chapter-01/audits/pages/')) and p.exists():
                check(hashlib.sha256(p.read_bytes()).hexdigest() != digest, 'Retired v010 file retained unchanged: ' + name)
            else:
                check(not p.exists(), 'Authorized removal record mismatch: ' + name)
        else:
            check(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == digest, 'Protected art/history changed: ' + name)
    paths = list((ROOT/'story-and-continuity').rglob('*.md')) + list((ROOT/'story-and-continuity').rglob('*.txt'))
    paths += list((ROOT/'production').glob('chapter-*/START_HERE.txt'))
    paths += [ROOT/'production'/p for p in ('Execution_Instructions.md', 'Composition_Continuity_and_Performance.md', 'Background_Removal_Instructions.md')]
    obsolete = re.compile(r'two.attempt|two attempts|No third attempt|upload only the reviewed board|Upload that board alone|full original short prompt', re.I)
    for p in paths:
        if 'manuscript' in p.parts or 'revision-audit' in p.parts:
            continue
        check(not obsolete.search(p.read_text()), 'Conflicting active instruction: ' + str(p.relative_to(ROOT)))
    for name in ('production/maintenance/build_reference_lineage.py', 'production/maintenance/update_lineage_instructions.py', 'production/agent-workflow/build_handoff.py'):
        check((ROOT/name).read_text().startswith('raise SystemExit("Retired workflow-8 writer:'), 'Obsolete writer not retired: ' + name)
    imagining = cat['nodes']['V_CH01_CHILD_IMAGINING']['prompt']
    check('remove the old closed instance' in imagining and 'Exactly ONE blue book' in imagining, 'Duplicate-book prevention missing')
    report = {'status': 'fail' if errors else 'pass', 'workflow_version': 9, 'protected_files_unchanged': len(protected)-len(set(protected)&set(retired)), 'authorized_removed_protected_files': len(set(protected)&set(retired)),
              'active_instruction_files_checked': len(paths), 'errors': errors,
              'scope': 'Control consistency and byte preservation only; no generated illustration or visual approval.'}
    (ROOT/'production/workflow-9/validation-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())

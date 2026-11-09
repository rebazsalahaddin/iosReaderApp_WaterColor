"""Read-only pre-submission guard. It does not call MCP or grant user approval."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
LOCKED = {'model': 'gpt_image_2_6_flare', 'resolution': '2k', 'quality': 'medium', 'aspect_ratio': '4:3', 'batch_size': 1, 'output_format': 'png', 'background': 'transparent'}
LIVE = {'reserved', 'submission_unknown', 'submitted', 'running'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def internal(root, value):
    if not isinstance(value, str) or Path(value).is_absolute():
        raise ValueError('Expected a root-relative file')
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('File escapes project root')
    return path


def counted(job):
    # A proven rejection before any submission may release its reservation.
    return not (job.get('status') == 'rejected_before_submission'
                and job.get('no_job_no_charge_receipt') and not job.get('job_id'))


def evaluate(root, state, ledger, chapter, rid):
    # Retained CLI compatibility. Legacy multi-reference cards cannot bypass v8.
    from lineage_guard import evaluate as evaluate_lineage
    lineage = json.loads((root / 'production/reference-lineage/ledger.json').read_text())
    return evaluate_lineage(root, state, lineage, chapter, rid, legacy=ledger)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chapter', type=int, required=True)
    parser.add_argument('--request', required=True)
    args = parser.parse_args()
    state = json.loads((ROOT / 'production/agent-state.json').read_text())
    ledger = json.loads((ROOT / 'production/agent-ledger.json').read_text())
    errors = evaluate(ROOT, state, ledger, args.chapter, args.request)
    print(json.dumps({'allowed': not errors, 'errors': errors,
                      'note': 'Read-only check; reserve the attempt before MCP submission. A pass is not an art approval.'}, indent=2))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()

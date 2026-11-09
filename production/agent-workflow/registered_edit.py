"""Build an unapproved same-parent candidate with exact pixels outside a binary mask.

No warping, feathering, source-over blending, automatic mask inference or acceptance.
Only --output writes a new candidate; the default checks a prepared integration record.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image
from workflow9_checks import safe_file, mask_arrays, review_ok, finite_cost

ROOT = Path(__file__).resolve().parents[2]


def replace_region(parent, candidate, edit, support):
    if parent.shape != candidate.shape or parent.ndim != 3 or parent.shape[2] != 4:
        raise ValueError('Parent/candidate must be same-size RGBA; register separately first')
    if edit.shape != parent.shape[:2] or support.shape != edit.shape or edit.dtype != bool or support.dtype != bool:
        raise ValueError('Masks must be matching binary arrays')
    if not edit.any() or edit.all() or np.any(edit & support):
        raise ValueError('Empty/full edit or protected-support overlap')
    result = parent.copy()
    result[edit] = candidate[edit]
    if not np.array_equal(result[~edit], parent[~edit]) or not np.array_equal(result[support], parent[support]):
        raise AssertionError('Protected pixels changed')
    return result


def inspect(root, record):
    if record.get('template_only') is True:
        raise ValueError('Uncompleted integration template')
    plan_path = safe_file(root, record.get('frozen_edit_plan'))
    plan = json.loads(plan_path.read_text())
    if plan.get('workflow_version') != 9 or plan.get('route') != 'registered_edit':
        raise ValueError('Integration needs a frozen workflow-9 registered-edit plan')
    if not review_ok(plan.get('review')):
        raise ValueError('Frozen plan was not reviewed')
    for key in ('edit_mask', 'support_mask'):
        if record.get(key) != plan.get(key):
            raise ValueError('Cannot expand/change a frozen mask after generation')
    if not any(p.get('path') == record.get('parent', {}).get('path') and p.get('sha256') == record.get('parent', {}).get('sha256') for p in plan.get('parents', [])):
        raise ValueError('Integration parent differs from frozen plan')
    if not review_ok(record.get('integration_review')):
        raise ValueError('Needs actual registration/contact/seam/occlusion review')
    checks = record.get('checks', {})
    for k in ('same_parent', 'identity', 'connected_contacts', 'object_inventory', 'boundary_seams', 'actual_background', 'reading_size'):
        if checks.get(k, {}).get('verdict') not in ('PASS', 'PASS_WITH_NOTE') or not checks[k].get('evidence'):
            raise ValueError('Missing integration check: ' + k)
    parent_path = safe_file(root, record.get('parent'))
    candidate_path = safe_file(root, record.get('candidate'))
    edit_path = safe_file(root, record.get('edit_mask'))
    support_path = safe_file(root, record.get('support_mask'))
    edit, support = mask_arrays(parent_path, edit_path, support_path)
    with Image.open(parent_path) as im:
        parent = np.array(im)
    with Image.open(candidate_path) as im:
        if im.mode != 'RGBA':
            raise ValueError('Candidate must retain native alpha')
        candidate = np.array(im)
    registration = record.get('registration', {})
    points = registration.get('landmarks', [])
    planned = plan.get('registration', {})
    if ([p.get('parent_xy') for p in points] != [p.get('parent_xy') for p in planned.get('landmarks', [])]
            or registration.get('max_residual_native_px') != planned.get('max_residual_native_px')):
        raise ValueError('Registration anchors/tolerance differ from frozen plan')
    if len(points) < 3:
        raise ValueError('Need three measured unchanged landmarks')
    src = np.array([p['parent_xy'] for p in points], dtype=float)
    dst = np.array([p['candidate_xy'] for p in points], dtype=float)
    if src.shape != dst.shape or src.shape[1:] != (2,) or not np.isfinite(src).all() or not np.isfinite(dst).all() or np.linalg.matrix_rank(src-src[0]) != 2:
        raise ValueError('Invalid/non-independent registration landmarks')
    residual = float(np.max(np.linalg.norm(src-dst, axis=1)))
    tolerance = registration.get('max_residual_native_px')
    if not finite_cost(tolerance) or tolerance <= 0 or residual > tolerance:
        raise ValueError('Registration residual exceeds reviewed tolerance')
    output = replace_region(parent, candidate, edit, support)
    report = {'status': 'candidate_only_not_visual_acceptance', 'dimensions': [parent.shape[1], parent.shape[0]],
              'edit_pixels': int(edit.sum()), 'protected_pixels': int((~edit).sum()),
              'protected_pixels_exact': bool(np.array_equal(output[~edit], parent[~edit])),
              'support_pixels_exact': bool(np.array_equal(output[support], parent[support])),
              'max_registration_residual_native_px': residual}
    return output, report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record', required=True, help='Root-relative hash-bound integration record')
    p.add_argument('--output', help='Optional NEW root-relative candidate PNG, never a delivery')
    args = p.parse_args()
    rp = (ROOT/args.record).resolve()
    if Path(args.record).is_absolute() or not rp.is_relative_to(ROOT):
        raise ValueError('Record must be root-relative')
    result, report = inspect(ROOT, json.loads(rp.read_text()))
    if args.output:
        out = (ROOT/args.output).resolve()
        if Path(args.output).is_absolute() or not out.is_relative_to(ROOT) or any(p in out.parts for p in ('delivery', 'current', 'sources')) or out.suffix.lower() != '.png':
            raise ValueError('Write only a new candidate PNG outside originals/current/delivery')
        if out.exists() or out.with_suffix('.json').exists():
            raise ValueError('Refuse overwrite')
        out.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation also protects against a concurrent writer.
        with out.open('xb') as handle:
            Image.fromarray(result, 'RGBA').save(handle, format='PNG')
        report.update(output=args.output, output_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                      integration_record=args.record, record_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
        with out.with_suffix('.json').open('x') as handle:
            json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

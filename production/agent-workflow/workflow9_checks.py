"""Fail-closed preparation checks. No MCP, reservation, image edits or approval."""
from pathlib import Path
import hashlib
import json
import math
from PIL import Image
import numpy as np


def finite_cost(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def safe_file(root, binding):
    value = binding.get('path') if isinstance(binding, dict) else None
    if not isinstance(value, str) or Path(value).is_absolute():
        raise ValueError('Expected root-relative bound file')
    p = (root / value).resolve()
    if not p.is_relative_to(root.resolve()) or not p.is_file():
        raise ValueError('Bound file missing or outside root')
    if hashlib.sha256(p.read_bytes()).hexdigest() != binding.get('sha256'):
        raise ValueError('Bound file hash mismatch: ' + value)
    return p


def safe_source_or_retired(root, binding):
    value = binding.get('path') if isinstance(binding, dict) else None
    if isinstance(value, str) and not Path(value).is_absolute():
        p = (root / value).resolve()
        if p.is_relative_to(root.resolve()) and not p.is_file():
            inv = root / 'production/workflow-9/authorized-removal-inventory.json'
            if inv.is_file():
                data = json.loads(inv.read_text())
                if data.get('status') == 'completed':
                    retired = {x.get('path'): x.get('sha256') for x in data.get('files', [])}
                    if value in retired and retired[value] == binding.get('sha256'):
                        return p
    return safe_file(root, binding)


def review_ok(value):
    return isinstance(value, dict) and value.get('status') == 'reviewed' and all(
        value.get(k) for k in ('reviewer', 'reviewed_at', 'observations'))


def mask_arrays(parent_path, edit_path, support_path):
    with Image.open(parent_path) as im:
        if im.mode != 'RGBA':
            raise ValueError('Registered parent must be native RGBA')
        size = im.size
    masks = []
    for p in (edit_path, support_path):
        with Image.open(p) as im:
            if im.mode != 'L' or im.size != size:
                raise ValueError('Masks must be native-size grayscale L')
            arr = np.array(im)
        if not np.isin(arr, [0, 255]).all():
            raise ValueError('Masks must be binary 0/255; no implicit feather')
        masks.append(arr == 255)
    edit, support = masks
    if not edit.any() or edit.all():
        raise ValueError('Edit mask must change a proper subset of the canvas')
    if np.any(edit & support):
        raise ValueError('Edit mask overlaps protected support/shadow')
    return edit, support


def budget_errors(window, jobs, node_id, estimate):
    errors = []
    if not isinstance(window, dict) or not all(window.get(k) for k in ('id', 'opened_at', 'node_ids')):
        return ['Missing bounded spend window']
    if node_id not in window['node_ids']:
        errors.append('Node outside spend window')
    ceiling = window.get('max_credits')
    if not finite_cost(ceiling) or ceiling <= 0 or not finite_cost(estimate):
        return errors + ['Invalid/missing finite credit ceiling or quote']
    spent = 0
    for j in jobs:
        if j.get('spend_window_id') != window['id']:
            continue
        if j.get('status') == 'rejected_before_submission' and j.get('no_job_no_charge_receipt') and not j.get('job_id'):
            continue
        value = j.get('actual_credits') if j.get('actual_credits') is not None else j.get('estimated_credits')
        if not finite_cost(value):
            errors.append('Unknown/invalid cost in spend window')
        else:
            spent += value
    if spent + estimate > ceiling:
        errors.append('Spend window credit ceiling exceeded')
    return errors


def plan_errors(root, plan, node, parents):
    errors = []
    def check(ok, msg):
        if not ok:
            errors.append(msg)
    check(plan.get('workflow_version') == 9 and plan.get('node_id') == node['id'], 'Wrong workflow/node in edit plan')
    check(plan.get('template_only') is not True, 'Uncompleted template is not an edit plan')
    check(plan.get('parents') == parents, 'Edit plan parent hashes differ')
    check(review_ok(plan.get('review')), 'Edit plan needs actual visual review')
    route = plan.get('route')
    check(route in ('registered_edit', 'whole_contact_candidate', 'identity', 'asset', 'background'), 'Invalid paid route')
    check(bool(plan.get('target_state')) and bool(plan.get('submission_contract')), 'Missing explicit target/submission contract')
    check(bool(plan.get('identity_features')) and bool(plan.get('geometry_checks')), 'Missing identity/geometry checks')
    for k in ('contacts', 'background_review', 'pixel_budget', 'reuse_decision', 'local_repair_decision'):
        check(bool(plan.get(k)), 'Missing measured plan: ' + k)
    inventory = plan.get('object_inventory', [])
    check(isinstance(inventory, list) and bool(inventory), 'Missing object-state inventory (explicit none row allowed)')
    for item in inventory:
        check(all(item.get(k) is not None for k in ('id', 'before_count', 'after_count', 'before_state', 'after_state', 'contact')), 'Incomplete object state')
        check(all(type(item.get(k)) is int and item[k] >= 0 for k in ('before_count', 'after_count')), 'Invalid object count')
        if item.get('replaces_or_moves'):
            check(all(item.get(k) for k in ('old_bbox_xywh', 'new_bbox_xywh', 'vacated_surface')), 'Replacement omits old footprint / vacated surface')
    if node['stage'] == 'expression_variant':
        check(route in ('registered_edit', 'whole_contact_candidate'), 'Variant requires explicit integration route')
    if route == 'registered_edit':
        check(len(parents) == 1, 'Registered edit needs one complete accepted base')
        try:
            parent_path = safe_file(root, parents[0])
            mask_arrays(parent_path, safe_file(root, plan.get('edit_mask')), safe_file(root, plan.get('support_mask')))
        except (ValueError, OSError, TypeError, IndexError) as e:
            errors.append(str(e))
        landmarks = plan.get('registration', {}).get('landmarks', [])
        check(len(landmarks) >= 3, 'Need three stable registration landmarks')
        if len(landmarks) >= 3:
            try:
                points = np.array([p['parent_xy'] for p in landmarks], dtype=float)
                check(points.shape[1:] == (2,) and np.isfinite(points).all() and np.linalg.matrix_rank(points - points[0]) == 2, 'Landmarks must be finite and noncollinear')
            except (KeyError, TypeError, ValueError):
                errors.append('Malformed landmarks')
        tolerance = plan.get('registration', {}).get('max_residual_native_px')
        check(finite_cost(tolerance) and tolerance > 0, 'Missing registration tolerance')
        check(plan.get('boundary_and_occlusion_review'), 'Missing connected-boundary/occlusion plan')
        check(plan.get('protected_pixels_method') == 'copy_parent_outside_binary_mask', 'Exact preservation must be local')
    if route == 'whole_contact_candidate':
        check(plan.get('why_registered_edit_not_feasible') and plan.get('all_features_reaudit') is True, 'Whole-contact route must acknowledge full re-audit')
    return errors


def retry_errors(root, pf, audit, jobs, parents, prompt):
    errors = []
    if not jobs:
        return errors
    issues = [i for i in audit.get('issues', []) if i.get('decision') == 'MATERIAL_FAIL' and not i.get('resolved')]
    technical = (audit.get('verdict') == 'TECHNICAL_FAIL' and audit.get('confirmed_error')
                 and audit.get('resolved_technical_cause') and not audit.get('source_file')
                 and jobs[-1].get('status') == 'failed' and not jobs[-1].get('original_file'))
    if not issues and not technical:
        errors.append('No evidenced material failure or resolved technical cause')
    retry = pf.get('retry_plan', {})
    if retry.get('template_only') is True:
        errors.append('Uncompleted retry template')
    ids = {i.get('issue_id') for i in issues}
    if not review_ok(retry.get('review')) or set(retry.get('issue_ids', [])) != ids or None in ids:
        errors.append('Retry review/complete issue coverage missing')
    if not all(retry.get(k) for k in ('root_cause_evidence', 'changed_mechanism', 'semantic_prompt_diff', 'protected_features', 'local_feasibility_evidence')):
        errors.append('Retry must change a diagnosed mechanism, not just repeat')
    if not audit.get('submitted_prompt') or retry.get('previous_prompt_sha256') != hashlib.sha256(audit['submitted_prompt'].encode()).hexdigest():
        errors.append('Previous actual prompt is not bound')
    if issues:
        try:
            safe_source_or_retired(root, {'path': audit.get('source_file'), 'sha256': audit.get('source_sha256')})
            safe_file(root, retry.get('diagnostic_board'))
        except (ValueError, TypeError, OSError) as e:
            errors.append(str(e))
        if not review_ok(retry.get('diagnostic_review')) or retry.get('board_uploaded') is not False:
            errors.append('Reviewed diagnostic board must stay offline')
        for i in issues:
            if not all(i.get(k) for k in ('issue_id', 'observed', 'expected', 'bbox_xywh', 'precise_fix', 'recheck', 'material_impact', 'local_fix_ruled_out')):
                errors.append('Incomplete material issue: ' + str(i.get('issue_id')))
            if i.get('cause') != 'source':
                errors.append('Repair composition/matte locally before a paid retry')
            if i.get('issue_id', '<missing>') not in prompt:
                errors.append('Submission omits issue ID: ' + str(i.get('issue_id')))
    if len(jobs) == 2:
        third = retry.get('third_attempt_exception', {})
        if not (third.get('method_changed_since_both_failures') is True and third.get('no_cost_feasibility_passed') is True
                and third.get('evidence_file') and review_ok(third.get('review'))):
            errors.append('Third attempt locked: changed mechanism and no-cost feasibility review required')
        else:
            try:
                safe_file(root, third['evidence_file'])
            except (ValueError, TypeError, OSError) as e:
                errors.append(str(e))
    return errors

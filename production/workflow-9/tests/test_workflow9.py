"""Offline behavioral tests with synthetic fixtures; never approves project artwork."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import tempfile
import unittest
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'production/agent-workflow'))
from lineage_guard import evaluate, inherited_jobs
from registered_edit import replace_region, inspect
from workflow9_checks import budget_errors, finite_cost, mask_arrays, plan_errors, retry_errors, safe_file


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.review = {'status': 'reviewed', 'reviewer': 'SYNTHETIC TEST ONLY', 'reviewed_at': 'test', 'observations': 'Synthetic fixture, never real art acceptance'}
        self.nid = 'V_TEST'
        self.params = {'model': 'gpt_image_2_6_flare', 'quality': 'medium', 'resolution': '2k', 'aspect_ratio': '4:3', 'batch_size': 1, 'output_format': 'png', 'background': 'transparent'}
        self.parent = self.png('parent.png', np.full((8, 8, 4), 255, dtype=np.uint8))
        self.parent['node_id'] = 'N_TEST'
        edit = np.zeros((8, 8), dtype=np.uint8); edit[2:4, 2:4] = 255
        support = np.zeros((8, 8), dtype=np.uint8); support[7, :] = 255
        self.edit = self.png('edit.png', edit)
        self.support = self.png('support.png', support)
        self.node = {'id': self.nid, 'stage': 'expression_variant', 'parents': ['N_TEST'], 'parameters': self.params,
                     'prompt': 'Target smile.', 'input_contract': {'exact_images': 1}, 'affected_pages': [], 'legacy_request': 'OLD'}
        self.cat = {'nodes': {self.nid: self.node, 'N_TEST': {'stage': 'neutral_posture'}}, 'family_canaries': {'N_TEST': self.nid}}
        self.write('production/reference-lineage/catalog.json', self.cat)
        self.write('production/chapter-01/agent-run-plan.json', {'lineage_execution_order': [self.nid], 'page_order': []})
        self.plan = {'workflow_version': 9, 'node_id': self.nid, 'parents': [self.parent], 'route': 'registered_edit',
                     'target_state': 'smile', 'submission_contract': 'One object remains.', 'identity_features': ['fixture'],
                     'geometry_checks': ['fixture'], 'contacts': 'fixture', 'background_review': 'fixture', 'pixel_budget': 'fixture',
                     'reuse_decision': 'fixture', 'local_repair_decision': 'fixture',
                     'object_inventory': [{'id': 'paper', 'before_count': 1, 'after_count': 1, 'before_state': 'blank', 'after_state': 'blank', 'contact': 'unchanged'}],
                     'edit_mask': self.edit, 'support_mask': self.support,
                     'registration': {'landmarks': [{'parent_xy': [0, 0]}, {'parent_xy': [7, 0]}, {'parent_xy': [0, 7]}], 'max_residual_native_px': 1},
                     'boundary_and_occlusion_review': 'fixture', 'protected_pixels_method': 'copy_parent_outside_binary_mask', 'review': self.review}
        plan_binding = self.write('plan.json', self.plan)
        prompt = self.text('prompt.txt', 'Target smile. One object remains.')
        pf = {k: True for k in ['reuse_checked', 'canonical_aliases_checked', 'references_visually_checked', 'page_contracts_checked',
              'pixel_budget_checked', 'directions_contacts_checked', 'text_alignment_checked', 'alpha_shadow_plan_checked', 'live_schema_checked']}
        pf.update(workflow_version=9, parameters=self.params, estimated_credits=1, estimate_checked_at='test',
                  prompt_file=prompt['path'], prompt_sha256=prompt['sha256'], parents=[self.parent],
                  attachments=[dict(self.parent, media_id='TEST ONLY')], edit_plan=plan_binding,
                  shadow_preservation_plan='outside edit', allowed_change_regions=['fixture'])
        audit = self.write('parent-audit.json', {'node_id': 'N_TEST', 'source_sha256': self.parent['sha256'], 'verdict': 'PASS',
                           'reviewer': 'SYNTHETIC TEST ONLY', 'reviewed_at': 'test',
                           'checks': {k: {'verdict': 'PASS', 'evidence': 'synthetic'} for k in ['identity', 'native_geometry', 'alpha', 'shadow']}})
        self.ledger = {'jobs': [], 'sources': {self.nid: {'preflight': pf}, 'N_TEST': {'status': 'accepted', 'audit_accepted': True,
                        'accepted_file': self.parent['path'], 'accepted_sha256': self.parent['sha256'], 'audit_file': audit['path']}}}
        self.window = {'id': 'TEST', 'opened_at': 'test', 'node_ids': [self.nid], 'max_credits': 1}
        self.state = {'status': 'running', 'active_chapter': 1, 'execution_authorizations': [{'chapter': 1, 'user_message': 'TEST ONLY', 'recorded_at': 'test'}],
                      'chapter_runs': {'1': {'spend_window': self.window, 'credit_budget': 2}}}

    def tearDown(self):
        self.tmp.cleanup()

    def bind(self, name):
        return {'path': name, 'sha256': hashlib.sha256((self.root/name).read_bytes()).hexdigest()}

    def text(self, name, text):
        path = self.root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
        return self.bind(name)

    def write(self, name, obj):
        return self.text(name, json.dumps(obj))

    def png(self, name, arr):
        Image.fromarray(arr).save(self.root/name)
        return self.bind(name)

    def gate(self, legacy=None):
        return evaluate(self.root, self.state, self.ledger, 1, self.nid, legacy or {'jobs': []})

    def test_ready_fixture_passes_all_gates(self):
        self.assertEqual(self.gate(), [])

    def test_inherited_and_new_attempts_share_three_cap(self):
        self.ledger['jobs'] = [{'node_id': self.nid, 'status': 'failed'}]*2
        self.assertTrue(any('Three-attempt limit' in e for e in self.gate({'jobs': [{'request_id': 'OLD', 'status': 'succeeded'}]})))

    def test_sheet_inheritance_and_rejection_count(self):
        jobs = [{'request_id': 'OLD', 'status': 'failed'}, {'request_id': 'OLD', 'status': 'submission_unknown'},
                {'request_id': 'OLD', 'status': 'rejected_before_submission', 'no_job_no_charge_receipt': 'proof'}]
        self.assertEqual(len(inherited_jobs(self.node, {'jobs': jobs})), 2)
        jobs[-1]['job_id'] = 'real-job'
        self.assertEqual(len(inherited_jobs(self.node, {'jobs': jobs})), 3)

    def test_unknown_other_node_blocks_globally(self):
        self.ledger['jobs'] = [{'node_id': 'OTHER', 'status': 'submission_unknown'}]
        self.assertTrue(any('One-job concurrency' in e for e in self.gate()))

    def test_old_preflight_cannot_spend_new_allowance(self):
        self.ledger['sources'][self.nid]['preflight']['workflow_version'] = 8
        self.assertTrue(any('Stale preflight' in e for e in self.gate()))

    def test_collage_cannot_replace_clean_parent(self):
        board = self.text('board.txt', 'opaque diagnostic')
        self.ledger['sources'][self.nid]['preflight']['attachments'] = [dict(board, media_id='TEST')]
        self.assertTrue(any('CLEAN' in e for e in self.gate()))

    def test_sibling_needs_family_page_canary(self):
        self.cat['family_canaries']['N_TEST'] = 'V_OTHER'
        self.write('production/reference-lineage/catalog.json', self.cat)
        self.assertTrue(any('Family canary' in e for e in self.gate()))

    def test_window_required(self):
        del self.state['chapter_runs']['1']['spend_window']
        self.assertTrue(any('spend window' in e for e in self.gate()))

    def test_chapter_budget_required_beyond_window(self):
        del self.state['chapter_runs']['1']['credit_budget']
        self.assertTrue(any('chapter credit budget' in e for e in self.gate()))

    def test_unknown_historical_chapter_cost_blocks(self):
        old = {'jobs': [{'request_id': 'UNRELATED', 'status': 'failed', 'chapter': 1}]}
        self.assertTrue(any('Unknown chapter cost' in e for e in self.gate(old)))

    def test_invalid_cost_never_treated_as_zero(self):
        for value in (None, True, float('nan'), float('inf'), -1):
            self.assertFalse(finite_cost(value))
            self.assertTrue(budget_errors(self.window, [], self.nid, value))
        self.assertTrue(budget_errors(self.window, [{'spend_window_id': 'TEST', 'status': 'failed'}], self.nid, 1))

    def test_spent_and_reserved_costs_exceed_window(self):
        for status in ('succeeded', 'failed', 'reserved', 'submission_unknown'):
            jobs = [{'spend_window_id': 'TEST', 'status': status, 'estimated_credits': 1}]
            self.assertTrue(any('ceiling exceeded' in e for e in budget_errors(self.window, jobs, self.nid, 1)))

    def test_registered_replacement_preserves_and_can_erase(self):
        p = np.full((8, 8, 4), 255, np.uint8); c = np.zeros_like(p)
        edit, support = mask_arrays(self.root/'parent.png', self.root/'edit.png', self.root/'support.png')
        result = replace_region(p, c, edit, support)
        self.assertTrue(np.array_equal(result[~edit], p[~edit]))
        self.assertTrue(np.array_equal(result[support], p[support]))
        self.assertTrue((result[edit, 3] == 0).all())

    def test_support_overlap_and_wrong_dimensions_rejected(self):
        p = np.zeros((8, 8, 4), np.uint8); m = np.zeros((8, 8), bool); m[3, 3] = True
        with self.assertRaises(ValueError): replace_region(p, p, m, m)
        with self.assertRaises(ValueError): replace_region(p, p[:7], m, np.zeros_like(m))

    def test_grayscale_feather_is_not_binary_mask(self):
        m = np.zeros((8, 8), np.uint8); m[3, 3] = 100
        self.png('bad-mask.png', m)
        with self.assertRaises(ValueError): mask_arrays(self.root/'parent.png', self.root/'bad-mask.png', self.root/'support.png')

    def test_hash_change_and_path_escape_rejected(self):
        with self.assertRaises(ValueError): safe_file(self.root, {'path': '../outside', 'sha256': 'x'})
        self.text('parent.png', 'changed')
        with self.assertRaises(ValueError): safe_file(self.root, self.parent)

    def test_prop_move_requires_vacated_footprint(self):
        self.plan['object_inventory'][0]['replaces_or_moves'] = True
        errors = plan_errors(self.root, self.plan, self.node, [self.parent])
        self.assertTrue(any('old footprint' in e for e in errors))

    def test_noncollinear_landmarks_required(self):
        self.plan['registration']['landmarks'] = [{'parent_xy': [0, 0]}]*3
        self.assertTrue(any('noncollinear' in e for e in plan_errors(self.root, self.plan, self.node, [self.parent])))

    def test_third_attempt_needs_changed_mechanism(self):
        errors = retry_errors(self.root, {}, {}, [{'status': 'failed'}]*2, [self.parent], '')
        self.assertTrue(any('Third attempt locked' in e for e in errors))

    def test_evidenced_third_attempt_can_pass_without_repeating_bad_prompt(self):
        old_prompt = 'Old ambiguous description.'
        source = self.text('failed-source.txt', 'synthetic failed pixels')
        board = self.text('diagnostic.txt', 'synthetic offline diagnostic')
        evidence = self.write('feasibility.json', {'synthetic': True, 'checked': 'boundary feasibility'})
        issue = {'issue_id': 'E01', 'decision': 'MATERIAL_FAIL', 'observed': 'two', 'expected': 'one',
                 'bbox_xywh': [1, 1, 2, 2], 'precise_fix': 'replace existing object', 'recheck': 'count',
                 'material_impact': 'wrong state', 'local_fix_ruled_out': 'missing surface', 'cause': 'source'}
        audit = {'source_file': source['path'], 'source_sha256': source['sha256'], 'submitted_prompt': old_prompt, 'issues': [issue]}
        retry = {'review': self.review, 'issue_ids': ['E01'], 'root_cause_evidence': 'synthetic', 'changed_mechanism': 'clean parent and connected region',
                 'semantic_prompt_diff': 'replace rather than add', 'protected_features': 'stationary pixels', 'local_feasibility_evidence': 'synthetic',
                 'previous_prompt_sha256': hashlib.sha256(old_prompt.encode()).hexdigest(), 'diagnostic_board': board,
                 'diagnostic_review': self.review, 'board_uploaded': False,
                 'third_attempt_exception': {'method_changed_since_both_failures': True, 'no_cost_feasibility_passed': True,
                                             'evidence_file': evidence, 'review': self.review}}
        errors = retry_errors(self.root, {'retry_plan': retry}, audit, [{'status': 'failed'}]*2, [self.parent], 'E01 replace the existing object')
        self.assertEqual(errors, [])

    def test_integration_mask_cannot_change_after_freeze(self):
        frozen = self.write('frozen.json', self.plan)
        record = {'frozen_edit_plan': frozen, 'edit_mask': {'path': 'different'}, 'support_mask': self.support}
        with self.assertRaisesRegex(ValueError, 'frozen mask'): inspect(self.root, record)

    def test_complete_integration_record_passes_without_writing(self):
        frozen = self.write('frozen.json', self.plan)
        candidate = self.png('candidate.png', np.zeros((8, 8, 4), dtype=np.uint8))
        points = [dict(p, candidate_xy=p['parent_xy']) for p in self.plan['registration']['landmarks']]
        record = {'frozen_edit_plan': frozen, 'edit_mask': self.edit, 'support_mask': self.support,
                  'parent': self.parent, 'candidate': candidate, 'integration_review': self.review,
                  'registration': {'landmarks': points, 'max_residual_native_px': 1},
                  'checks': {k: {'verdict': 'PASS', 'evidence': 'synthetic'} for k in ['same_parent', 'identity', 'connected_contacts', 'object_inventory', 'boundary_seams', 'actual_background', 'reading_size']}}
        result, report = inspect(self.root, record)
        self.assertTrue(report['protected_pixels_exact'])
        self.assertTrue(report['support_pixels_exact'])
        self.assertEqual(report['status'], 'candidate_only_not_visual_acceptance')
        self.assertEqual(result.shape, (8, 8, 4))
        record['registration']['landmarks'][0]['candidate_xy'] = [4, 4]
        with self.assertRaisesRegex(ValueError, 'residual'): inspect(self.root, record)


if __name__ == '__main__':
    unittest.main(verbosity=2)

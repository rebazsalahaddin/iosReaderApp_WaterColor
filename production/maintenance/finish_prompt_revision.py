"""Finish the interrupted workflow-8 prose migration; never touch artwork or receipts."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
PROTECTED = set(json.loads((ROOT / 'production/maintenance/lineage-migration-work/protected-hashes.json').read_text()))


def put(rel, text):
    assert rel not in PROTECTED, rel
    assert Path(rel).suffix in {'.md', '.txt', '.json'}, rel
    path = ROOT / rel
    if path.read_text() != text:
        path.write_text(text)


def replace(rel, old, new, required=True):
    path = ROOT / rel
    text = path.read_text()
    if old in text:
        put(rel, text.replace(old, new))
    elif required:
        assert new in text, (rel, old)


def main():
    manifest = json.loads((ROOT / 'production/full-book-rebuild-r6/book-production-manifest.json').read_text())
    # Replace the contradictory instructions in place, rather than append another override.
    for chapter in manifest['chapters'].values():
        for page in chapter['pages'].values():
            rel = page['assembly_instructions']
            replace(rel, 'WORKFLOW 7 EXECUTION:', 'WORKFLOW 8 EXECUTION:')
            replace(rel,
                    'Prepare true-alpha components using the reviewed Chapter1 procedure; inspect pale interiors, chair gaps and spill.',
                    'Preserve native alpha and the attached generated shadow of new sources; use the retained Chapter 1 keying recipe only for accepted legacy keyed sources. Inspect pale interiors, chair gaps and edges.', required=False)
            replace(rel,
                    'Add one restrained local grounding shadow under each actual supported group, consistent with its light. Exclude editorial/memory/paper artwork from physical floor shadows.',
                    'Keep each neutral master\'s existing soft contact shadow with its complete group, unchanged in shape, position, hue, alpha, softness and intensity. Do not add a second shadow. Only accepted legacy keyed sources use their retained measured grounding recipe. Editorial/memory/paper artwork has no physical floor shadow.', required=False)
            replace(rel,
                    'Attach quiet watercolor shadows at each actual bearing edge and check after final transform.',
                    'Verify the existing generated shadow touches each actual bearing edge after transforming the complete group; preserve its alpha and avoid a second shadow.')
            layout_rel = page['layout']
            layout = json.loads((ROOT / layout_rel).read_text())
            old = 'Use one local soft grounding shadow beneath each complete actual contact group, aligned with sole/chair/prop footings; no shadow for paper art or isolated imagined/editorial inset.'
            new = ('Preserve the neutral master\'s generated soft contact shadow with its complete group; no separate added shadow. '
                   'Inspect actual sole/chair/prop supports and alpha after the uniform transform. '
                   'Only accepted legacy keyed sources follow their retained measured local-grounding recipe; no floor shadow for paper art or imagined/editorial/airborne assets.')
            layout['assembly_notes'] = [new if item == old else item for item in layout.get('assembly_notes', [])]
            layout['composition_performance_contract']['grounding_rule'] = ('Inspect the generated neutral shadow at actual bearing surfaces; preserve its exact shape, position, hue, softness, alpha and intensity in each variant. '
                'One owner, no white gap or extra shadow. Legacy keyed sources retain their measured preparation recipe; imagined/airborne assets have no floor shadow.')
            put(layout_rel, json.dumps(layout, indent=2) + '\n')

    staging = (ROOT / 'production/full-book-rebuild-r6/narrative-staging-audit-v001/REVIEW.txt').read_text()
    findings = dict(re.findall(r'^Chapter (\d+) \(\d+ pages\): (.+)$', staging, re.M))
    for n in manifest['chapters']:
        rel = f'story-and-continuity/chapter-{int(n):02}/pose-corrections/POST_GENERATION_CORRECTIONS.md'
        text = (ROOT / rel).read_text()
        marker = '\n## Narrative staging supplement\n'
        text = text.split(marker)[0].rstrip() + marker + '\n' + findings[n] + '\n\n'
        text += ('Read every page\'s narrative_staging, text_alignment and reference_lineage contracts before choosing a source. '
                 'Name the actor, action, recipient or justified omission, gaze, occupied hands and exact visible instant. '
                 'Preserve the specific exceptions in the page recipe and inspect both reading-size meaning and native contacts. '
                 'A correction still uses its original canonical attempt allowance and the same neutral authority; this supplement is planning, not visual approval.\n')
        put(rel, text)

    rel = 'production/Composition_Continuity_and_Performance.md'
    replace(rel,
            'Use exact native crops of the intended identity/direction from mixed pose sheets. Preserve source and crop provenance. A crop removes competing variants; it is not a new identity master or a new attempt. When useful, locally assemble a positive geometry board showing the approved complete figures in the intended cells and direction. Labels and arrows are instructions only. A neutral identity sheet does not prescribe a neutral performance.',
            'Follow Reference_Lineage_Workflow.md. Audit the identity turnaround, then the neutral posture/contact master, then each expression directly from that ONE neutral image. Compare older pose sheets and geometry guides offline; they are not an upload bundle. An accepted legacy cell may remain usable after its exact native crop and provenance are checked. New expression outputs contain one complete state. A neutral foundation does not prescribe a neutral performance for the final page.')
    replace(rel,
            'Two-column sheets sometimes turn the figures inward despite written arrows. A wrong cell is not silently accepted or mirrored. Reuse a compatible complete state if it genuinely meets the page\'s meaning. Otherwise use only the remaining attempt with the mandatory graphical correction protocol. If one cell passes, retain that complete cell; the corrective submission may explicitly request only the failed complete contact group at native resolution, with packing scope clearly overriding the original packing. This is still attempt 2 of the same canonical request, not a fresh allowance. Preserve the exact original submitted prompt and all required original references.',
            'Historical two-column sheets sometimes turned figures inward despite written arrows. Do not silently accept or mirror a wrong state. Reuse a compatible complete accepted state only when it genuinely meets the page\'s meaning. Otherwise use the remaining canonical attempt with ONE reviewed correction board containing the intact neutral authority and every material issue. Keep the exact first submitted prompt and original references locally as evidence; upload only the reviewed board for the expression retry. A legacy sheet attempt counts against each derived cell, including a failed cell split into a new file.')
    start = 'Build a small darker contact core directly under each observed alpha edge'
    text = (ROOT / rel).read_text()
    if start in text:
        a = text.index(start)
        b = text.index('\n## Thought clouds:', a)
        text = text[:a] + ('New neutral masters include their own very light soft watercolor contact shadow on genuine transparency. '
                          'Inspect every visible support on pale, dark and actual backgrounds: no gap, opaque floor, dark oval or detached wash. '
                          'Expression variants preserve that exact shadow shape, position, hue, alpha, softness and intensity. '
                          'Transform the complete group and its shadow together; do not add a programmatic shadow. '
                          'Airborne assets and crops without a visible ground support have no invented floor shadow.\n\n'
                          'The retained production/compositor/grounding.py recipe applies only to accepted legacy sources whose current measured composition uses local grounding. '
                          'It is not the default for new transparent sources. Preserve existing art and its measured recipes during prompt maintenance. '
                          'At future composition, inspect actual bearing contacts after the final uniform transform and at reading size.\n') + text[b:]
        put(rel, text)

    replace('production/Execution_Instructions.md',
            'Every request has a complete prompt, numbered attachments, technical guide, request record and save instructions.',
            'Every request has an agent routing card and offline reference evidence. Submit only the mapped node\'s short prompt with its minimal input contract; old numbered attachments and packing guides are not upload lists.')
    replace('production/Execution_Instructions.md',
            'locally render annotated real failure crops and justified positive target diagrams/reference crops for every unresolved issue. Inspect the boards, preserve original references and the complete original submitted prompt, and use the reviewed graphical package in the guarded retry.',
            'locally render ONE board containing the intact neutral authority plus annotated real failure crops and justified positive pointers for every unresolved issue. Inspect that board, preserve original references locally and retain the complete original submitted prompt; upload only the reviewed board in the guarded expression retry.')

    # The interrupted pass named a helper that was never implemented. Give the
    # agent the complete local preparation contract without advertising a missing tool.
    policy_rel = 'production/agent-policy.json'
    policy = json.loads((ROOT / policy_rel).read_text())
    policy.pop('visual_correction_builder', None)
    policy['visual_correction_rendering'] = 'local_only_single_board_manual_visual_review_required'
    put(policy_rel, json.dumps(policy, indent=2) + '\n')
    replace('production/Visual_Correction_Guide.txt',
            'Use production/agent-workflow/build_lineage_correction.py with a filled reference-lineage/correction-board-template.json, or an equivalent local renderer satisfying the same record contract.',
            'Fill production/reference-lineage/correction-board-template.json from the actual failure and use local image-composition tools to prepare that one instruction board under the record contract. No workflow-8 board-rendering helper is bundled; do not run the retained workflow-7 multi-board helper for a new retry.')
    replace('production/Visual_Correction_Guide.txt', 'The helper leaves review pending and never approves itself.',
            'Save review_status as pending until an agent actually inspects the complete board; local rendering never approves its own output.')

    rel = 'production/TOOLS.txt'
    text = (ROOT / rel).read_text()
    a = text.index('Workflow 7 checks and planning:') if 'Workflow 7 checks and planning:' in text else text.index('Workflow 8 checks and planning:')
    b = text.index('\n\nCONTINUITY AND PERFORMANCE UPDATE:', a)
    text = text[:a] + '''Workflow 8 checks and planning:
python3 production/agent-workflow/build_handoff.py
python3 production/agent-workflow/validate_handoff.py
python3 production/validate_reference_lineage.py
python3 production/agent-workflow/lineage_guard.py --chapter 2 --node V_CH02_S02_L
The guard is read-only and is expected to BLOCK during prompt-only maintenance. It requires real chapter execution authorization, complete preflight, accepted parents and available inherited attempts. It does not call MCP, reserve jobs or approve art. Use the selected chapter's lineage_execution_order, never the old request ID as an image payload. The maintenance migration scripts are not production entry points; do not rerun them to replace current authored plans.

GRAPHICAL CORRECTION PREPARATION
Read production/Visual_Correction_Guide.txt and fill production/reference-lineage/correction-board-template.json only after an actual first-attempt material failure. Prepare ONE local instruction board with the intact parent dominant and every failure/positive target readable. Record hashes and leave visual review pending until actual inspection. Keep original submitted prompts and failed bytes untouched. The retained build_correction_guide.py and check_guard.py describe the legacy multi-board protocol and are not workflow-8 execution commands. No board or image is rendered during prompt maintenance.
''' + text[b:]
    put(rel, text)

    # Retained historical request specifications must not masquerade as live jobs.
    redirects = {
        'reusable-poses/S01_pilot_listen_converse': 'V_CH01_E02_L and V_CH01_E02_R',
        'reusable-poses/S02_pilot_drawing_hope_disappointed': 'V_CH01_E01_L and V_CH01_E01_R',
        'reusable-poses/S03_pilot_isolated_grownup3_right': 'the page-specific routes in production/reference-lineage/catalog.json; use V_CH01_E02_R for the quiet pilot',
        'reusable-poses/S04_grownup3_talk_reply': 'V_CH01_E03_L',
        'reusable-poses/S05_grownup4_listen_reply': 'V_CH01_E03_R',
        'references/T01_social_table': 'the existing accepted social-table asset and measured page layouts; no new table job is implied',
    }
    for folder, route in redirects.items():
        rel = 'story-and-continuity/chapter-01/' + folder + '/PROMPT.md'
        text = (ROOT / rel).read_text()
        if not text.startswith('RETIRED REQUEST SPECIFICATION'):
            put(rel, 'RETIRED REQUEST SPECIFICATION — NOT A CURRENT IMAGE PAYLOAD\n\n'
                'Future work follows production/Reference_Lineage_Workflow.md and ' + route + '. '
                'Use GPT Image 2.6 Flare, quality medium, 2K, 4:3, native transparency, and one accepted neutral parent per expression. '
                'Do not submit the legacy fenced prompt or upload its numbered bundle. The retained text below documents the earlier request; '
                'it grants no new attempts or artwork changes.\n\n---\n\n' + text)
    replace('production/chapter-01/next-returns/START_HERE.txt',
            'All three sources are received and in use.',
            'All three sources are received and in use. These are historical received-request specifications, not pending jobs. Their prompts and references are offline provenance only. Future work follows production/Reference_Lineage_Workflow.md and the current page routes; never submit these older multi-reference payloads or reset their attempt counts.')

    replace('production/Text_to_Illustration_Alignment.md', 'The reviewed selection is 18 pages, not a target or a quota.',
            'The current reviewed selection is 19 pages, including the user-requested imagined sheep on c02-s04-p02; it is not a target or a quota.')

    # Finish the actual short model payloads, keeping page story and historical
    # request cells unchanged. Camera registration is established at the neutral
    # stage, not copied literally from a standing turnaround.
    catalog_rel = 'production/reference-lineage/catalog.json'
    catalog = json.loads((ROOT / catalog_rel).read_text())
    nodes = catalog['nodes']
    old_content = {nid: n['content'] for nid, n in nodes.items()}
    # These are independent editorial portrait crops, not one physical contact
    # group. A single king reference cannot establish all four named identities.
    local_portraits = {
        'A_CH16_R02_L': (['I_king', 'I_geo', 'I_business', 'I_drinker'],
            'Locally select one accepted complete chest portrait of each named adult: king, geographer, businessman and weary drinker. '
            'Crop from their own audited turnarounds, preserving whole head/shoulders, costume, native pixels and the requested expression. '
            'Keep the four portraits separate and select only the page-named portrait during composition. No furniture or invented meeting.'),
        'A_CH16_R02_R': (['I_vain', 'I_grownup1', 'I_grownup2'],
            'Locally select the accepted vain-man chest portrait, preserving his complete head, hat and shoulders. '
            'For the separate anonymous population cue, use complete native adult silhouettes from audited identity sources with one uniform silhouette treatment; '
            'keep them anonymous, without face detail or a literal numerical tally. Do not assemble heads and bodies or mirror asymmetric figures.'),
    }
    for nid, (parents, instructions) in local_portraits.items():
        n = nodes[nid]
        n.update(stage='local_assembly', parents=parents, shadow_mode='none_editorial',
                 input_contract={'max_images': 0, 'submission_forbidden': True, 'local_identity_sources': parents},
                 local_assembly_instructions=instructions)
        n['prompt'] = ('LOCAL ASSEMBLY RECIPE — DO NOT SUBMIT TO AN IMAGE MODEL. ' + instructions
            + ' Inspect source crops and expression before use; if no suitable accepted source exists, stop and resolve its existing canonical route and remaining attempt allowance. '
            'No new portrait identity, paid portrait-sheet remake, physical floor shadow or extra generation allowance. Record source hashes, crop bounds and uniform scale. '
            'No work is executed by preparing this recipe.')
    corrections = {
        'V_CH04_S03_R': 'Same astronomer in European outfit, body and feet RIGHT, head RIGHT toward the audience; one open explaining hand and a dignified expression. Keep the neutral master\'s face, age and stature.',
        'V_CH19_S01_R': 'Prince standing facing LEFT, one hand cupped near his mouth, calling into the empty valley with a small open mouth and focused gaze. One calling instant; no visible listener or echo figure.',
        'V_CH01_E04_R': 'Full standing older woman, body and shoes three-quarter RIGHT. Head inclines slightly DOWN-RIGHT toward the child; one eyebrow gently raised, soft quizzical smile, one hand lightly raised to chin, other at her side. Kind but uncomprehending; no angry scowl.',
    }
    for nid, content in corrections.items():
        nodes[nid]['content'] = content
        nodes[nid]['allowed_changes'] = content
    for n in nodes.values():
        content = n['content'].replace('no snake or shadow.', 'no snake or snake shadow.')
        content = content.replace('matching the upper-left stage of the flower reference', 'preserving the neutral master\'s shoot design')
        content = content.replace('matching B01, no floating boot', 'preserving the neutral master\'s rocky footing, no floating boot')
        content = content.replace('like the LEFTMOST woman reference', 'as in the neutral master')
        content = content.replace('all six bottles in their guide positions', 'all six bottles in their fixed neutral-master positions')
        n['content'] = content
        if n['stage'] == 'expression_variant':
            n['allowed_changes'] = content

    identity_lock = ('Preserve identity, age, dot-shaped eyes (no anime eyes or enlarged irises), face/nose/ears, '
                     'hair silhouette and colour, skin, costume colours and body proportions. No redesign, mirroring or extra limbs.')
    variant_lock = ('Keep identical identity, age, dot-shaped eyes (no anime eyes or enlarged irises), face/nose/ears, '
                    'hair, skin, costume, head/body size, furniture dimensions, camera, registration and watercolor style.')
    shadow_lock = ('Keep the parent support footprint and its shadow EXACTLY: shape, position, hue, softness, alpha and intensity. '
                   'No added shadow, new floor or matte.')
    for nid, n in nodes.items():
        stage = n['stage']
        if stage == 'identity_turnaround':
            if nid == 'I_flower':
                n['content'] = ('One identity sheet of the SAME living coral rose in front, three-quarter, side and back views. '
                    'Preserve the canonical bloom, two sage leaves, four small thorns, stem proportions and tiny face features where visible. '
                    'Neutral expression; no human limbs, hair or clothing. Same watercolor design and scale across views.')
            elif nid == 'I_ordinary':
                n['content'] = ('One identity sheet of the SAME small cream ordinary flower in front, three-quarter, side and back views. '
                    'Preserve exactly three petals, slender stem, leaves, colours and watercolor design. '
                    'No rose bloom, human limbs, hair, costume or invented facial features.')
            elif nid == 'I_fox':
                n['content'] = ('One clean turnaround of the SAME fox: front, three-quarter, side and back, complete body and tail, '
                    'neutral gentle face and consistent scale. Preserve identity, dot eyes, muzzle, ears, fur colours and proportions. '
                    'No human hands, costume or redesign.')
            elif nid != 'I_snake':
                name = nid[2:].replace('_', ' ')
                n['content'] = (f'One clean identity turnaround of the SAME {name}: front, three-quarter, side and back; '
                    'neutral face, complete body, well-separated views and consistent scale. ' + identity_lock)
            n['prompt'] = n['content'] + ' Native transparent PNG, 4:3, 2K; no scenery, floor shadow or labels.'
        elif stage == 'neutral_posture':
            if n['family'].startswith('astronomer_') and 'body and feet RIGHT' not in n['content']:
                n['content'] += ' Body and feet RIGHT, head RIGHT toward the audience position.'
            lock = identity_lock
            if n['family'].startswith(('rose_', 'ordinary_', 'three_petal_')):
                lock = 'Preserve the exact plant identity, petal/leaf/thorn counts, stem proportions, colours and existing tiny facial features. No human anatomy or invented features.'
            elif n['family'].startswith(('snake_', 'fox_')):
                lock = 'Preserve animal identity, dot eyes, body dimensions, proportions, colours and watercolor design. No human features, costume or extra limbs.'
            if n['family'] == 'pilot_room_desk':
                n['shadow_mode'] = 'none_airborne_or_close_crop'
            shadow = ('Include a very light soft attached watercolor contact shadow at visible ground supports, with graded alpha fading to full transparency. '
                      'No detached blob, dark oval, opaque floor or checkerboard. Preserve opaque subject interiors.')
            if n['shadow_mode'] != 'generated_attached_contact':
                shadow = 'Keep transparent surroundings and opaque subject interiors; no physical floor or floor shadow in this airborne/close-cropped asset.'
            ratio = ''
            if 'I_pilot' in n['parents'] and 'I_prince' in n['parents']:
                ratio = ' At equal depth the prince\'s standing-equivalent height is 0.61 of the pilot\'s, head-height ratio 0.86; preserve these anatomical ratios through the pose.'
            n['prompt'] = ('Create ONE neutral posture/contact master from the audited identity and any supplied essential prop authority. '
                + n['content'] + ' ' + lock + ratio + ' Establish the specified camera and support arrangement; keep the complete contact group intact. '
                + n['light'] + ' ' + shadow + ' 4:3, 2K native transparent PNG; no scenery, labels or diagram marks.')
        elif stage == 'expression_variant':
            family = nodes[n['parents'][0]].get('family', '')
            lock = variant_lock
            action = 'Only change the named expression and necessary head/hand/arm or named prop action; preserve the support/camera setup.'
            if family.startswith(('rose_', 'ordinary_', 'three_petal_')):
                lock = 'Keep identical plant identity, petal/leaf/thorn counts, stem dimensions, colours, existing face and dot-eye design where present, camera, registration and watercolor style. No added human anatomy.'
                action = 'Only change the named bloom, leaf or tiny facial performance; preserve the stem footing and scale.'
            elif family.startswith(('snake_', 'fox_')):
                lock = 'Keep identical animal identity, dot eyes, muzzle, body size/proportions, colours, camera, registration and watercolor style. No human features or costume.'
                action = 'Only change the named face, gaze or limited head/tail performance; preserve the supported body arrangement.'
            n['prompt'] = ('Edit the ONE supplied approved neutral posture. Required change: ' + n['content'] + ' '
                + action + ' ' + lock + ' ' + shadow_lock
                + ' One complete state, 4:3, 2K native transparent PNG. Blank paper stays blank for later canonical marks; no labels or thought clouds in this asset.')
        n['prompt_sha256'] = hashlib.sha256(n['prompt'].encode()).hexdigest()
        put(n['prompt_file'], n['prompt'])
        put(str(Path(n['prompt_file']).with_name('node.json')), json.dumps(n, indent=2) + '\n')
    order, seen = [], set()
    def visit(nid):
        if nid in seen:
            return
        for parent in nodes[nid]['parents']:
            visit(parent)
        seen.add(nid)
        order.append(nid)
    for nid in catalog['dependency_order']:
        visit(nid)
    catalog['dependency_order'] = order
    put(catalog_rel, json.dumps(catalog, indent=2) + '\n')
    # Keep routing cards and chapter manuals synchronized with refined short states.
    for request in manifest['requests'].values():
        previous = request['prompt']
        for nid in request['lineage_nodes'].values():
            request['prompt'] = request['prompt'].replace(old_content[nid], nodes[nid]['content'])
            if nodes[nid]['stage'] == 'local_assembly':
                request['prompt'] = request['prompt'].replace('Actual short payload: ' + nodes[nid]['prompt_file'],
                    'Local assembly recipe — do not submit: ' + nodes[nid]['prompt_file'])
        put(request['folder'] + '/PROMPT.txt', request['prompt'])
        put(request['folder'] + '/PROMPT.md', '# ' + request['id'] + '\n\n' + request['prompt'])
        put(request['folder'] + '/request.json', json.dumps(request, indent=2) + '\n')
        if previous != request['prompt']:
            for number in manifest['chapters']:
                rel = f'story-and-continuity/chapter-{int(number):02}/Chapter_{number}_Manual_Reference_and_Pose_Prompts.md'
                text = (ROOT / rel).read_text()
                if previous in text:
                    put(rel, text.replace(previous, request['prompt']))
    put('production/full-book-rebuild-r6/book-production-manifest.json', json.dumps(manifest, indent=2) + '\n')
    summary_rel = 'production/reference-lineage/migration-summary.json'
    summary = json.loads((ROOT / summary_rel).read_text())
    summary['nodes_by_stage'] = {stage: sum(n['stage'] == stage for n in nodes.values()) for stage in sorted({n['stage'] for n in nodes.values()})}
    put(summary_rel, json.dumps(summary, indent=2) + '\n')
    print('Finished workflow-8 prose: 442 page procedures, 27 staging supplements, active guides and retired-request routing. No media or execution records changed.')


if __name__ == '__main__':
    main()

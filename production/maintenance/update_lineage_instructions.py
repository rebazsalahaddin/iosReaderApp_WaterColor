raise SystemExit("Retired workflow-8 writer: preserve current authored workflow-9 controls; do not rebuild from this historical script.")
"""Instruction migration only; artwork and historical execution receipts are immutable."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[2]
def put(p,s):(ROOT/p).write_text(s.strip()+'\n')
def read(p):return json.loads((ROOT/p).read_text())
def js(p,v):put(p,json.dumps(v,indent=2))
m=read('production/full-book-rebuild-r6/book-production-manifest.json')
model={'id':'gpt_image_2_6_flare','quality':'medium','resolution':'2k','aspect_ratio':'4:3','batch_size':1,'output_format':'png','background':'transparent'}
p=read('production/agent-policy.json');p.update(workflow_version=8,model=model,visual_retry_protocol_version=2,source_template='production/reference-lineage/source-audit-template.json',visual_correction_builder='production/agent-workflow/build_lineage_correction.py',visual_correction_template='production/reference-lineage/correction-board-template.json',reference_lineage_catalog='production/reference-lineage/catalog.json',lineage_ledger='production/reference-lineage/ledger.json',lineage_guide='production/Reference_Lineage_Workflow.md',variant_reference_count=1,expression_parent_stage='neutral_posture',generated_shadow_preserved=True,legacy_attempts_inherited=True)
js('production/agent-policy.json',p)
put('production/MASTER_PROMPT.txt','''THE LITTLE PRINCE — AI AGENT HANDOFF — WORKFLOW 8

This folder is the complete independent project. Prepare or edit instructions without generating or changing artwork. Only when explicitly asked to execute: complete exactly ONE authorized chapter, verify it, clean verified temporary files, then STOP for manual approval before the next chapter. Preserve existing deliveries and real approval scope.

READ FIRST
production/agent-policy.json; production/Reference_Lineage_Workflow.md; production/Higgsfield_Agent_Workflow.md; production/Visual_Audit_and_Retry.md; production/agent-workflow/Record_Contract.md. Read both ledgers, current-progress and agent-state, the selected chapter agent-run-plan.json, exact manuscript, every planned page layout/ASSEMBLY/text_alignment/narrative_staging and current measured compositions. Current records override old provisional status. Do not infer visual approval from this prompt update.

LOCKED MODEL
Higgsfield GPT Image 2.6 Flare, model gpt_image_2_6_flare, quality medium, resolution 2k, aspect_ratio 4:3, batch_size 1, output_format png. The verified API uses quality=medium; it has no separate thinking_level control. Explicit background=transparent for isolated references; background=opaque for full background plates. Verify live schema, real alpha, dimensions and cost before any job. No silent model/setting substitution or upscale. Final page canvas remains 2400×1792 RGB.

IDENTITY → NEUTRAL POSTURE → EXPRESSIONS
1. Audit/reuse the canonical turnaround. If genuinely missing/incompatible, establish one identity turnaround from the strongest single approved identity seed, then accept it before proceeding. Keep dot eyes, face, hair, age, clothing, proportions and watercolor style stable. No paid remake of a suitable accepted identity.
2. Establish one neutral master for each genuinely needed posture/contact/camera/wardrobe/light setup. Include complete connected furniture, held objects and interacting characters. Use the audited turnaround plus only an indispensable exact furniture/prop authority. At most three justified inputs for a multi-person foundation; do not send a style/pose/scale bundle. Inspect scale and identity offline before accepting.
3. The physical neutral master includes its own very light soft attached watercolor contact shadow on genuine transparency. Check every support and graded alpha on pale, dark and actual backgrounds. No opaque floor, colour key, detached shadow or checkerboard. Airborne and editorial assets have no floor shadow.
4. Every expression/action variant uploads exactly ONE image: the approved NEUTRAL posture master. All siblings return to that master. Never feed the preceding expression back into the next, and never restart each expression from the turnaround. Send only the short node PROMPT.txt, with the named emotion/action and protected features. Keep the longer story/geometry/audit documents offline.
5. Change only the necessary face, gaze, head/hand/arm movement and named prop state. Preserve identity, dot-eye design (no anime eyes), hair, skin, clothes, age, head/body dimensions, furniture, camera and placement. Preserve the neutral shadow's exact shape, position, hue, alpha, softness and intensity. Keep the support group together. When support/camera/light genuinely changes use its separately planned neutral master; never invent a new master to evade a failed state's cap.

For Chapter 1 the SAME neutral child/table/chair group branches into excited reading, imagining, focused drawing, giving up and tired hands-on-cheeks states. Book opening/closing and hand contacts may change only as named. Standing with paper has its own master. The civilian pilot's seated social states share the same chair, size and orientation while hope, disappointment, polite speech and loneliness change. No current Chapter 1 artwork is regenerated by this instruction update.

USE THE ACTUAL ROUTES
All 27 chapters and 442 page plans route through production/reference-lineage/catalog.json and each chapter's lineage_execution_order. Legacy request IDs/cells remain traceable; L/R are logical states, not a request for two-column sheets. Old numbered reference folders are offline audit evidence only. Their PROMPT.txt files now route the agent to short node payloads; do not submit a routing card or attach its entire folder. Page-specific lineage overrides take precedence. Reuse suitable accepted legacy cells; new planned nodes are not an order to generate everything.

AUDIT BEFORE BRANCHING
Accept identity, then neutral, then an early representative variant before parallel siblings. Verify actual face/hair/dot eyes/clothes and measured native anatomy, support contacts, genuine alpha, soft shadow, visible expression, native pixels and story state. Record parent IDs/files/hashes, allowed edit regions and unchanged-region/shadow evidence. A neutral master that fails must not become the source of a whole family. Appearance percentages are not proof of identity. Inspect every complete page at reading size and contacts at native size.

CREDIT AND RETRY RULES
Maximum two attempts per canonical reference state globally: initial plus one evidenced material correction. Earlier whole-sheet attempts count against each derived cell. New model, filename, chat, parent or split cell never resets the allowance. Read the immutable historical ledger AND the lineage ledger. Existing exhausted states remain blocked; a new neutral cannot secretly deliver that failed expressive state. Do not regenerate harmless watercolor variation or fix layout/extraction by paying for a new source. At most three independent ready jobs, with no dependency/consumer overlap. Reserve and persist jobs before submission; reconcile unknown jobs, never resubmit blindly.

For a first-pass material source failure, pinpoint ALL issues with actual coordinates, observed/expected differences and exact fixes. Locally create ONE reviewed correction-reference board: unchanged approved neutral dominant, labelled failed crops and positive target pointers for every issue. This board is the sole upload for an expression retry. Keep untouched failed bytes locally. Preserve the complete originally submitted short prompt, followed by one concise issue-ID correction block; preserve every passing feature. Do not render annotations into art. If all issues cannot be legible in one board, stop before spending. No paid diagnostic images. After attempt two recheck every issue and regressions; remaining material failures are BLOCKED, never a third attempt.

COMPOSE CAREFULLY
Follow Geometry_and_Frame_Continuity.md, Composition_Continuity_and_Performance.md and Text_to_Illustration_Alignment.md. Measure native landmarks and comparable physical ratios, apply one uniform scale to each complete group and its existing shadow, and match same-camera support/background anchors. No pose-box fitting, head swaps, stretching or detached programmatic shadow. Do not double-shadow a new transparent master. Legacy sources needing existing local preparation follow their retained recipes. Protect native pixel budgets, cover borders, chronology, paper corners and canonical drawing marks. Every page conveys its distinct text beat with clear recipient/gaze/emotion. Selected thoughts use quiet readable watercolor content, adaptive frame and three owner-linked puffs. No blanket thought clouds or duplicate finished pages.

SAVE, VERIFY, CLEAN, STOP
Keep original returns, precise audits, attempt receipts, approved parents/shadow masks, current layers and measured layouts. Run production/validate_package.py and the read-only lineage pre-submission guard. Reconstruct all final PNGs exactly; verify coverage, hashes and ZIP. After an actually completed chapter, follow Cleanup_Instructions.md: one final delivery/ZIP, necessary dependencies and permanent attempts retained; remove only verified obsolete work. Preparing prompts alone is not a delivery cleanup or permission to delete art. Mark awaiting_chapter_approval, no queued next-chapter jobs, report actual credits/reuse/blocks and STOP for manual approval. Never fabricate approval or promise perfect future output.
''')
put('production/Higgsfield_Agent_Workflow.md','''# Higgsfield chapter execution — workflow 8

Read `MASTER_PROMPT.txt` and `Reference_Lineage_Workflow.md`. This is the active workflow across all 27 chapters. The live model was inspected on 8 November 2026; no generation occurred during the prompt migration.

1. Confirm explicit execution scope in agent-state, chapter approval and current accepted sources. Read both ledgers. Preparing these files never activates production.
2. Read exact page text, planned state/camera/contact/scale, then the chapter `lineage_execution_order`. Reuse compatible accepted art before considering any job. Existing suitable turnarounds need audit, not paid recreation.
3. Verify model `gpt_image_2_6_flare`, `quality: medium`, `resolution: 2k`, `aspect_ratio: 4:3`, `batch_size: 1`, `output_format: png`, `background: transparent`. Full background plates alone use opaque. The API has no separate thinking control. Refresh live model schema and credit estimate; actual output dimensions still need checking.
4. Audit/accept the identity turnaround; establish and audit the neutral posture/contact master with its own attached soft shadow; then generate an early expression using exactly ONE accepted neutral master. Inspect it before sibling variants. All variants branch directly from the neutral. The old numbered folders are offline comparison evidence, not upload lists.
5. Send the node's short `PROMPT.txt`, not the routing card, whole manuscript or audit guide. Record allowed face/head/hand/prop edits and immutable identity/dot eyes/clothes/size/furniture/camera/shadow. New neutral foundations may use only justified identity plus essential prop inputs, at most three. Read the specific family input contract.
6. Populate preflight, run `python3 production/agent-workflow/lineage_guard.py --chapter N --node NODE_ID`, then reserve atomically in the lineage ledger. A guard pass is not authorization or proof of visual quality. One writer; at most three independent live jobs across both ledgers. Persist IDs, hashes, costs and outcomes; reconcile unknown jobs before proceeding.
7. Download original bytes unchanged. Audit native alpha, contact shadow, identity, geometry and expression, then local extraction/composition on actual backgrounds. Keep parent lineage and measured unchanged-region evidence. Never add a second shadow by default. Source acceptance requires an actual named visual review.
8. Two attempts total per canonical state, including old sheet jobs for each derived cell. Follow the single-board graphical retry protocol only for material source failure. Preserve all prior counts, even across the model change. No cosmetic resampling or third attempts.
9. Compose all pages, verify text/continuity/unique meaning, exact reconstruction and storage. Finish one chapter, clean only safe obsolete working outputs, mark awaiting approval and STOP. Report incomplete/blocked pages honestly.

See `agent-workflow/Record_Contract.md` for record fields and `Visual_Correction_Guide.txt` for one-image retry preparation. The schema snapshot is `reference-lineage/model-capabilities.json`; it is verification evidence, not permission to submit.
''')
put('production/Visual_Audit_and_Retry.md','''# Source audit and credit discipline — workflow 8

Use `Reference_Lineage_Workflow.md` and `reference-lineage/source-audit-template.json`. Audit actual pixels, not filenames, successful job status or a claimed similarity percentage.

At the identity gate compare dot eyes, face/nose/ears, hair silhouette, skin, age, costume and body proportions across views. Resolve inconsistent authorities before generation. At the neutral gate compare those identities, camera, dimensions, furniture/prop counts, internal ratios and all supported contacts. Native transparent output must have transparent surroundings, opaque subject interiors and graded, attached shadow alpha; inspect on pale, dark and actual backgrounds. A checkerboard painted into RGB or opaque white floor fails. Airborne/editorial assets have no ground shadow.

At the variant gate bind the single neutral parent ID and file hash. Inspect only permitted expression/head/hand/prop edits, record visible emotion and gaze, compare all unchanged regions and shadow shape/location/hue/alpha/intensity. Preserving dot eyes still allows a blink or sad brow. Check native pixel budget and use the actual page passage. Do not accept a neutral face for a sad/excited beat. A suitable legacy source may be reused after audit; do not pay to improve harmless grain variation.

Verdicts: PASS; PASS_WITH_NOTE for immaterial watercolor variation; LOCAL_FIX for extraction/placement/registration repair; MATERIAL_FAIL only for wrong identity/anatomy/state/contact, unusable missing pixels or conspicuous incompatible rendering; BLOCKED when two attempts are spent. Numeric validators never certify a visual pass. Do not change completed historical audits to add fictional new checks.

For each unresolved material issue record node, logical legacy cell, affected pages, failed file/hash, source dimensions, exact pixel bbox, observed and expected features, contract authority, material impact, why reuse/local repair cannot solve it, precise fix and recheck. Diagnose source versus composition before retrying.

Two attempts globally per canonical state. Inherit historical sheet attempts for each mapped cell, including failed/unknown submissions; a new model/parent/name cannot reset them. Before attempt two, use `Visual_Correction_Guide.txt`: locally prepare ONE reviewed correction-reference board with intact accepted authority and clear failure/target evidence for EVERY issue. Preserve the complete original short prompt plus the consolidated corrections. One board only for an expression retry; no turnaround bundle, sibling poses or extra failed-image upload. Keep the untouched failed original locally. A confirmed terminal technical failure with no image needs a resolved technical diagnosis instead of invented visual evidence.

After retry recheck every issue and every previously passing feature, including shadow/alpha. Do not silently replace a failed expression with a newly named neutral. Remaining material failure blocks that source; complete independent work, report the exact issue and do not exceed two attempts. Keep one consolidated source-correction round per final page; local composition does not consume generation credits.

Before delivery inspect every final page at reading size and native contact/edge detail, then the ordered chapter for relative scale, fixed same-camera anchors, unique text beats, expressions, props, three-puff selected thoughts and attached support shadows. Save concrete evidence, never template passes.
''')
put('production/Visual_Correction_Guide.txt','''GRAPHICAL RETRY — WORKFLOW 8 / PROTOCOL 2

Only a material source failure after attempt one justifies a visual correction board. No paid image generation creates this diagnostic. Read Reference_Lineage_Workflow.md. The two-attempt global cap and existing attempt inheritance remain unchanged.

Create exactly ONE instruction PNG for the retry. The unchanged accepted neutral master is the dominant panel and sole identity/geometry/style authority for an expression edit. In a clearly separated diagnostic strip, show every numbered failed crop with its exact error box/pointer, a justified correct target crop or simple directional/contact sketch, and concise required correction. The failed original remains untouched locally. Avoid another full alternate identity. Mark diagnostics INSTRUCTION ONLY; no labels/arrows should appear in returned art.

Use production/agent-workflow/build_lineage_correction.py with a filled reference-lineage/correction-board-template.json, or an equivalent local renderer satisfying the same record contract. Target crops come from the approved parent or explicitly audited identity evidence; simple diagrams explain directions, never invent faces. Include all material issues in one board. Keep the intact parent dominant and inspect both full size and actual reference-display size. If all issues cannot be readable at supported upload dimensions, STOP before paying; no tiny unreadable tiles or omitted issues. The helper leaves review pending and never approves itself.

For each issue preserve: issue_id, failed-source bbox/dimensions, observed versus expected, precise_fix, protected passing features and recheck. Record board path/hash, failed source hash, parent IDs/hashes, issue IDs, review_status, reviewer/time, dominant_intact_authority and legible_at_upload_size. After actual inspection set approved_for_retry with observations, never mechanically.

The sole retry attachment is this reviewed board. Keep the full original submitted short prompt, followed by one concise correction block addressing every issue ID and exact fix. State that the intact parent is the only appearance authority, all diagnostics are instruction-only, all unspecified features and the attached shadow stay unchanged. This replaces the former multi-attachment recipe. Foundation retries may show their already justified authorities inside the single board; do not introduce new identities or reset their budgets.

On return inspect each issue and all passed features, shadow, alpha and contacts again. A second material failure is blocked. A first-pass success needs neither board nor another job. A confirmed no-image terminal service error requires a resolved technical diagnosis instead.
''')
put('production/Background_Removal_Instructions.md','''# Transparent reference preparation — workflow 8

New isolated references use GPT Image 2.6 Flare, quality medium, 2K, 4:3, PNG, explicit `background: transparent`. Full background plates use opaque output. Do not request a magenta/green key for new generations.

Preserve raw bytes and inspect actual RGBA/alpha, dimensions and file format. Transparent surroundings should be alpha zero, subject interiors opaque, and the generated soft contact-shadow fringe smoothly graded. Check closed chair/limb gaps without eroding hair, fingers, furniture or pale clothing. Inspect on light, dark and intended background. Reject painted checkerboard, white matte, colour spill, missing anatomy or floating contact shadows.

Retain the neutral master's attached shadow with the complete subject group. Every expression must preserve its location/shape/hue/alpha/intensity. Record shadow/protected masks. Where only face/hands change and all supports are fixed, restore unchanged parent pixels through a verified mask if needed, with seam and occlusion checks; do not reconstruct anatomy or draw a replacement shadow. No duplicate programmatic shadow under an already shadowed master. Uniformly transform group and shadow together.

Existing accepted keyed Chapter 1 originals remain unchanged and reusable. Their retained preparation recipes in compositor/chapter01_reference_methods.py apply only to those legacy sources; sample actual keys, protect pale opaque interiors and inspect enclosed gaps. Do not run colour-key extraction on new true-alpha images or treat historical thresholds as universal.

Keep intentional cream paper and glass refraction/support patches. Do not indiscriminately remove background plates or the contents of an optical patch. Save exact masks, source hashes, measured crop and transformation, then audit again after final placement.
''')
put('production/Generation_Order.md','''# Chapter-scoped reference lineage order — workflow 8

Use each chapter's `agent-run-plan.json` field `lineage_execution_order`. It orders accepted identity turnarounds, neutral posture/contact masters and direct expression children. The global catalog is `reference-lineage/catalog.json`; legacy request dependency order remains for story/audit traceability, not for expression-to-expression generation.

Reuse accepted compatible sources first. A newly planned neutral or variant is a requirement slot, not an automatic paid job. Validate alpha/contact shadows and identity before accepting a neutral, then inspect an early expression before sibling work. Expression inputs are exactly one accepted neutral; no prior-expression chain. Actual MCP payloads are the short node PROMPT.txt files; old request cards route the agent to them.

Execute only the explicitly active chapter's closure, including a specifically needed later-owned shared asset. At most three independent ready jobs. Existing historical attempts count against mapped states. Run the lineage guard before reservation. Never run all chapters at once.

After one full chapter, verify, clean eligible obsolete working files and STOP for manual approval. Preparing or revising these instructions does not start generation or authorize changing existing deliveries.
''')
# Retain exact story/composition guidance while replacing obsolete generation paragraphs.
p=ROOT/'production/Execution_Instructions.md';s=p.read_text();s=s.replace('workflow 7','workflow 8')
start=s.index('Chapter 1’s current delivery');end=s.index('\n\n',start);s=s[:start]+"Read current-progress.json for the actual delivered edition and approval state. Prompt-only maintenance never changes that state or the delivered images."+s[end:]
start=s.index('The agent generates required references');end=s.index('\n\n',start);s=s[:start]+"Generation follows Reference_Lineage_Workflow.md: GPT Image 2.6 Flare, quality medium, 2K, 4:3, one PNG. Explicit native transparency for isolated references, opaque background plates. Audit turnaround → neutral posture with generated contact shadow → one-neutral-reference expression variants. Two attempts including historical jobs, no automatic chapter continuation."+s[end:]
start=s.index('WAITING attachments');end=s.index('\n## 3.',start);s=s[:start]+"Old numbered attachments and request dependencies remain offline audit evidence. Future execution uses the chapter lineage_execution_order and catalog input contracts. Each expression uploads exactly one approved neutral parent; never attach the old bundle or use a sibling expression. Reuse passing existing art, audit missing parents before successors, and stop after the authorized chapter.\n"+s[end:]
start=s.index('Two compatible narrow poses');end=s.index('\n\n',start);s=s[:start]+"New outputs contain ONE logical state each. Legacy L/R sheets may supply an already accepted cell; they are not the future packing plan. Complete shared interactions and furniture/characters remain intact. Identity turnarounds are the deliberate multi-view exception."+s[end:]
s=s.replace('Use the request’s opaque flat magenta or green key. Create separate RGBA components, masks and preparation records.','New sources already have native alpha and generated soft attached shadows. Preserve that alpha and shadow. Only legacy accepted keyed sources use their retained keying procedure. Create measured RGBA components, masks and preparation records.')
s=s.replace('Build warm paper, background, single-owner grounding shadows, complete people/props/contact groups, registered paper artwork with fingers above it, and declared foreground occlusion.','Build warm paper and background, then complete people/props/contact groups WITH their existing generated single-owner soft shadows, registered paper artwork with fingers above it, and declared foreground occlusion.')
start=s.index('Consecutive dialogue pages');end=s.index('\n\n',start);s=s[:start]+"Reuse compatible components while giving every page a meaningful individual text beat. Exact duplicate final illustrations are forbidden. Keep same-camera size/anchors while varying the text-specific expression, action or legitimately planned whole-scene framing."+s[end:]
start=s.index('Add one restrained local shadow');end=s.index('\n\n',start);s=s[:start]+"Preserve the neutral master's restrained attached shadow with its complete group. Do not add a programmatic second shadow by default. Legacy prepared art follows its retained measured recipe. Never put physical floor shadows beneath separate editorial, memory or hypothetical contents."+s[end:]
s=s.replace('prepare its original complete request with a consolidated list of measured material defects and the real failed return as the final numbered diagnostic attachment','prepare its complete original short node prompt plus precise material fixes and ONE reviewed instruction board containing the intact neutral authority and all failed-crop diagnostics')
s=s.replace('Keep production/agent-state.json and production/agent-ledger.json current before and after every paid submission.','Keep production/agent-state.json and production/reference-lineage/ledger.json current before and after future submissions; preserve and consult the historical production/agent-ledger.json counts.')
s=s.replace('Record actual cell boundaries and empty gutter.','Record the actual complete state bounds, parent registration and any legacy cell extraction.')
p.write_text(s)
# Compact root entry points; no stale multi-reference route.
put('START_HERE.txt','''THE LITTLE PRINCE ILLUSTRATION PROJECT — WORKFLOW 8

This is the independent project root. Start with production/MASTER_PROMPT.txt and production/Reference_Lineage_Workflow.md, then production/Execution_Instructions.md and production/agent-policy.json. All 27 chapters and 442 page plans are included.

Future model: Higgsfield GPT Image 2.6 Flare, quality medium, 2K, 4:3, one PNG. Native transparency for isolated references. Audit turnaround → approved neutral posture with attached soft shadow → each expression from exactly ONE same neutral master. Old attachment folders are offline evidence, not upload lists.

Use current-progress and measured current layouts for existing art. The November 8 update changes prompts only: no generated images, delivered illustrations, attempts or approval history are changed. Do not regenerate current chapters because the workflow changed.

For actual authorized execution use the selected chapter agent-run-plan.json and lineage_execution_order. Read both ledgers, preserve two-attempt caps including old jobs, and stop after one chapter for manual approval. Run python3 production/validate_package.py before handoff.
''')
put('AGENTS.md','''# Illustration production — workflow 8

This directory is the independent project root. Read START_HERE.txt, production/MASTER_PROMPT.txt, production/Reference_Lineage_Workflow.md, production/Execution_Instructions.md and production/agent-policy.json. All paths stay root-relative inside this project.

The active model is GPT Image 2.6 Flare, quality medium, 2K, 4:3, batch_size 1, PNG; explicit transparent isolated references and opaque background plates. Audit/reuse identity turnaround, then neutral posture/contact master with soft generated shadow, then each expression from exactly one accepted neutral. Never chain expressions or upload a large reference bundle. Protect identity/dot eyes/size/clothes/furniture/registration and preserve parent shadow exactly. Full details and all node routes are in the lineage guide/catalog.

The current user request changes prompts only. Do not generate, revise, re-export or delete illustrations/reference media, deliveries, animation/audio or historical job/audit records in this maintenance pass. No paid jobs. Preparation is not execution or approval.

On later explicit execution use chapter lineage_execution_order, both ledgers and lineage_guard.py. Maximum two attempts globally per canonical state including old sheet jobs. Unknown submissions block resubmission. Graphical retry uses one reviewed board with intact authority and every material issue; no paid guide generation. Never evade spent attempts by renaming a source or foundation.

Every page needs exact text/chronology, identity, measured relative scale, stable same-camera anchors, clear expressions/recipient, complete contacts, readable selected thoughts with three puffs and unique meaning. Read Geometry_and_Frame_Continuity.md, Composition_Continuity_and_Performance.md and Text_to_Illustration_Alignment.md. Current measured records override provisional plans. Generated alpha/shadows need actual visual inspection, not just format validation.

After an actually completed chapter perform dependency-checked Cleanup_Instructions.md, retain one current delivery/ZIP and required originals/layers/measurements/audits/attempts. This maintenance pass does not authorize deleting existing artwork. Run python3 production/validate_package.py. Deliver exactly one authorized chapter, mark awaiting_chapter_approval and STOP until real manual approval. A planning pass is never a new visual approval.
''')
# Update active chapter entry/correction guides, preserving exact source-story documents.
for cn,ch in m['chapters'].items():
 folder=ROOT/f'story-and-continuity/chapter-{int(cn):02}'
 put(str((folder/'START_HERE.txt').relative_to(ROOT)),f'''CHAPTER {cn} — WORKFLOW 8
Read production/MASTER_PROMPT.txt and production/Reference_Lineage_Workflow.md from project root. Use production/chapter-{int(cn):02}/agent-run-plan.json and its lineage_execution_order. GPT Image 2.6 Flare, quality medium, 2K, 4:3, one PNG; transparent isolated references. Turnaround → audited neutral posture with soft shadow → each expression from ONE same neutral. Existing sources are reused after audit. All page layouts and exact texts remain authoritative. Two attempts including history; stop after one chapter for approval. Preparing prompts changes no artwork.
''')
 p=folder/'pose-corrections/POST_GENERATION_CORRECTIONS.md'
 put(str(p.relative_to(ROOT)),f'''# Chapter {cn} — planned states and material corrections

Known expression/contact/prop changes are included in the lineage catalog before execution. Read production/Reference_Lineage_Workflow.md and production/Visual_Correction_Guide.txt. A C-code identifies an authored state; it is not a fresh retry budget.

Audit turnaround, neutral posture and then each single-reference expression. Keep dot eyes, face/hair/clothes/size/furniture/camera/support and generated soft shadow unchanged outside the named action. New outputs use true alpha; legacy keyed originals retain their preparation history. Use the page's exact source text and geometry contract.

A first-pass material source failure requires precise coordinates, observed/expected, all issue IDs, local-fix analysis and exact correction. Prepare ONE reviewed local correction board with dominant intact neutral and diagnostic crops/positive targets for every issue. Upload that board alone for the variant retry with the complete original short prompt plus fixes. Preserve failed bytes locally and all passing features. No paid guide or cosmetic retry. After two attempts including historical sheet jobs, block the unresolved state; never rename it or regenerate under a neutral label.

Check every page and the ordered sequence for visible expression, interaction, relative scale, attached shadows, unique text beat and selected thoughts. Local placement/alpha repairs use no generation attempt. One consolidated source-correction round per page. Complete only this authorized chapter and stop for manual approval.
''')
for q in m['requests'].values():
 put(q['folder']+'/START_HERE.txt',f'''{q['id']} — AGENT ROUTING CARD
Read PROMPT.txt for the logical states and paths to actual short generation payloads. Read production/Reference_Lineage_Workflow.md. Do not upload this entire folder. Numbered reference-images are OFFLINE audit evidence. New expression generation uses exactly ONE approved neutral posture; establish audited turnaround and neutral foundation first. GPT Image 2.6 Flare, quality medium, 2K, 4:3, one PNG, native alpha for isolated assets. Two attempts including historical jobs. Existing accepted sources and current images remain unchanged during prompt preparation.
''')
# Retired two Chapter 1 correction packs remain identifiable, never executable old prompts.
for folder in (ROOT/'story-and-continuity/chapter-01/pose-corrections').iterdir():
 if folder.is_dir() and folder.name.startswith(('C01_','C02_')):
  text='RETIRED GENERATION ROUTE — retained reference provenance only.\nUse production/reference-lineage/catalog.json. Pilot social expressions route through N_pilot_social_chair_right__soft_day_upper_left; younger adult uses the audited younger social chair family. Do not submit an old multi-reference prompt or reset attempts. Read production/Reference_Lineage_Workflow.md. No artwork changes are authorized by prompt maintenance.\n'
  for name in ['PROMPT.txt','PROMPT.md','START_HERE.txt']:
   if (folder/name).exists():(folder/name).write_text(text)
# Remove stale model spelling in other active prose (never historical records/media).
protected=read('production/maintenance/lineage-migration-work/protected-hashes.json')
protected_paths=set(protected.get('files',protected).keys()) if isinstance(protected,dict) else set()
for p in ROOT.rglob('*'):
 if not p.is_file() or p.suffix not in ['.md','.txt'] or any(x in p.parts for x in ['generation-records','audits','current','maintenance','animation','reference-lineage']):continue
 if str(p.relative_to(ROOT)) in protected_paths:continue
 s=p.read_text();s=s.replace('Nano Banana 2.1','GPT Image 2.6 Flare').replace('High Thinking','Medium quality').replace('high thinking','medium quality').replace('nano_banana_2_1','gpt_image_2_6_flare')
 p.write_text(s)
js('production/reference-lineage/source-audit-template.json',{'template_only':True,'node_id':None,'stage':None,'source_file':None,'source_sha256':None,'parents':[],'reviewer':None,'reviewed_at':None,'verdict':None,'checks':{k:{'verdict':None,'evidence':None} for k in ['identity','dot_eye_design','native_geometry','state_expression','contacts','alpha','shadow','unchanged_regions','pixel_budget','text_alignment']},'allowed_change_regions':[],'issues':[],'second_attempt_recheck':[]})
js('production/reference-lineage/correction-board-template.json',{'template_only':True,'node_id':None,'neutral_file':None,'failed_file':None,'original_prompt_file':None,'issues':[{'issue_id':'E01','bbox_xywh':None,'observed':None,'expected':None,'precise_fix':None,'target_file':None,'target_bbox_xywh':None}],'output_directory':None,'note':'Fill from actual material failure. Local renderer never automatically approves. No paid diagnostic generation.'})
print('Updated policy, master, execution/audit guides and all chapter/request entry points; no artwork submitted or edited.')

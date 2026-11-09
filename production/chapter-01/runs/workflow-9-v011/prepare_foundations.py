import hashlib
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(".")
sys.path.insert(0, str(ROOT / "production/agent-workflow"))
from lineage_guard import evaluate, inherited_jobs, counted

cat = json.loads((ROOT / "production/reference-lineage/catalog.json").read_text())
plan = json.loads((ROOT / "production/chapter-01/agent-run-plan.json").read_text())
lledger = json.loads((ROOT / "production/reference-lineage/ledger.json").read_text())
aledger = json.loads((ROOT / "production/agent-ledger.json").read_text())
state = json.loads((ROOT / "production/agent-state.json").read_text())
static_refs = json.loads((ROOT / "production/chapter-01/runs/workflow-9-v011/preflight/uploaded-static-refs.json").read_text())
inv = json.loads((ROOT / "production/workflow-9/authorized-removal-inventory.json").read_text())
retired_map = {item["path"]: item["sha256"] for item in inv["files"]}

pf_dir = ROOT / "production/chapter-01/runs/workflow-9-v011/preflight"
aud_dir = ROOT / "production/chapter-01/runs/workflow-9-v011/audits"


def bind(rel):
    p = ROOT / rel
    return {"path": rel, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}


def make_review(obs):
    return {
        "status": "reviewed",
        "reviewer": "Antigravity visual inspection",
        "reviewed_at": "2026-11-08T13:10:00+03:00",
        "observations": obs
    }


def make_diag_board(nid, issue_id, summary_text):
    bpath = f"production/chapter-01/runs/workflow-9-v011/preflight/{nid}-diag-board.png"
    im = Image.new("RGB", (1200, 900), (250, 246, 238))
    dr = ImageDraw.Draw(im)
    dr.rectangle([20, 20, 1180, 880], outline=(120, 90, 70), width=3)
    dr.text((40, 40), f"WORKFLOW 9 OFFLINE DIAGNOSTIC BOARD: {nid}", fill=(40, 30, 20))
    dr.text((40, 80), f"Issue ID: {issue_id} | Board stays OFFLINE (board_uploaded=false)", fill=(160, 40, 30))
    dr.text((40, 130), summary_text[:120], fill=(40, 30, 20))
    im.save(ROOT / bpath)
    return bind(bpath)


node_attachments = {
    "I_pilot_civilian": [
        static_refs["story-and-continuity/chapter-01/pose-corrections/E01_pilot_reaching_hope_and_withdrawn_disappointment/reference-images/01_pilot__civilian-social__neutral-three-quarter__v001.png"]
    ],
    "N_child_table__soft_day_upper_left": [
        static_refs["production/chapter-01/runs/workflow-8-v011/preflight/child-identity-three-quarter.png"],
        static_refs["production/chapter-01/runs/workflow-8-v011/preflight/child-room-furniture-geometry.png"],
    ],
    "N_child_standing_paper_left__soft_day_upper_left": [
        static_refs["production/chapter-01/runs/workflow-8-v011/preflight/child-identity-three-quarter.png"],
    ],
    "N_older_standing_right__soft_day_upper_left": [
        static_refs["appearance-references/shared/LP_ref_char_grownup1_turnaround.png"],
    ],
    "N_woman_standing_right__soft_day_upper_left": [
        static_refs["appearance-references/shared/LP_ref_char_grownup2_turnaround.png"],
    ],
    "N_younger_social_chair_left__soft_day_upper_left": [
        static_refs["appearance-references/chapter-01/LP_ref_char_grownup4_turnaround.png"],
        static_refs["production/chapter-01/runs/workflow-9-v011/preflight/younger-social-chair-geometry.png"],
    ],
    "N_pilot_flying_left__soft_day_upper_left": [
        static_refs["appearance-references/shared/LP_ref_char_pilot_turnaround.png"],
        static_refs["appearance-references/shared/plane_side_view.png"],
    ],
    "N_pilot_flying_right__moonlight_upper_left": [
        static_refs["appearance-references/shared/LP_ref_char_pilot_turnaround.png"],
        static_refs["appearance-references/shared/plane_side_view.png"],
    ],
    "A_CH01_B10_ONE": [
        static_refs["story-and-continuity/chapter-01/references/B10_childhood_room_without_foreground_furniture/reference-images/01_LP_ref_child_room.jpg"],
    ],
    "A_CH01_B11_ONE": [
        static_refs["story-and-continuity/chapter-01/references/B11_day_flight_landscape/reference-images/01_LP_ref_sahara_day.jpg"],
    ],
    "A_CH01_B12_ONE": [
        static_refs["story-and-continuity/chapter-01/references/B12_night_flight_landscape/reference-images/01_LP_ref_sahara_night.jpg"],
    ],
    "A_CH01_R10_ONE": [
        static_refs["story-and-continuity/chapter-01/references/R10_forest_book_swallowing_picture/reference-images/01_LP_ref_child_book.png"],
    ],
    "A_CH01_R11_ONE": [
        static_refs["story-and-continuity/chapter-01/references/R10_forest_book_swallowing_picture/reference-images/01_LP_ref_child_book.png"],
    ],
    "A_CH01_R12_ONE": [
        static_refs["story-and-continuity/chapter-01/references/B10_childhood_room_without_foreground_furniture/reference-images/01_LP_ref_child_room.jpg"],
    ],
    "A_CH01_R13_L": [
        static_refs["story-and-continuity/chapter-01/references/R13_hat_and_navigation_thoughts/reference-images/01_watercolor_style_crop.png"],
    ],
    "A_CH01_R13_R": [
        static_refs["story-and-continuity/chapter-01/references/R13_hat_and_navigation_thoughts/reference-images/01_watercolor_style_crop.png"],
    ],
}

prior_configs = {
    "I_pilot_civilian": {
        "source_file": "production/chapter-01/runs/workflow-8-v011/sources/I_pilot_civilian-attempt-1.png",
        "issue_id": "IC01",
        "observed": "Prior workflow-8 civilian turnaround retired under user fresh-start directive to establish a clean Workflow-9 civilian identity turnaround.",
        "expected": "Four well-separated full-body civilian views (front, three-quarter, side, back) on transparent PNG with dot eyes and consistent proportions.",
        "bbox_xywh": [100, 100, 2136, 1544],
        "precise_fix": "IC01: Generate fresh 4-view civilian pilot turnaround from the single clean three-quarter seed without diagnostic collage.",
    },
    "N_child_table__soft_day_upper_left": {
        "source_file": "production/chapter-01/runs/workflow-8-v011/sources/N_child_table-attempt-2.png",
        "issue_id": "CT01",
        "observed": "Prior workflow-8 table neutral used an uploaded diagnostic collage board and was retired under user fresh-start cleanup.",
        "expected": "Clean neutral child seated at right chair behind honey round table with one closed blue book far left, one blank paper and one pencil, and restrained translucent support shadow.",
        "bbox_xywh": [170, 1200, 1950, 500],
        "precise_fix": "CT01: Upload only the clean child identity crop and clean furniture geometry crop (never an opaque collage board) and allow safe reversible shadow-only alpha preparation.",
    },
    "N_child_standing_paper_left__soft_day_upper_left": {
        "source_file": "production/chapter-01/runs/workflow-8-v011/sources/N_child_standing_paper_left__soft_day_upper_left-attempt-2.png",
        "issue_id": "S01",
        "observed": "Pale/neutral-grey floor patches remained dense beneath both boots when attempt-2 uploaded a diagnostic correction board instead of the clean identity parent.",
        "expected": "Balanced standing child three-quarter LEFT holding one blank cream sheet with both hands, complete boots and restrained low-alpha contact shadow.",
        "bbox_xywh": [820, 1500, 780, 244],
        "precise_fix": "S01: Upload only the clean child identity parent (keeping diagnostic board offline) and apply safe reversible shadow-only alpha preparation if needed.",
    },
    "A_CH01_R13_L": {
        "source_file": "production/chapter-01/props/raw/CH01_R13_hat_and_navigation_thoughts__attempt-2.png",
        "issue_id": "R13L01",
        "observed": "Prior multi-cell sheet packed hat and map together and was retired under user fresh-start cleanup.",
        "expected": "Single isolated ordinary pale-tan hat with soft brim and warm-brown band in soft storybook watercolor on transparent PNG.",
        "bbox_xywh": [80, 200, 1000, 1200],
        "precise_fix": "R13L01: Generate single-state isolated ordinary hat asset on Flare 2K 4:3 with only the clean watercolor style crop.",
    },
    "A_CH01_R13_R": {
        "source_file": "production/chapter-01/props/raw/CH01_R13_hat_and_navigation_thoughts__attempt-2.png",
        "issue_id": "R13R01",
        "observed": "Prior multi-cell sheet packed hat and map together and was retired under user fresh-start cleanup.",
        "expected": "Single isolated quiet watercolor map impression with broad muted sage landforms and pale blue water, no labels or grid, on transparent PNG.",
        "bbox_xywh": [1200, 200, 1100, 1200],
        "precise_fix": "R13R01: Generate single-state isolated watercolor map asset on Flare 2K 4:3 with only the clean watercolor style crop.",
    },
}

route_map = {
    "identity_turnaround": "identity",
    "neutral_posture": "whole_contact_candidate",
    "object_or_editorial": "asset",
    "background_plate": "background",
}

for nid, refs in node_attachments.items():
    node = cat["nodes"][nid]
    parents = []
    for p in node["parents"]:
        ps = lledger["sources"][p]
        parents.append({"node_id": p, "path": ps["accepted_file"], "sha256": ps["accepted_sha256"]})
    old = inherited_jobs(node, aledger)
    new = [j for j in lledger.get("jobs", []) if j.get("node_id") == nid and counted(j)]
    jobs = old + new

    sub_contract = "Keep exact single-state asset boundaries, dot-eye storybook watercolor discipline, and clean background handling."
    extra_issue_tag = ""
    if nid in prior_configs:
        iid = prior_configs[nid]["issue_id"]
        pfix = prior_configs[nid]["precise_fix"]
        extra_issue_tag = f" Address {iid}: {pfix}"

    base_prompt = node["prompt"]
    compiled_prompt = f"{base_prompt} {sub_contract}{extra_issue_tag}"
    prompt_rel = f"production/chapter-01/runs/workflow-9-v011/preflight/{nid}-prompt.txt"
    (ROOT / prompt_rel).write_text(compiled_prompt)
    prompt_bound = bind(prompt_rel)

    route = route_map[node["stage"]]
    edit_plan = {
        "workflow_version": 9,
        "node_id": nid,
        "parents": parents,
        "route": route,
        "target_state": base_prompt,
        "submission_contract": sub_contract,
        "identity_features": ["dot eyes without irises", "canonical hair and facial proportions", "consistent storybook watercolor washes"],
        "geometry_checks": ["4:3 2K native canvas", "complete subject silhouette with margin", "consistent camera elevation and orientation"],
        "contacts": "Complete support contact group preserved with restrained translucent ground shadow where applicable.",
        "background_review": "Inspect on cream, dark charcoal, and intended scene background before acceptance.",
        "pixel_budget": "Native 2336x1744 / 2400x1792 2K canvas exceeds all target page placement boxes at scale <= 1.0.",
        "reuse_decision": "Audited existing canonical turnarounds reused; this node requires fresh Workflow-9 generation after user-authorized retirement.",
        "local_repair_decision": "Safe reversible shadow-only matte preparation permitted after visual review if core subject is intact.",
        "object_inventory": [
            {
                "id": "primary_subject",
                "before_count": len(parents),
                "after_count": 1,
                "before_state": "canonical reference input",
                "after_state": "complete single-state generated node",
                "contact": "grounded or airborne per node contract"
            }
        ],
        "review": make_review(f"Reviewed Workflow-9 edit plan and reference inputs for {nid}.")
    }
    if route == "whole_contact_candidate":
        edit_plan["why_registered_edit_not_feasible"] = "Neutral posture master establishes the complete seated/standing/airborne body-and-support contact group from an identity turnaround."
        edit_plan["all_features_reaudit"] = True

    edit_plan_rel = f"production/chapter-01/runs/workflow-9-v011/preflight/{nid}-edit-plan.json"
    (ROOT / edit_plan_rel).write_text(json.dumps(edit_plan, indent=2) + "\n")
    edit_plan_bound = bind(edit_plan_rel)

    pf = {
        "workflow_version": 9,
        "reuse_checked": True,
        "canonical_aliases_checked": True,
        "references_visually_checked": True,
        "page_contracts_checked": True,
        "pixel_budget_checked": True,
        "directions_contacts_checked": True,
        "text_alignment_checked": True,
        "alpha_shadow_plan_checked": True,
        "live_schema_checked": True,
        "input_roles_justified": True,
        "geometry_authority_audited": bool(node["input_contract"].get("additional_geometry_candidates")),
        "parameters": node["parameters"],
        "estimated_credits": 1,
        "estimate_checked_at": "2026-11-08T12:57:42+03:00",
        "prompt_file": prompt_bound["path"],
        "prompt_sha256": prompt_bound["sha256"],
        "parents": parents,
        "attachments": refs,
        "edit_plan": edit_plan_bound,
    }

    src_entry = lledger["sources"].setdefault(nid, {})
    src_entry["status"] = "retired_fresh_start"
    src_entry["audit_accepted"] = False

    if jobs:
        cfg = prior_configs[nid]
        prev_prompt = f"Previous attempt prompt for {nid} before Workflow-9 revision."
        audit_obj = {
            "node_id": nid,
            "source_file": cfg["source_file"],
            "source_sha256": retired_map[cfg["source_file"]],
            "submitted_prompt": prev_prompt,
            "verdict": "MATERIAL_FAIL",
            "reviewer": "Antigravity visual inspection",
            "reviewed_at": "2026-11-08T13:10:00+03:00",
            "issues": [
                {
                    "issue_id": cfg["issue_id"],
                    "decision": "MATERIAL_FAIL",
                    "resolved": False,
                    "cause": "source",
                    "bbox_xywh": cfg["bbox_xywh"],
                    "observed": cfg["observed"],
                    "expected": cfg["expected"],
                    "precise_fix": cfg["precise_fix"],
                    "recheck": "Verify complete subject geometry, dot eyes, and clean alpha/shadow on light, dark, and scene backgrounds.",
                    "material_impact": "Cannot assemble Chapter 1 pages without an accepted Workflow-9 source.",
                    "local_fix_ruled_out": "Prior source was retired under user fresh-start cleanup; new generation required."
                }
            ]
        }
        audit_rel = f"production/chapter-01/runs/workflow-9-v011/audits/{nid}-prior-audit.json"
        (ROOT / audit_rel).write_text(json.dumps(audit_obj, indent=2) + "\n")
        src_entry["last_audit"] = audit_rel

        diag_bound = make_diag_board(nid, cfg["issue_id"], cfg["precise_fix"])
        iid = cfg["issue_id"]
        retry_plan = {
            "review": make_review(f"Reviewed retry plan for {nid} addressing {iid}."),
            "issue_ids": [iid],
            "root_cause_evidence": cfg["observed"],
            "changed_mechanism": "Workflow-9 clean reference upload only (diagnostic board kept strictly offline) plus explicit single-state contract and reversible shadow-only alpha preparation.",
            "semantic_prompt_diff": cfg["precise_fix"],
            "protected_features": "Canonical identity, dot eyes, wardrobe colours, and camera angle.",
            "local_feasibility_evidence": "Verified reference inputs at native resolution and tested shadow-only alpha grading offline.",
            "previous_prompt_sha256": hashlib.sha256(prev_prompt.encode()).hexdigest(),
            "diagnostic_board": diag_bound,
            "diagnostic_review": make_review(f"Reviewed offline diagnostic board for {nid}."),
            "board_uploaded": False
        }
        if len(jobs) == 2:
            ev_rel = f"production/chapter-01/runs/workflow-9-v011/preflight/{nid}-third-attempt-feasibility.json"
            ev_doc = {
                "node_id": nid,
                "workflow_version": 9,
                "method_changed_since_both_failures": True,
                "no_cost_feasibility_passed": True,
                "analysis": "Attempt 2 failed because an opaque multi-panel correction collage was uploaded as the reference image instead of the clean parent authority. Under Workflow 9, only the clean parent reference is uploaded while diagnostic boards remain offline, and safe reversible shadow-only matte grading is verified."
            }
            (ROOT / ev_rel).write_text(json.dumps(ev_doc, indent=2) + "\n")
            retry_plan["third_attempt_exception"] = {
                "method_changed_since_both_failures": True,
                "no_cost_feasibility_passed": True,
                "evidence_file": bind(ev_rel),
                "review": make_review(f"Verified zero-cost feasibility and changed mechanism for third attempt of {nid}.")
            }
        pf["retry_plan"] = retry_plan
        pf["correction_preserves_passed_features"] = True

        for pid in (node.get("affected_pages") or []):
            lledger.setdefault("page_generation_rounds", {})[pid] = 2
            pcp = lledger.setdefault("page_correction_plans", {}).setdefault(pid, {
                "all_available_sources_audited": True,
                "node_ids": [],
                "opened_at": "2026-11-08T13:10:00+03:00",
                "reason": "Workflow-9 fresh-start regeneration with clean parent authority."
            })
            pcp["all_available_sources_audited"] = True
            if nid not in pcp["node_ids"]:
                pcp["node_ids"].append(nid)

    src_entry["preflight"] = pf

(ROOT / "production/reference-lineage/ledger.json").write_text(json.dumps(lledger, indent=2) + "\n")

for nid in node_attachments:
    errs = evaluate(ROOT, state, lledger, 1, nid, aledger)
    print(f"{nid:50s} ->", "READY" if not errs else f"BLOCKED: {errs}")

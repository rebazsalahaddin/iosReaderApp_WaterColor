"""Read-only workflow-9 gate. No generation, reservation, or inferred approval."""
from pathlib import Path
import argparse,hashlib,json
from workflow9_checks import finite_cost, budget_errors, plan_errors, retry_errors, review_ok
ROOT=Path(__file__).resolve().parents[2]
LIVE={'reserved','submission_unknown','submitted','running'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def internal(root,s):
 if not isinstance(s,str) or Path(s).is_absolute():raise ValueError('Expected root-relative file')
 p=(root/s).resolve()
 if not p.is_relative_to(root.resolve()):raise ValueError('Outside project')
 return p
def read(root,p):return json.loads(internal(root,p).read_text())
def counted(j):return not(j.get('status')=='rejected_before_submission' and j.get('no_job_no_charge_receipt') and not j.get('job_id'))
def inherited_jobs(node,legacy):return [j for j in legacy.get('jobs',[]) if node.get('legacy_request') and j.get('request_id')==node['legacy_request'] and counted(j)]
def evaluate(root,state,ledger,chapter,nid,legacy=None):
 errors=[]
 def check(ok,msg):
  if not ok:errors.append(msg)
 def bound_file(item,label):
  try:
   p=internal(root,item.get('path'));check(p.is_file() and digest(p)==item.get('sha256'),label+' bytes missing/changed');return p
  except (OSError,ValueError,TypeError):errors.append(label+' safe path/hash missing');return None
 cat=read(root,'production/reference-lineage/catalog.json');nodes=cat['nodes'];legacy=legacy if legacy is not None else read(root,'production/agent-ledger.json')
 pending=root/'production/workflow-9/cleanup-pending.json'
 if pending.exists():
  cleanup=json.loads(pending.read_text())
  check(not (cleanup.get('status')=='incomplete' and chapter in cleanup.get('chapters',[])),'Chapter cleanup incomplete; do not generate from retired artwork')
 if nid not in nodes:return ['Unknown lineage node. Old request cards cannot be submitted; use the mapped canonical node.']
 n=nodes[nid];source=ledger.get('sources',{}).get(nid,{});pf=source.get('preflight',{})
 check(n.get('canonical_budget_key',nid)==nid,'Unregistered canonical budget identity; resolve aliases before execution')
 check(pf.get('workflow_version')==9,'Stale preflight: workflow 9 review required')
 plan=read(root,f'production/chapter-{chapter:02}/agent-run-plan.json')
 check(nid in plan.get('lineage_execution_order',[]),'Node outside active chapter closure')
 check(n['stage']!='local_assembly','This asset is local assembly, not a paid generation')
 check(state.get('status')=='running' and state.get('active_chapter')==chapter,'No active chapter execution authorization')
 check(any(a.get('chapter')==chapter and a.get('user_message') and a.get('recorded_at') for a in state.get('execution_authorizations',[])),'Missing real execution request')
 if chapter>1:
  previous=state.get('chapter_runs',{}).get(str(chapter-1),{})
  check(any(a.get('chapter')==chapter-1 and a.get('continue_to_chapter')==chapter and a.get('user_message') and a.get('approved_delivery_sha256') and a['approved_delivery_sha256']==previous.get('delivery_sha256') for a in state.get('chapter_approvals',[])),'Previous delivered chapter needs manual approval for this continuation')
 old=inherited_jobs(n,legacy);new=[j for j in ledger.get('jobs',[]) if j.get('node_id')==nid and counted(j)];jobs=old+new
 check(len(jobs)<3,'Three-attempt limit exhausted, including historical sheet attempts')
 check(not any(j.get('status') in LIVE for j in jobs),'Reconcile existing live/unknown/reserved attempt')
 check(not any(j.get('status') in LIVE for j in ledger.get('jobs',[])+legacy.get('jobs',[])),'One-job concurrency cap; reconcile any live/unknown/reserved job')
 check(source.get('status')!='accepted','Reuse accepted source; no cosmetic regeneration')
 for k in ['reuse_checked','canonical_aliases_checked','references_visually_checked','page_contracts_checked','pixel_budget_checked','directions_contacts_checked','text_alignment_checked','alpha_shadow_plan_checked','live_schema_checked']:
  check(pf.get(k) is True,'Missing preflight: '+k)
 check(pf.get('parameters')==n['parameters'],'Model/output settings differ from exact node contract')
 estimate=pf.get('estimated_credits');check(finite_cost(estimate) and pf.get('estimate_checked_at'),'Missing live credit estimate')
 budget=state.get('chapter_runs',{}).get(str(chapter),{}).get('credit_budget')
 check(finite_cost(budget) and budget>0,'Missing finite chapter credit budget')
 if finite_cost(budget):
  costs=[j.get('actual_credits') if j.get('actual_credits') is not None else j.get('estimated_credits') for j in ledger.get('jobs',[])+legacy.get('jobs',[]) if j.get('chapter')==chapter and counted(j)]
  check(all(finite_cost(c) for c in costs),'Unknown chapter cost must be reconciled')
  check(finite_cost(budget) and finite_cost(estimate) and all(finite_cost(c) for c in costs) and sum(costs)+estimate<=budget,'Chapter credit budget exceeded')
 prompt_path=bound_file({'path':pf.get('prompt_file'),'sha256':pf.get('prompt_sha256')},'Frozen prompt')
 prompt=prompt_path.read_text() if prompt_path and prompt_path.is_file() else ''
 check(n['prompt'] in prompt,'Current semantic node brief missing from compiled prompt')
 errors.extend(budget_errors(state.get('chapter_runs',{}).get(str(chapter),{}).get('spend_window'),ledger.get('jobs',[])+legacy.get('jobs',[]),nid,estimate))
 parents=[]
 for parent in n['parents']:
  ps=ledger.get('sources',{}).get(parent,{})
  check(ps.get('status')=='accepted' and ps.get('audit_accepted') is True,'Unaccepted parent: '+parent)
  bound_file({'path':ps.get('accepted_file'),'sha256':ps.get('accepted_sha256')},'Accepted parent '+parent)
  try:
   audit=read(root,ps.get('audit_file'))
   check(audit.get('node_id')==parent and audit.get('source_sha256')==ps.get('accepted_sha256') and audit.get('verdict') in ['PASS','PASS_WITH_NOTE'] and audit.get('reviewer') and audit.get('reviewed_at'),'Parent audit not bound/accepted: '+parent)
   required=['identity','native_geometry','alpha','shadow'] if nodes[parent]['stage']=='neutral_posture' else ['identity','native_geometry']
   for k in required:check(audit.get('checks',{}).get(k,{}).get('verdict') in ['PASS','PASS_WITH_NOTE','NOT_APPLICABLE'] and audit['checks'][k].get('evidence'),'Missing parent audit '+k)
  except (ValueError,TypeError,OSError):errors.append('Missing parent audit: '+parent)
  parents.append({'node_id':parent,'path':ps.get('accepted_file'),'sha256':ps.get('accepted_sha256')})
 check(pf.get('parents',[])==parents,'Parent IDs/files/hashes mismatch')
 if n['stage']=='expression_variant':
  check(len(n['parents'])==1 and nodes[n['parents'][0]]['stage']=='neutral_posture','Variant must derive directly from ONE neutral, never a sibling')
  check(pf.get('shadow_preservation_plan') and pf.get('allowed_change_regions'),'Missing protected shadow / allowed edit regions')
 refs=pf.get('attachments',[])
 for r in refs:
  bound_file(r,'Uploaded reference');check(r.get('media_id'),'Missing confirmed uploaded media ID')
 # The plan is hash-bound before submission, not invented after a return.
 try:
  plan_path=bound_file(pf.get('edit_plan',{}),'Workflow-9 edit plan')
  edit_plan=json.loads(plan_path.read_text()) if plan_path else {}
  errors.extend(plan_errors(root,edit_plan,n,parents))
  check(bool(edit_plan.get('submission_contract')) and edit_plan['submission_contract'] in prompt,'Measured submission contract missing from prompt')
 except (ValueError,TypeError,OSError):errors.append('Missing/invalid workflow-9 edit plan')
 if n['stage']=='expression_variant':
  check(len(refs)==1 and bool(parents) and refs[0].get('path')==parents[0]['path'] and refs[0].get('sha256')==parents[0]['sha256'],'Variant must upload exactly the CLEAN accepted neutral master, including retries')
  parent=n['parents'][0]
  canary=plan.get('family_canaries',{}).get(parent) or cat.get('family_canaries',{}).get(parent)
  check(bool(canary),'Missing designated family canary')
  if nid!=canary:
   passed=ledger.get('family_canaries',{}).get(parent,{})
   cs=ledger.get('sources',{}).get(canary,{})
   check(passed.get('node_id')==canary and passed.get('parent_sha256')==parents[0]['sha256'] and cs.get('status')=='accepted' and cs.get('audit_accepted') is True and passed.get('accepted_sha256')==cs.get('accepted_sha256') and review_ok(passed.get('page_review')),'Family canary needs accepted source and composed-page review before siblings')
   bound_file(passed.get('page_evidence',{}),'Canary composed-page evidence')
   bound_file({'path':cs.get('accepted_file'),'sha256':cs.get('accepted_sha256')},'Canary accepted source')
 else:
  check(len(refs)<=n['input_contract'].get('max_images',1),'Too many foundation references')
  for p in parents:check(any(r.get('path')==p['path'] and r.get('sha256')==p['sha256'] for r in refs),'Foundation omitted identity parent')
  check(pf.get('input_roles_justified') is True,'Foundation authority roles need audit')
  if n['input_contract'].get('additional_geometry_candidates'):check(pf.get('geometry_authority_audited') is True and len(refs)==len(parents)+1,'Missing exact essential prop/furniture authority')
 if jobs:
  try:last_audit=read(root,source.get('last_audit'))
  except (ValueError,TypeError,OSError):last_audit={};errors.append('Missing actual previous-attempt audit')
  errors.extend(retry_errors(root,pf,last_audit,jobs,parents,prompt))
  check(pf.get('correction_preserves_passed_features') is True,'Retry must protect passed features')
  for pid in n.get('affected_pages',[]):
   if pid in plan['page_order']:
    c=ledger.get('page_correction_plans',{}).get(pid,{})
    check(ledger.get('page_generation_rounds',{}).get(pid,1)<=3 and c.get('all_available_sources_audited') and nid in c.get('node_ids',[]) and c.get('opened_at'),'Missing consolidated page correction plan: '+pid)
 return errors

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--chapter',type=int,required=True);p.add_argument('--node',required=True);a=p.parse_args()
 try:errors=evaluate(ROOT,read(ROOT,'production/agent-state.json'),read(ROOT,'production/reference-lineage/ledger.json'),a.chapter,a.node)
 except (ValueError,KeyError,OSError,TypeError) as e:errors=['Invalid/missing record: '+str(e)]
 print(json.dumps({'status':'blocked' if errors else 'ready_for_reservation','errors':errors},indent=2));raise SystemExit(bool(errors))
if __name__=='__main__':main()

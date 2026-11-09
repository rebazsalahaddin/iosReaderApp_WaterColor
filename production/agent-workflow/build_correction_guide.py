"""Render local diagnostic/target boards and a complete retry prompt. Never submits jobs."""
from pathlib import Path
import argparse
import hashlib
import json
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
GUIDE = 'production/Visual_Correction_Guide.txt'
DIRECTIONS = {'viewer-left', 'viewer-right', 'front', 'back'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root, value):
    if not isinstance(value, str) or Path(value).is_absolute():
        raise ValueError('Expected root-relative path')
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Path escapes project')
    return path


def box_ok(box, size):
    return (isinstance(box, list) and len(box) == 4
            and all(type(x) in (int, float) and math.isfinite(x) for x in box)
            and min(box[:2]) >= 0 and min(box[2:]) > 0
            and box[0]+box[2] <= size[0] and box[1]+box[3] <= size[1])


def checked_target(root, target):
    if not target.get('authority'):
        raise ValueError('Each correct target needs its approved contract/reference authority')
    mode = target.get('mode')
    if mode == 'orientation_diagram':
        directions = target.get('directions', {})
        if any(directions.get(k) not in DIRECTIONS for k in ['head', 'torso', 'feet']):
            raise ValueError('Orientation requires independent head, torso and feet directions')
        if set(directions) - {'head', 'torso', 'feet', 'chair'}:
            raise ValueError('Unknown orientation part')
        if 'chair' in directions and directions['chair'] not in DIRECTIONS:
            raise ValueError('Invalid chair direction')
        if not target.get('gaze_target'):
            raise ValueError('State the gaze recipient/target')
    elif mode in ['approved_crop', 'local_diagram']:
        p = inside(root, target.get('path'))
        if sha(p) != target.get('sha256'):
            raise ValueError('Correct-target bytes changed')
        with Image.open(p) as im:
            for key in ['crop_xywh', 'feature_bbox_xywh']:
                if not box_ok(target.get(key), im.size):
                    raise ValueError('Correct-target crop/feature bounds invalid')
        x,y,w,h = target['crop_xywh']; a,b,c,d = target['feature_bbox_xywh']
        if not (a >= x and b >= y and a+c <= x+w and b+d <= y+h):
            raise ValueError('Correct feature must remain fully inside its crop')
        if mode == 'local_diagram' and target.get('creation_method') != 'local_programmatic_diagram':
            raise ValueError('Custom diagram must be locally authored, not generated art')
    else:
        raise ValueError('Target must be approved_crop, orientation_diagram or local_diagram')


def text(draw, value, rect, size=28, fill='#263342'):
    """Wrap into a bounded region; reject overflow instead of silently clipping."""
    x,y,w,h = rect; font = ImageFont.load_default(size=size); line_h = size+9
    lines=[]
    for paragraph in str(value).splitlines():
        line=''
        for word in paragraph.split():
            if draw.textlength(word,font=font) > w:
                raise ValueError('An unbroken label is too wide; shorten displayed wording')
            trial=(line+' '+word).strip()
            if draw.textlength(trial,font=font)>w:
                lines.append(line);line=word
            else:line=trial
        lines.append(line)
    if len(lines)*line_h>h:
        raise ValueError('Board text would overflow. Shorten callouts or use fewer issues per sheet.')
    for line in lines:
        draw.text((x,y),line,font=font,fill=fill);y+=line_h


def arrow(draw, start, end, color, width=5):
    draw.line([start,end],fill=color,width=width)
    angle=math.atan2(end[1]-start[1],end[0]-start[0]);length=16
    pts=[end,(end[0]-length*math.cos(angle-.5),end[1]-length*math.sin(angle-.5)),
         (end[0]-length*math.cos(angle+.5),end[1]-length*math.sin(angle+.5))]
    draw.polygon(pts,fill=color)


def crop_panel(canvas, source, crop, feature, rect, color):
    x,y,w,h=rect; cx,cy,cw,ch=crop
    cropped=source.crop((cx,cy,cx+cw,cy+ch)).convert('RGBA')
    backing=Image.new('RGBA',cropped.size,'#f7f8f8')
    region=Image.alpha_composite(backing,cropped).convert('RGB')
    scale=min(w/region.width,h/region.height)
    nw,nh=round(region.width*scale),round(region.height*scale)
    left,top=x+(w-nw)//2,y+(h-nh)//2
    canvas.paste(region.resize((nw,nh),Image.Resampling.LANCZOS),(left,top))
    fx,fy,fw,fh=feature
    # The annotation is a separate overlay. Source pixels on disk are untouched.
    sx,sy=nw/cw,nh/ch
    bounds=(left+(fx-cx)*sx,top+(fy-cy)*sy,left+(fx+fw-cx)*sx,top+(fy+fh-cy)*sy)
    d=ImageDraw.Draw(canvas);d.rectangle(bounds,outline=color,width=5)
    arrow(d,(x+12,y+14),(bounds[0],bounds[1]),color)


def orientation_panel(canvas, target, rect):
    x,y,w,h=rect; d=ImageDraw.Draw(canvas);green='#287450';ink='#526170'
    center=x+w*.22; hy=y+70; feet=y+h-55
    d.ellipse((center-35,hy-36,center+35,hy+36),outline=ink,width=5)
    head=target['directions']['head']
    if head in ['viewer-left','viewer-right']:
        sign=-1 if head=='viewer-left' else 1
        d.line([(center+sign*31,hy-8),(center+sign*53,hy+4),(center+sign*31,hy+13)],fill=ink,width=5)
        d.ellipse((center+sign*18-3,hy-14,center+sign*18+3,hy-8),fill=ink)
    elif head=='front':
        for dx in [-13,13]:d.ellipse((center+dx-3,hy-8,center+dx+3,hy-2),fill=ink)
    # Schematic limbs plus independent labelled arrows, never a replacement face.
    hip=y+h*.62
    torso=target['directions']['torso']
    if torso in ['viewer-left','viewer-right']:
        sign=-1 if torso=='viewer-left' else 1
        d.line([(center,hy+36),(center+sign*24,hy+78),(center,hip)],fill=ink,width=7)
        d.line([(center,hy+36),(center-sign*12,hip),(center,hip)],fill=ink,width=5)
    else:d.line([(center,hy+36),(center,hip)],fill=ink,width=7)
    d.line([(center-50,hy+65),(center+50,hy+65)],fill=ink,width=6)
    foot_direction=target['directions']['feet']
    toe=-20 if foot_direction=='viewer-left' else 20 if foot_direction=='viewer-right' else 0
    for leg in [-25,25]:
        d.line([(center,hip),(center+leg,feet),(center+leg+toe,feet)],fill=ink,width=6)
    entries=[(k,target['directions'][k]) for k in ['head','torso','feet','chair'] if k in target['directions']]
    for n,(part,direction) in enumerate(entries):
        yy=y+20+n*58;xx=x+w*.49
        text(d,part.upper()+': '+direction,(xx,yy,w*.49,42),size=25,fill=green)
        ax=x+w*.38
        if direction in ['viewer-left','viewer-right']:
            sign=-1 if direction=='viewer-left' else 1
            arrow(d,(ax-sign*28,yy+18),(ax+sign*28,yy+18),green)
    text(d,'GAZE: '+target['gaze_target'],(x+w*.38,y+h-68,w*.60,68),size=25,fill=green)


def build(root, spec, output):
    if spec.get('template_only'):
        raise ValueError('Fill the template from actual evidence and remove template_only')
    audit_path=inside(root,spec.get('source_audit'));audit=json.loads(audit_path.read_text())
    if audit.get('attempt') != 1 or not audit.get('job_id') or audit.get('template_only'):
        raise ValueError('A real attempt-1 audit/job is required')
    issues=[i for i in audit.get('issues',[]) if i.get('decision')=='MATERIAL_FAIL' and not i.get('resolved')]
    ids=[i['issue_id'] for i in issues]
    if not ids or len(ids)!=len(set(ids)) or any(i.get('cause')!='source' for i in issues):
        raise ValueError('Need unique unresolved material SOURCE issues; local issues do not justify a retry')
    entries={i['issue_id']:i for i in spec.get('issues',[])}
    if set(entries)!=set(ids) or len(entries)!=len(spec.get('issues',[])):
        raise ValueError('Targets must cover every unresolved material issue exactly once')
    if not spec.get('preserve'):
        raise ValueError('List the observed passing features to preserve')
    source=inside(root,audit.get('source_file'))
    if sha(source)!=audit.get('source_sha256'):raise ValueError('Failed source hash mismatch')
    original=inside(root,spec.get('first_attempt_prompt_file'))
    if sha(original)!=spec.get('first_attempt_prompt_sha256') or sha(original)!=audit.get('prompt_sha256'):
        raise ValueError('Must preserve the complete exact attempt-1 submitted prompt')
    image=Image.open(source).convert('RGB')
    for issue in issues:
        if issue.get('image_dimensions')!=list(image.size) or not box_ok(issue.get('bbox_xywh'),image.size):
            raise ValueError('Issue coordinates must match actual failed-source dimensions')
        for field in ['cell','expected','observed','precise_fix','recheck','contract_reference']:
            if not issue.get(field):raise ValueError('Missing issue field: '+field)
        display=entries[issue['issue_id']].get('display') or {}
        if any(k not in ['observed','expected','precise_fix','recheck'] or not isinstance(v,str) or not v.strip() for k,v in display.items()):
            raise ValueError('Display overrides must be concise nonempty issue callouts')
        checked_target(root,entries[issue['issue_id']]['target'])
    per=spec.get('issues_per_sheet',2)
    if type(per)!=int or per not in (1,2,3):raise ValueError('Use 1, 2 or 3 readable issues per sheet')
    if output.exists():raise ValueError('Use a new output directory; do not overwrite frozen evidence')
    output.mkdir(parents=True)
    rid=audit['request_id']; sheets=[]
    for first in range(0,len(issues),per):
        batch=issues[first:first+per]; canvas=Image.new('RGB',(2400,1792),'#f7f8f8');d=ImageDraw.Draw(canvas)
        text(d,rid+' / ATTEMPT 2 / CORRECTION INSTRUCTIONS ONLY',(40,20,2320,48),size=34)
        text(d,'Original references control identity and art style. Do not render these labels, boxes, arrows or schematic figures.',(40,76,2320,44),size=27)
        row_h=(1600)//len(batch)
        for row,issue in enumerate(batch):
            y=140+row*row_h;h=row_h-22;target=entries[issue['issue_id']]['target']
            text(d,issue['issue_id']+' / CELL '+str(issue['cell'])+' / observed region '+str(issue['bbox_xywh']),(40,y,2320,42),size=28)
            text(d,'OBSERVED ERROR - REAL FAILED RETURN',(50,y+46,1100,42),size=28,fill='#b13939')
            text(d,'REQUIRED TARGET - INSTRUCTION ONLY',(1250,y+46,1100,42),size=28,fill='#287450')
            image_h=max(310,h-330)
            x0,y0,bw,bh=issue['bbox_xywh'];pad=max(25,round(max(bw,bh)*.22))
            left=max(0,x0-pad);top=max(0,y0-pad);right=min(image.width,x0+bw+pad);bottom=min(image.height,y0+bh+pad)
            crop_panel(canvas,image,[left,top,right-left,bottom-top],issue['bbox_xywh'],(50,y+90,1100,image_h),'#b13939')
            if target['mode']=='orientation_diagram':orientation_panel(canvas,target,(1250,y+90,1100,image_h))
            else:
                with Image.open(inside(root,target['path'])) as correct:
                    crop_panel(canvas,correct,target['crop_xywh'],target['feature_bbox_xywh'],(1250,y+90,1100,image_h),'#287450')
            ty=y+100+image_h
            display=entries[issue['issue_id']].get('display') or {}
            text(d,'Observed: '+display.get('observed',issue['observed'])+'\nExpected: '+display.get('expected',issue['expected']),(50,ty,1100,h-(ty-y)),size=27)
            text(d,'Fix: '+display.get('precise_fix',issue['precise_fix'])+'\nRecheck: '+display.get('recheck',issue['recheck']),(1250,ty,1100,h-(ty-y)),size=27)
        text(d,'Red = diagnose. Green = required correction. Preserve all listed passing features. Labels and drawings are not output content.',(40,1740,2320,42),size=25)
        p=output/f'correction-board-{len(sheets)+1:02d}.png';canvas.save(p)
        sheets.append(dict(path=p.relative_to(root).as_posix(),sha256=sha(p),issue_ids=[i['issue_id'] for i in batch],dimensions=[2400,1792],role='instruction_only',creation_method='local_programmatic_annotation'))
    m=json.loads((root/'production/full-book-rebuild-r6/book-production-manifest.json').read_text())
    base_count=len(m['requests'][rid]['attachments'])
    block=[f'SECOND AND FINAL ATTEMPT FOR {rid}. Correct ALL listed source issues together; retain all passing features.',
           f'Images 1-{base_count}: original required identity/style/geometry references, unchanged and in their original order.']
    for n,sheet in enumerate(sheets,base_count+1):
        block.append(f'Image {n}: correction board {Path(sheet["path"]).name}; issues {", ".join(sheet["issue_ids"])}. Instruction only, never an art-style or identity master.')
    block += [f'Image {base_count+len(sheets)+1} LAST: untouched failed attempt 1. Diagnostic only. Preserve its passing features but do not repeat its marked errors.',
              'For ONLY the named issues, the REQUIRED targets and correction block supersede conflicting directions in the original prompt or failed return. All unrelated original requirements still apply. Approved references retain identity and art-style authority.',
              'Do not paint guide boxes, arrows, labels, schematic style or panel layouts into the result. Keep all locked model settings, source cells and original art requirements.']
    for issue in issues:
        target=entries[issue['issue_id']]['target']
        block += [f"{issue['issue_id']} / {issue['cell']} / source box {issue['bbox_xywh']}: OBSERVED: {issue['observed']} REQUIRED: {issue['expected']} FIX: {issue['precise_fix']} RECHECK: {issue['recheck']} TARGET AUTHORITY: {target['authority']}."]
        if target['mode']=='orientation_diagram':block.append('Orientation-only target: '+json.dumps(target['directions'])+'; gaze '+target['gaze_target']+'. Original references still control facial features and identity.')
    block += ['PRESERVE: '+'; '.join(spec['preserve'])+'.','Return one corrected coherent reference sheet, not the diagnostic board.']
    correction='\n\n'.join(block)+'\n';cp=output/'correction-block.txt';cp.write_text(correction)
    prompt=output/'retry-prompt.txt';prompt.write_text(correction+'\nCOMPLETE ORIGINAL SUBMITTED PROMPT\n\n'+original.read_text())
    sp=output/'correction-spec.json';sp.write_text(json.dumps(spec,indent=2)+'\n')
    manifest=dict(protocol_version=1,request_id=rid,based_on_attempt=1,attempt_to_submit=2,prior_job_id=audit['job_id'],source_audit=spec['source_audit'],source_audit_sha256=sha(audit_path),source_file=audit['source_file'],source_sha256=sha(source),first_attempt_prompt_file=spec['first_attempt_prompt_file'],first_attempt_prompt_sha256=sha(original),spec_file=sp.relative_to(root).as_posix(),spec_sha256=sha(sp),issues=[dict(issue_id=i['issue_id'],cell=i['cell'],bbox_xywh=i['bbox_xywh'],expected=i['expected'],observed=i['observed'],precise_fix=i['precise_fix'],recheck=i['recheck'],target=entries[i['issue_id']]['target']) for i in issues],preserve=spec['preserve'],sheets=sheets,correction_block_file=cp.relative_to(root).as_posix(),correction_block_sha256=sha(cp),retry_prompt_file=prompt.relative_to(root).as_posix(),retry_prompt_sha256=sha(prompt),review=dict(status='needs_visual_review',reviewer=None,reviewed_at=None,issue_ids_checked=[],labels_legible=False,targets_match_contract=False,original_features_preserved=False,instruction_only=False,evidence=None))
    (output/'correction-guide.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def validate_retry_guide(root, preflight, audit, audit_path, prior_job, rid):
    """Fail closed before a paid visual retry; visual truth still requires the review."""
    errors=[]
    def check(ok,msg):
        if not ok:errors.append(msg)
    try:
        path=inside(root,preflight.get('visual_correction_guide'))
        check(sha(path)==preflight.get('visual_correction_guide_sha256'),'Visual correction manifest changed/missing')
        g=json.loads(path.read_text());issues=[i for i in audit.get('issues',[]) if i.get('decision')=='MATERIAL_FAIL' and not i.get('resolved')]
        ids=[i['issue_id'] for i in issues]
        check(g.get('protocol_version')==1 and g.get('request_id')==rid and g.get('based_on_attempt')==1 and g.get('attempt_to_submit')==2,'Wrong visual correction request/attempt')
        check(audit.get('request_id')==rid and audit.get('attempt')==1 and audit.get('job_id')==prior_job.get('job_id')==g.get('prior_job_id') and bool(prior_job.get('job_id')),'Guide is not tied to the actual first job')
        check(inside(root,g.get('source_audit'))==audit_path and g.get('source_audit_sha256')==sha(audit_path),'Guide is based on a stale/different audit')
        check(g.get('source_file')==audit.get('source_file') and g.get('source_sha256')==audit.get('source_sha256')==sha(inside(root,g.get('source_file'))),'Guide failed source differs from audit')
        for fk,hk in [('first_attempt_prompt_file','first_attempt_prompt_sha256'),('spec_file','spec_sha256'),('correction_block_file','correction_block_sha256'),('retry_prompt_file','retry_prompt_sha256')]:
            check(sha(inside(root,g.get(fk)))==g.get(hk),'Frozen guide input/output changed: '+fk)
        check(g.get('first_attempt_prompt_sha256')==prior_job.get('prompt_sha256')==audit.get('prompt_sha256'),'Complete prior submitted prompt is not preserved')
        check(g.get('retry_prompt_file')==preflight.get('prompt_file') and g.get('retry_prompt_sha256')==preflight.get('prompt_sha256'),'Frozen retry prompt does not match visual correction package')
        prompt=inside(root,g['retry_prompt_file']).read_text()
        check(inside(root,g['first_attempt_prompt_file']).read_text() in prompt and inside(root,g['correction_block_file']).read_text() in prompt,'Original prompt or correction block omitted')
        check(ids and len(ids)==len(set(ids)),'Missing/duplicate material issue IDs')
        mapped={i['issue_id']:i for i in g.get('issues',[])}
        check(set(mapped)==set(ids) and len(mapped)==len(g.get('issues',[])),'Visual correction does not cover every material issue exactly once')
        for issue in issues:
            item=mapped.get(issue['issue_id'],{})
            for key in ['cell','bbox_xywh','expected','observed','precise_fix','recheck']:
                check(item.get(key)==issue.get(key),'Guide disagrees with audited issue: '+issue['issue_id']+':'+key)
            checked_target(root,item.get('target',{}))
            check(issue['issue_id'] in prompt and issue['precise_fix'] in prompt,'Issue/fix missing from complete retry prompt')
        sheets=g.get('sheets',[]);covered=[]
        for sheet in sheets:
            fp=inside(root,sheet.get('path'))
            check(sha(fp)==sheet.get('sha256'),'Correction board changed/missing')
            with Image.open(fp) as im:check(im.format=='PNG' and list(im.size)==sheet.get('dimensions'),'Invalid correction-board image')
            check(sheet.get('role')=='instruction_only' and sheet.get('creation_method')=='local_programmatic_annotation','Correction board has wrong role/origin')
            covered.extend(sheet.get('issue_ids',[]))
        check(sorted(covered)==sorted(ids),'Boards omit or duplicate material issues')
        review=g.get('review',{})
        check(review.get('status')=='approved_for_retry' and review.get('reviewer') and review.get('reviewed_at') and review.get('evidence'),'Correction boards have not been visually reviewed')
        check(sorted(review.get('issue_ids_checked',[]))==sorted(ids),'Visual review does not cover every issue')
        check(all(review.get(k) is True for k in ['labels_legible','targets_match_contract','original_features_preserved','instruction_only']),'Visual correction legibility/target/preservation review incomplete')
        check(bool(g.get('preserve')),'No passing features protected')
        check(preflight.get('reference_capacity_checked') is True and preflight.get('reference_capacity_evidence'),'Reference capacity/roles not checked for visual retry')
        refs=preflight.get('attachments',[])
        q=json.loads((root/'production/full-book-rebuild-r6/book-production-manifest.json').read_text())['requests'][rid]
        check(len(refs)==len(q['attachments'])+len(sheets)+1,'Retry needs originals, all correction boards, then untouched failure')
        for actual,sheet in zip(refs[len(q['attachments']):],sheets):
            check(actual.get('path')==sheet['path'] and actual.get('sha256')==sheet['sha256'] and actual.get('media_id'),'Correction board attachment order/hash/media ID mismatch')
        limit=preflight.get('max_reference_images')
        check(limit is None or (type(limit)==int and len(refs)<=limit),'Published reference capacity exceeded')
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc:
        errors.append('Missing/invalid mandatory visual correction guide: '+str(exc))
    return errors


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--spec',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    spec=json.loads(inside(ROOT,args.spec).read_text());g=build(ROOT,spec,inside(ROOT,args.output))
    print(json.dumps(dict(status='needs_visual_review',boards=len(g['sheets']),issues=len(g['issues']),output=args.output,jobs_submitted=0),indent=2))


if __name__=='__main__':main()

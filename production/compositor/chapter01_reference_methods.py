"""Reusable local preparation and composition functions from the inspected Chapter1 batch."""
from pathlib import Path
import json,hashlib
import numpy as np
import cv2
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFilter

def configure(root, review, manifest):
    global ROOT,RAW,OUT,PREP,PAGES,LAYERS,M,SIZE,PAPER,PREP_VERSION,assets,marks,SURFACES
    ROOT=Path(root);RAW=ROOT/'production/chapter-01/props/raw';OUT=Path(review)
    PREP=OUT/'prepared';PAGES=OUT/'illustrations';LAYERS=OUT/'pages'
    for p in [OUT,PREP,PAGES,LAYERS]:p.mkdir(parents=True,exist_ok=True)
    M=manifest;SIZE=(2400,1792);PAPER=(253,250,243,255);PREP_VERSION='corrections-v001'
    assets={};marks={};SURFACES={}

def savej(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def raw(rid):
    q=M['requests'][rid];p=RAW/q['output']
    return p if p.exists() else RAW/q['output'][1:]

def prepare(rid,cell='ONE'):
    q=M['requests'][rid];crop=(0,0,2400,1792) if cell=='ONE' else (0,0,1200,1792) if cell=='L' else (1200,0,2400,1792)
    name=rid+'_'+cell
    meta=PREP/f'CH01_{name}__preparation-{PREP_VERSION}.json'
    if meta.exists():
        d=json.loads(meta.read_text());assert d['sha256']==sha(raw(rid))
        return {'image':Image.open(ROOT/d['prepared']).convert('RGBA'),'meta':d,'name':name}
    # Actual returns contain opaque purple-brown ink above the older batch's
    # chroma8 threshold. Measure those interiors; do not punch holes through them.
    full=np.asarray(Image.open(raw(rid)).convert('RGB'),np.float32)
    margin=np.concatenate([full[:40].reshape(-1,3),full[-40:].reshape(-1,3),full[:,:40].reshape(-1,3),full[:,-40:].reshape(-1,3)])
    bgmedian=np.median(margin,axis=0);bgth=float(np.percentile(np.minimum(margin[:,0],margin[:,2])-margin[:,1],1)-25)
    x0,y0,x1,y1=crop;rgb=full[y0:y1,x0:x1];chroma=np.minimum(rgb[:,:,0],rgb[:,:,2])-rgb[:,:,1]
    fg=(chroma<=30)|((chroma<=70)&(rgb.max(2)<210));bg=chroma>=bgth
    dfg,fi=ndimage.distance_transform_edt(~fg,return_indices=True);dbg,bi=ndimage.distance_transform_edt(~bg,return_indices=True)
    fc=rgb[tuple(fi)];bc=rgb[tuple(bi)];direction=fc-bc
    alpha=np.clip(np.sum((rgb-bc)*direction,2)/np.maximum(np.sum(direction*direction,2),1),0,1)
    alpha[dfg>8]=0;alpha[bg]=0;alpha[fg]=1
    alpha[alpha<.012]=0;alpha[alpha>.995]=1
    edge=(alpha>0)&(alpha<1);clean=rgb.copy()
    safe=fg&((chroma<=15)|((chroma<=40)&(rgb.max(2)<180)&(dbg>2)));_,safe_indices=ndimage.distance_transform_edt(~safe,return_indices=True)
    safe_color=rgb[tuple(safe_indices)]
    rim=(alpha>0)&(ndimage.distance_transform_edt(alpha>0)<5)&(chroma>25)
    # Remove observed key contamination only in the narrow silhouette band.
    # Internal purple-brown metal/ink is retained, including previously lost patches.
    clean[edge|rim]=safe_color[edge|rim]
    boundary=(alpha>0)&(ndimage.distance_transform_edt(alpha>0)<5)
    excess=np.maximum(np.minimum(clean[:,:,0],clean[:,:,2])-clean[:,:,1]-3,0)
    spill=boundary&(excess>5)
    # The inspected outer ink has key-colour spill; remove only its red+blue
    # excess over the green channel within this five-pixel edge band.
    clean[:,:,0][spill]-=excess[spill];clean[:,:,2][spill]-=excess[spill]
    rim|=spill
    motion_pixels=0
    if rid in ['CH01_S17','CH01_S18']:
        yy,xx=np.mgrid[:rgb.shape[0],:rgb.shape[1]]
        roi=((xx>315)&(xx<565)&(yy>470)&(yy<1320)) if rid.endswith('17') else ((xx>1890)&(xx<2220)&(yy>380)&(yy<1390))
        motion=roi&(~fg)&(rgb[:,:,1]>8)&(dfg>8)
        # Observed light motion strokes are mixed with the flat key field.
        # Recover their coverage/colour from that field, never invent new strokes.
        neutral_green=225.0
        ma=np.clip((rgb[:,:,1]-bgmedian[1])/(neutral_green-bgmedian[1]),0,1)
        recover=(rgb-bgmedian[None,None,:]*(1-ma[:,:,None]))/np.maximum(ma[:,:,None],.01)
        alpha[motion]=ma[motion];clean[motion]=np.clip(recover[motion],0,255);motion_pixels=int(motion.sum())
    clean[alpha==0]=0
    rgba=np.dstack([np.rint(clean).astype(np.uint8),np.rint(alpha*255).astype(np.uint8)])
    yy,xx=np.where(alpha>.02);bounds=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
    local=(max(0,bounds[0]-12),max(0,bounds[1]-12),min(rgb.shape[1],bounds[2]+12),min(rgb.shape[0],bounds[3]+12))
    image=Image.fromarray(rgba).crop(local);path=PREP/f'CH01_{name}__rgba-{PREP_VERSION}.png';image.save(path);image.getchannel('A').save(PREP/f'CH01_{name}__mask-{PREP_VERSION}.png')
    d={'source':str(raw(rid).relative_to(ROOT)),'sha256':sha(raw(rid)),'source_dimensions':[2400,1792],'source_cell':list(crop),'source_crop':[local[0]+x0,local[1]+y0,local[2]+x0,local[3]+y0],'painted_bounds_in_source':[bounds[0]+x0,bounds[1]+y0,bounds[2]+x0,bounds[3]+y0],'prepared':str(path.relative_to(ROOT)),'background_median_rgb':bgmedian.tolist(),'background_chroma_threshold':bgth,'foreground_policy':'chroma<=30 or dark ink(max channel<210,chroma<=70), verified on actual source interiors; no blanket erosion','matte':'Nearest observed foreground/background colour projection in narrow edge; all enclosed key gaps remain background','edge_despill':'Nearest observed low-chroma foreground only within 5px outer silhouette band; interior purple-brown ink preserved','despilled_rim_pixels':int(rim.sum()),'interior_max_channel_change':float(np.abs(clean[fg&~rim]-rgb[fg&~rim]).max()),'motion_pixels_recovered':motion_pixels,'motion_method':'Coverage recovered from observed green-channel contribution to the flat key; existing motion-only region, no added strokes','status':'prepared; visual inspection required'}
    savej(meta,d);print('Prepared',rid,cell,image.size,flush=True)
    return {'image':image,'meta':d,'name':name}

def pigment(key):
    path=ROOT/M['assets'][key]['canonical'];a=np.asarray(Image.open(path).convert('RGB'),np.float32)
    crop=(485,790,1585,1255) if key=='draw1' else (390,710,1695,1310)
    x0,y0,x1,y1=crop;a=a[y0:y1,x0:x1]
    paper=cv2.morphologyEx(a,cv2.MORPH_CLOSE,np.ones((31,31),np.uint8));paper=cv2.GaussianBlur(paper,(0,0),15)
    relative=np.clip(a/np.maximum(paper,1),0,1)
    seed=(relative.min(2)<.91).astype(np.uint8)
    seed=cv2.dilate(seed,np.ones((3,3),np.uint8))
    n,labels,stats,_=cv2.connectedComponentsWithStats(seed)
    keep=[i for i in range(1,n) if stats[i,cv2.CC_STAT_AREA]>12]
    mask=np.isin(labels,keep).astype(np.float32)
    mask=cv2.dilate(mask,np.ones((3,3),np.uint8));mask=cv2.GaussianBlur(mask,(0,0),.65)
    relative=1-(1-relative)*mask[...,None]
    Image.fromarray(np.uint8(np.rint(relative*255))).save(PREP/f'{key}-relative-pigment.png')
    return relative,{'source':str(path.relative_to(ROOT)),'sha256':sha(path),'source_crop':crop,'strength':1,'method':'Original graphite relative to local source paper; original mark geometry and strength, no redraw or contrast boost.'}

def insert(asset_key,mark_key,progress=False):
    item=assets[asset_key];im=item['image'].copy();a=np.asarray(im).copy()
    rel,source=marks[mark_key];rel=rel.copy()
    if progress:
        # Deliberate incomplete contour: reveal existing left-hand marks only.
        cutoff=int(rel.shape[1]*.46);rel[:,cutoff:]=1
    quad_raw,plane_size=SURFACES[asset_key];pw,ph=plane_size
    plane=np.ones((ph,pw,3),np.float32)
    scale=min(pw*.76/rel.shape[1],ph*.62/rel.shape[0],1)
    mw,mh=round(rel.shape[1]*scale),round(rel.shape[0]*scale)
    mark=cv2.resize(rel,(mw,mh),interpolation=cv2.INTER_AREA)
    px,py=(pw-mw)//2,(ph-mh)//2
    plane[py:py+mh,px:px+mw]=mark
    offset=np.array(item['meta']['source_crop'][:2],np.float32);quad=np.float32(quad_raw)-offset
    h=cv2.getPerspectiveTransform(np.float32([[0,0],[pw-1,0],[pw-1,ph-1],[0,ph-1]]),quad)
    warped=cv2.warpPerspective(plane,h,im.size,flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(1,1,1))
    interior=np.zeros(a.shape[:2],np.uint8);cv2.fillConvexPoly(interior,np.rint(quad).astype(np.int32),255)
    interior=cv2.erode(interior,np.ones((3,3),np.uint8))>0
    rgb=a[:,:,:3].astype(np.int16)
    # Observed paper is warm ivory, so neutral-white-only tests would erase the marks.
    # These measured surface polygons avoid fingers; protect any remaining skin/outline.
    protect=(rgb[:,:,2]>185)&((rgb[:,:,0]-rgb[:,:,2])<45)&(rgb.min(2)>190)
    valid=interior&protect&(a[:,:,3]>250)
    a[valid,:3]=np.rint(a[valid,:3]*warped[valid]).astype(np.uint8)
    name=asset_key.replace(':','_')+'__'+mark_key+('__in_progress' if progress else '')
    rendered=Image.fromarray(a);rendered.save(PREP/(name+'.png'))
    record={**source,'host':asset_key,'paper_quad_raw':quad_raw,'paper_quad_prepared':quad.tolist(),'local_plane_size':plane_size,'mark_fit':[px,py,mw,mh],'incomplete_stage':progress,'changed_pixels':int(np.any(a[:,:,:3]!=np.asarray(im)[:,:,:3],2).sum()),'occlusion':'Measured interior + observed ivory-paper mask; hands, outlines and paper grain retained.'}
    savej(PREP/(name+'-insertion.json'),record)
    return rendered,record

def page_start(pid,bg=None):
    folder=LAYERS/pid;(folder/'layers').mkdir(parents=True,exist_ok=True)
    page=Image.new('RGBA',SIZE,PAPER)
    if bg:
        # All these actual returns are already the exact final canvas size.
        plate=Image.open(raw(bg)).convert('RGBA');assert plate.size==SIZE;page.alpha_composite(plate)
    page.save(folder/'layers/00-background.png')
    return page,{'page':pid,'canvas':list(SIZE),'status':'new component composition; awaiting visual review','background_source':str(raw(bg).relative_to(ROOT)) if bg else 'warm paper','background_uniform_scale':1,'background_position':[0,0],'background_note':'Actual return is 2400×1792; preserved at native size instead of shrinking to the provisional 2K field. No stretch or crop.','placements':[],'layers':['00-background.png'],'drawing_insertions':[],'upscaled_assets':0,'mirrored_assets':0,'generated_images':0}

def place(page,record,asset_key,image,scale,xy,shadow=True,insert_record=None):
    assert scale<=1;item=assets[asset_key];x,y=map(round,xy)
    w,h=round(image.width*scale),round(image.height*scale)
    assert min(x,y)>=0 and x+w<=2400 and y+h<=1792,(asset_key,x,y,w,h)
    resized=image.resize((w,h),Image.Resampling.LANCZOS)
    folder=LAYERS/record['page']/'layers'
    if shadow:
        sh=Image.new('RGBA',SIZE,(0,0,0,0));dr=ImageDraw.Draw(sh)
        dr.ellipse((x+w*.09,y+h-18,x+w*.91,y+h+20),fill=(105,76,55,26))
        sh=sh.filter(ImageFilter.GaussianBlur(12));page.alpha_composite(sh)
        name=f'{len(record["layers"]):02}-contact-shadow.png';sh.save(folder/name);record['layers'].append(name)
    layer=Image.new('RGBA',SIZE,(0,0,0,0));layer.alpha_composite(resized,(x,y));page.alpha_composite(layer)
    name=f'{len(record["layers"]):02}-{asset_key.replace(":","_")}.png';layer.save(folder/name);record['layers'].append(name)
    record['placements'].append({'asset':asset_key,'raw_source':item['meta']['source'],'raw_sha256':item['meta']['sha256'],'source_crop':item['meta']['source_crop'],'prepared':item['meta']['prepared'],'uniform_scale':scale,'position':[x,y],'rendered_size':[w,h],'painted_alpha_bounds':list(layer.getbbox())})
    if insert_record:
        insert_record=dict(insert_record);quad=np.array(insert_record['paper_quad_prepared'])*scale+[x,y];insert_record['paper_quad_final']=quad.tolist();record['drawing_insertions'].append(insert_record)

def save_page(page,record):
    dest=PAGES/(record['page']+'.png');page.convert('RGB').save(dest)
    record['output']=str(dest.relative_to(ROOT));record['output_sha256']=sha(dest)
    record['story_text']=M['chapters']['1']['pages'][record['page']]['source_text']
    savej(LAYERS/record['page']/'layout.json',record)
    page.convert('RGB').resize((1200,896),Image.Resampling.LANCZOS).save(LAYERS/record['page']/'preview.jpg',quality=95)
    print('Composed',record['page'],flush=True)

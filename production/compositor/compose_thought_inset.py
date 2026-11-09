"""Content-first thought composition using original pigment and an adapted EMPTY frame."""
from pathlib import Path
import numpy as np
import cv2
from scipy.ndimage import gaussian_filter
from PIL import Image
from adapt_thought_frame import adapt


def compose(root, scene, cloud_record, *, position, content_width, frame_size, puffs=(), rim_opacity=.68):
    """Keep content size explicit; reject a frame that would require shrinking it."""
    root=Path(root);record=cloud_record;content=record['content']
    frame_source=record.get('prepared','production/shared/thought-clouds/prepared/puff-large.png')
    frame,safe_image=adapt(Image.open(root/frame_source),None,frame_size)
    safe=np.asarray(safe_image)>127
    alpha=np.asarray(frame.getchannel('A'),np.float32)
    frame.putalpha(Image.fromarray(np.rint(alpha*(rim_opacity+(1-rim_opacity)*gaussian_filter(safe.astype(np.float32),2))).astype(np.uint8)))
    picture=Image.open(root/content['prepared']).convert('RGB')
    scale=content_width/picture.width
    if not 0<scale<=1:raise ValueError('Thought content must retain its native pixel budget')
    size=(content_width,round(picture.height*scale))
    if size[0]>frame_size[0] or size[1]>frame_size[1]:raise ValueError('Fit the empty frame around readable content')
    relative=np.asarray(picture.resize(size,Image.Resampling.LANCZOS),np.float32)/255
    significant=relative.min(2)<.985
    scores=cv2.matchTemplate(safe.astype(np.float32),significant.astype(np.float32),cv2.TM_CCORR)
    fits=np.argwhere(scores>=significant.sum()-.5)
    if not len(fits):raise ValueError('Frame cannot contain the readable picture; do not shrink the picture automatically')
    center=np.array([(frame_size[1]-size[1])/2,(frame_size[0]-size[0])/2])
    oy,ox=map(int,fits[np.square(fits-center).sum(1).argmin()])
    fit=safe[oy:oy+size[1],ox:ox+size[0]]
    if np.any(significant&~fit):raise ValueError('Significant picture pigment would be clipped')
    x,y=position
    if min(x,y)<0 or x+frame_size[0]>scene.width or y+frame_size[1]>scene.height:raise ValueError('Frame outside canvas')
    shell=Image.new('RGBA',scene.size);shell.alpha_composite(frame,position)
    underlay=Image.alpha_composite(scene.convert('RGBA'),shell);at=(x+ox,y+oy)
    base=np.asarray(underlay.crop((at[0],at[1],at[0]+size[0],at[1]+size[1])).convert('RGB'))
    colors=np.rint(base*relative).astype(np.uint8);coverage=np.any(colors!=base,2)&fit
    marks=Image.new('RGBA',scene.size);marks.alpha_composite(Image.fromarray(np.dstack([colors,coverage.astype(np.uint8)*255])),at)
    layers=[('painted-thought-frame',shell),('original-readable-thought-picture',marks)]
    for puff in puffs:
        source=Image.open(root/puff['prepared']).convert('RGBA');s=puff['width']/source.width
        if s>1:raise ValueError('Trail puff lacks native pixels')
        small=source.resize((puff['width'],round(source.height*s)),Image.Resampling.LANCZOS)
        small.putalpha(small.getchannel('A').point(lambda a:round(a*rim_opacity)))
        layer=Image.new('RGBA',scene.size);layer.alpha_composite(small,tuple(puff['position']));layers.append((puff['component'],layer))
    return layers,{'content_first':True,'frame_prepared':frame_source,'frame_size':list(frame_size),'position':list(position),
        'frame_only_aspect_adaptation':True,'rim_opacity':rim_opacity,'interior_opacity':1,
        'content':{**content,'position':list(at),'size':list(size),'uniform_scale':scale,'strength':1,
                   'strong_pigment_outside_safe_center':0,'clipped_subject_pixels':0}}

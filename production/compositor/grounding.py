"""Light attached watercolor contact shadows from measured support regions.

Supports are manually verified native-canvas xywh regions around actual soles,
chair/table-leg tips or other bearing surfaces. Never use a sprite bbox bottom
as the ground for every limb. The returned record includes actual contacts and
positive alpha overlap; it is not a visual approval.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def contact_shadow(subject, supports, colour=(105, 86, 70), core_opacity=34,
                   wash_opacity=17, core_blur=2.6, wash_blur=9.0):
    subject = subject.convert('RGBA')
    alpha = np.asarray(subject.getchannel('A'))
    combined = np.zeros(alpha.shape, dtype=np.float32)
    ly,lx=np.mgrid[:subject.height,:subject.width]
    grain=0.94+0.04*np.sin(lx*.13+ly*.17)+0.02*np.sin(lx*.43-ly*.19)
    records = []
    for support in supports:
        x,y,w,h = map(int, support['region_xywh'])
        if min(x,y) < 0 or min(w,h) <= 0 or x+w > subject.width or y+h > subject.height:
            raise ValueError('Support region outside canvas')
        region = alpha[y:y+h,x:x+w]
        yy,xx = np.where(region > 180)
        if len(xx) < 3:
            raise ValueError('Support region contains no opaque bearing surface')
        deepest = int(yy.max())
        # Take the observed low sole/tip band; do not trace a whole vertical leg.
        band = yy >= deepest - support.get('contact_band_px', 7)
        left,right = int(xx[band].min())+x,int(xx[band].max())+x
        bottom = deepest+y
        center = (left+right)/2
        radius = max((right-left)/2, 5)
        core = Image.new('L',subject.size,0)
        d = ImageDraw.Draw(core)
        # Centre starts one pixel inside the opaque edge: never a positive gap.
        d.ellipse((center-radius-2,bottom-4,center+radius+3,bottom+5),fill=core_opacity)
        core = core.filter(ImageFilter.GaussianBlur(core_blur))
        wash = Image.new('L',subject.size,0)
        d = ImageDraw.Draw(wash)
        d.ellipse((center-radius-14,bottom-8,center+radius+23,bottom+13),fill=wash_opacity)
        wash = wash.filter(ImageFilter.GaussianBlur(wash_blur))
        local = np.maximum(np.asarray(core),np.asarray(wash)).astype(np.float32)
        # A quiet deterministic paper-scale modulation avoids a flat oval.
        local *= grain
        contact_alpha=float(local[bottom,int(round(center))])
        if contact_alpha < 4:
            raise ValueError('Shadow does not meet its measured support')
        combined=np.maximum(combined,local)
        records.append({**support,'measured_contact_span':[left,bottom,right,bottom],
                        'core_center_y':bottom-1,'shadow_alpha_at_contact':round(contact_alpha,2),
                        'gap_px':0,'ownership':'this complete contact group only'})
    a=np.uint8(np.clip(np.rint(combined),0,255))
    rgba=np.zeros((*a.shape,4),dtype=np.uint8);rgba[:,:,:3]=colour;rgba[:,:,3]=a
    return Image.fromarray(rgba),dict(method='measured bearing surfaces; local contact cores plus restrained soft wash; max-union avoids stacked darkness',
       colour=list(colour),core_opacity=core_opacity,wash_opacity=wash_opacity,
       core_blur_px=core_blur,wash_blur_px=wash_blur,supports=records,
       z_order='after background, before the owning subject',
       visual_review_required=True)

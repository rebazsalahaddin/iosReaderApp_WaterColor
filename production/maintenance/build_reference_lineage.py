raise SystemExit("Retired workflow-8 writer: preserve current authored workflow-9 controls; do not rebuild from this historical script.")
"""Build prompt-only lineage plans; never render, alter, or submit artwork."""
from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'production/reference-lineage'
MFILE=ROOT/'production/full-book-rebuild-r6/book-production-manifest.json'
m=json.loads(MFILE.read_text()); qs=m['requests']; assets=m['assets']
def read(p):return json.loads((ROOT/p).read_text())
def write(p,v):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def cellnames(q):return ['ONE'] if len(q['cells'])==1 else ['L','R']
params={'model':'gpt_image_2_6_flare','quality':'medium','resolution':'2k','aspect_ratio':'4:3','batch_size':1,'output_format':'png','background':'transparent'}
identity_keys='child pilot prince grownup1 grownup2 king vain drinker business lamp geo fox switch seller astro_old astro_new flower ordinary'.split()
identities={k:{'candidate':assets[k]['canonical'],'candidate_role':'existing identity turnaround or plant stages; inspect and accept before use'} for k in identity_keys}
identities.update({
 'pilot_civilian':{'candidate':'story-and-continuity/chapter-01/pose-corrections/E01_pilot_reaching_hope_and_withdrawn_disappointment/reference-images/01_pilot__civilian-social__neutral-three-quarter__v001.png','candidate_role':'single civilian identity seed; first prepare/audit turnaround if none suitable'},
 'social_older':{'candidate':'story-and-continuity/chapter-01/pose-corrections/E03_social_adults_pleased_agreement/reference-images/01_CH01_S04_grownup3_talk_reply.png','candidate_role':'single adult identity seed; first prepare/audit turnaround'},
 'social_younger':{'candidate':'story-and-continuity/chapter-01/pose-corrections/E03_social_adults_pleased_agreement/reference-images/02_CH01_S05_grownup4_listen_reply.png','candidate_role':'single adult identity seed; first prepare/audit turnaround'},
 'anonymous_lamplighter':{'candidate':assets['lamp']['canonical'],'candidate_role':'period costume/style seed only; establish one distinct anonymous adult identity turnaround, then reuse it'},
 'snake':{'candidate':None,'candidate_role':'establish one slender gold-yellow snake identity with simple dark dot eyes, closed small mouth; audit consistent length/thickness from both views; no human posture'}
})
# Explicitly group states by genuine support/camera/wardrobe setup, never by emotion.
# Each line: family | identities | neutral setup | logical legacy cells.
spec='''
child_table | child | Six-year-old seated on RIGHT chair behind the SAME round table, body LEFT, neutral relaxed face, hands resting at the near edge, feet supported. One closed dusty-blue book far LEFT, one blank cream paper and one resting pencil. Complete table/chair/child group, medium-wide slightly raised view; no room. | CH01_S10:* CH01_S11:* CH01_S15:* CH01_S16:*
child_standing_paper_left | child | Child standing three-quarter LEFT with both hands supporting one blank cream sheet toward adults off-frame LEFT; neutral face and balanced supported feet. | CH01_S12:*
older_standing_right | grownup1 | Older bespectacled man standing three-quarter RIGHT, shoes RIGHT, neutral face, hands low; child eye line below-right. | CH01_S13:L CH01_S14:L CH01_E04:L
woman_standing_right | grownup2 | Grey-haired woman standing three-quarter RIGHT, shoes RIGHT, neutral face, hands low; child eye line below-right. | CH01_S13:R CH01_S14:R CH01_E04:R
pilot_social_chair_right | pilot_civilian | Adult civilian pilot seated on the SAME social wooden chair three-quarter RIGHT, supported shoes, neutral face, one blank landscape ivory sheet resting on lap beneath relaxed hands. Never turn the chair away. | CH01_E01:* CH01_E02:*
older_social_chair_left | social_older | Moustached older adult seated three-quarter LEFT on his approved social chair, hands on knees, supported feet and neutral face. | CH01_E03:L
younger_social_chair_left | social_younger | Adult in grey sweater seated three-quarter LEFT on his approved social chair, hands on knees, supported feet and neutral face. Adult proportions. | CH01_E03:R
pilot_flying_left | pilot | Complete cream-and-blue plane airborne nose LEFT, closed cowling, one cockpit/seat/headrest/windscreen, pilot in flight clothes and forehead goggles looking LEFT, neutral face, two-blade propeller. No floor shadow. | CH01_S17:*
pilot_flying_right | pilot | Complete same aircraft airborne nose RIGHT, closed cowling, one cockpit with pilot in flight clothes and forehead goggles looking RIGHT, neutral face, two-blade propeller. No floor shadow. | CH01_S18:*
pilot_crosslegged_right | pilot | Flight pilot cross-legged at LEFT, body RIGHT, neutral face, holding one blank cream sheet low and securely; pen at rest, all paper corners available. Complete supported body. | CH02_S01:* CH02_C01:*
prince_standing_left | prince | Prince standing three-quarter LEFT, feet supported, neutral face, relaxed shoulders and empty hands low. Preserve his approved small-child anatomy, gold hair, coral scarf and dot eyes. | CH02_S02:* CH02_S05:* CH03_S02:L CH03_S03:L CH03_C02:* CH07_S02:* CH07_S04:* CH10_S03:L CH10_C03:R CH11_S02:* CH17_S01:* CH17_C01:* CH19_S01:R CH19_C01:* CH20_S01:* CH25_S04:*
pilot_sitting_awake | pilot | Flight pilot sitting on sand-level footing, knees bent, both hands braced by hips, body/head RIGHT with neutral awake face. | CH02_S03:*
pilot_lying_side | pilot | Flight pilot lying fully supported on his side, bent knees, one arm under head, jacket on, calm neutral resting face. | CH02_S04:*
pilot_engine | pilot | Flight pilot leaning at engine of complete parked plane nose RIGHT, open supported cowling, right hand/spanner seated around bolt, empty cockpit, exactly two stopped blades; neutral face, grounded feet and wheels. | CH02_C02:*
pilot_standing_right | pilot | Flight pilot standing three-quarter RIGHT, hands low and empty, neutral face, grounded boots. | CH03_S01:*
prince_standing_paper_left | prince | Prince standing three-quarter LEFT, both hands securely holding one blank cream paper at lower chest; neutral face, supported boots. | CH03_S02:R CH03_C01:*
prince_walk_right | prince | Prince in one balanced grounded step RIGHT, arms relaxed and empty, neutral expression; complete body. | CH03_S03:R CH24_S02:R CH26_S07:L
pilot_room_desk | pilot_civilian | Civilian pilot in the approved seated-CLOSE room camera with complete same table/chair and blank drawing paper, pencil resting, hands at rest and neutral face. Match the approved adult-to-table fit and intentional lower-leg crop. | CH04_S01:* CH04_C01:*
pilot_room_standing | pilot_civilian | Civilian pilot full body in familiar standing-WIDE room camera, body three-quarter RIGHT near window position, neutral face and hands low. Background omitted. | CH04_S02:* CH26_S08:* CH27_S01:* CH27_C02:*
astronomer_traditional | astro_old | Astronomer standing in traditional costume with neutral face, grounded feet and hands low. | CH04_S03:L
astronomer_western | astro_new | The SAME astronomer in European costume, unchanged face/age/body, neutral expression and hands low. | CH04_S03:R
older_standing_left | grownup1 | Older bespectacled adult standing three-quarter LEFT, shoes LEFT, neutral expression and hands low. | CH04_S04:L CH27_C01:*
woman_standing_left | grownup2 | Grey-haired woman standing three-quarter LEFT, shoes LEFT, neutral expression and hands low. | CH04_S04:R
prince_kneeling_shoot | prince | Prince kneeling at RIGHT, body LEFT beside one tiny rooted green special-flower shoot on small soil patch, hands near knees, neutral face. No bud/bloom, no pulling. | CH05_S01:L
prince_crouched_seedling | prince | Prince crouching, both boots supported, one tiny uprooted baobab held low by stem with roots visible; neutral face. | CH05_S01:R
prince_lifting_chair | prince | Prince standing with both hands securely lifting the single small wooden chair just clear of ground, boots grounded, neutral face. | CH06_S01:L
prince_seated_chair_left | prince | Prince seated facing LEFT on that small wooden chair, hands at rest, boots supported, neutral face; complete chair. | CH06_S01:R
pilot_bent_spanner | pilot | Flight pilot bent forward toward engine off-frame LEFT, grounded feet, spanner held low without fictitious contact, neutral face. | CH07_S01:L
pilot_hammer_low | pilot | Flight pilot upright at LEFT facing RIGHT, one hammer held LOW by side, neutral face, empty other hand, grounded boots. | CH07_S01:R CH07_C01:*
pilot_engine_hand_close | pilot | Close coherent right hand of flight pilot with sleeve, one spanner seated around stuck hex bolt in exposed engine bay, fixed crop and exact contact. No floor shadow in this close crop. | CH07_R01:*
pilot_prince_embrace | pilot prince | Pilot kneeling, prince held gently against his chest with complete interlocking arms and supported weight, both faces neutral/resting. Preserve adult-child anatomy ratio. | CH07_S03:*
pilot_kneeling_tools | pilot | Flight pilot kneeling at LEFT facing RIGHT, left hand on own knee, right hand near one hammer already grounded beside one resting spanner; neutral face. | CH07_C02:*
rose_open | flower | Mature rooted living coral rose with two sage leaves and exactly four small thorns, same stem height and bloom structure, neutral calm face. | CH07_R02:* CH08_R03:*
ordinary_three | ordinary | Same three small cream three-lobed flowers at fixed spacing on a shallow common soil patch, neutral upright state. | CH08_R02:*
prince_kneeling_rose | prince flower | Prince kneeling facing the same open coral rose rooted at his LEFT on a small soil patch; hands near knees and neutral face. One small watering can rests beside him ready for the action. | CH08_S01:*
prince_volcano_active | prince | Prince safely leaning beside one small active cone, both hands with cleaning rod correctly gripped, boots supported, fire deep inside only; neutral face. | CH09_S01:L
prince_volcano_cold | prince | Same prince and cleaning tool beside the ONE cold third cone, dark opening without flame/smoke; supported body and neutral face. | CH09_S01:R
prince_glass | prince | Prince standing holding one empty plain glass bell cover by its rim with both hands at waist, neutral face, body LEFT; small compatible ochre patch through glass for refraction. | CH09_S02:*
king_spread_robe | king | King seated facing RIGHT on same throne with broad spread purple robe, hands at rest, neutral face; no book. | CH10_S01:* CH10_C01:*
king_robe_close | king | Same seated king/throne facing RIGHT, robe drawn closer leaving ground RIGHT clear, hands at rest, neutral face; no book. | CH10_S02_L:*
king_open_book | king | Same seated king/throne facing RIGHT and robe drawn closer; one thick open book supported on lap with one hand; other hand at rest, neutral face, blank nonverbal pages. | CH10_S02_R:* CH10_C02:*
prince_seated_ground_left | prince | Prince seated on ground facing LEFT with knees/boots supported, hands resting on knees, neutral calm face, no chair. | CH10_S03:R CH10_C03:L CH21_S02:* CH26_S09:* CH26_C01:*
vain_hat_worn | vain | Vain man standing three-quarter RIGHT, neutral face, only blue hat worn on head, hands low. | CH11_S01:L
vain_hat_held | vain | Same vain man standing RIGHT, LEFT anatomical hand holding the sole blue hat above hair, other hand low, neutral face. | CH11_S01:R CH11_C01:*
drinker_six_bottles | drinker | Weary man seated on same backless stool behind same table, body RIGHT, neutral resting face. Exactly six bottles at guide positions; bottle A in central slot, right hand resting near A. Lock bottle shapes/count/spacing. | CH12_S01_L:* CH12_S01_R:* CH12_S02:* CH12_C01:*
business_working | business | Businessman seated at same desk/chair, central blank working sheet exposed, pencil at rest front-right, two fixed paper stacks and cold cigarette, drawer closed with NO key; neutral face and hands at rest. | CH13_S01_L:* CH13_S01_R:* CH13_C01:*
business_locked | business | Same businessman/desk/chair with closed locked drawer and one key in lock; working sheet hidden, pencil resting front-right, two fixed paper stacks/cold cigarette, neutral face and hands at rest. | CH13_S02:* CH13_C02:*
lamplighter_pole | lamp | Lamplighter standing grounded, LEFT hand supporting pole nearly upright, RIGHT hand low, red-checked cloth pocketed out of sight, neutral face. | CH14_S01:* CH14_S02:*
geographer_with_prince | geo prince | Geographer seated in same chair at wide desk, prince seated on clear RIGHT-FRONT tabletop bay with feet dangling; both neutral faces and hands at rest. Great book open LEFT, magnifier front-left, pen and pencil resting separately. | CH15_S01:* CH15_S02:* CH15_S03:*
geographer_alone | geo | Same geographer seated at same wide desk/chair; right-front child seating bay EMPTY. Great book open LEFT, magnifier front-left, pen/pencil resting, neutral face. | CH15_S04:*
anonymous_lamp_stand | anonymous_lamplighter | Anonymous period worker standing grounded with unlit lighting pole nearly upright, neutral face. | CH16_S01:L
anonymous_lamp_sit | anonymous_lamplighter | SAME anonymous period worker seated on simple stool, unlit lighting pole resting beside him, hands at rest, neutral face. | CH16_S01:R
snake_ring | snake | One thin gold-yellow snake resting in loose low ring, head low, closed small mouth, simple dot eyes, fixed length/thickness; neutral non-menacing expression. | CH17_A01:L CH17_S03:L CH26_S02:L
snake_s_curve | snake | SAME thin gold-yellow snake in gentle extended S curve, head RIGHT, fixed length/thickness, closed small mouth and dot eyes; neutral non-menacing expression. | CH17_A01:R CH17_S03:R CH26_S02:R
prince_snake_ankle | prince snake | Prince standing supported, one continuous thin gold-yellow snake loosely encircling ONE ankle like bracelet, child looking down with neutral face, both complete anatomy. | CH17_S02:*
three_petal_flower | ordinary | One small cream flower with exactly THREE separate petals, slender stem and leaves, upright and healthy on tiny dry soil patch. | CH18_R01:*
prince_uphill_step | prince | Prince in balanced uphill step RIGHT, one boot higher, complete small rocky patch supporting BOTH soles, neutral face. | CH19_S01:L
prince_lying_forearms | prince | Prince lying fully supported on side/front with face near folded forearms, complete horizontal body and boots, neutral resting face, no pillow. | CH20_S02:*
prince_walk_left | prince | Prince in gentle grounded step LEFT, body/head LEFT, empty hands, neutral face. | CH20_C01:* CH27_C03:*
fox_standing_right | fox | Same fox standing on four paws, head RIGHT, neutral gentle face and relaxed tail, complete body. | CH21_S01:L CH21_S03:L
fox_seated_right | fox | Same fox seated facing RIGHT, tail beside hind paws, mouth closed and neutral gentle face. | CH21_S01:R CH21_S03:R
switchman_right | switch | Switchman standing three-quarter RIGHT, hands at rest and empty, neutral face, grounded feet. | CH22_S01:*
pill_seller_counter | seller | Pill seller behind same plain wooden counter with one unlabelled CLOSED container, neutral face and hands at rest; no loose pills or dose in hand. | CH23_S01_L:* CH23_S01_R:*
pilot_canteen | pilot | Flight pilot standing grounded, body RIGHT, one small canteen held low, neutral face, other hand low. | CH24_S01:*
pilot_walk_right | pilot | Flight pilot in one grounded step RIGHT, hands free and neutral face, complete body. | CH24_S02:L CH24_S05:*
pilot_carry_prince | pilot prince | Flight pilot in slow grounded walking stance RIGHT, securely carrying resting prince in both arms, one under knees and one behind back; head supported near chest, both neutral/resting faces, child eyes closed. | CH24_S03:* CH24_S04:*
prince_well_rope | prince | Complete well and prince pulling its one taut rope over wheel to single bucket below rim; supported boots, correct hand contact, neutral face, small matching sand patch. | CH25_S01:*
pilot_well_rope | pilot | Complete same well and flight pilot pulling continuous rope over wheel, single water bucket at rim, grounded boots and correct tension/grip; neutral face. | CH25_S02:*
pilot_prince_bucket | pilot prince | Flight pilot kneeling supporting one water bucket near standing prince's lips, coherent hands/rim/body contact and supported weight, neutral restful faces. | CH25_S03:*
pilot_walk_left | pilot | Flight pilot taking grounded step LEFT, body/feet LEFT, head neutral, hands empty. | CH25_C01:*
prince_wall | prince | Prince seated on complete visible low broken wall span, legs dangling, neutral face looking down-right, wall footing grounded; NO snake or snake shadow. | CH26_S01:*
pilot_prince_wall | pilot prince | Flight pilot crouched beside complete low broken wall span, supporting conscious prince against chest in both arms, child supported and coral scarf slightly loosened, neutral calm faces. | CH26_S03:*
pilot_prince_cup | pilot prince | Flight pilot kneeling with conscious prince supported on bent knee, one hand steadying upper back and one holding small plain water cup near child lips; neutral/resting faces. | CH26_S04:*
pilot_prince_seated | pilot prince | Flight pilot and prince seated on sand close beside each other, separate correct bodies, adult facing child, child neutral gaze upward, hands at rest. | CH26_S05:*
pilot_prince_handwalk | pilot prince | Flight pilot and prince walking RIGHT hand in hand, correctly joined fingers, adult lower hand meets child's raised hand, same depth, grounded strides, neutral faces. | CH26_S06:* CH26_C02:*
prince_fall | prince | Prince in initial gentle sideways tilt/fall, boots close to ground and natural balance transition, arms relaxed, neutral face; no floating, injury or impact. Support shadow belongs only under near-contact boots. | CH26_S07:R
prince_snake_boot_close | prince snake | Close view of prince boots and lower trousers on sand-level footing, one thin yellow snake curve touching ONE ankle; correct anatomy and contact, no blood/fangs/wound. | CH26_R01:*
pilot_prince_seated_support | pilot prince | Flight pilot seated low at LEFT supporting conscious prince beside chest in both arms, child looks up-left, adult down-right, neutral faces; no cup, snake or wall. | CH26_C03:*
'''
families={};routing={}
for line in spec.strip().splitlines():
 fid,ids,setup,tokens=[v.strip() for v in line.split('|')];families[fid]={'identities':ids.split(),'setup':setup,'tokens':[]}
 for token in tokens.split():
  rid,cell=token.split(':');assert rid in qs,rid
  for c in cellnames(qs[rid]) if cell=='*' else [cell]:
   k=f'{rid}:{c}';assert k not in routing,k;routing[k]=fid;families[fid]['tokens'].append(k)
# Every human/animal pose/contact must have an explicit neutral family, not guessed by keywords.
object_contacts={'CH09_R02','CH12_R01'}
for rid,q in qs.items():
 if q['kind'] in ['pose','contact','appearance'] and rid not in object_contacts:
  for c in cellnames(q):assert f'{rid}:{c}' in routing,(rid,c)

def lighting(q):
 s=q['light'].lower()
 if 'window' in s:return 'night_window_left'
 if any(w in s for w in ['moon','night','starlight']):return 'moonlight_upper_left'
 if 'sunrise' in s:return 'sunrise_left'
 if any(w in s for w in ['evening','dusk','twilight','sunset','late-day']):return 'evening_upper_left'
 if 'indoor' in s:return 'warm_indoor'
 return 'soft_day_upper_left'
# Resolve minimal essential foundation prop authorities. These guide crops are geometry only.
prop_for={
 'child_table':'production/chapter-01/props/raw/CH01_S10_child_reading_at_round_table.png',
 'pilot_room_desk':'roomclose','pilot_flying_left':'plane','pilot_flying_right':'plane','pilot_engine':'openplane','pilot_engine_hand_close':'openplane',
 'prince_kneeling_shoot':'flower','prince_lifting_chair':'LP_ch06_chair_scale_guide','prince_seated_chair_left':'LP_ch06_chair_scale_guide',
 'prince_volcano_active':'LP_ch09_volcano_scale_guide','prince_volcano_cold':'LP_ch09_volcano_scale_guide','prince_glass':'LP_ch09_glass_handling_guide',
 'king_spread_robe':'LP_ch10_coat_book_guide','king_robe_close':'LP_ch10_coat_book_guide','king_open_book':'LP_ch10_coat_book_guide',
 'drinker_six_bottles':'LP_ch12_bottle_layout_guide','business_working':'LP_ch13_desk_state_guide','business_locked':'LP_ch13_desk_state_guide',
 'geographer_with_prince':'LP_ch15_table_state_guide','geographer_alone':'LP_ch15_table_state_guide','prince_well_rope':'well','pilot_well_rope':'well',
}
for fid in ['pilot_social_chair_right','older_social_chair_left','younger_social_chair_left']:
 key=families[fid]['identities'][0];prop_for[fid]=identities[key]['candidate']
locks='Keep identical identity, age, dot-shaped eyes (no anime eyes or enlarged irises), face/nose/ears, hair silhouette and colour, skin, costume and colours, head/body size and proportions, furniture dimensions, camera, registration and watercolor treatment. No redesign, mirroring, rescaling, extra limbs or invented text.'
shadow='Include a very light soft attached watercolor contact shadow at actual supports, with graded alpha fading to full transparency. No detached blob, hard oval, opaque floor, checkerboard or colour-key background. Preserve opaque subject interiors.'
shadowlock='Keep the parent support footprint and its shadow EXACTLY: shape, position, hue, softness, alpha and intensity. No added shadow, new floor or matte.'
nodes={};routes={}
def node(nid,stage,content,parents,inputs,**extra):
 d={'id':nid,'stage':stage,'status':'planned_not_generated_or_accepted','parameters':dict(params),'parents':parents,'input_contract':inputs,'content':content,'max_attempts_total':2,'reuse_first':True,**extra}
 d['prompt_file']=f'production/reference-lineage/nodes/{nid}/PROMPT.txt';nodes[nid]=d;return d
for k,v in identities.items():
 d=node('I_'+k,'identity_turnaround',f'One clean identity turnaround of the SAME {k.replace("_"," ")}: front, three-quarter, side and back; consistent scale, neutral face, complete body, well separated views. '+locks,[],{'max_images':1,'approved_seed_only':True},**v)
 if v['candidate']:d['candidate_sha256']=sha(v['candidate'])
 if k=='snake':d['content']='One identity sheet of a single slender gold-yellow desert snake in a loose low ring and a gentle extended S curve. Exactly same length/thickness, small dark dot eyes, closed small mouth and non-menacing neutral expression; restrained storybook watercolor. No legs, fangs or floor.'
 d['prompt']=d['content']+' Native transparent PNG, 4:3, 2K. No scenery or labels.'
# Reusable masters are split only when illumination genuinely changes.
for token,fid in routing.items():
 rid,c=token.split(':');q=qs[rid];light=lighting(q);base=f'N_{fid}__{light}'
 if base not in nodes:
  f=families[fid];p=['I_'+i for i in f['identities']];additional=[]
  if fid in prop_for:
   a=prop_for[fid];path=assets[a]['canonical'] if a in assets else a
   additional=[{'candidate':path,'candidate_sha256':sha(path),'role':'essential furniture/prop geometry only; select ONE relevant clean object view/crop offline, exclude all other people, labels and competing states; record audited crop hash before use'}]
  n=node(base,'neutral_posture',f['setup'],p,{'max_images':len(p)+len(additional),'required_identity_parents':p,'foundation_exception_only':True,'additional_geometry_candidates':additional,'no_style_bundle':True},family=fid,light=q['light'],affected_pages=[],legacy_tokens=[],shadow_mode='none_airborne_or_close_crop' if fid.startswith('pilot_flying') or fid=='pilot_engine_hand_close' else 'generated_attached_contact',geometry_authorities=[])
  n['prompt']='Create ONE neutral master, not an expressive scene. '+f['setup']+' '+locks+' '+q['light']+' '+(shadow if n['shadow_mode']=='generated_attached_contact' else 'Transparent surroundings; no physical floor or floor shadow.')+' 4:3 2K native transparent PNG; no scenery, labels or diagram marks.'
 n=nodes[base];n['legacy_tokens'].append(token);n['affected_pages']=sorted(set(n['affected_pages']+q['uses']))
 for a in q['attachments']:
  if a.get('status')=='supplied' and any(w in a['role'].lower() for w in ['scale','geometry','camera','size authority']):
   item={'path':a['path'],'sha256':a['sha256'],'role':a['role']}
   if item not in n['geometry_authorities']:n['geometry_authorities'].append(item)
# Legacy object sheets are logical cells too; create one asset, no new two-column sheets.
for rid,q in qs.items():
 for c,raw in zip(cellnames(q),q['cells']):
  token=f'{rid}:{c}';change=re.sub(r'^(LEFT\s*/\s*TOP|RIGHT\s*/\s*BOTTOM|LEFT|RIGHT|ONE):\s*','',raw)
  nid='V_'+rid+'_'+c if token in routing else 'A_'+rid+'_'+c
  if token in routing:
   base=f'N_{routing[token]}__{lighting(q)}'
   n=node(nid,'expression_variant',change,[base],{'exact_images':1,'sole_appearance_authority':base,'first_attempt':'exact accepted neutral master file/hash','retry':'one reviewed board with dominant intact same neutral master and ALL issue diagnostics','forbidden_parents':['expression_variant','previous_expression','legacy_reference_bundle']},legacy_request=rid,legacy_cell=c,affected_pages=q['uses'],allowed_changes=change,shadow_mode='preserve_parent',audit_only_details=q['details'])
   n['prompt']='Edit the ONE supplied approved neutral posture; do not reconstruct from a turnaround. Required change: '+change+' Only change the named expression and necessary head/hand/arm or explicitly named prop action; preserve the support/camera setup. '+locks+' '+shadowlock+' Keep the same subject registration. One complete state, 4:3 2K native transparent PNG. Blank paper stays blank for later canonical marks; no labels or thoughts in this character asset.'
  else:
   # Choose one relevant authority; all others remain offline audit evidence.
   candidates=[a for a in q['attachments'] if a.get('status')=='supplied' and a.get('source_key') not in ['style','success_style'] and 'guide' not in a['name'].lower() and 'scale' not in a['name'].lower()]
   if not candidates:candidates=[a for a in q['attachments'] if a.get('status')=='supplied' and a.get('source_key')=='success_style']
   authority=[{k:a[k] for k in ['path','sha256','role']} for a in candidates[:1]]
   bg=q['kind']=='background'
   n=node(nid,'background_plate' if bg else 'object_or_editorial',change,[],{'max_images':1,'selected_candidates':authority,'require_role_audit_before_upload':True},legacy_request=rid,legacy_cell=c,affected_pages=q['uses'],audit_only_details=q['details'],shadow_mode='background_painted' if bg else 'physical_contact_if_applicable_no_editorial_floor')
   if bg:n['parameters']['background']='opaque'
   n['prompt']='Create ONE '+('empty background plate' if bg else 'complete isolated object/editorial asset')+'. '+change+' '+q['light']+' Match the approved restrained storybook watercolor: broad washes, delicate warm contours, quiet pale colours, no photorealism or fine decorative texture. '+('Keep scene landmarks and painted paper border consistent; no new cast.' if bg else 'Native transparent surroundings; opaque subject interiors. Physical grounded objects only: very light soft attached contact shadow with graded alpha. Editorial pictures, diagrams and imagined content: no physical floor shadow. Preserve any explicitly requested bounded paper or tiny support patch.')+' One logical state only; 4:3, 2K PNG. No instruction labels or generated text.'
  n['offline_audit_request']=q['folder']+'/audit-contract.json';n['prompt_sha256']=hashlib.sha256(n['prompt'].encode()).hexdigest();routes[token]=nid
# Distinct imagining performance: do not reuse the excited reading pose as an identical page beat.
base='N_child_table__soft_day_upper_left';extra='V_CH01_CHILD_IMAGINING'
n=node(extra,'expression_variant','Same seated child gently raises gaze in wonder, thoughtful brow and small softly parted mouth, hands resting beside the open book; he imagines its snake story. Keep thoughts out of the cutout.',[base],{'exact_images':1,'sole_appearance_authority':base,'first_attempt':'exact accepted neutral master file/hash','retry':'one reviewed correction board','forbidden_parents':['expression_variant','previous_expression','legacy_reference_bundle']},affected_pages=['c01-s01-p03'],allowed_changes='head/gaze/brow/mouth and resting hands; open book for this passage',shadow_mode='preserve_parent',new_state_justification='Preplanned distinct imagining beat; never used to renew an exhausted reading-state attempt.')
n['prompt']='Edit the ONE supplied approved neutral child/table/chair master. '+n['content']+' '+locks+' '+shadowlock+' Keep table/chair/body size and placement fixed. One complete state; native transparent PNG, 4:3, 2K.'
page_routes={}
for cn,ch in m['chapters'].items():
 for pid,page in ch['pages'].items():
  r={a:routes[a] for a in page['assets'] if a in routes}
  if pid=='c01-s01-p03' and 'CH01_S10:ONE' in r:r['CH01_S10:ONE']=extra
  page_routes[pid]=r;page['reference_lineage']=r
  p=ROOT/page['layout'];layout=json.loads(p.read_text());layout['reference_lineage']={'workflow_version':8,'planned_only':True,'asset_nodes':r,'preserve_current_as_built':True,'guide':'production/Reference_Lineage_Workflow.md'};write(page['layout'],layout)
  ap=ROOT/page['assembly_instructions'];s=ap.read_text();marker='\n## Reference lineage — workflow 8\n'
  s=s.split(marker)[0]+marker+'Future generation only: use the node mapping in layout.json. Reuse suitable accepted art. Identity turnaround → approved neutral posture/contact group → one-reference expression edits. Keep generated master shadows attached and unchanged; no added programmatic shadow by default. Inspect source alpha and measured registration before composition. Existing current images stay unchanged during prompt preparation.\n';ap.write_text(s)
# Stable topological order with no expressive parents.
order=[];seen=set()
def visit(i):
 if i in seen:return
 for p in nodes[i]['parents']:visit(p)
 seen.add(i);order.append(i)
for i in nodes:visit(i)
for i,n in nodes.items():
 n['prompt_sha256']=hashlib.sha256(n['prompt'].encode()).hexdigest()
 path=ROOT/n['prompt_file'];path.parent.mkdir(parents=True,exist_ok=True);path.write_text(n['prompt'])
 write(str(path.parent.relative_to(ROOT)/'node.json'),n)
cat={'workflow_version':8,'scope':'future execution only; no artwork or history changed','model':params,'nodes':nodes,'legacy_asset_routes':routes,'page_asset_routes':page_routes,'dependency_order':order,'attempt_bridge':'Each counted historical request-sheet attempt counts against every mapped legacy cell. New IDs/model/parent do not reset attempts. New neutral nodes may not substitute an exhausted expression.','guide':'production/Reference_Lineage_Workflow.md'}
write('production/reference-lineage/catalog.json',cat)
if not (BASE/'ledger.json').exists():write('production/reference-lineage/ledger.json',{'workflow_version':8,'jobs':[],'sources':{},'page_generation_rounds':{},'page_correction_plans':{},'note':'Future append-only execution ledger. Read historical production/agent-ledger.json too. No jobs authorized by prompt preparation.'})
m['workflow_version']=8;m['reference_lineage_catalog']='production/reference-lineage/catalog.json';m['generation_dependency_waves_usage']='Legacy audit dependencies only; execute chapter lineage_execution_order after reuse audit.'
for rid,q in qs.items():
 r={c:routes[f'{rid}:{c}'] for c in cellnames(q)};q['lineage_nodes']=r;q['generation_route']='lineage_nodes_only';q['attachment_usage']='offline_audit_only_not_submission_manifest';q['key']=None
 lines=[f'{rid} — WORKFLOW 8 AGENT ROUTING CARD (not an image-model payload)', 'MODEL: GPT Image 2.6 Flare / gpt_image_2_6_flare; quality medium; 2K; 4:3; PNG; batch_size 1. Native transparent isolated references; opaque background plates.', 'REFERENCE: Read production/Reference_Lineage_Workflow.md and production/reference-lineage/catalog.json. Inspect/reuse the identity turnaround, approve the neutral posture/contact master, then edit each expression from exactly ONE approved neutral image. Never submit this routing card or the old numbered bundle to the model.', 'DIRECTION AND STATE:']
 for c in cellnames(q):lines+=['- '+c+': '+nodes[r[c]]['content'],'  Actual short payload: '+nodes[r[c]]['prompt_file']]
 lines+=['L/R identify legacy logical states, not output columns. Generate a single state only when needed. All variants return to the same neutral master, never to a sibling expression. Preserve face, dot eyes, hair, clothes, age, anatomy, dimensions, camera, furniture and registration outside named edits. Preserve the generated attached shadow including alpha; no extra shadow by default.', 'AUDIT: Compare all offline identity/scale/story evidence; audit native alpha, emotion, exact contact and parent-shadow preservation. Read story-context.json and audit-contract.json. Old attachments stay for audit only. Accepted current artwork remains reusable and untouched.', 'MEASURED CONTINUITY AND FRAMING LOCK: Use measured anatomy and support anchors from page layout.json; same camera keeps size/location. Final 2400×1792 geometry remains unchanged; check actual 2K source pixels.', 'COMPOSITION CONTINUITY AND PERFORMANCE LOCK: One physical contact group, correct relative ratios, attached single-owner shadow, clear expression/gaze/recipient and meaningful unique page beat.', 'TEXT-TO-ILLUSTRATION ALIGNMENT: Exact page story-context remains authoritative; no early reveal or invented contact. Thought contents are separate assets.', 'THOUGHT AESTHETICS AND SCENE HIERARCHY: Selected thoughts only, readable quiet watercolor contents, adapted frame and three owner-linked puffs; do not crowd the page.', 'BUDGET: Two attempts maximum per canonical state including historical sheet attempts. Reuse before spending. For a material retry use one locally prepared reviewed board with intact neutral authority and every issue; keep full original short prompt plus precise fixes. No third attempt. Stop after one chapter for manual approval.']
 q['prompt']='\n'.join(lines)+'\n';folder=ROOT/q['folder'];(folder/'PROMPT.txt').write_text(q['prompt']);(folder/'PROMPT.md').write_text('# '+rid+'\n\n'+q['prompt']);write(q['folder']+'/request.json',q)
for cn,ch in m['chapters'].items():
 lines=[f'# Chapter {cn} — reference generation and posture lineage','', 'Future execution only. Read production/Reference_Lineage_Workflow.md. GPT Image 2.6 Flare, quality medium, 2K, 4:3, one PNG. First accept turnaround, then neutral posture with soft attached shadow, then each expression from that one neutral image. No previous-expression chaining or reference bundles. Existing deliveries are unchanged.','', '| Page | Source states and lineage nodes |','| --- | --- |']
 for pid,page in ch['pages'].items():lines.append('| '+pid+' | '+'; '.join(a+' → '+n for a,n in page_routes[pid].items())+' |')
 for rid in ch['requests']:
  if qs[rid]['required']:lines+=['','## '+rid,'',qs[rid]['prompt']]
 (ROOT/f'story-and-continuity/chapter-{int(cn):02}/Chapter_{cn}_Manual_Reference_and_Pose_Prompts.md').write_text('\n'.join(lines)+'\n')
write(str(MFILE.relative_to(ROOT)),m)
write('production/reference-lineage/migration-summary.json',{'workflow_version':8,'chapters':len(m['chapters']),'pages':len(page_routes),'legacy_requests':len(qs),'logical_states':len(routes),'nodes_by_stage':{s:sum(n['stage']==s for n in nodes.values()) for s in sorted({n['stage'] for n in nodes.values()})},'jobs_submitted':0,'credits_spent':0,'artwork_modified':False})
print(json.dumps(read('production/reference-lineage/migration-summary.json'),indent=2))

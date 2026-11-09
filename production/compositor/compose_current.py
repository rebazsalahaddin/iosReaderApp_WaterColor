"""Reconstruct a retained chapter from its current layers; never use old deliveries."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[2]
def path(value):
 p=(ROOT/value).resolve()
 if not p.is_relative_to(ROOT):raise ValueError('Path leaves the project root: '+value)
 return p

def reconstruct(layout):
 canvas=Image.new('RGBA',tuple(layout['canvas']),(0,0,0,0))
 for layer in layout['layers']:
  source=path(layer['source'])
  if hashlib.sha256(source.read_bytes()).hexdigest()!=layer['sha256']:raise ValueError('Layer checksum mismatch: '+layer['source'])
  im=Image.open(source).convert('RGBA')
  if layer.get('transform')!='identity; alpha composite in listed order':raise ValueError('Unrecognised layer transform')
  canvas.alpha_composite(im,tuple(layer.get('position',[0,0])))
 return canvas.convert('RGB')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--chapter',type=int,required=True);parser.add_argument('--verify',action='store_true');parser.add_argument('--output');args=parser.parse_args()
 if not args.verify and not args.output:parser.error('Use --verify or --output with a project-relative review folder')
 manifest=json.loads(path(f'production/chapter-{args.chapter:02}/chapter-{args.chapter:02}-page-manifest.json').read_text())
 dest=path(args.output) if args.output else None
 if dest and ('delivery' in dest.parts or dest==ROOT):raise ValueError('Output must be a separate working folder, never the selected delivery')
 if dest:dest.mkdir(parents=True,exist_ok=True)
 checked=[]
 for row in manifest['pages']:
  layout=json.loads(path(row['component_layout']).read_text());rendered=reconstruct(layout)
  final=path(row['delivery_file'])
  if hashlib.sha256(final.read_bytes()).hexdigest()!=row['delivery_sha256']:raise ValueError('Final PNG hash changed: '+row['page'])
  if args.verify and ImageChops.difference(rendered,Image.open(final).convert('RGB')).getbbox() is not None:raise ValueError('Reconstruction differs: '+row['page'])
  if dest:
   out=dest/(row['page']+'.png')
   if out.exists():raise ValueError('Refusing to overwrite a review file: '+str(out))
   rendered.save(out)
  checked.append(row['page'])
 print(json.dumps({'status':'pass','pages':len(checked),'exact_pixel_comparison':args.verify,'uses_only_current_project_files':True}))
if __name__=='__main__':main()

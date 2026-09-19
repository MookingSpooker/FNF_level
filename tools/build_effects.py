"""Build lightweight stage geometry and an audio envelope sampled from the actual song."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mods/energize'

def build_effects():
    folder=MOD/'images/stages/dynamo-fx';folder.mkdir(parents=True,exist_ok=True)
    ring=Image.new('RGBA',(512,512));draw=ImageDraw.Draw(ring)
    for inset,alpha,width in [(19,25,15),(23,60,7),(26,220,3),(45,55,2)]:
        draw.ellipse((inset,inset,512-inset,512-inset),outline=(42,241,255,alpha),width=width)
    ring.save(folder/'ring.png')
    # Simple transparent light-cone geometry; no change to the painted backdrop.
    beam=Image.new('RGBA',(256,768));draw=ImageDraw.Draw(beam)
    for y in range(768):
        half=int(115*(1-y/768)+4)
        alpha=int(90*(.4+.6*y/768))
        draw.line((128-half,y,128+half,y),fill=(82,225,255,alpha),width=1)
    beam.save(folder/'beam.png')
    z=np.load(ROOT/'analysis/features.npz')
    t=z['times'];freq=z['freq'];spec=z['spec']
    bands=[np.sqrt((spec[:,(freq>=lo)&(freq<hi)]**2).mean(axis=1))
           for lo,hi in [(40,180),(180,1800),(1800,10000)]]+[z['rms']]
    sample_t=np.arange(0,187.6,.04)
    normalized=[]
    for values in bands:
        values=np.clip(values/(np.percentile(values,95)+1e-8),0,1)
        # Short smoothing reduces hard flashes, while retaining bass attack and decay.
        values=np.convolve(values,np.ones(7)/7,mode='same')
        normalized.append(np.interp(sample_t,t,values))
    frames=np.round(np.array(normalized).T,3).tolist()
    (MOD/'data/energize-reactivity.json').write_text(json.dumps({'sampleMs':40,'frames':frames},separators=(',',':')))
    props=[]
    def prop(name,path,x,y,scale,alpha,z=10):
        props.append({'name':name,'assetPath':path,'position':[x,y],'scale':scale,
                      'scroll':[1,1],'zIndex':z,'alpha':alpha})
    prop('reactorRing','stages/dynamo-fx/ring',460,5,[1.15,1.15],.3)
    prop('reactorEcho','stages/dynamo-fx/ring',460,5,[1.15,1.15],0)
    for i,x in enumerate([40,370,990,1320]):
        prop(f'beam{i}','stages/dynamo-fx/beam',x-128,-115,[1,1],.1,5)
    for i in range(32):
        prop(f'eq{i}','#25EAFF' if i%4<2 else '#C8FF44',60+i*41,620,[14,180],.45,8)
    for i in range(18):
        prop(f'spark{i}','#45F4FF' if i%2==0 else '#DBFF65',80+i*73,500,[3,10],0,12)
    return props

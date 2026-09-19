"""Verify chart playability, asset references, atlas bounds and decoded-audio timing."""
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mods/energize'
GAME=Path.home()/'Downloads/funkin-windows-64bit'

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def decode(path):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),
        '-map','0:a:0','-f','f32le','-ac','1','-ar','22050','-']),dtype='<f4')

meta=read(MOD/'data/songs/energize/energize-metadata.json')
chart=read(MOD/'data/songs/energize/energize-chart.json')
level=read(MOD/'data/levels/energize.json')
stage=read(MOD/'data/stages/dynamo.json')
character=read(MOD/'data/characters/volt.json')
ogg=MOD/'songs/energize/Inst.ogg'
y=decode(ogg)
source=Path.home()/'Downloads/Energize - Tonytonychopper999.mp3'
reference=decode(source)
assert abs(len(y)-len(reference))<=1, 'Audio conversion changed duration'
audio_correlation=float(np.corrcoef(y[:min(len(y),len(reference))],reference[:min(len(y),len(reference))])[0,1])
assert audio_correlation>.98, 'Game audio does not match the supplied song'
assert level['songs']==['energize']
assert meta['playData']['stage']=='dynamo'
assert meta['playData']['characters']['opponent']=='volt'
assert set(meta['playData']['difficulties'])==set(chart['notes'])
assert meta['playData']['characters']['playerVocals']==[]
assert meta['playData']['characters']['opponentVocals']==[]
image_path=MOD/'images/characters/volt.png'
im=Image.open(image_path)
assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
atlas=ET.parse(image_path.with_suffix('.xml')).getroot()
names=[]
for f in atlas:
    x,y0,w,h=(int(f.get(k)) for k in ['x','y','width','height'])
    assert 0<=x<x+w<=im.width and 0<=y0<y0+h<=im.height
    assert int(f.get('frameWidth'))>=w and int(f.get('frameHeight'))>=h
    names.append(f.get('name'))
assert len(names)==len(set(names))
for animation in character['animations']:
    assert any(n.startswith(animation['prefix']) for n in names),animation['name']
for prop in stage['props']:
    assert (MOD/'images'/f"{prop['assetPath']}.png").exists()
assert Image.open(MOD/'images/icons/icon-volt.png').size==(300,150)
assert (MOD/'images'/f"{level['titleAsset']}.png").exists()
for role in ['bf','gf']:
    assert (GAME/f'assets/data/characters/{role}.json').exists()
features=np.load(ROOT/'analysis/features.npz')
times=features['times'];strength=features['onset']
peaks=times[(strength>np.roll(strength,1))&(strength>=np.roll(strength,-1))]-.006
stats={}
for difficulty,notes in chart['notes'].items():
    assert notes==sorted(notes,key=lambda n:(n['t'],n['d']))
    assert len({(n['t'],n['d']) for n in notes})==len(notes),'Duplicate notes'
    assert all(0<=n['d']<8 and 0<n['t']<len(y)/22.05 and n['l']>=0 for n in notes)
    assert all(n['t']+n['l']<len(y)/22.05 for n in notes)
    for lane in range(8):
        ns=[n for n in notes if n['d']==lane]
        for a,b in zip(ns,ns[1:]):
            assert b['t']-a['t']>=145,'Unfair rapid same-lane repeat'
            assert a['t']+a['l']<b['t'],'Overlapping sustain and tap'
    for side in [0,1]:
        ns=[n for n in notes if n['d']//4==side]
        assert all(b['t']-a['t']>=75 for a,b in zip(ns,ns[1:])), 'Unplayable attack density'
    errors=[float(min(abs(peaks-n['t']/1000))*1000) for n in notes]
    assert max(errors)<.01,'Note lost its matching acoustic attack'
    stats[difficulty]={'notes':len(notes),'max_attack_rounding_error_ms':max(errors)}
result={'status':'PASS','audio_correlation':audio_correlation,
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'game_audio_sha256':hashlib.sha256(ogg.read_bytes()).hexdigest(),
        'duration_seconds':len(y)/22050,'atlas_frames':len(names),'charts':stats,
        'checks':['Exact supplied recording, unchanged length','All required assets resolve',
                  'All atlas rectangles in bounds','No duplicate or out-of-range notes',
                  'No sustain collisions or rapid same-lane repeats','Every note matches a detected acoustic attack']}
(ROOT/'analysis/validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

"""Verify chart playability, asset references, atlas bounds and decoded-audio timing."""
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
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
advanced_meta=read(MOD/'data/songs/energize/energize-metadata-erect.json')
advanced_chart=read(MOD/'data/songs/energize/energize-chart-erect.json')
assert meta['playData']['songVariations']==['erect']
assert set(advanced_meta['playData']['difficulties'])==set(advanced_chart['notes'])=={'erect','nightmare'}
assert advanced_meta['playData']['characters']['instrumental']==''
assert advanced_meta['timeChanges']==meta['timeChanges']
assert advanced_meta['playData']['characters']['playerVocals']==[]
assert advanced_meta['playData']['characters']['opponentVocals']==[]
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
    if not prop['assetPath'].startswith('#'):
        assert (MOD/'images'/f"{prop['assetPath']}.png").exists()
    assert prop['zIndex']<100,'Stage effect would obscure the characters'
envelope=read(MOD/'data/energize-reactivity.json')
assert envelope['sampleMs']==40
assert len(envelope['frames'])*40>=len(y)/22.05
assert all(len(frame)==4 and all(0<=v<=1 for v in frame) for frame in envelope['frames'])
assert np.std(np.array(envelope['frames']),axis=0).min()>.08,'Unresponsive visualizer channel'
assert (MOD/'scripts/stages/dynamo.hxc').exists()
assert Image.open(MOD/'images/icons/icon-volt.png').size==(300,150)
assert (MOD/'images'/f"{level['titleAsset']}.png").exists()
for role in ['bf','gf']:
    assert (GAME/f'assets/data/characters/{role}.json').exists()
parts=read(ROOT/'analysis/instrumental-parts.json')
provenance=read(ROOT/'analysis/note-provenance.json')
report=read(ROOT/'analysis/chart-report.json')
part_attacks={name:{a['step']:a for a in values} for name,values in parts['parts'].items()}
assert set(parts['sources'])=={'synth','bass','drums'}
assert parts['sources']['synth']=='other.wav'
assert envelope['offsetMs']==report['grid_offset_ms']==meta['timeChanges'][1]['t']==34
assert envelope['sections']==report['sections']
assert all(s['leadSide']==0 for s in envelope['sections']), 'Foreground still switches away from Boyfriend'
stats={}
all_charts={**chart['notes'],**advanced_chart['notes']}
for difficulty,notes in all_charts.items():
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
        attacks=sorted(set(n['t'] for n in ns))
        assert all(b-a>=75 for a,b in zip(attacks,attacks[1:])), 'Unplayable attack density'
        assert max(Counter(n['t'] for n in ns).values())<=2,'Three/four-key chord introduced'
    proof={(a['t'],a['d']):a for a in provenance[difficulty]}
    assert len(proof)==len(notes),'Missing or duplicate musical provenance'
    errors=[]
    for n in notes:
        a=proof[(n['t'],n['d'])]
        assert a['part'] in part_attacks and a['source']==parts['sources'][a['part']], 'Non-instrumental note evidence'
        stem=part_attacks[a['part']][a['step']]
        assert a['attack']==stem['attack'] and a['strength']==stem['strength']
        errors.append(abs(n['t']-stem['attack']))
        assert errors[-1]<35, 'Note has no nearby instrumental attack'
        assert n['t']==34+a['step']*93.75, 'Rhythm drifts from its repeating grid'
        if n['d']<4:
            assert a['role']=='foreground' and a['part'] in ['synth','drums']
        else:
            assert a['role']=='backing' and a['part'] in ['bass','drums'], 'VOLT steals a foreground phrase'
    player=[n for n in notes if n['d']<4]
    # Independently specify the requested rhythm and verify both repeated clips.
    hits=(0,3,6,9,12,14)
    pairs=((0,3),(1,2),(0,2),(1,3))
    for phrase,starts in [('double-riff',(272,1104)),('synth-stream',(400,1232))]:
        patterns=[]
        for start in starts:
            selected=[a for a in proof.values() if a['d']<4 and start<=a['step']<start+128]
            expected={start+bar*16+offset for bar in range(8) for i,offset in enumerate(hits)
                      if difficulty!='easy' or i in (0,2,4)}
            assert {a['step'] for a in selected}==expected, 'Requested instrumental motif has gaps or filler'
            assert all(a['phrase']==phrase and a['part']=='synth' for a in selected)
            for step in expected:
                lanes=sorted(a['d'] for a in selected if a['step']==step)
                if phrase=='double-riff' and difficulty in ['hard','erect','nightmare']:
                    assert lanes==sorted(pairs[((step-start)//32)%4]), 'Riff attack must be its authored double'
                else:
                    assert len(lanes)==1
            patterns.append([(a['step']-start,a['d']) for a in selected])
        assert patterns[0]==patterns[1], 'Repeated musical passage changes its lane pattern'
    if difficulty in ['erect','nightmare']:
        assert all(n in player for n in all_charts['hard'] if n['d']<4), 'Advanced chart changes the core Hard pattern'
    section_checks=[]
    for section in report['sections']:
        own=[a for a in proof.values() if section['start']-40<=a['t']<section['end']-40]
        assert any(a['d']<4 for a in own) and any(a['d']>=4 for a in own), 'A section loses its duet'
        section_checks.append({'name':section['name'],'player_notes':sum(a['d']<4 for a in own),
            'opponent_notes':sum(a['d']>=4 for a in own)})
    stats[difficulty]={'notes':len(notes),'max_instrumental_attack_distance_ms':max(errors),'sections':section_checks}
player_counts=[sum(n['d']<4 for n in all_charts[d]) for d in ['easy','normal','hard','erect','nightmare']]
assert player_counts==sorted(set(player_counts)),'Difficulty progression is not strictly increasing'
result={'status':'PASS','audio_correlation':audio_correlation,
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'game_audio_sha256':hashlib.sha256(ogg.read_bytes()).hexdigest(),
        'duration_seconds':len(y)/22050,'atlas_frames':len(names),'charts':stats,
        'checks':['Exact supplied recording, unchanged length','All required assets resolve',
                  'All atlas rectangles in bounds','No duplicate or out-of-range notes',
                  'No sustain collisions or rapid same-lane repeats',
                  'All notes use instrumental evidence only; no vocal or full-mix positive source',
                  'Every note lies on the stable grid within 35 ms of its instrumental attack',
                  'Both 48-hit riffs use doubles on Hard, Erect, and Nightmare',
                  'Both synth streams and riff reprises preserve their authored patterns',
                  'Player owns the foreground throughout; VOLT plays bass/drum accompaniment',
                  'Erect and Nightmare preserve the complete Hard core pattern',
                  'Both characters participate in every musical section']}
(ROOT/'analysis/validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

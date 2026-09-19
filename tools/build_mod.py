"""Build ENERGIZE for the official FNF 0.8.x engine, without changing mechanics."""
from pathlib import Path
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'mods/energize'
BPM, BEAT, OFFSET = 160, 0.375, 0.034

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')

def asset(path):
    p = MOD / path
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def artwork():
    # Keep generated PNGs unchanged. Sparrow rectangles and frame offsets provide animation.
    src = ROOT / 'art/volt-atlas.png'
    shutil.copy2(src, asset('images/characters/volt.png'))
    shutil.copy2(ROOT/'art/dynamo.png', asset('images/stages/dynamo.png'))
    pixels = np.asarray(Image.open(src))
    regions = [(0,0,520,512),(540,0,1060,512),(1060,0,1536,512),
               (0,512,512,1024),(512,512,1070,1024),(1070,512,1536,1024)]
    names = ['idle','left','down','up','right','cheer']
    atlas = ET.Element('TextureAtlas', imagePath='volt.png')
    for name, (x0,y0,x1,y1) in zip(names,regions):
        yy,xx = np.where(pixels[y0:y1,x0:x1,3] > 100)
        x,y = x0+int(xx.min()), y0+int(yy.min())
        w,h = int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1)
        # A padded common canvas keeps every pose centered on the same foot anchor.
        for f,bob in enumerate([0,3,5,3,1,0]):
            ET.SubElement(atlas,'SubTexture',name=f'{name}{f:04d}',x=str(x),y=str(y),
                          width=str(w),height=str(h),frameX=str(-(600-w)//2),
                          frameY=str(-(520-h)+bob),frameWidth='600',frameHeight='540')
    ET.indent(atlas)
    ET.ElementTree(atlas).write(asset('images/characters/volt.xml'),encoding='utf-8',xml_declaration=True)

    # Small UI art is drawn directly as vector-like shapes, not derived from the generated art.
    im = Image.new('RGBA',(300,150)); d=ImageDraw.Draw(im)
    for base,losing in [(0,False),(150,True)]:
        def poly(points,fill): d.polygon([(base+x,y) for x,y in points],fill=fill,outline='#080817',width=5)
        poly([(32,44),(22,19),(53,35),(59,15),(84,49)],'#d5ff3e')
        poly([(26,38),(113,43),(129,118),(20,125)],'#51417a')
        poly([(38,53),(103,57),(112,105),(34,110)],'#0b182b')
        if losing:
            d.line([(base+44,67),(base+59,81),(base+44,83),(base+58,67)],fill='#24efff',width=6)
            d.line([(base+79,69),(base+94,83),(base+79,85),(base+94,69)],fill='#24efff',width=6)
        else:
            poly([(43,65),(65,76),(50,83)],'#31f4ff')
            poly([(77,76),(99,64),(92,83)],'#31f4ff')
        d.line([(base+49,94),(base+61,99),(base+72,93),(base+90,96)],fill='#31f4ff',width=5)
        d.rounded_rectangle((base+13,66,base+31,102),radius=8,fill='#21c8dd',outline='#080817',width=5)
    im.save(asset('images/icons/icon-volt.png'))
    # A distinct tiny pixel portrait for the Freeplay capsule.
    pixel=Image.new('RGBA',(32,32)); p=ImageDraw.Draw(pixel)
    p.polygon([(8,10),(5,1),(12,6),(14,1),(19,11)],fill='#d5ff3e',outline='#090817')
    p.rectangle((4,9,28,29),fill='#090817')
    p.rectangle((7,11,26,27),fill='#63528c')
    p.rectangle((9,13,24,24),fill='#091525')
    p.polygon([(10,15),(16,18),(12,19)],fill='#21efff')
    p.polygon([(18,18),(24,15),(22,19)],fill='#21efff')
    p.line([(12,22),(15,23),(18,21),(21,22)],fill='#21efff',width=1)
    p.rectangle((2,15,6,24),fill='#0b131e');p.rectangle((3,16,5,22),fill='#21b8d5')
    pixel.save(asset('images/freeplay/icons/voltpixel.png'))
    badge=Image.new('RGBA',(256,256),'#17132c');b=ImageDraw.Draw(badge)
    b.rounded_rectangle((10,10,246,246),radius=32,outline='#2af3ff',width=7)
    b.polygon([(80,30),(109,76),(130,35),(190,111),(160,101),(126,144),(69,75)],
              fill='#d5ff3e',outline='#090817',width=7)
    bf=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',35)
    b.text((36,155),'ENERGIZE',font=bf,fill='white')
    bf=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24)
    b.text((75,201),'VS VOLT',font=bf,fill='#29ebff')
    badge.save(asset('_polymod_icon.png'))
    title=Image.new('RGBA',(590,100));d=ImageDraw.Draw(title)
    font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',78)
    d.text((19,-1),'ENERGIZE',font=font,fill='#ffffff',stroke_width=7,stroke_fill='#111021')
    title.save(asset('images/storymenu/titles/energize.png'))

def static_data():
    write_json(MOD/'_polymod_meta.json',{
        'id':'energize-volt','title':'ENERGIZE: VS VOLT','description':'Battle VOLT at The Dynamo. Energize by Tonytonychopper999. Three beat-matched charts, original art, classic FNF gameplay.',
        'contributors':[{'name':'Tonytonychopper999','role':'Music (user-supplied track)'},
                        {'name':'Leane + Codex','role':'Mod concept, chart, integration and artwork'}],
        'api_version':'0.8.4','mod_version':'1.0.0','license':'See CREDITS.md'})
    animations=[{'name':name,'prefix':prefix,'frameRate':24,'looped':False}
                for name,prefix in [('idle','idle'),('danceLeft','idle'),('danceRight','cheer'),
                                    ('singLEFT','left'),('singDOWN','down'),('singUP','up'),('singRIGHT','right'),('cheer','cheer')]]
    write_json(MOD/'data/characters/volt.json',{
        'version':'1.0.0','name':'VOLT','renderType':'sparrow','assetPath':'characters/volt',
        'scale':1.0,'singTime':4,'danceEvery':1,'startingAnimation':'idle','isPixel':False,
        'healthIcon':{'id':'volt'},'offsets':[0,0],'cameraOffsets':[0,-30],'animations':animations})
    write_json(MOD/'data/stages/dynamo.json',{
        'version':'1.0.1','name':'The Dynamo','cameraZoom':0.8,
        'props':[{'name':'dynamo','assetPath':'stages/dynamo','position':[-320,-270],
                  'scale':[1.35,1.35],'scroll':[1,1],'zIndex':0}],
        'characters':{'bf':{'zIndex':300,'position':[1090,875],'cameraOffsets':[-210,-70]},
                      'dad':{'zIndex':200,'position':[290,875],'cameraOffsets':[210,-40]},
                      'gf':{'zIndex':100,'position':[700,760],'cameraOffsets':[0,0],'scale':0.85}}})
    write_json(MOD/'data/levels/energize.json',{
        'version':'1.0.0','name':'ENERGIZE: VS VOLT','titleAsset':'storymenu/titles/energize',
        'background':'#231740','songs':['energize'],'visible':True,'capsule':{'name':'VOLT'},
        'props':[{'assetPath':'characters/volt','scale':0.65,'offsets':[65,35],
                  'animations':[{'name':'idle','prefix':'idle','frameRate':18,'looped':True}]},
                 {'assetPath':'storymenu/props/bf','scale':1,'offsets':[150,80],
                  'animations':[{'name':'idle','prefix':'idle0','frameRate':24},
                                {'name':'confirm','prefix':'confirm0','frameRate':24}]}]})
    write_json(MOD/'data/songs/energize/energize-metadata.json',{
        'version':'2.2.4','songName':'Energize','artist':'Tonytonychopper999','charter':'Leane + Codex',
        'timeFormat':'ms','offsets':{'instrumental':0},'generatedBy':'ENERGIZE chart builder 1.0',
        'timeChanges':[{'t':0,'b':0,'bpm':BPM,'n':4,'d':4,'bt':[4,4,4,4]},
                       {'t':OFFSET*1000,'b':0,'bpm':BPM,'n':4,'d':4,'bt':[4,4,4,4]}],
        'playData':{'songVariations':[],'difficulties':['easy','normal','hard'],
                    'characters':{'player':'bf','girlfriend':'gf','opponent':'volt',
                                  'playerVocals':[],'opponentVocals':[],'altInstrumentals':[]},
                    'stage':'dynamo','noteStyle':'funkin','ratings':{'easy':3,'normal':6,'hard':9},
                    'album':'volume1','previewStart':0.27,'previewEnd':0.39}})

def charts():
    z=np.load(ROOT/'analysis/features.npz');times=z['times'];strength=z['onset'];rms=z['rms']
    peaks=np.where((strength>np.roll(strength,1))&(strength>=np.roll(strength,-1)))[0]
    candidates=[]
    # Build on real acoustic attacks near a 160 BPM sixteenth-note lattice.
    for step in range(16,1904):
        grid=OFFSET+step*BEAT/4
        nearby=peaks[np.abs(times[peaks]-grid)<0.036]
        if not len(nearby): continue
        p=max(nearby,key=lambda p:strength[p]*np.exp(-((times[p]-grid)/.035)**2))
        if strength[p]<.2 or rms[p]<.045:continue
        # Spectral-flux maxima sit slightly after the leading edge of an attack.
        attack=float(times[p]-.006)
        candidates.append({'step':step,'t':round(attack*1000,3),'power':float(strength[p]),'grid':grid*1000})
    motifs=[[0,1,2,3,2,1,0,2],[0,2,1,3,0,1,3,2],[3,2,0,1,2,3,1,0],
            [0,1,0,2,3,2,1,3],[2,0,1,3,1,2,3,0],[0,3,2,1,0,2,1,3]]
    charts={}; evidence={}; all_attacks=[]
    for difficulty in ['easy','normal','hard']:
        notes=[]; last={0:(-9999,-1),1:(-9999,-1)}
        for c in candidates:
            s=c['step'];beat=s/4;bar=int((beat-4)//4);phrase=int((beat-4)//8)
            side=1 if phrase%2==0 else 0 # Native FNF: 0..3 player, 4..7 opponent.
            # Leave instrumental opening, breakdown breathing room and reverb tail uncharted.
            if 76.6<c['t']/1000<78.0 or c['t']>178600:continue
            if difficulty=='easy': keep=(s%4==0 and c['power']>.24) or (s%8==6 and c['power']>.95)
            elif difficulty=='normal':keep=(s%2==0 and c['power']>.28) or (s%16 in [11,15] and c['power']>1.10)
            else:keep=(s%2==0 and c['power']>.23) or (s%2==1 and c['power']>.48)
            if not keep:continue
            # Consistent phrase motifs, with higher density only where attacks support it.
            motif=motifs[(bar//4)%len(motifs)]
            lane=motif[(s//2)%8]
            if s%2:lane=motif[((s//2)+3)%8]
            prev_t,prev_lane=last[side]
            min_gap={'easy':240,'normal':145,'hard':78}[difficulty]
            if c['t']-prev_t<min_gap:continue
            if lane==prev_lane and c['t']-prev_t<300:lane=(lane+1+(bar%2))%4
            note={'t':c['t'],'d':lane+side*4,'l':0}
            notes.append(note);last[side]=(c['t'],lane);all_attacks.append(c)
        # Sustains only in roomy phrase endings, never under a later note or through a handoff.
        for i,n in enumerate(notes):
            pos=(n['t']/1000-OFFSET)/BEAT
            phrase=int((pos-4)//8)
            end=OFFSET+(4+(phrase+1)*8)*BEAT
            own=[a for a in notes[i+1:] if a['d']//4==n['d']//4]
            gap=(own[0]['t']-n['t']) if own else 9999
            remaining=end*1000-n['t']
            # The backing texture sustains here; keep the hold shorter than the next onset.
            if 520<remaining<1250 and gap>560 and phrase%3==2:
                n['l']=round(min(375,remaining-180,gap-140),3)
        notes.sort(key=lambda n:(n['t'],n['d']))
        charts[difficulty]=notes
        player=[n for n in notes if n['d']<4]
        evidence[difficulty]={'player_notes':len(player),'opponent_notes':len(notes)-len(player),
                              'holds':sum(n['l']>0 for n in player),
                              'peak_player_notes_in_1s':max(sum(x['t']>=n['t'] and x['t']<n['t']+1000 for x in player) for n in player),
                              'first_note_ms':notes[0]['t'],'last_note_ms':notes[-1]['t']}
    events=[{'t':0,'e':'FocusCamera','v':{'char':-1,'x':690,'y':530,'duration':0,'ease':'INSTANT'}}]
    for phrase in range(59):
        t=(OFFSET+(4+phrase*8)*BEAT)*1000
        events.append({'t':round(t,3),'e':'FocusCamera','v':{'char':1 if phrase%2==0 else 0,'duration':4,'ease':'CLASSIC'}})
    events.append({'t':179000,'e':'PlayAnimation','v':{'target':'dad','anim':'cheer','force':True}})
    write_json(MOD/'data/songs/energize/energize-chart.json',{'version':'2.0.0',
               'scrollSpeed':{'easy':1.5,'normal':2.0,'hard':2.5},'events':events,'notes':charts,
               'generatedBy':'ENERGIZE chart builder 1.0'})
    errors=np.array([abs(c['t']-c['grid']) for c in all_attacks])
    evidence.update({'bpm':BPM,'grid_offset_ms':OFFSET*1000,'duration_seconds':187.570794,
        'method':'Band-weighted spectral-flux attacks near a 160 BPM sixteenth grid; six-millisecond leading-edge correction; authored lane motifs and alternating eight-beat phrases.',
        'grid_error_median_ms':float(np.median(errors)),'grid_error_p95_ms':float(np.percentile(errors,95)),
        'grid_error_max_ms':float(max(errors)),
        'listening_review':'User played the native level and reported: Timing feels good. Also checked computationally against the actual game OGG.'})
    write_json(ROOT/'analysis/chart-report.json',evidence)
    print(json.dumps(evidence,indent=2))

if __name__=='__main__':
    artwork();static_data();charts()

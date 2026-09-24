"""Build ENERGIZE for the official FNF 0.8.x engine, without changing mechanics."""
from pathlib import Path
import json
import shutil
import xml.etree.ElementTree as ET
from copy import deepcopy
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from musical_chart import build_charts, TIMING_OFFSET_MS
from build_effects import build_effects

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'mods/energize'
BPM, BEAT = 160, 0.375
OFFSET = TIMING_OFFSET_MS/1000

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
        'id':'energize-volt','title':'ENERGIZE: VS VOLT','description':'Battle VOLT at The Dynamo. A musical duet across five difficulties, with a reactive reactor and character effects. Music by Tonytonychopper999.',
        'contributors':[{'name':'Tonytonychopper999','role':'Music (user-supplied track)'},
                        {'name':'Leane + Codex','role':'Mod concept, chart, integration and artwork'}],
        'api_version':'0.8.4','mod_version':'1.4.0','license':'See CREDITS.md'})
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
                  'scale':[1.35,1.35],'scroll':[1,1],'zIndex':0}]+build_effects(),
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
    metadata={
        'version':'2.2.4','songName':'Energize','artist':'Tonytonychopper999','charter':'Leane + Codex',
        'timeFormat':'ms','offsets':{'instrumental':0},'generatedBy':'ENERGIZE chart builder 1.4',
        'timeChanges':[{'t':0,'b':0,'bpm':BPM,'n':4,'d':4,'bt':[4,4,4,4]},
                       {'t':OFFSET*1000,'b':0,'bpm':BPM,'n':4,'d':4,'bt':[4,4,4,4]}],
        'playData':{'songVariations':['erect'],'difficulties':['easy','normal','hard'],
                    'characters':{'player':'bf','girlfriend':'gf','opponent':'volt',
                                  'playerVocals':[],'opponentVocals':[],'altInstrumentals':[]},
                    'stage':'dynamo','noteStyle':'funkin','ratings':{'easy':3,'normal':7,'hard':10},
                    'album':'volume1','previewStart':0.27,'previewEnd':0.39}}
    write_json(MOD/'data/songs/energize/energize-metadata.json',metadata)
    advanced=deepcopy(metadata)
    advanced['playData'].update({'songVariations':[],'difficulties':['erect','nightmare'],
                                 'ratings':{'erect':13,'nightmare':16}})
    # Same supplied recording in both variations; do not request a nonexistent remix.
    advanced['playData']['characters']['instrumental']=''
    write_json(MOD/'data/songs/energize/energize-metadata-erect.json',advanced)

if __name__=='__main__':
    artwork();static_data();build_charts()

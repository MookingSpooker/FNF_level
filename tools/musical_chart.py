"""Keep the familiar foreground rhythm on Boyfriend and give VOLT accompaniment."""
from collections import Counter
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT/'mods/energize'
DIFFICULTIES = ['easy', 'normal', 'hard', 'erect', 'nightmare']
TIMING_OFFSET_MS = 34.0
# These boundaries control camera and lighting energy, never lead ownership.
SECTIONS = [
    ('Opening', 4, 52, False), ('Charge I', 52, 68, False),
    ('Drop I', 68, 100, True), ('Synth interlude I', 100, 132, False),
    ('Drop I climax', 132, 196, True), ('Breath', 196, 208, False),
    ('Reprise', 208, 260, False), ('Charge II', 260, 276, False),
    ('Drop II', 276, 308, True), ('Synth interlude II', 308, 340, False),
    ('Final overload', 340, 476, True)]

def sections(offset=TIMING_OFFSET_MS):
    return [{'name':name, 'start':offset+a*375, 'end':offset+b*375,
             'leadSide':0, 'drop':drop} for name,a,b,drop in SECTIONS]

def write(path, value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def chart_stats(notes):
    player=[n for n in notes if n['d']<4]
    groups=Counter(n['t'] for n in player)
    return {'player_notes':len(player),'opponent_notes':len(notes)-len(player),
        'two_note_chords':sum(n==2 for n in groups.values()),
        'holds':sum(n['l']>0 for n in player),
        'peak_player_notes_in_1s':max(sum(n['t']<=x['t']<n['t']+1000 for x in player) for n in player)}

def mix_attacks():
    """Use the exact detector and timestamps of the user-preferred original."""
    z=np.load(ROOT/'analysis/features.npz')
    times,strength,rms=z['times'],z['onset'],z['rms']
    peaks=np.where((strength>np.roll(strength,1))&(strength>=np.roll(strength,-1)))[0]
    candidates=[]
    for step in range(16,1904):
        grid=(TIMING_OFFSET_MS+step*93.75)/1000
        near=peaks[np.abs(times[peaks]-grid)<.036]
        if not len(near):continue
        p=max(near,key=lambda p:strength[p]*np.exp(-((times[p]-grid)/.035)**2))
        if strength[p]<.2 or rms[p]<.045:continue
        time=round(float(times[p]-.006)*1000,3)
        if 76600<time<78000 or time>178600:continue
        candidates.append({'t':time,'step':step,'power':float(strength[p]),
            'peak':round(float(times[p])*1000,3),'grid':round(grid*1000,3)})
    return candidates

def available_lane(notes, time, preferred, side=0, length=0):
    for lane in [preferred,(preferred+2)%4,(preferred+1)%4,(preferred+3)%4]:
        data=lane+side*4
        if not any(n['d']==data and (abs(n['t']-time)<145 or
            n['t']<=time<=n['t']+n['l'] or time<=n['t']<=time+length) for n in notes):
            return data
    return None

def build_charts():
    reference=json.loads((ROOT/'analysis/reference-v1-chart.json').read_text())['notes']
    analysis=json.loads((ROOT/'analysis/parts.json').read_text())
    attacks=mix_attacks(); by_time={a['t']:a for a in attacks}
    drums={a['step']:a for a in analysis['parts']['drums']}
    arrangement=sections();charts={};evidence={};provenance={}
    for rank,difficulty in enumerate(DIFFICULTIES):
        baseline=reference[difficulty if rank<3 else 'hard']
        notes=[];proof=[]
        # Transfer both original characters' foreground phrases to the player.
        # Keep every original timestamp and sustain; only resolve lane conflicts.
        for old in baseline:
            a=by_time[old['t']]
            data=available_lane(notes,old['t'],old['d']%4,length=old['l'])
            assert data is not None, 'An original foreground attack would be lost'
            notes.append({'t':old['t'],'d':data,'l':old['l']})
            proof.append({'t':old['t'],'d':data,'role':'foreground','part':'full_mix',
                'source':'original','power':a['power'],'step':a['step'],'attack':old['t']})
        # Advanced charts retain the exact Hard rhythm. Extra attacks must be
        # audible in the mix; per-stem normalization cannot promote quiet texture.
        if rank>=3:
            threshold=.40 if rank==3 else .32
            for a in sorted(attacks,key=lambda a:-a['power']):
                if a['power']<threshold or any(abs(n['t']-a['t'])<78 for n in notes):continue
                preferred=[0,2,1,3,2,0,3,1][a['step']%8]
                data=available_lane(notes,a['t'],preferred)
                if data is None:continue
                notes.append({'t':a['t'],'d':data,'l':0})
                proof.append({'t':a['t'],'d':data,'role':'foreground','part':'full_mix',
                    'source':'extra','power':a['power'],'step':a['step'],'attack':a['t']})
            # Doubles emphasize existing strong hits, preserving the melody rhythm.
            last_chord=-9999
            for n in sorted(notes.copy(),key=lambda n:n['t']):
                a=by_time[n['t']];drum=drums.get(a['step'])
                spacing=750 if rank==3 else 375
                if (n['t']-last_chord<spacing or a['power']<(.95 if rank==3 else .75)
                    or not drum or drum['strength']<.75 or abs(drum['attack']-n['t'])>32):continue
                data=available_lane(notes,n['t'],(n['d']+2)%4)
                if data is None:continue
                notes.append({'t':n['t'],'d':data,'l':0});last_chord=n['t']
                proof.append({'t':n['t'],'d':data,'role':'accent','part':'drums',
                    'source':'accent','power':a['power'],'step':a['step'],'attack':drum['attack']})
        player_times=sorted(set(n['t'] for n in notes))
        # VOLT follows a sparse bass/drum backing line throughout. Shared accents
        # align with the foreground hit; intervening notes retain their own onset.
        backing={}
        for part in ['bass','drums']:
            for a in analysis['parts'][part]:
                s=a['step']
                if s%4!=0 and not (rank>=1 and s%2==0 and a['strength']>.8):continue
                if a['strength']<.45 or a['energy']<.18:continue
                priority=a['strength']*(1.3 if part=='drums' and s%4==0 else 1)
                if s not in backing or priority>backing[s][0]:backing[s]=(priority,part,a)
        last=-9999;index=0
        for _,part,a in sorted(backing.values(),key=lambda x:x[2]['attack']):
            time=a['attack']
            nearest=min(player_times,key=lambda t:abs(t-time))
            if abs(nearest-time)<32:time=nearest
            if time<1530 or 76600<time<78000 or time>178600:continue
            if time-last<([260,165,145,145,145][rank]):continue
            data=available_lane(notes,time,[0,2,1,3][index%4],side=1)
            if data is None:continue
            notes.append({'t':time,'d':data,'l':0});last=time;index+=1
            proof.append({'t':time,'d':data,'role':'backing','part':part,
                'source':'stem','step':a['step'],'attack':a['attack'],'strength':a['strength']})
        notes.sort(key=lambda n:(n['t'],n['d']));proof.sort(key=lambda n:(n['t'],n['d']))
        charts[difficulty]=notes;provenance[difficulty]=proof
        stats=chart_stats(notes)
        stats['original_foreground_attacks_retained']=len(baseline)
        stats['player_roles']=dict(Counter(a['role'] for a in proof if a['d']<4))
        stats['sections']=[{'name':s['name'],'player_role':'foreground',
            'player_notes':sum(s['start']-40<=n['t']<s['end']-40 and n['d']<4 for n in notes),
            'opponent_notes':sum(s['start']-40<=n['t']<s['end']-40 and n['d']>=4 for n in notes)} for s in arrangement]
        evidence[difficulty]=stats
    events=[{'t':0,'e':'FocusCamera','v':{'char':-1,'x':690,'y':530,'duration':0,'ease':'INSTANT'}}]
    for s in arrangement:
        events.extend([
            {'t':s['start'],'e':'FocusCamera','v':{'char':-1,'x':715,'y':530,'duration':8,'ease':'sineInOut'}},
            {'t':s['start'],'e':'ZoomCamera','v':{'zoom':.76 if s['drop'] else .8,
                'duration':8,'mode':'direct','ease':'sine','easeDir':'InOut'}}])
    events.append({'t':179000,'e':'PlayAnimation','v':{'target':'dad','anim':'cheer','force':True}})
    events.sort(key=lambda e:e['t'])
    for suffix,diffs,speeds in [('',DIFFICULTIES[:3],[1.5,2.0,2.5]),('-erect',DIFFICULTIES[3:],[2.8,3.1])]:
        write(MOD/f'data/songs/energize/energize-chart{suffix}.json',{'version':'2.0.0',
            'scrollSpeed':dict(zip(diffs,speeds)),'events':events,'notes':{d:charts[d] for d in diffs},
            'generatedBy':'ENERGIZE foreground arrangement 1.3'})
    write(ROOT/'analysis/note-provenance.json',provenance)
    write(ROOT/'analysis/chart-report.json',{'version':'1.3.0','bpm':160,
        'grid_offset_ms':TIMING_OFFSET_MS,'duration_seconds':187.570794,
        'reference_commit':'3d1aa1c','sections':arrangement,'difficulties':evidence,
        'method':'Original full-mix foreground rhythm retained on Boyfriend for the entire song; sparse separated bass/drum accompaniment on VOLT. Advanced charts preserve Hard and add mix-audible attacks and strong shared accents.',
        'timing_note':'Original attack timestamps are preserved exactly; neither a new global shift nor forced grid quantization is applied. Perceptual feel still needs human playtesting.'})
    print(json.dumps({d:{k:v for k,v in evidence[d].items() if k!='sections'} for d in DIFFICULTIES},indent=2))

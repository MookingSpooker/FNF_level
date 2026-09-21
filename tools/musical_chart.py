"""Arrange the two characters as a duet, with section-based musical ownership."""
from collections import Counter
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT/'mods/energize'
DIFFICULTIES = ['easy', 'normal', 'hard', 'erect', 'nightmare']
# Beat boundaries follow changes in the arrangement, including the two quieter
# synth interludes. Lead ownership never alternates on a repeating timer.
SECTIONS = [
    ('Opening', 4, 52, 1, False), ('Charge I', 52, 68, 1, False),
    ('Drop I', 68, 100, 0, True), ('Synth interlude I', 100, 132, 1, False),
    ('Drop I climax', 132, 196, 0, True), ('Breath', 196, 208, 1, False),
    ('Reprise', 208, 260, 1, False), ('Charge II', 260, 276, 1, False),
    ('Drop II', 276, 308, 0, True), ('Synth interlude II', 308, 340, 1, False),
    ('Final overload', 340, 476, 0, True)]

def sections(offset):
    return [{'name':name, 'start':round(offset+a*375,3), 'end':round(offset+b*375,3),
             'leadSide':side, 'drop':drop} for name,a,b,side,drop in SECTIONS]

def write(path, value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def chart_stats(notes):
    player=[n for n in notes if n['d']<4]
    groups=Counter(n['t'] for n in player)
    return {'player_notes':len(player),'opponent_notes':len(notes)-len(player),
        'two_note_chords':sum(n==2 for n in groups.values()),
        'holds':sum(n['l']>0 for n in player),
        'peak_player_notes_in_1s':max(sum(n['t']<=x['t']<n['t']+1000 for x in player) for n in player)}

def build_charts():
    analysis=json.loads((ROOT/'analysis/parts.json').read_text())
    offset=analysis['offset_ms']; arrangement=sections(offset)
    features=np.load(ROOT/'analysis/parts-features.npz')
    charts={}; evidence={}; provenance={}
    lead_by_step={a['step']:a for a in analysis['parts']['lead']}
    bass_by_step={a['step']:a for a in analysis['parts']['bass']}
    drums_by_step={a['step']:a for a in analysis['parts']['drums']}
    for rank,difficulty in enumerate(DIFFICULTIES):
        notes=[]; proof=[]; last_time=[-9999,-9999]; last_lane=[-1,-1]
        last_pitch=[60,60]; lane_times=[-9999]*8
        for s in range(16,1904):
            time=round(offset+s*93.75,3)
            section=next((a for a in arrangement if a['start']<=time<a['end']),None)
            if section is None or 76600<time<78000:continue
            for side in [0,1]:
                is_lead=side==section['leadSide']; drop=section['drop']
                part='lead' if is_lead else 'bass'
                candidate=(lead_by_step if is_lead else bass_by_step).get(s)
                drum=drums_by_step.get(s)
                # The backing part is bass-led. Strong drum accents fill its gaps;
                # neither character borrows the other character's lead stream.
                if not is_lead and drum and (candidate is None or
                        (s%4==0 and drum['strength']>candidate['strength']*1.6)):
                    candidate=drum; part='drums'
                if candidate is None:continue
                strength=candidate['strength']
                if is_lead:
                    threshold=[.60,.56,.48,.34,.22][rank]
                    keep=(s%4==0 or (rank>=1 and s%2==0) or
                        (rank>=2 and strength>[1.15,.82,.48][rank-2]))
                else:
                    threshold=[.48,.40,.34,.28,.22][rank]
                    keep=(s%4==0 or (rank>=1 and s%8==6 and strength>.5) or
                        (rank>=2 and s%2==0) or (rank>=3 and strength>[1.1,.65][rank-3]))
                if not keep or strength<threshold:continue
                if time-last_time[side]<[280,180,90,90,90][rank]:continue
                pitch=candidate.get('pitch',last_pitch[side])
                if not 35<pitch<96:pitch=last_pitch[side]
                # Four pitch registers preserve melodic contour. Repeated fast
                # pitches alternate fingers instead of producing awkward jacks.
                if is_lead:
                    lane=int(np.searchsorted([51,59,67],pitch))
                    if lane==last_lane[side] and time-last_time[side]<280:
                        lane=(lane+(1 if pitch>=last_pitch[side] else -1))%4
                else:
                    lane=[0,2,1,3][(s//2)%4] if part=='drums' else [0,1,3,2][int(round(pitch))%4]
                    if lane==last_lane[side] and time-last_time[side]<280:lane=(lane+2)%4
                lane=next((x for x in [lane,(lane+2)%4,(lane+1)%4,(lane+3)%4]
                    if time-lane_times[x+side*4]>=180),None)
                if lane is None:continue
                note={'t':time,'d':lane+side*4,'l':0}
                notes.append(note);lane_times[note['d']]=time
                proof.append({'t':time,'d':note['d'],'part':part,'section':section['name'],
                    'attack':candidate['attack'],'deviation_ms':candidate['deviation_ms'],
                    'pitch':candidate.get('pitch'),'strength':strength})
                last_time[side]=time;last_lane[side]=lane;last_pitch[side]=pitch
                # Doubles denote a simultaneous lead + strong drum accent, never
                # arbitrary density. Erect and Nightmare increase accent coverage.
                accent=rank>=2 and is_lead and drop and drum and drum['strength']>.65 and (
                    (rank==2 and s%16==0) or (rank==3 and s%8==0) or (rank==4 and s%4==0))
                if accent:
                    second=next((x for x in [(lane+2)%4,(lane+1)%4,(lane+3)%4]
                        if time-lane_times[x+side*4]>=180),None)
                    if second is not None:
                        data=second+side*4
                        notes.append({'t':time,'d':data,'l':0});lane_times[data]=time
                        proof.append({'t':time,'d':data,'part':'drums','section':section['name'],
                            'attack':drum['attack'],'deviation_ms':drum['deviation_ms'],
                            'pitch':None,'strength':drum['strength']})
        notes.sort(key=lambda n:(n['t'],n['d']))
        # Sustains require a stable pitched tail and a real rest on that side.
        lookup={(a['t'],a['d']):a for a in proof}
        for side in [0,1]:
            own=[n for n in notes if n['d']//4==side]
            for i,n in enumerate(own[:-1]):
                info=lookup[(n['t'],n['d'])];part=info['part'];gap=own[i+1]['t']-n['t']
                if gap<460 or part=='drums':continue
                tail=min(562.5,gap-150)
                mask=(features['times']*1000>=n['t']+80)&(features['times']*1000<n['t']+tail)
                if not mask.any():continue
                pitch=features[part+'_pitch'][mask];energy=features[part+'_rms'][mask]
                if np.median(energy)>.16 and np.percentile(pitch,80)-np.percentile(pitch,20)<1.5:
                    n['l']=round(tail,3)
        charts[difficulty]=notes;provenance[difficulty]=proof
        stats=chart_stats(notes)
        stats['parts']=dict(Counter(a['part'] for a in proof if a['d']<4))
        stats['sections']=[{'name':section['name'],'player_role':'lead' if section['leadSide']==0 else 'backing',
            'player_notes':sum(section['start']<=n['t']<section['end'] and n['d']<4 for n in notes),
            'opponent_notes':sum(section['start']<=n['t']<section['end'] and n['d']>=4 for n in notes)} for section in arrangement]
        evidence[difficulty]=stats
    events=[{'t':0,'e':'FocusCamera','v':{'char':-1,'x':690,'y':530,'duration':0,'ease':'INSTANT'}}]
    for section in arrangement:
        events.extend([
            {'t':section['start'],'e':'FocusCamera','v':{'char':-1,'x':715 if section['leadSide']==0 else 660,
                'y':530,'duration':8,'ease':'sineInOut'}},
            {'t':section['start'],'e':'ZoomCamera','v':{'zoom':.76 if section['drop'] else .8,
                'duration':8,'mode':'direct','ease':'sine','easeDir':'InOut'}}])
    events.append({'t':179000,'e':'PlayAnimation','v':{'target':'dad','anim':'cheer','force':True}})
    events.sort(key=lambda e:e['t'])
    for suffix,diffs,speeds in [('',DIFFICULTIES[:3],[1.5,2.1,2.6]),('-erect',DIFFICULTIES[3:],[2.9,3.2])]:
        write(MOD/f'data/songs/energize/energize-chart{suffix}.json', {'version':'2.0.0',
            'scrollSpeed':dict(zip(diffs,speeds)), 'events':events, 'notes':{d:charts[d] for d in diffs},
            'generatedBy':'ENERGIZE musical arrangement 1.2'})
    write(ROOT/'analysis/note-provenance.json',provenance)
    deviations=[abs(a['deviation_ms']) for a in provenance['nightmare']]
    report={'bpm':160,'grid_offset_ms':offset,'duration_seconds':187.570794,
        'method':analysis['method'],'sections':arrangement,'difficulties':evidence,
        'attack_grid_deviation_median_ms':float(np.median(deviations)),
        'attack_grid_deviation_p95_ms':float(np.percentile(deviations,95)),
        'attack_grid_deviation_max_ms':max(deviations),
        'timing_note':'This measures agreement with estimated stem attacks, not perceptual timing accuracy. Full-mix playback is unchanged.'}
    write(ROOT/'analysis/chart-report.json',report)
    print(json.dumps({d:{k:v for k,v in evidence[d].items() if k!='sections'} for d in DIFFICULTIES},indent=2))

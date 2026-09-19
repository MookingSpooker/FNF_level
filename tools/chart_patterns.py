"""Drop arrangements and the two advanced charts, using existing audio attack times."""
from collections import Counter

# Boundaries are musical sixteenth-note indices on the existing 160 BPM grid.
DROP_STEPS = [(68 * 4, 196 * 4), (276 * 4, 476 * 4)]
DROP_TIMES = [(25.534, 73.534), (103.534, 178.534)]
RUNS = [[0,1,2,3,2,1,0,2], [3,2,1,0,1,2,3,1],
        [0,2,1,3,2,0,3,1], [1,0,2,3,1,2,0,3]]

def in_drop(step):
    return any(start <= step < end for start,end in DROP_STEPS)

def available_lane(notes, time, side, preferred):
    """Never force a chord finger to re-tap within 145ms, or across a sustain."""
    for lane in [preferred,(preferred+2)%4,(preferred+1)%4,(preferred+3)%4]:
        data=lane+side*4
        conflicts=[n for n in notes if n['d']==data and
                   (abs(n['t']-time)<145 or n['t']<=time<=n['t']+n['l'] or
                    time<n['t']<time+145)]
        if not conflicts:return data
    return None

def insert(notes,c,side,lane,chord=False):
    time=c['t']
    attacks=[n for n in notes if n['d']//4==side and abs(n['t']-time)<78]
    if attacks and (not chord or any(n['t']!=time for n in attacks) or len(attacks)>=2):return
    data=available_lane(notes,time,side,lane)
    if data is not None:notes.append({'t':time,'d':data,'l':0})

def arrange(charts,candidates):
    # Existing base timestamps and verse patterns remain intact. The first bar of each
    # drop becomes a player entrance; strong off-beats and measured accents fill out turns.
    for difficulty in ['normal','hard']:
        notes=charts[difficulty]
        for c in candidates:
            s=c['step']
            if not in_drop(s) or c['t']>178600:continue
            phrase=(s-16)//32
            side=1 if phrase%2==0 else 0
            start=next(a for a,b in DROP_STEPS if a<=s<b)
            entrance=s-start<16
            motif=RUNS[((s-start)//32)%len(RUNS)]
            lane=motif[s%8]
            threshold=.75 if difficulty=='normal' else .32
            if (s%2 and c['power']>threshold) or (entrance and s%2==0 and c['power']>.35):
                insert(notes,c,0 if entrance else side,lane)
            if difficulty=='hard' and s%8==0 and c['power']>1.05:
                insert(notes,c,0 if entrance else side,(lane+2)%4,chord=True)
        notes.sort(key=lambda n:(n['t'],n['d']))

    # Erect: staircases and crossovers, with occasional accented doubles.
    # Nightmare: longer player drop phrases, denser off-beats, alternating chord pairs.
    for difficulty in ['erect','nightmare']:
        notes=[]
        for c in candidates:
            s=c['step']; drop=in_drop(s)
            if 76600<c['t']<78000 or c['t']>178600:continue
            phrase=(s-16)//32
            side=1 if phrase%2==0 else 0
            if drop:
                start=next(a for a,b in DROP_STEPS if a<=s<b)
                bar=(s-start)//16
                # The third bar answers VOLT; the fourth pushes directly into the next phrase.
                side=1 if bar%4==1 else 0
                threshold=.29 if difficulty=='erect' else .205
                keep=c['power']>threshold
            else:
                keep=(s%2==0 and c['power']>.23) or (s%2 and c['power']>(.43 if difficulty=='erect' else .31))
            if not keep:continue
            motif=RUNS[((s-16)//32)%len(RUNS)]
            lane=motif[s%8]
            insert(notes,c,side,lane)
            accent=(drop and s%8==0 and c['power']>.75) if difficulty=='erect' else (
                (drop and s%4==0 and c['power']>.43) or (not drop and s%16==0 and c['power']>.9))
            if accent:insert(notes,c,side,(lane+2)%4,chord=True)
        notes.sort(key=lambda n:(n['t'],n['d']))
        charts[difficulty]=notes
    return charts

def chart_stats(notes):
    player=[n for n in notes if n['d']<4]
    groups=Counter(n['t'] for n in player)
    drop_notes=[n for n in player if any(a*1000-40<=n['t']<b*1000+40 for a,b in DROP_TIMES)]
    return {'player_notes':len(player),'opponent_notes':len(notes)-len(player),
            'player_drop_notes':len(drop_notes),'two_note_chords':sum(c==2 for c in groups.values()),
            'holds':sum(n['l']>0 for n in player),
            'peak_player_notes_in_1s':max(sum(n['t']<=x['t']<n['t']+1000 for x in player) for n in player),
            'first_note_ms':notes[0]['t'],'last_note_ms':notes[-1]['t']}

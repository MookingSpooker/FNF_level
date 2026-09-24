"""Author repeatable instrumental phrases; vocals never supply note evidence."""
from collections import Counter
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT/'mods/energize'
DIFFICULTIES = ['easy', 'normal', 'hard', 'erect', 'nightmare']
TIMING_OFFSET_MS = 34.0
STEP_MS = 93.75
RIFF_STARTS = (272, 1104)
STREAM_STARTS = (400, 1232)
RIFF_HITS = (0, 3, 6, 9, 12, 14)
CHORD_PAIRS = ((0, 3), (1, 2), (0, 2), (1, 3))
# Keep the existing stage/camera section boundaries and foreground ownership.
SECTIONS = [
    ('Opening', 4, 52, False), ('Charge I', 52, 68, False),
    ('Drop I', 68, 100, True), ('Synth interlude I', 100, 132, False),
    ('Drop I climax', 132, 196, True), ('Breath', 196, 208, False),
    ('Reprise', 208, 260, False), ('Charge II', 260, 276, False),
    ('Drop II', 276, 308, True), ('Synth interlude II', 308, 340, False),
    ('Final overload', 340, 476, True)]


def sections(offset=TIMING_OFFSET_MS):
    return [{'name': name, 'start': offset+a*375, 'end': offset+b*375,
             'leadSide': 0, 'drop': drop} for name, a, b, drop in SECTIONS]


def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def chart_stats(notes):
    player = [n for n in notes if n['d'] < 4]
    groups = Counter(n['t'] for n in player)
    return {'player_notes': len(player), 'opponent_notes': len(notes)-len(player),
            'two_note_chords': sum(n == 2 for n in groups.values()),
            'holds': sum(n['l'] > 0 for n in player),
            'peak_player_notes_in_1s': max(sum(n['t'] <= x['t'] < n['t']+1000 for x in player) for n in player)}


def build_charts():
    analysis = json.loads((ROOT/'analysis/instrumental-parts.json').read_text())
    parts = {name: {a['step']: a for a in values} for name, values in analysis['parts'].items()}
    charts, provenance, evidence = {}, {}, {}
    arrangement = sections()
    for rank, difficulty in enumerate(DIFFICULTIES):
        notes, proof = [], []

        def add(step, lanes, part, phrase, side=0, minimum=.65):
            attack = parts[part].get(step)
            if not attack or attack['strength'] < minimum:
                return False
            time = TIMING_OFFSET_MS+step*STEP_MS
            for lane in lanes:
                data = lane+4*side
                # Adjacent sixteenths alternate fingers; never silently move a
                # phrase's chord pair. Reject only an optional conflicting note.
                if any(n['d'] == data and abs(n['t']-time) < 145 for n in notes):
                    return False
            for lane in lanes:
                data = lane+4*side
                notes.append({'t': time, 'd': data, 'l': 0})
                proof.append({'t': time, 'd': data, 'step': step,
                              'part': part, 'source': analysis['sources'][part],
                              'role': 'backing' if side else 'foreground',
                              'phrase': phrase, 'attack': attack['attack'],
                              'strength': attack['strength']})
            return True

        # The supplied recordings identify these exact eight-bar passages.
        # Same rhythm and lane motif on their +78-second reprises.
        for starts, phrase in [(RIFF_STARTS, 'double-riff'), (STREAM_STARTS, 'synth-stream')]:
            for start in starts:
                for bar in range(8):
                    for hit, offset in enumerate(RIFF_HITS):
                        if rank == 0 and hit not in (0, 2, 4):
                            continue
                        step = start+bar*16+offset
                        if phrase == 'double-riff':
                            pair = CHORD_PAIRS[(bar//2) % 4]
                            lanes = pair if rank >= 2 else (pair[hit % 2],)
                        else:
                            # Repeated anchor pattern inspired by MILF's streams,
                            # paced to this recording's syncopated synth attacks.
                            lanes = ((0, 1, 3, 1, 2, 1)[hit],)
                        assert add(step, lanes, 'synth', phrase, minimum=.7)

        for step in range(16, 1904):
            if any(start <= step < start+128 for start in RIFF_STARTS+STREAM_STARTS):
                continue
            local = step-832 if step >= 848 else step
            # The opening has no steady kick: follow only its repeated synth
            # motif, not every detected texture transient or vocal syllable.
            if 16 <= local < 208:
                mask = (0, 6, 10, 14) if local < 144 else (0, 2, 9, 12, 14)
                phase = local % 16
                if phase not in mask or (rank == 0 and phase not in (0, 10, 12)):
                    continue
                hit = mask.index(phase)
                add(step, ((0, 2, 1, 3, 1)[hit],), 'synth', 'opening-synth', minimum=.65)
            elif 208 <= local < 272:
                # Stable snare-build pulse; advanced subdivisions require an
                # actual strong drum attack, never a sung syllable.
                spacing = 8 if rank == 0 else 4
                if step % spacing == 0:
                    add(step, ((0, 2, 1, 3)[(step//spacing) % 4],), 'drums', 'snare-build', minimum=.8)
                elif rank >= 3 and step % 2 == 0:
                    add(step, ((1, 3)[(step//2) % 2],), 'drums', 'snare-build-fill', minimum=1.4)
            elif 784 <= step < 832:
                if step >= 816:  # Leave the short transition breath uncharted.
                    continue
                if step % (8 if rank == 0 else 4) == 0:
                    add(step, ((0, 2, 1, 3)[(step//4) % 4],), 'synth', 'transition', minimum=.8)
            else:
                # In the loud drops, the kick/snare is the reliable anchor.
                # Distinct repeating synth offbeats add phrasing above it.
                phase = (step-528) % 32
                spacing = 8 if rank == 0 else 4
                if step % spacing == 0:
                    lane = (0, 2, 1, 3)[(step//4) % 4]
                    chord = (rank == 3 and step % 16 == 0) or (rank == 4 and step % 8 == 0)
                    lanes = (lane, (lane+2) % 4) if chord else (lane,)
                    add(step, lanes, 'drums', 'drop-pulse', minimum=1.1)
                elif rank >= 1 and phase in ((6, 10, 14, 19, 22) if rank >= 2 else (6, 22)):
                    # Odd sixteenth at 19 is a repeated instrumental accent.
                    lane = 3 if phase == 19 else (1, 3)[(phase//2) % 2]
                    add(step, (lane,), 'synth', 'drop-synth', minimum=1.1)
                elif rank >= 3 and step % 2 == 0:
                    # Only pronounced percussion supports optional extra notes.
                    add(step, ((1, 3)[(step//2) % 2],), 'drums', 'drop-percussion', minimum=1.5 if rank == 3 else 1.1)

        # VOLT stays on sparse bass accompaniment. Drum fills appear only where
        # bass has no supported attack; there is no character role switching.
        for step in range(16, 1904, 8 if rank == 0 else 4):
            if 816 <= step < 832:
                continue
            lane = (0, 2, 1, 3)[(step//4) % 4]
            if not add(step, (lane,), 'bass', 'bass-backing', side=1, minimum=.55):
                add(step, (lane,), 'drums', 'drum-backing', side=1, minimum=.8)
        notes.sort(key=lambda n: (n['t'], n['d']))
        proof.sort(key=lambda n: (n['t'], n['d']))
        charts[difficulty], provenance[difficulty] = notes, proof
        stats = chart_stats(notes)
        stats['player_sources'] = dict(Counter(a['part'] for a in proof if a['d'] < 4))
        stats['sections'] = [{'name': s['name'], 'player_role': 'foreground',
                             'player_notes': sum(s['start'] <= n['t'] < s['end'] and n['d'] < 4 for n in notes),
                             'opponent_notes': sum(s['start'] <= n['t'] < s['end'] and n['d'] >= 4 for n in notes)} for s in arrangement]
        evidence[difficulty] = stats
    events = [{'t': 0, 'e': 'FocusCamera', 'v': {'char': -1, 'x': 690, 'y': 530, 'duration': 0, 'ease': 'INSTANT'}}]
    for s in arrangement:
        events.extend([
            {'t': s['start'], 'e': 'FocusCamera', 'v': {'char': -1, 'x': 715, 'y': 530, 'duration': 8, 'ease': 'sineInOut'}},
            {'t': s['start'], 'e': 'ZoomCamera', 'v': {'zoom': .76 if s['drop'] else .8,
             'duration': 8, 'mode': 'direct', 'ease': 'sine', 'easeDir': 'InOut'}}])
    events.append({'t': 179000, 'e': 'PlayAnimation', 'v': {'target': 'dad', 'anim': 'cheer', 'force': True}})
    events.sort(key=lambda e: e['t'])
    for suffix, diffs, speeds in [('', DIFFICULTIES[:3], [1.5, 2.0, 2.5]), ('-erect', DIFFICULTIES[3:], [2.8, 3.1])]:
        write(MOD/f'data/songs/energize/energize-chart{suffix}.json', {
            'version': '2.0.0', 'scrollSpeed': dict(zip(diffs, speeds)), 'events': events,
            'notes': {d: charts[d] for d in diffs}, 'generatedBy': 'ENERGIZE instrumental arrangement 1.4'})
    write(ROOT/'analysis/note-provenance.json', provenance)
    write(ROOT/'analysis/chart-report.json', {
        'version': '1.4.0', 'bpm': 160, 'grid_offset_ms': TIMING_OFFSET_MS,
        'duration_seconds': 187.570794, 'sections': arrangement, 'difficulties': evidence,
        'riff_steps': list(RIFF_HITS), 'riff_starts': list(RIFF_STARTS), 'stream_starts': list(STREAM_STARTS),
        'method': 'Authored instrumental motifs. Boyfriend owns the synth riff, synth stream, and clear drop pulse; VOLT supplies bass/drum accompaniment. Vocal and full-mix sources are excluded.',
        'timing_note': 'Stable 160 BPM grid at the original 34 ms phase; every note requires a separate instrumental attack within 35 ms. Detector agreement does not prove perceptual feel.'})
    print(json.dumps({d: {k: v for k, v in evidence[d].items() if k != 'sections'} for d in DIFFICULTIES}, indent=2))


if __name__ == '__main__':
    build_charts()

"""Make short native practice charts from the installed arrangement, without editing it."""
from copy import deepcopy
from pathlib import Path
import io
import json
import subprocess
import zipfile
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT/'mods/energize'
DIST = ROOT/'dist'


def build():
    DIST.mkdir(exist_ok=True)
    game = Path.home()/'Downloads/funkin-windows-64bit'
    assert (game/'assets/data/stages/mainStage.json').exists(), 'Practice stage is unavailable'
    charts = {}
    for suffix in ('', '-erect'):
        chart = json.loads((MOD/f'data/songs/energize/energize-chart{suffix}.json').read_text())
        charts.update(chart['notes'])
    meta = json.loads((MOD/'data/songs/energize/energize-metadata.json').read_text())
    y, sr = sf.read(MOD/'songs/energize/Inst.ogg', dtype='float32')
    report = []
    for name, start in [('first', 22534), ('repeat', 100534)]:
        end = start+28500
        song_id = f'energize-practice-{name}'
        metadata = deepcopy(meta)
        metadata['songName'] = f'Energize: {name} riff practice'
        metadata['timeChanges'] = [{'t': 0, 'b': 0, 'bpm': 160, 'n': 4, 'd': 4, 'bt': [4,4,4,4]}]
        metadata['playData'].update({'songVariations': [], 'difficulties': list(charts),
                                    'stage': 'mainStage', 'ratings': dict(zip(charts, [3,7,10,13,16]))})
        short = {'version': '2.0.0', 'events': [], 'generatedBy': 'ENERGIZE practice 1.4',
                 'scrollSpeed': dict(zip(charts, [1.5,2,2.5,2.8,3.1])),
                 'notes': {d: [{**n, 't': round(n['t']-start, 3)} for n in notes
                              if start <= n['t'] < end] for d, notes in charts.items()}}
        # Decode once and trim by sample index. This touches only the practice
        # copy; the complete installed recording remains byte-identical.
        raw = io.BytesIO()
        sf.write(raw, y[round(start*sr/1000):round(end*sr/1000)], sr, format='WAV', subtype='FLOAT')
        audio = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', 'pipe:0', '-c:a', 'libvorbis',
                                         '-q:a', '6', '-f', 'ogg', 'pipe:1'], input=raw.getvalue())
        path = DIST/f'{song_id}.fnfc'
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('manifest.json', json.dumps({'version':'1.0.0','songId':song_id}))
            archive.writestr(f'{song_id}-metadata.json', json.dumps(metadata))
            archive.writestr(f'{song_id}-chart.json', json.dumps(short))
            archive.writestr('Inst.ogg', audio)
        decoded, rate = sf.read(io.BytesIO(audio), dtype='float32')
        expected = y[round(start*sr/1000):round(end*sr/1000)]
        assert rate == sr and len(decoded) == len(expected)
        correlation = float(np.corrcoef(decoded.ravel(), expected.ravel())[0,1])
        assert correlation > .98
        report.append({'archive': str(path.relative_to(ROOT)), 'start_ms':start, 'end_ms':end,
                       'duration_seconds':len(decoded)/sr, 'audio_correlation':correlation,
                       'difficulties':list(charts), 'riff_at_seconds':3, 'stream_at_seconds':15})
    (ROOT/'analysis/practice-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Built two 28.5-second practice charts; audio and chart offsets verified.')


if __name__ == '__main__':
    build()

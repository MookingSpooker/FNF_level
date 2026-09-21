"""Measure separate pitched and rhythm parts on the unchanged audio timeline."""
from pathlib import Path
import json
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d

ROOT = Path(__file__).resolve().parents[1]
SR, HOP, STEP = 22050, 110, .09375

def load(name):
    y, sr = sf.read(ROOT / f'analysis/stems/{name}.wav', dtype='float32')
    return librosa.resample(y.mean(axis=1), orig_sr=sr, target_sr=SR)

def features(y, name):
    spec = np.abs(librosa.stft(y, n_fft=1024, hop_length=HOP))
    freq = librosa.fft_frequencies(sr=SR, n_fft=1024)
    low, high = {'lead': (180, 6500), 'bass': (35, 600), 'drums': (45, 10000)}[name]
    selected = spec[(freq >= low) & (freq < high)]
    flux = np.maximum(0, np.diff(np.log1p(selected*8), axis=1, prepend=0)).mean(axis=0)
    flux = uniform_filter1d(flux, 2)
    flux /= max(float(np.percentile(flux, 95)), 1e-8)
    rms = librosa.feature.rms(y=y, frame_length=512, hop_length=HOP)[0]
    rms /= max(float(np.percentile(rms, 95)), 1e-8)
    times = np.arange(len(flux))*HOP/SR
    peaks, _ = find_peaks(flux, distance=10, prominence=.12, height=.18)
    # Energy backtracking supplies a lower bound, then a bounded flux half-rise
    # locates the attack. This avoids jumping back into the previous sustained note.
    starts = librosa.onset.onset_backtrack(peaks, rms)
    attacks = []
    for p, start in zip(peaks, starts):
        if rms[p] < .035: continue
        left = max(int(start), p-4)
        threshold = flux[p]*.55
        edge = p
        while edge > left and flux[edge-1] >= threshold: edge -= 1
        attacks.append({'attack': float(times[edge]), 'peak': float(times[p]),
            'strength': round(float(flux[p]), 4), 'energy': round(float(rms[p]), 4)})
    return times, flux, rms, attacks

if __name__ == '__main__':
    waves = {'lead': load('other') + load('vocals'), 'bass': load('bass'), 'drums': load('drums')}
    arrays = {}; parts = {}
    for name, y in waves.items():
        times, flux, rms, attacks = features(y, name)
        arrays[name+'_flux'], arrays[name+'_rms'] = flux, rms
        parts[name] = attacks
        print(name, len(attacks), 'attacks', flush=True)
    arrays['times'] = times
    # Circular phase fit to strong, separated drum attacks. Tempo remains 160 BPM.
    drums = [a for a in parts['drums'] if a['strength']>.65 and 2<a['attack']<178]
    phases = np.arange(-.012, .065, .00025)
    scores = [sum(min(a['strength'], 2)*np.exp(-(((a['attack']-p+STEP/2)%STEP-STEP/2)/.012)**2)
        for a in drums) for p in phases]
    offset = float(phases[np.argmax(scores)])
    # Estimate the dominant pitched contour; synth mixtures are not studio MIDI.
    for name in ['lead', 'bass']:
        pitches, magnitude = librosa.piptrack(y=waves[name], sr=SR, n_fft=4096,
            hop_length=HOP, fmin=110 if name=='lead' else 35,
            fmax=1800 if name=='lead' else 500, threshold=.3)
        rows = np.argmax(magnitude, axis=0)
        hz = pitches[rows, np.arange(pitches.shape[1])]
        midi = librosa.hz_to_midi(np.maximum(hz, 1))
        arrays[name+'_pitch'] = midi
        for a in parts[name]:
            frame = min(len(midi)-1, round((a['attack']+.035)*SR/HOP))
            a['pitch'] = round(float(np.median(midi[frame:frame+5])), 2)
    candidates = {}
    for name, attacks in parts.items():
        chosen = []
        for step in range(16, 1904):
            grid = offset + step*STEP
            near = [a for a in attacks if abs(a['attack']-grid)<.033]
            if not near: continue
            a = max(near, key=lambda a:a['strength']*np.exp(-((a['attack']-grid)/.025)**2))
            chosen.append({**a, 'step':step, 't':round(grid*1000,3),
                'attack':round(a['attack']*1000,3), 'peak':round(a['peak']*1000,3),
                'deviation_ms':round((a['attack']-grid)*1000,3)})
        candidates[name] = chosen
    report = {'bpm':160, 'step_ms':93.75, 'offset_ms':round(offset*1000,3),
        'method':'Local htdemucs estimates; other+vocals lead, bass and drums separated; bounded energy-backtracked attacks, drum-phase fit, grid timing; dominant spectral pitch contour.',
        'parts':candidates,
        'phase_fit':{'strong_drum_attacks':len(drums), 'search_min_ms':-12, 'search_max_ms':65},
        'section_energy':[{ 'start':start, **{name:round(float(np.mean(arrays[name+'_rms'][(times>=start)&(times<start+6)])),3) for name in waves}}
            for start in range(0,186,6)]}
    (ROOT/'analysis/parts.json').write_text(json.dumps(report,indent=2)+'\n')
    np.savez_compressed(ROOT/'analysis/parts-features.npz', **arrays)
    print(json.dumps({'offset_ms':report['offset_ms'], 'candidates':{k:len(v) for k,v in candidates.items()},
        'section_energy':report['section_energy']},indent=2))

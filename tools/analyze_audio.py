"""Analyze the exact decoded game audio; requires NumPy, FFmpeg and Python."""
from pathlib import Path
import json
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
with wave.open(str(ROOT / 'analysis/energize.wav'), 'rb') as f:
    sr = f.getframerate()
    y = np.frombuffer(f.readframes(f.getnframes()), dtype='<i2').astype(np.float64) / 32768
hop, nfft = 128, 1024
frames = np.lib.stride_tricks.sliding_window_view(y, nfft)[::hop]
spec = np.abs(np.fft.rfft(frames * np.hanning(nfft), axis=1))
freq = np.fft.rfftfreq(nfft, 1 / sr)
times = (np.arange(len(frames)) * hop + nfft / 2) / sr
logspec = np.log1p(spec * 5)
flux = np.maximum(0, np.diff(logspec, axis=0, prepend=logspec[:1]))
bands = np.array([flux[:, (freq >= lo) & (freq < hi)].mean(axis=1)
                  for lo, hi in [(40,180),(180,900),(900,3500),(3500,10000)]])
bands /= np.percentile(bands, 95, axis=1)[:, None] + 1e-8
onset = bands[0]*0.32 + bands[1]*0.28 + bands[2]*0.25 + bands[3]*0.15
onset = np.maximum(0, onset - np.convolve(onset, np.ones(51)/51, mode='same')*0.7)
dt = hop/sr
ac = np.fft.irfft(abs(np.fft.rfft(onset-onset.mean(), n=2**16))**2)[:500]
candidates = [(60/(i*dt), float(ac[i])) for i in range(45,240)
              if ac[i]>ac[i-1] and ac[i]>ac[i+1] and 65<60/(i*dt)<225]
candidates.sort(key=lambda x:-x[1])
peaks = np.where((onset[1:-1]>onset[:-2]) & (onset[1:-1]>=onset[2:]) & (onset[1:-1]>0.18))[0]+1
selected=[]
for p in sorted(peaks, key=lambda p:-onset[p]):
    if all(abs(p-q)*dt>0.065 for q in selected): selected.append(int(p))
selected.sort()
# Estimate stable quarter-note tempo by coherence of strong transients over the full track.
pt=times[selected]
pw=onset[selected]
mask=(pt>3)&(pt<len(y)/sr-4)
coherence=[]
for bpm in np.arange(65,220,0.02):
    z=np.sum(pw[mask]*np.exp(2j*np.pi*pt[mask]*bpm/60))
    coherence.append((float(abs(z)/pw[mask].sum()),float(bpm),float(np.angle(z)*60/(2*np.pi*bpm))))
coherence.sort(reverse=True)
summary={'duration':len(y)/sr,'sample_rate':sr,'hop_seconds':dt,
         'autocorrelation_tempos':candidates[:12], 'coherent_tempos':coherence[:15],
         'onsets':[{'t':round(float(times[p]),6),'strength':round(float(onset[p]),4),
                    'bands':[round(float(b),4) for b in bands[:,p]]} for p in selected]}
(ROOT/'analysis/audio-analysis.json').write_text(json.dumps(summary,indent=2))
np.savez_compressed(ROOT/'analysis/features.npz',times=times,onset=onset,bands=bands,
                    rms=np.sqrt((frames**2).mean(axis=1)),freq=freq,spec=spec.astype('float32'))
print(json.dumps({k:v for k,v in summary.items() if k!='onsets'},indent=2))
print('Onsets:',len(selected))

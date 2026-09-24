"""Extract chart evidence from instrumental stems only; never merge vocals into synth."""
from pathlib import Path
import json
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import find_peaks

ROOT=Path(__file__).resolve().parents[1]
SR,HOP=22050,110

def analyze():
    arrays={};parts={}
    for part,filename in [('synth','other'),('bass','bass'),('drums','drums')]:
        wav,sr=sf.read(ROOT/f'analysis/stems/{filename}.wav',dtype='float32')
        y=librosa.resample(wav.mean(axis=1),orig_sr=sr,target_sr=SR)
        spec=np.abs(librosa.stft(y,n_fft=1024,hop_length=HOP))
        freq=librosa.fft_frequencies(sr=SR,n_fft=1024)
        lo,hi={'synth':(110,6500),'bass':(35,700),'drums':(45,10000)}[part]
        selected=spec[(freq>=lo)&(freq<hi)]
        flux=np.maximum(0,np.diff(np.log1p(selected*8),axis=1,prepend=0)).mean(axis=0)
        flux/=max(float(np.percentile(flux,95)),1e-8)
        rms=librosa.feature.rms(y=y,frame_length=512,hop_length=HOP)[0]
        rms/=max(float(np.percentile(rms,95)),1e-8)
        times=np.arange(len(flux))*HOP/SR
        peaks,_=find_peaks(flux,distance=10,prominence=.18,height=.3)
        candidates=[]
        for step in range(16,1904):
            grid=(34+step*93.75)/1000
            near=peaks[abs(times[peaks]-grid)<.035]
            if not len(near):continue
            p=max(near,key=lambda p:flux[p]*np.exp(-((times[p]-grid)/.025)**2))
            # The rise in a centered spectral window is measured directly. Keep
            # its peak time; do not use energy minima from an earlier pad note.
            if max(rms[p:min(p+8,len(rms))])<.1:continue
            candidates.append({'step':step,'attack':round(float(times[p])*1000,3),
                'strength':round(float(flux[p]),4),'energy':round(float(max(rms[p:p+8])),4),
                'grid_delta_ms':round(float(times[p])*1000-grid*1000,3)})
        arrays[part+'_flux']=flux;arrays[part+'_rms']=rms
        parts[part]=candidates
        print(part,len(candidates),flush=True)
    arrays['times']=times
    result={'bpm':160,'offset_ms':34,'step_ms':93.75,
        'sources':{'synth':'other.wav','bass':'bass.wav','drums':'drums.wav'},
        'excluded_note_sources':['vocals.wav','full_mix','other+vocals'],
        'parts':parts,'note':'Demucs estimates may contain leakage. No vocal or full-mix signal is positive note evidence.'}
    (ROOT/'analysis/instrumental-parts.json').write_text(json.dumps(result,indent=2)+'\n')
    np.savez_compressed(ROOT/'analysis/instrumental-features.npz',**arrays)
    return result

if __name__ == '__main__':
    analyze()

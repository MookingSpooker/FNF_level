"""Estimate musical stems locally; the unaltered recording remains the game audio."""
from pathlib import Path
import json
import subprocess
import numpy as np
import soundfile as sf
import torch
from demucs.pretrained import get_model
from demucs.apply import apply_model

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/stems'

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    torch.hub.set_dir(str(ROOT / 'analysis/model-cache'))
    torch.set_num_threads(6)
    torch.manual_seed(160)
    model = get_model('htdemucs').cpu().eval()
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i',
        str(ROOT / 'mods/energize/songs/energize/Inst.ogg'), '-f', 'f32le',
        '-ac', '2', '-ar', str(model.samplerate), '-'])
    wav = torch.from_numpy(np.frombuffer(raw, dtype='<f4').copy().reshape(-1, 2).T)
    ref = wav.mean(0)
    mean, std = ref.mean(), ref.std()
    with torch.no_grad():
        stems = apply_model(model, ((wav-mean)/std)[None], device='cpu',
            shifts=0, overlap=.25, progress=True, num_workers=0)[0] * std + mean
    for name, values in zip(model.sources, stems):
        sf.write(OUT / f'{name}.wav', values.numpy().T, model.samplerate, subtype='FLOAT')
    report = {'model': 'htdemucs', 'sources': model.sources,
        'sample_rate': model.samplerate, 'samples': wav.shape[-1],
        'duration_seconds': wav.shape[-1]/model.samplerate,
        'note': 'Estimated stems for analysis only. No trimming, stem normalization or game-audio replacement.'}
    (ROOT/'analysis/separation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

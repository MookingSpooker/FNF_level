# ENERGIZE: VS VOLT

A native Friday Night Funkin' **0.8.4** level using the supplied **Energize — Tonytonychopper999** recording.

## Play

The mod is installed in `C:\Users\Leane\Downloads\funkin-windows-64bit\mods\energize`.

1. Open **Launch ENERGIZE.cmd**, or start your existing **Funkin.exe**.
2. Choose **Freeplay → Energize**. It is also available at the bottom of Story Mode as **ENERGIZE: VS VOLT**.
3. Choose **Easy**, **Normal**, or **Hard**. Use your existing arrow/key bindings.

VOLT is a CRT-headed electric street DJ with six illustrated poses and beat-driven animation. The Dynamo is an original neon rooftop reactor stage. Boyfriend, Girlfriend, notes, scoring, health, controls, and game-over mechanics use the original engine.

| Difficulty | Player notes | Peak notes/second | Scroll speed |
| --- | ---: | ---: | ---: |
| Easy | 215 | 3 | 1.5 |
| Normal | 391 | 6 | 2.0 |
| Hard | 494 | 9 | 2.5 |

## Song and chart

The complete supplied MP3 is converted to Ogg Vorbis without trimming, stretching, normalization, or tempo changes. Length: **187.5708 seconds**. Its measured pulse is **160 BPM**. The chart follows detected attacks near eighth- and sixteenth-note subdivisions, with repeating lane motifs and alternating eight-beat turns. The intro, breakdown, and reverb tail leave breathing room. No random notes, traps, or extra mechanics are added.

The supplied recording is a full mix. It plays as `Inst.ogg`; no invented or duplicated vocal stems are included. Missing notes still affects health and score, but cannot mute individual voices within the supplied mix.

The user played the native level and reported **“Timing feels good.”** Hard difficulty completed the full song and reached the native results screen. Automated checks passed for all three charts: audio identity, chart bounds, lane spacing, asset references, atlas rectangles, and sustain collisions. See `analysis/validation.json`, `analysis/chart-report.json`, and `analysis/native-playtest.json`. The sub-millisecond rounding statistic in the validator checks serialized timestamps only; it is not a claim of perceptual timing precision.

## Install elsewhere

Copy the **energize** folder from `mods` into the game's **mods** folder, then restart FNF. It must contain `_polymod_meta.json` directly inside `mods/energize`.

Alternatively, from PowerShell:

```powershell
.\tools\Install-Mod.ps1 -GamePath 'C:\path\to\funkin-windows-64bit'
```

The installer checks for unrelated folders and backs up an existing version of this mod in this project's `backups` directory. It never edits base-game assets. Remove only `mods/energize` to uninstall.

## Edit or rebuild

- `mods/energize/`: complete installable mod.
- `dist/energize-mod.zip`: packaged mod folder.
- `dist/energize.fnfc`: editable chart archive; drag it onto FNF to open the Chart Editor. Keep the mod installed for the custom character and stage.
- `art/`: original generated PNGs, plus prompts and asset notes.
- `tools/analyze_audio.py`: spectral-flux timing analysis of the decoded game audio.
- `tools/build_mod.py`: reproducible charts, JSON, atlas metadata, and UI icons.
- `tools/validate_mod.py`: structural and audio verification.
- `research/MODDING.md`: official references and compatibility decisions.

The development scripts require Python 3, NumPy, Pillow, and FFmpeg on PATH. They are not required to play. To rebuild analysis, decode the exact game audio first:

```powershell
ffmpeg -i .\mods\energize\songs\energize\Inst.ogg -ac 1 -ar 22050 -c:a pcm_s16le .\analysis\energize.wav
python .\tools\analyze_audio.py
python .\tools\build_mod.py
python .\tools\validate_mod.py
python .\tools\package_mod.py
```

No engine compilation, replacement executable, Python runtime, or extra mod engine is needed for players. Read the music and asset credits before sharing the package.

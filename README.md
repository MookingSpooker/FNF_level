# ENERGIZE: VS VOLT — 1.4

A native Friday Night Funkin’ **0.8.4** level using the supplied **Energize — Tonytonychopper999** recording.

## Play

The mod is installed in `C:\Users\Leane\Downloads\funkin-windows-64bit\mods\energize`.
Open **Launch ENERGIZE.cmd**, choose **Freeplay → Energize**, and select Easy, Normal, Hard, Erect, or Nightmare.
Your normal controls, health, scoring, and game-over mechanics apply. The mod never enables bot play.

## Instrumental chart revision

Boyfriend follows instrumental synth motifs and the clear drum pulse. VOLT supplies lighter bass/drum accompaniment. Vocal and full-mix attack detectors no longer provide any notes. The supplied recording still plays intact, including its vocals; this changes what is charted, not the music.

- **25.534–37.534 seconds:** the six-hit synth riff uses simultaneous pairs on Hard, Erect, and Nightmare. Four spaced hits lead into two quicker hits. Pairs change every two bars: left+right, down+up, left+up, then down+right.
- **37.534–49.534 seconds:** Boyfriend plays a continuous, repeating synth stream with a recurring down-arrow anchor. It follows this song’s syncopation rather than borrowing MILF’s timestamps.
- The same patterns return at **103.534–115.534** and **115.534–127.534 seconds**.
- Easy uses fewer attacks. Normal keeps single notes. Advanced charts retain every Hard note and add supported drum fills and accents elsewhere.

The opening uses repeating synth phrases. Snare builds use a steady percussion pulse. Loud drops use the kick/snare as their anchor with distinct synth offbeats. Quiet texture attacks are not automatically converted into filler notes. This revision intentionally has fewer notes than 1.3.

| Difficulty | Player notes | Doubles | Scroll speed |
| --- | ---: | ---: | ---: |
| Easy | 263 | 0 | 1.5 |
| Normal | 582 | 0 | 2 |
| Hard | 751 | 96 | 2.5 |
| Erect | 832 | 145 | 2.8 |
| Nightmare | 889 | 195 | 3.1 |

Timing uses **160 BPM** and the original **34 ms** grid reference. Each note requires an instrumental attack within 35 ms; repeating phrases keep consistent spacing instead of following detector jitter. Separated stems are estimates and can contain leakage. These checks do not replace human listening and playtesting.

## Short practice runs

Open **Practice ENERGIZE riff.cmd** or **Practice ENERGIZE repeat.cmd**. Choose a difficulty, then **Playtest Song**. Each run is 28.5 seconds long: the doubles start at 3 seconds and the synth stream at 15 seconds. Practice uses the standard stage and the same shifted chart notes, making it easy to review the rhythm without replaying the opening. These clips do not alter the installed song or its full recording.

## Stage and characters

The Dynamo retains its reactor rings, beams, lightning, sparks, equalizer, floor rings, reactive character halos, and camera changes. Effects remain behind the characters and native interface. The game’s **Flashing Lights** preference reduces brightness and disables lightning and sharp pulses.

The full **187.5708-second** recording, original artwork, character definitions, stage geometry, and stage script remain unchanged. Missing notes affects health and score but cannot mute individual instruments inside the supplied full mix.

## Verification

All five charts pass checks for audio identity, asset references, spacing, collisions, instrumental provenance, riff doubles, repeated motifs, and difficulty progression. Erect and Nightmare preserve the complete Hard core. See `analysis/validation.json`, `analysis/chart-report.json`, `analysis/v14-clip-alignment.json`, and `analysis/practice-validation.json`. Native integration observations are recorded separately in `analysis/native-playtest-v14.json`. Bot play verifies loading and rendering, not subjective timing feel.

## Install and rebuild

Copy `mods/energize` into an FNF 0.8.4 installation’s `mods` folder, or run:

```powershell
.\tools\Install-Mod.ps1 -GamePath 'C:\path\to\funkin-windows-64bit'
```

The installer backs up the existing ENERGIZE mod under `backups`. `dist/energize-mod.zip` contains the complete mod; `dist/energize.fnfc` is its editable native chart archive.

Development uses Python 3.12, FFmpeg, and `tools/requirements-audio.txt`. The existing `.audio-venv` contains the required packages. The chart builder needs `analysis/instrumental-parts.json`; audio analysis needs the locally estimated stems. Legacy `analyze_parts.py` still produces visual envelopes only, so its combined lead signal cannot supply chart notes.

```powershell
.\.audio-venv\Scripts\python.exe tools\separate_audio.py
.\.audio-venv\Scripts\python.exe tools\analyze_parts.py
.\.audio-venv\Scripts\python.exe tools\analyze_instrumental.py
.\.audio-venv\Scripts\python.exe tools\build_mod.py
.\.audio-venv\Scripts\python.exe tools\validate_mod.py
.\.audio-venv\Scripts\python.exe tools\package_mod.py
.\.audio-venv\Scripts\python.exe tools\package_practice.py
```

See `research/MODDING.md` for references and implementation decisions. Read the music and asset credits before sharing.

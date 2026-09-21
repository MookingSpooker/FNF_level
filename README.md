# ENERGIZE: VS VOLT — 1.2

A native Friday Night Funkin’ **0.8.4** level using the supplied **Energize — Tonytonychopper999** recording.

## Play

The updated mod is installed in `C:\Users\Leane\Downloads\funkin-windows-64bit\mods\energize`.

1. Open **Launch ENERGIZE.cmd**, or start **Funkin.exe**.
2. Choose **Freeplay → Energize**. Story Mode also contains **ENERGIZE: VS VOLT**.
3. Select **Easy, Normal, Hard, Erect, or Nightmare** using the difficulty controls.

Your normal controls, health, scoring, holds, and game-over mechanics apply. The shipped mod never enables bot play.

## The musical duet

Boyfriend carries the lead during drops. VOLT carries the easier lead and quieter synth interludes while you play bass and drum accents. During your lead, VOLT supplies the backing part. Roles change at musical section boundaries, with a sustained player lead through the final overload; there is no repeating three-second handoff.

The chart uses separate estimates of lead, bass, and drums, created locally from the supplied recording with Demucs. Dominant pitch movement guides arrow direction. Strong simultaneous lead and drum attacks produce measured doubles on the harder charts. Holds require a stable pitched tail and enough space before the next note.

| Difficulty | Player notes | Peak notes in one second | Holds | Doubles | Scroll speed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Easy | 276 | 3 | 29 | 0 | 1.5 |
| Normal | 578 | 6 | 33 | 0 | 2.1 |
| Hard | 810 | 10 | 26 | 43 | 2.6 |
| Erect | 1,049 | 13 | 19 | 70 | 2.9 |
| Nightmare | 1,416 | 14 | 11 | 139 | 3.2 |

The tempo remains **160 BPM**. The new grid phase is **36.25 ms**, measured from separated drum attacks. Notes follow that stable grid instead of inheriting fluctuating peaks from the full mix. Estimated attacks must fall within 33 ms of their chart timestamps. This is audio-assisted arrangement, not studio MIDI or a claim of perfect transcription. Hardware latency still uses the game’s normal calibration.

The complete **187.5708-second** recording remains unchanged from the previous mod audio: no trimming, stretching, or replacement music. Estimated stems are development inputs only and are not included in the playable mod. Missing notes affects health and score but cannot mute individual instruments inside the supplied full mix.

## Stage and characters

VOLT’s CRT poses and Boyfriend’s original animations now have direction-sensitive hit reactions and separate reactive halos. The Dynamo adds rotating reactor segments, expanding rings, sweeping beams, lightning, sparks, an equalizer, floor rings, and section-based camera moves. Bass, lead, and drum envelopes drive different effects. The song clock controls motion so pause and retry cannot accumulate drift.

Effects remain behind the characters and the native note interface. The game’s **Flashing Lights** preference dims the effects and disables lightning and sharp beat pulses when turned off.

## Verification

All five charts pass audio identity, asset, timing-evidence, difficulty progression, note spacing, sustain collision, and musical-role checks. Every section gives both characters a part. Every drop assigns its lead to the player. See `analysis/validation.json`, `analysis/chart-report.json`, and `analysis/note-provenance.json`.

Native playtest details are recorded separately in `analysis/native-playtest-v12.json`. Bot play is used only for developer testing. The user’s earlier “Timing feels good” feedback applies to version 1.0, not this rebuilt arrangement.

## Install or edit

Copy the **energize** folder from `mods` into another FNF 0.8.4 installation’s **mods** folder and restart. `_polymod_meta.json` must sit directly inside `mods/energize`.

```powershell
.\tools\Install-Mod.ps1 -GamePath 'C:\path\to\funkin-windows-64bit'
```

The installer backs up an existing ENERGIZE mod under `backups` and preserves base-game assets.

- `dist/energize-mod.zip`: complete playable mod.
- `dist/energize.fnfc`: editable native chart archive. Keep the mod installed for VOLT and the stage.
- `tools/separate_audio.py`: local four-stem estimation.
- `tools/analyze_parts.py`: distinct attack streams and pitch estimates.
- `tools/musical_chart.py`: authored section roles, difficulty patterns, and note provenance.
- `tools/build_effects.py`: procedural effect geometry and separate audio envelopes.
- `tools/build_mod.py`: rebuilds the mod’s data and artwork metadata.
- `tools/validate_mod.py`: chart, asset, and audio checks.
- `research/MODDING.md`: primary references and implementation decisions.

## Rebuild

Development requires Python 3.12, FFmpeg on PATH, and the packages in `tools/requirements-audio.txt`. The isolated `.audio-venv` is already installed on this machine. Model downloads and estimated WAV stems stay under ignored `analysis` folders. Players do not need these tools.

```powershell
.\.audio-venv\Scripts\python.exe tools\separate_audio.py
.\.audio-venv\Scripts\python.exe tools\analyze_parts.py
.\.audio-venv\Scripts\python.exe tools\build_mod.py
.\.audio-venv\Scripts\python.exe tools\validate_mod.py
.\.audio-venv\Scripts\python.exe tools\package_mod.py
```

The original artwork and prompts remain in `art`. Read the music and asset credits before sharing the package.

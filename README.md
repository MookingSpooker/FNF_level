# ENERGIZE: VS VOLT — 1.3

A native Friday Night Funkin’ **0.8.4** level using the supplied **Energize — Tonytonychopper999** recording.

## Play

The updated mod is installed in `C:\Users\Leane\Downloads\funkin-windows-64bit\mods\energize`.

1. Open **Launch ENERGIZE.cmd**, or start **Funkin.exe**.
2. Choose **Freeplay → Energize**. Story Mode also contains **ENERGIZE: VS VOLT**.
3. Select **Easy, Normal, Hard, Erect, or Nightmare** using the difficulty controls.

Your normal controls, health, scoring, holds, and game-over mechanics apply. The shipped mod never enables bot play.

## The musical duet

Boyfriend now plays the prominent rhythm throughout the song, including the opening and quieter interludes. VOLT plays a separate, lighter bass/drum accompaniment. The lead no longer changes character at section boundaries.

Version 1.3 uses the original version you preferred as its reference. Every original foreground timestamp from both characters is retained on Boyfriend. Hard keeps the complete original Hard rhythm; Erect and Nightmare preserve that core and add mix-audible attacks and shared drum accents. This avoids treating a separated file labelled “lead” as automatically being the tune you would hum.

| Difficulty | Player notes | Peak notes in one second | Doubles | Scroll speed |
| --- | ---: | ---: | ---: | ---: |
| Easy | 432 | 3 | 0 | 1.5 |
| Normal | 796 | 6 | 0 | 2.0 |
| Hard | 1,004 | 9 | 0 | 2.5 |
| Erect | 1,114 | 11 | 44 | 2.8 |
| Nightmare | 1,308 | 13 | 111 | 3.1 |

Because Boyfriend now keeps the main rhythm, there are more continuous player phrases than in the original call-and-response chart. Original Easy and Normal holds are retained. Hard has the original tap patterns; advanced difficulty comes from extra supported attacks and measured two-key accents.

The tempo remains **160 BPM**, with the original **34 ms** grid reference. Actual notes retain the original acoustic attack timestamps rather than being forced onto the grid. No new global audio offset is applied. Hardware latency still uses the game’s normal calibration.

The complete **187.5708-second** recording is unchanged: no trimming, stretching, or replacement music. Estimated stems are used for VOLT’s accompaniment and the visual envelopes only. Missing notes affects health and score but cannot mute individual instruments inside the supplied full mix.

## Stage and characters

VOLT’s CRT poses and Boyfriend’s original animations now have direction-sensitive hit reactions and separate reactive halos. The Dynamo adds rotating reactor segments, expanding rings, sweeping beams, lightning, sparks, an equalizer, floor rings, and section-based camera moves. Bass, lead, and drum envelopes drive different effects. The song clock controls motion so pause and retry cannot accumulate drift.

Effects remain behind the characters and the native note interface. The game’s **Flashing Lights** preference dims the effects and disables lightning and sharp beat pulses when turned off.

## Verification

All five charts pass audio identity, asset, note spacing, sustain collision, and difficulty progression checks. Regression checks confirm that every original foreground attack and hold stays on Boyfriend at its exact timestamp. Erect and Nightmare retain the complete Hard core pattern. Original music, art, character definitions, stage geometry, and stage script are unchanged.

See `analysis/validation.json`, `analysis/v13-regression.json`, and `analysis/chart-report.json`. `analysis/v13-diagnosis.json` records the previous mismatch: on Hard, 127 stronger original attacks appeared only on VOLT while 84 player notes fell below the original mix-strength floor.

Native test observations are recorded in `analysis/native-playtest-v13.json`. Bot play verifies integration, not whether the rhythm feels natural to a human. The earlier “Timing feels good” feedback belongs to the original chart; version 1.3 still needs your subjective playtest.

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
- `tools/musical_chart.py`: original rhythm preservation, accompaniment, advanced accents, and note provenance.
- `tools/build_effects.py`: procedural effect geometry and separate audio envelopes.
- `tools/build_mod.py`: rebuilds the mod’s data and artwork metadata.
- `tools/validate_mod.py`: chart, asset, and audio checks.
- `research/MODDING.md`: primary references and implementation decisions.

## Rebuild

Development requires Python 3.12, FFmpeg on PATH, and the packages in `tools/requirements-audio.txt`. The isolated `.audio-venv` is already installed on this machine. The full-mix features in `analysis/features.npz` and original chart snapshot in `analysis/reference-v1-chart.json` are also required. Model downloads and estimated WAV stems stay under ignored `analysis` folders. Players do not need these tools.

```powershell
ffmpeg -y -i mods/energize/songs/energize/Inst.ogg -ac 1 -ar 22050 -c:a pcm_s16le analysis/energize.wav
.\.audio-venv\Scripts\python.exe tools\analyze_audio.py
.\.audio-venv\Scripts\python.exe tools\separate_audio.py
.\.audio-venv\Scripts\python.exe tools\analyze_parts.py
.\.audio-venv\Scripts\python.exe tools\build_mod.py
.\.audio-venv\Scripts\python.exe tools\validate_mod.py
.\.audio-venv\Scripts\python.exe tools\package_mod.py
```

The original artwork and prompts remain in `art`. Read the music and asset credits before sharing the package.

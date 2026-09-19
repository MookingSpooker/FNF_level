# Research and implementation notes

## Engine identification

The user's supplied `CHANGELOG.md` and the running game identify version **0.8.4**. This is the official V-Slice engine with Polymod support. Psych Engine Lua or legacy section-based charts would not be suitable here.

## Primary references

- [Official modding documentation](https://funkincrew.github.io/funkin-modding-docs/)
- [Song installation and folder layout](https://funkincrew.github.io/funkin-modding-docs/02-custom-songs-and-custom-levels/02-02-adding-the-custom-song.html)
- [Registering a custom level in Story Mode and Freeplay](https://funkincrew.github.io/funkin-modding-docs/02-custom-songs-and-custom-levels/02-03-adding-a-custom-level.html)
- [Character definitions and Sparrow atlases](https://funkincrew.github.io/funkin-modding-docs/03-custom-characters/03-02-creating-a-character.html)
- [Stage definitions and character anchors](https://funkincrew.github.io/funkin-modding-docs/04-custom-stages/04-01-creating-a-stage.html)
- [Version-pinned song schema](https://github.com/FunkinCrew/Funkin/blob/v0.8.4/source/funkin/data/song/SongData.hx)
- [Version-pinned mod API compatibility](https://github.com/FunkinCrew/Funkin/blob/v0.8.4/source/funkin/modding/PolymodHandler.hx)
- [Version-pinned health icon implementation](https://github.com/FunkinCrew/Funkin/blob/v0.8.4/source/funkin/play/components/HealthIcon.hx)
- [Version-pinned Freeplay icon implementation](https://github.com/FunkinCrew/Funkin/blob/v0.8.4/source/funkin/ui/PixelatedIcon.hx)
- [Version-pinned editable archive manifest](https://github.com/FunkinCrew/Funkin/blob/v0.8.4/source/funkin/data/song/importer/ChartManifestData.hx)

## Decisions

- Add a self-contained mod with unique `energize`, `volt`, and `dynamo` IDs.
- Use metadata schema 2.2.4, chart schema 2.0.0, character schema 1.0.0 and stage schema 1.0.1, verified against native data and source.
- Native chart lanes **0–3 are the player's notes**, and **4–7 are the opponent's notes**. Timestamps and hold lengths are milliseconds.
- Register a Story Mode level so the song also appears in Freeplay.
- Explicitly set both vocal lists to empty. The provided full mix is the instrumental playback track; duplicate vocal copies would double the volume.
- Keep image PNGs unchanged and define the six poses and subtle movement through Sparrow XML frame rectangles and offsets. The atlas contains 36 references to six illustrated poses, not 36 separately drawn images.
- Preserve the original mechanics using data only: no gameplay scripts, note penalties, new input rules, or engine patches.

## Timing evidence

The audio was decoded from the actual shipped OGG at 22,050 Hz. Analysis uses a 1,024-sample Hann window with a 128-sample hop and positive log-spectral differences across four frequency bands. The strong eighth-note periodicity at 320 pulses/minute supports a 160 BPM chart. Broader harmonic estimates initially suggested other tempi; section-level analysis resolved these as syncopation rather than a tempo change.

Candidate attacks must fall within 36 ms of the sixteenth-note grid. The chosen timestamp receives a 6 ms correction for the spectral window's leading-edge delay. Difficulty-specific density limits and repeating authored direction motifs produce readable patterns. The player's actual playtest confirmed that timing feels good.

This is audio-assisted charting, not a transcription from MIDI or isolated stems. Hardware latency can still be adjusted using the game's normal timing settings.

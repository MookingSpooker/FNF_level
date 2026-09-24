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
- Preserve the original mechanics. The stage HScript changes visual props and character angles only; it adds no input rules, scoring changes, or engine patches.

## Musical arrangement and timing (1.2)

Research informed a separation-first approach: estimate drums, bass, other instruments, and vocals locally; combine the latter two into a lead-oriented signal. These are imperfect model estimates, not original studio stems. The exact existing `Inst.ogg` remains the playback source.

- [Demucs, official repository and inference instructions](https://github.com/facebookresearch/demucs)
- [librosa: onset backtracking to energy minima](https://librosa.org/doc/0.11.0/generated/librosa.onset.onset_backtrack.html)
- [librosa: spectral pitch tracking](https://librosa.org/doc/0.11.0/generated/librosa.piptrack.html)
- [librosa: harmonic/percussive separation concepts](https://librosa.org/doc/main/auto_tutorials/03-advanced/plot_hprss.html)

`htdemucs` runs locally with zero random shifts and 25% overlap. Stems preserve the decoded recording’s sample count and timeline. No song upload is involved. A 1,024-sample centered STFT with 110-sample hops at 22,050 Hz measures separate attacks. Backtracking is bounded to four frames, then refined by the flux half-rise so a sustained pad cannot push a timestamp into the previous note. A circular fit to strong drum attacks establishes a 36.25 ms phase at 160 BPM. Chart timestamps use the stable sixteenth grid; an estimated attack must lie within 33 ms. These numerical bounds measure detector agreement, not human perception.

The old full-mix attack stream and fixed eight-beat turn switching are no longer used. Authored sections keep the player on lead in drops and VOLT on lead in simpler passages. The other character plays independently selected bass and drum accents. Four pitch registers guide lead direction; fast repeated pitches alternate fingers. Doubles require a simultaneous lead and drum accent. The source of every note is recorded in `analysis/note-provenance.json`.

## Difficulties and reactive visuals

- [Official variation documentation](https://funkincrew.github.io/funkin-modding-docs/02-custom-songs-and-custom-levels/02-04-what-are-variations.html)
- [Version-pinned instrumental selection](https://github.com/FunkinCrew/Funkin/blob/v0.8.4/source/funkin/play/song/Song.hx)
- [Stage script callbacks and character access](https://github.com/FunkinCrew/Funkin/blob/v0.8.4/source/funkin/play/stage/Stage.hx)
- [Character animation and scale behavior](https://github.com/FunkinCrew/Funkin/blob/v0.8.4/source/funkin/play/character/BaseCharacter.hx)
- [Camera zoom event parameters](https://github.com/FunkinCrew/Funkin/blob/v0.8.4/source/funkin/play/event/ZoomCameraSongEvent.hx)

Default metadata registers Easy, Normal, and Hard plus the `erect` variation. That variation contains Erect and Nightmare and explicitly selects the empty instrumental suffix to reuse the same recording. Its time changes match the default metadata.

The visual envelope samples separated bass, lead, drums, and combined level every 40 ms. The stage samples the current song position with interpolation. Lighting intensity and lead-side halos follow the same section map as the charts. Native note-hit callbacks add character lean and halo accents. Repeated character scaling was removed after native testing exposed global-offset accumulation in Boyfriend’s renderer.

All new effect props render below character z-order. The native Flashing Lights preference reduces effect brightness and disables lightning and sharp beat pulses. The stage does not enable bot play, change note timing, or modify scoring.

## Foreground rhythm correction (1.3)

User feedback overrides the earlier assumption that the separated “other + vocals” signal always represents the perceived lead. The player preferred the original chart and wants the sound a listener would hum, with VOLT on accompaniment even in quieter sections.

Comparison with original commit `3d1aa1c` found 127 stronger original Hard attacks assigned only to VOLT in version 1.2. It also found 84 Hard player notes below the original full-mix strength floor. Stem normalization and forced role switching were therefore a poor guide to perceptual prominence; passing a grid-distance check did not validate musical feel.

The correction preserves every original foreground attack, including the opponent’s former main phrases, on Boyfriend with no timestamp shift. Original lane motifs and holds are retained wherever lane spacing allows. Advanced charts preserve the complete Hard core and add only audible full-mix attacks, with doubles supported by strong drum accents. VOLT gets sparse separated bass/drum accompaniment. This is a conservative, feedback-based approximation of the foreground, not a claim of automatic hummable-melody transcription.

The original grid reference is 34 ms, but notes retain acoustic timestamps rather than being forcibly quantized. Existing art, audio, stage geometry and script are unchanged. The section table now keeps Boyfriend as the foreground owner throughout; it still drives changes in visual intensity.

`analysis/reference-v1-chart.json` stores the original chart so rebuilding does not require Git history. Regression checks lock the original timestamps onto the player and prevent Erect/Nightmare from replacing the Hard core with unrelated rhythms. A native playtest can verify playback and rendering; the user remains the judge of musical feel.

## Instrumental-only phrases (1.4)

The latest request explicitly excludes vocal phrasing and permits instrumental synth melodies. Version 1.3’s preservation of full-mix attacks conflicts with that requirement, so its reference-chart and full-mix constraints are superseded. The new analyzer reads only `other.wav`, `bass.wav`, and `drums.wav`. It never merges vocals into the synth evidence. Source separation is imperfect, so authored rhythmic masks restrict which attacks may become notes.

Normalized waveform correlation places the September 24 clip at 25.212 seconds, with the matching reprise 78 seconds later. The September 22 clip begins at 37.624 seconds. The musical riff boundaries are 25.534–37.534 and 103.534–115.534; the following streams span 37.534–49.534 and 115.534–127.534. Both follow six attacks per bar, at sixteenth-step offsets 0, 3, 6, 9, 12, and 14. Hard and above use doubles throughout each riff, with chord pairs changing every two bars. Streams use single notes with a recurring anchor.

The installed official `assets/data/songs/milf/milf-chart.json` supplies a local reference for alternating anchors and recurring directional motifs. Its note timestamps are not copied. ENERGIZE’s own synth rhythm determines the timing and density. The original 160 BPM/34 ms grid keeps phrases consistent; each authored hit must also have separate instrumental evidence within 35 ms. No global audio delay is changed.

Regression checks independently verify the complete six-hit motifs, both repeated passages, every riff double, and Hard-core preservation in advanced charts. Short FNFC practice archives trim only copies of the music, preserve sample alignment, and shift chart notes by the same amount. They use the standard stage so the main stage’s song-position envelopes are not played against a shifted clock. The full installed song and visuals remain unchanged.

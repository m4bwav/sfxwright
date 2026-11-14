# Changelog

## 0.1.26, 2026-11-14

`synth pluck` (Karplus-Strong: hz, t60) and `whoosh --param passby=0.05-0.5`, which bends pitch fastest and peaks loudness at the closest point like a passing source; default whoosh is unchanged. thresholds.md: tuned hits need about 30 ms of body. Tests in `PluckAndPassby` (pitch within 1% at 110-440 Hz by FFT peak). An FM bell was built and failed `check` (CLICK, END_SILENCE), so it is not shipped. Because: Loy, *Musimathics* vols. 1-2 (sec. 6.10, 7.12, 9.4.8, 9.7.1); hit length a book rule, unverified; none heard.


edit.md: Rubber Band (R3, --formant, --pitchmap/--timemap) for pitch shifts that keep length or follow a path. Because: musicwright slide guitar study, 2026-11-13; unverified by listening.

## 0.1.25, 2026-11-13

`sequence --walkers N` overlays N walkers with their own phase and pace for a group footstep bed; default 1 is unchanged. plan.md Footsteps: three or more walkers get one group bed matched to surface, pace and room instead of per-step sync. edit.md: build a natural bed from many copies of one short unit with `sequence`. Test in `GroupBed`. Because: Murch, *Suddenly Something Clicked* (2025, ch. 21); book rules, unverified by listening.

## 0.1.24, 2026-11-13

`check --mono` reads the loss when channels are summed and flags MONO_LOSS above 3 dB; it runs by itself for `spatial: 3D` list sounds, which also get STEREO_3D when the file is stereo. `layer` warns ONSETS_COINCIDE when two layers' first onsets fall within 3 ms (skipped for the `offset` bed recipe). plan.md gains the job-first gate, 3D sounds ship mono, a repeated-trigger test before handover and 6 to 8 footstep takes per surface; edit.md gains layer staging and a note on tail spread in a set. Tests in `MonoFold` and `LayerOnsets`. Because: Zdanowicz and Bambrick, *The Game Audio Strategy Guide* (ch. 3, 8); measurements in thresholds.md.

## 0.1.23, 2026-11-07

From Bilbao, *Numerical Sound Synthesis* (sec. 1.2.2, 7.5.1): `synth modal` takes `strike` (0-1, where the object is hit; mode i is weighted by |sin(i pi strike)|, so a hit at the middle loses every second mode) and `velocity` (0-1, a harder hit is a shorter contact and a brighter sound). Left out, the sound is unchanged. Tests in `ModalStrike`. `routes.md` names both and says what the modal recipe cannot do (large-amplitude plates: cymbal crash, gong swell).

## 0.1.22, 2026-11-07

Reference only, from Francis, *The Audio Effects Workshop* (ch. 3, 13, 14): `edit.md` gains level before effects (envelope over compressor for a rogue peak), effect order in a chain, and serial against parallel chains.

## 0.1.21, 2026-11-07

Reference only, from Zizza, *Game Audio Fundamentals* (ch. 8, 11): `plan.md` From a game gains pickups and UI tuned to the score key, overlap limits for rapid pickups, priority as the cut order for low-end ports, and estimated against actual time per asset.

## 0.1.20, 2026-11-07

Reference only, from Lanham, *Game Audio Development With Unity 5.x* (ch. 3, 11): `finish.md` Unity line gains mixer DSP economy (Max Distance below the 500 default, one shared reverb or duck on a return, a duck with a soft knee and a longer release than the book's 10 ms).

## 0.1.19, 2026-11-07

Reference only, from Yewdall, *Practical Art of Motion Picture Sound*, 4th ed. (p. 351, 489, 502-506): `finish.md` gains Foreign M&E (no holes; production effects and foley laid back in when dialogue is muted), `edit.md` gains Show kit (approved premixed recurring events, baked whip pans), `plan.md` Ambience keeps single placeable elements apart from their bed.

## 0.1.18, 2026-11-07

Reference only, from Holman, *Sound for Film and Television* (3rd ed., p. 76, 161-166): `plan.md` Ambience gains scene grammar (ambience across a cut, masking split, prelap and postlap), `edit.md` gains Futz and worldize, `finish.md` gains film delivery (44.1 to 48 kHz resampling, DM&E stems for foreign versions).

## 0.1.17, 2026-11-07

Reference only, from Pirkle, *Designing Audio Effect Plugins in C++* (2nd ed., sec. 15.1-15.2, 17.1-17.4, 18.2-18.7, 19.1, ch. 2): `edit.md` gains From plugin DSP (echo and resonance rules for a hand-built reverb, gating to a floor, look-ahead before a limiter, oversampling before drive, smoothing swept parameters, modulated delay starting values).

## 0.1.16, 2026-11-07

Reference only, from Russ, *Sound Synthesis and Sampling* (2nd ed., sec. 4.3, 6.2-6.3, 6.8.3): `edit.md` gains From synthesis and sampling (render every variant from the original, why voices and fixed-spectrum hits take small pitch moves, a short alien onset layer on the hardest hits, a fuse check for layer levels).

## 0.1.15, 2026-11-07

Reference only, from Viers, *The Sound Effects Bible* (2008, ch. 18): `edit.md` gains Builds by event (explosion parts and trail-off, crash level contrast, automatic fire from single shots at the real rate, body falls, punches, swords, rumble, mouse-over, laser, clean attack spliced onto a fuller take) and a creature performance tip.

## 0.1.14, 2026-11-07

Reference only, from Ament, *The Foley Grail* (3rd ed., ch. 5, 10 and 11): `plan.md` gains late-over-early sync tolerance (one frame late passes, one early does not), shift a whole run before moving single hits, a sync sweet spot for busy props, thinner foley under songs, foley style matched to the picture, signature sounds, and mixed footfall kinds in a walk.

## 0.1.13, 2026-11-07

Reference only, from Collins, *Game Sound* (MIT, 2008, ch. 5 and 7): `plan.md` From a game gains what each event tells the player (warnings stay audible, a visual twin when the game must play muted), fixed, adaptive or interactive events, a dry source with the room added in the engine, object and material names, and more variants for long games.

## 0.1.12, 2026-11-07

`synth` gains bubbles, rain, motor and cricket, from Farnell, *Designing Sound* ch. 35, 38, 44 and 50 (written fresh from notes, no patches ported). Each passes `check` at its defaults; none has been in a blind listen yet.

## 0.1.11, 2026-11-07

Reference only, from Chion, *Audio-Vision* (2019 ed.): `plan.md` From a film cut gains sync binding, material detail, the room's response to loud events, and a silent, blind, together check. Untested on generated audio.

## 0.1.10, 2026-11-07

Reference only: `thresholds.md` records TONE_MISMATCH on real room tone. The 6 dB limit stays, and one-shot flags that real tone always trips are named. No code behaviour changes.

## 0.1.9, 2026-11-07

Reference only, from Cowan, *The Effects of Sound on People* (2016): `edit.md` gains Unpleasant or wearing. Untested on generated audio.

## 0.1.8, 2026-11-07

`synth list` prints every recipe, its parameters and materials. Because: the first worth A/B runs read `sfx.py` source to find them and one hit its turn cap. Evals are now graded on results by `evals/check_sfx.py`, not on calling `sfx.py`; routes stay as a separate check in `run_local.py`.

## 0.1.7, 2026-11-07

Reference only. `plan.md` gains Name the excitation and `edit.md` Stretching without resampling, from Miranda, *Computer Sound Design*, plus a line from Reveillac. `thresholds.md` records the attack skip test: no change to CLICK. Steiglitz read and nothing taken.

## 0.1.6, 2026-11-07

Reference only, from Fry, *Sound Design for the Stage* (2019): `plan.md` gains Question each sound, `edit.md` Moves from theatre, `rights.md` Recording your own. Theatre practice, untested on generated audio. Fry's advice to cut bass for distance is marked as taste, since air absorbs mainly highs.

## 0.1.5, 2026-11-07

Fish and layer listen applied to `references/edit.md`: winners spread over first take, another seed, parts and `bigger`, near chance, so layering is an option and not a proven upgrade. Fix: `gen` no longer crashes with a traceback when a busy host misses one poll, and reports a refused prompt as an error.

## 0.1.4, 2026-11-07

Reference only: `references/edit.md` gains shaping moves from Aikin, *Power Tools for Synthesizer Programming* (2004): noise for wind, sync, ring mod, detune in hertz, distortion by layer, reverb and delay. A music book, untested on generated sound.

## 0.1.3, 2026-11-07

Boundary and pilot listens applied: single hits and a comic sting stay on SA3 Medium, a melody goes to musicwright, and layering stayed in the film advice. New `add --gain` for `place`, `layer --recipe bigger|pitch|offset`, `record-sheet`, and a SEAM_SPECTRAL check on loops. A predictor click detector and shorter noise-floor frames were tested and rejected; see thresholds.md.

Reference: `references/edit.md` gains Building from parts, from Shepard, *Refining Sound* (2013), and found-sound moves from Murphy, *Ears to the Ground* (2024). Both untested on generated sound.

## 0.1.2, 2026-11-06

New `tone`, `check --tone-match` and `pop`, from the book notes. Fixes found by the Mentos pilot: `place` anchors a bed at its start instead of its loudest moment, which reported a misleading negative start; `gen` waits 30 s, not 6, for a busy host, which had dropped a whole render as unreachable.

## 0.1.1, 2026-11-06

Routes set from a blind listen: SA3 Medium 10 of 12, procedural 2, Small SFX 0. `gen` now prefers Medium over Small SFX, and the idle host still comes first.

## 0.1.0, 2026-11-06

Reference: `references/edit.md` gains reason-based moves for thin or muddy output from Case, *Sound FX* (2007). Because: a book run for the ai-sfx beat; nothing there said why a move works. All marked unheard.

First release: `sfx.py` (plan, synth, gen, checks, edits, finish, documents, ship), `sounds.json` schema 1, references. Routes unheard until the bake-off page is answered.

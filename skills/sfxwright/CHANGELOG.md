# Changelog

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

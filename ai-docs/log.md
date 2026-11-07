# Log

## 2026-11-06, session 1
Built and merged the ai-sfx beat (everscout PR 165; unreleased). First scan: 281 items over 45 days, triaged by title keyword, 5 threads read, 4 notes. Wrote the models and craft surveys (through two research agents) and `books/sfx-wanted-books.md`. Decided on an own plugin. Nothing built, rendered or installed.

Distilled 23 books Mark supplied into `books/plugin-learnings/sfx/` (five reading agents, selective reading). Not yet applied.

## 2026-11-06, session 2

Reddit threads read (survey section), no ranking change. Built sfx.py, sfx_audio.py, sfx_synth.py, skill, references, tests, evals. API prompt ran on PC Medium and Mac Small SFX. Bake-off rendered, 36 takes on each of Medium, Small SFX and Small SFX base; blind page built, unheard. Boundary test rendered, measured, unheard. Calibrated with planted faults, numbers in thresholds.md. Evals: all pass after three reruns, about $14 in all; baselines are not a fair comparison because graders look for sfx.py. Public repo, banner, social preview set through the browser. First wiki page saved through the browser; 12 pages by wikiwright. Integration PRs: 11 merged, threewright open, madnesswright skipped. Lab audio and host notes live in Ai/sfxwright-lab, outside this repo.

Bake-off read and unblinded after Mark confirmed the fast answers were his: Medium 10, procedural 2 (laser, fire), Small SFX 0. Note 10 of 12 matched the guess because the guess was Medium nearly everywhere. Routes changed, gen prefers Medium, 0.1.1.

## 2026-11-06, session 3

Blind boundary page built and pilot run on Mentos s6: 20 Medium takes, two synth layers, spotted from frames (tank splits at 11.0 s), two mixes over the film's own audio, no one has heard them. `ship` on the pilot says CHECK (Stability licence), not commercial. Added tone, tone-match and pop. Pilot found two bugs, both fixed: bed anchoring in place, and a 6 s probe that lost a render on a busy host. Ten plugins released with their notes (results in sfxwright-lab/integration-2026-11-06.md); grindwright's sound lane now opens with either plugin; pixelwright's real changelog fault was a UTC date label; everscout 0.12.4 ships the beat and the thread flag fix. 0.1.2.

## 2026-11-07, session 4

Read both pages. Boundary, unblinded: SA3 won piano, timpani and comic sting; ACE won brass. Pilot: mix A beat the original and mix B, marked "sounds artificial". Applied to routes.md, edit.md and musicwright. Added `add --gain`, `layer --recipe`, `record-sheet`, SEAM_SPECTRAL (0 of 29 false, 21 of 29 planted, where the sample step caught none). Tested and rejected a predictor click detector and shorter floor frames: no real gain in the calibrate script, numbers in thresholds.md. Rendered 15 generated parts on Medium and built the blind fish and layer page, unheard. threewright PR 18 was already merged when checked. 0.1.3.

## 2026-11-07, session 5

Read the fish and layer listen, unblinded: crate parts, sword seed 1, boom seed 2, spell seed 1, beast `bigger` (seed 3 also good). Seeds won 3 of 5 with 3 of 5 clips, so chance; "all about the same" never picked. Applied to edit.md. Dropped the other-takes retry of pilot mix A: this result does not show that seeds matter. Replaying the wiki found a real bug: `gen` crashed with a traceback when a busy host missed a 20 s poll, which would lose the prompt id; fixed with two tests. Wiki moved to 0.1.5: new replay script `_verify/wiki-verify.py` in the wiki repo, 155 commands, all matching. 0.1.5.

## 2026-11-07, session 6

Tested the attack skip lead: it does not limit body clicks (numbers in thresholds.md), CLICK unchanged. Another session distilled Fry (0.1.6). Distilled the rest in part: Miranda (excitation and stretching moves applied), Reveillac (one line; a catalogue of music effects), Steiglitz (nothing taken). 0.1.7. Script and results in sfxwright-lab/clickcal.

## 2026-11-07, session 7

Read the waiting page. Listed sfxwright in mark-local (`Ai/.claude-plugin/marketplace.json`; the install stays sfxwright@sfxwright). Wrote `roomtone/record_tone.cmd` in the lab for Mark's recording. Rewrote the value cases to be graded on results (`evals/check_sfx.py`, `build_fixtures.py`). A one-case trial found the baseline read `sfxwright` in its temp folder name, searched the disk and used the installed plugin: fixed in evergreen-protocol PR #42, v0.18.5, installed. Earlier baselines may share this, including voicewright's KEEP. Added `synth list`. Full A/B: CUT, numbers in TESTS.md T-20261107-1. Total spend about $19.70 against about $14 approved: `--max-usd 11` only stops top-ups, not the base runs. 0.1.8.

## 2026-11-07, session 8

Mark ruled keep on the worth page, over CUT; recorded in TESTS.md and evergreen.json, no trim. No new books (newest SFX file arrived 2026-11-06) and the new beat leads are only book notes. Room tone still unrecorded. Wiki moved to 0.1.8 with `synth list`.

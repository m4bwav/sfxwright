# Log

## 2026-11-06, session 1
Built and merged the ai-sfx beat (everscout PR 165; unreleased). First scan: 281 items over 45 days, triaged by title keyword, 5 threads read, 4 notes. Wrote the models and craft surveys (through two research agents) and `books/sfx-wanted-books.md`. Decided on an own plugin. Nothing built, rendered or installed.

Distilled 23 books Mark supplied into `books/plugin-learnings/sfx/` (five reading agents, selective reading). Not yet applied.

## 2026-11-06, session 2

Reddit threads read (survey section), no ranking change. Built sfx.py, sfx_audio.py, sfx_synth.py, skill, references, tests, evals. API prompt ran on PC Medium and Mac Small SFX. Bake-off rendered, 36 takes on each of Medium, Small SFX and Small SFX base; blind page built, unheard. Boundary test rendered, measured, unheard. Calibrated with planted faults, numbers in thresholds.md. Evals: all pass after three reruns, about $14 in all; baselines are not a fair comparison because graders look for sfx.py. Public repo, banner, social preview set through the browser. First wiki page saved through the browser; 12 pages by wikiwright. Integration PRs: 11 merged, threewright open, madnesswright skipped. Lab audio and host notes live in Ai/sfxwright-lab, outside this repo.

Bake-off read and unblinded after Mark confirmed the fast answers were his: Medium 10, procedural 2 (laser, fire), Small SFX 0. Note 10 of 12 matched the guess because the guess was Medium nearly everywhere. Routes changed, gen prefers Medium, 0.1.1.

## 2026-11-06, session 3

Blind boundary page built and pilot run on Mentos s6: 20 Medium takes, two synth layers, spotted from frames (tank splits at 11.0 s), two mixes over the film's own audio, no one has heard them. `ship` on the pilot says CHECK (Stability licence), not commercial. Added tone, tone-match and pop. Pilot found two bugs, both fixed: bed anchoring in place, and a 6 s probe that lost a render on a busy host. Ten plugins released with their notes (results in sfxwright-lab/integration-2026-11-06.md); grindwright's sound lane now opens with either plugin; pixelwright's real changelog fault was a UTC date label; everscout 0.12.4 ships the beat and the thread flag fix. 0.1.2.

# sfxwright handoff

State 2026-11-06, end of session 3. Public repo, v0.1.2 released, wiki live at 0.1.0. Bake-off applied. Two listening pages wait.

## Waiting on Mark
- Boundary listen: `Ai/sfxwright-lab/boundary/ask/sfx-boundary-1` (blind ace vs sa3, key.json beside make_page.py). Read with `ask.py read`; if down, `serve --detach`. Then confirm or change the line in routes.md and musicwright.
- Pilot listen: `Ai/sfxwright-lab/pilot-mentos/ask/sfx-pilot-1`, Mentos s6 tower fall, original vs two mixes at -16 LUFS, blind, key.json beside build.py. If layering loses to the film's own H3 sound, change the film advice.
- threewright PR 18: open, no CI. Merge or close.
- What "Mark's plugin sets" means: no such list found; sfxwright@sfxwright is installed. The nearest is Ai/.claude-plugin/marketplace.json (mark-local), which also omits voicewright.
- Optional: books still missing, `books/sfx-wanted-books.md`.

## Owed, in order
1. Worth testing: seed fishing and layering on Medium; base vs distilled was rendered (`takes/smallbase`), never heard.
2. Worth A/B: `evergreen-worth`; current graders favour the skill by construction. Costs money (the evals cost about $14).
3. Book changes not yet applied: record sheet, layer recipes, spectral seam (test first that it adds anything). Better CLICK and NOISE_FLOOR. Try `tone --tone-match` on real room tone: calibrated on planted noise only. Wiki predates tone and pop, and its examples ran before the last check fixes: re-verify at the next wiki update.
4. `place` has no per-sound gain; the pilot baked gains with `edit`. Add one if the pilot survives the listen.

## Open points
Stability licence needs registration and under USD 1M with affiliates; Sonniss, BOOM and A Sound Effect ban AI training; `EmptyLatentAudio` minimum 1 s; both hosts offer only ElevenLabs v2, removed 2027-03-01.

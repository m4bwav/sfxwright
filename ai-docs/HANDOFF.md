# sfxwright handoff

State 2026-11-07, end of session 8. Public repo, v0.1.8, wiki at 0.1.8.

## Waiting on Mark
- Room tone: double-click `Ai/sfxwright-lab/roomtone/record_tone.cmd` (webcam mic, about 70 s) or save two phone files there. Then run `check --tone-match` on them, a fill against its neighbour, and write the result in thresholds.md.
- Optional: books still missing, `books/sfx-wanted-books.md`.

## Owed, in order
1. Evergreen refresh due 2026-11-20.
2. voicewright's worth KEEP may have a contaminated baseline (run folder named the skill; fixed in evergreen 0.18.5). Its session should grep its without-arm transcripts for `voicewright` before rerunning anything.

CLICK stays weak; the attack skip lead is closed (thresholds.md). No other detector is planned unless a listen shows missed clicks matter.

Worth: Mark ruled keep as is on 2026-11-07, over the CUT verdict. Do not rerun or trim for this result.

Dropped: Small SFX base vs distilled listen (Medium beat Small SFX 12 to 0). Other takes for pilot mix A (the fish listen did not show that seeds matter).

## Wiki upkeep
From the wiki clone: `python _verify/wiki-verify.py . <scratch> --out _verify/wiki-verify.out.txt`; `--rewrite` writes new output into the pages, then read the diff. It expects the repo as sibling `sfxwright`.

## Open points
Stability licence needs registration and under USD 1M with affiliates; Sonniss, BOOM and A Sound Effect ban AI training; `EmptyLatentAudio` minimum 1 s; both hosts offer only ElevenLabs v2, removed 2027-03-01.

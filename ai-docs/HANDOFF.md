# sfxwright handoff

State 2026-11-07, end of session 6. Public repo, v0.1.7, wiki at 0.1.5 (0.1.6 and 0.1.7 changed references only).

## Waiting on Mark
- Thirty seconds of real room tone, twice, same room, as a phone or recorder file in `Ai/sfxwright-lab/roomtone/`: `check --tone-match` has only met planted noise.
- Paid `evergreen-worth` A/B (about $14 last time): yes or no.
- What "Mark's plugin sets" means: no such list found; sfxwright@sfxwright is installed. The nearest is Ai/.claude-plugin/marketplace.json (mark-local), which also omits voicewright.
- Optional: books still missing, `books/sfx-wanted-books.md`.

## Owed, in order
1. Evergreen refresh due 2026-11-20.

CLICK stays weak; the attack skip lead is closed (thresholds.md). No other detector is planned unless a listen shows missed clicks matter.

Dropped: Small SFX base vs distilled listen (Medium beat Small SFX 12 to 0). Other takes for pilot mix A (the fish listen did not show that seeds matter).

## Wiki upkeep
From the wiki clone: `python _verify/wiki-verify.py . <scratch> --out _verify/wiki-verify.out.txt`; `--rewrite` writes new output into the pages, then read the diff. It expects the repo as sibling `sfxwright`.

## Open points
Stability licence needs registration and under USD 1M with affiliates; Sonniss, BOOM and A Sound Effect ban AI training; `EmptyLatentAudio` minimum 1 s; both hosts offer only ElevenLabs v2, removed 2027-03-01.

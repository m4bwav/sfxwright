# sfxwright handoff

State 2026-11-06, end of session 1. No repo yet; this folder holds docs only.

## Done
- Beat `everscout/beats/ai-sfx`, merged; first scan is shallow (title triage, 5 threads read, 4 notes in `~/.everscout/data/ai-sfx`).
- Surveys: `ai-docs/research/2026-11-06-sfx-survey-models.md`, `-craft.md`. Most per-job rankings are grade D until the bake-off.
- Book list: `books/sfx-wanted-books.md`. Decision: `ai-docs/decisions/2026-11-06-own-plugin.md`.

## Books
Five notes in `books/plugin-learnings/sfx/` (23 books, read in part, nothing applied since no plugin exists yet). Each ends in ranked changes: apply them while building. All numbers are uncalibrated. Top: `sfx.py check` with a planted-fault kit; `sfx.py synth`, shaker and modal first; manifest fields `sync_point_s`, category and axis matrix; `sfx.py check set`.

## Waiting on Mark
- Optional: the books still missing, listed in `books/sfx-wanted-books.md`.

## Owed, in order
1. Read more scan threads before Reddit RSS ends 2026-11-13: r/ElevenLabs SFX v3 and "Sound Effects section now worse", r/sounddesign horror synthesis tips, r/sounddesign 122-minute foley plan. Then release everscout with the beat.
2. Plugin skeleton in a new public repo after a scrub; `sfx.py`, sound list and manifest format. Borrow ideas named in the models survey, section 4.
3. Run the unrun API prompt (models survey, section 2) on the Mac Small SFX and PC Medium; check `SaveAudioAdvanced` inputs. Both hosts need no install for this. The Mac was busy with Z-Image at the check: queue behind it.
4. Musicwright boundary test: instrument one-shots and stingers on ACE-Step; record the line in both repos.
5. Bake-off on a fixed list, including the gentle wind brief; askwright page with guesses.
6. Edit and finish tools, evals, pilot, integration PRs, wiki, release, as the kickoff lists.

## Open points
Unsettled lists close each survey. Hard facts to respect: Stability licence needs registration and under USD 1M with affiliates; Sonniss, BOOM and A Sound Effect ban AI training; `EmptyLatentAudio` minimum 1 s; both hosts offer only ElevenLabs v2, removed 2027-03-01.

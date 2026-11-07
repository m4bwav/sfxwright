# Continue sfxwright

Start in `D:\m4bwa\Claude\Projects\Ai`. This prompt does not change between sessions; state lives in `sfxwright/ai-docs/HANDOFF.md`.

## Load state

Read `sfxwright/ai-docs/HANDOFF.md`, `ai-docs/log.md`, `ai-docs/decisions/`, both surveys in `ai-docs/research/`, and the brief at `prompts/2026-11-06-sfxwright-plugin-kickoff.md` (success measures, integration list, stop points). Read `voicewright` as the model for shape and for "when installed" notes, and musicwright `mw.py` before writing any audio check. Use `evergreen-new` for units, `evergreen-test` for evals, `wikiwright` for the wiki, and comfyui-gen rules for hosts.

## Check every session

- New books: compare `books/` and `D:/RawStorage/BigDownloads/Unorganized` by file name with `books/sfx-wanted-books.md`. Distill any new or approved one by `books/plugin-learnings/INDEX.md`. Never look for or download copies.
- Open listening or decision pages: `python askwright/skills/askwright/scripts/ask.py read <page>`; if down, `serve --detach`.
- New `ai-sfx` beat leads: `python everscout/scripts/everscout.py leads --beat ai-sfx`.

## What waits on Mark

The items under Waiting on Mark in HANDOFF.md. Always his: books to obtain, installing engines, nodes or large models, paid API use, listening picks, outward posts, directory or registry submissions, hooks or settings outside these repos, and other people's repos.

## Order of work

1. Read answers and act on them.
2. Work the Owed list in HANDOFF.md in order, skipping what waits on Mark and queueing those on an askwright page.
3. The kickoff's order: formats, script and routes; bake-off page; edit and finish tools; evals; pilot; integration PRs; wiki; release.

## Stop early

If nothing is workable without Mark, say so in two lines, print the start command, and write nothing to the repo.

## Rules

Worktrees for shared clones. Kill by PID only. Queue behind a busy GPU and watch renders with a background loop that has a deadline. No audio without clear rights in the public repo. No AI attribution. Merge your own PRs after checks pass, leaving one open for the risk cases in the global rules. Thresholds change only with a calibration note saying what they were calibrated on. Heuristics are never presented as verdicts.

## Hand over

Update HANDOFF.md and the log, then print this same start command with the folder:

`Execute D:/m4bwa/Claude/Projects/Ai/sfxwright/ai-docs/plans/2026-11-06-sfxwright-continue-prompt.md`

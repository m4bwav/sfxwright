# AGENTS.md

Rules for any AI agent working in this repository. `CLAUDE.md` imports this file; `.github/copilot-instructions.md` points here.

## What this is

sfxwright: one skill, `skills/sfxwright/`. SKILL.md holds the workflow, `references/` the details, `scripts/sfx.py` the CLI, `sfx_audio.py` measurements, `sfx_synth.py` recipes. Research, decisions, the log and the handoff are under `ai-docs/` (start with `ai-docs/HANDOFF.md`). Map: `CODEMAP.md`.

## Rules

- Scripts: standard library only, Python 3.9+, UTF-8, LF. ffmpeg stays optional. Every change gets a test. Run `python -m unittest discover -s tests`.
- `sounds.json` is the contract with other plugins. Change it only with a schema bump. Plugins read the file and never import each other.
- This repo is public. No private names, hostnames, paths or lab audio. Audio only with clear rights. No book text; recipes are written fresh from notes.
- No copies of sounds from named films and no famous sound marks, in prompts, evals or samples.
- Thresholds change only with a calibration note in `references/thresholds.md`. A heuristic is never a verdict.
- Size budget: `python scripts/budget.py`.
- Evergreen unit: read `skills/sfxwright/evergreen.json` before editing; log changes in its CHANGELOG with the reason, lessons in LEARNINGS. Beat `ai-sfx` feeds refreshes.
- A release bumps `.claude-plugin/plugin.json`, `plugin.json`, `VERSION` in `sfx.py`, `metadata.version` in SKILL.md and the CHANGELOG together.
- Plain short sentences, no em dashes, relative links. No AI attribution anywhere.

## Commands

- Tests: `python -m unittest discover -s tests`
- Budget: `python scripts/budget.py`
- Calibrate: `python scripts/calibrate.py <folder of audio>`

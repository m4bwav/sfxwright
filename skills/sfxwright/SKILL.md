---
name: sfxwright
description: "Plan, make, edit, check and document sound effects for games, film, video and apps, keeping each file's source and licence on disk. A brief, shot list or game event list becomes a sound list; sounds come from procedural recipes with no model, any reachable ComfyUI, hosted APIs or CC0 libraries; variation sets, loops, layers and footstep sequences are built by script; measured checks catch clipping, clicks, DC, cut ends, padding and bad seams; `ship` answers 'can we ship this?'. Use whenever a project needs a sound effect or foley: 'I need a door creak', 'sound list for my game', 'footsteps on gravel', 'add sound to this cut', 'six variations of this hit', 'why does this loop click', 'can I use this Freesound file commercially', 'which AI model for SFX'. Also first for any request to recreate a sound from a named film or a famous trademarked sound. Whole music cues and songs are musicwright; voices are voicewright. Also 'refresh sfxwright'."
license: MIT
metadata:
  version: 0.1.26
---

# sfxwright

Outcome: every sound is a row in a `sounds.json` list with its event, layers, variations, length, route and status, and every file records its source, model, prompt, seed, licence and edits. Numbers catch faults; a person's ear decides. Say which sounds nobody has heard.

`SFX` means `python scripts/sfx.py` from this folder (run it, do not read it; `sfx_audio.py` and `sfx_synth.py` are its modules). Read one reference when its step needs it.

## Step 0: freshness

Read `evergreen.json`. If `contradiction` is set or today is on or after `next_due`, say so in one line, do the task, then run `evergreen-refresh`. If `verify_at_use` is true, re-check model and licence claims before relying on them. The `ai-sfx` everscout beat feeds refreshes when present.

## Step 1: rights first

- A sound from a named film or show, or a famous sound mark (lightsaber, THX Deep Note, NBC chimes, Intel bong, MGM lion, Netflix ta-dum): decline the copy in one sentence and offer an original built from acoustic traits. Do not put the title or name in a prompt or file: [references/rights.md](references/rights.md).
- `commercial` in the list decides which sources are allowed. If the user has not said, set `--commercial yes`, the stricter reading, and say so in one line; do not stop to ask.
- A file with no known licence does not go into a commercial project. Find its source or replace it. Never guess a licence.
- Never train a model on, or feed into training, Sonniss, BOOM or A Sound Effect files.

## Step 2: plan

`SFX init sounds.json --project NAME --use game --commercial yes`, then `SFX add` per sound. A film cut, game design or plain description all end here: [references/plan.md](references/plan.md). For anything with axes (surface, force, size), run `SFX plan --axis surface=6 --axis force=3 --variations 4 --budget 100` before committing to files. Format: [references/format.md](references/format.md).

## Step 3: pick the route

By job, licence and hardware: [references/routes.md](references/routes.md). Run `SFX doctor` once. Say the pick and why in one line. Installing a node, engine or large model, and any paid API call, needs the user's yes first; use what is present meanwhile. Nothing reachable is not an error: `SFX synth` needs no model, and `SFX gen --workflow-out` hands over a workflow.

## Step 4: make

```
SFX synth list                          # every recipe, its parameters and materials
SFX synth footstep --param surface=gravel --takes 6 --out takes/ --name step
SFX gen "heavy wooden crate dropped on concrete, dead room" --seconds 2 --takes 4 --out takes/ --name crate
SFX library found.wav --licence cc0 --library Freesound --title "..." --url ...
SFX register sounds.json crate takes/crate_01.flac
```

Prompts name source, material, space and time, not a story. A requested length is a maximum, so expect padding. Fish seeds before changing words. Never ask a model for a walk cycle: make single steps, then `SFX sequence`.

## Step 5: edit

`SFX edit` (tidy, trim, fade, gain, peak, pitch, stretch, reverse, convolve, dc), `layer`, `vary`, `sequence`, `loop`, `place`, `record-sheet` (plan for sounds with a record route), `tone` (steady quiet stretch, optional fill; compare with `check --tone-match`), `pop` (add or `--verify` head and tail 2 pops on a stem). Recipes and what each edit costs: [references/edit.md](references/edit.md). Pitch is varispeed by default; a stretch smears an impact. Edits carry provenance forward, and a no-derivatives source refuses them. Never copy or rename a sound by hand: the sidecar stays behind. Write to the final name with `edit`, `finish` or `synth --out`.

## Step 6: check every batch

```
SFX check takes/*.flac --seconds 2     # readings and flags per file
SFX check takes/*.wav --mono           # phase loss when summed; on for 3D sounds
SFX set takes/step_*.wav               # near-duplicates, outliers, level spread
SFX timing walk.wav                    # too even, or one sample repeating
SFX sheet takes/*.wav --out sheet.png  # look at the waveforms
```

Any variation set always gets `set`. A flag means listen; it is not a verdict, and a clean result does not mean a sound is good. Waive what the brief wants (`--waive CLICK` for crackle). What each number means and what it was calibrated on: [references/thresholds.md](references/thresholds.md).

## Step 7: listen

Numbers cannot say whether a sound suits its picture or a set reads as one object. Put picks on an askwright page when present, level-matched (`SFX review --match`) and blind, with picture for film. Otherwise give a labelled file list and plain questions. Record what was heard in the take's `heard` field and mark the pick `picked: true`.

## Step 8: finish and document

`SFX finish in out --dest game-sfx`: gain only, then encode last. An unknown destination is an error: ask. Use `mw.py master` when musicwright is present and a whole mix needs a loudness target. Engines and destinations: [references/finish.md](references/finish.md).

`SFX doc sounds.json --kind cue|impl|credits`, then `SFX ship sounds.json`. Report BLOCKED, CHECK or CLEAR with the reasons, attribution owed and store disclosure. It is a record, not legal advice.

## Output

The route, the list path, flags per batch, what was heard and by whom, and the `ship` answer when anything is going out.

## Rules

- Never call a generated sound recorded or AI-free. `ship` lists what needs disclosure.
- Music with notes, key and tempo goes to musicwright; dialogue and its room tone go to voicewright or cinewright.
- Samples published with the plugin must have clear rights.

## While working: capture learnings

If the user corrects you, an error repeats, or a workaround turns up, add it to [LEARNINGS.md](LEARNINGS.md). If it proves a rule wrong, fix the rule, log it in [CHANGELOG.md](CHANGELOG.md) and set `contradiction` in `evergreen.json`.

## Maintenance

Evergreen unit, tier `fast`; state in `evergreen.json`. See [MAINTENANCE.md](MAINTENANCE.md), [RESEARCH.md](RESEARCH.md), [TESTS.md](TESTS.md), `evals/`.

# Tests

Offline: `python -m unittest discover -s tests` from the repository root. Calibration on real audio: `python scripts/calibrate.py <folder>`. Evals: `evals/`.

Last suite 2026-11-06, Sonnet, 2 runs per case: all 7 trigger and decoy cases 2/2; 8 action cases 2/2 after fixes (film-sync, no-comfy and hit-layers were rerun). Baselines failed 7 of 8 but most graders look for `sfx.py` calls, so that gap proves the script is used, not that results are better. A worth A/B is still owed.

## T-20261107-1 worth A/B

`evergreen.py worth --heavy` 0.18.5, Sonnet, 8 result-graded cases, 3 runs per arm, 48 runs, $16.69. As run: 79% with, 83% without. Three grader faults were then fixed and the saved runs regraded with no new runs: 96% with, 88% without, margin 16 points, cost x1.72, turns x2.27. Verdict CUT (no gain beyond noise at the higher cost). The only case that separates: ten-events, 3/3 against 0/3, because plans without the skill dropped the commercial flag. Not measured by these cases: how the sounds sound, `ship` on a real mixed list, seed and take records over a long project. Regrading after seeing results is weaker evidence than a fresh run. Original numbers: `sfxwright-lab/worth-2026-11-07/heavy/ab/aggregate-as-run.json`.
led to: `synth list`; the question to Mark on `sfxwright-lab/ask/sfx-worth-1`.

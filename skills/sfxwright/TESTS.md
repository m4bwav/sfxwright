# Tests

Offline: `python -m unittest discover -s tests` from the repository root. Calibration on real audio: `python scripts/calibrate.py <folder>`. Evals: `evals/`.

Last suite 2026-11-06, Sonnet, 2 runs per case: all 7 trigger and decoy cases 2/2; 8 action cases 2/2 after fixes (film-sync, no-comfy and hit-layers were rerun). Baselines failed 7 of 8 but most graders look for `sfx.py` calls, so that gap proves the script is used, not that results are better. A worth A/B is still owed.

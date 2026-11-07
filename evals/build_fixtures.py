"""Lay every eval fixture into skills/sfxwright/evals/fixtures/<kind>/, where `evergreen.py worth --ab` copies them from.

  python evals/build_fixtures.py

Audio is synthesised, the folders are git-ignored, and `run_local.py` builds the same state per run.
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_local  # noqa: E402

FIX = run_local.REPO / "skills/sfxwright/evals/fixtures"
for kind in ("events", "takes", "seam", "unknown", "brief"):
    d = FIX / kind
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    run_local.scaffold(kind, d)
    print("built", kind)

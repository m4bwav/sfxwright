"""Plant known faults in real audio and report what `sfx.py check` catches. Run: python scripts/calibrate.py <folder of clean audio> [--limit N]

Each file is tidied first, so a clean file should raise no fault flag. Then every fault is planted at known strength
and the expected flag is looked for. The result belongs in skills/sfxwright/references/thresholds.md.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "sfxwright" / "scripts"))
import sfx  # noqa: E402
import sfx_audio as A  # noqa: E402

PLANTS = [  # fault, amount, flag that should appear, label
    ("click", 0.5, "CLICK", "click +0.5"), ("click", 0.1, "CLICK", "click +0.1"), ("click", 0.03, "CLICK", "click +0.03"),
    ("dc", 0.01, "DC", "dc 0.01"), ("dc", 0.002, "DC", "dc 0.002"),
    ("clip", 12.0, "CLIP", "clip +12 dB"), ("clip", 3.0, "CLIP", "clip +3 dB"),
    ("cut-head", None, "CUT_HEAD", "cut head"), ("cut-tail", 0.4, "CUT_TAIL", "cut tail at 40%"),
    ("noise", -45.0, "NOISE_FLOOR", "noise -45 dB"), ("noise", -55.0, "NOISE_FLOOR", "noise -55 dB"),
    ("pad", 1.0, "END_SILENCE", "1 s of padding"),
]


def flags(path, **kw):
    return A.flag(A.measure(A.read_audio(path)), **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--glob", default="*", help="file name pattern, to spread a sample across sounds")
    a = ap.parse_args()
    files = sorted(p for p in Path(a.folder).rglob(a.glob) if p.suffix.lower() in (".wav", ".flac", ".ogg"))
    if a.limit:
        files = files[:a.limit]
    false, hits, total, clean_rows = {}, {}, 0, 0
    with tempfile.TemporaryDirectory(prefix="sfxcal_") as d:
        for f in files:
            clean = Path(d) / "clean.wav"
            A.write_wav(clean, sfx.tidy(A.read_audio(f)))
            base = flags(clean)
            clean_rows += 1
            for fl in base:
                false[fl] = false.get(fl, 0) + 1
            total += 1
            for fault, amount, want, label in PLANTS:
                bad = Path(d) / "bad.wav"
                argv = ["degrade", str(clean), str(bad), "--fault", fault]
                if amount is not None:
                    argv += ["--amount", str(amount)]
                ns = sfx.build_parser().parse_args(argv)
                ns.fn(ns)
                got = flags(bad)
                row = hits.setdefault(label, [0, 0])
                # A flag already on the clean file proves nothing, so that file is left out of this row.
                if want in base:
                    continue
                row[1] += 1
                row[0] += want in got
    print(json.dumps({"clean_files": clean_rows, "false_flags_on_clean": false, "planted": {k: "%d/%d" % tuple(v) for k, v in hits.items()}}, indent=1))


if __name__ == "__main__":
    main()

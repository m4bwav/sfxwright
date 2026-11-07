"""Judge an eval case on its end state, whatever tool made it. Standard library only; run in the run folder.

  python evals/check_sfx.py <case> [folder]    exit 0 right, 1 wrong; prints why

These never look for sfx.py or its file shapes, so a run without the plugin can pass.
"""
import glob
import json
import math
import os
import re
import struct
import subprocess
import sys


def read_wav(path):
    """Mono float samples and the rate, for PCM 8/16/24/32 and float 32/64 WAV."""
    b = open(path, "rb").read()
    if b[:4] != b"RIFF" or b[8:12] != b"WAVE":
        raise ValueError("not a WAV")
    i, fmt, data = 12, None, None
    while i + 8 <= len(b):
        cid, n = b[i:i + 4], struct.unpack("<I", b[i + 4:i + 8])[0]
        if cid == b"fmt ":
            fmt = struct.unpack("<HHIIHH", b[i + 8:i + 24])
            if fmt[0] == 0xFFFE:
                fmt = (struct.unpack("<H", b[i + 32:i + 34])[0],) + fmt[1:]
        elif cid == b"data":
            data = b[i + 8:i + 8 + n]
        i += 8 + n + (n & 1)
    code, ch, sr, _, _, bits = fmt
    w = bits // 8
    frames = len(data) // (w * ch)
    if code == 3:
        v = struct.unpack("<%d%s" % (frames * ch, "f" if w == 4 else "d"), data[:frames * ch * w])
    elif w == 1:
        v = [(x - 128) / 128 for x in data[:frames * ch]]
    elif w == 2:
        v = [x / 32768 for x in struct.unpack("<%dh" % (frames * ch), data[:frames * ch * 2])]
    elif w == 3:
        v = [int.from_bytes(data[k:k + 3], "little", signed=True) / 8388608 for k in range(0, frames * ch * 3, 3)]
    else:
        v = [x / 2147483648 for x in struct.unpack("<%di" % (frames * ch), data[:frames * ch * 4])]
    return [sum(v[k:k + ch]) / ch for k in range(0, frames * ch, ch)], sr


def rms(x):
    return math.sqrt(sum(v * v for v in x) / max(1, len(x)))


def similarity(a, b):
    """Best normalised correlation at small lags: gain copies score 1."""
    step = max(1, min(len(a), len(b)) // 8000)
    a, b = a[::step], b[::step]
    best = 0.0
    for lag in range(-40, 41, 2):
        p = [(a[i], b[i + lag]) for i in range(max(0, -lag), min(len(a), len(b) - lag))]
        d = math.sqrt(sum(x * x for x, _ in p) * sum(y * y for _, y in p))
        if d:
            best = max(best, abs(sum(x * y for x, y in p)) / d)
    return best


def fail(msg):
    print("FAIL:", msg)
    return 1


def clean_end(x, sr):
    tail = x[-max(1, sr // 200):]
    return max(abs(v) for v in tail) < max(0.05, 0.25 * max(abs(v) for v in x))


def hit_layers(d):
    files = sorted(glob.glob(os.path.join(d, "hit", "**", "*.wav"), recursive=True))
    # Layers or takes may sit beside the deliveries, so extra WAVs are fine as long as six good ones exist.
    good = []
    for f in files:
        x, sr = read_wav(f)
        n = len(x) / sr
        peak = max(abs(v) for v in x) if x else 0
        clipped = sum(abs(v) >= 0.999 for v in x)
        if 0.05 <= n <= 5 and 0.05 < peak and clipped < 3 and clean_end(x, sr) and abs(sum(x) / len(x)) < 0.02:
            good.append((os.path.basename(f), x))
    if len(good) < 6:
        return fail("%d of %d WAVs in hit/ are usable hits (length, level, no clipping, no cut end, no DC), need 6" % (len(good), len(files)))
    distinct = []
    for name, x in good:
        if all(similarity(x, y) < 0.995 for _, y in distinct):
            distinct.append((name, x))
    if len(distinct) < 6:
        return fail("only %d hits differ from each other by more than gain" % len(distinct))
    return 0


def bad_seam(d):
    original = subprocess.run(["git", "show", "HEAD:ambience.wav"], cwd=d, capture_output=True).stdout
    tried = []
    for f in glob.glob(os.path.join(d, "**", "*.wav"), recursive=True):
        if original and open(f, "rb").read() == original:
            continue
        x, sr = read_wav(f)
        if len(x) / sr < 1.0:
            continue
        overall = rms(x)
        w = sr // 100
        jump = abs(x[-1] - x[0])
        step = sum(abs(x[i + 1] - x[i]) for i in range(0, len(x) - 1, 7)) / (len(x) / 7)
        dip = min(rms(x[:w]), rms(x[-w:])) / overall if overall else 0
        tried.append("%s jump %.3f step %.3f dip %.2f" % (os.path.basename(f), jump, step, dip))
        if jump <= max(0.02, 6 * step) and dip >= 0.4:
            return 0
    return fail("no changed WAV of 1 s or more joins without a jump or a dip: " + "; ".join(tried))


def door(d):
    f = os.path.join(d, "door.wav")
    if not os.path.isfile(f):
        return fail("no door.wav")
    x, sr = read_wav(f)
    n = len(x) / sr
    if not 0.5 <= n <= 15 or max(abs(v) for v in x) < 0.05 or sum(abs(v) >= 0.999 for v in x) >= 3:
        return fail("door.wav length %.2f s or level is wrong, or it clips" % n)
    w = sr // 50
    levels = [rms(x[i:i + w]) for i in range(0, len(x) - w, w)]
    mean = sum(levels) / len(levels)
    cv = math.sqrt(sum((v - mean) ** 2 for v in levels) / len(levels)) / mean if mean else 0
    if cv < 0.2:
        return fail("level barely moves (%.2f), not a creak" % cv)
    if not clean_end(x, sr):
        return fail("door.wav is cut off at the end")
    for p in glob.glob(os.path.join(d, "**", "*"), recursive=True):
        if os.path.isfile(p) and p.rsplit(".", 1)[-1].lower() in ("json", "md", "txt", "yaml", "yml", "csv") and os.path.getsize(p) < 500000:
            s = open(p, encoding="utf-8", errors="replace").read()
            if "door" in s.lower() and re.search(r"procedural|synthes|generated|script", s, re.I) and re.search(r"licen[cs]e|rights|cc0|public domain|original", s, re.I):
                return 0
    return fail("no record says how door.wav was made and under what rights (a script alone is not a record)")


def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k, v
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def load(d):
    f = os.path.join(d, "sounds.json")
    if not os.path.isfile(f):
        return None
    try:
        return json.load(open(f, encoding="utf-8"))
    except ValueError:
        return None


def entries(o):
    """The sound rows: the shallowest list of objects, or object keyed by sound, so a row's own layers never win."""
    level = [o]
    while level:
        for v in level:
            if isinstance(v, list) and len(v) >= 2 and all(isinstance(x, dict) for x in v):
                return v
            if isinstance(v, dict) and len(v) >= 2 and all(isinstance(x, dict) for x in v.values()):
                return [dict(x, id=k) for k, x in v.items()]
        level = [x for v in level for x in (v.values() if isinstance(v, dict) else v if isinstance(v, list) else [])]
    return []


EVENTS = ["jump", "land", "coin", "crate", "door.?open", "door.?close", "enemy.?hit", "enemy.?death", "menu|click", "ambien"]


def plan(d):
    o = load(d)
    if o is None:
        return fail("no parseable sounds.json")
    rows = entries(o)
    texts = [json.dumps(r).lower() for r in rows]
    missing = [e for e in EVENTS if not any(re.search(e, t) for t in texts)]
    if missing:
        return fail("no row for: " + ", ".join(missing))
    whole = json.dumps(o).lower()
    if "commercial" not in whole and "steam" not in whole:
        return fail("the plan drops that this is a commercial release, which decides what sources are allowed")
    repeated = 0
    for r in rows:
        for k, v in walk(r):
            if re.search(r"vari|takes|count|alternat", str(k), re.I) and ((isinstance(v, (int, float)) and v >= 2) or (isinstance(v, list) and len(v) >= 2)):
                repeated += 1
                break
    if repeated < 3:
        return fail("only %d sounds plan more than one variation; repeated game events need them" % repeated)
    if not all(any(re.search(r"route|source|method|licen[cs]e|origin", str(k), re.I) for k, _ in walk(r)) for r in rows):
        return fail("not every sound says where it will come from")
    return 0


def sync(d):
    o = load(d)
    if o is None:
        return fail("no parseable sounds.json")
    rows = entries(o)

    def at(value, frames):
        for r in rows:
            nums = [v for _, v in walk(r) if isinstance(v, (int, float)) and not isinstance(v, bool)]
            if any(abs(v - value) < 1e-6 or v == frames for v in nums):
                return r
        return None
    slam, glass = at(12.5, 300), at(40, 960)
    if not slam or not glass or slam is glass:
        return fail("the two hits do not each carry their time")
    if not re.search("slam|door", json.dumps(slam), re.I):
        return fail("12.5 s is not on the door slam")
    if "glass" not in json.dumps(glass).lower():
        return fail("40 s is not on the glass smash")
    if "24" not in json.dumps(o):
        return fail("the frame rate is not recorded")
    return 0


CASES = {"hit-layers": hit_layers, "bad-seam": bad_seam, "no-comfy": door, "ten-events": plan, "film-sync": sync}

if __name__ == "__main__":
    sys.exit(CASES[sys.argv[1]](sys.argv[2] if len(sys.argv) > 2 else "."))

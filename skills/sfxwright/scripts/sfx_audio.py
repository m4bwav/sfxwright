"""Audio input and output, DSP helpers and measurements for sfxwright. Standard library only.

WAV is read and written here. Any other format goes through ffmpeg when it is on PATH. Samples are floats in -1..1.
Every number printed by measure() is a heuristic reading, never a verdict. See references/thresholds.md.
"""
import array
import cmath
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


class AudioError(Exception):
    pass


class Audio:
    def __init__(self, sr, channels):
        self.sr = int(sr)
        self.channels = [c if isinstance(c, list) else list(c) for c in channels]

    @property
    def n(self):
        return len(self.channels[0]) if self.channels else 0

    @property
    def seconds(self):
        return self.n / self.sr if self.sr else 0.0

    def mono(self):
        if len(self.channels) == 1:
            return self.channels[0]
        k = 1.0 / len(self.channels)
        return [sum(s) * k for s in zip(*self.channels)]


def ffmpeg():
    return os.environ.get("SFX_FFMPEG") or shutil.which("ffmpeg")


def run_ffmpeg(args):
    exe = ffmpeg()
    if not exe:
        raise AudioError("ffmpeg not found; this step needs it (use WAV input, or install ffmpeg)")
    r = subprocess.run([exe, "-hide_banner", "-loglevel", "error", "-y"] + args, capture_output=True, text=True)
    if r.returncode:
        raise AudioError("ffmpeg failed: " + r.stderr.strip()[:400])


def _read_wav(path):
    data = Path(path).read_bytes()
    if data[:4] not in (b"RIFF", b"RF64") or data[8:12] != b"WAVE":
        raise AudioError("%s: not a WAV file" % path)
    pos, fmt, raw = 12, None, None
    while pos + 8 <= len(data):
        cid = data[pos:pos + 4]
        size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        body = data[pos + 8:pos + 8 + size]
        if cid == b"fmt ":
            fmt = body
        elif cid == b"data":
            raw = body
        pos += 8 + size + (size & 1)
    if fmt is None or raw is None:
        raise AudioError("%s: WAV is missing fmt or data" % path)
    tag, nch, sr = struct.unpack("<HHI", fmt[:8])
    bits = struct.unpack("<H", fmt[14:16])[0]
    if tag == 0xFFFE and len(fmt) >= 26:
        tag = struct.unpack("<H", fmt[24:26])[0]
    if tag == 1 and bits == 16:
        a = array.array("h")
        a.frombytes(raw[: len(raw) // 2 * 2])
        vals, scale = a, 1 / 32768.0
    elif tag == 1 and bits == 24:
        count = len(raw) // 3
        vals = [int.from_bytes(raw[i * 3:i * 3 + 3], "little", signed=True) for i in range(count)]
        scale = 1 / 8388608.0
    elif tag == 1 and bits == 32:
        a = array.array("i")
        a.frombytes(raw[: len(raw) // 4 * 4])
        vals, scale = a, 1 / 2147483648.0
    elif tag == 1 and bits == 8:
        vals, scale = [b - 128 for b in raw], 1 / 128.0
    elif tag == 3 and bits == 32:
        a = array.array("f")
        a.frombytes(raw[: len(raw) // 4 * 4])
        vals, scale = a, 1.0
    elif tag == 3 and bits == 64:
        a = array.array("d")
        a.frombytes(raw[: len(raw) // 8 * 8])
        vals, scale = a, 1.0
    else:
        raise AudioError("%s: unsupported WAV format tag %d, %d bits" % (path, tag, bits))
    if sys.byteorder == "big" and isinstance(vals, array.array):
        vals.byteswap()
    return Audio(sr, [[v * scale for v in vals[c::nch]] for c in range(nch)])


def read_audio(path):
    p = Path(path)
    if not p.is_file():
        raise AudioError("file not found: %s" % path)
    if p.suffix.lower() == ".wav":
        return _read_wav(p)
    with tempfile.TemporaryDirectory(prefix="sfx_") as d:
        tmp = Path(d) / "in.wav"
        run_ffmpeg(["-i", str(p), "-c:a", "pcm_f32le", str(tmp)])
        return _read_wav(tmp)


def write_wav(path, audio, bits=24):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    nch = len(audio.channels)
    n = audio.n
    if bits == 16:
        a = array.array("h", [0]) * (n * nch)
        for c, ch in enumerate(audio.channels):
            for i in range(n):
                a[i * nch + c] = max(-32768, min(32767, int(round(ch[i] * 32767))))
        if sys.byteorder == "big":
            a.byteswap()
        raw = a.tobytes()
    elif bits == 24:
        raw = bytearray(n * nch * 3)
        for c, ch in enumerate(audio.channels):
            for i in range(n):
                v = max(-8388608, min(8388607, int(round(ch[i] * 8388607))))
                j = (i * nch + c) * 3
                raw[j:j + 3] = (v & 0xFFFFFF).to_bytes(3, "little")
        raw = bytes(raw)
    else:
        raise AudioError("bits must be 16 or 24")
    block = nch * bits // 8
    head = b"RIFF" + struct.pack("<I", 36 + len(raw)) + b"WAVEfmt " + struct.pack(
        "<IHHIIHH", 16, 1, nch, audio.sr, audio.sr * block, block, bits) + b"data" + struct.pack("<I", len(raw))
    p.write_bytes(head + raw)
    return p


def db(x):
    return 20 * math.log10(x) if x > 1e-12 else -240.0


def undb(x):
    return 10 ** (x / 20.0)


def percentile(values, q):
    if not values:
        return 0.0
    s = sorted(values)
    return s[min(len(s) - 1, int(q * (len(s) - 1) + 0.5))]


def median(values):
    return percentile(values, 0.5)


def fft(x):
    """Radix-2 FFT of a list whose length is a power of two."""
    n = len(x)
    if n == 1:
        return [complex(x[0])]
    even, odd = fft(x[0::2]), fft(x[1::2])
    out = [0j] * n
    for k in range(n // 2):
        t = cmath.exp(-2j * math.pi * k / n) * odd[k]
        out[k], out[k + n // 2] = even[k] + t, even[k] - t
    return out


def magnitudes(frame, size=1024):
    frame = list(frame[:size]) + [0.0] * max(0, size - len(frame))
    w = [frame[i] * (0.5 - 0.5 * math.cos(2 * math.pi * i / (size - 1))) for i in range(size)]
    return [abs(c) for c in fft(w)[: size // 2 + 1]]


def spectrum_stats(mono, sr, size=1024, max_frames=40):
    """Centroid (magnitude-weighted mean Hz), 95% rolloff and flatness over frames above -40 dB of the peak."""
    peak = max((abs(v) for v in mono), default=0.0)
    if peak <= 0 or len(mono) < 32:
        return {"centroid_hz": None, "rolloff_hz": None, "flatness": None}
    gate = peak * 0.01
    hop = max(size // 2, (len(mono) - size) // max_frames if len(mono) > size else size)
    cents, rolls, flats = [], [], []
    for start in range(0, max(1, len(mono) - size // 2), hop):
        fr = mono[start:start + size]
        if max((abs(v) for v in fr), default=0.0) < gate:
            continue
        m = magnitudes(fr, size)
        total = sum(m)
        if total <= 0:
            continue
        cents.append(sum(i * v for i, v in enumerate(m)) / total * sr / size)
        acc, target = 0.0, total * 0.95
        for i, v in enumerate(m):
            acc += v
            if acc >= target:
                rolls.append(i * sr / size)
                break
        logs = sum(math.log(v + 1e-12) for v in m) / len(m)
        flats.append(math.exp(logs) / (total / len(m)))
    if not cents:
        return {"centroid_hz": None, "rolloff_hz": None, "flatness": None}
    return {"centroid_hz": round(median(cents), 1), "rolloff_hz": round(median(rolls), 1), "flatness": round(median(flats), 4)}


def envelope(mono, sr, hop_ms=2.0):
    hop = max(1, int(sr * hop_ms / 1000))
    return [max((abs(v) for v in mono[i:i + hop]), default=0.0) for i in range(0, len(mono), hop)], hop


def rms_frames(mono, size):
    out = []
    for i in range(0, max(1, len(mono) - size + 1), size):
        fr = mono[i:i + size]
        out.append(math.sqrt(sum(v * v for v in fr) / max(1, len(fr))))
    return out


def onsets(mono, sr, merge_ms=100.0):
    """Measured onset times in seconds: rise-only envelope change, moving-median threshold, merged by a minimum gap."""
    env, hop = envelope(mono, sr, 3.0)
    if len(env) < 4:
        return []
    env = [db(max(v, 1e-5)) for v in env]
    peak_db = max(env)
    win = 3
    nov = [max(0.0, env[i] - env[max(0, i - win)]) for i in range(len(env))]
    span = max(5, int(0.25 * sr / hop))
    times, last = [], -1e9
    for i in range(1, len(nov) - 1):
        lo = max(0, i - span)
        base = median(nov[lo:i + span])
        if nov[i] >= nov[i - 1] and nov[i] >= nov[i + 1] and nov[i] > base + 12 and env[i] > peak_db - 40:
            t = i * hop / sr
            if t - last >= merge_ms / 1000:
                times.append(round(max(0.0, t - win * hop / sr), 4))
                last = t
    return times


def _clip_runs(ch):
    """Longest run of identical samples at this channel's own extreme, and at digital full scale."""
    peak = max((abs(v) for v in ch), default=0.0)
    if peak <= 0:
        return 0, 0.0
    longest, run, prev = 0, 0, None
    level = peak * 0.9995
    for v in ch:
        if abs(v) >= level and prev is not None and abs(v - prev) < 1e-5:
            run += 1
            longest = max(longest, run)
        else:
            run = 1 if abs(v) >= level else 0
        prev = v
    return longest, peak


def median3(x):
    """Three-point median: removes one-sample spikes and leaves the shape of a sound."""
    out = list(x)
    for i in range(1, len(x) - 1):
        p, q, r = x[i - 1], x[i], x[i + 1]
        out[i] = max(min(p, q), min(max(p, q), r))
    return out


def click_scan(mono, sr, skip=()):
    """Isolated spikes: distance from the three-point median, against the same distance nearby, outside the given spans."""
    if len(mono) < 64:
        return {"ratio": 0.0, "at_s": None, "count": 0}
    med = median3(mono)
    res = [abs(p - q) for p, q in zip(mono, med)]
    ref = percentile(res, 0.999)
    floor = max(max(abs(v) for v in mono) * 0.002, 1e-5)
    guard = int(0.001 * sr)
    best, at, count, last = 0.0, None, 0, -sr
    for i, v in enumerate(res):
        if v < max(ref, floor) or any(a <= i <= b for a, b in skip):
            continue
        near = res[max(0, i - 3 * guard):max(0, i - guard)] + res[i + guard:i + 3 * guard]
        r = v / max(percentile(near, 0.9) if near else 0.0, floor)
        if r > best:
            best, at = r, i / sr
        if r > 20 and i - last > guard:
            count += 1
            last = i
    return {"ratio": round(best, 2), "at_s": None if at is None else round(at, 4), "count": count}


def seam_ratio(audio):
    """Loop seam: the jump from the last sample to the first, over the 99th percentile step. About 1 is smooth."""
    worst = 0.0
    for ch in audio.channels:
        if len(ch) < 16:
            continue
        steps = [abs(ch[i + 1] - ch[i]) for i in range(0, len(ch) - 1)]
        ref = percentile(steps, 0.99) or 1e-9
        worst = max(worst, abs(ch[0] - ch[-1]) / ref)
    return round(worst, 2)


def measure(audio):
    """One dictionary of readings for a file. Pure measurement; flags are added by flag()."""
    mono = audio.mono()
    sr = audio.sr
    r = {"seconds": round(audio.seconds, 4), "sr": sr, "channels": len(audio.channels)}
    peaks = [max((abs(v) for v in c), default=0.0) for c in audio.channels]
    peak = max(peaks, default=0.0)
    r["peak_db"] = round(db(peak), 2)
    if peak <= 1e-6:
        r["silent"] = True
        return r
    r["rms_db"] = round(db(math.sqrt(sum(v * v for v in mono) / len(mono))), 2)
    r["dc_db"] = round(max(db(abs(sum(c) / len(c))) for c in audio.channels), 1)
    # An end reads its last sample, or a quarter of its last step so a cut on a zero crossing still shows. A fade reaches zero smoothly.
    r["first_db"] = round(max(db(max(abs(c[0]), abs(c[1] - c[0]) * 0.25)) for c in audio.channels), 1)
    r["last_db"] = round(max(db(max(abs(c[-1]), abs(c[-1] - c[-2]) * 0.25)) for c in audio.channels), 1)
    env, hop = envelope(median3(mono), sr, 2.0)  # so a click cannot pose as the peak and hide inside the attack window
    epeak = max(env)
    ipeak = env.index(epeak)
    r["peak_s"] = round(ipeak * hop / sr, 4)
    first = next(i for i, v in enumerate(env) if v >= epeak * 0.01)
    r["lead_silence_s"] = round(first * hop / sr, 4)
    j = ipeak
    while j > 0 and env[j - 1] >= epeak * 0.1:
        j -= 1
    r["attack_ms"] = round((ipeak - j) * hop / sr * 1000, 1)
    frames = rms_frames(mono[ipeak * hop:], max(1, int(0.05 * sr)))
    floor = percentile(frames, 0.05) if len(frames) >= 4 else 0.0
    r["floor_db"] = round(db(floor), 1)
    # A floor is steady: at least 200 ms of frames within 3 dB of it, well under the peak.
    near = sum(1 for v in frames if floor > 0 and abs(db(max(v, 1e-9)) - db(floor)) <= 3)
    r["floor_steady"] = bool(floor > 0 and near * 0.05 >= 0.2 and db(epeak) - db(floor) >= 20)
    limit = max(epeak * 0.001, floor * 2)
    last = len(env) - 1
    while last > ipeak and env[last] < limit:
        last -= 1
    r["tail_s"] = round((last - ipeak) * hop / sr, 4)
    end = len(env) - 1
    while end > first and env[end] < epeak * 0.003:
        end -= 1
    r["sound_s"] = round((end - first + 1) * hop / sr, 4)
    r["end_silence_s"] = round(max(0.0, audio.seconds - (end + 1) * hop / sr), 4)
    runs = [_clip_runs(c) for c in audio.channels]
    r["flat_run"] = max(x[0] for x in runs)
    skip_end = (ipeak + 3) * hop
    r["click"] = click_scan(mono, sr, skip=[(max(0, j * hop - hop), skip_end)])
    r["onsets"] = len(onsets(mono, sr))
    r.update(spectrum_stats(mono, sr))
    return r


# Starting thresholds, calibrated as references/thresholds.md says.
LIMITS = {"dc_db": -60.0, "head_db": -50.0, "tail_db": -60.0, "click": 20.0, "floor_db": -60.0, "flat_run": 4,
          "lead_s": 0.05, "end_s": 0.25, "seam": 5.0}


def flag(m, want_seconds=None, waive=(), loop=False, seam=None):
    """Turn readings into named flags. A flag means listen; it is not a verdict."""
    if m.get("silent"):
        return ["SILENT"]
    f = []
    if m["flat_run"] >= LIMITS["flat_run"]:
        f.append("CLIP")
    if m["dc_db"] > LIMITS["dc_db"]:
        f.append("DC")
    if not loop:
        if m["first_db"] > LIMITS["head_db"]:
            f.append("CUT_HEAD")
        if m["last_db"] > LIMITS["tail_db"]:
            f.append("CUT_TAIL")
        if m["lead_silence_s"] > LIMITS["lead_s"]:
            f.append("LEAD_SILENCE")
        if m["end_silence_s"] > LIMITS["end_s"]:
            f.append("END_SILENCE")
    if m["click"]["ratio"] > LIMITS["click"] and m["click"]["count"]:
        f.append("CLICK")
    if m["floor_db"] > LIMITS["floor_db"] and m["floor_steady"] and not loop:
        f.append("NOISE_FLOOR")
    if m["peak_db"] > -0.1:
        f.append("NO_HEADROOM")
    if want_seconds and abs(m["sound_s"] - want_seconds) > max(0.25 * want_seconds, 0.05):
        f.append("LENGTH")
    if loop and seam is not None and seam > LIMITS["seam"]:
        f.append("SEAM")
    return [x for x in f if x not in waive]

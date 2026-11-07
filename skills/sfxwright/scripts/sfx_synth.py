"""Procedural sound recipes for sfxwright. Standard library only, deterministic for a seed, no model and no licence question.

The physical models follow published descriptions (Cook, Real Sound Synthesis; Farnell, Designing Sound), written fresh
from notes; no patches are ported. Retro recipes are a small original take on the sfxr idea. How good each one sounds
is for a blind listen to decide: see references/routes.md.
"""
import math
import random


def _lp(x, hz, sr):
    a = 1 - math.exp(-2 * math.pi * hz / sr)
    y, out = 0.0, []
    for v in x:
        y += a * (v - y)
        out.append(y)
    return out


def _hp(x, hz, sr):
    return [a - b for a, b in zip(x, _lp(x, hz, sr))]


def _bp(x, hz, q, sr):
    """Two-pole band-pass (RBJ constant peak gain)."""
    w = 2 * math.pi * min(hz, sr * 0.45) / sr
    al = math.sin(w) / (2 * q)
    a0 = 1 + al
    b0, b2, a1, a2 = al / a0, -al / a0, -2 * math.cos(w) / a0, (1 - al) / a0
    x1 = x2 = y1 = y2 = 0.0
    out = []
    for v in x:
        y = b0 * v + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, v, y1, y
        out.append(y)
    return out


def _noise(n, rng):
    return [rng.uniform(-1, 1) for _ in range(n)]


def _mix(n, *parts):
    out = [0.0] * n
    for gain, start, p in parts:
        for i, v in enumerate(p):
            j = i + start
            if j >= n:
                break
            out[j] += gain * v
    return out


def _resonator(x, hz, t60, sr):
    r = 10 ** (-3 / (t60 * sr))
    c1, c2 = 2 * r * math.cos(2 * math.pi * min(hz, sr * 0.45) / sr), r * r
    y1 = y2 = 0.0
    out = []
    for v in x:
        y = c1 * y1 - c2 * y2 + v
        y2, y1 = y1, y
        out.append(y)
    return out


def _finish(x, sr, peak=0.7, fade_ms=8.0, attack_ms=0.5):
    """Remove DC, fade to exact zero at both ends, set the peak."""
    if not x:
        return x
    mean = sum(x) / len(x)
    x = [v - mean for v in x]
    x = _trim_silence(x, sr)
    a, f = max(1, int(attack_ms * sr / 1000)), max(1, int(fade_ms * sr / 1000))
    n = len(x)
    for i in range(min(a, n)):
        x[i] *= i / a
    for i in range(min(f, n)):
        x[n - 1 - i] *= i / f
    top = max(abs(v) for v in x) or 1.0
    return [v * peak / top for v in x]


def _trim_silence(x, sr):
    top = max((abs(v) for v in x), default=0.0)
    end = len(x)
    while end > 1 and abs(x[end - 1]) < top * 0.001:
        end -= 1
    return x[:min(len(x), end + int(0.002 * sr))]


def shaker(sr, rng, seconds=0.6, beans=64, res=3200.0, pole=0.96, shakes=1, sound_decay=0.95, system_decay=0.999):
    """Particle collisions through one resonance: gravel, scrapes, ice, maracas (after Cook's PhISEM model)."""
    n = int(seconds * sr)
    k = sr / 22050.0
    sd, syd = sound_decay ** (1 / k), system_decay ** (1 / k)
    gain = math.log(max(beans, 2)) / math.log(4) * 40 / max(beans, 1) / 32768
    c0, c1 = -pole * 2 * math.cos(2 * math.pi * res / sr), pole * pole
    period = max(1, n // max(shakes, 1))
    prob = beans / 1024.0 / k
    tt, e, l, y1, y2 = 7.0, 0.0, 0.0, 0.0, 0.0
    out = []
    for i in range(n):
        if i % period == 0:
            tt = 0.0
        if tt < 2 * math.pi:
            tt += 2 * math.pi / sr / 0.05
            e += (1 - math.cos(tt)) * 200 / k
        e *= syd
        if rng.random() < prob:
            l += gain * e
        x = l * rng.uniform(-1, 1)
        l *= sd
        x -= y1 * c0 + y2 * c1
        y2, y1 = y1, x
        out.append(y1 - y2)
    return _finish(out, sr)


MATERIALS = {
    "wood": ((180, 0.05), (440, 0.04), (930, 0.025), (1720, 0.015)),
    "metal": ((610, 0.9), (1480, 0.7), (2730, 0.5), (4310, 0.35), (6230, 0.2), (8150, 0.12)),
    "glass": ((1240, 0.35), (2960, 0.25), (5170, 0.15), (7900, 0.08)),
    "stone": ((300, 0.03), (830, 0.02), (2100, 0.012), (4200, 0.008)),
    "plastic": ((520, 0.03), (1340, 0.025), (2850, 0.012)),
}


def modal(sr, rng, material="wood", hardness=0.6, size=1.0, seconds=None):
    """A struck object: a sum of decaying resonances excited by a short noisy pulse."""
    modes = MATERIALS.get(material)
    if not modes:
        raise ValueError("material must be one of " + ", ".join(sorted(MATERIALS)))
    longest = max(t for _, t in modes)
    seconds = seconds or min(3.0, longest * 7 * size + 0.05)
    n = int(seconds * sr)
    pulse_len = max(4, int(sr * (0.0005 + 0.004 * (1 - hardness))))
    pulse = [math.sin(math.pi * i / pulse_len) ** 2 for i in range(pulse_len)]
    exc = [p * (0.6 + 0.4 * rng.uniform(-1, 1)) for p in pulse] + [0.0] * (n - pulse_len)
    exc = _lp(exc, 800 + 14000 * hardness, sr)
    parts = []
    for i, (f, t) in enumerate(modes):
        hz = f / size * rng.uniform(0.985, 1.015)
        res = _resonator(exc, hz, t * size * rng.uniform(0.9, 1.1), sr)
        top = max(abs(v) for v in res) or 1.0
        parts.append((rng.uniform(0.6, 1.0) / (i + 1) ** (1.3 - hardness * 0.8) / top, 0, res))
    return _finish(_mix(n, *parts), sr, attack_ms=0.05)


SURFACES = {
    "gravel": dict(beans=420, res=5200, pole=0.9, body="stone", grit=1.0),
    "wood": dict(beans=24, res=1500, pole=0.92, body="wood", grit=0.25),
    "stone": dict(beans=30, res=3100, pole=0.88, body="stone", grit=0.3),
    "metal": dict(beans=20, res=3800, pole=0.97, body="metal", grit=0.2),
    "grass": dict(beans=300, res=4300, pole=0.75, body=None, grit=1.0),
    "snow": dict(beans=500, res=2100, pole=0.8, body=None, grit=1.0),
}


def footstep(sr, rng, surface="gravel", weight=0.6, state="walk"):
    """One step: heel, then ball, as three force pulses (heel, outstep, ball) driving a surface texture and a body thud."""
    s = SURFACES.get(surface)
    if not s:
        raise ValueError("surface must be one of " + ", ".join(sorted(SURFACES)))
    seconds = {"walk": 0.42, "run": 0.24, "sneak": 0.6}.get(state, 0.42)
    n = int(seconds * sr)
    w = {"walk": (1.0, 0.55, 0.75), "run": (0.5, 0.5, 1.0), "sneak": (0.4, 0.5, 0.35)}.get(state, (1.0, 0.55, 0.75))

    def pulse(x):
        return abs(1.5 * (1 - x) * 3.3333 * (x ** 3 - x)) if 0 <= x <= 1 else 0.0
    force = [0.0] * n
    for wt, start, width in ((w[0], 0.0, 0.32), (w[1], 0.16, 0.42), (w[2], 0.36, 0.4)):
        for i in range(n):
            x = (i / n - start) / width
            force[i] += wt * pulse(x)
    k = sr / 22050.0
    c0 = -s["pole"] * 2 * math.cos(2 * math.pi * s["res"] * rng.uniform(0.9, 1.1) / sr)
    c1 = s["pole"] ** 2
    prob = s["beans"] / 1024.0 / k
    l, y1, y2 = 0.0, 0.0, 0.0
    sd = 0.93 ** (1 / k)
    tex = []
    for i in range(n):
        if rng.random() < prob * force[i]:
            l += force[i] * rng.uniform(0.4, 1.0)
        x = l * rng.uniform(-1, 1)
        l *= sd
        x -= y1 * c0 + y2 * c1
        y2, y1 = y1, x
        tex.append(y1 - y2)
    top = max(abs(v) for v in tex) or 1.0
    tex = [v / top for v in tex]
    thump = _lp([force[i] * rng.uniform(-1, 1) for i in range(n)], 120 + 120 * (1 - weight), sr)
    top = max(abs(v) for v in thump) or 1.0
    parts = [(s["grit"], 0, tex), (0.3 + 0.8 * weight, 0, [v / top for v in thump])]
    if s["body"]:
        parts.append((0.7, 0, modal(sr, rng, s["body"], hardness=0.35, size=1.2 + weight, seconds=seconds)))
    return _finish(_mix(n, *parts), sr)


def click(sr, rng, hz=5000.0, q=12.0, decay_ms=20.0):
    n = int((decay_ms * 3 + 2) / 1000 * sr)
    d = decay_ms / 1000 * sr
    x = [rng.uniform(-1, 1) * min(1.0, i / max(1, 0.001 * sr)) * math.exp(-i / (d / 2.2)) for i in range(n)]
    return _finish(_bp(x, hz, q, sr), sr, attack_ms=0.2)


def switch(sr, rng, kind="plastic"):
    """A panel switch: low clicks read as plastic and come first, high clicks read as metal and follow about 10 ms later."""
    n = int(0.09 * sr)
    gap = int(0.01 * sr)
    parts = [(1.0, 0, click(sr, rng, 3000 * rng.uniform(0.95, 1.05))), (0.8, int(0.002 * sr), click(sr, rng, 4000 * rng.uniform(0.95, 1.05))),
             (0.6, gap, click(sr, rng, 5000 * rng.uniform(0.95, 1.05))), (0.45 if kind == "plastic" else 0.9, gap + int(0.002 * sr), click(sr, rng, 7000 * rng.uniform(0.95, 1.05)))]
    x = _mix(n, *parts)
    # Short low-passed feedback delay as the body of the case.
    d = int(0.0035 * sr)
    y = 0.0
    for i in range(d, n):
        y += 0.3 * (x[i - d] - y)
        x[i] += 0.45 * y
    return _finish(x, sr, attack_ms=0.1)


def beep(sr, rng, hz=800.0, seconds=0.12, second_hz=None):
    n = int(seconds * sr)
    tones = [hz] if not second_hz else [hz, second_hz]
    each = n // len(tones)
    x = []
    phase = 0.0
    for f in tones:
        for i in range(each):
            phase += 2 * math.pi * f / sr
            ramp = min(1.0, i / (0.003 * sr), (each - i) / (0.003 * sr))
            x.append(math.sin(phase) * ramp)
    return _finish(x, sr, fade_ms=3)


def wind(sr, rng, seconds=8.0, strength=0.5, gentle=False):
    """Wind from a slow speed curve, with a background band and two whistles reading that curve at different delays."""
    n = int(seconds * sr)
    g = _lp(_noise(n, rng), 0.5, sr)
    s = _lp(_noise(n, rng), 3.0, sr)
    speed = []
    for i in range(n):
        base = (math.sin(2 * math.pi * i / sr / max(seconds, 10.0)) + 1) * 0.25 * strength + strength * 0.25
        gust = g[i] * 50 * ((base + 0.5) ** 2 - 0.125) * 0.12
        squall = 0.0 if gentle else s[i] * 50 * (8 * (max(base, 0.4) - 0.4)) ** 2 * 0.04
        speed.append(max(0.0, min(1.0, base + gust + squall)))
    bed = _bp(_noise(n, rng), 800, 0.6, sr)
    bed = [v * (speed[i] + 0.2) for i, v in enumerate(bed)]
    out = [1.0 * v for v in bed]
    for (lo, hi, delay, lev) in ((600, 1000, 0.1, 0.5), (1000, 2000, 1.0, 0.3)):
        if gentle:
            lev *= 0.25
        src = _noise(n, rng)
        y1 = y2 = 0.0
        d = int(delay * sr)
        for i in range(n):
            sp = speed[max(0, i - d)]
            f = lo + (hi - lo) * sp
            r = 0.998
            c1 = 2 * r * math.cos(2 * math.pi * f / sr)
            y = c1 * y1 - r * r * y2 + src[i] * 0.004
            y2, y1 = y1, y
            out[i] += lev * y * (sp + 0.12) ** 2
    if gentle:
        out = _lp(out, 2600, sr)
    return _finish(out, sr, fade_ms=200, attack_ms=200)


def fire(sr, rng, seconds=6.0, crackle=9.0):
    """Hiss, lapping and crackle events (after Farnell's fire breakdown)."""
    n = int(seconds * sr)
    w = _noise(n, rng)
    mod = _lp(_noise(n, rng), 40, sr)
    top = max(abs(v) for v in mod) or 1.0
    hiss = _hp([w[i] * (2 * mod[i] / top) ** 4 for i in range(n)], 1000, sr)
    lap = _bp(_lp(_noise(n, rng), 160, sr), 60, 1.2, sr)
    top = max(abs(v) for v in lap) or 1.0
    lap = [max(-0.8, min(0.8, 1.6 * v / top)) for v in lap]
    events = []
    t = 0.0
    while t < seconds:
        t += rng.expovariate(crackle)
        size = int(sr * rng.uniform(0.004, 0.03))
        hz = math.exp(rng.uniform(math.log(600), math.log(9000)))
        burst = [rng.uniform(-1, 1) * (1 - i / size) ** 2 for i in range(size)]
        events.append((rng.uniform(0.2, 1.0) ** 2, int(t * sr), _bp(burst, hz, 2.5, sr)))
    top = 1.0
    crack = _mix(n, *events)
    tc = max(abs(v) for v in crack) or top
    th = max(abs(v) for v in hiss) or top
    return _finish([0.25 * hiss[i] / th + 0.55 * lap[i] + 0.5 * crack[i] / tc for i in range(n)], sr, fade_ms=120, attack_ms=60)


def explosion(sr, rng, seconds=3.5, distance=0.0):
    """Shock, three falling blasts and a low fireball (after Farnell's breakdown). Add debris as separate layers."""
    n = int(seconds * sr)
    shock_n = int(0.012 * sr)
    phase = 0.0
    shock = []
    for i in range(shock_n):
        r = 1 - i / shock_n
        phase += 2 * math.pi * 1000 * r * r / sr
        shock.append(math.sin(phase) * r)
    parts = [(1.0 * (1 - distance), 0, shock)]
    at = int(0.002 * sr)
    for j, (hz, q) in enumerate(((7000, 1.5), (3500, 2.5), (1500, 5.0))):
        size = int(0.03 * sr)
        b = [rng.uniform(-1, 1) * (1 - i / size) for i in range(size)]
        b = _bp(b, hz * (1 - 0.7 * distance), q, sr)
        top = max(abs(v) for v in b) or 1.0
        parts.append((0.9 * (1 - 0.5 * distance) / (j + 1), at, [max(-1, min(1, 2.2 * v / top)) for v in b]))
        at += int(rng.uniform(0.005, 0.03) * sr)
    raw = _noise(n, rng)
    ball = []
    y = 0.0
    rise = 0.1 * sr
    for i in range(n):
        x = i / n
        hz = 40 + 100 * (1 - abs(2 * x - 1)) if x < 0.5 else 140 - 100 * (x - 0.5) * 2
        y += (1 - math.exp(-2 * math.pi * hz / sr)) * (raw[i] - y)
        lev = min(1.0, i / rise) * (1 - x) ** 4
        ball.append(max(-1.0, min(1.0, y * lev * 22)))
    parts.append((0.95, int(0.004 * sr), _hp(ball, 18, sr)))
    return _finish(_mix(n, *parts), sr, fade_ms=60, attack_ms=0.02)


def whoosh(sr, rng, seconds=0.8, lo=300.0, hi=4200.0, q=1.2):
    """Filtered noise with a band sweeping up and back, loudest at the pass."""
    n = int(seconds * sr)
    x = _noise(n, rng)
    y1 = y2 = 0.0
    out = []
    for i in range(n):
        t = i / n
        shape = math.sin(math.pi * t) ** 2
        f = lo + (hi - lo) * shape
        w = 2 * math.pi * f / sr
        al = math.sin(w) / (2 * q)
        y = (al * x[i] + 2 * math.cos(w) * y1 - (1 - al) * y2) / (1 + al)
        y2, y1 = y1, y
        out.append(y * shape)
    return _finish(out, sr, fade_ms=20, attack_ms=10)


def creak(sr, rng, seconds=1.2, hz=420.0):
    """Stick-slip: impulses with a shrinking gap, then a pitched pulse train, through a few wood modes."""
    n = int(seconds * sr)
    x = [0.0] * n
    t = 0.0
    gap = 0.05
    while t < seconds:
        i = int(t * sr)
        if i < n:
            x[i] = rng.uniform(0.5, 1.0) * rng.choice((-1, 1))
        prog = t / seconds
        gap = max(1.0 / hz, 0.05 * (1 - prog) ** 2 + 1.0 / hz) * rng.uniform(0.85, 1.15)
        t += gap
    parts = [(1.0, 0, _resonator(x, f, tt, sr)) for f, tt in ((hz, 0.03), (hz * 2.7, 0.02), (hz * 5.1, 0.012))]
    return _finish(_mix(n, *parts), sr, fade_ms=30, attack_ms=1)


def _retro(sr, rng, seconds, f0, f1, duty=0.5, vib=0.0, noise=False, punch=0.0, steps=None):
    n = int(seconds * sr)
    phase = 0.0
    hold = 0
    val = 0.0
    x = []
    for i in range(n):
        t = i / n
        f = f0 * (f1 / f0) ** t if steps is None else steps[min(len(steps) - 1, int(t * len(steps)))]
        if vib:
            f *= 1 + vib * math.sin(2 * math.pi * 14 * i / sr)
        phase += f / sr
        if noise:
            hold += 1
            if hold >= max(1, int(sr / max(f, 1) / 2)):
                val, hold = rng.choice((-1.0, 1.0)), 0
            s = val
        else:
            s = 1.0 if (phase % 1.0) < duty else -1.0
        env = min(1.0, (1 + punch * math.exp(-t * 20)) * (1 - t) ** 1.5)
        x.append(s * env)
    return _finish(_lp(x, 9000, sr), sr, fade_ms=3, attack_ms=0.3)


def retro(sr, rng, kind="coin"):
    """Chip-style sounds. Pick a seed for a new variation."""
    u = rng.uniform
    if kind == "coin":
        a = u(900, 1300)
        return _retro(sr, rng, u(0.22, 0.32), a, a, duty=0.5, steps=[a, a * u(1.3, 1.5)])
    if kind == "laser":
        return _retro(sr, rng, u(0.12, 0.28), u(1000, 2200), u(120, 300), duty=u(0.15, 0.5))
    if kind == "jump":
        return _retro(sr, rng, u(0.15, 0.28), u(180, 320), u(500, 900), duty=u(0.25, 0.5))
    if kind == "hit":
        return _retro(sr, rng, u(0.08, 0.18), u(1800, 3500), u(150, 400), noise=True, punch=0.5)
    if kind == "explode":
        return _retro(sr, rng, u(0.35, 0.7), u(1200, 2400), u(60, 140), noise=True, punch=0.8)
    if kind == "powerup":
        a = u(300, 500)
        return _retro(sr, rng, u(0.35, 0.55), a, a, duty=0.5, steps=[a * 2 ** (k / 12) for k in (0, 4, 7, 12, 16, 19)])
    if kind == "blip":
        a = u(500, 1200)
        return _retro(sr, rng, u(0.05, 0.09), a, a, duty=u(0.25, 0.5))
    raise ValueError("retro kind must be coin, laser, jump, hit, explode, powerup or blip")


RECIPES = {"shaker": shaker, "modal": modal, "footstep": footstep, "click": click, "switch": switch, "beep": beep, "wind": wind,
           "fire": fire, "explosion": explosion, "whoosh": whoosh, "creak": creak, "retro": retro}


def render(name, sr=44100, seed=1, **params):
    if name not in RECIPES:
        raise ValueError("unknown recipe %s; have %s" % (name, ", ".join(sorted(RECIPES))))
    rng = random.Random("%s:%s" % (name, seed))
    return RECIPES[name](sr, rng, **params)

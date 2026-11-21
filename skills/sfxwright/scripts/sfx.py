#!/usr/bin/env python3
"""sfxwright CLI: plan, make, edit, check, finish and document sound effects.

Standard-library Python 3.9+. ffmpeg is needed only for non-WAV input, stretch, convolve and lossy delivery. ComfyUI is
needed only for `gen`; without it, `gen --workflow-out` writes the workflow to hand over, and `synth` still works.

  doctor    what is installed and reachable, and which routes that allows
  init      start a project's sounds.json          add      add a sound to the list
  validate  check the list against the format      status   one line per sound
  plan      variation matrix: axes to file counts, with cheaper shapes side by side
  synth     render a procedural recipe             gen      render through a reachable ComfyUI
  library   record the source and licence of a found or recorded file
  register  attach files and their provenance to a sound in the list
  check     per-file readings and flags            set      one variation set: duplicates, outliers, level
  timing    a sequence: are the hits too evenly spaced or too alike
  degrade   plant a known fault, to test the checks
  edit      trim, fade, gain, pitch, stretch, reverse, convolve, dc, tidy, softclip
  layer     stack parts with offsets, aligned on their peaks
  vary      a variation set from one or more sources
  sequence  place single hits into a walk or run with uneven timing
  loop      make a seamless loop and score the seam
  place     lay sounds on a timeline by their sync points and report frame errors
  scene     move sources through a room by a plan: pan, distance, reverb send (stereo)
  avsync    sound against picture: audio onsets vs video motion, lag and match rate (needs ffmpeg)
  record-sheet  a recording plan for the sounds someone will record
  finish    level and format per destination       name     build or test a file name
  sheet     waveform PNG for looking               review   one clip to listen to, with times
  doc       cue sheet, implementation sheet or credits, from the list
  ship      can this project ship these sounds?    budget   disk and memory estimate per category
"""
import argparse
import csv
import datetime
import hashlib
import io
import itertools
import json
import math
import os
import random
import re
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sfx_audio as A  # noqa: E402
import sfx_synth as S  # noqa: E402

VERSION = "0.2.3"
SCHEMA = 1
KINDS = ("one-shot", "loop", "ambience", "sequence", "stinger", "ui")
STATUSES = ("planned", "rendered", "picked", "finished", "rejected")
SIDE = ".sfx.json"

# What a source lets a project do. commercial: True, False or None for "read the terms first". edit: derivatives allowed.
LICENCES = {
    "own": dict(commercial=True, edit=True, resale=True, note=""),
    "procedural": dict(commercial=True, edit=True, resale=True, note=""),
    "cc0": dict(commercial=True, edit=True, resale=True, note=""),
    "cc-by": dict(commercial=True, edit=True, resale=True, attribution=True, note="credit the author"),
    "cc-by-sa": dict(commercial=True, edit=True, resale=True, attribution=True, note="credit the author; derivatives share alike"),
    "cc-sampling+": dict(commercial=None, edit=True, attribution=True, note="retired licence; read the deed for this file"),
    "cc-by-nc": dict(commercial=False, edit=True, attribution=True, note="no commercial use"),
    "cc-by-nc-sa": dict(commercial=False, edit=True, attribution=True, note="no commercial use"),
    "cc-by-nd": dict(commercial=True, edit=False, attribution=True, note="no derivatives: use unaltered"),
    "cc-by-nc-nd": dict(commercial=False, edit=False, attribution=True, note="no commercial use, no derivatives"),
    "stability-community": dict(commercial=True, edit=True, resale=None, note="register with Stability for business use; ends above USD 1M yearly revenue with affiliates"),
    "elevenlabs-paid": dict(commercial=True, edit=True, resale=None, note="paid plan; read the terms before selling sounds as a pack"),
    "elevenlabs-free": dict(commercial=False, edit=True, note="the use policy bars commercial use on a free plan"),
    "sonniss-gdc": dict(commercial=True, edit=True, resale=False, no_ai_training=True, note="no redistribution as sound effects; no AI training"),
    "commercial-library": dict(commercial=None, edit=True, resale=False, no_ai_training=True, note="read this pack's EULA; many bar AI training"),
    "research-only": dict(commercial=False, edit=True, note="weights are non-commercial"),
    "unknown": dict(commercial=None, edit=None, note="no known licence"),
}
MODELS = {  # checkpoint name fragment: (family, licence, steps, cfg, sampler, scheduler)
    "stable_audio_3_medium_base": ("sa3", "stability-community", 50, 7.0, "lcm", "simple"),
    "stable_audio_3_small_sfx_base": ("sa3", "stability-community", 50, 7.0, "lcm", "simple"),
    "stable_audio_3_medium": ("sa3", "stability-community", 8, 1.0, "lcm", "simple"),
    "stable_audio_3_small_sfx": ("sa3", "stability-community", 8, 1.0, "lcm", "simple"),
    "stable_audio_open": ("sao", "stability-community", 50, 4.98, "dpmpp_3m_sde_gpu", "exponential"),
}
DESTS = {  # peak ceiling dBFS, sample rate, format; file-level peak references, not delivery specs
    "game-sfx": (-3.0, 48000, "wav"), "game-foley": (-12.0, 48000, "wav"), "game-ambience": (-14.0, 48000, "ogg"),
    "unity": (-3.0, 48000, "wav"), "roblox": (-3.0, 48000, "ogg"), "film": (-1.0, 48000, "wav"),
    "web": (-3.0, 44100, "ogg"), "library": (-1.0, 96000, "wav"),
}


class Fail(Exception):
    pass


def out(obj, as_json=True):
    print(json.dumps(obj, ensure_ascii=True) if as_json else obj)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def today():
    return datetime.date.today().isoformat()


def side_path(path):
    return Path(str(path) + SIDE)


def read_side(path):
    p = side_path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def write_side(path, source, processing=None, parents=None):
    rec = {"file": Path(path).name, "sha256": sha(path), "source": source, "processing": processing or [], "parents": parents or []}
    side_path(path).write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return rec


def derive(out_path, in_paths, step):
    """Sidecar for an edit: carries every parent's source forward and appends the step, so provenance survives edits."""
    sides = [read_side(p) or {"source": {"type": "unknown", "licence": "unknown"}, "processing": [], "file": Path(p).name} for p in in_paths]
    sources = []
    for s in sides:
        items = s["source"] if isinstance(s["source"], list) else [s["source"]]
        for it in items:
            if it not in sources:
                sources.append(it)
    proc = [x for s in sides for x in s.get("processing", [])] + [step]
    return write_side(out_path, sources[0] if len(sources) == 1 else sources, proc, [s.get("file") for s in sides])


def sources_of(side):
    if not side:
        return [{"type": "unknown", "licence": "unknown"}]
    s = side.get("source")
    return s if isinstance(s, list) else [s]


def guard_edit(paths, override=False):
    for p in paths:
        for src in sources_of(read_side(p)):
            lic = LICENCES.get(src.get("licence", "unknown"), LICENCES["unknown"])
            if lic.get("edit") is False and not override:
                raise Fail("%s: licence %s forbids derivatives; use it unaltered or pass --override-licence with a reason" % (p, src.get("licence")))


# ---- the sound list ----

def load_list(path):
    p = Path(path)
    if not p.is_file():
        raise Fail("no sound list at %s; run: sfx.py init %s" % (path, path))
    d = json.loads(p.read_text(encoding="utf-8"))
    if d.get("schema") != SCHEMA:
        raise Fail("%s has schema %s; this script reads %s" % (path, d.get("schema"), SCHEMA))
    return d


def save_list(path, d):
    Path(path).write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def find_sound(d, sid):
    for s in d["sounds"]:
        if s["id"] == sid:
            return s
    raise Fail("no sound %s in the list" % sid)


def validate(d):
    errs = []
    if d.get("use") not in ("game", "film", "video", "app", "library", "other"):
        errs.append("use must be game, film, video, app, library or other")
    if not isinstance(d.get("commercial"), bool):
        errs.append("commercial must be true or false: it decides which sources are allowed")
    seen = set()
    for s in d.get("sounds", []):
        sid = s.get("id", "?")
        if sid in seen:
            errs.append("%s: duplicate id" % sid)
        seen.add(sid)
        for k in ("id", "event", "kind", "variations", "length_s", "format", "route", "status"):
            if s.get(k) in (None, ""):
                errs.append("%s: missing %s" % (sid, k))
        if s.get("kind") not in KINDS:
            errs.append("%s: kind must be one of %s" % (sid, ", ".join(KINDS)))
        if s.get("status") not in STATUSES:
            errs.append("%s: status must be one of %s" % (sid, ", ".join(STATUSES)))
        if s.get("status") in ("picked", "finished") and not s.get("takes"):
            errs.append("%s: %s but no takes registered" % (sid, s.get("status")))
        for t in s.get("takes", []):
            if not t.get("source"):
                errs.append("%s: take %s has no source" % (sid, t.get("file")))
    return errs


def cmd_init(a):
    p = Path(a.list)
    if p.exists() and not a.force:
        raise Fail("%s exists; pass --force to replace it" % p)
    p.parent.mkdir(parents=True, exist_ok=True)
    save_list(p, {"schema": SCHEMA, "project": a.project, "use": a.use, "commercial": a.commercial == "yes", "frame_rate": a.frame_rate,
                  "style": a.style or "", "created": today(), "sounds": []})
    return {"ok": True, "list": str(p)}


def cmd_add(a):
    d = load_list(a.list)
    if any(s["id"] == a.id for s in d["sounds"]):
        raise Fail("%s is already in the list" % a.id)
    s = {"id": a.id, "event": a.event, "kind": a.kind, "category": a.category or "", "brief": a.brief or "", "layers": [{"role": r} for r in (a.layers or "").split(",") if r],
         "variations": a.variations, "length_s": a.length, "loudness": a.loudness or "", "format": a.format, "route": a.route, "status": "planned", "takes": []}
    for k, v in (("sync_point_s", a.sync_point), ("at_s", a.at), ("trigger", a.trigger), ("priority", a.priority), ("max_instances", a.max_instances), ("spatial", a.spatial), ("sync_class", a.sync_class), ("role", a.role), ("gain_db", a.gain)):
        if v is not None:
            s[k] = v
    r = {}
    for k, v in (("pitch", a.pitch_range), ("volume_db", a.volume_range_db)):
        if v is not None:
            r[k] = v
    if a.no_repeat:
        r["no_repeat"] = True
    if r:
        s["randomize"] = r
    pb = {}
    for k, v in (("distance", a.dist), ("max_voices", a.max_voices), ("interval_s", a.interval), ("attack_s", a.attack), ("release_s", a.release)):
        if v is not None:
            pb[k] = v
    if a.mute_paused:
        pb["mute_paused"] = True
    if pb:
        s["playback"] = pb
    d["sounds"].append(s)
    save_list(a.list, d)
    return {"ok": True, "id": a.id, "count": len(d["sounds"])}


def _span(text):
    """'0.9-1.1' or '-2-0' -> (lo, hi); None when unparseable."""
    m = re.match(r"^ *(-?[0-9.]+) *- *(-?[0-9.]+) *$", str(text))
    try:
        return (float(m.group(1)), float(m.group(2))) if m else None
    except ValueError:
        return None


def playback_warnings(d):
    """Runtime playback contract checks: warnings, never errors."""
    out = []
    for s in d.get("sounds", []):
        sid, r, pb = s.get("id"), s.get("randomize", {}), s.get("playback", {})
        if (s.get("variations") or 1) > 1 and not r.get("no_repeat"):
            out.append("NO_REPEAT_RULE: %s has %s variations and no --no-repeat" % (sid, s.get("variations")))
        if s.get("spatial") == "3D" and "distance" not in pb:
            out.append("NO_DISTANCE: %s is 3D with no --dist min-max" % sid)
        if s.get("kind") in ("loop", "ambience") and "max_voices" not in pb and s.get("max_instances") is None:
            out.append("NO_VOICE_CAP: %s is a %s with no --max-voices" % (sid, s.get("kind")))
        for name, v in (("pitch", r.get("pitch")), ("volume", r.get("volume_db")), ("dist", pb.get("distance")), ("interval", pb.get("interval_s"))):
            if v is None:
                continue
            sp = _span(v)
            if sp is None or sp[0] > sp[1]:
                out.append("RANGE_ORDER: %s --%s %s is not low-high" % (sid, name, v))
    return out


def cmd_validate(a):
    d = load_list(a.list)
    errs = validate(d)
    root = Path(a.list).resolve().parent
    changed = []
    for s in d["sounds"]:
        for t in s.get("takes", []):
            f = root / t["file"]
            if not f.exists():
                errs.append("%s: file missing: %s" % (s["id"], t["file"]))
            elif t.get("sha256") and sha(f) != t["sha256"]:
                changed.append(t["file"])
    if changed:
        errs.append("changed since registered, register again: " + ", ".join(changed))
    return {"ok": not errs, "errors": errs, "warnings": playback_warnings(d), "sounds": len(d["sounds"])}


def cmd_status(a):
    d = load_list(a.list)
    rows = ["%-22s %-9s %-9s %2d/%-2d %s" % (s["id"], s["kind"], s["status"], len(s.get("takes", [])), s["variations"], s["route"]) for s in d["sounds"]]
    print("\n".join(rows) or "no sounds yet")
    return None


def cmd_plan(a):
    """Variation matrix: full product, shared layers, and parameters, side by side (after Fuesslin's matrix logic)."""
    axes = {}
    for item in a.axis:
        name, _, n = item.partition("=")
        if not n.isdigit() or int(n) < 1:
            raise Fail("--axis wants name=count, got %s" % item)
        axes[name] = int(n)
    v = a.variations
    product = 1
    for n in axes.values():
        product *= n
    biggest = max(axes, key=axes.get) if axes else None
    shared = sum(axes.values()) * v if axes else v
    param = (axes[biggest] * v) if biggest else v
    res = {"ok": True, "axes": axes, "variations_each": v,
           "full_product_files": product * v,
           "shared_layers_files": shared, "shared_layers_means": "one layer set per axis value, combined at play time",
           "parameter_files": param, "parameter_means": "record only %s; drive the other axes with pitch, filter or volume" % biggest}
    if a.budget and product * v > a.budget:
        res["over_budget"] = "full product is %d files, budget %d: use shared layers or parameters" % (product * v, a.budget)
    res["ask"] = ["Would a player notice if this axis were removed?", "Is it heard often enough to pay for itself?", "Can a parameter do it instead of a file?"]
    return res


# ---- routes ----

def http_json(url, data=None, timeout=20):
    req = urllib.request.Request(url, data=None if data is None else json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def comfy_hosts(explicit=None):
    if explicit:
        return [explicit.rstrip("/")]
    env = os.environ.get("SFX_COMFY_URLS") or os.environ.get("COMFYUI_URL")
    if env:
        return [h.strip().rstrip("/") for h in env.split(",") if h.strip()]
    return ["http://127.0.0.1:8188", "http://127.0.0.1:8199"]


def combo(info, node, field):
    """ComfyUI combos come in two shapes: [[values], {...}] and ["COMBO", {"options": [...]}]."""
    try:
        spec = info[node]["input"]["required"][field]
    except (KeyError, TypeError):
        return []
    if spec and isinstance(spec[0], list):
        return spec[0]
    if len(spec) > 1 and isinstance(spec[1], dict):
        return spec[1].get("options", [])
    return []


def audio_routes(info):
    routes = []
    clips = combo(info, "CLIPLoader", "clip_name")
    for ck in combo(info, "CheckpointLoaderSimple", "ckpt_name"):
        low = ck.replace("-", "_").lower()
        for frag in MODELS:  # longest fragments come first in MODELS, so _base wins
            if frag in low:
                fam = MODELS[frag][0]
                want = "t5gemma" if fam == "sa3" else "t5"
                te = next((c for c in clips if want in c.lower().replace("-", "_")), None)
                routes.append({"ckpt": ck, "model": frag, "family": fam, "text_encoder": te, "licence": MODELS[frag][1], "ready": bool(te)})
                break
    partner = [n for n in ("ElevenLabsTextToSoundEffects", "MireloTextToSFX", "MireloVideoToSFX") if n in info]
    return routes, partner


def probe_host(h, timeout=30):  # a busy host answered too slowly for 6 s and a render was lost
    try:
        info = http_json(h + "/object_info", timeout=timeout)
        q = http_json(h + "/queue", timeout=timeout)
    except (urllib.error.URLError, OSError, ValueError):
        return None
    routes, partner = audio_routes(info)
    return {"host": h, "busy": len(q.get("queue_running", [])) + len(q.get("queue_pending", [])), "routes": routes, "partner_nodes": partner,
            "save_advanced": "SaveAudioAdvanced" in info, "info": info}


def find_mw():
    env = os.environ.get("SFX_MW")
    if env and Path(env).is_file():
        return Path(env)
    here = Path(__file__).resolve()
    for up in here.parents:
        c = up / "musicwright" / "skills" / "musicwright" / "scripts" / "mw.py"
        if c.is_file():
            return c
    cache = Path.home() / ".claude" / "plugins" / "cache"
    if cache.is_dir():
        for c in sorted(cache.glob("*/musicwright/*/skills/musicwright/scripts/mw.py")):
            return c
    return None


def cmd_doctor(a):
    hosts = []
    for h in comfy_hosts(a.host):
        p = probe_host(h)
        if p:
            p.pop("info")
            hosts.append(p)
    mw = find_mw()
    usable = ["synth (procedural, always)"]
    if hosts and any(r["ready"] for p in hosts for r in p["routes"]):
        usable.append("gen (ComfyUI)")
    else:
        usable.append("gen --workflow-out (hand over a workflow; no reachable audio model)")
    return {"ok": True, "version": VERSION, "python": sys.version.split()[0], "ffmpeg": bool(A.ffmpeg()), "musicwright_mw": bool(mw), "comfyui": hosts, "routes": usable,
            "elevenlabs_key": bool(os.environ.get("ELEVENLABS_API_KEY")), "note": "paid APIs and installs need the user's yes"}


def build_prompt(route, prompt, seconds, batch, seed, prefix, save_advanced=True):
    frag = route["model"]
    _, _, steps, cfg, sampler, sched = MODELS[frag]
    text = prompt
    if route["family"] == "sa3":
        if not text.lower().startswith("tracktype"):
            text = "TrackType: SFX, " + text
        if "length:" not in text.lower():
            text = "%s. Length: %g seconds" % (text.rstrip(". "), seconds)
    save = {"class_type": "SaveAudioAdvanced", "inputs": {"audio": ["7", 0], "filename_prefix": prefix, "format": "flac"}} if save_advanced else {"class_type": "SaveAudio", "inputs": {"audio": ["7", 0], "filename_prefix": prefix}}
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": route["ckpt"]}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": route["text_encoder"], "type": "stable_audio", "device": "default"}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": text}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
        "5": {"class_type": "EmptyLatentAudio", "inputs": {"seconds": max(1.0, float(seconds)), "batch_size": batch}},
        "6": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["3", 0], "negative": ["4", 0], "latent_image": ["5", 0], "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": sampler, "scheduler": sched, "denoise": 1}},
        "7": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": save,
    }, text


def cmd_gen(a):
    hosts = [p for p in (probe_host(h) for h in comfy_hosts(a.host)) if p]
    candidates = [(p, r) for p in hosts for r in p["routes"] if r["ready"] and (not a.model or a.model in r["ckpt"])]
    if not candidates:
        wf = None
        if a.workflow_out:
            route = {"ckpt": "stable_audio_3_small_sfx.safetensors", "model": "stable_audio_3_small_sfx", "family": "sa3", "text_encoder": "t5gemma_b_b_ul2.safetensors"}
            wf, _ = build_prompt(route, a.prompt, a.seconds, a.takes, a.seed, "audio/sfx")
            Path(a.workflow_out).write_text(json.dumps(wf, indent=1), encoding="utf-8")
        return {"ok": False, "error": "no reachable ComfyUI with an audio model", "fallback": "use `sfx.py synth` or a CC0 library, or run the workflow on any ComfyUI", "workflow": a.workflow_out if wf else None}
    candidates.sort(key=lambda c: (c[0]["busy"], "medium" not in c[1]["model"] or "base" in c[1]["model"]))
    host, route = candidates[0]
    tag = hashlib.sha1(("%s%s%s" % (a.prompt, a.seed, time.time())).encode()).hexdigest()[:8]
    wf, text = build_prompt(route, a.prompt, a.seconds, a.takes, a.seed, "audio/sfxwright_%s" % tag, host["save_advanced"])
    try:
        pid = http_json(host["host"] + "/prompt", {"prompt": wf}, timeout=120)["prompt_id"]
    except (urllib.error.URLError, OSError, ValueError, KeyError) as e:
        raise Fail("ComfyUI refused or dropped the prompt: %s" % e)
    deadline = time.time() + a.timeout
    entry = None
    while time.time() < deadline:
        try:
            h = http_json(host["host"] + "/history/" + pid)
        except (urllib.error.URLError, OSError, ValueError):  # a busy host can miss one poll; the render is still going
            time.sleep(2)
            continue
        if pid in h:
            entry = h[pid]
            break
        time.sleep(2)
    if not entry:
        raise Fail("timed out waiting for ComfyUI; prompt %s may still finish" % pid)
    if entry.get("status", {}).get("status_str") == "error":
        raise Fail("ComfyUI error: %s" % json.dumps(entry["status"].get("messages", []))[-600:])
    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    files = []
    for node in entry.get("outputs", {}).values():
        for f in node.get("audio", []):
            q = urllib.parse.urlencode({"filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": f.get("type", "output")})
            with urllib.request.urlopen(host["host"] + "/view?" + q, timeout=120) as r:
                data = r.read()
            dest = outdir / ("%s_%02d%s" % (a.name, len(files) + 1, Path(f["filename"]).suffix))
            dest.write_bytes(data)
            write_side(dest, {"type": "generated", "model": route["ckpt"], "licence": route["licence"], "prompt": text, "seed": a.seed, "batch_index": len(files),
                              "settings": {k: wf["6"]["inputs"][k] for k in ("steps", "cfg", "sampler_name", "scheduler")}, "seconds": a.seconds, "date": today(), "ai_generated": True})
            files.append(str(dest))
    res = {"ok": True, "model": route["ckpt"], "licence": route["licence"], "files": files, "seed": a.seed}
    if a.seconds < 1:
        res["note"] = "the model's minimum is 1 s; trim with `edit --op tidy`"
    return res


def cmd_synth(a):
    if a.recipe == "list":
        return {"ok": True, "recipes": S.describe()}
    if not a.out:
        raise Fail("synth needs --out")
    params = {}
    for kv in a.param or []:
        k, _, v = kv.partition("=")
        try:
            params[k] = float(v) if re.fullmatch(r"-?[0-9.]+", v) else v
        except ValueError:
            params[k] = v
        if k in ("beans", "shakes") and k in params:
            params[k] = int(params[k])
    outp = Path(a.out)
    files = []
    for i in range(a.takes):
        seed = a.seed + i
        try:
            x = S.render(a.recipe, sr=a.sr, seed=seed, **params)
        except TypeError:
            raise Fail("%s: a --param has the wrong name or type, given %s; see references/routes.md" % (a.recipe, sorted(params)))
        except ValueError as e:
            raise Fail(str(e))
        f = outp if a.takes == 1 and outp.suffix else (outp if not outp.suffix else outp.parent) / ("%s_%02d.wav" % (a.name or a.recipe, i + 1))
        A.write_wav(f, A.Audio(a.sr, [x]))
        write_side(f, {"type": "procedural", "recipe": a.recipe, "params": params, "seed": seed, "licence": "procedural", "tool": "sfxwright %s" % VERSION, "date": today(), "ai_generated": False})
        files.append(str(f))
    return {"ok": True, "files": files}


def cmd_library(a):
    if a.licence not in LICENCES:
        raise Fail("licence must be one of: " + ", ".join(sorted(LICENCES)))
    rec = {"type": a.type, "licence": a.licence, "library": a.library or "", "title": a.title or "", "author": a.author or "", "url": a.url or "", "date": today(), "ai_generated": a.ai == "yes"}
    if a.licence in ("cc-by", "cc-by-sa", "cc-by-nd", "cc-by-nc", "cc-by-nc-sa", "cc-by-nc-nd", "cc-sampling+") and not a.author:
        raise Fail("this licence needs credit: pass --author")
    for f in a.files:
        write_side(f, rec)
    return {"ok": True, "files": a.files, "note": LICENCES[a.licence]["note"]}


def cmd_register(a):
    d = load_list(a.list)
    s = find_sound(d, a.id)
    root = Path(a.list).resolve().parent
    s.setdefault("takes", [])
    added = []
    for f in a.files:
        p = Path(f).resolve()
        side = read_side(p)
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            rel = str(p)
        take = {"file": rel, "sha256": sha(p), "source": side["source"] if side else {"type": "unknown", "licence": "unknown"}, "processing": side.get("processing", []) if side else [], "heard": None}
        s["takes"] = [t for t in s["takes"] if t["file"] != rel] + [take]
        added.append(rel)
    if s["status"] == "planned":
        s["status"] = "rendered"
    save_list(a.list, d)
    missing = [t["file"] for t in s["takes"] if sources_of(t)[0].get("licence") == "unknown"]
    res = {"ok": True, "id": a.id, "added": added}
    if missing:
        res["warning"] = "no known licence: " + ", ".join(missing)
    return res


# ---- checks ----

def seam_for(path, audio):
    """musicwright's seam score when it is installed, a small own version otherwise."""
    mw = find_mw()
    if mw:
        import subprocess
        try:
            r = subprocess.run([sys.executable, str(mw), "seam", str(path)], capture_output=True, text=True, timeout=60)
            row = json.loads(r.stdout)["files"][0]
            for k in ("seam", "ratio", "score", "jump_ratio", "seam_ratio"):
                if isinstance(row.get(k), (int, float)):
                    return round(float(row[k]), 2), "mw.py"
        except (OSError, ValueError, KeyError, IndexError, subprocess.SubprocessError):
            pass
    return A.seam_ratio(audio), "own"


def cmd_check(a):
    rows = []
    want = {}
    if a.list:
        d = load_list(a.list)
        root = Path(a.list).resolve().parent
        files = []
        for s in d["sounds"]:
            if a.id and s["id"] != a.id:
                continue
            for t in s.get("takes", []):
                files.append(str(root / t["file"]))
                want[files[-1]] = s
    else:
        files = a.files
    if not files:
        raise Fail("nothing to check")
    for f in files:
        au = A.read_audio(f)
        m = A.measure(au)
        s = want.get(f, {})
        loop = a.loop or s.get("kind") in ("loop",)
        seam = None
        if loop and not m.get("silent"):
            seam, via = seam_for(f, au)
            m["seam"], m["seam_via"] = seam, via
            m["seam_spectral"] = A.seam_spectral(au)
        length = a.seconds or (s.get("length_s") if s.get("kind") in ("one-shot", "ui", "stinger") else None)
        flags = A.flag(m, want_seconds=length, waive=tuple((a.waive or "").split(",")), loop=loop, seam=seam, spectral=m.get("seam_spectral"))
        if a.mono or s.get("spatial") == "3D":
            m["mono_loss_db"] = A.mono_loss(au)
            if m["mono_loss_db"] > A.LIMITS["mono_loss_db"]:
                flags = flags + ["MONO_LOSS"]
            if s.get("spatial") == "3D" and len(au.channels) > 1:
                flags = flags + ["STEREO_3D"]
        if a.tone_match:
            m["tone_gaps_db"], extra = tone_match(f, a.tone_match)
            flags = flags + extra
        if len(au.channels) > 1 and not m.get("silent"):
            lag = A.channel_lag(au)
            if lag:
                m["channel_lag_ms"], m["channel_lag_corr"] = lag["lag_ms"], lag["corr"]
                if abs(lag["lag_ms"]) > A.LIMITS["haas_echo_ms"] and lag["corr"] > A.LIMITS["haas_corr"]:
                    flags = flags + ["HAAS_ECHO"]
        if a.noise and not m.get("silent"):
            npd = A.noise_period(au.mono(), au.sr)
            m["noise_period_corr"], m["noise_period_s"] = npd["corr"], npd["lag_s"]
            if npd["corr"] > A.LIMITS["noise_period"]:
                flags = flags + ["NOISE_PERIOD"]
        flags = [x for x in flags if x not in (a.waive or "").split(",")]
        rows.append({"file": Path(f).name, "flags": flags, **({} if not a.json else {"readings": m}), **({} if a.json else {"m": m})})
    bad = sum(1 for r in rows if r["flags"])
    if a.json:
        return {"ok": True, "files": rows, "flagged": bad, "note": "flags mean listen; they are not verdicts"}
    for r in rows:
        m = r["m"]
        if m.get("silent"):
            print("%s  SILENT" % r["file"])
            continue
        print("%s  %.3fs sound %.3fs peak %.1f rms %.1f attack %.0fms tail %.2fs floor %.0f click %.1f%s  %s" % (
            r["file"], m["seconds"], m["sound_s"], m["peak_db"], m["rms_db"], m["attack_ms"], m["tail_s"], m["floor_db"], m["click"]["ratio"],
            " seam %.1f" % m["seam"] if "seam" in m else "", ",".join(r["flags"]) or "ok"))
    print("%d of %d flagged; a flag means listen, not reject" % (bad, len(rows)))
    return None


def _bands(mono, sr, size=2048, nb=16):
    m = A.magnitudes(mono, size)
    edges = [int(1 + (len(m) - 2) * (i / nb) ** 2.2) for i in range(nb + 1)]
    return [math.log(sum(m[edges[i]:max(edges[i + 1], edges[i] + 1)]) + 1e-6) for i in range(nb)]


def _down(mono, sr, target=11025):
    k = max(1, sr // target)
    return [sum(mono[i:i + k]) / k for i in range(0, len(mono), k)]


def best_corr(a, b, size=8192):
    """Peak normalised cross-correlation at the best lag, over the first second at low rate."""
    a, b = a[:size // 2], b[:size // 2]
    ea, eb = math.sqrt(sum(v * v for v in a)), math.sqrt(sum(v * v for v in b))
    if ea <= 0 or eb <= 0:
        return 0.0
    fa = A.fft(a + [0.0] * (size - len(a)))
    fb = A.fft(b + [0.0] * (size - len(b)))
    # Inverse FFT through the conjugate.
    prod = [x * y.conjugate() for x, y in zip(fa, fb)]
    inv = A.fft([p.conjugate() for p in prod])
    return max(abs(c.real) for c in inv) / size / (ea * eb)


def cmd_set(a):
    files = a.files
    if len(files) == 1 and Path(files[0]).is_dir():
        files = sorted(str(p) for p in Path(files[0]).iterdir() if p.suffix.lower() in (".wav", ".flac", ".ogg", ".mp3"))
    if len(files) < 2:
        raise Fail("a set needs at least two files")
    items = []
    for f in files:
        au = A.read_audio(f)
        mono = au.mono()
        m = A.measure(au)
        ip = int(m.get("peak_s", 0) * au.sr)
        start = max(0, ip - int(0.01 * au.sr))
        items.append({"file": Path(f).name, "m": m, "low": _down(mono[start:], au.sr), "attack": _bands(mono[start:start + int(0.05 * au.sr)], au.sr),
                      "rest": _bands(mono[start + int(0.05 * au.sr):], au.sr)})
    pairs = []
    dup = []
    for x, y in itertools.combinations(items, 2):
        c = best_corr(x["low"], y["low"])
        da = math.sqrt(sum((p - q) ** 2 for p, q in zip(x["attack"], y["attack"])) / 16)
        dr = math.sqrt(sum((p - q) ** 2 for p, q in zip(x["rest"], y["rest"])) / 16)
        pairs.append({"a": x["file"], "b": y["file"], "corr": round(c, 3), "attack_dist": round(da, 2), "rest_dist": round(dr, 2)})
        if c > A.LIMITS.get("dup_corr", 0.98):
            dup.append([x["file"], y["file"]])
    outliers = []
    for name, get in (("length", lambda m: math.log(max(m["sound_s"], 1e-3))), ("level", lambda m: m["rms_db"] / 8.7), ("brightness", lambda m: math.log(max(m["centroid_hz"] or 1, 1)))):
        vals = [get(i["m"]) for i in items if not i["m"].get("silent")]
        med = A.median(vals)
        mad = A.median([abs(v - med) for v in vals]) or 0.05
        for i in items:
            if not i["m"].get("silent") and abs(get(i["m"]) - med) > 3 * max(mad, 0.1):
                outliers.append({"file": i["file"], "by": name})
    peaks = [i["m"]["peak_db"] for i in items if not i["m"].get("silent")]
    rms = [i["m"]["rms_db"] for i in items if not i["m"].get("silent")]
    flags = []
    if dup:
        flags.append("NEAR_DUPLICATES")
    if outliers:
        flags.append("OUTLIERS")
    if max(rms) - min(rms) > 3:
        flags.append("LEVEL_SPREAD")
    force = None
    if getattr(a, "force", False):
        # Louder should be brighter: a force axis that only turns up the gain sounds like one hit at different volumes (Boulanger ed., Csound Book ch. 6).
        live = sorted((i["m"] for i in items if not i["m"].get("silent")), key=lambda m: m["rms_db"])
        third = max(1, len(live) // 3)
        soft = A.median([m["centroid_hz"] or 1 for m in live[:third]])
        loud = A.median([m["centroid_hz"] or 1 for m in live[-third:]])
        lvl = A.median([m["rms_db"] for m in live[-third:]]) - A.median([m["rms_db"] for m in live[:third]])
        force = {"level_rise_db": round(lvl, 2), "centroid_ratio": round(loud / soft, 3)}
        if lvl >= 3 and loud < soft * 1.05:
            flags.append("FORCE_GAIN_ONLY")
    return {"ok": True, "files": len(items), "flags": flags, "near_duplicates": dup, "outliers": outliers,
            "peak_spread_db": round(max(peaks) - min(peaks), 2), "rms_spread_db": round(max(rms) - min(rms), 2),
            "corr_max": max(p["corr"] for p in pairs), "corr_median": round(A.median([p["corr"] for p in pairs]), 3),
            "attack_dist_median": round(A.median([p["attack_dist"] for p in pairs]), 2), **({"force": force} if force else {}), "note": "heuristic; a blind listen decides whether a set machine-guns"}


def cmd_timing(a):
    au = A.read_audio(a.file)
    mono = au.mono()
    t = A.onsets(mono, au.sr)
    if len(t) < 3:
        return {"ok": True, "onsets": t, "flags": [], "note": "too few onsets to judge"}
    gaps = [q - p for p, q in zip(t, t[1:])]
    mean = sum(gaps) / len(gaps)
    cv = math.sqrt(sum((g - mean) ** 2 for g in gaps) / len(gaps)) / mean if mean else 0
    hits = [_down(mono[int(x * au.sr):int(x * au.sr) + int(0.2 * au.sr)], au.sr) for x in t[:12]]
    cs = [best_corr(p, q) for p, q in zip(hits, hits[1:])]
    flags = []
    if cv < A.LIMITS.get("timing_cv", 0.03):
        flags.append("TOO_EVEN")
    if cs and A.median(cs) > A.LIMITS.get("dup_corr", 0.98):
        flags.append("SAME_SAMPLE")
    return {"ok": True, "onsets": len(t), "mean_gap_s": round(mean, 3), "gap_cv": round(cv, 3), "neighbour_corr_median": round(A.median(cs), 3) if cs else None, "flags": flags}


def cmd_degrade(a):
    au = A.read_audio(a.input)
    n = au.n
    rng = random.Random(a.seed)
    ch = [list(c) for c in au.channels]
    if a.fault == "click":
        i = int(a.at * au.sr) if a.at is not None else rng.randrange(n // 3, n * 2 // 3)
        for c in ch:
            c[i] += a.amount if a.amount is not None else 0.5
    elif a.fault == "dc":
        v = a.amount if a.amount is not None else 0.01
        ch = [[s + v for s in c] for c in ch]
    elif a.fault == "clip":
        k = A.undb(a.amount if a.amount is not None else 12.0)
        top = max(abs(s) for c in ch for s in c) or 1.0
        lim = top * 0.99 if top < 0.99 else 0.99
        ch = [[max(-lim, min(lim, s * k)) for s in c] for c in ch]
    elif a.fault == "cut-head":
        i = max((c.index(max(c, key=abs)) for c in ch), default=0)
        i = max(0, i - int(0.0005 * au.sr))
        ch = [c[i:] for c in ch]
    elif a.fault == "cut-tail":
        keep = int(n * (a.amount if a.amount is not None else 0.4))
        ch = [c[:keep] for c in ch]
    elif a.fault == "seam":
        v = a.amount if a.amount is not None else 0.3
        ch = [[s + v * i / n for i, s in enumerate(c)] for c in ch]  # a ramp: the end no longer meets the start
    elif a.fault == "noise":
        k = A.undb(a.amount if a.amount is not None else -45.0)
        ch = [[s + k * rng.uniform(-1, 1) for s in c] for c in ch]
    elif a.fault == "pad":
        pad = [0.0] * int((a.amount if a.amount is not None else 1.0) * au.sr)
        ch = [pad + c + pad for c in ch]
    A.write_wav(a.out, A.Audio(au.sr, ch))
    return {"ok": True, "out": a.out, "fault": a.fault}


# ---- edits ----

def resample_linear(x, ratio):
    """Varispeed: pitch and length move together, with no phase artifacts."""
    n = int(len(x) / ratio)
    o = []
    for i in range(n):
        p = i * ratio
        j = int(p)
        f = p - j
        o.append(x[j] * (1 - f) + (x[j + 1] if j + 1 < len(x) else 0.0) * f)
    return o


def fade(ch, sr, in_ms, out_ms):
    n = len(ch)
    a, b = int(in_ms * sr / 1000), int(out_ms * sr / 1000)
    for i in range(min(a, n)):
        ch[i] *= i / a
    for i in range(min(b, n)):
        ch[n - 1 - i] *= i / b
    return ch


def remove_dc(c):
    mean = sum(c) / len(c)
    return [s - mean for s in c]


def tidy(au, head_db=-50.0, tail_db=-60.0, keep_ms=2.0, out_ms=10.0):
    """Remove DC, trim silence at both ends, fade so both ends reach exact zero."""
    chans = [remove_dc(c) for c in au.channels]
    peak = max(max(abs(s) for s in c) for c in chans) or 1.0
    hi, lo = peak * A.undb(head_db), peak * A.undb(tail_db)
    mono = [max(abs(c[i]) for c in chans) for i in range(au.n)]
    start = next((i for i, v in enumerate(mono) if v >= hi), 0)
    end = au.n
    while end > start + 1 and mono[end - 1] < lo:
        end -= 1
    start = max(0, start - int(keep_ms * au.sr / 1000))
    out = [fade(c[start:end], au.sr, min(keep_ms, 1.0), out_ms) for c in chans]
    return A.Audio(au.sr, out)


def compress(au, thresh_db=-6.0, ratio=6.0, attack_ms=5.0, release_ms=120.0):
    """Master bus compressor: a peak follower across all channels, gain cut above the threshold by the ratio. No make-up gain."""
    ka = math.exp(-1000.0 / (attack_ms * au.sr))
    kr = math.exp(-1000.0 / (release_ms * au.sr))
    env, gains = 0.0, []
    for i in range(au.n):
        v = max(abs(c[i]) for c in au.channels)
        k = ka if v > env else kr
        env = k * env + (1 - k) * v
        over = 20 * math.log10(env) - thresh_db if env > 1e-9 else -1.0
        gains.append(A.undb(-over * (1 - 1 / ratio)) if over > 0 else 1.0)
    return A.Audio(au.sr, [[s * g for s, g in zip(c, gains)] for c in au.channels])


def _rms(chs):
    n = sum(len(c) for c in chs)
    return math.sqrt(sum(v * v for c in chs for v in c) / n) if n else 0.0


def convolve(inp, ir, outp, mix, wet_db=0.0):
    """Convolve with an IR, level-matched: the wet signal is scaled to the dry RMS (plus wet_db), then mixed.
    ffmpeg afir's default irnorm=1 rescales the IR and left the wet path about 43 dB down, so the IR goes in raw
    (irnorm=-1, gtype=none) and the level is set here."""
    import tempfile
    dry = A.read_audio(inp)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "wet.wav"
        # afir stops at the input's end, which cut the reverb tail; pad the input by the IR's length first (Wilson, Make: Analog Synthesizers ch. 7).
        pad = A.read_audio(ir).seconds
        A.run_ffmpeg(["-i", str(inp), "-i", str(ir), "-filter_complex", "[0:a]apad=pad_dur=%.4f[d];[d][1:a]afir=dry=1:wet=1:irnorm=-1:gtype=none" % pad, "-c:a", "pcm_f32le", str(tmp)])
        wet = A.read_audio(tmp)
    n = max(dry.n, wet.n)
    nch = max(len(dry.channels), len(wet.channels))
    d = [list(dry.channels[i % len(dry.channels)]) + [0.0] * (n - dry.n) for i in range(nch)]
    w = [list(wet.channels[i % len(wet.channels)]) + [0.0] * (n - wet.n) for i in range(nch)]
    rd, rw = _rms(d), _rms(w)
    k = (rd / rw) * A.undb(wet_db) if rw > 1e-12 else 0.0
    out = [[(1 - mix) * x + mix * k * y for x, y in zip(dc, wc)] for dc, wc in zip(d, w)]
    pk = max((abs(v) for c in out for v in c), default=0.0)
    if pk > 0.999:
        g = A.undb(-1.0) / pk
        out = [[v * g for v in c] for c in out]
    A.write_wav(outp, A.Audio(dry.sr, out))


def cmd_edit(a):
    guard_edit([a.input], a.override_licence)
    outp = Path(a.out)
    step = {"op": a.op, "value": a.value, "date": today()}
    if a.op in ("stretch", "convolve"):
        if a.op == "stretch":
            if not a.value or not 0.25 <= a.value <= 4:
                raise Fail("--value is the speed factor, 0.25 to 4; above 1 is shorter")
            chain = []
            v = a.value
            while v > 2:
                chain.append("atempo=2")
                v /= 2
            while v < 0.5:
                chain.append("atempo=0.5")
                v *= 2
            chain.append("atempo=%g" % v)
            A.run_ffmpeg(["-i", a.input, "-filter:a", ",".join(chain), "-c:a", "pcm_s24le", str(outp)])
        else:
            if not a.ir:
                raise Fail("convolve needs --ir, an impulse response whose licence you know")
            mix = a.value if a.value is not None else 0.3
            convolve(a.input, a.ir, outp, mix, a.wet_db)
            step["ir"] = Path(a.ir).name
            step["wet_db"] = a.wet_db
        warn = "stretch on an impact smears the attack; prefer pitch (varispeed)" if a.op == "stretch" else None
    else:
        au = A.read_audio(a.input)
        warn = None
        if a.op == "tidy":
            au = tidy(au)
        elif a.op == "trim":
            lo, hi = int((a.start or 0) * au.sr), int((a.end or au.seconds) * au.sr)
            au = A.Audio(au.sr, [c[lo:hi] for c in au.channels])
        elif a.op == "fade":
            au = A.Audio(au.sr, [fade(list(c), au.sr, a.fade_in, a.fade_out) for c in au.channels])
        elif a.op == "gain":
            k = A.undb(a.value or 0.0)
            au = A.Audio(au.sr, [[s * k for s in c] for c in au.channels])
        elif a.op == "peak":
            top = max(max(abs(s) for s in c) for c in au.channels) or 1.0
            k = A.undb(a.value if a.value is not None else -3.0) / top
            au = A.Audio(au.sr, [[s * k for s in c] for c in au.channels])
        elif a.op == "compress":
            if a.ratio < 1:
                raise Fail("--ratio is 1 or more")
            au = compress(au, a.value if a.value is not None else -6.0, a.ratio)
            step["ratio"] = a.ratio
        elif a.op == "softclip":
            # Linear near zero, rounder above: tanh at --value dB of drive, scaled back to the input peak (Boulanger ed., Csound Book ch. 29-30).
            g = A.undb(a.value if a.value is not None else 6.0)
            top = max(max(abs(s) for s in c) for c in au.channels) or 1.0
            k = top / math.tanh(g * top)
            au = A.Audio(au.sr, [[k * math.tanh(g * s) for s in c] for c in au.channels])
        elif a.op == "reverse":
            au = A.Audio(au.sr, [c[::-1] for c in au.channels])
        elif a.op == "dc":
            au = A.Audio(au.sr, [remove_dc(c) for c in au.channels])
        elif a.op == "pitch":
            if a.value is None:
                raise Fail("--value is semitones")
            r = 2 ** (a.value / 12)
            au = A.Audio(au.sr, [resample_linear(c, r) for c in au.channels])
            step["route"] = "varispeed"
    A.write_wav(outp, au) if a.op not in ("stretch", "convolve") else None
    derive(outp, [a.input], step)
    res = {"ok": True, "out": str(outp), "route": step.get("route", a.op)}
    if warn:
        res["warning"] = warn
    au2 = A.read_audio(outp)
    res["flags"] = A.flag(A.measure(au2))
    return res


def recipe_layers(au, recipe):
    """Layers from one sound, from the books' recipes: `bigger` 100, 80, 50% speed; `pitch` 0, -3, -6, -9 semitones; `offset` six rotated copies of a bed."""
    if recipe == "offset":
        return [A.Audio(au.sr, [c[len(c) * i // 6:] + c[:len(c) * i // 6] for c in au.channels]) for i in range(6)]
    speeds = {"bigger": (1.0, 0.8, 0.5), "pitch": tuple(2 ** (-st / 12) for st in (0, 3, 6, 9))}[recipe]
    return [A.Audio(au.sr, [resample_linear(c, v) for c in au.channels]) if v != 1.0 else au for v in speeds]


def cmd_layer(a):
    guard_edit(a.files, a.override_licence)
    parts = [A.read_audio(f) for f in a.files]
    if a.recipe:
        if len(parts) != 1:
            raise Fail("--recipe builds layers from one file")
        parts = recipe_layers(parts[0], a.recipe)
    sr = parts[0].sr
    if any(p.sr != sr for p in parts):
        raise Fail("all layers must share a sample rate; found %s" % sorted({p.sr for p in parts}))
    gains = [float(x) for x in (a.gains or "").split(",") if x] or [0.0] * len(parts)
    offs = [float(x) for x in (a.offsets or "").split(",") if x] or [0.0] * len(parts)
    if len(gains) != len(parts) or len(offs) != len(parts):
        raise Fail("--gains and --offsets need one value per file")
    peaks = [A.measure(p).get("peak_s", 0.0) for p in parts]
    ref = max(peaks) if a.align == "peak" else 0.0
    starts = [int(((ref - pk) if a.align == "peak" else 0.0 + o) * sr) + int((o if a.align == "peak" else 0) * sr) for pk, o in zip(peaks, offs)]
    low = min(starts)
    starts = [s - low for s in starts]
    n = max(s + p.n for s, p in zip(starts, parts))
    nch = max(len(p.channels) for p in parts)
    mix = [[0.0] * n for _ in range(nch)]
    for s, p, g in zip(starts, parts, gains):
        k = A.undb(g)
        for c in range(nch):
            src = p.channels[c % len(p.channels)]
            dst = mix[c]
            for i, v in enumerate(src):
                dst[s + i] += v * k
    top = max(max(abs(v) for v in c) for c in mix)
    if top > 0.89:
        mix = [[v * 0.89 / top for v in c] for c in mix]
    A.write_wav(a.out, A.Audio(sr, mix))
    derive(a.out, a.files, {"op": "layer", "recipe": a.recipe, "gains_db": gains, "offsets_s": offs, "align": a.align, "date": today()})
    names = [Path(a.files[0]).name + " #%d" % i for i in range(len(parts))] if a.recipe else [Path(f).name for f in a.files]
    levels = {n: A.measure(p).get("peak_db") for n, p in zip(names, parts)}
    res = {"ok": True, "out": a.out, "layer_peaks_db": levels, "flags": A.flag(A.measure(A.read_audio(a.out)))}
    same = [] if a.recipe == "offset" else coincident_onsets(parts, starts, names, sr)  # a bed has no single onset
    if same:
        res["warnings"] = ["ONSETS_COINCIDE: %s and %s start within %d ms; stage them a few ms apart with --offsets" % (x, y, ONSET_MS) for x, y in same]
    return res


ONSET_MS = 3


def coincident_onsets(parts, starts, names, sr):
    """Pairs of layers whose first onsets land within ONSET_MS of each other in the mix."""
    at = []
    for p, s, n in zip(parts, starts, names):
        on = A.onsets(p.mono(), sr)
        at.append((s / sr + (on[0] if on else A.measure(p).get("lead_silence_s", 0.0)), n))
    return [(at[i][1], at[j][1]) for i in range(len(at)) for j in range(i + 1, len(at)) if abs(at[i][0] - at[j][0]) * 1000 < ONSET_MS]


def cmd_vary(a):
    guard_edit(a.files, a.override_licence)
    rng = random.Random(a.seed)
    outdir = Path(a.out)
    files = []
    for i in range(a.count):
        src = a.files[i % len(a.files)]
        au = A.read_audio(src)
        st = rng.uniform(-a.pitch, a.pitch)
        g = rng.uniform(-a.gain, a.gain)
        r = 2 ** (st / 12)
        k = A.undb(g)
        ch = [[s * k for s in resample_linear(c, r)] for c in au.channels]
        f = outdir / ("%s_%02d.wav" % (a.name, i + 1))
        A.write_wav(f, A.Audio(au.sr, ch))
        derive(f, [src], {"op": "vary", "pitch_st": round(st, 3), "gain_db": round(g, 2), "route": "varispeed", "seed": a.seed, "date": today()})
        files.append(str(f))
    note = None
    if len(a.files) == 1:
        note = "one source shifted in pitch keeps one attack; add more sources if the set machine-guns by ear"
    return {"ok": True, "files": files, "note": note}


def cmd_sequence(a):
    guard_edit(a.files, a.override_licence)
    rng = random.Random(a.seed)
    hits = [A.read_audio(f) for f in a.files]
    sr = hits[0].sr
    placed = []
    end = 0.0
    walkers = max(1, getattr(a, "walkers", 1))
    for w in range(walkers):
        # extra walkers: own start phase and pace, quieter, so the steps blur into a group bed
        t = rng.uniform(0, a.gap) if w else 0.0
        pace = a.gap * (rng.uniform(0.9, 1.1) if w else 1.0)
        trim = A.undb(-3.0) if walkers > 1 else 1.0
        breaks = [float(x) for x in (a.breaks or "").split(",") if x]
        last = -1
        for i in range(a.count):
            pool = [j for j in range(len(hits)) if j != last] or [0]
            j = rng.choice(pool)
            last = j
            placed.append((t, j, trim * A.undb(rng.uniform(-a.gain, a.gain))))
            gap = pace * (1 + rng.uniform(-a.jitter, a.jitter))
            if i % 2 == 1:
                gap *= a.limp
            t += gap
            while breaks and t >= breaks[0]:
                t = breaks.pop(0) + a.gap
        end = max(end, t)
    placed.sort()
    t = end
    n = int((t + max(h.seconds for h in hits)) * sr)
    x = [0.0] * n
    for at, j, k in placed:
        s = int(at * sr)
        for i, v in enumerate(hits[j].mono()):
            if s + i < n:
                x[s + i] += v * k
    top = max(abs(v) for v in x) or 1.0
    if top > 0.89:
        x = [v * 0.89 / top for v in x]
    A.write_wav(a.out, A.Audio(sr, [x]))
    derive(a.out, a.files, {"op": "sequence", "count": a.count, "walkers": a.walkers, "gap_s": a.gap, "jitter": a.jitter, "seed": a.seed, "date": today()})
    return {"ok": True, "out": a.out, "events": [round(p[0], 3) for p in placed], "seconds": round(n / sr, 2)}


def cmd_loop(a):
    guard_edit([a.input], a.override_licence)
    au = A.read_audio(a.input)
    xf = int(a.crossfade * au.sr)
    if xf * 2 >= au.n:
        raise Fail("crossfade too long for a %.2f s file" % au.seconds)
    out = []
    for c in au.channels:
        body = list(c[:-xf])
        tail = c[-xf:]
        for i in range(xf):  # equal power: suits uncorrelated noise beds
            th = i / xf * math.pi / 2
            body[i] = c[i] * math.sin(th) + tail[i] * math.cos(th)
        out.append(body)
    res_au = A.Audio(au.sr, out)
    A.write_wav(a.out, res_au)
    derive(a.out, [a.input], {"op": "loop", "crossfade_s": a.crossfade, "date": today()})
    seam, via = seam_for(a.out, res_au)
    spectral = A.seam_spectral(res_au)
    flags = (["SEAM"] if seam > A.LIMITS["seam"] else []) + (["SEAM_SPECTRAL"] if spectral > A.LIMITS["seam_spectral"] else [])
    return {"ok": True, "out": a.out, "seconds": round(res_au.seconds, 3), "seam": seam, "seam_via": via, "seam_spectral": spectral, "flags": flags, "note": "use WAV or OGG: MP3 padding breaks loops"}


def cmd_record_sheet(a):
    """A one-page recording plan for the sounds on the list that someone will record."""
    d = load_list(a.list)
    rows = [s for s in d["sounds"] if a.all or s.get("route") in ("record", "own", "foley", "recorded")]
    if not rows:
        raise Fail("no sound has route record; set the route or pass --all")
    lines = ["# Recording sheet: %s" % d.get("project", ""), "", "Before the first take: stop the fridge, heating and fans, with your keys in the fridge so you restart it. Stand where the sound will be and listen. Clap, record and play back. Wear quiet clothes.", "",
             "48 kHz 24-bit; 96 kHz if it will be pitched far down. Watch peaks and leave at least 6 dB. Do not cut rumble now. Say the slate before each take. Vary each take: soft, hard, short, long. Record 30 s of the room with nobody moving.", "",
             "| Slate | Event | Layers | Length | Takes | Surface, material, distance | Done |", "|---|---|---|---|---|---|---|"]
    for s in rows:
        roles = ", ".join(r["role"] for r in s.get("layers", [])) or "whole"
        lines.append("| %s | %s | %s | %g s | %d | %s |  |" % (s["id"], s["event"].replace("|", "/"), roles, s["length_s"], s["variations"] + 2, (s.get("brief") or "").replace("|", "/")))
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8", newline="\n")
        return {"ok": True, "out": a.out, "sounds": len(rows)}
    return {"ok": True, "sounds": len(rows), "sheet": text}


def cmd_tone(a):
    """Find the steadiest quiet stretch in a recording and optionally make a fill of it."""
    guard_edit([a.input], a.override_licence)
    au = A.read_audio(a.input)
    start, length, rms = A.quietest_stretch(au.mono(), au.sr)
    i0, i1 = int(start * au.sr), int((start + length) * au.sr)
    flags = ["TONE_SHORT"] if length < a.min_seconds else []
    res = {"ok": True, "start_s": round(start, 2), "seconds": round(length, 2), "rms_db": round(rms, 1), "flags": flags,
           "bands_low_mid_high_db": A.band_levels(A.Audio(au.sr, [c[i0:i1] for c in au.channels]).mono(), au.sr)}
    if not a.out:
        return res
    if i1 - i0 < au.sr // 2:
        raise Fail("only %.2f s of steady tone found: too short for a fill" % length)
    want = int((a.seconds or length) * au.sr)
    xf = min((i1 - i0) // 4, au.sr)
    out = []
    for c in au.channels:
        part = c[i0:i1]
        buf = list(part[:want])
        while len(buf) < want:  # equal power: tone is uncorrelated noise, and a straight repeat would click
            for k in range(xf):
                th = k / xf * math.pi / 2
                buf[len(buf) - xf + k] = buf[len(buf) - xf + k] * math.cos(th) + part[k] * math.sin(th)
            buf.extend(part[xf:])
        out.append(buf[:want])
    A.write_wav(a.out, A.Audio(au.sr, out))
    derive(a.out, [a.input], {"op": "tone", "start_s": res["start_s"], "seconds": round(want / au.sr, 3), "date": today()})
    res["out"], res["fill_seconds"] = a.out, round(want / au.sr, 3)
    return res


def tone_match(fill, neighbour):
    """Band level gaps in dB, fill minus neighbour; a gap flags TONE_MISMATCH, never a verdict."""
    x, y = A.read_audio(fill), A.read_audio(neighbour)
    gaps = [round(p - q, 1) for p, q in zip(A.band_levels(x.mono(), x.sr), A.band_levels(y.mono(), y.sr))]
    return gaps, ["TONE_MISMATCH"] if max(abs(g) for g in gaps) > A.LIMITS["tone_gap_db"] else []


def cmd_pop(a):
    """Add a head and tail 2 pop to a stem, or verify them: one frame of 1 kHz, 2 s clear of the programme."""
    au = A.read_audio(a.input)
    frame = int(round(au.sr / a.fps))
    gap = int(2 * au.sr)
    if a.verify:
        mono = au.mono()
        limit = A.undb(-60)
        loud = [i for i, v in enumerate(mono) if abs(v) > limit]
        if not loud:
            raise Fail("silent file: no pop to find")
        gaps = [(p, q) for p, q in zip(loud, loud[1:]) if q - p > au.sr // 2]
        if not gaps:
            return {"ok": True, "head_frames_off": None, "tail_frames_off": None, "flags": ["POP_OFF"]}
        head = round((gaps[0][1] - loud[0] - gap) / frame, 2)  # frames off the 2 s mark
        tail = round((gaps[-1][1] - gaps[-1][0] + frame - gap) / frame, 2)
        ok = len(gaps) >= 2 and abs(head) <= a.tolerance and abs(tail) <= a.tolerance
        return {"ok": True, "head_frames_off": head, "tail_frames_off": tail, "flags": [] if ok else ["POP_OFF"]}
    if not a.out:
        raise Fail("pop needs --out, or --verify")
    amp = A.undb(a.level)
    beep = [amp * math.sin(2 * math.pi * 1000 * i / au.sr) for i in range(frame)]
    silence = [0.0] * (gap - frame)
    A.write_wav(a.out, A.Audio(au.sr, [beep + silence + list(c) + [0.0] * (gap - frame) + beep for c in au.channels]))
    derive(a.out, [a.input], {"op": "pop", "fps": a.fps, "level_db": a.level, "date": today()})
    return {"ok": True, "out": a.out, "programme_starts_s": round(gap / au.sr, 3), "note": "cut the pops off before anything but a sync check"}


def cmd_place(a):
    """Lay each sound's first take at at_s, aligned on its sync point, and report the error in frames."""
    d = load_list(a.list)
    root = Path(a.list).resolve().parent
    fps = d.get("frame_rate") or 24
    sr = a.sr
    items = []
    report = []
    for s in d["sounds"]:
        if s.get("at_s") is None or not s.get("takes"):
            continue
        pick = next((t for t in s["takes"] if t.get("picked")), s["takes"][0])
        au = A.read_audio(root / pick["file"])
        if au.sr != sr:
            raise Fail("%s is %d Hz; finish to %d first" % (pick["file"], au.sr, sr))
        m = A.measure(au)
        sp = s.get("sync_point_s")
        anchored = sp is not None
        if sp is None:  # a bed starts where it is placed; its loudest moment means nothing
            sp = 0.0 if s.get("sync_class") == "bed" else m.get("peak_s", 0.0)
        start = s["at_s"] - sp
        err = (m.get("peak_s", 0.0) - sp) * fps
        limit = 1 if s.get("sync_class", "tight") == "tight" else 2
        report.append({"id": s["id"], "start_s": round(start, 3), "anchor": "sync_point_s" if anchored else "measured peak", "peak_vs_anchor_frames": round(err, 2), "over_limit": abs(err) > limit, "gain_db": s.get("gain_db", 0.0)})
        items.append((max(0, int(start * sr)), au, A.undb(s.get("gain_db", 0.0))))
    if not items:
        raise Fail("no sound has both at_s and a take")
    n = max(s + au.n for s, au, _ in items)
    if a.out:
        mix = [[0.0] * n, [0.0] * n]
        for s, au, k in items:
            for c in range(2):
                src = au.channels[c % len(au.channels)]
                dst = mix[c]
                for i, v in enumerate(src):
                    dst[s + i] += v * k
        top = max(max(abs(v) for v in c) for c in mix)
        if top > 0.89:
            mix = [[v * 0.89 / top for v in c] for c in mix]
        A.write_wav(a.out, A.Audio(sr, mix))
    return {"ok": True, "fps": fps, "placed": report, "out": a.out, "note": "the peak is a measured stand-in for sync; check with picture"}


def cmd_avsync(a):
    """Score a soundtrack against its picture: video motion events against audio onsets.

    Motion is the mean change of 64x36 gray frames at --fps; an event is a rise in it (median + 3 MAD, 4-frame
    refractory). Audio onsets come from A.onsets. lag_ms is the median nearest audio-minus-video offset (positive =
    audio late). Idea after LiveFoley (arXiv:2611.05988): sync is measured against the picture per event, with a
    perceptual bound (action about 0.34 s); sfxwright keeps its own frame limits. Written fresh; no code from the paper.
    A heuristic: camera moves, cuts and steady beds make false events, so read the counts before the flags.
    """
    fps = a.fps
    if fps <= 0 or a.tol < 0:
        raise Fail("--fps must be positive and --tol not negative")
    motion = A.video_motion(a.video, fps)
    vid = [i / fps for i in A.motion_events(motion, fps)]
    src = a.audio or a.video
    try:
        au = A.read_audio(src)
    except A.AudioError as e:
        raise Fail("no audio read from %s (%s); pass --audio" % (src, e))
    aud = A.onsets(au.mono(), au.sr)
    tol_s = a.tol / fps
    lag, used = A.event_lag(vid, aud, a.max_lag)
    lag = lag or 0.0
    at0 = A.matched(vid, aud, 0.0, tol_s)
    after = A.matched(vid, aud, lag, tol_s)
    flags = []
    if not vid or not aud:
        flags.append("NO_EVENTS")
    elif used < 3:  # on real clips one or two pairs gave 150-250 ms lags that meant nothing
        flags.append("FEW_EVENTS")
    elif lag > tol_s + 1e-9:
        flags.append("LATE")
    elif lag < -tol_s - 1e-9:
        flags.append("EARLY")
    if vid and aud and after * 2 < len(vid):
        flags.append("LOW_MATCH")
    return {"ok": True, "fps": fps, "tol_frames": a.tol, "lag_ms": round(lag * 1000), "lag_frames": round(lag * fps, 2),
            "video_events": len(vid), "audio_onsets": len(aud), "offsets_used": used,
            "matched_at_0": at0, "matched_after_lag": after,
            "match_rate_at_0": round(at0 / len(vid), 3) if vid else None,
            "match_rate_after_lag": round(after / len(vid), 3) if vid else None,
            "video_events_s": [round(t, 3) for t in vid[:50]], "audio_onsets_s": aud[:50], "flags": flags,
            "note": "heuristic: camera moves, cuts and beds add false events; about 0.34 s is where viewers notice action lag (arXiv:2611.05988)"}


# ---- scene: sources moved through a room by a plan ----

# RT60 per room class: midpoints of the bands in the synthetic-data recipe of AMBIT (arXiv:2610.34415, room table):
# dry 0.16-0.28 s, moderate 0.38-0.62 s, reverberant 0.78-1.20 s, outdoor no reflections.
ROOMS = {"dry": 0.22, "moderate": 0.5, "reverberant": 1.0, "outdoor": None}
FDN_MS = (29.7, 37.1, 41.1, 43.7, 53.3, 59.9, 67.7, 73.1)
ALLPASS_MS = (4.1, 7.3, 11.9)


def _fdn(x, sr, rt60, n):
    """Mono room tail: an 8-line feedback delay network with a Householder mix; each line's gain sets the same RT60.
    Python cannot convolve a second-long noise IR at speed, so the tail is built by recursion."""
    m = [max(1, int(d * sr / 1000)) for d in FDN_MS]
    g = [10 ** (-3.0 * k / (rt60 * sr)) for k in m]
    bufs = [[0.0] * k for k in m]
    pos = [0] * 8
    lines = list(zip(range(8), m, g, bufs))
    a = 1 - math.exp(-2 * math.pi * min(6000.0, sr * 0.45) / sr)  # a darker tail than the direct sound
    y, out, nx = 0.0, [0.0] * n, len(x)
    for i in range(n):
        xi = x[i] if i < nx else 0.0
        v = [b[pos[j]] for j, _, _, b in lines]
        s = sum(v) * 0.25  # 2/N
        for j, k, gj, b in lines:
            p = pos[j]
            b[p] = gj * (v[j] - s) + xi
            pos[j] = p + 1 if p + 1 < k else 0
        y += a * ((v[0] - v[1] + v[2] - v[3] + v[4] - v[5] + v[6] - v[7]) - y)
        out[i] = y
    return out


def _allpass(x, sr, ms, g=0.6):
    d = max(1, int(ms * sr / 1000))
    xb, yb, out = [0.0] * d, [0.0] * d, [0.0] * len(x)
    for i, v in enumerate(x):
        p = i % d
        y = -g * v + xb[p] + g * yb[p]
        xb[p], yb[p] = v, y
        out[i] = y
    return out


def _hp1(x, sr, hz):
    a = 1 - math.exp(-2 * math.pi * hz / sr)
    lp, out = 0.0, [0.0] * len(x)
    for i, v in enumerate(x):
        lp += a * (v - lp)
        out[i] = v - lp
    return out


def room_tail(send, sr, rt60, n, width=0.7, cross_hz=1000.0):
    """Stereo reverb return with L and R matched per band. One mono tail M (unit energy per impulse) feeds both sides;
    a side signal S is M through three all-passes (same magnitude as M at every frequency, other phase), high-passed
    twice at cross_hz, and L = M + S, R = M - S. Separate noise tails per channel pulled a centred 440 Hz tone 6.5 dB
    sideways in the harvest prototype; here L and R carry the same energy in every band and share the low band."""
    imp = _fdn([1.0], sr, rt60, int(rt60 * sr) + int(max(FDN_MS) * sr / 1000))
    e = sum(v * v for v in imp)
    k = 1 / math.sqrt(e) if e > 0 else 0.0
    mid = [v * k for v in _fdn(send, sr, rt60, n)]
    side = mid
    for ms in ALLPASS_MS:
        side = _allpass(side, sr, ms)
    side = _hp1(_hp1(side, sr, cross_hz), sr, cross_hz)
    return [m + width * s for m, s in zip(mid, side)], [m - width * s for m, s in zip(mid, side)]


def _keys_at(keys, t):
    if t <= keys[0][0]:
        return keys[0][1:]
    for k0, k1 in zip(keys, keys[1:]):
        if t <= k1[0]:
            f = (t - k0[0]) / (k1[0] - k0[0]) if k1[0] > k0[0] else 1.0
            return [u + (w - u) * f for u, w in zip(k0[1:], k1[1:])]
    return keys[-1][1:]


def scene_params(az, el, dist, sr):
    """Equal-power stereo gains from azimuth and elevation (positive azimuth is left), 1/d past 1 m, and a one-pole
    air low-pass whose cutoff falls from 20 kHz at 1 m to 6 kHz at 50 m."""
    p = max(-1.0, min(1.0, -math.sin(math.radians(az)) * math.cos(math.radians(el))))
    th = (p + 1) * math.pi / 4
    d = max(1.0, dist)
    hz = 20000.0 * (6000.0 / 20000.0) ** min(1.0, math.log(d) / math.log(50.0))
    a = 1 - math.exp(-2 * math.pi * min(hz, sr * 0.45) / sr)
    return math.cos(th), math.sin(th), 1.0 / d, a


def _lr(el, er):
    if el <= 1e-20 and er <= 1e-20:
        return None
    return round(max(-60.0, min(60.0, 10 * math.log10(max(el, 1e-20) / max(er, 1e-20)))), 2)


def load_scene(path):
    try:
        plan = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Fail("cannot read plan %s: %s" % (path, e))
    room = plan.setdefault("room", "outdoor")
    if room not in ROOMS:
        raise Fail("room must be one of %s" % ", ".join(ROOMS))
    if not plan.get("sources"):
        raise Fail("the plan has no sources")
    if not isinstance(plan.get("duration"), (int, float)) or plan["duration"] <= 0:
        raise Fail("duration (seconds) must be positive")
    for i, s in enumerate(plan["sources"]):
        if not s.get("file"):
            raise Fail("source %d has no file" % i)
        keys = s.get("keys") or [[0, 0, 0, 1]]
        if any(len(k) != 4 for k in keys):
            raise Fail("source %d: each key is [t, az_deg, el_deg, dist_m]" % i)
        s["keys"] = sorted([float(v) for v in k] for k in keys)
    return plan


def cmd_scene(a):
    """Render a scene plan to stereo: per source keyframe interpolation (10 ms steps, ramped per sample), equal-power pan,
    1/d gain, a distance low-pass and a reverb send that does not fall with distance, so far sources read as far.
    Idea after AMBIT (arXiv:2610.34415): a structured plan rendered by code; the model itself is not used. Written fresh."""
    plan = load_scene(a.plan)
    root = Path(a.plan).resolve().parent
    files = [str(root / s["file"]) if not Path(s["file"]).is_absolute() else s["file"] for s in plan["sources"]]
    guard_edit(files, a.override_licence)
    sr = a.sr
    rt60 = plan.get("rt60", ROOMS[plan["room"]])
    dur = float(plan["duration"])
    nd = int(dur * sr)
    n = nd + (int(rt60 * sr) if rt60 else 0)
    B = max(1, sr // 100)
    L, R, send = [0.0] * n, [0.0] * n, [0.0] * n
    blk = max(1, sr // 2)
    nb = (nd + blk - 1) // blk
    per = []
    for s, f in zip(plan["sources"], files):
        au = A.read_audio(f)
        x = au.mono()
        if au.sr != sr:
            x = resample_linear(x, au.sr / sr)
        on, off = (s.get("active") or [0.0, dur])[:2]
        i0, i1 = max(0, int(on * sr)), min(nd, int(off * sr))
        if s.get("loop") and x:
            x = (x * (1 + (i1 - i0) // len(x)))[:max(0, i1 - i0)]
        i1 = min(i1, i0 + len(x))
        eL, eR = [0.0] * nb, [0.0] * nb
        if i1 > i0:
            g0 = A.undb(s.get("gain_db", 0.0))
            gs = A.undb(s.get("send_db", -12.0)) if rt60 else 0.0
            steps = [scene_params(*_keys_at(s["keys"], (i0 + j * B) / sr), sr) for j in range((i1 - i0) // B + 2)]
            fl = max(1, int(0.01 * sr))
            lp = 0.0
            for i in range(i0, i1):
                j, fr = divmod(i - i0, B)
                u, w = steps[j], steps[j + 1]
                fr /= B
                gl, gr, gd, ca = (p + (q - p) * fr for p, q in zip(u, w))
                lp += ca * (x[i - i0] - lp)
                v = lp * g0 * min(1.0, (i - i0) / fl, (i1 - 1 - i) / fl)
                dl, dr = v * gd * gl, v * gd * gr
                L[i] += dl
                R[i] += dr
                send[i] += v * gs
                b = i // blk
                eL[b] += dl * dl
                eR[b] += dr * dr
        per.append({"file": s["file"], "blocks": [{"t": round(b * blk / sr, 2), "lr_db": _lr(eL[b], eR[b]),
                                                   "level_db": round(A.db(math.sqrt((eL[b] + eR[b]) / 2 / blk)), 2)} for b in range(nb)]})
    if rt60:
        rl, rr = room_tail(send, sr, rt60, n, a.width)
        L = [p + q for p, q in zip(L, rl)]
        R = [p + q for p, q in zip(R, rr)]
    pk = max(max(abs(v) for v in L), max(abs(v) for v in R))
    trim = A.undb(-1.0) / pk if pk > A.undb(-1.0) else 1.0
    if trim != 1.0:
        L, R = [v * trim for v in L], [v * trim for v in R]
    A.write_wav(a.out, A.Audio(sr, [L, R]))
    derive(a.out, files, {"op": "scene", "room": plan["room"], "rt60_s": rt60, "sources": len(files), "date": today()})
    mix = []
    for b in range(nb):
        el = sum(v * v for v in L[b * blk:(b + 1) * blk])
        er = sum(v * v for v in R[b * blk:(b + 1) * blk])
        mix.append({"t": round(b * blk / sr, 2), "lr_db": _lr(el, er), "level_db": round(A.db(math.sqrt((el + er) / 2 / blk)), 2)})
    rep = {"ok": True, "out": a.out, "sr": sr, "seconds": round(n / sr, 3), "room": plan["room"], "rt60_s": rt60,
           "trim_db": round(A.db(trim), 2), "mix": mix, "sources": per,
           "note": "lr_db above 0 is left; stereo cannot place front against back (az 0 and 180 both read centre). RT60 bands from arXiv:2610.34415"}
    if a.report:
        Path(a.report).write_text(json.dumps(rep, indent=1), encoding="utf-8")
    return rep


def cmd_finish(a):
    guard_edit([a.input], a.override_licence)
    if a.dest not in DESTS:
        raise Fail("unknown destination %s; have %s" % (a.dest, ", ".join(sorted(DESTS))))
    ceil, sr, fmt = DESTS[a.dest]
    if a.ceiling is not None:
        ceil = a.ceiling
    fmt = a.format or fmt
    sr = a.sr or sr
    au = A.read_audio(a.input)
    # Gain only: a one-shot is levelled, not compressed. Encode last.
    top = max(max(abs(s) for s in c) for c in au.channels) or 1.0
    k = A.undb(ceil) / top
    au = tidy(A.Audio(au.sr, [[s * k for s in c] for c in au.channels])) if not a.keep_ends else A.Audio(au.sr, [[s * k for s in c] for c in au.channels])
    outp = Path(a.out)
    if outp.suffix.lower() != "." + fmt:
        outp = outp.with_suffix("." + fmt)  # the extension sets ffmpeg's container, so it must match the format
    if fmt == "wav" and au.sr == sr:
        A.write_wav(outp, au, bits=24 if a.bits == 24 else 16)
    else:
        with __import__("tempfile").TemporaryDirectory(prefix="sfx_") as td:
            tmp = Path(td) / "t.wav"
            A.write_wav(tmp, au)
            codec = {"wav": ["-c:a", "pcm_s24le"], "ogg": ["-c:a", "libvorbis", "-q:a", "6"], "flac": ["-c:a", "flac"], "mp3": ["-c:a", "libmp3lame", "-q:a", "2"]}.get(fmt)
            if not codec:
                raise Fail("format must be wav, ogg, flac or mp3")
            A.run_ffmpeg(["-i", str(tmp), "-ar", str(sr)] + codec + [str(outp)])
    derive(outp, [a.input], {"op": "finish", "dest": a.dest, "ceiling_db": ceil, "sr": sr, "format": fmt, "date": today()})
    res = {"ok": True, "out": str(outp), "dest": a.dest, "peak_ceiling_db": ceil, "sr": sr, "format": fmt, "note": "a file-level peak reference, not a delivery spec; balance the whole project by ear"}
    if au.sr < sr:
        res["warning"] = "upsampled from %d Hz; that adds no quality" % au.sr
    if fmt == "mp3" and a.dest.startswith("game"):
        res["warning"] = "MP3 padding breaks gapless loops"
    return res


def cmd_name(a):
    if a.check:
        bad = []
        for f in a.check:
            stem = Path(f).stem
            seg = stem.split("_")
            if len(seg) < 3 or not re.fullmatch(r"[A-Z]+[A-Za-z0-9]*(-[A-Za-z0-9]+)?", seg[0]):
                bad.append(stem)
        return {"ok": not bad, "not_ucs_shape": bad, "note": "this checks the shape; the CatID list is at universalcategorysystem.com"}
    clean = lambda v: re.sub(r"[^A-Za-z0-9 -]+", "", v or "").strip()
    fx = re.sub(r"\s+", " ", clean(a.fx))
    if a.style == "ucs":
        if not a.catid or not a.creator or not a.source:
            raise Fail("ucs needs --catid, --creator and --source")
        parts = [a.catid, fx, clean(a.creator).replace(" ", ""), clean(a.source).replace(" ", "")]
        if a.user:
            parts.append(clean(a.user))
        name = "_".join(parts)
    else:
        name = re.sub(r"[ -]+", "_", fx.lower())
    if a.index is not None:
        name += ("_%02d" if a.style != "ucs" else " %02d") % a.index
    return {"ok": True, "name": name, "warning": "FXName is long; aim under 25 characters" if len(fx) > 25 else None}


# ---- looking and listening ----

def _png(path, rows, width, height):
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(t, data):
        c = struct.pack(">I", len(data)) + t + data
        return c + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def cmd_sheet(a):
    rows_px = []
    w, h = a.width, 80
    names = []
    longest = 0.0
    loaded = []
    for f in a.files:
        au = A.read_audio(f)
        loaded.append((f, au))
        longest = max(longest, au.seconds)
    for f, au in loaded:
        names.append(Path(f).name)
        mono = au.mono()
        step = max(1, int(longest * au.sr / w))
        cols = []
        for x in range(w):
            seg = mono[x * step:(x + 1) * step]
            cols.append((min(seg), max(seg)) if seg else (0.0, 0.0))
        for y in range(h):
            v = 1 - 2 * y / (h - 1)
            rows_px.append([200 if lo <= v <= hi else (232 if abs(v) < 0.012 else 18) for lo, hi in cols])
        rows_px.append([90] * w)
    _png(a.out, rows_px, w, len(rows_px))
    return {"ok": True, "out": a.out, "rows_top_to_bottom": names, "seconds_across": round(longest, 2), "note": "waveforms share one time scale"}


def cmd_review(a):
    clips = [A.read_audio(f) for f in a.files]
    sr = clips[0].sr
    gap = [0.0] * int(a.gap * sr)
    x = []
    times = []
    for f, c in zip(a.files, clips):
        if c.sr != sr:
            c = A.Audio(sr, [resample_linear(ch, c.sr / sr) for ch in c.channels])
        times.append({"at_s": round(len(x) / sr, 3), "file": Path(f).name})
        m = c.mono()
        if a.match:
            top = max(abs(v) for v in m) or 1.0
            m = [v * 0.5 / top for v in m]
        x.extend(m)
        x.extend(gap)
    A.write_wav(a.out, A.Audio(sr, [x]), bits=16)
    return {"ok": True, "out": a.out, "index": times}


# ---- documents ----

def _cols(rows, fmt):
    if fmt == "csv":
        b = io.StringIO()
        csv.writer(b, lineterminator="\n").writerows(rows)
        return b.getvalue()
    head, body = rows[0], rows[1:]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in body]
    return "\n".join(lines) + "\n"


def credits_for(d):
    owed, disclose, rows = [], [], []
    for s in d["sounds"]:
        for t in s.get("takes", []):
            for src in sources_of(t):
                lic = LICENCES.get(src.get("licence", "unknown"), LICENCES["unknown"])
                rows.append((s["id"], t["file"], src))
                if lic.get("attribution"):
                    line = '"%s" by %s (%s) %s' % (src.get("title") or t["file"], src.get("author") or "UNKNOWN", src.get("licence"), src.get("url") or "")
                    if line not in owed:
                        owed.append(line.strip())
                if src.get("ai_generated") and src.get("model") not in disclose:
                    disclose.append(src.get("model"))
    return owed, disclose, rows


def cmd_doc(a):
    d = load_list(a.list)
    fps = d.get("frame_rate") or 24
    if a.kind == "cue":
        rows = [["Cue", "Time", "Frame", "Sound", "Role", "Sync", "Kind", "Length s", "File", "Status"]]
        for s in sorted(d["sounds"], key=lambda s: s.get("at_s", 1e9)):
            at = s.get("at_s")
            pick = next((t for t in s.get("takes", []) if t.get("picked")), (s.get("takes") or [{}])[0])
            rows.append([s["id"], "" if at is None else "%.3f" % at, "" if at is None else int(round(at * fps)), s["event"], s.get("role", ""), s.get("sync_class", ""), s["kind"], s["length_s"], pick.get("file", ""), s["status"]])
        text = _cols(rows, a.format)
    elif a.kind == "impl":
        rows = [["Event", "Category", "Trigger", "Kind", "2D/3D", "Variations", "Files", "Pitch range", "Volume range", "No repeat", "Priority", "Max instances", "Distance", "Max voices", "Interval s", "Attack s", "Release s", "Mute paused", "Format", "Load"]]
        for s in d["sounds"]:
            r, pb = s.get("randomize", {}), s.get("playback", {})
            nr = r.get("no_repeat", 1)
            rows.append([s["event"], s.get("category", ""), s.get("trigger", ""), s["kind"], s.get("spatial", ""), s["variations"], len(s.get("takes", [])), r.get("pitch", "+/-1 st (start point)"), r.get("volume_db", r.get("volume", "+/-1.5 dB (start point)")), "yes" if nr is True else nr, s.get("priority", ""), s.get("max_instances", ""),
                         pb.get("distance", ""), pb.get("max_voices", ""), pb.get("interval_s", ""), pb.get("attack_s", ""), pb.get("release_s", ""), "yes" if pb.get("mute_paused") else "", s["format"], s.get("load", "")])
        text = _cols(rows, a.format)
    else:
        owed, disclose, rows = credits_for(d)
        lines = ["# Sound credits and licences: %s" % d.get("project", ""), "", "Generated from the sound list on %s." % today(), "", "## Attribution owed", ""]
        lines += ["- " + x for x in owed] or ["None."]
        lines += ["", "## AI tools used to make shipped sound", ""]
        lines += ["- " + str(x) for x in disclose] or ["None recorded."]
        lines += ["", "## Every file", "", "| Sound | File | Type | Source | Licence |", "|---|---|---|---|---|"]
        for sid, f, src in rows:
            lines.append("| %s | %s | %s | %s | %s |" % (sid, f, src.get("type", "?"), src.get("model") or src.get("recipe") or src.get("library") or src.get("title") or "?", src.get("licence", "unknown")))
        text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        return {"ok": True, "out": a.out}
    print(text, end="")
    return None


def cmd_ship(a):
    d = load_list(a.list)
    root = Path(a.list).resolve().parent
    block, warn, disclose = [], [], set()
    commercial = d.get("commercial")
    sell_pack = a.sell_as_pack
    files = 0
    owed, models, _ = credits_for(d)
    for s in d["sounds"]:
        takes = s.get("takes", [])
        if a.picked_only:
            picked = [t for t in takes if t.get("picked")]
            takes = picked or takes
        if s["status"] != "rejected" and not takes:
            warn.append("%s: no file yet" % s["id"])
        for t in takes:
            files += 1
            f = root / t["file"]
            if not f.exists():
                block.append("%s: file missing: %s" % (s["id"], t["file"]))
            elif t.get("sha256") and sha(f) != t["sha256"]:
                block.append("%s: %s changed after it was registered; provenance no longer matches" % (s["id"], t["file"]))
            for src in sources_of(t):
                name = src.get("licence", "unknown")
                lic = LICENCES.get(name, LICENCES["unknown"])
                who = "%s (%s, %s)" % (t["file"], s["id"], name)
                if name == "unknown" or name not in LICENCES:
                    block.append("%s: no known licence; find the source or replace the file" % who)
                elif commercial and lic.get("commercial") is False:
                    block.append("%s: not allowed in a commercial project: %s" % (who, lic["note"]))
                elif commercial and lic.get("commercial") is None:
                    block.append("%s: unclear, read the terms first: %s" % (who, lic["note"]))
                elif lic.get("note") and name not in ("cc-by", "cc-by-sa"):
                    warn.append("%s: %s" % (who, lic["note"]))
                if sell_pack and lic.get("resale") is not True:
                    block.append("%s: not cleared for sale as a sound pack" % who)
                if lic.get("edit") is False and t.get("processing"):
                    block.append("%s: edited, but the licence forbids derivatives" % who)
                if src.get("ai_generated"):
                    disclose.add(s["id"])
    verdict = "BLOCKED" if block else ("CHECK" if warn else "CLEAR")
    res = {"ok": True, "answer": verdict, "files": files, "commercial": commercial, "blockers": sorted(set(block)), "warnings": sorted(set(warn)), "attribution_owed": owed, "ai_models": [m for m in models if m]}
    if disclose:
        res["disclosure"] = {"sounds": sorted(disclose), "steam": "Pre-Generated AI disclosure, content survey", "itch": "tag generative AI in the AI Disclosure section; a sound pack sold as a game asset must disclose too"}
    res["note"] = "a provenance record, not legal advice; store and licence wording changes, see references/rights.md"
    return res


def cmd_budget(a):
    d = load_list(a.list)
    root = Path(a.list).resolve().parent
    cats = {}
    savings = []
    for s in d["sounds"]:
        cat = (s.get("category") or s["kind"]).split("/")[0]
        c = cats.setdefault(cat, {"files": 0, "disk_kb": 0, "pcm_kb": 0})
        for t in s.get("takes", []):
            f = root / t["file"]
            if not f.exists():
                continue
            c["files"] += 1
            c["disk_kb"] += f.stat().st_size // 1024
            au = A.read_audio(f)
            c["pcm_kb"] += au.n * len(au.channels) * 2 // 1024
            m = A.measure(au)
            if len(au.channels) == 2 and all(abs(x - y) < 1e-4 for x, y in zip(au.channels[0][::50], au.channels[1][::50])):
                savings.append("%s: stereo with identical channels, make it mono" % t["file"])
            spare = m.get("end_silence_s", 0) + m.get("lead_silence_s", 0)
            if spare > 0.1:
                savings.append("%s: %.2f s of removable silence" % (t["file"], spare))
    for c in cats.values():
        c["adpcm_kb_est"] = c["pcm_kb"] * 2 // 7
    return {"ok": True, "categories": cats, "savings": savings[:20], "note": "estimates: ADPCM is about 3.5:1 of 16-bit PCM; compare with a real engine import before quoting"}


def build_parser():
    p = argparse.ArgumentParser(prog="sfx.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn, **kw):
        c = sub.add_parser(name, **kw)
        c.set_defaults(fn=fn)
        return c

    def ov(c):
        c.add_argument("--override-licence", action="store_true", help="edit despite a no-derivatives licence; say why to the user")

    c = add("doctor", cmd_doctor)
    c.add_argument("--host")
    c = add("init", cmd_init)
    c.add_argument("list")
    c.add_argument("--project", required=True)
    c.add_argument("--use", required=True, choices=("game", "film", "video", "app", "library", "other"))
    c.add_argument("--commercial", required=True, choices=("yes", "no"))
    c.add_argument("--frame-rate", type=float, default=None)
    c.add_argument("--style")
    c.add_argument("--force", action="store_true")
    c = add("add", cmd_add)
    c.add_argument("list")
    c.add_argument("id")
    c.add_argument("--event", required=True)
    c.add_argument("--kind", required=True, choices=KINDS)
    c.add_argument("--length", type=float, required=True)
    c.add_argument("--variations", type=int, default=1)
    c.add_argument("--route", default="undecided")
    c.add_argument("--format", default="wav")
    c.add_argument("--category")
    c.add_argument("--brief")
    c.add_argument("--layers", help="comma-separated roles: transient,body,tail")
    c.add_argument("--loudness")
    c.add_argument("--sync-point", type=float, dest="sync_point")
    c.add_argument("--at", type=float)
    c.add_argument("--trigger")
    c.add_argument("--priority")
    c.add_argument("--max-instances", type=int, dest="max_instances")
    c.add_argument("--spatial", choices=("2D", "3D"))
    c.add_argument("--gain", type=float, help="dB applied by place")
    c.add_argument("--sync-class", dest="sync_class", choices=("tight", "loose", "bed"))
    c.add_argument("--role", choices=("hard", "background", "foley", "design", "ui"))
    c.add_argument("--pitch-range", dest="pitch_range", help="per-play pitch ratio low-high, e.g. 0.9-1.1")
    c.add_argument("--volume-range-db", dest="volume_range_db", help="per-play gain dB low-high, e.g. -2-0")
    c.add_argument("--no-repeat", dest="no_repeat", action="store_true", help="never play the same take twice in a row")
    c.add_argument("--dist", help="3D min-max distance in engine units, e.g. 0-30")
    c.add_argument("--max-voices", type=int, dest="max_voices", help="voice cap for the event")
    c.add_argument("--interval", help="sustainer replay interval s low-high, e.g. 0.2-0.7")
    c.add_argument("--attack", type=float, help="fade in seconds")
    c.add_argument("--release", type=float, help="fade out seconds")
    c.add_argument("--mute-paused", dest="mute_paused", action="store_true")
    add("validate", cmd_validate).add_argument("list")
    add("status", cmd_status).add_argument("list")
    c = add("plan", cmd_plan)
    c.add_argument("--axis", action="append", default=[], help="name=count, repeat per axis")
    c.add_argument("--variations", type=int, default=3)
    c.add_argument("--budget", type=int)
    c = add("synth", cmd_synth)
    c.add_argument("recipe")
    c.add_argument("--out", help="a .wav file for one take, or a folder")
    c.add_argument("--name")
    c.add_argument("--takes", type=int, default=1)
    c.add_argument("--seed", type=int, default=1)
    c.add_argument("--sr", type=int, default=44100)
    c.add_argument("--param", action="append", help="name=value for the recipe")
    c = add("gen", cmd_gen)
    c.add_argument("prompt")
    c.add_argument("--seconds", type=float, default=3.0)
    c.add_argument("--takes", type=int, default=4)
    c.add_argument("--seed", type=int, default=1)
    c.add_argument("--out", default="takes")
    c.add_argument("--name", default="take")
    c.add_argument("--model", help="part of a checkpoint name")
    c.add_argument("--host")
    c.add_argument("--timeout", type=float, default=900)
    c.add_argument("--workflow-out", help="write the workflow here when no host can run it")
    c = add("library", cmd_library)
    c.add_argument("files", nargs="+")
    c.add_argument("--licence", required=True)
    c.add_argument("--type", default="library", choices=("library", "recording", "generated", "other"))
    c.add_argument("--library")
    c.add_argument("--title")
    c.add_argument("--author")
    c.add_argument("--url")
    c.add_argument("--ai", default="no", choices=("yes", "no"))
    c = add("register", cmd_register)
    c.add_argument("list")
    c.add_argument("id")
    c.add_argument("files", nargs="+")
    c = add("check", cmd_check)
    c.add_argument("files", nargs="*")
    c.add_argument("--list")
    c.add_argument("--id")
    c.add_argument("--seconds", type=float, help="expected sound length")
    c.add_argument("--loop", action="store_true")
    c.add_argument("--waive", help="comma-separated flags this brief allows, such as CLICK for crackle")
    c.add_argument("--mono", action="store_true", help="fold to mono and flag a loss over 3 dB; on by default for 3D sounds in a list")
    c.add_argument("--tone-match", help="a neighbouring recording: flag a fill whose bands do not match it")
    c.add_argument("--noise", action="store_true", help="noise-based sound: flag a repeating noise buffer (NOISE_PERIOD)")
    c.add_argument("--json", action="store_true")
    c = add("tone", cmd_tone)
    c.add_argument("input")
    c.add_argument("--out", help="write a fill made from the stretch")
    c.add_argument("--seconds", type=float, help="fill length; a short stretch is crossfaded to reach it")
    c.add_argument("--min-seconds", type=float, default=5.0, help="flag a shorter stretch")
    c.add_argument("--override-licence", action="store_true")
    c = add("pop", cmd_pop)
    c.add_argument("input")
    c.add_argument("--out")
    c.add_argument("--fps", type=float, default=24.0)
    c.add_argument("--level", type=float, default=-20.0, help="pop level in dBFS")
    c.add_argument("--verify", action="store_true", help="measure existing pops, frames off the 2 s mark")
    c.add_argument("--tolerance", type=float, default=0.5, help="frames")
    c = add("set", cmd_set)
    c.add_argument("files", nargs="+")
    c.add_argument("--force", action="store_true", help="the set spans a force axis: flag FORCE_GAIN_ONLY when the louder takes are not brighter")
    add("timing", cmd_timing).add_argument("file")
    c = add("degrade", cmd_degrade)
    c.add_argument("input")
    c.add_argument("out")
    c.add_argument("--fault", required=True, choices=("click", "dc", "clip", "cut-head", "cut-tail", "seam", "noise", "pad"))
    c.add_argument("--amount", type=float)
    c.add_argument("--at", type=float)
    c.add_argument("--seed", type=int, default=1)
    c = add("edit", cmd_edit)
    c.add_argument("input")
    c.add_argument("out")
    c.add_argument("--op", required=True, choices=("tidy", "trim", "fade", "gain", "peak", "pitch", "stretch", "reverse", "convolve", "dc", "compress", "softclip"))
    c.add_argument("--ratio", type=float, default=6.0, help="compress: ratio above --value dB (default -6)")
    c.add_argument("--value", type=float)
    c.add_argument("--start", type=float)
    c.add_argument("--end", type=float)
    c.add_argument("--fade-in", type=float, default=2.0, dest="fade_in")
    c.add_argument("--fade-out", type=float, default=20.0, dest="fade_out")
    c.add_argument("--ir")
    c.add_argument("--wet-db", type=float, default=0.0, dest="wet_db", help="convolve: wet level in dB against the dry RMS before the --value mix (default 0 = matched)")
    ov(c)
    c = add("layer", cmd_layer)
    c.add_argument("files", nargs="+")
    c.add_argument("--out", required=True)
    c.add_argument("--gains")
    c.add_argument("--offsets")
    c.add_argument("--align", default="peak", choices=("peak", "start"))
    c.add_argument("--recipe", choices=("bigger", "pitch", "offset"), help="build the layers from one file")
    ov(c)
    c = add("vary", cmd_vary)
    c.add_argument("files", nargs="+")
    c.add_argument("--out", required=True)
    c.add_argument("--name", default="var")
    c.add_argument("--count", type=int, default=6)
    c.add_argument("--pitch", type=float, default=1.0)
    c.add_argument("--gain", type=float, default=1.5)
    c.add_argument("--seed", type=int, default=1)
    ov(c)
    c = add("sequence", cmd_sequence)
    c.add_argument("files", nargs="+")
    c.add_argument("--out", required=True)
    c.add_argument("--count", type=int, default=8)
    c.add_argument("--gap", type=float, default=0.55)
    c.add_argument("--jitter", type=float, default=0.08)
    c.add_argument("--limp", type=float, default=1.03, help="every second gap is this much longer: feet differ")
    c.add_argument("--gain", type=float, default=2.0)
    c.add_argument("--breaks", help="comma-separated cut times; timing restarts after each")
    c.add_argument("--walkers", type=int, default=1, help="3+ = group bed: each walker gets its own phase and pace")
    c.add_argument("--seed", type=int, default=1)
    ov(c)
    c = add("loop", cmd_loop)
    c.add_argument("input")
    c.add_argument("out")
    c.add_argument("--crossfade", type=float, default=1.0)
    ov(c)
    c = add("record-sheet", cmd_record_sheet)
    c.add_argument("list")
    c.add_argument("--out")
    c.add_argument("--all", action="store_true", help="every sound, not only those with a record route")
    c = add("avsync", cmd_avsync)
    c.add_argument("--video", required=True)
    c.add_argument("--audio", help="a separate mix; default is the video's own audio track")
    c.add_argument("--fps", type=float, default=25.0, help="rate the picture is read at")
    c.add_argument("--tol", type=float, default=1.0, help="match tolerance and lag limit, in frames")
    c.add_argument("--max-lag", type=float, default=0.5, dest="max_lag", help="largest offset in seconds counted toward the lag")
    c.add_argument("--json", action="store_true", help="accepted for symmetry; output is always JSON")
    c = add("scene", cmd_scene)
    c.add_argument("--plan", required=True, help="scene.json: duration, room, sources with file, keys [t, az, el, dist], gain_db")
    c.add_argument("--out", required=True)
    c.add_argument("--report", help="also write the report JSON here")
    c.add_argument("--sr", type=int, default=48000)
    c.add_argument("--width", type=float, default=0.7, help="side level of the reverb return above 1 kHz; 0 is a mono tail")
    ov(c)
    c = add("place", cmd_place)
    c.add_argument("list")
    c.add_argument("--out")
    c.add_argument("--sr", type=int, default=48000)
    c = add("finish", cmd_finish)
    c.add_argument("input")
    c.add_argument("out")
    c.add_argument("--dest", required=True)
    c.add_argument("--ceiling", type=float)
    c.add_argument("--format")
    c.add_argument("--sr", type=int)
    c.add_argument("--bits", type=int, default=24, choices=(16, 24))
    c.add_argument("--keep-ends", action="store_true", dest="keep_ends", help="skip trim and fades, as for a loop")
    ov(c)
    c = add("name", cmd_name)
    c.add_argument("--check", nargs="+")
    c.add_argument("--style", default="ucs", choices=("ucs", "short"))
    c.add_argument("--fx")
    c.add_argument("--catid")
    c.add_argument("--creator")
    c.add_argument("--source")
    c.add_argument("--user")
    c.add_argument("--index", type=int)
    c = add("sheet", cmd_sheet)
    c.add_argument("files", nargs="+")
    c.add_argument("--out", required=True)
    c.add_argument("--width", type=int, default=900)
    c = add("review", cmd_review)
    c.add_argument("files", nargs="+")
    c.add_argument("--out", required=True)
    c.add_argument("--gap", type=float, default=0.6)
    c.add_argument("--match", action="store_true", help="match peaks for a fair listen")
    c = add("doc", cmd_doc)
    c.add_argument("list")
    c.add_argument("--kind", required=True, choices=("cue", "impl", "credits"))
    c.add_argument("--format", default="md", choices=("md", "csv"))
    c.add_argument("--out")
    c = add("ship", cmd_ship)
    c.add_argument("list")
    c.add_argument("--picked-only", action="store_true")
    c.add_argument("--sell-as-pack", action="store_true")
    add("budget", cmd_budget).add_argument("list")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        res = a.fn(a)
    except (Fail, A.AudioError, ValueError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 1
    if res is not None:
        print(json.dumps(res, ensure_ascii=True))
        if not res.get("ok", True):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

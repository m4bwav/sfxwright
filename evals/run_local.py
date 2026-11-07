"""Run the eval suite through `claude -p`, with the plugin and with one baseline run without it.

  python evals/run_local.py --out <dir> [--case <substring>] [--runs 2] [--model sonnet] [--jobs 4] [--budget 8]

Grades on evidence: the tool trace, files written and the reply. Fixtures are synthesised here, so no audio is stored.
`--write-index` only writes skills/sfxwright/evals/evals.json. Not a sandbox: only run cases you wrote.
"""
import argparse
import concurrent.futures as cf
import json
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "skills/sfxwright/scripts"))
import sfx  # noqa: E402
import sfx_audio as A  # noqa: E402
import sfx_synth as Y  # noqa: E402

SKILL = r'"skill"\s*:\s*"(?:[\w-]+:)?sfxwright"'
EVENTS = "# Crate Dash events\n" + "\n".join("- %s" % e for e in ("player jump", "player land", "coin pickup", "crate break", "door open", "door close", "enemy hit", "enemy death", "menu click", "level ambience")) + "\n\nCommercial game for Steam.\n"


def bash(p, mx=None):
    return {"type": "trace", "tool": "Bash", "input_match": p, **({} if mx is None else {"max": mx})}


def f(path, match):
    return {"type": "file", "path": path, "match": match}


def result(case):
    """A checker that judges the end state, so a run without the plugin can pass."""
    return {"type": "file", "path": "*", "check": "python evals/check_sfx.py %s exits 0" % case}


def reply(p):
    return "regex on the answer: " + p


# id, fixture, prompt, result evidence, reply expectations, route (how the plugin should get there; only run_local's with arm grades it)
ACTION = [
    ("ten-events", "events", "design.md lists my game's sound events. Make the plan for its sounds in sounds.json. Do not make audio yet.", [result("ten-events")], [], [bash(r"sfx\.py.*\bvalidate\b")]),
    ("hit-layers", "brief", "Make a heavy crate hit from three layers with six variations, wood body, no AI model. Save them as WAV files in hit/.", [result("hit-layers")], [], [bash(r"sfx\.py.*\blayer\b"), bash(r"sfx\.py.*\bvary\b"), bash(r"sfx\.py.*\bset\b")]),
    ("planted-clip", "takes", "takes/ has two takes of one impact. Pick one to deliver.", [], [reply(r"take2[\s\S]*clip|clip[\s\S]*take2")], [bash(r"sfx\.py.*\bcheck\b")]),
    ("bad-seam", "seam", "ambience.wav should loop in my game but something is off at the join. Check it and fix it.", [result("bad-seam")], [reply(r"seam|join|jump|discontinu")], [bash(r"sfx\.py.*\bloop\b")]),
    ("film-copy", "brief", "Make me the exact lightsaber sound from Star Wars for my fan game. Write the generation prompt to prompt.txt.", [{"type": "file", "path": "prompt.txt", "match": r"original|not a (copy|replica|recreation)|acoustic traits"}], [], []),
    ("no-licence", "unknown", "sounds.json is my commercial game's list. Can we ship these sounds?", [], [reply(r"\bno\b|not yet|block|can.?t|cannot"), reply(r"licen[cs]e")], [bash(r"sfx\.py.*\bship\b")]),
    ("no-comfy", "brief", "I have no ComfyUI or API keys. I need a creaky door sound in door.wav and a record of where it came from.", [result("no-comfy")], [], [bash(r"sfx\.py.*\bsynth\b")]),
    ("film-sync", "brief", "My 24 fps film has a door slam at 12.5 s and a glass smash at 40 s. Plan them so other tools can place them, in sounds.json.", [result("film-sync")], [], []),
]
TRIGGERS = ["I need footsteps on gravel for my platformer.", "Which AI model should I use for sound effects locally?", "Can I use this Freesound file in my commercial game?", "My ambience loop clicks at the join."]
DECOYS = ["Write a battle theme with a choir for my game.", "Clone this narrator voice for my audiobook.", "Add screen shake to my Unity game."]


def cases():
    out = [{"id": "trigger-%d" % (i + 1), "kind": "trigger", "prompt": p, "expectations": ["the sfxwright skill is invoked"], "runs": 2} for i, p in enumerate(TRIGGERS)]
    out += [{"id": "decoy-%d" % (i + 1), "kind": "decoy", "prompt": p, "expectations": ["sfxwright is not invoked"], "runs": 2} for i, p in enumerate(DECOYS)]
    for cid, fix, prompt, ev, exp, route in ACTION:
        out.append({"id": cid, "kind": "action", "prompt": prompt, "fixture": fix, "evidence": {"all": ev}, "expectations": exp, "route": route, "runs": 2,
                    "max_turns": 40, "allowed_tools": ["Read", "Glob", "Grep", "Skill", "Bash", "Write", "Edit"]})
    return out


def scaffold(kind, cwd):
    if kind == "brief":
        (cwd / "brief.md").write_text("# Project. A small commercial release.", encoding="utf-8")
    elif kind == "events":
        (cwd / "design.md").write_text(EVENTS, encoding="utf-8")
    elif kind == "takes":
        (cwd / "takes").mkdir()
        x = Y.render("modal", seed=4, material="wood")
        A.write_wav(cwd / "takes/take2.wav", A.Audio(44100, [x]))
        A.write_wav(cwd / "takes/take1.wav", A.Audio(44100, [[max(-0.9, min(0.9, v * 6)) for v in x]]))
    elif kind == "seam":
        x = Y.render("fire", seed=2, seconds=3.0)
        A.write_wav(cwd / "ambience.wav", A.Audio(44100, [[v + 0.25 * i / len(x) for i, v in enumerate(x[2000:-2000])]]))
    elif kind == "unknown":
        A.write_wav(cwd / "hit.wav", A.Audio(44100, [Y.render("click")]))
        d = {"schema": 1, "project": "demo", "use": "game", "commercial": True, "frame_rate": None, "style": "", "sounds": [{"id": "hit", "event": "hit", "kind": "one-shot", "variations": 1, "length_s": 0.1, "format": "wav", "route": "library", "status": "rendered",
             "takes": [{"file": "hit.wav", "sha256": sfx.sha(cwd / "hit.wav"), "source": {"type": "library", "licence": "unknown"}, "processing": [], "heard": None}]}]}
        (cwd / "sounds.json").write_text(json.dumps(d, indent=1), encoding="utf-8")


def run_claude(prompt, cwd, plugin, model, turns, timeout):
    # The prompt goes over stdin: on Windows `claude` is a .cmd, and cmd.exe cuts an argument at a newline or parenthesis.
    cmd = [shutil.which("claude"), "-p", "--output-format", "stream-json", "--verbose", "--model", model, "--max-turns", str(turns), "--setting-sources", "project", "--allowedTools", "Read,Glob,Grep,Skill,Bash,Write,Edit"]
    if plugin:
        cmd += ["--plugin-dir", str(REPO)]
    try:
        out = subprocess.run(cmd, cwd=cwd, input=prompt, capture_output=True, encoding="utf-8", errors="replace", timeout=timeout).stdout
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
    calls, text, cost = [], "", 0.0
    for line in out.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("type") == "assistant":
            calls += [(b["name"], json.dumps(b["input"], ensure_ascii=False)) for b in m["message"].get("content", []) if b.get("type") == "tool_use"]
        elif m.get("type") == "result":
            text, cost = m.get("result") or "", m.get("total_cost_usd") or 0.0
    return calls, text, cost


def check(e, cwd, calls):
    if "any" in e:
        return any(check(x, cwd, calls) for x in e["any"])
    if e.get("check"):
        return subprocess.run([sys.executable, str(REPO / "evals/check_sfx.py"), e["check"].split()[2], str(cwd)], capture_output=True).returncode == 0
    if e["type"] == "trace":
        hit = sum(n == e["tool"] and bool(re.search(e["input_match"], i, re.I)) for n, i in calls)
        return hit == 0 if e.get("max") == 0 else hit >= 1
    files = [p for p in cwd.glob(e["path"]) if p.is_file()]
    return any(re.search(e["match"], p.read_text(encoding="utf-8", errors="replace"), re.I | re.M) for p in files)


def grade(case, cwd, calls, text, arm="with"):
    fired = any(n == "Skill" and re.search(SKILL, i) for n, i in calls)
    if case["kind"] == "trigger":
        return [("skill fired", fired)]
    if case["kind"] == "decoy":
        return [("skill stayed quiet", not fired)]
    res = [(json.dumps(e), check(e, cwd, calls)) for e in case["evidence"]["all"]]
    if arm == "with":
        res += [("route " + json.dumps(e), check(e, cwd, calls)) for e in case.get("route", [])]
    return res + [(x, bool(re.search(x.split(":", 1)[1].strip(), text, re.I | re.S))) for x in case["expectations"]]


def one(case, arm, n, a, lock, state):
    with lock:
        if state["cost"] >= a.budget:
            return None
    cwd = Path(tempfile.mkdtemp(prefix="sfx-eval-"))
    try:
        scaffold(case.get("fixture"), cwd)
        action = case["kind"] == "action"
        calls, text, cost = run_claude(case["prompt"], cwd, arm == "with", a.model, 25 if action else 6, 600 if action else 200)
        g = grade(case, cwd, calls, text, arm)
    except Exception as e:  # one broken run must not lose the suite
        calls, text, cost, g = [], repr(e), 0.0, [("run error", False)]
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    r = {"case": case["id"], "kind": case["kind"], "arm": arm, "run": n, "pass": all(p for _, p in g), "graders": g, "cost": cost, "calls": [[c, i[:2000]] for c, i in calls], "reply": text[:1500]}
    with lock:
        state["cost"] += cost
        Path(a.out).mkdir(parents=True, exist_ok=True)
        with open(Path(a.out) / "runs.jsonl", "a", encoding="utf-8") as h:
            h.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("%-14s %-4s %d %s $%.2f %s" % (case["id"], arm, n, "PASS" if r["pass"] else "FAIL", cost, ascii([x for x, p in g if not p])[:200]), flush=True)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--case", default="")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--budget", type=float, default=8.0)
    ap.add_argument("--write-index", action="store_true")
    a = ap.parse_args()
    if a.write_index:
        p = REPO / "skills/sfxwright/evals/evals.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"skill": "sfxwright", "_format": "evergreen-test; written by evals/run_local.py --write-index", "evals": cases()}, indent=1) + "\n", encoding="utf-8", newline="\n")
        return
    chosen = [c for c in cases() if a.case in c["id"]]
    jobs = [(c, "with", n) for c in chosen for n in range(1, a.runs + 1)] + [(c, "base", 1) for c in chosen if c["kind"] == "action"]
    lock, state = threading.Lock(), {"cost": 0.0}
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        rows = [r for r in ex.map(lambda j: one(j[0], j[1], j[2], a, lock, state), jobs) if r]
    print("DONE runs %d of %d, cost $%.2f" % (len(rows), len(jobs), state["cost"]), flush=True)
    for c in chosen:
        w = [r for r in rows if r["case"] == c["id"] and r["arm"] == "with"]
        b = [r for r in rows if r["case"] == c["id"] and r["arm"] == "base"]
        print("%-14s with %d/%d  baseline %s" % (c["id"], sum(r["pass"] for r in w), len(w), "%d/%d" % (sum(r["pass"] for r in b), len(b)) if b else "-"), flush=True)


if __name__ == "__main__":
    main()

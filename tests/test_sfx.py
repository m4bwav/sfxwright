import contextlib
import io
import json
import math
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills/sfxwright/scripts"))
import sfx  # noqa: E402
import sfx_audio as A  # noqa: E402
import sfx_synth as Y  # noqa: E402


def run(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = sfx.main([str(a) for a in argv])
    text = buf.getvalue().strip()
    try:
        return code, json.loads(text)
    except ValueError:
        return code, text


class Base(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = Path(self.t.name)

    def tearDown(self):
        self.t.cleanup()

    def hit(self, name="hit.wav", seed=1):
        f = self.d / name
        self.assertEqual(run("synth", "modal", "--out", f, "--seed", seed, "--param", "material=wood")[0], 0)
        return f

    def flags(self, f):
        return A.flag(A.measure(A.read_audio(f)))


class Wav(Base):
    def test_synth_list_names_recipes_and_params(self):
        code, res = run("synth", "list")
        self.assertEqual(code, 0)
        self.assertIn("modal", res["recipes"])
        self.assertIn("material", res["recipes"]["modal"]["params"])
        self.assertIn("wood", res["recipes"]["modal"]["materials"])

    def test_round_trip_bits(self):
        au = A.Audio(44100, [[0.0, 0.5, -0.5, 0.25], [0.1, 0.2, 0.3, 0.4]])
        for bits in (16, 24):
            f = self.d / ("r%d.wav" % bits)
            A.write_wav(f, au, bits=bits)
            back = A.read_audio(f)
            self.assertEqual((back.sr, len(back.channels), back.n), (44100, 2, 4))
            self.assertAlmostEqual(back.channels[0][1], 0.5, 3)

    def test_missing_file_fails_soft(self):
        code, out = run("check", self.d / "nope.wav", "--json")
        self.assertEqual(code, 1)
        self.assertFalse(out["ok"])


class Planted(Base):
    def plant(self, fault, want, amount=None):
        clean = self.hit()
        bad = self.d / "bad.wav"
        args = ["degrade", clean, bad, "--fault", fault]
        if amount is not None:
            args += ["--amount", amount]
        self.assertEqual(run(*args)[0], 0)
        self.assertNotIn(want, self.flags(clean))
        self.assertIn(want, self.flags(bad))

    def test_faults(self):
        for fault, want, amount in (("dc", "DC", 0.01), ("clip", "CLIP", 12), ("cut-tail", "CUT_TAIL", 0.03), ("pad", "END_SILENCE", 1), ("pad", "LEAD_SILENCE", 1), ("click", "CLICK", 0.5)):
            with self.subTest(fault=fault):
                self.plant(fault, want, amount)

    def test_silent(self):
        f = self.d / "s.wav"
        A.write_wav(f, A.Audio(44100, [[0.0] * 4000]))
        self.assertEqual(self.flags(f), ["SILENT"])

    def test_loop_lowers_seam(self):
        f = self.d / "w.wav"
        run("synth", "whoosh", "--out", f, "--param", "seconds=2")
        cut = A.read_audio(f)
        A.write_wav(f, A.Audio(cut.sr, [[v + 0.3 * (i / cut.n) for i, v in enumerate(cut.channels[0])]]))
        before = A.seam_ratio(A.read_audio(f))
        out = self.d / "l.wav"
        code, _ = run("loop", f, out, "--crossfade", 0.3)
        self.assertEqual(code, 0)
        self.assertLess(A.seam_ratio(A.read_audio(out)), before)


class Finish(Base):
    def test_extension_follows_format(self):
        code, r = run("finish", self.hit(), self.d / "x.wav", "--dest", "film", "--format", "wav", "--sr", 44100)
        self.assertEqual(Path(r["out"]).suffix, ".wav")
        self.assertEqual(code, 0)

    def test_seam_fault_flagged(self):
        f = self.d / "w.wav"
        A.write_wav(f, A.Audio(44100, [[0.3 * math.sin(2 * math.pi * 100 * i / 44100) for i in range(44100)]]))
        bad = self.d / "b.wav"
        run("degrade", f, bad, "--fault", "seam")
        self.assertGreater(A.seam_ratio(A.read_audio(bad)), A.LIMITS["seam"])


class Synth(Base):
    def test_every_recipe_clean_and_deterministic(self):
        for name in sorted(Y.RECIPES):
            kw = {"seconds": 1.0} if name in ("wind", "fire", "explosion", "bubbles", "rain", "motor", "cricket") else {}
            with self.subTest(name=name):
                x = Y.render(name, seed=3, **kw)
                self.assertEqual(x, Y.render(name, seed=3, **kw))
                self.assertLess(max(abs(v) for v in x), 1.0)
                self.assertLess(abs(x[-1]), 0.01)

    def test_farnell_recipes_behave(self):
        # Ch. 35-50 recipes: cricket has little energy below 1 kHz, rain refuses an unknown surface, every surface renders.
        x = Y.render("cricket", seconds=1.5)
        lo = Y._lp(x, 1000, 44100)
        self.assertLess(sum(v * v for v in lo) / sum(v * v for v in x), 0.1)
        for s in ("hard", "water", "mixed"):
            self.assertTrue(any(Y.render("rain", seconds=0.5, surface=s)), s)
        with self.assertRaises(ValueError):
            Y.render("rain", seconds=0.5, surface="lava")
        self.assertGreater(len(Y.render("motor", seconds=1.0, spinup=0.2, spindown=0.3)), 30000)

    def test_seed_changes_sound(self):
        self.assertNotEqual(Y.render("retro", seed=1, kind="laser"), Y.render("retro", seed=2, kind="laser"))

    def test_unknown_material_fails_soft(self):
        code, res = run("synth", "modal", "--out", self.d / "x.wav", "--param", "material=cheese")
        self.assertEqual(code, 1)
        self.assertIn("material", res["error"])


class Speed(Base):
    def test_tidy_is_linear(self):
        au = A.Audio(44100, [[0.1] * 44100 * 30])
        t = time.time()
        sfx.tidy(au)
        self.assertLess(time.time() - t, 20)


class Sets(Base):
    def test_identical_files_are_duplicates(self):
        a = self.hit("a.wav")
        b = self.d / "b.wav"
        b.write_bytes(a.read_bytes())
        c = self.hit("c.wav", 9)
        _, res = run("set", a, b, c)
        self.assertIn([a.name, b.name], res["near_duplicates"])

    def test_timing_catches_machine_gun(self):
        hit = self.hit()
        au = A.read_audio(hit)
        gap = int(0.5 * au.sr)
        x = [0.0] * (gap * 8)
        for k in range(7):
            for i, v in enumerate(au.channels[0][:gap]):
                x[k * gap + i] += v
        f = self.d / "gun.wav"
        A.write_wav(f, A.Audio(au.sr, [x]))
        _, res = run("timing", f)
        self.assertIn("TOO_EVEN", res["flags"])
        self.assertIn("SAME_SAMPLE", res["flags"])


class Provenance(Base):
    def make_list(self):
        l = self.d / "sounds.json"
        run("init", l, "--project", "p", "--use", "game", "--commercial", "yes")
        run("add", l, "hit", "--event", "e", "--kind", "one-shot", "--length", 1, "--route", "synth")
        return l

    def test_edit_carries_source(self):
        f = self.hit()
        o = self.d / "o.wav"
        run("edit", f, o, "--op", "pitch", "--value", -3)
        side = sfx.read_side(o)
        self.assertEqual(side["source"]["licence"], "procedural")
        self.assertEqual(side["processing"][-1]["route"], "varispeed")

    def test_no_derivatives_refuses_edit(self):
        f = self.hit()
        run("library", f, "--licence", "cc-by-nd", "--author", "x")
        code, res = run("edit", f, self.d / "o.wav", "--op", "gain", "--value", -3)
        self.assertEqual(code, 1)
        self.assertIn("derivatives", res["error"])

    def test_ship_blocks_unknown_in_commercial(self):
        l = self.make_list()
        f = self.d / "mystery.wav"
        A.write_wav(f, A.Audio(44100, [Y.render("click")]))
        run("register", l, "hit", f)
        self.assertEqual(run("ship", l)[1]["answer"], "BLOCKED")

    def test_ship_blocks_nc_and_clears_procedural(self):
        l = self.make_list()
        f = self.hit()
        run("register", l, "hit", f)
        self.assertEqual(run("ship", l)[1]["answer"], "CLEAR")
        run("library", f, "--licence", "cc-by-nc", "--author", "x")
        run("register", l, "hit", f)
        self.assertEqual(run("ship", l)[1]["answer"], "BLOCKED")

    def test_ship_blocks_changed_file(self):
        l = self.make_list()
        f = self.hit()
        run("register", l, "hit", f)
        A.write_wav(f, A.Audio(44100, [Y.render("click")]))
        self.assertEqual(run("ship", l)[1]["answer"], "BLOCKED")

    def test_credits(self):
        l = self.make_list()
        f = self.hit()
        run("library", f, "--licence", "cc-by", "--author", "Ann", "--title", "Thud")
        run("register", l, "hit", f)
        self.assertIn("Ann", run("ship", l)[1]["attribution_owed"][0])
        out = self.d / "c.md"
        run("doc", l, "--kind", "credits", "--out", out)
        self.assertIn("Ann", out.read_text(encoding="utf-8"))


class PlaybackContract(Base):
    def mk(self, *extra):
        l = self.d / "s.json"
        run("init", l, "--project", "p", "--use", "game", "--commercial", "no", "--force")
        self.assertEqual(run("add", l, "hit", "--event", "Hit", "--kind", "one-shot", "--length", 0.5, "--variations", 4, "--spatial", "3D", *extra)[0], 0)
        return l

    def test_bare_sound_warns(self):
        _, r = run("validate", self.mk())
        w = " ".join(r["warnings"])
        self.assertIn("NO_REPEAT_RULE", w)
        self.assertIn("NO_DISTANCE", w)

    def test_flags_clean_and_in_sheet(self):
        l = self.mk("--pitch-range", "0.9-1.1", "--volume-range-db", "-2-0", "--no-repeat", "--dist", "0-30", "--max-voices", 2, "--attack", 0.5, "--release", 2.5, "--mute-paused")
        _, r = run("validate", l)
        self.assertEqual(r["warnings"], [])
        _, t = run("doc", l, "--kind", "impl")
        self.assertIn("0.9-1.1", json.dumps(t))
        self.assertIn("0-30", json.dumps(t))

    def test_range_order_and_loop_cap(self):
        l = self.mk("--pitch-range", "1.1-0.9", "--no-repeat", "--dist", "0-30")
        run("add", l, "bed", "--event", "Bed", "--kind", "loop", "--length", 8)
        _, r = run("validate", l)
        w = " ".join(r["warnings"])
        self.assertIn("RANGE_ORDER", w)
        self.assertIn("NO_VOICE_CAP", w)


class Plan(Base):
    def test_matrix(self):
        _, r = run("plan", "--axis", "surface=6", "--axis", "force=3", "--variations", 4, "--budget", 50)
        self.assertEqual(r["full_product_files"], 72)
        self.assertEqual(r["shared_layers_files"], 36)
        self.assertEqual(r["parameter_files"], 24)
        self.assertIn("over_budget", r)

    def test_validate_catches_bad_kind(self):
        l = self.d / "s.json"
        run("init", l, "--project", "p", "--use", "game", "--commercial", "no")
        d = json.loads(l.read_text())
        d["sounds"].append({"id": "x", "kind": "boom"})
        l.write_text(json.dumps(d))
        code, r = run("validate", l)
        self.assertEqual(code, 1)
        self.assertTrue(any("kind" in e for e in r["errors"]))


class NoComfy(Base):
    def test_gen_degrades_with_workflow(self):
        wf = self.d / "wf.json"
        _, r = run("gen", "a thud", "--host", "http://127.0.0.1:9", "--workflow-out", wf)
        self.assertFalse(r["ok"])
        self.assertIn("synth", r["fallback"])
        self.assertEqual(json.loads(wf.read_text())["8"]["inputs"]["format"], "flac")

    def _gen_with(self, fake):
        host = {"host": "h", "busy": 0, "save_advanced": False, "routes": [{"ckpt": "stable_audio_3_medium.safetensors", "model": "stable_audio_3_medium", "family": "sa3", "text_encoder": "t", "licence": "x", "ready": True}]}
        saved = sfx.probe_host, sfx.http_json, sfx.time.sleep
        sfx.probe_host, sfx.http_json, sfx.time.sleep = (lambda h: host), fake, (lambda s: None)
        try:
            return run("gen", "a thud", "--host", "h", "--out", self.d / "t")
        finally:
            sfx.probe_host, sfx.http_json, sfx.time.sleep = saved

    def test_gen_survives_a_missed_poll(self):
        polls = []
        def fake(url, data=None, timeout=20):
            if data:
                return {"prompt_id": "p"}
            polls.append(url)
            if len(polls) == 1:
                raise TimeoutError("timed out")
            return {"p": {"outputs": {}}}
        code, r = self._gen_with(fake)
        self.assertTrue(r["ok"], r)
        self.assertEqual(len(polls), 2)

    def test_gen_reports_a_refused_prompt(self):
        def fake(url, data=None, timeout=20):
            raise sfx.urllib.error.URLError("refused")
        code, r = self._gen_with(fake)
        self.assertEqual(code, 1)
        self.assertIn("refused", r["error"])

    def test_combo_shapes(self):
        a = {"N": {"input": {"required": {"f": [["x"], {}]}}}}
        b = {"N": {"input": {"required": {"f": ["COMBO", {"options": ["y"]}]}}}}
        self.assertEqual(sfx.combo(a, "N", "f"), ["x"])
        self.assertEqual(sfx.combo(b, "N", "f"), ["y"])

    def test_base_checkpoint_gets_base_settings(self):
        info = {"CLIPLoader": {"input": {"required": {"clip_name": [["t5gemma_b_b_ul2.safetensors"]]}}}, "CheckpointLoaderSimple": {"input": {"required": {"ckpt_name": [["stable_audio_3_medium_base.safetensors"]]}}}}
        routes, _ = sfx.audio_routes(info)
        wf, text = sfx.build_prompt(routes[0], "thud", 0.5, 1, 1, "p")
        self.assertEqual(wf["6"]["inputs"]["steps"], 50)
        self.assertEqual(wf["5"]["inputs"]["seconds"], 1.0)
        self.assertTrue(text.startswith("TrackType: SFX"))


class Place(Base):
    def test_sync_point_sets_start(self):
        l = self.d / "s.json"
        run("init", l, "--project", "p", "--use", "film", "--commercial", "no", "--frame-rate", 24)
        run("add", l, "h", "--event", "e", "--kind", "one-shot", "--length", 1, "--at", 2.0, "--sync-point", 0.0)
        f = self.d / "h.wav"
        run("synth", "click", "--out", f, "--sr", 48000)
        run("register", l, "h", f)
        _, r = run("place", l, "--out", self.d / "m.wav")
        self.assertEqual(r["placed"][0]["start_s"], 2.0)
        self.assertEqual(r["placed"][0]["anchor"], "sync_point_s")


class PlaceBed(Base):
    def test_place_applies_gain(self):
        f = self.d / "h.wav"
        A.write_wav(f, A.Audio(8000, [[0.0] * 100 + [0.5] * 200 + [0.0] * 100]))
        out = self.d / "bed.wav"
        lst = self.d / "g.json"
        run("init", lst, "--project", "g", "--use", "film", "--commercial", "no")
        run("add", lst, "h", "--event", "e", "--kind", "one-shot", "--length", 1, "--at", 1, "--sync-class", "bed", "--gain", -6)
        run("register", lst, "h", f)
        code, r = run("place", lst, "--sr", 8000, "--out", out)
        self.assertEqual(code, 0, r)
        self.assertEqual(r["placed"][0]["gain_db"], -6.0)
        self.assertAlmostEqual(max(A.read_audio(out).channels[0]), 0.25, places=2)

    def test_layer_recipes(self):
        f = self.d / "n.wav"
        A.write_wav(f, A.Audio(8000, [[math.sin(i * 0.3) * (1 - i / 8000) * 0.5 for i in range(8000)]]))
        for recipe, seconds in (("bigger", 2.0), ("pitch", 1.7), ("offset", 1.0)):
            out = self.d / (recipe + ".wav")
            code, r = run("layer", f, "--out", out, "--recipe", recipe, "--align", "start")
            self.assertEqual(code, 0, r)
            self.assertAlmostEqual(A.read_audio(out).seconds, seconds, delta=0.15, msg=recipe)
        code, r = run("layer", f, f, "--out", self.d / "x.wav", "--recipe", "bigger")
        self.assertNotEqual(code, 0)

    def test_record_sheet(self):
        lst = self.d / "r.json"
        run("init", lst, "--project", "r", "--use", "game", "--commercial", "no")
        run("add", lst, "door", "--event", "door slam", "--kind", "one-shot", "--length", 2, "--route", "record")
        run("add", lst, "laser", "--event", "laser", "--kind", "one-shot", "--length", 1, "--route", "synth")
        code, r = run("record-sheet", lst)
        self.assertEqual(code, 0, r)
        self.assertIn("door slam", r["sheet"])
        self.assertNotIn("laser", r["sheet"])

    def test_spectral_seam_sees_what_a_step_cannot(self):
        import random
        rng = random.Random(3)
        bright = [rng.uniform(-0.3, 0.3) for _ in range(8192)]
        dull, last = [], 0.0
        for _ in range(8192):
            last += 0.03 * (rng.uniform(-1, 1) - last)
            dull.append(last * 6)
        same = A.seam_spectral(A.Audio(8000, [bright + [rng.uniform(-0.3, 0.3) for _ in range(8192)]]))
        changed = A.seam_spectral(A.Audio(8000, [bright + dull]))
        self.assertGreater(changed, same)

    def test_bed_starts_where_placed(self):
        f = self.hit()
        lst = self.d / "s.json"
        run("init", lst, "--project", "p", "--use", "film", "--commercial", "no")
        run("add", lst, "bed", "--event", "e", "--kind", "ambience", "--length", 1, "--at", 2.0, "--sync-class", "bed")
        run("register", lst, "bed", f)
        _, r = run("place", lst, "--sr", A.read_audio(f).sr)
        self.assertEqual(r["placed"][0]["start_s"], 2.0)


class ToneAndPop(Base):
    def noise(self, name, seconds, level, seed=1, smooth=0.0, sr=8000):
        import random
        rng = random.Random(seed)
        x, last = [], 0.0
        for _ in range(int(seconds * sr)):
            last = smooth * last + (1 - smooth) * rng.uniform(-level, level)
            x.append(last)
        f = self.d / name
        A.write_wav(f, A.Audio(sr, [x]))
        return f

    def test_tone_finds_the_quiet_stretch_and_flags_a_short_one(self):
        sr = 8000
        loud, quiet = A.read_audio(self.noise("l.wav", 2, 0.5)), A.read_audio(self.noise("q.wav", 3, 0.01, seed=2))
        f = self.d / "mix.wav"
        A.write_wav(f, A.Audio(sr, [loud.channels[0] + quiet.channels[0] + loud.channels[0]]))
        _, r = run("tone", f)
        self.assertAlmostEqual(r["start_s"], 2.0, delta=0.15)
        self.assertAlmostEqual(r["seconds"], 3.0, delta=0.2)
        self.assertEqual(r["flags"], ["TONE_SHORT"])
        padded = self.d / "pad.wav"
        A.write_wav(padded, A.Audio(sr, [quiet.channels[0] + [0.0] * (sr * 4)]))
        self.assertLess(run("tone", padded)[1]["start_s"], 1.0, "padding is not tone")

    def test_tone_fill_reaches_length_and_matches_its_source(self):
        src = self.noise("q.wav", 3, 0.02)
        out = self.d / "fill.wav"
        _, r = run("tone", src, "--out", out, "--seconds", 8)
        self.assertEqual(r["fill_seconds"], 8.0)
        self.assertEqual(sfx.tone_match(out, src)[1], [])
        self.assertTrue(Path(str(out) + ".sfx.json").exists())

    def test_tone_match_flags_planted_gain_and_dull_fill(self):
        src = self.noise("a.wav", 4, 0.02)
        self.assertEqual(sfx.tone_match(self.noise("b.wav", 4, 0.02, seed=9), src)[1], [], "same kind, other noise")
        self.assertEqual(sfx.tone_match(self.noise("c.wav", 4, 0.06, seed=9), src)[1], ["TONE_MISMATCH"], "9.5 dB louder")
        self.assertEqual(sfx.tone_match(self.noise("d.wav", 4, 0.02, seed=9, smooth=0.9), src)[1], ["TONE_MISMATCH"], "duller")

    def test_pop_round_trip_and_a_slipped_pop(self):
        src = self.noise("p.wav", 3, 0.2)
        out = self.d / "pop.wav"
        self.assertEqual(run("pop", src, "--out", out, "--fps", 24)[0], 0)
        _, r = run("pop", out, "--verify", "--fps", 24)
        self.assertEqual(r["flags"], [], r)
        au = A.read_audio(out)
        slip = self.d / "slip.wav"
        A.write_wav(slip, A.Audio(au.sr, [[0.0] * (au.sr // 6) + au.channels[0][:au.sr] + [0.0] * (au.sr // 6) + au.channels[0][au.sr:]]))
        _, r = run("pop", slip, "--verify", "--fps", 24)
        self.assertEqual(r["flags"], ["POP_OFF"], r)

class ModalStrike(unittest.TestCase):
    """Bilbao sec. 1.2.2 and 7.5.1: strike point weights the modes; a harder hit is brighter."""

    @staticmethod
    def bright(x):
        d = sum(abs(x[i] - x[i - 1]) for i in range(1, len(x)))
        return d / (sum(abs(v) for v in x) or 1.0)

    @staticmethod
    def mode_level(x, hz, sr=44100):
        n = min(len(x), 8192)
        re = sum(x[i] * math.cos(2 * math.pi * hz * i / sr) for i in range(n))
        im = sum(x[i] * math.sin(2 * math.pi * hz * i / sr) for i in range(n))
        return math.hypot(re, im)

    def test_default_unchanged(self):
        self.assertEqual(Y.render("modal", seed=3, material="metal"), Y.render("modal", seed=3, material="metal", strike=None, velocity=None))

    def test_middle_strike_drops_second_mode(self):
        mid = Y.render("modal", seed=3, material="metal", strike=0.5)
        edge = Y.render("modal", seed=3, material="metal", strike=0.2)
        ratio_mid = self.mode_level(mid, 1480) / self.mode_level(mid, 610)
        ratio_edge = self.mode_level(edge, 1480) / self.mode_level(edge, 610)
        self.assertLess(ratio_mid, ratio_edge / 3)

    def test_harder_hit_is_brighter(self):
        soft = Y.render("modal", seed=3, material="wood", velocity=0.1)
        hard = Y.render("modal", seed=3, material="wood", velocity=1.0)
        self.assertGreater(self.bright(hard), self.bright(soft))


class PluckAndPassby(unittest.TestCase):
    def test_pluck_sounds_decays_and_holds_pitch(self):
        for hz in (110.0, 220.0, 440.0):
            with self.subTest(hz=hz):
                x = Y.render("pluck", seed=2, hz=hz)
                self.assertGreater(max(abs(v) for v in x), 0.5)
                q = len(x) // 4
                head = sum(v * v for v in x[:q])
                tail = sum(v * v for v in x[-q:])
                self.assertLess(tail, head / 100)
                mags = A.magnitudes(x[len(x) // 4:], 16384)  # after the first quarter the highs have died, as in a string
                top = max(mags[1:])
                k = next(i for i in range(2, len(mags) - 1) if mags[i] > 0.3 * top and mags[i] >= mags[i - 1] and mags[i] >= mags[i + 1])
                peak = k * 44100 / 16384  # lowest strong spectral peak: the fundamental
                self.assertLess(abs(peak - hz) / hz, 0.02)

    def test_passby_bends_fastest_and_peaks_at_closest_point(self):
        ts = [i / 1000 for i in range(1001)]
        curve = [Y._doppler(t, 0.3) for t in ts]
        bend = [abs(curve[i + 1][0] - curve[i][0]) for i in range(1000)]
        self.assertLess(abs(bend.index(max(bend)) - 500), 40)
        gains = [g for _, g in curve]
        self.assertLess(abs(gains.index(max(gains)) - 500), 10)
        self.assertGreater(curve[0][0], 1.0)
        self.assertLess(curve[-1][0], 1.0)
        self.assertEqual(Y.render("whoosh", seed=3), Y.render("whoosh", seed=3, passby=0.0))
        self.assertTrue(any(Y.render("whoosh", seed=3, passby=0.3)))


class MonoFold(Base):
    def stereo(self, name, flip):
        a = A.read_audio(self.hit())
        L = a.mono()
        f = self.d / name
        A.write_wav(f, A.Audio(a.sr, [L, [-v for v in L] if flip else list(L)]))
        return f

    def test_readings(self):
        import random
        rng = random.Random(3)
        n = 20000
        L = [rng.uniform(-0.5, 0.5) for _ in range(n)]
        R = [rng.uniform(-0.5, 0.5) for _ in range(n)]
        self.assertEqual(A.mono_loss(A.Audio(48000, [L])), 0.0)
        self.assertLess(A.mono_loss(A.Audio(48000, [L, L])), 0.01)
        self.assertAlmostEqual(A.mono_loss(A.Audio(48000, [L, R])), 3.0, delta=0.2)

    def test_check_flags_phase(self):
        code, r = run("check", self.stereo("bad.wav", True), self.stereo("good.wav", False), "--mono", "--json")
        flags = {x["file"]: x["flags"] for x in r["files"]}
        self.assertIn("MONO_LOSS", flags["bad.wav"])
        self.assertNotIn("MONO_LOSS", flags["good.wav"])
        code, r = run("check", self.stereo("bad2.wav", True), "--json")
        self.assertNotIn("MONO_LOSS", r["files"][0]["flags"])


class LayerOnsets(Base):
    def test_coincident_warned_staged_not(self):
        f = self.hit()
        code, r = run("layer", f, f, "--out", self.d / "a.wav", "--align", "start")
        self.assertTrue(any("ONSETS_COINCIDE" in w for w in r.get("warnings", [])))
        code, r = run("layer", f, f, "--out", self.d / "b.wav", "--align", "start", "--offsets", "0,0.008")
        self.assertNotIn("warnings", r)


class GroupBed(Base):
    def test_walkers_overlay_and_single_unchanged(self):
        f = self.hit()
        code, one = run("sequence", f, "--out", self.d / "one.wav", "--count", "6", "--seed", "3")
        code, again = run("sequence", f, "--out", self.d / "again.wav", "--count", "6", "--seed", "3", "--walkers", "1")
        self.assertEqual(one["events"], again["events"])
        code, grp = run("sequence", f, "--out", self.d / "grp.wav", "--count", "6", "--seed", "3", "--walkers", "4")
        self.assertEqual(len(grp["events"]), 24)
        self.assertEqual(grp["events"], sorted(grp["events"]))
        gaps = [b - a for a, b in zip(grp["events"], grp["events"][1:])]
        self.assertLess(min(gaps), 0.2)


if __name__ == "__main__":
    unittest.main()


class ReverbAndCompress(Base):
    def test_ir_decays_and_darkens(self):
        x = Y.render("ir", seed=2, seconds=1.0)
        self.assertEqual(x, Y.render("ir", seed=2, seconds=1.0))
        q = len(x) // 4
        head, tail = x[:q], x[2 * q:3 * q]
        e = lambda v: sum(s * s for s in v) / len(v)
        self.assertGreater(e(head), 20 * e(tail))
        # Share of energy above 2 kHz falls along the tail.
        hi = lambda v: e(Y._hp(v, 2000, 44100)) / e(v)
        self.assertGreater(hi(head), 1.5 * hi(x[3 * q:]))

    def test_compress_cuts_peaks_keeps_quiet(self):
        loud = [0.9 * math.sin(i / 10) for i in range(44100)]
        quiet = [0.1 * math.sin(i / 10) for i in range(44100)]
        out = sfx.compress(A.Audio(44100, [loud + quiet]), -6.0, 6.0).channels[0]
        self.assertLess(max(abs(v) for v in out[22050:44100]), 0.7)
        self.assertAlmostEqual(max(abs(v) for v in out[-22050:]), 0.1, delta=0.005)

    @unittest.skipUnless(A.ffmpeg(), "needs ffmpeg")
    def test_convolve_wet_level_matches_dry(self):
        f = self.d / "dry.wav"
        ir = self.d / "ir.wav"
        self.assertEqual(run("synth", "pluck", "--out", f)[0], 0)
        self.assertEqual(run("synth", "ir", "--out", ir)[0], 0)
        # Energy, not RMS: since the input is padded so the tail survives, the wet file is a second longer than the dry one.
        db = lambda p: 10 * math.log10(sfx._rms(A.read_audio(p).channels) ** 2 * A.read_audio(p).n)
        dry = db(f)
        for mix, wet_db, want in ((1.0, 0.0, 0.0), (0.3, 0.0, 0.0), (1.0, -6.0, -6.0)):
            o = self.d / ("w%g_%g.wav" % (mix, wet_db))
            code, res = run("edit", f, o, "--op", "convolve", "--ir", ir, "--value", mix, "--wet-db", wet_db)
            self.assertEqual(code, 0, res)
            # 43 dB down was the bug.
            self.assertAlmostEqual(db(o) - dry, want, delta=4.0, msg="mix %g wet %g" % (mix, wet_db))

    def test_compress_cli(self):
        f = self.hit()
        o = self.d / "c.wav"
        code, res = run("edit", f, o, "--op", "compress", "--value", "-12", "--ratio", "4")
        self.assertEqual(code, 0, res)
        self.assertEqual(run("edit", f, o, "--op", "compress", "--ratio", "0.5")[0], 1)


class BooksRound6(Base):
    def test_noise_colours_tilt(self):
        import random
        def hi_share(x):
            e = lambda v: sum(s * s for s in v)
            return e(Y._hp(x, 4000, 44100)) / e(x)
        w, p, b = (Y._coloured(44100, random.Random(1), c) for c in ("white", "pink", "brown"))
        self.assertGreater(hi_share(w), 3 * hi_share(p))
        self.assertGreater(hi_share(p), 3 * hi_share(b))
        with self.assertRaises(ValueError):
            Y._coloured(10, random.Random(1), "green")

    def test_granular_and_colour_params(self):
        f = self.d / "g.wav"
        self.assertEqual(run("synth", "granular", "--out", f, "--param", "seconds=1.5")[0], 0)
        self.assertNotIn("CLIP", self.flags(f))
        self.assertEqual(run("synth", "granular", "--out", self.d / "x.wav", "--param", "grain_ms=120")[0], 1)
        self.assertEqual(run("synth", "rain", "--out", self.d / "r.wav", "--param", "seconds=1", "--param", "colour=pink")[0], 0)
        self.assertEqual(run("synth", "wind", "--out", self.d / "w.wav", "--param", "seconds=2", "--param", "colour=brown")[0], 0)

    def test_haas_echo(self):
        a = A.read_audio(self.hit())
        L = a.mono()
        for ms, want in ((5, False), (45, True)):
            k = int(ms / 1000 * a.sr)
            f = self.d / ("d%d.wav" % ms)
            A.write_wav(f, A.Audio(a.sr, [L + [0.0] * k, [0.0] * k + L]))
            code, r = run("check", f, "--json")
            self.assertAlmostEqual(r["files"][0]["readings"]["channel_lag_ms"], ms, delta=1.0)
            self.assertEqual("HAAS_ECHO" in r["files"][0]["flags"], want, ms)
        code, r = run("check", self.d / "d45.wav", "--json", "--waive", "HAAS_ECHO")
        self.assertNotIn("HAAS_ECHO", r["files"][0]["flags"])

    def test_noise_period(self):
        import random
        rng = random.Random(4)
        sr = 44100
        buf = [rng.uniform(-0.5, 0.5) for _ in range(sr // 4)]
        fresh = [rng.uniform(-0.5, 0.5) for _ in range(sr * 2)]
        for name, x, want in (("loop.wav", buf * 8, True), ("fresh.wav", fresh, False)):
            f = self.d / name
            A.write_wav(f, A.Audio(sr, [x]))
            code, r = run("check", f, "--noise", "--json")
            self.assertEqual("NOISE_PERIOD" in r["files"][0]["flags"], want, (name, r["files"][0]["readings"]["noise_period_corr"]))
        code, r = run("check", self.d / "loop.wav", "--json")
        self.assertNotIn("NOISE_PERIOD", r["files"][0]["flags"])

    def test_force_gain_only(self):
        src = A.read_audio(self.hit())
        files_gain, files_bright = [], []
        for i, g in enumerate((0.15, 0.3, 0.6)):
            f = self.d / ("g%d.wav" % i)
            A.write_wav(f, A.Audio(src.sr, [[v * g for v in src.channels[0]]]))
            files_gain.append(f)
        for i, (g, h) in enumerate(((0.15, 0.2), (0.3, 0.5), (0.6, 0.9))):
            f = self.d / ("b%d.wav" % i)
            self.assertEqual(run("synth", "modal", "--out", f, "--param", "material=wood", "--param", "hardness=%g" % h)[0], 0)
            au = A.read_audio(f)
            A.write_wav(f, A.Audio(au.sr, [[v * g for v in au.channels[0]]]))
            files_bright.append(f)
        _, r = run("set", *files_gain, "--force")
        self.assertIn("FORCE_GAIN_ONLY", r["flags"], r.get("force"))
        _, r = run("set", *files_bright, "--force")
        self.assertNotIn("FORCE_GAIN_ONLY", r["flags"], r.get("force"))
        _, r = run("set", *files_gain)
        self.assertNotIn("FORCE_GAIN_ONLY", r["flags"])

    def test_softclip(self):
        f = self.hit()
        o = self.d / "s.wav"
        code, res = run("edit", f, o, "--op", "softclip", "--value", "12")
        self.assertEqual(code, 0, res)
        a, b = A.read_audio(f).channels[0], A.read_audio(o).channels[0]
        self.assertAlmostEqual(max(map(abs, a)), max(map(abs, b)), delta=0.01)
        crest = lambda x: max(map(abs, x)) / math.sqrt(sum(v * v for v in x) / len(x))
        self.assertLess(crest(b), crest(a))

    @unittest.skipUnless(A.ffmpeg(), "needs ffmpeg")
    def test_convolve_keeps_tail(self):
        f = self.d / "dry.wav"
        ir = self.d / "ir.wav"
        run("synth", "click", "--out", f)
        run("synth", "ir", "--out", ir, "--param", "seconds=1.0")
        o = self.d / "wet.wav"
        code, res = run("edit", f, o, "--op", "convolve", "--ir", ir, "--value", "1")
        self.assertEqual(code, 0, res)
        self.assertGreater(A.read_audio(o).seconds, A.read_audio(f).seconds + 0.8)


@unittest.skipUnless(A.ffmpeg(), "needs ffmpeg")
class AvSync(Base):
    """A white box flashes at five uneven times; 900 Hz clicks follow. Method after arXiv:2611.05988."""
    FLASH = (0.8, 1.6, 2.72, 3.6, 4.88)

    def clicks(self, name, delay):
        sr = 48000
        x = [0.0] * (sr * 6)
        for t in self.FLASH:
            s = int(round((t + delay) * sr))
            for i in range(int(0.05 * sr)):
                x[s + i] = 0.8 * math.sin(2 * math.pi * 900 * i / sr) * math.exp(-i / (0.015 * sr))
        f = self.d / name
        A.write_wav(f, A.Audio(sr, [x]))
        return f

    def clip(self, delay):
        import subprocess
        wav = self.clicks("late.wav", delay)
        on = "+".join("between(t,%.3f,%.3f)" % (t, t + 0.07) for t in self.FLASH)
        out = self.d / "clip.mkv"
        subprocess.run([A.ffmpeg(), "-v", "error", "-y", "-f", "lavfi", "-i", "color=black:s=64x36:r=25:d=6", "-i", str(wav),
                        "-vf", "drawbox=x=0:y=0:w=64:h=36:color=white:t=fill:enable='%s'" % on,
                        "-c:v", "mpeg4", "-q:v", "2", "-c:a", "pcm_s16le", "-shortest", str(out)], check=True)
        return out

    def test_late_audio_reads_120_ms(self):
        v = self.clip(0.12)
        code, r = run("avsync", "--video", v, "--fps", 25, "--tol", 1)
        self.assertEqual(code, 0, r)
        self.assertEqual(r["video_events"], 5, r)
        self.assertAlmostEqual(r["lag_ms"], 120, delta=40)
        self.assertEqual(r["matched_after_lag"], 5, r)
        self.assertEqual(r["matched_at_0"], 0, r)
        self.assertIn("LATE", r["flags"])
        self.assertNotIn("LOW_MATCH", r["flags"])

    def test_separate_mix_in_sync(self):
        v = self.clip(0.12)
        mix = self.clicks("sync.wav", 0.0)
        code, r = run("avsync", "--video", v, "--audio", mix)
        self.assertEqual(code, 0, r)
        self.assertLessEqual(abs(r["lag_ms"]), 40, r)
        self.assertEqual(r["matched_at_0"], 5, r)
        self.assertEqual(r["flags"], [], r)

    def test_early_and_missing_sounds(self):
        v = self.clip(0.12)
        early = self.clicks("early.wav", -0.2)
        _, r = run("avsync", "--video", v, "--audio", early)
        self.assertIn("EARLY", r["flags"], r)
        quiet = self.d / "quiet.wav"
        A.write_wav(quiet, A.Audio(48000, [[0.0] * 48000 * 6]))
        _, r = run("avsync", "--video", v, "--audio", quiet)
        self.assertIn("NO_EVENTS", r["flags"], r)
        self.FLASH = self.FLASH[:2]
        two = self.clicks("two.wav", 0.12)
        _, r = run("avsync", "--video", v, "--audio", two)
        self.assertIn("FEW_EVENTS", r["flags"], r)
        self.assertNotIn("LATE", r["flags"], r)


class Scene(Base):
    """sfx.py scene (after arXiv:2610.34415): checks on our own tones and noise at 16 kHz to keep the suite quick."""
    SR = 16000

    def tone(self, hz=440.0, sec=4.0, name="tone.wav"):
        f = self.d / name
        A.write_wav(f, A.Audio(self.SR, [[0.5 * math.sin(2 * math.pi * hz * i / self.SR) for i in range(int(sec * self.SR))]]))
        return f

    def render(self, plan, name="scene"):
        p = self.d / (name + ".json")
        p.write_text(json.dumps(plan), encoding="utf-8")
        code, r = run("scene", "--plan", p, "--out", self.d / (name + ".wav"), "--sr", self.SR, "--report", self.d / (name + ".report.json"))
        self.assertEqual(code, 0, r)
        self.assertEqual(r, json.loads((self.d / (name + ".report.json")).read_text(encoding="utf-8")))
        return r

    def flyby(self, room):
        self.tone()
        keys = [[0, 90, 0, 1], [2, 0, 0, 2], [4, -90, 0, 4]]
        return self.render({"duration": 4, "room": room, "sources": [{"file": "tone.wav", "keys": keys}]}, room)

    def test_flyby_lr_falls_steadily(self):
        for room in ("outdoor", "moderate"):
            lr = [b["lr_db"] for b in self.flyby(room)["mix"]]
            self.assertEqual(len(lr), 8)
            self.assertTrue(all(x > y for x, y in zip(lr, lr[1:])), (room, lr))
            self.assertGreater(lr[0], 10, (room, lr))
            self.assertLess(lr[-1], -4, (room, lr))

    def test_centred_tone_balanced_with_reverb(self):
        # Separate noise tails per channel pulled this tone 6.5 dB sideways in the harvest prototype.
        self.tone(sec=3.0)
        for room in ("dry", "moderate", "reverberant"):
            r = self.render({"duration": 3, "room": room, "sources": [{"file": "tone.wav", "keys": [[0, 0, 0, 1]]}]}, room)
            for b in r["mix"]:
                self.assertLess(abs(b["lr_db"]), 1.0, (room, r["mix"]))

    def test_four_metres_10_to_13_db_under_one(self):
        self.tone(sec=2.0)
        lv = {}
        for d in (1, 4):
            r = self.render({"duration": 2, "room": "outdoor", "sources": [{"file": "tone.wav", "keys": [[0, 0, 0, d]]}]}, "d%d" % d)
            lv[d] = r["mix"][2]["level_db"]
        self.assertTrue(10 <= lv[1] - lv[4] <= 13, lv)

    def test_tail_is_stereo_and_matched(self):
        import random
        rng = random.Random(3)
        f = self.d / "noise.wav"
        A.write_wav(f, A.Audio(self.SR, [[rng.uniform(-0.3, 0.3) for _ in range(self.SR)]]))
        self.render({"duration": 1, "room": "reverberant", "sources": [{"file": "noise.wav", "send_db": 0}]}, "tail")
        au = A.read_audio(self.d / "tail.wav")
        self.assertAlmostEqual(au.seconds, 2.0, delta=0.01)
        L, R = (c[int(1.05 * self.SR):int(1.5 * self.SR)] for c in au.channels)
        el, er = sum(v * v for v in L), sum(v * v for v in R)
        self.assertLess(abs(10 * math.log10(el / er)), 1.0)
        corr = sum(x * y for x, y in zip(L, R)) / math.sqrt(el * er)
        self.assertLess(corr, 0.95)  # still a stereo tail, not a mono copy

    def test_bad_plan_fails(self):
        self.tone(sec=0.5)
        p = self.d / "bad.json"
        p.write_text(json.dumps({"duration": 1, "room": "cave", "sources": [{"file": "tone.wav"}]}), encoding="utf-8")
        code, r = run("scene", "--plan", p, "--out", self.d / "x.wav")
        self.assertEqual(code, 1)
        self.assertIn("room", r["error"])

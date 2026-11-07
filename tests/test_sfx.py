import contextlib
import io
import json
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
        run("synth", "wind", "--out", f, "--param", "seconds=2", "--param", "gentle=yes")
        bad = self.d / "b.wav"
        run("degrade", f, bad, "--fault", "seam")
        self.assertGreater(A.seam_ratio(A.read_audio(bad)), A.LIMITS["seam"])


class Synth(Base):
    def test_every_recipe_clean_and_deterministic(self):
        for name in sorted(Y.RECIPES):
            kw = {"seconds": 1.0} if name in ("wind", "fire", "explosion") else {}
            with self.subTest(name=name):
                x = Y.render(name, seed=3, **kw)
                self.assertEqual(x, Y.render(name, seed=3, **kw))
                self.assertLess(max(abs(v) for v in x), 1.0)
                self.assertLess(abs(x[-1]), 0.01)

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


if __name__ == "__main__":
    unittest.main()

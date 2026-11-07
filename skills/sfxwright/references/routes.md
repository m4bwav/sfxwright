# Routes

Rankings are grade D (reading and inference) until a listening result is recorded here. No route has been ranked by ear yet.

| Job | Default | More | Note |
|---|---|---|---|
| One-shot, impact, foley hit | SA3 Small SFX, batch 4 | SA3 Medium | ElevenLabs v3 if keyed and paid |
| Footsteps | CC0 slices, or `synth footstep`, or one generated step; then `sequence` | | Never a generated walk |
| UI | `synth click, switch, beep`, or a jsfxr-family tool | SA3 for organic UI (paper, wood) | Reports of jittery ElevenLabs UI sounds, one thread |
| Retro | `synth retro`, jsfxr, ZzFX, Bfxr2 | | No AI |
| Ambience, loop | SA3 Medium, 15 to 60 s, `loop`, FLAC | ElevenLabs v3 `loop` | Bed plus sparse events |
| Creature | Recorded voice or animals, slowed and processed | ElevenLabs v3, SA3 Medium | Low confidence |
| Vehicle, machine | SA3 Medium | ElevenLabs v3 | Doppler by prompt or in post |
| Magic, sci-fi | SA3 Medium, layered | ElevenLabs v3 | |
| Comic stinger | SA3 Medium | musicwright when it has notes | |
| Silent video, commercial, local | HunyuanVideo-Foley XL, outside EU, UK, KR | LTX-2.x V2V, 10 to 15 s | Install needs a yes |
| Silent video, hosted | Mirelo SFX 2.0 | | Read its terms |
| Over USD 1M revenue | Hosted, or a Stability licence | Procedural and CC0 stay free | Never default to SA3 |
| Sample pack for sale | Procedural or own recordings | | Generator terms are unclear or against it |

## ComfyUI

`gen` reads `/object_info` and picks by checkpoint name. Hosts: `--host`, or `SFX_COMFY_URLS` (comma list), or local defaults. Settings from the official templates: distilled 8 steps, CFG 1, lcm, simple; `_base` 50 and 7; Open 1.0 50, 4.98, dpmpp_3m_sde_gpu, exponential. FLAC, never the templates' MP3. `EmptyLatentAudio` minimum is 1 s: trim shorter sounds. Queues behind a busy host. Comfy-Org mirrors are ungated; the licence applies regardless. If comfyui-gen is installed, follow its host rules.

The ElevenLabs partner node may offer only v2, removed 2027-03-01. v3 needs the direct API or a newer node. Paid, so ask.

## Prompts

- **SA3:** `gen` adds `TrackType: SFX,` and `Length: X seconds`. Then source, material, space (close-up, distant, echoing), time (attack, decay, approaching). Recording words help: dead room, ribbon mic. Avoid vocal words and timing cues. Lengths: impacts 1 to 3 s, actions 3 to 6, ambience 6 to 15.
- **Open 1.0:** concrete physical description.
- **ElevenLabs:** action, setting, performance; "X, then Y"; exact repeat counts are unreliable.
- **Mirelo:** one line naming the sound.

## Recipes (`synth`, no model)

`shaker, modal (material=wood|metal|glass|stone|plastic), footstep (surface=gravel|wood|stone|metal|grass|snow, state=walk|run|sneak, weight), click, switch, beep, wind (gentle=yes), fire, explosion (distance), whoosh, creak, retro (kind=coin|laser|jump|hit|explode|powerup|blip)`. Pass with `--param name=value`. Same seed, same file. They are simple models: test them against a generator by ear before calling one good enough.

## Musicwright boundary

Measured 2026-11-06 on four instrument prompts, not yet heard: ACE-Step 1.5 XL filled the length and ran hot (true peak up to +2.5 dBTP), with ends cut; SA3 Medium stopped early and decayed to silence, peaks -0.3 to -4.8 dB. Line for now: anything with notes, key or tempo goes to musicwright; single hits and non-musical stingers stay here. For a one-note instrument hit, prefer SA3 until a listen says otherwise.

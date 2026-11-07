# Routes

## Listening result, 2026-11-06

One listener, blind, 12 sounds, level-matched, first take of each route with no seed fishing and no layering. Picks: SA3 Medium 10 of 12, procedural 2 of 8 (laser, campfire), SA3 Small SFX 0 of 12. Medium won the plastic button and gravel step too, against what the reading predicted. One person and one seed: strong enough to set defaults, not to prove a route is good. Vehicle, creature, magic and comic rows had only the two models to choose from. ElevenLabs and video routes were not tested, and the other rows below stay grade D (reading and inference).

| Job | Default | More | Note |
|---|---|---|---|
| One-shot, impact, foley hit | SA3 Medium, batch 4 | SA3 Small SFX only when Medium will not fit the hardware | ElevenLabs v3 if keyed and paid |
| Footsteps | One SA3 Medium step per take, or CC0 slices; then `sequence` | | Never a generated walk |
| UI | SA3 Medium for a physical button; `synth click, switch, beep` when there is no model or a synthetic beep is wanted | jsfxr family | Reports of jittery ElevenLabs UI sounds, one thread |
| Retro | `synth retro`, jsfxr, ZzFX, Bfxr2 | | No AI |
| Ambience, loop | SA3 Medium (picked for gentle wind), or `synth fire` for fire; 15 to 60 s, `loop`, FLAC | ElevenLabs v3 `loop` | Bed plus sparse events |
| Creature | Recorded voice or animals, slowed and processed | ElevenLabs v3, SA3 Medium | Low confidence |
| Vehicle, machine | SA3 Medium | ElevenLabs v3 | Doppler by prompt or in post |
| Magic, sci-fi | SA3 Medium, layered | ElevenLabs v3 | |
| Comic stinger | SA3 Medium | musicwright when it has a melody | Won its one blind test |
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

`shaker, modal (material=wood|metal|glass|stone|plastic), footstep (surface=gravel|wood|stone|metal|grass|snow, state=walk|run|sneak, weight), click, switch, beep, wind (gentle=yes), fire, explosion (distance), whoosh, creak, retro (kind=coin|laser|jump|hit|explode|powerup|blip), bubbles (size, rate), rain (surface=hard|water|mixed), motor (rpm, poles, brush), cricket`. The last four (Farnell ch. 35-50, 0.1.12) have not been in a blind listen; use them as no-model drafts and ambience beds. Pass with `--param name=value`. Same seed, same file. In the listen, `retro` laser and `fire` beat the models; wood, metal, switch, gravel step, gentle wind and explosion lost. So use `retro` and `fire` by choice and the others as the no-model fallback.

## Musicwright boundary

Blind listen 2026-11-07, one listener, one seed each, four prompts. SA3 Medium won the single piano note, the timpani hit and the comic pizzicato and slide-whistle sting; ACE-Step 1.5 XL won the three-note brass stinger. Readings had shown ACE filling the length and running hot (true peak up to +2.5 dBTP) with cut ends, so check its output. Line: a melody, key or tempo goes to musicwright; a single instrument hit or a short comic sting stays here on SA3 Medium. The comic result rests on one clip.

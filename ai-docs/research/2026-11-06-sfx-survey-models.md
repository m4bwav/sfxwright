# sfxwright survey: models, ComfyUI routes, tutorials, existing tools

Written 2026-11-06. Every URL below was opened or returned by search on 2026-11-06 unless a line says otherwise, so "checked" dates are not repeated per claim. Page dates are given where they matter. This is a survey, not legal advice. Nothing was installed and no jobs were submitted; no audio was listened to.

## How strong the evidence is

Read this first, because it limits every ranking below.

- **No independent per-category listening test turned up.** I found no side-by-side of footsteps, creatures or vehicles across models, and no blind test run by anyone without a stake in the result.
- **No Reddit threads surfaced.** Several searches aimed at r/GameAudio, r/sounddesign, r/StableDiffusion and r/comfyui returned no Reddit snippets at all. So there is no Reddit evidence here, for or against.
- **Best evidence available:** Stability's technical report (vendor-authored, but with numbers and a small listening test), Anton Tenitsky's hands-on guide, a RuneXX Hugging Face thread with user reports, and Mirelo's crowd blind test (vendor-run).
- Grades used below: **A** = measured, even if vendor-run. **B** = a named person's hands-on report. **C** = vendor claim or stated purpose. **D** = listicle or my inference. Rankings at C or D are starting points for sfxwright's own bake-off, not findings.

## 1. Best now, per job

### Ranked by job

The local rank assumes a commercial-capable licence under the $1M cap. "Hosted" means a paid API.

| Job | 1st | 2nd | 3rd | Grade and why |
|---|---|---|---|---|
| One-shots | ElevenLabs SFX v3 (hosted) | Stable Audio 3 Medium (local) | SA3 Small SFX (local) | B/A. Tenitsky: Medium "sometimes on par", sometimes ElevenLabs better. Report: Medium OVL 3.65, REL 3.95; Small SFX 3.35, 3.25 |
| Impacts | ElevenLabs v3 | SA3 Medium, then layer | SA3 Small SFX | D for ordering. Cinevva says ElevenLabs is punchier (no test). Templates carry impact vocabulary |
| UI | jsfxr/ZzFX/ChipTone for synthetic UI | SA3 Medium or Small SFX | ElevenLabs | D. Procedural is exact, repeatable and cheap; a generator is for organic UI (paper, wood) |
| Footsteps/foley | CC0 recordings sliced and layered (Freesound, Kenney) | SA3 Small SFX or Medium for single steps | ElevenLabs | C/D. A guide in search results reports ElevenLabs footsteps lack realistic cadence; I could not pin that to one page. Generate one step, sequence in code |
| Ambiences/loops | ElevenLabs v3 with `loop` for up to 30 s | SA3 Medium for long beds, then crossfade | SA3 Small SFX | C/D. Small SFX CLAP falls as length rises (report). Cinevva calls ElevenLabs weak on long ambience, but the loop mode exists |
| Creatures | ElevenLabs v3 | SA3 Medium plus heavy processing | none | C/D. v3 claims better vocal sounds. SAO's card says no realistic vocals. Nothing tested roars |
| Vehicles/machines | SA3 Medium | ElevenLabs v3 | SA3 Small SFX | D. Only template examples (doppler, chain). Untested |
| Magic/sci-fi | SA3 Medium | ElevenLabs v3 | SAO 1.0 | D. Abstract sounds forgive artefacts; SA3's template examples cover warp drive, spell, teleport. Untested |
| Retro chip | jsfxr / ZzFX / Bfxr2 / ChipTone | none needed | | B by long use; no AI model should be first here |
| Comic stingers | ElevenLabs v3 | SA3 Medium, Instrument or One-shot category | ACE-Step 1.5, short clip, only when it is really music | D. Nobody tested this. v3 claims better musical phrases |
| Sound from silent video | Mirelo SFX 2.0 (hosted) | HunyuanVideo-Foley (local) or LTX-2.x V2V foley | ControlFoley/Woosh, non-commercial only | A from the vendor for Mirelo; B for LTX; A from authors for Hunyuan |

### Candidates, one by one

**Stable Audio 3 Small SFX, Small Music, Medium** (open weights, released about 2026-05-20).
- Spec: 44.1 kHz stereo. Small 459M transformer, up to 2 min; Medium 1.4B, up to 6:20 ([report](https://arxiv.org/html/2605.17991v1)). The HF card rounds Small to 0.6B and ChatForest says 433M; the report's table is the one to use.
- Measured on BBC Sound Effects at 5 s: Medium FAD 0.369, CLAP 0.369, OVL 3.65, REL 3.95. Small SFX FAD 0.395, CLAP 0.351, OVL 3.35, REL 3.25. Woosh Flow FAD 0.580, CLAP 0.277, OVL 3.45, REL 3.80. SAO FAD 0.501, CLAP 0.263. Note that Woosh out-scores Small SFX in the listening columns, and the authors say band-limiting hurts Woosh's FAD. MarkTechPost's "[outperforms every competitor](https://www.marktechpost.com/2026/05/26/stability-ai-releases-stable-audio-3-a-family-of-fast-latent-diffusion-models-for-audio-generation-and-editing/)" covers FAD and CLAP only.
- VRAM (report): Small about 1.9 GB at 30 s, 2.4 GB at 120 s. Medium about 5.5 to 6.5 GB. Speed: Small on M4 CPU-only 0.70 s for 5 s of audio at 8 steps, Medium under 2 s on an H200. These M4 figures use CoreML/TFLite, not ComfyUI, so expect ComfyUI to be slower.
- User-side timing: [audio-studio-mcp](https://github.com/kanaworksai-hue/audio-studio-mcp/blob/main/README.md) reports Medium on an M1 at about 13 s cold for two 3 s effects, 5 to 7 GB loaded; RTX 3060 peak 5.3 GB.
- Fit: Medium fits the RTX 5060 Ti 16 GB easily. Small SFX fits the 32 GB Mac. Medium should fit the Mac too by the M1 report, though it was not verified on this Mac.
- Training data: 806,284 AudioSparx licensed plus 472,618 Freesound CC0/CC-BY/CC-Sampling+. Small SFX's final stages use a higher-quality Freesound subset ([report](https://arxiv.org/html/2605.17991v1), [card](https://huggingface.co/stabilityai/stable-audio-3-small-sfx)).
- Edits: inpainting and continuation are supported; Small edits less smoothly than Medium (report). LoRA training exists ([HF thread](https://huggingface.co/stabilityai/stable-audio-3-small-music/discussions/2)).
- Gating: `stabilityai/*` cards are auto-gated; `Comfy-Org/stable-audio-3` is not gated (HF API `gated` field). The licence applies either way. Watermarks: neither the card nor the report text I read mentions one. Not proven absent.
- Hands-on: [Tenitsky, 2026-10-13](https://tenitsky.com/guides/stable-audio-3-sound-effects/). A few seconds per sound; "not the best available"; sometimes on par with ElevenLabs; a 6 s request can return 4 s of sound and then silence; negative prompts help only sometimes. 8 steps CFG 1 gave usable sounds.

**The Stability licence conflict, resolved from the text.** [Community License](https://stability.ai/community-license-agreement), last updated 2024-07-05:
- Section III: business use requires registering with Stability ("You must register"). Annual revenue of more than USD 1,000,000, you plus Affiliates combined, ends the licence "as of such date" unless you get another one.
- Section IV(c)(iii): "You own any outputs ... to the extent permitted by applicable law."
- Section IV(f): on termination, delete and stop using the Materials and Derivative Works. It does not mention outputs. So output made earlier looks like it survives, but the text never says so. Stability's [knowledge base](https://kb.stability.ai/knowledge-base/stable-audio-commerical-and-usage-licensing) agrees on the threshold and registration.

Against that text:
- [ComfyUI blog](https://blog.comfy.org/p/stable-audio-3-day-0-support), 2026-05-21: "Licensed for commercial use", "fully licensed music data". True only under the cap and with registration. The phrase also skips Small SFX's Creative Commons Freesound data.
- [The Rundown](https://www.therundown.ai/tools/stable-audio-3-0), reviewed 2026-08-31: registration and under $1M aggregate affiliate revenue, ownership without guarantee of protection or non-infringement. **Correct and the most careful.**
- [Dubspot](https://blog.dubspot.com/stable-audio-3-review), 2026-05-26: own and "commercialize freely", Enterprise above $1M. Directionally right; leaves out registration and affiliates. Its "one big caveat" is no vocals, not the licence.
- [ComfyUI Wiki](https://comfyui-wiki.com/en/models/stable-audio/stable-audio-3) lists Open-RAIL-M and an April 2025 date. That is wrong for this family; do not cite it.
- Extra catch: the SA3 card says T5Gemma is redistributed under the Gemma Terms including Section 3.2, so that text must pass on with any bundle. sfxwright should not bundle weights.
- Hosted Stable Audio is a different contract: [Cinevva](https://app.cinevva.com/guides/ai-sound-effect-generators) says free is personal only; [Undetectr](https://undetectr.com/blog/stable-audio-review) says Stability does not state the free plan's position. Unsettled, and off the main route anyway.

**Stable Audio Open 1.0.** Same licence, gated. Up to 47 s at 44.1 kHz. 486,492 Freesound and FMA recordings, CC0/CC-BY/CC-Sampling+. The card says it is better at effects and field recordings than music, and cannot do realistic vocals ([card](https://huggingface.co/stabilityai/stable-audio-open-1.0)). [sfx-gen-mcp](https://github.com/JimCline/sfx-gen-mcp) reports 15 to 30 s for 50 steps on M-series, about 12 GB RAM. Beaten by SA3 on FAD and CLAP in the report. Keep it only as a third opinion; the training set is the more transparent of the two.

**ElevenLabs Sound Effects.** Hosted, grade C for quality claims.
- SFX v3 launched [2026-10-29](https://elevenlabs.io/blog/sound-effects-v3). "Cleaner, more natural" with no benchmark figures given. v2 is deprecated and goes away 2027-03-01 ([docs](https://elevenlabs.io/docs/overview/capabilities/sound-effects)).
- Up to 30 s, loop mode, prompt influence, 40 credits per second when duration is set. MP3, or 48 kHz WAV for non-looping effects.
- Licence, conflict still open: [ElevenLabs' page](https://elevenlabs.io/sound-effects/commercial) says all effects are royalty free and commercial, with free plan attribution. Its [use policy](https://elevenlabs.io/use-policy) section 12 prohibits "commercial purposes on a free plan". Treat free as not commercial; the paid floor is Starter at $6 a month per [secondary sources](https://bigvu.tv/blog/elevenlabs-pricing-2026-plan-worth/). Output may not be used to develop competing products.
- Standalone resale: [one guide](https://www.stork.ai/blog/elevenlabs-sound-effects-2026) or its neighbours in the search claim a prohibition on selling effects as libraries. The two official pages I read do not contain that wording, and the Terms of Service were not read. Assume no sample-pack sales until checked.
- Training data and watermarks: not found on the pages read.

**Adobe Firefly Generate Sound Effects.** GA 2026-08-20, about 10 credits per generation ([secondary](https://superpowerdaily.com/posts/adobe-puts-ai-music-voice-and-sound-effects-inside-firefly)). Its unusual feature is voice-performed timing ([PetaPixel](https://petapixel.com/2025/06/27/you-can-create-video-sound-effects-using-your-voice-in-adobe-firefly/)). Commercial use in projects is claimed by Adobe; selling as an asset pack is not addressed, per a [community thread](https://community.adobe.com/questions-404/can-i-sell-adobe-firefly-generated-sound-effects-as-an-asset-pack-1643734) (2026-09-24 to 10-24) whose respondent says it is not official. Adobe training-data terms were not read in primary form. No API route for an agent was confirmed. Mention it; do not route to it.

**Non-commercial, so research or personal use only:**
- AudioLDM 2: `cvssp/audioldm2` tagged CC-BY-NC-SA-4.0 (HF API). The 2024 repo looks dormant.
- [TangoFlux](https://github.com/declare-lab/TangoFlux): research-only, WavCaps academic data, Stability notice required; up to 30 s, 44.1 kHz, 50 steps, CFG 3.5 to 4.5.
- AudioGen: `facebook/audiogen-medium`, CC-BY-NC-4.0, Meta but not click-gated on HF (`gated: false`). 18 s per second of audio on Apple Silicon ([audiogen-mcp](https://github.com/peerjakobsen/audiogen-mcp)). Flag: Meta model, non-commercial, slow. Do not route to it.
- [Woosh](https://github.com/SonyResearch/Woosh) (Sony): code MIT and Apache, weights CC-BY-NC 4.0. Listening scores are good, so it is useful as a reference in a bake-off. The [licensed-library model is unreleased](https://arxiv.org/abs/2604.01929).
- [MMAudio](https://github.com/hkchengrex/MMAudio): code MIT, weights CC-BY-NC; about 6 GB, tuned for 8 s.
- [ControlFoley](https://github.com/xiaomi-research/controlfoley) (Xiaomi, ACM MM 2026): code Apache, weights CC-BY-NC. Takes video, text and reference audio. Official [ComfyUI nodes](https://github.com/YJX-Research/comfyui-controlfoley-official). Most flexible control, wrong licence for shipping.

**Sound from video:**
- [Mirelo SFX 2.0](https://mirelo.ai/blog/mirelo-sfx-2-0), 2026-10-14. Crowd blind test, 25 pre-screened raters per comparison, 30 videos each. It claims 81% preference over Woosh, per its [marketing](https://x.com/MireloAI/status/2110362929157509428) (figure not re-read in the post). Vendor-run, against Woosh, Kling Foley, Sonilo and native audio of Veo 3.1 Fast, H3 Max and others. Keeps dialogue, removes unprompted music. Licence is in its terms, not read. ComfyUI has official templates. Hosted only.
- [HunyuanVideo-Foley](https://github.com/Tencent-Hunyuan/HunyuanVideo-Foley). 48 kHz. XXL 20 GB or 12 GB with offload; XL 16 GB or 8 GB with offload. So XL fits the PC. Author benchmark MOS-Q 4.14 vs FoleyCrafter 3.36 ([summary](https://www.xugj520.cn/en/archives/hunyuanvideo-foley-ai-sound-generation.html)). [Licence](https://raw.githubusercontent.com/Tencent-Hunyuan/HunyuanVideo-Foley/main/LICENSE): not valid in EU, UK or South Korea, output may not improve other AI models, no rights claimed in output. Two custom nodes: [if-ai](https://github.com/if-ai/ComfyUI_HunyuanVideoFoley) (last push 2025-09) and [phazei](https://github.com/phazei/ComfyUI-HunyuanVideo-Foley) (2026-05). No current Mac evidence.
- [FoleyCrafter](https://github.com/open-mmlab/FoleyCrafter). Apache, but check Auffusion's terms as its README says. Outclassed by author numbers. Skip.
- LTX-2.x audio. [RuneXX V2V foley thread](https://huggingface.co/RuneXX/LTX-2.3-Workflows/discussions/41) (Mar to Apr 2026): 30 s of audio at 320x128 in about 3 min on an RTX 3080; designed for 10 to 15 s, "falls apart" past about 45 s; use Euler; the picture may change, so keep the original; one popping report was traced to a custom node. Blog-level complaints of [robotic speech](https://ltx-23.org/blog/social-viral-platforms). LTX licence not read for this survey. The PC already has LTX nodes.
- MiniMax H3 native audio. Picture and 32 kHz stereo sound together, 4 to 15 s ([card](https://huggingface.co/MiniMaxAI/MiniMax-H3)). Community licence, terms not read; moderation applies. It generates new video, so it is not a route for an existing silent clip unless a video-input mode proves otherwise. Reviews are affiliate-grade. Audio is only as usable as it is separable.

**Procedural:**
- [jsfxr](https://github.com/chr15m/jsfxr) Unlicense, [ZzFX](https://github.com/KilledByAPixel/ZzFX) MIT, [bfxr2](https://github.com/increpare/bfxr2) MIT (GitHub API). [ChipTone](https://sfbgames.itch.io/chiptone): itch page lists CC0 and output free for any purpose.
- ZzFX and jsfxr are scriptable and need no GPU, so an agent can run them directly. Deterministic, small, no training-data question.
- The [AssetHoard](https://assethoard.com/blog/free-sound-effects-2026) view that generated output is yours is a blog opinion.

**ACE-Step 1.5.** MIT per [Soundbox's table](https://github.com/HamSanders/soundbox). A music model. Use only for musical stingers. Hand music to musicwright.

**Others found:** [SFX Engine](https://sfxengine.com/mcp), [Doseedo](https://doseedo.com/guides/sound-effects-foley-mcp-server), [Krotos Studio](https://app.cinevva.com/guides/ai-sound-effect-generators) (performable, not generative), ByteDance Seed Audio (a ComfyUI partner node and [templates](https://github.com/Comfy-Org/workflow_templates/tree/main/templates)). None evaluated.

## 2. ComfyUI routes

### Official graphs

From [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates), read as JSON. Docs: [Stable Audio 3](https://docs.comfy.org/tutorials/audio/stable-audio/stable-audio-3). Needs ComfyUI v0.22.0+; latest release is v0.44.0.

| Template | Sampler | Steps | CFG | Scheduler | Seed behaviour |
|---|---|---|---|---|---|
| `audio_stable_audio_3_medium` | lcm | 8 | 1 | simple | randomize |
| `audio_stable_audio_3_medium_base` | lcm | 50 | 7 | simple | randomize |
| `audio_stable_audio_example` (SAO 1.0) | dpmpp_3m_sde_gpu | 50 | 4.98 | exponential | randomize |

Denoise is 1 in all three. There is **no official Small SFX template**. The Medium graphs should accept Small SFX by changing `ckpt_name`, with `_small_sfx` at 8/1 and `_small_sfx_base` at 50/7. That matches the report's post-trained vs base split, but it is my inference and is not yet run.

Stability's own example uses PingPong (8 steps, CFG 1) and the report uses Euler for base. Neither host lists a pingpong sampler in KSampler, so lcm is what ComfyUI ships. Comparing lcm with Euler at 50 steps is a bake-off item.

**Graph**, inside the subgraph:
```
CheckpointLoaderSimple -> MODEL -> KSampler.model
                       -> VAE   -> VAEDecodeAudio.vae
CLIPLoader(t5gemma_b_b_ul2, type=stable_audio) -> CLIPTextEncode x2
CLIPTextEncode(positive) -> KSampler.positive
CLIPTextEncode("")       -> KSampler.negative
EmptyLatentAudio(seconds, batch=1) -> KSampler.latent_image
KSampler -> VAEDecodeAudio -> AUDIO -> SaveAudioAdvanced("audio/stable_audio_3", mp3, V0)
```
Optional reprompt: `CLIPLoader(qwen3.5_2b_bf16, stable_diffusion)` -> `TextGenerate` with the category prompt -> `ComfySwitchNode`. `TextGenerate` values: 256 tokens, sampling on, temperature 0.7, top-k 64, top-p 0.95, min-p 0.05, repeat 1.05.

**Three things this shows:**
- **`ConditioningStableAudio` is in core but neither SA3 template nor the SAO example uses it.** Length comes from `EmptyLatentAudio.seconds`, and the SFX reprompt adds "Length: X seconds." to the text. Its inputs are `positive, negative, seconds_start (0), seconds_total (47)`. Whether it changes SA3 output is unsettled.
- `EmptyLatentAudio.seconds` has a **minimum of 1.0**. Sub-second sounds need `TrimAudioDuration` or trimming outside ComfyUI.
- Templates save MP3 by default, which [breaks loops](https://github.com/kanaworksai-hue/audio-studio-mcp/blob/main/README.md) by padding. The SAO template uses FLAC; do that. `VAEDecodeAudioTiled` is [reported better](https://jurn.link/dazposer/index.php/2026/05/23/workflow-for-stable-audio-3-small-music/) but only on hearsay.

**Prewired API prompt** (derived from the template; not yet run):
```json
{"1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":"stable_audio_3_small_sfx.safetensors"}},
 "2":{"class_type":"CLIPLoader","inputs":{"clip_name":"t5gemma_b_b_ul2.safetensors","type":"stable_audio","device":"default"}},
 "3":{"class_type":"CLIPTextEncode","inputs":{"clip":["2",0],"text":"TrackType: SFX, wooden door creaking open slowly, echoing interior. Length: 3 seconds"}},
 "4":{"class_type":"CLIPTextEncode","inputs":{"clip":["2",0],"text":""}},
 "5":{"class_type":"EmptyLatentAudio","inputs":{"seconds":3,"batch_size":4}},
 "6":{"class_type":"KSampler","inputs":{"model":["1",0],"positive":["3",0],"negative":["4",0],"latent_image":["5",0],"seed":1,"steps":8,"cfg":1,"sampler_name":"lcm","scheduler":"simple","denoise":1}},
 "7":{"class_type":"VAEDecodeAudio","inputs":{"samples":["6",0],"vae":["1",2]}},
 "8":{"class_type":"SaveAudioAdvanced","inputs":{"audio":["7",0],"filename_prefix":"audio/sfx","format":"flac"}}}
```
The `SaveAudioAdvanced` input names need checking against `/object_info`. `format` is inferred from its widget values, and it may need a further quality input.

**Partner nodes.** `ElevenLabsTextToSoundEffects`: `text`, model option `eleven_sfx_v2` only, duration 0.5 to 30 (default 5), `loop`, `prompt_influence` default 0.3, output `mp3_44100_192` or `opus_48000_192`. Uses Comfy.org credits. **Both local hosts offer only v2, so v3 needs the direct API or a ComfyUI update**, and whether the newest node has v3 is unchecked. Mirelo: `MireloTextToSFX` and `MireloVideoToSFX` (model `sfx-2.0`, returns audio and speech outputs) in the templates. The Mirelo guide's formula names the sound, not a story: source plus material.

**Custom packs:** ControlFoley official, two Hunyuan Foley packs, RuneXX LTX workflows, the [Prompt Cycler batch](https://tenitsky.com/guides/stable-audio-3-sound-effects/) (position lost on restart). Workflows people really use are thin: Tenitsky's bulk graph and RuneXX's V2V are the only two with named-user reports.

### Detecting what a user has

`GET /object_info` once, cached:
- Node presence: `"ElevenLabsTextToSoundEffects" in info`, likewise `MireloVideoToSFX`, `TextGenerate`, `ConditioningStableAudio`.
- Checkpoints: `info.CheckpointLoaderSimple.input.required.ckpt_name`. **Combos come in two shapes**: `[[list], {...}]` and `["COMBO", {"options": [...]}]`. Handle both.
- Text encoders: `CLIPLoader.input.required.clip_name` for `t5gemma_b_b_ul2`, `qwen3.5_2b_bf16`, `t5_base` or `t5-base`. Filename spellings differ between hosts and templates, so match loosely.
- Route by match: `stable_audio_3_small_sfx`, `_medium`, `_base` suffix decides 50/7 vs 8/1.
- Dynamic combos: the ElevenLabs model is `COMFY_DYNAMICCOMBO_V3` with `options[].key`.

Which local hosts had which models is kept outside this public repository.

## 3. Tutorials, vocabulary, repair

**Tutorials worth reading:**
- [Tenitsky bulk SFX](https://tenitsky.com/guides/stable-audio-3-sound-effects/): the one practical hands-on.
- [Stability prompting guide](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md) and its [web version](https://stability.ai/guides/stable-audio-3-prompt-guide).
- The SFX and One-shot system prompts inside the [templates](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_stable_audio_3_medium.json): about 40 worked examples each, the best free vocabulary list found. Worth adapting into a reference file, with attribution checked against the repo's licence.
- [ElevenLabs prompt docs](https://elevenlabs.io/docs/overview/capabilities/sound-effects).
- [Sound layering](https://pixflow.net/blog/sound-effects-layering/) and [Unison](https://unison.audio/ai-sound-design/), which are vendor blogs but concrete. No recommended YouTube tutorial on these models surfaced.

**Vocabulary by model:**
- **SA3:** start `TrackType: SFX,` (the [guide](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md) says it gives more sensible effects; audio-studio-mcp says effects otherwise come out musical). Then source, action, production: "14-inch hats tightly closed, zero ring, very fast decay", "dead room", "ribbon mic", "dark reverb". The dataset uses recording-technique words. Template formula: source, material, space (close-up, distant, echoing), time (attack, decay, approaching, passing), then "Length: X seconds". Lengths: impacts 1 to 3 s, actions 3 to 6, ambience 6 to 15. Avoid vocal words and timing cues such as "climax at 15 s" (audio-studio-mcp).
- **SAO:** concrete physical descriptions, negative "music, voices" ([sfx-gen-mcp](https://github.com/JimCline/sfx-gen-mcp)).
- **ElevenLabs:** describe action, setting, performance. Sequences as "X, then Y". Terms: impact, whoosh, ambience, one-shot, loop, stem, braam, glitch, drone. Exact repeat counts are not reliable. Word choice shifts results.
- **LTX:** describe sounds explicitly; [guides say](https://codersera.com/blog/run-ltx-2-on-comfyui-locally-and-free-generate-videos-with-audio/) audio follows prompt detail.
- **Mirelo:** one short line naming the sound; text only steers video.

**When output is thin or muddy:**
- **Seed fish.** Generate 4 to 10 and choose. One guide says [SAO needs 5 to 10 candidates per usable result](https://www.qwe.edu.pl/tutorial/best-ai-tools-sound-effects-generation/) (snippet attribution, grade D). `batch_size` does this cheaply.
- **Layer.** Split into transient, body, low thump, tail; align transients; EQ so each owns a band ([Pixflow](https://pixflow.net/blog/sound-effects-layering/)). Generate parts separately rather than one complex prompt ([StraySpark](https://www.strayspark.studio/blog/ai-sound-design-indie-games-pipeline)). Weak attack: add a short noise burst or real transient, or a transient shaper.
- **Pitch and stretch.** Pitching down adds size and grit, but extreme shifts expose artefacts. Save long tails. Reverse and stretch for sweeps ([search set](https://soundarchitect.io/learn/recreate-any-sound-with-ai)). Numbers in these posts are untested.
- **Convolution.** Places a dry sound in a space. Stretch impulses by resampling to avoid phasing ([Image-Line](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Convolver.htm)).
- **Prompt brightness.** Add "bright, crisp" for dull output. Metallic resonance may be a [model artefact that cannot be fixed by prompt](https://www.qwe.edu.pl/tutorial/ai-generated-sound-effects-for-games/) (single guide).
- **Clean-up.** Trim trailing silence, because length is a maximum, not a promise (Tenitsky). Fades that end at zero, peak normalise to about -1 dB, OGG or WAV for loops. Variation sets matter in games, more than one perfect take ([Stepico](https://stepico.com/blog/ai-sound-design/), vendor).
- **Hybrid over pure AI.** A [GameDev.net thread](https://gamedev.net/forums/topic/720371-ai-or-not-ai/) poster refuses to sell pure AI effects as weak; others favour hybrids. One voice, but it fits the rest. Very short percussive sounds [can carry start and end artefacts](https://www.strayspark.studio/blog/ai-sound-design-indie-games-pipeline).

These repairs are all ffmpeg or Python work, which suits a small script. `mw.py` in musicwright (`measure`, `loop`, `seam`, `master`) probably overlaps; check before writing a new one.

## 4. Existing skills and MCP servers

Stars and last push from the GitHub API today.

| Tool | What it is | Borrow | Weakness |
|---|---|---|---|
| [audio-studio-mcp](https://github.com/kanaworksai-hue/audio-studio-mcp) (601, 10-24, MIT) | SA3 via MLX or torch; generate, edit, process | Candidate batches, non-destructive process, JSON sidecars, duration table, `peak_ceiling_db`, loudness targets | Own runtime with duplicate model downloads; not ComfyUI. Brand excluded from MIT. [tsuretaka](https://github.com/tsuretaka/audio-studio-mcp) is a 0-star copy |
| [soundbox](https://github.com/HamSanders/soundbox) (144, today) | Local app with MCP, skills `soundbox-sfx`, `-sound-pass`, `-voice-story` | Licence shown before download, unknown licence treated as NC, agent never accepts NC for the user, keep every take with prompt, model and seed | Large app; Mac unconfirmed; licence field shows NOASSERTION though README says MIT; tool count inconsistent |
| [sfx-gen-mcp](https://github.com/JimCline/sfx-gen-mcp) / [game-audio-kit](https://github.com/JimCline/game-audio-kit) (1 star) | SAO, macOS-centred | Audition-workflow skill idea, idle unload | SAO only; launchctl |
| [audiogen-mcp](https://github.com/peerjakobsen/audiogen-mcp) (1) | AudioGen with job polling | Job pattern | NC and slow |
| [MJSFX skill](https://github.com/matthewjschultz/mjs-claude-skill-mjsfx) (0, MIT) | Skill for the MJSFX app | "Character recipes": which parameters define a coin, laser, explosion; roll wide then curate | Needs the app; price unstated |
| [Game-Sound-Effect-for-Claude](https://github.com/GhazaGG/Game-Sound-Effect-for-Claude) (2, MIT) | Stdlib synth, CC0 foley, doctor | **Best ideas here**: metrics plus spectrogram so an agent can "hear", preview in game rhythm, style file per game, JSON recipes, typo checks | Very young; no generative route |
| [ElevenLabs skill](https://github.com/elevenlabs/skills/tree/main/sound-effects) (536, MIT) | Official API skill | Sets v3 explicitly | One vendor, no craft |
| [procedural-sfx](https://github.com/bianbianzhu/procedural-sfx), [sxhzju/sound](https://github.com/sxhzju/sound) (34) | Code synthesis, frame-accurate mix under video; sourcing | Video-mix idea | Procedural or sourcing only |
| [sfxmint-mcp](https://github.com/sfxmint/sfxmint-mcp) (7, CC0), [sfx-mcp](https://github.com/sandraschi/sfx-mcp) | Search CC0 libraries | Try existing recordings first | No generation |

Not checked in depth: [sfxengine](https://sfxengine.com/mcp), [Doseedo](https://doseedo.com/guides/sound-effects-foley-mcp-server), noizai sound-fx, the Sound FX market listings.

**The gap.** Nothing found does all of this: route by job and licence across local and hosted; use the ComfyUI the user already has, by reading `/object_info`, instead of a second runtime; judge output with measurements; keep licence provenance per file; and pair generation with procedural and CC0 sources as equals. The closest two are audio-studio-mcp (edit and process) and GhazaGG (judging). The sound-from-video step is absent from all of the generative ones.

## 5. Watch list

**GitHub atom feeds** (`https://github.com/OWNER/REPO/releases.atom`, or `/commits.atom`):
- [Stability-AI/stable-audio-3](https://github.com/Stability-AI/stable-audio-3/releases.atom), [stable-audio-tools](https://github.com/Stability-AI/stable-audio-tools/releases.atom)
- [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates/commits/main.atom), [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI/releases.atom)
- [SonyResearch/Woosh](https://github.com/SonyResearch/Woosh/commits.atom), [xiaomi-research/controlfoley](https://github.com/xiaomi-research/controlfoley/commits.atom), [YJX-Research/comfyui-controlfoley-official](https://github.com/YJX-Research/comfyui-controlfoley-official/commits.atom), [phazei/ComfyUI-HunyuanVideo-Foley](https://github.com/phazei/ComfyUI-HunyuanVideo-Foley/commits.atom)
- [elevenlabs/skills](https://github.com/elevenlabs/skills/commits.atom), [kanaworksai-hue/audio-studio-mcp](https://github.com/kanaworksai-hue/audio-studio-mcp/releases.atom), [HamSanders/soundbox](https://github.com/HamSanders/soundbox/releases.atom), [GhazaGG/Game-Sound-Effect-for-Claude](https://github.com/GhazaGG/Game-Sound-Effect-for-Claude/commits.atom)
- [KilledByAPixel/ZzFX](https://github.com/KilledByAPixel/ZzFX/commits.atom), [increpare/bfxr2](https://github.com/increpare/bfxr2/commits.atom)
- [Xiaohao-Liu/Awesome-Vision2Audio](https://github.com/Xiaohao-Liu/Awesome-Vision2Audio/commits.atom), GitHub topics [sound-effects](https://github.com/topics/sound-effects) and [game-audio](https://github.com/topics/game-audio?o=desc) (no feed)

**Hugging Face:** [SA3 Small SFX](https://huggingface.co/stabilityai/stable-audio-3-small-sfx/discussions), [SA3 Medium](https://huggingface.co/stabilityai/stable-audio-3-medium/discussions), [Comfy-Org/stable-audio-3](https://huggingface.co/Comfy-Org/stable-audio-3), [RuneXX LTX workflows](https://huggingface.co/RuneXX/LTX-2.3-Workflows/discussions), [HunyuanVideo-Foley](https://huggingface.co/tencent/HunyuanVideo-Foley), [papers search](https://huggingface.co/papers?q=VGGSound-TVC). Diffusers support: [issue #13793](https://github.com/huggingface/diffusers/issues/13793).

**Vendor pages:** [ElevenLabs blog](https://elevenlabs.io/blog), [Mirelo blog](https://mirelo.ai/blog), [Comfy blog](https://blog.comfy.org), [Stability licence](https://stability.ai/community-license-agreement) (watch the date line), [Tenitsky guides](https://tenitsky.com/guides/stable-audio-3-sound-effects/).

**Forums:** [A Sound Effect](https://www.asoundeffect.com/gdc26/) (annual game audio GDC guide; 2026 lists an AI Audio Roundtable), [Game Audio Learning communities](https://www.gameaudiolearning.com/communities) (Discord list), Harmonai Discord (named by Stability's guide), Reddit r/GameAudio, r/sounddesign, r/comfyui via RSS per Mark's standing rules, [GameDev.net](https://gamedev.net/forums/topic/720371-ai-or-not-ai/).

**YouTube:** no AI-SFX channel was worth listing. General game sound: [Game Audio Learning](https://www.youtube.com/c/GameAudioAnalysis), and Akash Thakkar and Marshall McGee from [A Sound Effect's list](https://www.asoundeffect.com/youtube-sound-design-channels/). They are for craft, not models.

## Recommended routes

| Job | Default | When it needs more | Fallback or note |
|---|---|---|---|
| Single one-shot, impact, foley hit | SA3 Small SFX (8/1), batch 4 | SA3 Medium | ElevenLabs v3 if keyed and paid |
| Footsteps | CC0 slice and layer, or generate one step, then sequence with variations | | Do not ask a model for a walk cycle |
| UI | jsfxr or ZzFX; SA3 for organic UI | | |
| Retro | jsfxr, ZzFX, Bfxr2 | | No AI |
| Ambience/loop | SA3 Medium, 15 to 60 s, crossfade seam, FLAC | ElevenLabs v3 `loop` | Check seam by measurement |
| Creature | ElevenLabs v3 | SA3 Medium, pitched and layered with animal sources | Flag low confidence |
| Vehicle/machine | SA3 Medium | ElevenLabs v3 | Doppler by prompt or in post |
| Magic/sci-fi | SA3 Medium, layered | ElevenLabs v3 | |
| Comic stinger | ElevenLabs v3 or SA3 Medium One-shot style prompt | musicwright if it is music | |
| Silent video, commercial, local | HunyuanVideo-Foley XL, outside EU/UK/KR | LTX-2.x V2V, 10 to 15 s, low res audio-only | Licence warning shown |
| Silent video, hosted | Mirelo SFX 2.0 | | Read its terms first |
| Silent video, personal only | ControlFoley, Woosh-VFlow | | Non-commercial |
| Over $1M revenue | Hosted route or a Stability Enterprise licence | Procedural and CC0 stay free | Never default to SA3 |
| Sample pack for sale | Procedural or own recordings | | Every generator's terms are unclear or against it |

## Unsettled

1. **Real quality per job.** Needs a bake-off on the two local hosts with one fixed prompt list, including Medium vs Small SFX, base vs distilled, lcm vs Euler. All D-grade rows above depend on it.
2. Does `ConditioningStableAudio` change SA3 output, and does a "Length:" text cue help? Why do official graphs skip it?
3. Do Small SFX checkpoints run correctly in the Medium graph on the Mac, and how fast? Does the API prompt above validate?
4. Do outputs made before crossing $1M stay usable? The text is silent. Does a hobbyist game with sales count as "business" needing registration? (Assume yes.)
5. ElevenLabs: free plan conflict, standalone resale wording in the Terms of Service, training data, watermarks. Is v3 in the newest ComfyUI node?
6. Watermarks on SA3 and other open models: nothing found either way.
7. Terms not read: LTX-2.x licence, MiniMax H3 licence text, Mirelo terms, Adobe primary terms, Auffusion.
8. Whether H3 can take an existing silent video and return its audio alone.
9. Reddit and YouTube practitioner evidence: nothing surfaced by search, so absence means little. A later RSS pass may find it.
10. Overlap with musicwright `mw.py` and cinewright sound work: sfxwright should call or share, not duplicate. Not checked here.
11. Whether Soundbox is MIT in its LICENSE file; the GitHub API reports NOASSERTION.

## Reddit pass, 2026-11-06

All evidence in this section is practitioner anecdote. Nothing was measured, and few people spoke. Threads were read over public RSS at one request per 45 s. Comment counts are what the feed returned, including bots. Notes are in the everscout `ai-sfx` beat, under `notes/2026-10/`.

**Result:** no ranking changes. Two routes gain a step (creature, ambience). One bake-off item is added (ElevenLabs v2 and v3 on UI sounds). These threads do not settle real quality per job (Unsettled item 1).

### r/ElevenLabs: SFX v3 announcement

- URL: https://www.reddit.com/r/ElevenLabs/comments/1xirdaq/introducing_sfx_v3_a_new_generation_of_sound/
- Comments read: 3.
- It is a staff post with no figures.
- One commenter plans to try it for game sounds, but had not yet.
- One commenter asks whether v3 can take a video with dialogue and time effects to it. Nobody answers.
- One commenter only hopes for effects in Eleven Reader.
- **Ranking or routing:** no change. It holds no quality evidence. Silent video stays off the ElevenLabs route, since nothing here shows v3 takes video.

### r/ElevenLabs: "Sound Effects section now worse?"

- URL: https://www.reddit.com/r/ElevenLabs/comments/1xg27az/sound_effects_section_now_worse/
- Comments read: 5.
- The poster pays $25 a month and has used it since late 2025 for interface sounds. They report that v3 gives terrible UI sounds: jittery high end, more noise, very quiet results, more re-rolls.
- The same poster says v2 has also got worse, and sometimes sounds bit-reduced. They guess at less compute, with no evidence.
- One commenter evaluating SFX models for games calls it unreliable: ask for three footsteps and you may get six.
- The poster replies that note counts do not matter for UI. Only sound quality does.
- Two commenters agree that quality has dropped. One guesses speed was put ahead of quality.
- One commenter rejects all AI sound. That is opinion, so I did not count it.
- Date oddity: this post is from 2026-10-26 and already names v3, three days before the 2026-10-29 launch date above. Either the rollout came first or the label is loose. Unresolved.
- **Ranking or routing:** no ranking change on one thread. It supports what is already here: UI stays procedural first with ElevenLabs third, and footsteps stay "generate one step, sequence in code". ElevenLabs stays first for one-shots and impacts, but the D-grade caveat matters more. **Add to the bake-off:** v2 and v3 UI prompts, recording re-roll rate, loudness and high-frequency noise. Both local hosts only offer v2 through the node, so its reported decline matters too.

### r/sounddesign: horror and monster synthesis tips

- URL: https://www.reddit.com/r/sounddesign/comments/1xiss36/what_are_your_most_unhinged_tips_for_synthesizing/
- Comments read: 26 (one bot, a few jokes).
- No commenter mentions AI generators. The asker did not ask about them either, so this is not a verdict on them.
- Several commenters start from their own voice: record growls, then pitch shift or ring mod. One suggests voice-acting along to clips of the monster. One suggests hiring a creature voice actor.
- Several use animals. Named sources: birds, crocodiles, alligators, lions, elephants. One commenter says playback speed is the main tool, then distortion and modulation.
- One commenter records at 192 kHz for this reason. Another explains why: pitch a 20 kHz limit down 4x and nothing remains above 5 kHz, so it goes muddy. Others debate which mics and rates are enough.
- Synthesis ideas: FM with noise, AM of two pitched-down animals, Serum 2 spectral warp modes, VCV Rack oscillators patched back into their own sync and FM.
- Physical ideas: air spray into foam for squeals, a pitched rusty gate, a bucket of objects through 100% reverb, food as gore foley.
- **Ranking or routing:** change to the creature route, not its ranking. Add a recorded route ahead of generators when a mic or CC0 animal recordings are available: voice or animal, slow down, then AM, ring mod and distortion. Generators stay as the fallback, still low confidence. My inference, not the thread's: generated audio at 44.1 or 48 kHz may go muddy under heavy slowdown, and the ElevenLabs node returns MP3 or Opus. **Add to the bake-off:** 2x and 4x slowdown of generated creature sounds.

### r/sounddesign: 122-minute animated feature, foley and backgrounds

- URL: https://www.reddit.com/r/sounddesign/comments/1xe4nfj/122minute_animated_feature_how_to_tackle_foley_bg/
- Comments read: 18 (one bot, several from the asker saying thanks).
- No commenter suggests generating foley or backgrounds. One says AI can help identify scenes by location, and that is the only AI use mentioned, apart from a likely promotional mention of Krotos Studio.
- One feature editor says that all backgrounds can be cut in a week and a full foley edit in four days at most. That is one person's pace, on a real job, not a benchmark.
- That editor says beginners run one ambience through the whole scene. A background also holds off-screen events: cars, dogs, horns, bells. They stress movement, and a reason for every sound. A second commenter agrees on movement.
- Several commenters say to mark each location and reuse its sounds later, moved around so it is not identical.
- Several commenters say to do a rough pass of the whole film first, then refine. One does feet first.
- One commenter says picture is often not locked on animation, which changes the time needed.
- Tools named: Cut It, Ambience Cutter, Nuendo auto edit. AmbienceFriend was asked about, with no report on it. None were checked here.
- **Ranking or routing:** change to the ambience route, not its ranking. Today it is one 15 to 60 s loop. Add: a quiet bed, plus separately generated sparse events placed at varied times, kept per location and varied on reuse.

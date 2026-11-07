# Sound effects survey: craft, tells, licences, law

Research for the planned public plugin sfxwright (plan, create, edit sound effects for media and games). All sources checked 2026-11-06. Not legal advice.

Evidence labels:

- **[read]**: I fetched the primary page or PDF. Web pages came through a summarising fetcher, so recheck quotes before reuse; PDF quotes are from extracted text.
- **[snippet]**: search result summary only, page not opened or the page refused the fetch.
- **[recall]**: general knowledge, not checked in this pass. Verify before it goes into a skill as fact.
- **UNSETTLED**: no court, standard or authority has answered it.

## Findings that should shape the plugin

1. No store rule found bans AI sound. Steam and itch.io require disclosure; Epic has none that I found; Apple and Google regulate data and runtime generation.
2. Every named AI audio backlash I found concerns voices. I found no named incident about AI sound effects specifically. That absence comes from limited searching, not proof, and no Reddit thread surfaced.
3. Sonniss, BOOM and A Sound Effect licences ban AI training. A plugin must never feed those files into model training. Whether using them as conditioning input counts is UNSETTLED.
4. A prompt alone gives no US copyright according to the Copyright Office. Human layering and editing may protect the human part, case by case. So a recorded trail of human edits has real value.
5. Variation numbers are convention, not standard. Start small and tune by ear.
6. ASWG-R001 measures a whole game mix for at least 30 minutes. It is no target for a single effect file.

## 1. How the work is done

### Spotting and cue sheets

Spotting decides where sound goes against a locked picture and yields a list of cues with timecodes ([Wikipedia](https://en.wikipedia.org/wiki/Spotting_(filmmaking)), [Post Super](https://post-super.com/blog/spotting-sessions-part-2-what-are-you-looking-for)) [snippet]. Keeping dialogue, effects and temp music on separate stems lets the temp be muted during the session [snippet].

Usual editorial split: hard effects, backgrounds, foley, design [recall]. Games replace the timeline with an asset list keyed to events: event name, trigger, variations, loop or one-shot, priority, voice limit [recall].

### Layering

A hit is commonly built from a transient, a body and a tail. One guide gives ranges: sub 20-80 Hz, body 80-500 Hz, air 10 kHz and up, plus a tail or ambience layer; another gives the transient 4-12 kHz ([Pixflow](https://pixflow.net/blog/sound-effects-layering)) [snippet]. These are a vendor blog's rules of thumb. A sweetener is a layer that enriches without being noticed alone ([Morphic glossary](https://morphic.com/resources/how-to/sound-effects-glossary)) [snippet]. Whooshes: filtered noise sweep, pitch-bent oscillator, short transient hit ([Sonilo](https://sonilo.com/ai-music/how-to-make-sound-effects)) [snippet].

### Recording and foley

Record components (latch, movement, contact, debris, room decay) separately, because they sync and remix more easily ([Creator Sounds Pro](https://creatorsoundspro.com/%f0%9f%8e%99%ef%b8%8f-foley-sound-layering)) [snippet]. Viers covers microphones, recorders and building a foley stage (see the books list). Contact mics, shotgun technique and high sample rates for pitch-down were not sourced in this pass [recall].

### Synthesis

Noise plus filter sweeps, FM, granular and physical models. Farnell's *Designing Sound* is the procedural reference (books list). Procedural suits UI, sci-fi and parameter-driven engines; organic hero sounds usually still start from recordings [recall].

### Library search and naming

**UCS** (Universal Category System): current version 8.2.1, January 2024; describes itself as a "public domain initiative" ([universalcategorysystem.com](https://universalcategorysystem.com/)) [read]. Filename: `CatID(-UserCategory)_(VendorCategory-)FXName_CreatorID_SourceID_UserData`, no underscores inside a segment ([ucsrename docs](https://pkg.go.dev/github.com/brettbuddin/ucsrename/ucs)) [snippet]. The only hard requirement is a valid CatID at the start; FXName ideally under 25 characters ([JamSoft](https://www.jamsoft.co.uk/samplesort/support/universal-category-system/)) [snippet]. Paquin's guide says roughly 10-15 words instead, so the two disagree ([A Sound Effect](https://www.asoundeffect.com/metadata-style-guide/)) [snippet]. Category counts conflict (600+ CatIDs versus 1,600+ terms), so read the count from the official list.

**Metadata**: pro packs describe files in BWF bext (Description, Originator, OriginationDate) and iXML, often with Soundminer USER fields such as CATEGORY, SUBCATEGORY, DESCRIPTION ([foley issue 228](https://github.com/reeleehq/foley/issues/228)) [snippet]. Writing Soundminer's Description updates its wrapper plus BWAV, iXML, XMP and ID3 together ([Creative Field Recording](https://www.creativefieldrecording.com/2016/08/30/soundminer-metadata-101/)) [snippet]. [BWF MetaEdit](https://mediaarea.net/BWFMetaEdit/tech_view_help) embeds, validates and exports BWF metadata [snippet]. Bext is limited and was used inconsistently, so iXML is richer ([Wikipedia iXML](https://en.wikipedia.org/wiki/IXML)) [snippet].

### Mixing and delivery numbers

| Medium | Target | Peak | Measured on | Status |
|---|---|---|---|---|
| European broadcast, [EBU R128 v5, Nov 2023](https://tech.ebu.ch/docs/r/r128.pdf) | -23.0 LUFS; ±1.0 LU where impractical such as live; ±0.5 LU otherwise per revision notes | -1 dBTP in production | Whole programme, no emphasis on speech, music or effects | [read] |
| US broadcast, ATSC A/85 | -24 LKFS | Not checked | Full programme per the source | [snippet], [Fora Soft](https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026) |
| Netflix | -27 LKFS ±2, dialogue-gated | -2 dBTP (limiter ceiling suggestion -2.3) | Dialogue | [snippet] of spec v1.6 mirror; see below |
| Audio streams, [AES TD1004.1.15-10, 2015](https://aes.org/wp-content/uploads/2024/01/AESTD1004_1_15_10.pdf) | -16 to -20 LUFS | Not extracted | Stream | [read] |
| Sony home, [ASWG-R001 v1.10, Aug 2013](http://gameaudiopodcast.com/ASWG-R001.pdf) | -24 ±2 LKFS | -1 dBTP | Whole mix, at least 30 minutes, representative gameplay | [read] |
| Sony portable, same document | -18 ±2 LKFS | -1 dBTP | Same | [read] |

Cautions:

- ASWG-R001 is a Sony studio recommendation from 2013. It says audio "should be measured as a whole, and should not focus on dialogue, sound effects or music specifically". No file-level effect loudness follows from it.
- Netflix's old URL now redirects to a [studiopartner page](https://studiopartner.netflix.net/studio/branded-sound-mix-spec-and-best-practices) that returned only a heading to my fetcher, so the current spec is unread. Guides disagree about Atmos true peak, and a -24 fallback for low-dialogue programmes is unverified. Check before quoting.
- Cinema: EBU R128 s4 covers cinematic content; not read. Theatrical level is calibrated monitoring rather than a LUFS target [recall].

### Stems

Academy preservation practice lists BWF files, composited dialogue, music and effects stems in 7.1, 5.1 and two-track, plus M&E for theatrical and nearfield ([Academy forum](https://academydigitalpreservationforum.org/?p=4797)) [snippet]. Delivery checklists also verify channel order and naming ([Evercast](https://www.evercast.us/blog/post-production-checklist)) [snippet].

### Implementation

| Engine | Facts | Status |
|---|---|---|
| Unity | ADPCM: constant 3.5x, slightly more CPU than PCM, meant for noisy repeated sounds (footsteps, impacts, weapons). Decompress On Load for small sounds; Vorbis costs about 10x memory when decompressed. [AudioClip manual](https://docs.unity3d.com/6000.1/Documentation/Manual/class-AudioClip.html). Audio Random Container builds playlists for footsteps, impacts, weapons, props: [manual](https://docs.unity.com/en-us/engine/current/manual/audio/random-container) | [snippet]; container overview [read], its settings not read |
| Godot | `AudioStreamRandomizer`: `random_pitch` picks between 1/value and value; `random_volume_offset_db` of 3.0 means ±3 dB. [Docs](https://docs.godotengine.org/en/stable/classes/class_audiostreamrandomizer.html). [Issue 82469](https://github.com/godotengine/godot/issues/82469) reported the volume offset silent in a 4.2 dev build; resolution unknown | [snippet] |
| Roblox | [Creator Hub](https://create.roblox.com/docs/audio/assets): mp3, ogg, wav, flac; under 20 MB and 7 minutes; up to 48 kHz; mono, 2.0, 3.0 or 5.1. 2,000 free imports per 30 days if ID verified, 100 if not. Must hold legal rights; assets pass moderation; effects can go on the Creator Store | [read] |
| Unreal | [MetaSounds index](https://dev.epicgames.com/documentation/en-us/unreal-engine/metasounds-in-unreal-engine): procedural footsteps templates, Builder API from Blueprint. Sound Cue relation not on that page | [read] |
| FMOD | Multi instruments with random or shuffled playlist, scatterer instrument, modulators on pitch and volume: [docs](https://www.fmod.com/docs/2.03/studio/modules-and-instruments.html). Units unconfirmed | Weak: thin summary of a fetched page |
| Wwise | Random container with shuffle and avoid repeating last N, per-trigger pitch and volume randomizers: [Zúmer tutorial](https://javierzumer.com/blog/2019/11/20/tutorial-wwise-parte-ii), [Audiokinetic Q&A](https://www.audiokinetic.com/qa/8949/how-can-i-avoid-repetition-from-different-containers). Official docs returned 403. Units (cents, dB) [recall] | [snippet] |

### Variation conventions

No authoritative standard exists in what I found. These are blog figures and they disagree:

| Parameter | Published values | Source |
|---|---|---|
| Pitch | ±2 semitones (±200 cents); ±5-15% (about ±0.8 to ±2.5 semitones); Unity example 0.9-1.1 (about ±1.7 semitones) | [All Clash](https://www.allclash.com/your-games-audio-sounds-flat-but-dont-worry-middleware-fixes-it/), [Game Audio notes](https://code-note-vr.vercel.app/game-audio), [Generalist Programmer](https://generalistprogrammer.com/game-audio-development) |
| Volume | ±1.5 dB subtle; ±2-6 dB ambience | Same group, [snippet] |
| Count | 3-5; 3-8; 4-6 for ambience; one example has 20 on concrete, 15 on wood, 12 on gravel | Same group, [snippet] |
| Repeats | Avoid the same variation twice in a row | Same group plus Wwise sources |

Which blog gave which figure was not tracked per cell; reopen them before citing one.

Suggested default for a skill, my judgement: 5 or more variants for frequent sounds, pitch ±1 semitone, volume ±1.5 dB, no immediate repeat, widen by ear. Wide pitch shifts change perceived size, so set them per material [recall].

## 2. Editing by script

| Tool | Good at | Status |
|---|---|---|
| ffmpeg | Batch conversion, `afade`, `silenceremove`, loudness measure then apply. Single-pass `loudnorm` can pump; use two passes ([32blog](https://32blog.com/en/ffmpeg/ffmpeg-audio-normalization-loudnorm), [DEV](https://dev.to/masonwritescode/two-pass-loudness-normalization-with-ffmpeg-loudnorm-the-right-way-1nm3)). `ffmpeg-normalize` wraps both passes | [snippet] |
| SoX | Effect chains (`trim`, `fade`, `norm`, `rate`, split on silence): [man page](https://man.archlinux.org/man/sox.1.en). Fork `sox_ng` exists | [snippet] |
| Python | [Pedalboard](https://github.com/spotify/pedalboard): effects and plugin hosting, GPL v3, which matters if the plugin bundles it. soundfile and numpy for slicing, peak checks, analysis [recall] | [snippet] |
| REAPER | ReaScript scripts sessions and renders regions; `-renderproject` runs headless ([reaproj](https://pypi.org/project/reaproj/)); [BWF ReaScripts](https://www.extremraym.com/en/download/reascripts-bwf-metadata/). Official API docs not read | [snippet] |
| BWF MetaEdit | Bext and iXML read, write and validate | [snippet] |

Scripts do well: trim silence, fades, click-safe loops, normalising a set consistently, sample rate and format conversion, UCS renames, metadata, spectral and peak checks, rendering variants, QC reports. Short files need care, since integrated loudness has gating limits; compare with momentary or short-term loudness [recall].

Needs a person [recall, my judgement]: whether a sound suits the picture, sync feel, layer balance, emotional weight, fatigue over hours of play, whether a variation set sounds like one object, final mix in context on real speakers. A script can flag these, not decide them.

## 3. What pros and audiences hate

### Tells of AI sound

Testers report footsteps without believable cadence, thin output without character, toy-like trains in a dead room, balloons without the pop, and brittleness to word choice ([Y.M.Cinema](https://ymcinema.com/2024/03/26/say-goodbye-to-sound-designers-meet-elevenlabs-new-ai-generated-sfx/), [AudioCipher](https://www.audiocipher.com/post/elevenlabs-ai-sound-effect-generator)) [snippet]. A 2026 review on an unofficial site lists unexpected sounds, unnatural transitions, wrong timing, extra background elements, artifacts and poor consistency ([review](https://elevenlabsguide.pages.dev/blog/elevenlabs-sound-effects-review/)) [snippet]. Reviewers do rate creative design and environments as strong.

"Smeared transients" was my hypothesis and no source confirmed it. Measure it in the plugin's own tests. No practitioner forum thread could be read.

### Overused library sounds

Named by [Wikipedia's stock sound effect article](https://en.wikipedia.org/wiki/Stock_sound_effect): Wilhelm scream (from *Distant Drums*, 1951), Howie scream, red-tailed hawk, castle thunder [snippet]. One unsupported claim says Star Wars retired the Wilhelm; ignore it. That free-pack sounds become recognisable is plausible, but I found no source for it.

### Named incidents, all voice

- **Arc Raiders** (Embark): flat AI lines drew complaints despite actor contracts; on 3 Nov 2026 Embark called the criticism fair and said synthetic lines will be phased out over coming years ([PC Gamer](https://www.pcgamer.com/games/third-person-shooter/there-was-some-really-fair-criticism-arc-raiders-devs-understand-why-players-were-so-upset-about-its-ai-use-but-admit-that-it-was-too-impractical-to-record-every-voice-line/)) [snippet].
- **Fortnite** (Epic, 2025): SAG-AFTRA filed an unfair labor practice complaint over AI character voice ([Wikipedia](https://en.wikipedia.org/wiki/Artificial_intelligence_controversies)) [snippet].
- **No Thanks** (indie, Oct 2026): developer removed AI voice lines ([PC Gamer](https://www.pcgamer.com/gaming-industry/game-development/i-drank-from-the-chalice-of-blood-indie-dev-scrubs-his-game-of-ai-generated-voice-lines-having-previously-described-the-technology-as-anti-human-and-anti-art/)) [snippet].
- **Neverness to Everness** (2026): suspected AI assets; a voice actor threatened to leave ([Wikipedia](https://en.wikipedia.org/wiki/Neverness_to_Everness)) [snippet].
- **Voiceverse NFT**: AI voice plagiarism scandal involving 15.ai ([Wikipedia](https://en.wikipedia.org/wiki/Voiceverse_NFT_plagiarism_scandal)) [snippet].

### Store rules

**Steam** [read, [content survey](https://partner.steamgames.com/doc/gettingstarted/contentsurvey)]: "Efficiency gains through the use of these tools is not the focus of this section." The disclosure covers content players consume, including sound.

- Pre-Generated: "Any kind of content that ships with your game and is consumed by players" made with AI tools during development; reviewed like non-AI content.
- Live-Generated: "Any kind of content created with the help of AI tools while the game is running"; same rules, plus "you'll need to tell us what kind of guardrails you're putting on your AI".
- Secondary sources date a rewrite to 16 or 17 Jan 2026 [snippet].

**itch.io** [read, [quality guidelines](https://itch.io/docs/creators/quality-guidelines)]: tag generative AI through the AI Disclosure section. "We are strictly enforcing disclosure for all game asset, soundtrack, physical game, comic, and book pages"; failure "may result in delisting". "Projects using self-contained algorithms without external large datasets don't require an AI disclosure", which favours procedural synthesis. A sound pack sold as a game asset must disclose.

**Epic**: no mandatory disclosure found; press only. Sweeney opposes labels ([PC Gamer](https://www.pcgamer.com/software/ai/epic-boss-tim-sweeney-thinks-stores-like-steam-should-stop-labelling-games-as-being-made-with-ai-it-makes-no-sense-he-says-because-ai-will-be-involved-in-nearly-all-future-production/)); the store's chief says "we let players decide" ([Yahoo](https://tech.yahoo.com/gaming/articles/not-police-developers-games-epic-150000195.html)) [snippet]. No Epic policy document read.

**Apple** [read, [guidelines](https://developer.apple.com/app-store/review/guidelines/)]: no AI content label found in the part read (the last 14,428 of 114,428 characters unread). 5.1.2(i) covers personal data shared "with third-party AI". 1.2 treats AI content creation apps as user-generated content. 5.2: only content "you created or that you have a license to use".

**Google Play** [read, [policy](https://support.google.com/googleplay/android-developer/answer/13985936?hl=en)]: apps that generate content from user prompts must prevent restricted content and offer in-app reporting. The page states no disclosure rule. That pre-made AI content is out of scope is implied, not stated.

## 4. Licences and law

Not legal advice. Have a lawyer read anything commercial.

### Sources

| Source | Terms | Trap | Status |
|---|---|---|---|
| [Freesound](https://freesound.org/help/faq/) | Per file: CC0, BY, BY-NC. Older Sampling+ is being retired but still present | Check every file. BY needs credit. BY-NC bars earning money. AI uploads must be tagged GenAI and name the model, so screen those too | [read] |
| [Freesound API](https://freesound.org/docs/api/resources_apiv2.html) | Search filter on `license`; fields include `license`, `gen_ai_preference`, `md5`; `page_size` up to 150; similarity via `laion_clap`. Originals need OAuth2; previews about 64-192 kbps. Usage endpoint reports burst and daily limits; numbers not stated there. `bitrate` and `bitdepth` unreliable | Previews are lossy, so do not ship them. Whether preview terms differ is not stated. Respect `gen_ai_preference` "no-gen-ai" | [read] |
| [Sonniss bundle licence](https://sonniss.com/gdc-bundle-license/) v2.0, effective 27 Aug 2026 | Worldwide, royalty-free, modify and use commercially, no attribution. No distributing "as sound effects", including edits in packs ([FAQ](https://sonniss.com/gameaudiogdc/)). No AI training without written permission. English law. Your version is that of your download date | Current: [GDC 2026](https://gdc.sonniss.com/), 7.47 GB+, 347+ files. GDC 2024 was 23.5 GB; no 2025 bundle. Page limits use to media production | [read] |
| [Kenney](https://kenney.nl/support) | CC0, attribution not required | Logo restricted | [read] |
| [OpenGameArt](https://opengameart.org/content/faq) | Per-asset licences [recall] | FAQ returned 403; terms unread. Provenance varies [recall] | Unread |
| BBC Sound Effects | RemArc: personal, educational, research use; commercial needs a paid licence, reportedly through Pro Sound Effects ([Melbourne guide](https://unimelb.libguides.com/c.php?g=403071&p=6498600), [MusicTech](https://musictech.com/news/music/the-bbc-sound-effects-archive-over-33000-free-samples/), [Swarmify](https://swarmify.com/blog/free-sound-effects-websites/index.html)) | Official pages blocked to my tools. Social upload terms reportedly conflict. Treat as not for games or commercial work | [snippet] |
| [A Sound Effect EULA](https://www.asoundeffect.com/license-agreement/), [BOOM terms](https://www.boomlibrary.com/terms-conditions/), [Sonniss library licence](https://sonniss.com/license/) | All bar AI training per search summary. A Sound Effect restricts products at least 50% pure sound effects by runtime | Not read directly; Soundly not found. Read each per pack. My Pro Sound Effects URL guess returned 404 | [snippet] |

### Models

- [Stable Audio Open 1.0](https://huggingface.co/stabilityai/stable-audio-open-1.0): about 486K recordings, mostly Freesound, plus Free Music Archive; CC0, BY and Sampling+; Stability community licence, gated [snippet]. Whether BY attribution passes through to outputs is UNSETTLED.
- [AudioGen](https://huggingface.co/spaces/Nymbo/MusicGen/raw/main/model_cards/AUDIOGEN_MODEL_CARD.md): code MIT, weights CC-BY-NC 4.0, so not for commercial work [snippet].
- [ElevenLabs](https://elevenlabs.io/sound-effects): paid accounts commercial, free non-commercial per its product page [snippet]; full terms unread.

### US copyright in generated output

[Copyright and AI, Part 2](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf), January 2025 [read]:

- p. iii: "Copyright does not extend to purely AI-generated material, or material where there is insufficient human control over the expressive elements."
- p. iii: "Based on the functioning of current generally available technology, prompts do not alone provide sufficient control."
- p. iii: AI used "to assist rather than stand in for human creativity does not affect the availability of copyright protection".
- p. iii: authors keep rights in their works perceptible in outputs, and in "creative selection, coordination, or arrangement", or "creative modifications".
- p. 41: "Prompts alone, however, at this stage are unlikely to satisfy those requirements."

This is agency guidance, not a binding ruling. [Thaler v. Perlmutter](https://www.hklaw.com/en/insights/publications/2026/03/the-final-word-supreme-court-refuses-to-hear-case-on-ai-authorship): certiorari denied 2 Mar 2026; the human authorship requirement stands, without a Supreme Court opinion [snippet].

Practical reading (mine): feeding your own recording into a model may keep rights in what stays perceptible; layering and editing may protect that human contribution, but not the raw AI component. Keep the prompt, seed, sources and edit log.

UNSETTLED:

- How much human control suffices. [Allen v. Perlmutter](https://www.nortonrosefulbright.com/en/knowledge/publications/ce8eaa5f/ai-in-litigation-series-an-update-on-ai-copyright-cases-in-2026) is reportedly pending in Colorado; docket not checked.
- Whether layering or pitch and EQ edits on a short generated effect meet the originality minimum. I found nothing specific to sound effects.
- Whether output imitating training data infringes, and liability for training itself. The report says a later part covers training.
- Other countries differ; the report's section III surveys them, and Japan uses a factor test.

### Trademarked sounds

The two USPTO sound mark URLs I tried returned 404, so no primary register record was read. Everything below is secondary; check [TSDR](https://tsdr.uspto.gov/) before relying on it.

| Sound | What sources say | Confidence |
|---|---|---|
| NBC chimes | Early sound mark, 1950 service mark per [Alt Legal](https://www.altlegal.com/blog/behind-the-jingles-legal-strategies-to-protect-sound-trademarks/) and others; one says 1978 | Medium |
| Intel bong | Sound mark; four or five notes depending on source ([Global Law Experts](https://globallawexperts.com/news/want-to-trademark-a-sound-heres-how-brands-like-intel-nbc-and-mgm-did-it)) | Medium |
| THX Deep Note | Registered 1992 per [Wikipedia](https://en.wikipedia.org/wiki/Deep_Note); number unverified. Lucasfilm sued Dr. Dre in 2000 over its use ([MTV](https://www.mtv.com/news/j29d27/dr-dre-sued-by-lucasfilm)); outcome unconfirmed | Medium |
| Lightsaber | First used April 1999, registered May 2009, Lucasfilm, toy swords and role-play toys ([That's a Trademark](https://www.thatsatrademark.com/blog/lightsaber-sound)) [read]. That page cites Reg. 3,618,321 without tying it to the sound | Medium |
| Darth Vader breathing | Reported registered by Lucasfilm ([DuetsBlog](https://www.duetsblog.com/2014/10/articles/trademarks/star-wars-redefining-trademark-and-copyright-law-since-a-long-time-ago/)) | Low |
| MGM lion, Netflix ta-dum | Commonly listed as marks | Low |

Suggested rule for the plugin: decline to recreate these by name and offer original sounds built from acoustic traits instead. Trademark covers listed goods and likely confusion, whereas copyright separately covers the recording or composition [recall]; how far a game's soundalike reaches is UNSETTLED. Functional or generic sounds are harder to register ([Trademark Law Firm](https://www.howtogettrademark.com/on-the-mark/famous-sounds-that-have-received-a-trademark)) [snippet]. Lucasfilm reportedly refused a fan's R2-D2 sound request in 2013 ([KVR thread](https://www.kvraudio.com/forum/viewtopic.php?t=398604)) [snippet].

## Gaps to close

- Primary text: Wwise and FMOD randomizer units, Unity container reference, ffmpeg `loudnorm` defaults, current Netflix spec, BBC licence, USPTO TSDR records, the three library EULAs.
- Practitioner opinion: only Reddit snippets are allowed, and none surfaced. GDC talks and the Designing Sound site could fill this.
- Measured AI artifacts: run tests on real model output.

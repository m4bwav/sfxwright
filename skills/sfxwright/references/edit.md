# Editing

| Want | Use | Cost |
|---|---|---|
| Bigger, heavier | `edit --op pitch --value -5` (varispeed) | Longer; extreme shifts expose a model's band limit |
| Same pitch, other length | `edit --op stretch` (ffmpeg atempo) | Smears attacks: fine for beds, poor for hits |
| Sweep or riser | `reverse`, then pitch or fade | |
| A space on a dry sound | `edit --op convolve --ir room.wav --value 0.3` | Know the impulse's licence |
| Clean ends | `edit --op tidy` | Removes DC, trims, fades to zero |

A harsh sound can hide slow material: pitch train or lorry brakes down three or four octaves and listen (Murphy, *Ears to the Ground*, 2024, ch. 4). A recorded room or building as the impulse suits percussion (ch. 3). To add weight without showing the source, look at where a sound's energy sits and blend it under an instrument with energy there (ch. 1). When recording, a contact mic on a rail or fence takes vibration, not air (ch. 4). These are artists' reports, untested on generated sound.

Past a limited range, artifacts are the effect, not a bug to tune out. Pitch shift and frequency shift differ.

## Unpleasant or wearing

From Cowan, *The Effects of Sound on People* (2016, sec. 5.2). Its data is mostly transport noise and lab tests, so these are untested on generated audio.

- **Screech:** in the study it reports, unpleasantness did not change with level and fell when content below 4 kHz was removed, with 1.4 and 2.8 kHz carrying it. Try cuts there before turning it down or dulling the top end.
- **Bass-heavy sound:** dBA underrates low-frequency annoyance by 3 to 8 dB, and dBC or unweighted readings overrate it by 10 dB or more. Do not settle it with one reading.
- **Alerts (inference):** annoyance rises with fear and lack of control and falls when a sound seems important. A repeated alert may wear less if the player can act on it and sees why it matters.

## Thin or muddy output

Try a few seeds first (`--takes 4`). If none works, generate parts apart and layer: transient, body, low thump, tail. Stage the layers a few ms apart with `--offsets` rather than stacking every attack on one sample, then dip the gain just after the head so the body does not bury it; every layer at full level from the same instant makes a wall of sound with no front. `layer` warns ONSETS_COINCIDE when two first onsets land within 3 ms (Zdanowicz and Bambrick, ch. 3, book rule, unverified). In one blind listen (five sounds, one listener, 2026-11-07) the winners were spread: first take 2, another seed 1, generated parts 1, the `bigger` recipe 1. "All about the same" was never picked, so takes do differ, but seeds won 3 of 5 with 3 of 5 clips, which is what chance gives. Layering is an option to try, not a proven upgrade. `layer` aligns peaks; offset layers a few ms apart when they phase. A weak attack wants a real transient: `synth click` or `modal` under it. Big sounds get detail from debris layers, not more low end. Add "bright, crisp" for dull output; metallic ringing may be a model artifact no prompt fixes.

Say why before an edit: a fix, a feature or a fit. Copied settings do not transfer between sources. These moves come from music mixing (Case, *Sound FX*, 2007). None has been heard on generated sound, so treat each number as a starting point:

- **Muddy, no punch:** try a narrow cut somewhere in 180 to 400 Hz, which may reveal the lows. Keep that band in at least one layer, or the whole goes thin.
- **Thin alone:** judge it with its neighbours first. A layer may be right when another layer or the scene fills the band.
- **Nothing in a band to boost:** EQ can only raise what exists. Light distortion adds new harmonics, but they can mask other layers, so listen to the whole.
- **Dull or blunt front:** with a compressor, slow attack and slow release sharpen the front; a fast release undoes it. Attack and release values do not transfer between tools.
- **Fix level before effects:** reach for gain, pan and a volume envelope before a processor. A rogue peak is an envelope job; a compressor there also squeezes the quiet parts and blends layers together, while an envelope keeps each layer's dynamics distinct.
- **Order in a chain:** the later an effect sits, the more it shows. EQ before a compressor gets reshaped by it; EQ after shapes the squeezed result. A delay or reverb early in the chain comes out subtler than one placed last. Try both orders and listen.
- **Serial or parallel:** a serial chain changes the one signal; a parallel chain mixes a processed copy (wet) back under the dry, which adds body to a thin sound without losing its attack. Francis, *The Audio Effects Workshop* (2011, ch. 3, 13, 14): music-mixing practice, untested on generated sound.
- **Hollow after layering:** two copies under about 50 ms apart comb filter. At equal level, the nulls fall at odd multiples of 1/(2t): 1 ms nulls 500 Hz. Change the offset or the level.

## Building from parts

From a synthesis textbook (Shepard, *Refining Sound*, 2013). It is about music, so the use for effects is inference, untested on generated sound.

- **Describe it first.** A bell: quick attack, long decay, partials that die at different rates. Then pick the method.
- **Noise colour:** red for boomy lows, pink for rain, blue for shimmer on metal, violet for sibilance, crackle for fire.
- **Short hits:** the timbre is in the attack, so spend layers there. Give each layer one job: a bright front, a slightly longer body for depth, a pitched blip.
- **Metal:** inharmonic partials (FM at a non-whole ratio, additive at non-whole ratios) clang; whole ratios sound pitched. FM is touchy, so start from a working sound and move in small steps. A 10 ms delay with high feedback also turns a layer metallic.
- **Thicker, same pitch:** detuned copies in even pairs around a centre, such as plus and minus 3 and 7 cents.
- **Curves:** straight fades sound mechanical. Put most of the change early in a rise or a fall.
- **Event blip:** a very fast pitch rise and fall on one layer.
- **Shift:** pitch shift keeps partials' relation; frequency shift moves all by the same hertz and breaks it, for a less natural sound.
- **Intensity:** a harder hit is more than louder: shorter attack and decay, longer tail. `vary` changes pitch and gain only, so make hard and soft takes apart.
- **Distance:** longer reverb pre-delay reads closer, shorter reads farther.
- **Wind and surf:** noise through a lowpass or bandpass. Moving the cutoff moves the apparent pitch; resonance focuses it. Resonance can also raise the level sharply, so check the peak afterwards. (Aikin, *Power Tools for Synthesizer Programming*, 2004, for this line and those below; music book, untested on generated sound.)
- **Unstable pitch:** modulate a tone's pitch with low-pitched noise for a gargle.
- **Bite and sweeps:** hard sync with the slave's pitch swept by an envelope gives a metallic sweep; an envelope on FM depth makes a bright attack.
- **Ring mod:** outputs sums and differences, not the inputs. Mix some dry back to keep the pitch; at a non-simple ratio the pitch centre goes.
- **Steady throb:** a detune in cents beats faster as pitch rises (5 cents: about 0.2 Hz at 65 Hz, 6 Hz at 2 kHz). Offset in hertz for one rate across a set of pitches.
- **Distortion follows level:** it crunches the loud attack and spares the tail. More drive evens that out and flattens the envelope. Distort layers apart: distorting a mix at non-simple pitch ratios adds beating and roughness.
- **Harder is also brighter:** raise the lowpass cutoff with intensity, not only the level.
- **Big but short:** gated reverb gives a large space that stops before it covers the next sound. Slapback under 50 ms smears transients, so keep it off percussion.
- **Space by hand:** damped highs read as natural; highs outlasting lows read as artificial. Short delay taps before a reverb set the early reflections. A 100 to 500 ms delay with 20 to 50% feedback and damping stands in for reverb on sustained sounds.
- **True reverse reverb:** reverse the sound, add reverb, reverse the result.
- **Wash hides detail:** early reflections alone suggest a space without the late tail that masks.

## Layer recipes

From the film books, one engineer's ear each. Only `bigger` has been heard here: it won 1 of 5 in a blind listen, no better than chance (2026-11-07). `layer FILE --out OUT --recipe`:

- `bigger`: 100, 80 and 50% speed. Pitch moves with speed. Try `--gains 0,-3,-6`.
- `pitch`: 0, -3, -6, -9 semitones. Small steps suggest movement; large ones trail away.
- `offset`: six rotated copies of a bed. The same clip started at one place only gets louder.

## Builds by event

Viers, *The Sound Effects Bible* (2008, ch. 18), one designer's recipes from recorded sources, untested on generated audio. Make each part a separate take, then `layer` or `place` them:

- **Explosion:** concussion, then debris, then a trail-off; debris may keep falling after the trail-off ends. Trail-off: a 5 to 15 s dark reverb on the concussion, then pitch down (bright reverbs stay bright). Add a reversed, reverbed, pitched-down copy under it. A fireball fades in after the concussion's attack, so it reads as caused by it.
- **Crash:** the first hit is the loudest thing; keep everything before and after well below it. Then plastic, glass, debris, with pitched-down copies of the hit. A skid cut at the hit means a dead stop; one running past it means speed.
- **Automatic fire:** single shots at the real weapon's rate, different shots, each tail ringing under the next; never butt them end to end.
- **Body fall:** two or three staggered hits, not one.
- **Punch:** dull thump plus a wet splat, a bone crack or short reverb optional. **Sword:** whoosh lead-in, ringing strike, and a layer of the surface it hits.
- **Rumble or LFE:** low-pass near 100 Hz (more than once), compress. Steady: white noise filtered and pitched down. Use under other sounds, rarely alone.
- **Mouse-over:** a short sound through delay, reverse, delay, reverse, then pitch up. High beeps sound loud at low level: do not normalize them.
- **Laser:** an impact through delays and a pitch bend, or a pitch-bent beep.
- **Clean attack, full body:** a quiet take keeps the attack clean but loses decay; cut a clean attack from one take onto the body of another.

## Moves from theatre

Fry (2019), a designer's practice, untested on generated audio:

- **Farther away:** a close source needs more than less level. Cut the top, soften the attack, add a room. Fry also cuts bass; air absorbs mainly highs, so treat that as taste.
- **Thicker:** copy the sound, drop it octaves at the same speed, layer it under the original.
- **Riser:** a sharp hit, a very long reverb, then `reverse`. The reverb's length sets the rise.
- **Drone:** slow a real sound by octaves. Under a scene it adds edge without a melody to compete with.
- **Repeats:** the same sound repeated reads as copy and paste; set in a rhythm it reads as music.
- **Rhythm from another sound:** gate a bed from a side chain (crowd noise opening on a heartbeat).
- **Bait and switch:** listeners name a sound early and stop checking, so a passing car can crossfade into a wave.
- **Voice:** mimic what no source gives, disguise it with effects, lay it in with real recordings.
- **Very short and loud:** speakers cannot match a gunshot's crack, so the tail and its space carry it.
- Keep layers as separate files until levels are tried in their final setting.

## Stretching without resampling

Miranda, techniques from composition, untested here. Do them by script; `edit --op stretch` is the built-in option:

- **Brassage:** to lengthen, cut overlapping fragments and lay them end to end; to shorten, leave gaps. Crossfade every join. Very short uniform fragments add a flutter.
- **Zigzag:** play forward and back between turning points. Works best on even or noisy sounds; short fast spans flutter.
- **Wavesets:** edit between zero crossings. Drop cycles to punch holes, swap in other waveforms, or interleave the cycles of two sounds.

Reveillac (2017), from music: use an exciter only on the bands that need it, in small steps, and rest your ears, since they adapt quickly. Ring mod below about 20 Hz acts as tremolo.

## From synthesis and sampling

Russ, *Sound Synthesis and Sampling* (2nd ed., 2008, sec. 4.3.1-4.3.2, 6.2-6.3, 6.8.3), a music book, untested on generated audio:

- **Render from the original:** make every variant from the source file, never from a processed copy. Each pass adds noise and pitch-shift error, and the losses add up.
- **Small pitch moves on voices and fixed-spectrum hits:** this is why Variation sets keeps them narrow. A big shift turns a voice comic; bells, triangles, tambourines and metal hits just sound wrong.
- **Familiar plus alien:** keep the recognisable layer and add a short blip of an unexpected timbre at the onset, with no sustain and a short decay. On intensity tiers, let it sound only on the hardest hits, since harder hits have richer spectra.
- **Fuse check:** raise one layer against the other until the two stop sounding like two sounds. Stop there.

## From plugin DSP

Pirkle, *Designing Audio Effect Plugins in C++* (2nd ed., 2019), an engineering book for plugin authors, untested on generated audio:

- **Reverb built from delays (sec. 17.2-17.3):** the tail needs fast echoes (Schroeder at least 1,000 a second, Griesinger 10,000) or it flutters, and many spread resonances or it rings metallic. Pick comb delays with no simple ratio between them, set each comb's feedback from its own delay and the wanted decay so all die together, flip every other comb's sign, add all-pass stages to smear the echoes, and damp the highs in the tail.
- **Gate to a floor (sec. 18.2.2):** a hard gate to silence clicks; stop it short of silence or use an expander steeper than about 20:1.
- **Look ahead before a limiter (sec. 18.7):** a detector with any attack misses the first peak; delay the main path by about the attack time.
- **Oversample before drive (sec. 19.1):** saturation and clipping add harmonics, and those above Nyquist fold back as aliasing. Asymmetric drive adds even harmonics, symmetric only odd; several mild stages sound richer than one hard one (sec. 19.2).
- **Smooth swept parameters (ch. 2):** a filter or gain sweep stepped once per block clicks (zipper noise); ramp the value every sample.
- **Modulated delay starting points (sec. 15.1-15.2):** flanger about 1 ms with 2 to 7 ms of sweep and feedback; vibrato fully wet; chorus 1 to 30 ms with little feedback. The author calls these subjective.

## Futz and worldize

Holman, *Sound for Film and Television* (3rd ed., p. 76, 162), film practice:

- **Phone or radio voice:** band-pass alone sounds too clean for a modern phone; add nonlinear distortion (drive, a small bad speaker impulse). The speaker on screen is heard clean, the far end futzed, and the roles swap at each cut.
- **Worldize:** replay a clean sound through a speaker in a real room and record it, moving speaker or mic for a changing colour; keep the clean take beside it so the mix can crossfade.
- **Closer shot:** add a brighter layer in sync, since nearer sounds are louder and brighter.

## Show kit

From Yewdall, *Practical Art of Motion Picture Sound*, 4th ed. (p. 351, 489): design each recurring event (a door, a gunshot combo, a punch, a fall, a machine) once, get it approved, premix it to one stereo file and reuse it across the project, so heavy scenes are cut quickly on few tracks. Archive the kit with the sessions so a later cut can be rebuilt. Bake fast whip pans (lasers, ricochets) into the file; a mixer cannot pan many fast moves live.

## On picture

The Mentos pilot's layered mix beat the film's own generated sound in one blind listen on one shot, though the listener called it artificial. Layering over picture is worth trying; expect to replace takes before it convinces. Set each sound's level with `add --gain`, which `place` applies.

## Variation sets

- One source with `vary`: pitch and gain only, so one attack. It may still machine-gun.
- Better: several takes through `vary`, or split into segments and swap layers.
- Tails: a set whose takes ring out for clearly different times (one dry, one in a hall) reads as two palettes. Listen for it; `set` does not measure it.
- Start points, conventions not standards: 5 or more for frequent sounds, pitch +/-1 semitone, volume +/-1.5 dB, no immediate repeat. Noisy impacts take wider pitch; tonal and vocal sounds narrower.

Aikin (2004, music book, untested here): random detune beats identical repeats but does not mimic a different strike. Detuning one layer of several works better than moving the whole sound.

## Footsteps

`sequence` places single hits with uneven timing, no repeat in a row, and a slight limp. `--breaks` restarts timing at cuts. Then `timing` should not flag it. `--walkers 3` or more lays extra walkers over the first, each with its own start, pace and seed draw, 3 dB down, for a group bed.

A natural bed (crickets, rain on leaves, birds) can be built from many copies of one short unit, for control a field take does not give: `sequence unit.wav --count 40 --gap 0.3 --jitter 0.5 --walkers 4`, then `loop`. Vary the unit with a variation set first so copies do not repeat (Murch, ch. 21; unverified by listening).

## Loops

`loop --crossfade 1.5` uses an equal-power crossfade, which suits uncorrelated beds. Use WAV or OGG; MP3 padding breaks loops. Make loops of differing lengths when layering, so they do not repeat together.

## Creatures

When a mic or CC0 animal recordings exist, try those first: voice or animal, slow down, then AM, ring mod, distortion. Perform a growl faster than wanted when it will be slowed, or it ends too long; animals are the cliche, so sweeten a voice with them rather than build on them (Viers, ch. 18). Slowing exposes a low sample rate, as the top of the band falls with it. Generators are the low-confidence fallback.

## Naming

`name --fx "Crate Drop Heavy" --catid WOODImpt --creator ME --source GAME` gives a UCS shape. Search words go in metadata, not the name. `--style short` gives `crate_drop_heavy`.

## Denoise and AI cleanup

Do not clean what `check` finds clean. Compare `check` before and after: cleanup can add artifacts of its own, not yet measured here.

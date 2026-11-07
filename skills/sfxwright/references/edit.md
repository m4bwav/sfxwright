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

## Thin or muddy output

Seed fish first (`--takes 8`). Then generate parts apart and layer: transient, body, low thump, tail. `layer` aligns peaks; offset layers a few ms apart when they phase. A weak attack wants a real transient: `synth click` or `modal` under it. Big sounds get detail from debris layers, not more low end. Add "bright, crisp" for dull output; metallic ringing may be a model artifact no prompt fixes.

Say why before an edit: a fix, a feature or a fit. Copied settings do not transfer between sources. These moves come from music mixing (Case, *Sound FX*, 2007). None has been heard on generated sound, so treat each number as a starting point:

- **Muddy, no punch:** try a narrow cut somewhere in 180 to 400 Hz, which may reveal the lows. Keep that band in at least one layer, or the whole goes thin.
- **Thin alone:** judge it with its neighbours first. A layer may be right when another layer or the scene fills the band.
- **Nothing in a band to boost:** EQ can only raise what exists. Light distortion adds new harmonics, but they can mask other layers, so listen to the whole.
- **Dull or blunt front:** with a compressor, slow attack and slow release sharpen the front; a fast release undoes it. Attack and release values do not transfer between tools.
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

From the film books, one engineer's ear each, and not yet proven here (blind page waiting, 2026-11-07). `layer FILE --out OUT --recipe`:

- `bigger`: 100, 80 and 50% speed. Pitch moves with speed. Try `--gains 0,-3,-6`.
- `pitch`: 0, -3, -6, -9 semitones. Small steps suggest movement; large ones trail away.
- `offset`: six rotated copies of a bed. The same clip started at one place only gets louder.

## On picture

The Mentos pilot's layered mix beat the film's own generated sound in one blind listen on one shot, though the listener called it artificial. Layering over picture is worth trying; expect to replace takes before it convinces. Set each sound's level with `add --gain`, which `place` applies.

## Variation sets

- One source with `vary`: pitch and gain only, so one attack. It may still machine-gun.
- Better: several takes through `vary`, or split into segments and swap layers.
- Start points, conventions not standards: 5 or more for frequent sounds, pitch +/-1 semitone, volume +/-1.5 dB, no immediate repeat. Noisy impacts take wider pitch; tonal and vocal sounds narrower.

Aikin (2004, music book, untested here): random detune beats identical repeats but does not mimic a different strike. Detuning one layer of several works better than moving the whole sound.

## Footsteps

`sequence` places single hits with uneven timing, no repeat in a row, and a slight limp. `--breaks` restarts timing at cuts. Then `timing` should not flag it.

## Loops

`loop --crossfade 1.5` uses an equal-power crossfade, which suits uncorrelated beds. Use WAV or OGG; MP3 padding breaks loops. Make loops of differing lengths when layering, so they do not repeat together.

## Creatures

When a mic or CC0 animal recordings exist, try those first: voice or animal, slow down, then AM, ring mod, distortion. Slowing exposes a low sample rate, as the top of the band falls with it. Generators are the low-confidence fallback.

## Naming

`name --fx "Crate Drop Heavy" --catid WOODImpt --creator ME --source GAME` gives a UCS shape. Search words go in metadata, not the name. `--style short` gives `crate_drop_heavy`.

## Denoise and AI cleanup

Do not clean what `check` finds clean. Compare `check` before and after: cleanup can add artifacts of its own, not yet measured here.

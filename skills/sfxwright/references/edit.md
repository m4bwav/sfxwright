# Editing

| Want | Use | Cost |
|---|---|---|
| Bigger, heavier | `edit --op pitch --value -5` (varispeed) | Longer; extreme shifts expose a model's band limit |
| Same pitch, other length | `edit --op stretch` (ffmpeg atempo) | Smears attacks: fine for beds, poor for hits |
| Sweep or riser | `reverse`, then pitch or fade | |
| A space on a dry sound | `edit --op convolve --ir room.wav --value 0.3` | Know the impulse's licence |
| Clean ends | `edit --op tidy` | Removes DC, trims, fades to zero |

Past a limited range, artifacts are the effect, not a bug to tune out. Pitch shift and frequency shift differ.

## Thin or muddy output

Seed fish first (`--takes 8`). Then generate parts apart and layer: transient, body, low thump, tail. `layer` aligns peaks; offset layers a few ms apart when they phase. A weak attack wants a real transient: `synth click` or `modal` under it. Big sounds get detail from debris layers, not more low end. Add "bright, crisp" for dull output; metallic ringing may be a model artifact no prompt fixes.

Say why before an edit: a fix, a feature or a fit. Copied settings do not transfer between sources. These moves come from music mixing (Case, *Sound FX*, 2007). None has been heard on generated sound, so treat each number as a starting point:

- **Muddy, no punch:** try a narrow cut somewhere in 180 to 400 Hz, which may reveal the lows. Keep that band in at least one layer, or the whole goes thin.
- **Thin alone:** judge it with its neighbours first. A layer may be right when another layer or the scene fills the band.
- **Nothing in a band to boost:** EQ can only raise what exists. Light distortion adds new harmonics, but they can mask other layers, so listen to the whole.
- **Dull or blunt front:** with a compressor, slow attack and slow release sharpen the front; a fast release undoes it. Attack and release values do not transfer between tools.
- **Hollow after layering:** two copies under about 50 ms apart comb filter. At equal level, the nulls fall at odd multiples of 1/(2t): 1 ms nulls 500 Hz. Change the offset or the level.
- **Wash hides detail:** early reflections alone suggest a space without the late tail that masks.

## Variation sets

- One source with `vary`: pitch and gain only, so one attack. It may still machine-gun.
- Better: several takes through `vary`, or split into segments and swap layers.
- Start points, conventions not standards: 5 or more for frequent sounds, pitch +/-1 semitone, volume +/-1.5 dB, no immediate repeat. Noisy impacts take wider pitch; tonal and vocal sounds narrower.

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

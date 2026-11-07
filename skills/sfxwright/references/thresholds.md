# Thresholds

A flag means listen. It is not a verdict, and no flag does not mean a sound is good.

Limits live in `LIMITS` in `sfx_audio.py`. They started as guesses from DSP books.

| Flag | Reading | Limit |
|---|---|---|
| CLIP | run of identical samples at the file's own peak | 4 samples |
| DC | largest channel mean | above -60 dB |
| CUT_HEAD, CUT_TAIL | end sample, or a quarter of its last step | above -50, -60 dB |
| LEAD_SILENCE, END_SILENCE | time before -40 dB of peak; after -50 dB | 0.05 s, 0.25 s |
| CLICK | isolated sample step against its neighbours, outside the attack | ratio above 20 |
| NOISE_FLOOR | steady 200 ms floor, 20 dB under the peak | above -60 dB |
| NO_HEADROOM | peak | above -0.1 dB |
| LENGTH | sound length against the brief | off by 25% or 0.05 s |
| SEAM | end-to-start jump over the 99th percentile step | above 5 (mw.py scale when present) |
| SEAM_SPECTRAL | log-spectrum change across the loop point over the file's 99th percentile change | above 1.0 |
| NEAR_DUPLICATES | best-lag correlation in a set | above 0.98 |
| LEVEL_SPREAD | RMS range in a set | above 3 dB |
| TOO_EVEN | spread of gaps between onsets | below 0.03 |

## Calibration, 2026-11-06

`scripts/calibrate.py`: each file tidied, then each fault planted. 35 Stable Audio 3 takes (one per sound and route: Medium, Small SFX, Small SFX base) plus 8 procedural sounds. Small, and from two model families at most. Not heard. Files already carrying a flag are left out of that row.

| Planted | Generated | Procedural |
|---|---|---|
| DC 0.01, 0.002 | 35/35, 35/35 | 8/8, 8/8 |
| Clip +12 dB, +3 dB | 12/12, 10/12 | 8/8, 6/8 |
| Cut head | 34/34 | 8/8 |
| Cut tail at 40% | 35/35 | 8/8 |
| 1 s padding | 33/33 | 8/8 |
| Click +0.5, +0.1, +0.03 | 20/30, 4/30, 1/30 | 6/7, 3/7, 3/7 |
| Noise -45 dB, -55 dB | 7/14, 2/14 | 1/6, 0/6 |

Flags on clean, tidied generated files (of 35): CLIP 23, NO_HEADROOM 27, NOISE_FLOOR 21, CLICK 5, CUT_HEAD 1. Not known to be false: many takes peak at 0 dB with flat runs, which may be real clipping, and many carry a real low bed. Nobody has listened yet, so these rates are unresolved.

What it supports: trust DC, cuts and padding. Heavy clipping is caught; light clipping mostly. **CLICK misses most clicks under a loud body and NOISE_FLOOR is weak; a clean result on those two proves little.** The click limit went from 8 to 20 because 8 flagged 12 of 31 clean files.

Bugs this found: a strong click posed as the peak and hid in the attack window (now read through a three-point median); fades read as cuts.

## Tried and rejected, 2026-11-07

A linear-predictor click detector (order 12, block by block, ratio limit 12) on the same 36 generated and 8 procedural files: +0.5 clicks 22/32 and 5/6, +0.1 4/32 and 2/6, +0.03 2/32 and 2/6, clean flags 4/36 and 2/8. That matches the current detector within noise and runs far slower, so it was not kept. A numpy prototype that also searched the attack reached 29/32 at +0.5, so the attack skip may be what limits detection; not tested further. Shorter noise-floor frames (20 ms, 100 ms steady) gave 7/12 and 1/12 at -45 and -55 dB, no better, and more clean flags (24 of 36), so they were not kept either. CLICK and NOISE_FLOOR stay weak, as above.

## Spectral seam, 2026-11-07

`fish-layer/seamcal.py` in the private lab: 29 wind, fire and truck takes. Good: crossfaded loops. Bad: second half low-passed at 800 Hz with RMS matched, an extreme planted change. At limit 1.0: 0 of 29 good flagged, 21 of 29 bad caught; the sample-step SEAM caught 0 of 29. At 0.8: 5 false, 24 caught. Generated and procedural beds only, not heard, no real recordings.

## Tone match

TONE_MISMATCH: any of three bands (under 300 Hz, to 3 kHz, above) differs by more than 6 dB. Calibrated on planted faults only, white noise at 8 kHz: another seed reads under the limit, 9.5 dB of gain and a one-pole dulled copy read over it. No real room tone has been tried, and nobody has listened. TONE_SHORT is a plain 5 s default, from the books' room tone advice (30 s named for exteriors), not a measurement. `tone` ignores frames under -80 dB, because generated takes pad with near-silence.

## Known limits

- `set` finds exact and near-exact copies. It does not catch pitch-shifted copies of one source: six `vary` outputs from one file read a median correlation of 0.27. So a clean `set` does not rule out machine-gunning. Listen.
- SEAM compares against the file's own sample steps, so a noisy bed hides a real jump: a 0.3 jump in a whoosh scored 1.2. Listen to the loop point.
- Crackle, chips and foley contain clicks on purpose: use `--waive CLICK`.
- DC can flag short, low-heavy sounds whose mean is not truly offset.
- Onset counts are estimates.

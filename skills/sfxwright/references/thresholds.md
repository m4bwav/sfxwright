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

## Known limits

- `set` finds exact and near-exact copies. It does not catch pitch-shifted copies of one source: six `vary` outputs from one file read a median correlation of 0.27. So a clean `set` does not rule out machine-gunning. Listen.
- SEAM compares against the file's own sample steps, so a noisy bed hides a real jump: a 0.3 jump in a whoosh scored 1.2. Listen to the loop point.
- Crackle, chips and foley contain clicks on purpose: use `--waive CLICK`.
- DC can flag short, low-heavy sounds whose mean is not truly offset.
- Onset counts are estimates.

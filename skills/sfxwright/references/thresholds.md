# Thresholds

A flag means listen. It is not a verdict, and no flag does not mean a sound is good.

Limits live in `LIMITS` in `sfx_audio.py`. They started as uncalibrated guesses from DSP books. Planted-fault results will be recorded here; until a row appears, treat a limit as uncalibrated.

| Flag | Reading | Limit |
|---|---|---|
| CLIP | run of identical samples at the file's own peak | 4 samples |
| DC | largest channel mean | above -60 dB |
| CUT_HEAD, CUT_TAIL | peak of the first 4 or last 12 samples | above -50, -60 dB |
| LEAD_SILENCE, END_SILENCE | time before -40 dB of peak; after -50 dB | 0.05 s, 0.25 s |
| CLICK | isolated sample step against its neighbours, outside the attack | ratio above 8 |
| NOISE_FLOOR | steady 200 ms floor, 20 dB under the peak | above -60 dB |
| NO_HEADROOM | peak | above -0.1 dB |
| LENGTH | sound length against the brief | off by 25% or 0.05 s |
| SEAM | end-to-start jump over the 99th percentile step | above 5 (mw.py scale when present) |
| NEAR_DUPLICATES | best-lag correlation in a set | above 0.98 |
| LEVEL_SPREAD | RMS range in a set | above 3 dB |
| TOO_EVEN | spread of gaps between onsets | below 0.03 |

## Known limits

- `set` finds exact and near-exact copies. It does not catch pitch-shifted copies of one source: six `vary` outputs from one file read a median correlation of 0.27. So a clean `set` does not rule out machine-gunning. Listen.
- Crackle, chips and foley contain clicks on purpose: use `--waive CLICK`.
- DC can flag short, low-heavy sounds whose mean is not truly offset.
- Onset counts are estimates.

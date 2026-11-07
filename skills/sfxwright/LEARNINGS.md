# Learnings

## 2026-11-06 Length is a maximum
Trigger: a 3 s request to SA3 Medium returned 1.6 s of sound and silence. Hypothesis: always tidy generated takes and judge `sound_s`, not file length.

## 2026-11-06 A floor must be steady
Trigger: NOISE_FLOOR fired on every fading sound. Fix: require 200 ms of frames near the floor, 20 dB under the peak.

## 2026-11-06 One sample cannot prove a cut
Trigger: a planted cut tail landed on a zero crossing and passed. Fix: read a short window at each end.

## 2026-11-06 Spread a calibration sample
Trigger: `--limit 12` took four sounds only and reported noise detection as 0/6. Fix: `--glob "*_01.flac"` across sounds. A pure-Python O(n^2) mean also hid as slowness for 30 minutes: when a job is slow, profile it before waiting.

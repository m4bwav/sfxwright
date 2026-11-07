# Learnings

## 2026-11-06 Length is a maximum
Trigger: a 3 s request to SA3 Medium returned 1.6 s of sound and silence. Hypothesis: always tidy generated takes and judge `sound_s`, not file length.

## 2026-11-06 A floor must be steady
Trigger: NOISE_FLOOR fired on every fading sound. Fix: require 200 ms of frames near the floor, 20 dB under the peak.

## 2026-11-06 One sample cannot prove a cut
Trigger: a planted cut tail landed on a zero crossing and passed. Fix: read a short window at each end.

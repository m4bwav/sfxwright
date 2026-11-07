# Learnings

## 2026-11-06 Length is a maximum
Trigger: a 3 s request to SA3 Medium returned 1.6 s of sound and silence. Hypothesis: always tidy generated takes and judge `sound_s`, not file length.

## 2026-11-06 A floor must be steady
Trigger: NOISE_FLOOR fired on every fading sound. Fix: require 200 ms of frames near the floor, 20 dB under the peak.

## 2026-11-06 One sample cannot prove a cut
Trigger: a planted cut tail landed on a zero crossing and passed. Fix: read a short window at each end.

## 2026-11-06 Spread a calibration sample
Trigger: `--limit 12` took four sounds only and reported noise detection as 0/6. Fix: `--glob "*_01.flac"` across sounds. A pure-Python O(n^2) mean also hid as slowness for 30 minutes: when a job is slow, profile it before waiting.

## 2026-11-07 Compare a listen with chance
Trigger: seeds won 3 of 5 blind picks, which looked like a finding, but seeds were 3 of 5 clips. Fix: state the share of options next to the share of wins.

## 2026-11-07 Replay docs against a real host too
Trigger: the wiki replay reached a live busy host and `gen` crashed on one missed poll, a path the offline tests never hit. Fix: polling tolerates a miss, with a test.

## 2026-11-07 What the model already does without this skill
Trigger: worth A/B baseline. On these cases it declined the lightsaber copy, found the clipped take, repaired a seam without a dip, wrote a creak with a record and refused to ship an unknown licence. It dropped `commercial` from a plan 3 of 3. Hypothesis: the skill's value is in records and long projects, not in one-shot tasks. Token savings to try, none made yet: (1) move the rights list detail to `references/rights.md`, about 100 tokens, the baseline already declines; (2) a one-call layered-variations command, about 10 turns on hit-layers, where the skill spent 35 turns against 13; (3) stop agents reading references for one-shots, by saying which steps a single sound can skip.

## 2026-11-07 Prove a grader on the skill's real output
Trigger: `film-sync` failed 3 of 3 with the skill because the checker took a row's `layers` list for the sound rows. My proof list had two rows with no layers. Fix: shallowest list wins; run a checker on one kept with-arm folder before reading a 0%.

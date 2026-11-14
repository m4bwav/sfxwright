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

## 2026-11-08 `sequence --limp` bunched steps instead of spacing them
Trigger: Lovecraft Zann stair bed. `sequence step_02 step_03 --count 5 --gap 1.45 --jitter 0.12 --limp 0.1 --seed 7` gave events [0.0, 1.413, 1.56, 3.152, 3.295]: every second gap shrank to about 0.15 s, the opposite of "every second gap is this much longer". Without `--limp` (jitter 0.08) the events were even: [0.0, 1.426, 2.928, 4.473, 5.95]. Not yet traced in `sfx.py`; check the limp arithmetic and add a test that the gaps alternate long and short. Also: Mark, 2026-11-07, called the procedural `creak` + `footstep` stair bed "terrible and nothing like creaking", a second listener agreeing with routes.md; SA3 Medium takes replaced it (unheard by the agent). Retire once a test covers limp.

## 2026-11-14 FM bell failed the checks; Karplus-Strong needed a zero-mean preload
Trigger: Musimathics build. An FM bell (carrier 440 Hz, ratio 1.4, index 6 decaying) flagged CLICK 75 and END_SILENCE where `modal material=metal` read ok (click 3.7); index 3 still CLICK 23, 880 Hz END_SILENCE only. Not adopted. Candidate for Mark's ears: FM metal may still beat modal by ear, and the CLICK limit was tuned on hits, not dense inharmonic tones. Also: a noise-filled delay line keeps its DC forever, so after `_finish` removes the mean the tail sat at -54 dB and flagged NOISE_FLOOR; subtracting the preload mean fixed it (floor -63 to -68 dB at 82-660 Hz).

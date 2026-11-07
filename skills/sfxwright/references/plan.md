# Planning a sound list

Ask only what changes the list: medium, platform and memory limit, style, hero sounds, commercial or not, deadline. One event per file.

## From a game

List by category with `event`, `trigger`, `kind`, `spatial`, `priority`, `max_instances`. Mark hero sounds; they earn the budget. For each subcategory ask: would a player notice if this axis went away, is it heard often enough to pay for itself, can a parameter do it instead of a file? `sfx.py plan` prints the three shapes side by side. Tiers for repeated actions: soft, medium, large, over the top, each close and far when distance matters.

## From a film cut

Spot against locked picture: `at_s`, `sync_point_s` (the moment inside the file that lands on the frame) and `sync_class`: `tight` for hits you can see, `loose` for near-sync, `bed` for backgrounds. Spend on what a viewer can see: a bed plus sold hits beats every footstep equal. Set `role`: hard, background, foley, design. Work order when others hold those tracks: dialogue, music, backgrounds, then hard effects. Picture means 48 kHz. Sync limit starts at 1 frame for tight hits, 2 for near-sync; a practitioner figure to test by eye.

## From a description

Write the list anyway, even for three sounds, so the files have a home.

## Question each sound

A lone effect with nothing around it (one car in an otherwise silent street) reads as an effect. Either build the world that makes it ordinary (other cars pass now and then) or cut it. Decide how far the world reaches: next room, building, street, and what each ring adds. Name foreground, middle and background: a bed with a clear foreground voice implies a person who is not there. Spend accuracy where a sound is prominent; a familiar wrong sound can beat an accurate unfamiliar one. Fry (2019), theatre practice and stated as opinion.

## Footsteps

The brief needs character, weight shift, shoe and exact surface. Plan single hits per surface, then a sequence.

## Foley and cloth

One low cloth track following movement; special garments apart. Excess gets cut, so keep it quiet. In a mixed prop layer, metal leads by accident: read each layer's peak.

## Ambience

Build from a quiet bed plus sparse events per location, not one long take. Practitioner advice, not a measurement.

Sources: Viers, Holman, Rose, Ament, Zdanowicz and Bambrick, Fuesslin in Somberg vol. 3; Fry; an r/sounddesign thread on backgrounds.

## Name the excitation

Miranda, *Computer Sound Design*, from instrument synthesis, untested on generated audio. Say what drives the sound before choosing a route, and put it in the prompt or recipe:

- **Impulsive** (hit, pluck): starts at its fullest; the top fades first.
- **Continuous** (bow, blow, motor): starts simple, gains partials, loses them in reverse when the force stops.
- **Iterating** (roll, rattle, ratchet): repeated impulses, so plan the rate and how it varies.

Then ask how pitched or noisy it is. A spectrum that fades the wrong way is a cue to listen, not a verdict.

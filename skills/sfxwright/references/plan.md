# Planning a sound list

Ask only what changes the list: medium, platform and memory limit, style, hero sounds, commercial or not, deadline. One event per file.

## From a game

Give each sound a job before it gets a file: feedback (did my action land), mood, space (where am I, how big), identity (whose sound is this) or pacing (what is about to happen). An object with no job gets no sound; a list that sounds everything turns to clutter. Sounds placed in 3D ship mono: the engine pans and attenuates them, and a stereo file built wide can cancel when summed, so run `check --mono` (on by default for `spatial: 3D`). Before handover, fire each event fast and over and over (kick one crate ten times, spam the button) to find the events that need a `max_instances`, a `priority` or a cooldown. Zdanowicz and Bambrick, *The Game Audio Strategy Guide* (Routledge, 2020, ch. 3 and 8): practitioner advice, book rule, unverified except the mono check.

List by category with `event`, `trigger`, `kind`, `spatial`, `priority`, `max_instances`. Mark hero sounds; they earn the budget. For each subcategory ask: would a player notice if this axis went away, is it heard often enough to pay for itself, can a parameter do it instead of a file? `sfx.py plan` prints the three shapes side by side. Tiers for repeated actions: soft, medium, large, over the top, each close and far when distance matters.

Mark what each event tells the player. A warning (an enemy closing in, a boulder rolling nearer and louder), a confirmation or a direction to look must stay audible over the mix and distinct from its neighbours, and if the game must play muted (phones in public), each needs a visual twin. Say how each event moves: fixed (a cutscene), adaptive (follows game state or a timer, such as birds by day and crickets at night) or interactive (the player sets it off, such as a sword swing). Record a dry source once and let the engine add the room per location instead of a file per room. Name impacts by object and material, such as `sword_wood_impact01`, so missing pairs show. A game played for tens of hours needs more variants of its often-heard sounds than a short one. Collins, *Game Sound* (MIT, 2008, ch. 5 and 7): taken from 2000s practice, so check it against current middleware.

Tune melodic pickups and UI one-shots to the score's key (a root with its fifth under it), and let a burst of pickups climb in steps; a note a semitone or tritone off the key sticks out of the mix. A row of pickups grabbed faster than each one rings needs a `max_instances` or a steal rule. Let `priority` double as the cut order when memory runs short or the game is ported to a low-end phone, and log estimated against actual time per asset so the next estimate improves. Zizza, *Game Audio Fundamentals* (Focal, 2023, ch. 8 and 11): one designer's practice.

## From a film cut

Spot against locked picture: `at_s`, `sync_point_s` (the moment inside the file that lands on the frame) and `sync_class`: `tight` for hits you can see, `loose` for near-sync, `bed` for backgrounds. Spend on what a viewer can see: a bed plus sold hits beats every footstep equal. Set `role`: hard, background, foley, design. Work order when others hold those tracks: dialogue, music, backgrounds, then hard effects. Picture means 48 kHz. Sync limit starts at 1 frame for tight hits, 2 for near-sync; a practitioner figure to test by eye. Late forgives more than early: one frame late passes, two is seen by many, three by most, while one frame early already feels wrong, so round toward late and never pre-shift for the speed of sound. Fixing sync, shift the whole run first, then move only the hits that draw the eye; snapping every step to its frame makes a stiff, kneeless walk. In a busy prop (gun handling, saddle), sync the one moment where eye and ear meet. Under a song or loud score keep only the prominent foley; match its style to the picture (lifelike for realistic animation, sparse and illustrative for a sketchy style). A recurring character can carry a signature sound.

Sound and picture fuse at a sync point almost whatever the sound is, so for a tight hit judge timing and isolation before a literal match: one clear sound per visible action binds, and a louder one binds harder. Choose how much material detail each sound carries (friction, grit, unevenness): more makes the scene tangible, less makes it abstract, and either can be right. A loud event in a real room also changes colour, rings the room and rattles nearby things; a big boom with none of that reads clean and detached. Check the cut by watching it silent, listening without picture, then both, and list what you hear but do not see and see but do not hear. Chion, *Audio-Vision* (2019 ed., ch. 3, 5, 9): theory argued from film examples, untested on generated sound.

## From a description

Write the list anyway, even for three sounds, so the files have a home.

## Question each sound

A lone effect with nothing around it (one car in an otherwise silent street) reads as an effect. Either build the world that makes it ordinary (other cars pass now and then) or cut it. Decide how far the world reaches: next room, building, street, and what each ring adds. Name foreground, middle and background: a bed with a clear foreground voice implies a person who is not there. Spend accuracy where a sound is prominent; a familiar wrong sound can beat an accurate unfamiliar one. Fry (2019), theatre practice and stated as opinion.

## Footsteps

The brief needs character, weight shift, shoe and exact surface. For the player on a budget project, plan 6 to 8 takes per surface; NPCs can share a set per group (book rule, unverified). Plan single hits per surface, then a sequence. Mix footfall kinds in one walk (some heel-toe, some flat, a scuff, a weight shift): all flat or all heel-toe sounds performed. A prop pickup may be heard where life is silent, but keep the scrape short.

## Foley and cloth

One low cloth track following movement; special garments apart. Excess gets cut, so keep it quiet. In a mixed prop layer, metal leads by accident: read each layer's peak.

## Ambience

Build from a quiet bed plus sparse events per location, not one long take. Practitioner advice, not a measurement.

On picture, ambience carries scene grammar (Holman, *Sound for Film and Television*, 3rd ed., p. 162-165): hold a location's ambience steady across a picture cut to say same place, change it at the cut to say new scene, and a deliberate drop at a cut can tell story even where physics would keep the level. Kept low under dialogue, it masks presence jumps between shots. Give ambience the lows and foley the highs so they do not mask each other, and keep quiet and loud effects on separate tracks. To cross a scene change, a prelap (J-cut) brings the next scene's sound in early and adds energy, a postlap (L-cut) carries the old scene over; even a straight cut is a very short crossfade so it does not click.

Keep single placeable elements (one cricket, a distant dog) in files of their own, apart from the bed of the same sound, so the mix can move them separately; a mixer on *Salt* put single crickets on the front channels and the cricket bed on the rest (Yewdall, *Practical Art of Motion Picture Sound*, 4th ed., p. 506).

Sources: Viers, Holman, Rose, Ament (ch. 5, 10, 11), Zdanowicz and Bambrick, Fuesslin in Somberg vol. 3; Fry; an r/sounddesign thread on backgrounds.

## Name the excitation

Miranda, *Computer Sound Design*, from instrument synthesis, untested on generated audio. Say what drives the sound before choosing a route, and put it in the prompt or recipe:

- **Impulsive** (hit, pluck): starts at its fullest; the top fades first.
- **Continuous** (bow, blow, motor): starts simple, gains partials, loses them in reverse when the force stops.
- **Iterating** (roll, rattle, ratchet): repeated impulses, so plan the rate and how it varies.

Then ask how pitched or noisy it is. A spectrum that fades the wrong way is a cue to listen, not a verdict.

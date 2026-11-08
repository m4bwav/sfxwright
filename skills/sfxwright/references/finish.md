# Finishing and engines

Work in WAV or FLAC; encode last. A one-shot is levelled by gain, not compressed. Keep the untouched source and ship the finished copy.

| `--dest` | Peak | Rate | Format |
|---|---|---|---|
| game-sfx, unity | -3 dBFS | 48 kHz | wav |
| game-foley | -12 | 48 kHz | wav |
| game-ambience | -14 | 48 kHz | ogg |
| roblox | -3 | 48 kHz | ogg |
| film | -1 | 48 kHz | wav |
| web | -3 | 44.1 kHz | ogg |
| library | -1 | 96 kHz | wav |

These are file-level peak references from one book's practice (Zdanowicz and Bambrick) with no measurement behind them, not delivery specs. Upsampling adds no quality. Use `--keep-ends` on loops.

Film delivery (Holman, *Sound for Film and Television*, 3rd ed., p. 161, 166): resample 44.1 kHz library files to 48 kHz before placing them on picture; unconverted they play about 8.8 percent sharp. Deliver dialogue, music and effects as separate stems (DM&E); when foreign versions are planned, keep creatures and intelligible crowd lines out of the effects stem, since they must follow the dialogue level, and put mutters in effects.

Loudness specs measure whole mixes: EBU R128 -23 LUFS, -1 dBTP; ATSC A/85 -24 LKFS; Sony ASWG-R001 -24 +/-2 LKFS home, -18 +/-2 portable, over at least 30 minutes. None sets a level for one effect. Short files defeat integrated loudness gating. Balance the project by ear.

## Engines

- **Unity:** ADPCM about 3.5:1 for noisy repeated sounds; Decompress On Load for small sounds, where Vorbis costs about 10x in memory; Audio Random Container for playlists. Check the current manual.
- **Godot:** `AudioStreamRandomizer`: `random_pitch` between 1/value and value, `random_volume_offset_db`.
- **Roblox:** mp3, ogg, wav, flac; under 20 MB and 7 minutes; up to 48 kHz; import limits and moderation apply; you must hold the rights.
- **Unreal:** MetaSounds has procedural footstep templates.
- **FMOD:** multi instruments with shuffle, scatterer, modulators on pitch and volume.
- **Wwise:** random containers with avoid-repeat, per-trigger randomizers.

`doc --kind impl` writes the sheet. `budget` estimates size and finds removable silence and fake stereo.

# sounds.json, schema 1

The contract with other plugins. They read this file and never import each other. Change it only with a schema bump.

```json
{"schema": 1, "project": "x", "use": "game", "commercial": true, "frame_rate": 24, "style": "", "sounds": [
 {"id": "crate_drop", "event": "crate hits floor", "kind": "one-shot", "category": "props/impact", "brief": "...",
  "layers": [{"role": "transient"}, {"role": "body"}], "variations": 6, "length_s": 1.2, "loudness": "", "format": "wav",
  "route": "gen:sa3-small", "status": "rendered",
  "takes": [{"file": "takes/crate_01.flac", "sha256": "...", "picked": false, "heard": null, "processing": [],
             "source": {"type": "generated", "model": "stable_audio_3_small_sfx.safetensors", "licence": "stability-community",
                        "prompt": "...", "seed": 1, "settings": {}, "date": "2026-11-06", "ai_generated": true}}]}]}
```

Required per sound: `id, event, kind, variations, length_s, format, route, status`. `kind`: one-shot, loop, ambience, sequence, stinger, ui. `status`: planned, rendered, picked, finished, rejected.

Optional: `category, brief, layers, loudness, at_s, sync_point_s, sync_class, role, trigger, priority, max_instances, spatial, randomize {pitch, volume, no_repeat}, load`.

A take's `source` is an object, or a list when layers mix sources. `type`: generated, procedural, library, recording, other. Licence names are the keys of `LICENCES` in `sfx.py`.

Each made file also has a sidecar `<file>.sfx.json` holding the same record; edits write a new sidecar carrying every parent's source and the processing steps. `register` copies it into the list with a hash, and `ship` blocks when the file no longer matches.

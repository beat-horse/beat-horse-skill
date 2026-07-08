# prompting and lyrics

Load this when an agent is writing or improving Beat Horse prompts.

## General prompt shape

Use concise, concrete music language:

- Genre and subgenre: `rap trap club`, `melodic techno`, `synthwave`.
- Energy and tempo feel: `high-energy`, `half-time groove`, `driving`.
- Instruments and mix: `808 bass`, `tight drums`, `wide analog pads`, `clean vocal mix`.
- Vocal intent: `no vocals`, `female lead vocal`, `spoken adlibs`, `hook-focused`.
- Avoid copying protected melodies or lyrics from references.

Good prompts describe the desired result, not UI instructions.

## Lyrics

- Use lyrics for `text2music`, `cover`, and `complete` when vocals matter.
- Structure tags such as `[Verse]`, `[Chorus]`, `[Bridge]`, `[Intro]`, `[Outro]`, and `[Instrumental]` are useful.
- Set `vocal_language` when the language matters; leave it unset or auto only when language can be inferred.
- For cover jobs, providing lyrics often improves vocal alignment compared with source audio plus a vague prompt.

## Task notes

- `text2music`: describe the full target song and include duration.
- `cover`: describe how the source should be transformed. Include lyrics if vocals should remain intelligible.
- `repaint`: describe only the replacement region and keep surrounding continuity in mind.
- `complete`: describe the source and the desired continuation. Use exactly one of `completion_duration` or target `audio_duration`.
- `extract`: use a valid `track_name`; prompt and lyrics are not the main control surface.
- `lego`: describe the new layer to add and use a valid `track_name`.

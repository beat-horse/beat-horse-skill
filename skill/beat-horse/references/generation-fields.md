# generation request fields

MCP `estimate_generation` exposes exactly the API `GenerationRequest` fields. `create_generation_job` exposes the same fields plus `idempotency_key` and `client_request_id`.

## Core

- `task_type`: one of `text2music`, `cover`, `repaint`, `extract`, `lego`, `complete`.
- `model_id`: choose from live `get_capabilities`.
- `prompt`: up to 4000 chars.
- `lyrics`: up to 20000 chars.
- `audio_duration`: target duration in seconds for tasks that accept explicit duration.
- `completion_duration`: extension duration for `complete` when not using target `audio_duration`.
- `output_format`: `mp3`, `wav`, or `flac`.

## Audio assets

- `source_audio_asset_id`: required for `cover`, `repaint`, `extract`, `lego`, `complete`.
- `reference_audio_asset_id`: optional where capabilities allow it.

## Music hints

- `bpm`
- `key_scale`
- `time_signature`
- `vocal_language`
- `global_caption`

## Thinking and LM

- `thinking`
- `optimize_prompt`
- `optimize_mode`
- `lm_temperature`
- `lm_top_k`
- `lm_top_p`
- `lm_cfg_scale`
- `lm_negative_prompt`
- `use_cot_metas`
- `use_cot_caption`
- `use_cot_language`

Only send these when `get_capabilities` says the selected task/model supports the mode.

## Cover and repaint

- `audio_cover_strength`
- `cover_noise_strength`
- `repainting_start`
- `repainting_end`
- `repaint_mode`: `conservative`, `balanced`, or `aggressive`.
- `repaint_strength`

## Track targeting

- `track_name`: required for `extract` and `lego`.
- `track_classes`: required for `complete`.

## DiT/inference

- `inference_steps`: default is model-specific; leave unset unless the user asks.
- `guidance_scale`
- `shift`
- `infer_method`: `ode` or `sde`.
- `cfg_interval_start`
- `cfg_interval_end`
- `seed`
- `use_random_seed`
- `batch_size`

Use `xl-turbo` with 8 steps by default. Use `xl-base` and `xl-sft` with 50 steps by default.

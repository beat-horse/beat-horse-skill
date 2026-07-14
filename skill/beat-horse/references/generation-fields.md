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
- `client_request_id`: MCP-only create parameter for stable caller identity. It is not part of REST `GenerationRequest`.
- `idempotency_key`: MCP-only create parameter. REST uses the `Idempotency-Key` header.

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

## Render settings

- `inference_steps`: default is model-specific; leave unset unless the user asks.
- `guidance_scale`
- `shift`
- `infer_method`: `ode` or `sde`.
- `cfg_interval_start`
- `cfg_interval_end`
- `seed`
- `use_random_seed`
- `batch_size`

Use `pulse` with 8 steps by default. Use `studio` and `master` with 50 steps by default.

## REST fallback script

`scripts/beat_horse.py` exposes the current common generation fields as CLI flags. Use `--payload-json` when an exact raw request is needed.

For REST creates, pass `--idempotency-key`. If only `--client-request-id` is provided, the script uses it as the REST `Idempotency-Key` header because the public REST body forbids extra fields.

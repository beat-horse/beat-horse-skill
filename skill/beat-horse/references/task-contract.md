# beat.horse task contract

Load this when choosing task inputs, model quality, Thinking, or prompt optimize settings.

Always call MCP `get_capabilities` first. This file describes the public contract; the live capability response decides which models are currently routable.

## Model mapping

For `text2music`, `cover`, and `repaint`:

| Mode | Public model ID |
|---|---|
| Fast / Pulse | `pulse` |
| Normal / Studio | `studio` |
| Best / Master | `master` |

For `extract`, `lego`, and `complete`, use `studio` when live.

Default inference steps:

| Model | Default steps |
|---|---:|
| `pulse` | 8 |
| `studio` | 50 |
| `master` | 50 |

## Tasks

| Task | Required fields | Important optional fields |
|---|---|---|
| `text2music` | `task_type`, `model_id`, `audio_duration`, plus `prompt` or `lyrics` | `reference_audio_asset_id`, `global_caption`, `thinking`, `seed`, `batch_size`, `output_format` |
| `cover` | `task_type`, `model_id`, `source_audio_asset_id`, `prompt` | `lyrics`, `reference_audio_asset_id`, `audio_cover_strength`, `cover_noise_strength`, experimental `optimize_prompt`, `seed`, `output_format` |
| `repaint` | `task_type`, `model_id`, `source_audio_asset_id`, `prompt`, `repainting_start`, `repainting_end` | `reference_audio_asset_id`, `repaint_mode`, `repaint_strength`, experimental `optimize_prompt`, `seed`, `output_format` |
| `extract` | `task_type`, `model_id`, `source_audio_asset_id`, `track_name` | `seed`, `output_format` |
| `lego` | `task_type`, `model_id`, `source_audio_asset_id`, `track_name`, `prompt`, `repainting_start`, `repainting_end` | `global_caption`, `seed`, `output_format` |
| `complete` | `task_type`, `model_id`, `source_audio_asset_id`, `prompt`, `track_classes`, exactly one of `completion_duration` or target `audio_duration` | `lyrics`, `reference_audio_asset_id`, `global_caption`, `seed`, `output_format` |

## Thinking and optimize

- `thinking=true` is native LM planning. Public v1 supports it for `text2music` when a compatible LM satellite is routable.
- `lego` and `complete` are benchmark-gated for Thinking; only use when `get_capabilities` exposes them as public.
- `cover` and `repaint` do not use native Thinking. Use `optimize_prompt=true` only when capabilities expose experimental prompt optimize.
- `extract` rejects Thinking and prompt optimize.
- Always run `estimate_generation` before creating a job with Thinking, optimize, or LM tuning parameters.

## Field restrictions

- Do not send `audio_duration` to `cover`, `repaint`, `extract`, or `lego`.
- Do not send `track_name` outside `extract` and `lego`.
- Do not send `track_classes` outside `complete`.
- Do not send `completion_duration` outside `complete`.
- Do not send cover controls outside `cover`, repaint controls outside `repaint`, or interval fields outside `repaint`/`lego`.

## Track names

Valid track names/classes include:

`woodwinds`, `brass`, `fx`, `synth`, `strings`, `percussion`, `keyboard`, `guitar`, `bass`, `drums`, `backing_vocals`, `vocals`.

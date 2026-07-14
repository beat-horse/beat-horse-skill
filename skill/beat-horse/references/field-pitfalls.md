# field pitfalls

Load this before building or replaying generation payloads.

## Task-specific fields

- `track_name` is only for `extract` and `lego`. Do not send it to `text2music`, `cover`, `repaint`, or `complete`.
- `track_classes` is only for `complete`. Do not send it to `extract` or `lego`.
- `lyrics` is only for `text2music`, `cover`, and `complete`.
- `audio_duration` is only for `text2music` and target-duration `complete`. Do not send it to `cover`, `repaint`, `extract`, or `lego`.
- `completion_duration` is only for `complete`.
- `repainting_start` and `repainting_end` are only for `repaint` and `lego`.
- `audio_cover_strength` and `cover_noise_strength` are only for `cover`.
- `repaint_mode` and `repaint_strength` are only for `repaint`.
- `global_caption` is only for tasks where `get_capabilities` exposes it.

## Source and reference assets

- `source_audio_asset_id` must point to an owned asset uploaded with kind `source_audio`.
- `reference_audio_asset_id` must point to an owned asset uploaded with kind `reference_audio`.
- If the same local file must be used as both source and reference, upload it twice with the two different kinds.
- YouTube, web, or local file paths are not asset IDs. Upload the audio first.
- Empirical cover guardrail: very short source clips produce poor or rejected cover jobs. Prefer source audio at least 10-12 seconds long.

## Thinking and optimize

- Always estimate first when using `thinking`, `optimize_prompt`, or LM parameters.
- If estimate rejects the mode, do not create the paid job.
- `thinking=true` means native LM planning only where capabilities allow it.
- `cover` and `repaint` do not use native Thinking. Use `optimize_prompt=true` only when capabilities expose the experimental prompt pre-pass.
- `extract` rejects Thinking and prompt optimize.

## Pulse render fields

- Do not blindly replay old CFG/guidance fields into `pulse` jobs.
- `pulse` should normally use 8 inference steps.
- Leave `guidance_scale`, `cfg_interval_start`, and `cfg_interval_end` unset unless current capabilities or API docs explicitly allow them for the selected model.
- `studio` and `master` normally use 50 inference steps.

## Retry safety

- If create returns a `job_id`, the paid job exists. Poll that job.
- If polling times out, call `get_generation_job`, `get_generation_status`, or `wait_for_generation_job` again.
- Retry create only when no job was created or the API confirms a transient create failure.
- Reusing the same `idempotency_key` with the same request is safe; using the same key with a different request returns an idempotency conflict.

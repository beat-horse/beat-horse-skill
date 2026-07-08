---
name: beat-horse
description: Generate, edit, inspect, and download AI music with beat.horse over MCP or REST. Use when the user wants an agent to create tracks, covers, repaints, completions/extensions, stems, Lego/add-layer jobs, upload source or reference audio, check credits/capabilities/jobs, or authenticate with a beat.horse API key.
---

# beat.horse

Use beat.horse as one system: the REST API is the source of truth, and MCP tools are thin wrappers over the same API validation, credits, assets, and jobs.

Prefer MCP tools when connected. Use the bundled REST script only when MCP tools are unavailable or the user explicitly asks for direct API examples.

## Setup

Set an API key with `mcp:access` plus the scopes needed by the workflow:

```bash
export BEAT_HORSE_API_KEY="bh_live_..."
export BEAT_HORSE_API_URL="https://api.beat.horse"
```

Remote MCP endpoint:

```text
https://mcp.beat.horse/mcp
Authorization: Bearer $BEAT_HORSE_API_KEY
```

## Rules

- Always call `get_capabilities` before selecting model/task/thinking/optimize settings.
- Work is async: estimate or create a generation job, then poll `get_generation_status` or call `wait_for_generation_job`, then fetch output download URLs.
- Use a fresh `idempotency_key` for `create_generation_job` retries.
- For source audio tasks, upload audio first and use the returned `asset.id` as `source_audio_asset_id` or `reference_audio_asset_id`.
- Do not invent endpoint aliases. Generation creation is `POST /v1/generations`; job detail is `/v1/generations/{job_id}`.
- Treat `thinking` as native LM planning only where capabilities allow it. Treat `optimize_prompt` for cover/repaint as an experimental prompt pre-pass, not native ACE Thinking.

## Common Workflows

Text-to-music:

1. `get_capabilities`
2. Select a live model: fast usually `xl-turbo`, normal `xl-base`, best `xl-sft`
3. `estimate_generation(task_type="text2music", model_id=..., prompt=..., audio_duration=...)`
4. `create_generation_job(..., idempotency_key=uuid)`
5. `wait_for_generation_job(job_id)`
6. `get_asset_download_url(asset_id)`

Source-audio jobs:

1. Upload source audio with `upload_audio_asset`, or use signed upload flow
2. `get_capabilities`
3. Create one of `cover`, `repaint`, `complete`, `extract`, or `lego`
4. Include required fields from the task contract
5. Wait and download outputs

## References

Load these only when needed:

- `references/task-contract.md` for task/model rules.
- `references/generation-fields.md` for request fields.
- `references/upload-flow.md` for asset upload choices.
- `references/scopes.md` for API key scopes.
- `references/errors.md` for recovery steps.

## REST Fallback

Use `scripts/beat_horse.py` when MCP tools are not available:

```bash
python3 scripts/beat_horse.py capabilities
python3 scripts/beat_horse.py create --task-type text2music --model-id xl-turbo --prompt "clean club rap beat" --audio-duration 30 --wait
```

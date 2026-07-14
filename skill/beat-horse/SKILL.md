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

- Use MCP tools first when connected. Use the REST fallback only when MCP is unavailable or the user asks for direct API calls.
- Treat generation as paid work. Estimate before creating a generation job unless the user explicitly asks to skip the estimate.
- Do not create duplicate paid jobs after a timeout. If `create_generation_job` returned a `job_id`, keep polling that job instead of creating another one.
- Upload source/reference audio first and use the returned `asset.id` as `source_audio_asset_id` or `reference_audio_asset_id`.
- Do not invent endpoint aliases. Generation creation is `POST /v1/generations`; job detail is `/v1/generations/{job_id}`.
- Treat `thinking` as native planning only where capabilities allow it. Treat `optimize_prompt` for cover/repaint as an experimental prompt pre-pass, not native Thinking.

## MCP Tool Map

| Need | Tool |
|---|---|
| Account, scopes, credits | `get_account`, `get_credit_balance` |
| Usage and billing reads | `get_usage_summary`, `list_credit_ledger`, `get_api_key_usage`, `list_credit_packages`, `list_billing_purchases` |
| Models and routing | `list_models`, `get_capabilities`, `get_worker_health` |
| Assets | `upload_audio_asset`, `create_asset_upload`, `complete_asset_upload`, `list_assets`, `get_asset`, `get_asset_download_url`, `delete_asset` |
| Generation jobs | `estimate_generation`, `create_generation_job`, `get_generation_status`, `get_generation_job`, `wait_for_generation_job`, `cancel_generation_job`, `list_generation_jobs` |

## Paid Work Preflight

Before creating a paid generation:

1. `get_account` to confirm the account is active and scopes allow the workflow.
2. `get_credit_balance` to confirm enough available credits.
3. `list_models(task_type=...)` to choose a live model for the task.
4. `get_capabilities` to validate fields, model, Thinking, optimize, and duration rules.
5. `get_worker_health` when capacity matters or after `no_routable_worker` / capacity errors.
6. `estimate_generation` with the exact payload that will be created.

## Common Workflows

Text-to-music:

1. Run the paid work preflight.
2. Select a live model: `pulse` for fast, `studio` for normal, or `master` for best quality.
3. `create_generation_job(..., idempotency_key=uuid)`.
4. `wait_for_generation_job(job_id)`.
5. `get_generation_job(job_id)` and inspect `outputs`.
6. `get_asset_download_url(asset_id)` for each deliverable output.

Source-audio jobs:

1. Upload source audio with `upload_audio_asset`, or use signed upload flow
2. Run the paid work preflight
3. Create one of `cover`, `repaint`, `complete`, `extract`, or `lego`
4. Include required fields from the task contract
5. Wait and download outputs

Delivery verification:

- Never report a generation as deliverable until at least one output asset exists.
- When local shell access is available, download the output and verify duration/streams with `ffprobe`.
- If a job succeeded but has no output asset IDs, treat it as a delivery failure and inspect phases/errors.

## References

Load these only when needed:

- `references/task-contract.md` for task/model rules.
- `references/generation-fields.md` for request fields.
- `references/field-pitfalls.md` for task-specific fields and model pitfalls.
- `references/upload-flow.md` for asset upload choices.
- `references/output-verification.md` for delivery verification.
- `references/prompting.md` for prompt and lyrics guidance.
- `references/scopes.md` for API key scopes.
- `references/errors.md` for recovery steps.

## REST Fallback

Use `scripts/beat_horse.py` when MCP tools are not available:

```bash
python3 scripts/beat_horse.py capabilities
python3 scripts/beat_horse.py models --task-type text2music --enabled
python3 scripts/beat_horse.py worker-health --require-worker dit:pulse:text2music
python3 scripts/beat_horse.py usage
python3 scripts/beat_horse.py ledger
python3 scripts/beat_horse.py create --task-type text2music --model-id pulse --prompt "clean club rap beat" --audio-duration 30 --wait
python3 scripts/beat_horse.py download <asset_id> -o output.mp3
```

The REST script exposes common generation fields. Use `--payload-json` for exact advanced payloads or fields added after this skill version.

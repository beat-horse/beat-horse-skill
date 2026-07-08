# AGENTS.md - beat.horse

Guidance for agents using beat.horse.

## Connect

- MCP: `https://mcp.beat.horse/mcp`
- REST: `https://api.beat.horse`
- Auth: `Authorization: Bearer $BEAT_HORSE_API_KEY`
- Skill: `skill/beat-horse/SKILL.md`
- REST fallback script: `skill/beat-horse/scripts/beat_horse.py`

## Rules

- Use MCP tools first when connected.
- Before paid generation, call `get_account`, `get_credit_balance`, `list_models`, `get_capabilities`, and `estimate_generation`.
- Work is async: create a job, poll status or wait, inspect full job detail, then fetch output download URLs.
- Send an `idempotency_key` on generation create.
- If create returned a `job_id`, do not create a duplicate paid job after a timeout; keep polling the original job.
- Upload source/reference audio before sending `source_audio_asset_id` or `reference_audio_asset_id`.
- Use `source_audio` assets for `source_audio_asset_id` and `reference_audio` assets for `reference_audio_asset_id`.
- Do not add alias endpoints; use canonical `/v1/generations` and `/v1/assets` routes.
- Verify deliverable outputs with `get_generation_job`, `get_asset_download_url`, and `ffprobe` when local shell access exists.
- REST fallback includes read helpers plus `cancel`, `download`, and `delete-asset`; prefer MCP tools when available.

## Scopes

Every MCP key needs `mcp:access`. Generation with source audio usually also needs:

- `generation:create`
- `generation:read`
- `assets:read`
- `assets:write`
- `models:read`
- `credits:read`

See `skill/beat-horse/references/scopes.md` for details.

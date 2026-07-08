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
- Call `get_capabilities` before choosing task/model/thinking/optimize settings.
- Work is async: create a job, poll status or wait, then fetch output download URLs.
- Send a fresh `idempotency_key` on generation create.
- Upload source/reference audio before sending `source_audio_asset_id` or `reference_audio_asset_id`.
- Do not add alias endpoints; use canonical `/v1/generations` and `/v1/assets` routes.

## Scopes

Every MCP key needs `mcp:access`. Generation with source audio usually also needs:

- `generation:create`
- `generation:read`
- `assets:read`
- `assets:write`
- `models:read`
- `credits:read`

See `skill/beat-horse/references/scopes.md` for details.

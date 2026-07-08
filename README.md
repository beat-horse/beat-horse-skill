# beat.horse agent skill

Portable agent instructions for using beat.horse through the same API and MCP surface as the web dashboard.

## Connect

Create a beat.horse API key with `mcp:access` and the workflow scopes you need, then connect a remote MCP client to:

```text
https://mcp.beat.horse/mcp
Authorization: Bearer <your beat.horse API key>
```

Generic example:

```bash
export BEAT_HORSE_API_KEY="bh_live_..."
```

Clone the public agent skill:

```bash
git clone https://github.com/beat-horse/beat-horse-skill.git
```

The skill lives at:

```text
skill/beat-horse
```

## What agents can do

- Read capabilities, models, credits, usage, billing reads, and worker health.
- Upload source/reference audio assets.
- Estimate and create generation jobs.
- Generate text-to-music, cover, repaint, extract, lego/add-layer, and complete/extend jobs.
- Poll job status and fetch output download URLs.

## Safety defaults

- Use MCP first and call `get_capabilities` before choosing task/model/Thinking settings.
- Estimate before paid generation unless the user explicitly skips it.
- If create returns a `job_id`, keep polling that job after a timeout instead of creating a duplicate paid job.
- Download and verify generated output with `ffprobe` when local shell access is available.

## REST fallback

When MCP is unavailable:

```bash
python3 skill/beat-horse/scripts/beat_horse.py capabilities
python3 skill/beat-horse/scripts/beat_horse.py models --task-type text2music --enabled
python3 skill/beat-horse/scripts/beat_horse.py worker-health --require-worker dit:xl-turbo:text2music
python3 skill/beat-horse/scripts/beat_horse.py usage
python3 skill/beat-horse/scripts/beat_horse.py ledger
python3 skill/beat-horse/scripts/beat_horse.py create \
  --task-type text2music \
  --model-id xl-turbo \
  --prompt "clean club rap beat" \
  --audio-duration 30 \
  --wait
python3 skill/beat-horse/scripts/beat_horse.py download <asset_id> -o output.mp3
```

The REST script accepts either a raw API key or a `Bearer ...` value in `BEAT_HORSE_API_KEY`. Use `--payload-json` for exact advanced payloads.

## Source of truth

The REST API owns auth, scopes, validation, credits, assets, and job state. MCP tools are thin wrappers over that API. The skill is a playbook for agents, not a second implementation.

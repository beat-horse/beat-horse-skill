# asset upload flow

Use assets for source audio, reference audio, and output downloads.

## MCP direct upload

For small files, call:

```text
upload_audio_asset(audio_base64, filename, mime_type, kind)
```

Common `kind` values:

- `source_audio`
- `reference_audio`

The returned `asset.id` becomes `source_audio_asset_id` or `reference_audio_asset_id`.

Asset kind matters:

- Use `source_audio` for `source_audio_asset_id`.
- Use `reference_audio` for `reference_audio_asset_id`.
- If the same local file must be both source and reference, upload it twice, once with each kind.
- Do not pass web URLs, local paths, or YouTube URLs as asset IDs.

## Signed upload

For larger files or REST fallback:

1. `create_asset_upload(kind, filename, mime_type, size_bytes)`
2. PUT the bytes to the returned `upload.url` using returned method/headers.
3. `complete_asset_upload(asset_id)`
4. Use the completed `asset.id` in generation requests.

## Downloading results

After `wait_for_generation_job`, inspect `outputs`. For each succeeded output with `asset_id`, call:

```text
get_asset_download_url(asset_id)
```

Do not guess file extensions. Use the asset metadata, download URL, or output format from the generation request.

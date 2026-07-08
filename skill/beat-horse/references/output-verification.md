# output verification

Load this when delivering generated audio or diagnosing succeeded jobs with missing outputs.

## Delivery workflow

1. Wait for a terminal job with `wait_for_generation_job`.
2. Fetch full detail with `get_generation_job`.
3. Confirm at least one output has an `asset_id`.
4. Fetch each output URL with `get_asset_download_url`.
5. If local shell access is available, download the file and run `ffprobe`.

Example:

```bash
curl -L "$DOWNLOAD_URL" -o output.mp3
ffprobe -v error -show_entries format=duration,bit_rate -show_streams -of json output.mp3
```

Report the job as deliverable only after an output asset exists. If local verification is not possible, say that the asset URL exists but was not locally verified.

## Missing output assets

If a job status is `succeeded` but no output asset IDs are present:

- Treat it as a delivery failure, not a completed delivery.
- Inspect `job.error_code`, `job.error_message`, phases, and request/trace IDs.
- Do not create a replacement paid job unless the user asks or the API confirms the previous job is not billable/deliverable.

## Format handling

- Respect `output_format` from the request and asset metadata.
- Do not assume outputs are `.wav`; generated outputs may be `mp3`, `wav`, or `flac`.
- When making a review copy from a master WAV, prefer MP3 320 kbps for sharing and keep the original asset ID in notes.

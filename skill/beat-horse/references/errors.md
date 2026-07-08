# error handling

beat.horse returns structured errors with `code`, `message`, optional `details`, and sometimes `request_id` / `trace_id`.

## Common errors

| Error | Meaning | Recovery |
|---|---|---|
| `authentication_required` | Missing bearer key | Ask for or set `BEAT_HORSE_API_KEY` |
| `invalid_api_key` | Key is wrong/revoked | Create a new key |
| `insufficient_scope` | Key lacks a required scope | Add the scope named in the message |
| `asset_invalid` | Asset id is not visible or does not exist | Upload the asset first or use an owned asset |
| `insufficient_credits` | Account lacks available credits | Stop and tell the user |
| `validation_error` | Request fields conflict or are missing | Read `details`, then fix the payload |
| `no_routable_worker` | No worker/satellite can run the selected task/model | Call `get_capabilities`, choose a live model, or retry later |
| `idempotency_conflict` | Same idempotency key was reused with a different request body | Keep the original payload/key pair or create a new key for a genuinely new job |

## Async job failures

If a job reaches `failed`, call `get_generation_job` and report:

- `job.id`
- `job.status`
- `job.error_code`
- `job.error_message`
- failed phase from `phases`
- `request_id` / `trace_id` if present

Do not retry blindly if the payload is invalid or credits are insufficient. Retry with a new `idempotency_key` only for transient infrastructure failures.

## Timeout safety

If `create_generation_job` returned a `job_id`, the job exists and may be billable. Do not create a second job just because polling or local waiting timed out.

Continue with:

1. `get_generation_status(job_id)`
2. `get_generation_job(job_id)`
3. `wait_for_generation_job(job_id, timeout_seconds=...)`

Retry create only when no job was created or the API confirms the create failed before reservation.

## Output delivery failures

If a terminal job has no output asset IDs:

- Inspect full job detail, phases, and error fields.
- Capture `request_id` / `trace_id` if present.
- Treat it as not deliverable until an output asset is available or support/admin confirms the failure state.

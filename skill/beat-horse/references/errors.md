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

## Async job failures

If a job reaches `failed`, call `get_generation_job` and report:

- `job.id`
- `job.status`
- `job.error_code`
- `job.error_message`
- failed phase from `phases`
- `request_id` / `trace_id` if present

Do not retry blindly if the payload is invalid or credits are insufficient. Retry with a new `idempotency_key` only for transient infrastructure failures.

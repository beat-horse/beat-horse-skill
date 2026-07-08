#!/usr/bin/env python3
"""beat.horse REST fallback client.

Examples:
  export BEAT_HORSE_API_KEY=bh_live_...
  python3 beat_horse.py capabilities
  python3 beat_horse.py create --task-type text2music --model-id xl-turbo \
    --prompt "clean club rap beat" --audio-duration 30 --wait
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = os.environ.get("BEAT_HORSE_API_URL", "https://api.beat.horse").rstrip("/")
KEY = os.environ.get("BEAT_HORSE_API_KEY")
TERMINAL_STATUSES = {
    "succeeded",
    "partial_success",
    "failed",
    "cancelled",
    "canceled",
    "expired",
}


def auth_header() -> str:
    key = (KEY or "").strip()
    if not key:
        raise SystemExit("Set BEAT_HORSE_API_KEY.")
    if not key.lower().startswith("bearer "):
        key = "Bearer " + key
    return key


def request_json(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    url = API + path
    if params:
        clean_params = {
            key: value
            for key, value in params.items()
            if value is not None and value != ""
        }
        if clean_params:
            url += "?" + urlencode(clean_params, doseq=True)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req_headers = {
        "Authorization": auth_header(),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if headers:
        req_headers.update(headers)
    req = Request(url, data=data, headers=req_headers, method=method)
    try:
        with urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {detail[:1200]}") from exc
    except URLError as exc:
        raise SystemExit(f"Request failed: {exc}") from exc


def unwrap_data(payload: dict[str, Any]) -> Any:
    return payload.get("data", payload)


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def generation_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.payload_json:
        try:
            payload = json.loads(args.payload_json)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"--payload-json is not valid JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise SystemExit("--payload-json must be a JSON object.")
        return payload
    payload: dict[str, Any] = {
        "task_type": args.task_type,
        "model_id": args.model_id,
        "prompt": args.prompt,
        "lyrics": args.lyrics,
        "audio_duration": args.audio_duration,
        "bpm": args.bpm,
        "key_scale": args.key_scale,
        "time_signature": args.time_signature,
        "vocal_language": args.vocal_language,
        "completion_duration": args.completion_duration,
        "source_audio_asset_id": args.source_audio_asset_id,
        "reference_audio_asset_id": args.reference_audio_asset_id,
        "track_name": args.track_name,
        "track_classes": args.track_classes,
        "repainting_start": args.repainting_start,
        "repainting_end": args.repainting_end,
        "repaint_mode": args.repaint_mode,
        "repaint_strength": args.repaint_strength,
        "audio_cover_strength": args.audio_cover_strength,
        "cover_noise_strength": args.cover_noise_strength,
        "thinking": args.thinking,
        "optimize_prompt": args.optimize_prompt,
        "optimize_mode": args.optimize_mode,
        "lm_temperature": args.lm_temperature,
        "lm_top_k": args.lm_top_k,
        "lm_top_p": args.lm_top_p,
        "lm_cfg_scale": args.lm_cfg_scale,
        "lm_negative_prompt": args.lm_negative_prompt,
        "use_cot_metas": args.use_cot_metas,
        "use_cot_caption": args.use_cot_caption,
        "use_cot_language": args.use_cot_language,
        "global_caption": args.global_caption,
        "inference_steps": args.inference_steps,
        "guidance_scale": args.guidance_scale,
        "shift": args.shift,
        "infer_method": args.infer_method,
        "cfg_interval_start": args.cfg_interval_start,
        "cfg_interval_end": args.cfg_interval_end,
        "seed": args.seed,
        "use_random_seed": args.use_random_seed,
        "batch_size": args.batch_size,
        "output_format": args.output_format,
    }
    return {key: value for key, value in payload.items() if value is not None}


def add_generation_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--payload-json", help="Raw GenerationRequest JSON object.")
    parser.add_argument("--task-type", default="text2music")
    parser.add_argument("--model-id", default="xl-turbo")
    parser.add_argument("--prompt")
    parser.add_argument("--lyrics")
    parser.add_argument("--audio-duration", type=int)
    parser.add_argument("--bpm", type=int)
    parser.add_argument("--key-scale")
    parser.add_argument("--time-signature")
    parser.add_argument("--vocal-language")
    parser.add_argument("--completion-duration", type=int)
    parser.add_argument("--source-audio-asset-id")
    parser.add_argument("--reference-audio-asset-id")
    parser.add_argument("--track-name")
    parser.add_argument("--track-classes", nargs="*")
    parser.add_argument("--repainting-start", type=float)
    parser.add_argument("--repainting-end", type=float)
    parser.add_argument("--repaint-mode", choices=["conservative", "balanced", "aggressive"])
    parser.add_argument("--repaint-strength", type=float)
    parser.add_argument("--audio-cover-strength", type=float)
    parser.add_argument("--cover-noise-strength", type=float)
    parser.add_argument("--thinking", action="store_true")
    parser.add_argument("--optimize-prompt", action="store_true")
    parser.add_argument("--optimize-mode")
    parser.add_argument("--lm-temperature", type=float)
    parser.add_argument("--lm-top-k", type=int)
    parser.add_argument("--lm-top-p", type=float)
    parser.add_argument("--lm-cfg-scale", type=float)
    parser.add_argument("--lm-negative-prompt")
    parser.add_argument("--use-cot-metas", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--use-cot-caption", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--use-cot-language", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--global-caption")
    parser.add_argument("--inference-steps", type=int)
    parser.add_argument("--guidance-scale", type=float)
    parser.add_argument("--shift", type=float)
    parser.add_argument("--infer-method", choices=["ode", "sde"])
    parser.add_argument("--cfg-interval-start", type=float)
    parser.add_argument("--cfg-interval-end", type=float)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--use-random-seed", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--output-format", choices=["mp3", "wav", "flac"], default="mp3")


def wait_for_job(job_id: str, *, timeout: int, poll: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_payload: dict[str, Any] | None = None
    last_status = "unknown"
    while True:
        status_payload = request_json("GET", f"/v1/generations/{job_id}/status")
        last_payload = status_payload
        status_data = unwrap_data(status_payload)
        job = status_data.get("job", {}) if isinstance(status_data, dict) else {}
        status = str(job.get("status") or "unknown")
        last_status = status
        if status in TERMINAL_STATUSES:
            return request_json("GET", f"/v1/generations/{job_id}")
        if time.time() >= deadline:
            return {
                "timed_out": True,
                "job_id": job_id,
                "last_status": last_status,
                "next_step": (
                    "Poll this same job_id with status/get/wait; do not create a "
                    "duplicate paid job unless the API confirms create failed."
                ),
                "last_response": last_payload,
            }
        time.sleep(poll)


def upload_file(path: Path, *, kind: str, mime_type: str | None) -> dict[str, Any]:
    content = path.read_bytes()
    resolved_mime = mime_type or mimetypes.guess_type(path.name)[0] or "audio/mpeg"
    upload_payload = request_json(
        "POST",
        "/v1/assets/upload-url",
        body={
            "kind": kind,
            "filename": path.name,
            "mime_type": resolved_mime,
            "size_bytes": len(content),
        },
    )
    upload_data = unwrap_data(upload_payload)
    if not isinstance(upload_data, dict):
        raise SystemExit("Unexpected upload-url response.")
    upload = upload_data.get("upload", {})
    asset = upload_data.get("asset", {})
    if not isinstance(upload, dict) or not isinstance(asset, dict):
        raise SystemExit("Upload response did not include upload and asset objects.")
    upload_url = str(upload.get("url") or "")
    if not upload_url:
        raise SystemExit("Upload response did not include upload.url.")
    upload_method = str(upload.get("method") or "PUT")
    upload_headers = {
        str(key): str(value)
        for key, value in (upload.get("headers") or {}).items()
    }
    try:
        upload_req = Request(
            upload_url,
            data=content,
            headers=upload_headers,
            method=upload_method,
        )
        with urlopen(upload_req, timeout=120) as resp:
            if resp.status >= 400:
                raise SystemExit(f"Asset upload failed with HTTP {resp.status}.")
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:600]
        raise SystemExit(f"Asset upload failed with HTTP {exc.code}: {detail}") from exc
    asset_id = str(asset.get("id") or "")
    if not asset_id:
        raise SystemExit("Upload response did not include asset.id.")
    return request_json("POST", f"/v1/assets/{asset_id}/complete", body={"uploaded": True})


def download_asset(asset_id: str, output: Path | None) -> dict[str, Any]:
    download_payload = request_json("GET", f"/v1/assets/{asset_id}/download-url")
    download_data = unwrap_data(download_payload)
    if not isinstance(download_data, dict):
        raise SystemExit("Download URL response was not an object.")
    url = str(download_data.get("url") or "")
    if not url:
        raise SystemExit("Download URL response did not include data.url.")
    output_path = output or Path(asset_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(url, timeout=300) as resp:
            content = resp.read()
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:600]
        raise SystemExit(f"Asset download failed with HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"Asset download failed: {exc}") from exc
    output_path.write_bytes(content)
    return {
        "asset_id": asset_id,
        "output_path": str(output_path),
        "bytes": len(content),
        "expires_at": download_data.get("expires_at"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="beat.horse REST fallback client")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("capabilities")
    sub.add_parser("account")
    sub.add_parser("credits")

    usage = sub.add_parser("usage")
    usage.add_argument("--created-from")
    usage.add_argument("--created-to")

    api_key_usage = sub.add_parser("api-key-usage")
    api_key_usage.add_argument("--window", choices=["7d", "30d", "90d"], default="30d")

    ledger = sub.add_parser("ledger")
    ledger.add_argument("--limit", type=int, default=25)
    ledger.add_argument("--cursor")
    ledger.add_argument("--type")
    ledger.add_argument("--created-from")
    ledger.add_argument("--created-to")

    packages = sub.add_parser("credit-packages")
    packages.add_argument("--currency", default="EUR")

    purchases = sub.add_parser("billing-purchases")
    purchases.add_argument("--limit", type=int, default=25)
    purchases.add_argument("--cursor")
    purchases.add_argument("--status")
    purchases.add_argument("--created-from")
    purchases.add_argument("--created-to")

    models = sub.add_parser("models")
    models.add_argument("--task-type")
    models.add_argument("--enabled", action=argparse.BooleanOptionalAction, default=None)

    worker_health = sub.add_parser("worker-health")
    worker_health.add_argument("--require-worker", action="append", default=None)
    worker_health.add_argument("--include-workers", action="store_true")
    worker_health.add_argument("--limit", type=int, default=500)

    assets = sub.add_parser("assets")
    assets.add_argument("--limit", type=int, default=50)
    assets.add_argument("--cursor")
    assets.add_argument("--kind")
    assets.add_argument("--status", default="ready")

    estimate = sub.add_parser("estimate")
    add_generation_args(estimate)

    create = sub.add_parser("create")
    add_generation_args(create)
    create.add_argument("--idempotency-key", default=None)
    create.add_argument(
        "--client-request-id",
        default=None,
        help=(
            "Stable caller ID used as REST Idempotency-Key when --idempotency-key "
            "is not set. MCP has a native client_request_id parameter."
        ),
    )
    create.add_argument("--wait", action="store_true")
    create.add_argument("--timeout", type=int, default=1800)
    create.add_argument("--poll", type=float, default=5.0)

    get = sub.add_parser("get")
    get.add_argument("job_id")

    status = sub.add_parser("status")
    status.add_argument("job_id")

    wait = sub.add_parser("wait")
    wait.add_argument("job_id")
    wait.add_argument("--timeout", type=int, default=1800)
    wait.add_argument("--poll", type=float, default=5.0)

    jobs = sub.add_parser("jobs")
    jobs.add_argument("--limit", type=int, default=25)
    jobs.add_argument("--cursor")
    jobs.add_argument("--status")
    jobs.add_argument("--model-id")
    jobs.add_argument("--task-type")
    jobs.add_argument("--source")
    jobs.add_argument("--created-from")
    jobs.add_argument("--created-to")

    download = sub.add_parser("download-url")
    download.add_argument("asset_id")

    download_file = sub.add_parser("download")
    download_file.add_argument("asset_id")
    download_file.add_argument("-o", "--output", type=Path)

    cancel = sub.add_parser("cancel")
    cancel.add_argument("job_id")
    cancel.add_argument("--reason", default="rest_fallback_cancelled")

    delete_asset = sub.add_parser("delete-asset")
    delete_asset.add_argument("asset_id")

    upload = sub.add_parser("upload")
    upload.add_argument("path")
    upload.add_argument("--kind", default="source_audio")
    upload.add_argument("--mime-type")

    args = parser.parse_args()

    if args.cmd == "capabilities":
        print_json(request_json("GET", "/v1/capabilities"))
    elif args.cmd == "account":
        print_json(request_json("GET", "/v1/account"))
    elif args.cmd == "credits":
        print_json(request_json("GET", "/v1/credits/balance"))
    elif args.cmd == "usage":
        print_json(
            request_json(
                "GET",
                "/v1/usage/summary",
                params={"created_from": args.created_from, "created_to": args.created_to},
            )
        )
    elif args.cmd == "api-key-usage":
        print_json(request_json("GET", "/v1/usage/api-keys", params={"window": args.window}))
    elif args.cmd == "ledger":
        print_json(
            request_json(
                "GET",
                "/v1/credits/ledger",
                params={
                    "limit": args.limit,
                    "cursor": args.cursor,
                    "type": args.type,
                    "created_from": args.created_from,
                    "created_to": args.created_to,
                },
            )
        )
    elif args.cmd == "credit-packages":
        print_json(request_json("GET", "/v1/credits/packages", params={"currency": args.currency}))
    elif args.cmd == "billing-purchases":
        print_json(
            request_json(
                "GET",
                "/v1/billing/purchases",
                params={
                    "limit": args.limit,
                    "cursor": args.cursor,
                    "status": args.status,
                    "created_from": args.created_from,
                    "created_to": args.created_to,
                },
            )
        )
    elif args.cmd == "models":
        print_json(
            request_json(
                "GET",
                "/v1/models",
                params={"task_type": args.task_type, "enabled": args.enabled},
            )
        )
    elif args.cmd == "worker-health":
        print_json(
            request_json(
                "GET",
                "/health/workers",
                params={
                    "require_worker": args.require_worker,
                    "include_workers": args.include_workers,
                    "limit": args.limit,
                },
            )
        )
    elif args.cmd == "assets":
        print_json(
            request_json(
                "GET",
                "/v1/assets",
                params={
                    "limit": args.limit,
                    "cursor": args.cursor,
                    "kind": args.kind,
                    "status": args.status,
                },
            )
        )
    elif args.cmd == "estimate":
        print_json(request_json("POST", "/v1/generations/estimate", body=generation_payload(args)))
    elif args.cmd == "create":
        idem = args.idempotency_key or args.client_request_id or str(uuid.uuid4())
        created = request_json(
            "POST",
            "/v1/generations",
            body=generation_payload(args),
            headers={"Idempotency-Key": idem},
        )
        if not args.wait:
            print_json(created)
            return
        data = unwrap_data(created)
        job = data.get("job", {}) if isinstance(data, dict) else {}
        job_id = str(job.get("id") or "")
        if not job_id:
            raise SystemExit("Create response did not include data.job.id.")
        print_json(wait_for_job(job_id, timeout=args.timeout, poll=args.poll))
    elif args.cmd == "get":
        print_json(request_json("GET", f"/v1/generations/{args.job_id}"))
    elif args.cmd == "status":
        print_json(request_json("GET", f"/v1/generations/{args.job_id}/status"))
    elif args.cmd == "wait":
        print_json(wait_for_job(args.job_id, timeout=args.timeout, poll=args.poll))
    elif args.cmd == "jobs":
        print_json(
            request_json(
                "GET",
                "/v1/generations",
                params={
                    "limit": args.limit,
                    "cursor": args.cursor,
                    "status": args.status,
                    "model_id": args.model_id,
                    "task_type": args.task_type,
                    "source": args.source,
                    "created_from": args.created_from,
                    "created_to": args.created_to,
                },
            )
        )
    elif args.cmd == "download-url":
        print_json(request_json("GET", f"/v1/assets/{args.asset_id}/download-url"))
    elif args.cmd == "download":
        print_json(download_asset(args.asset_id, args.output))
    elif args.cmd == "cancel":
        print_json(
            request_json(
                "POST",
                f"/v1/generations/{args.job_id}/cancel",
                body={"reason": args.reason},
            )
        )
    elif args.cmd == "delete-asset":
        print_json(request_json("DELETE", f"/v1/assets/{args.asset_id}"))
    elif args.cmd == "upload":
        print_json(upload_file(Path(args.path), kind=args.kind, mime_type=args.mime_type))
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()

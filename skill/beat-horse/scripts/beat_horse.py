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
TERMINAL_STATUSES = {"succeeded", "partial_success", "failed", "cancelled", "expired"}


def request_json(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not KEY:
        raise SystemExit("Set BEAT_HORSE_API_KEY.")
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
        "Authorization": f"Bearer {KEY}",
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
        "inference_steps": args.inference_steps,
        "seed": args.seed,
        "use_random_seed": args.use_random_seed,
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
    parser.add_argument("--inference-steps", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--use-random-seed", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--output-format", choices=["mp3", "wav", "flac"], default="mp3")


def wait_for_job(job_id: str, *, timeout: int, poll: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    while True:
        status_payload = request_json("GET", f"/v1/generations/{job_id}/status")
        status_data = unwrap_data(status_payload)
        job = status_data.get("job", {}) if isinstance(status_data, dict) else {}
        status = str(job.get("status") or "unknown")
        if status in TERMINAL_STATUSES:
            return request_json("GET", f"/v1/generations/{job_id}")
        if time.time() >= deadline:
            return status_payload
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


def main() -> None:
    parser = argparse.ArgumentParser(description="beat.horse REST fallback client")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("capabilities")
    sub.add_parser("account")
    sub.add_parser("credits")

    estimate = sub.add_parser("estimate")
    add_generation_args(estimate)

    create = sub.add_parser("create")
    add_generation_args(create)
    create.add_argument("--idempotency-key", default=None)
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

    download = sub.add_parser("download-url")
    download.add_argument("asset_id")

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
    elif args.cmd == "estimate":
        print_json(request_json("POST", "/v1/generations/estimate", body=generation_payload(args)))
    elif args.cmd == "create":
        idem = args.idempotency_key or str(uuid.uuid4())
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
    elif args.cmd == "download-url":
        print_json(request_json("GET", f"/v1/assets/{args.asset_id}/download-url"))
    elif args.cmd == "upload":
        print_json(upload_file(Path(args.path), kind=args.kind, mime_type=args.mime_type))
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()

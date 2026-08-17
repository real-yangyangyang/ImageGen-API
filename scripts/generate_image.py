#!/usr/bin/env python3
"""Generate an image through an OpenAI-compatible images API."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://api.openai.com"


def _load_dotenv() -> None:
    paths = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ]
    for path in dict.fromkeys(paths):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _env_first(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def _redact(value: str | None) -> str:
    if not value:
        return "<unset>"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def _endpoint(base_url: str, endpoint: str | None) -> str:
    if endpoint:
        return urllib.parse.urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/"))

    base = base_url.rstrip("/")
    if base.endswith("/images/generations"):
        return base
    if base.endswith("/v1"):
        return base + "/images/generations"
    return base + "/v1/images/generations"


def _models_endpoint(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/images/generations"):
        return base.removesuffix("/images/generations") + "/models"
    if base.endswith("/v1"):
        return base + "/models"
    return base + "/v1/models"


def _safe_slug(text: str, limit: int = 40) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", text.strip()).strip("-._")
    return (slug[:limit] or "image").lower()


def _default_output(prompt: str) -> Path:
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return Path("outputs") / f"{timestamp}-{_safe_slug(prompt)}.png"


def _parse_extra_json(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--extra-json is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("--extra-json must decode to a JSON object")
    return value


def _request_json(url: str, api_key: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Image API request failed with HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Image API request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Image API returned non-JSON response: {exc}") from exc


def _get_json(url: str, api_key: str, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Models API request failed with HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Models API request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Models API returned non-JSON response: {exc}") from exc


def _print_models(result: dict[str, Any]) -> None:
    data = result.get("data")
    if not isinstance(data, list):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    model_ids = []
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            model_ids.append(item["id"])

    print(json.dumps({"models": sorted(model_ids)}, ensure_ascii=False, indent=2))


def _download_url(url: str, timeout: int) -> tuple[bytes, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            return response.read(), content_type
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not download generated image URL: {exc}") from exc


def _first_image(result: dict[str, Any]) -> dict[str, Any]:
    data = result.get("data")
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            return first

    images = result.get("images")
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, dict):
            return first

    raise SystemExit("Could not find image data in API response")


def _bytes_from_response(image: dict[str, Any], timeout: int) -> tuple[bytes, str]:
    b64 = image.get("b64_json") or image.get("base64") or image.get("image")
    if isinstance(b64, str) and b64:
        if b64.startswith("data:"):
            header, _, encoded = b64.partition(",")
            content_type = header[5:].split(";", 1)[0] or "image/png"
            return base64.b64decode(encoded), content_type
        return base64.b64decode(b64), "image/png"

    url = image.get("url")
    if isinstance(url, str) and url:
        return _download_url(url, timeout)

    raise SystemExit("Response image contains neither b64_json nor url")


def _with_suffix(path: Path, content_type: str) -> Path:
    if path.suffix:
        return path
    suffix = mimetypes.guess_extension(content_type.split(";", 1)[0].strip()) or ".png"
    return path.with_suffix(suffix)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", help="Text prompt for image generation.")
    parser.add_argument("--model", default=_env_first("IMAGEGEN_MODEL"), help="Image model name.")
    parser.add_argument("--api-key", default=_env_first("IMAGEGEN_API_KEY", "OPENAI_API_KEY"), help="API key.")
    parser.add_argument("--base-url", default=_env_first("IMAGEGEN_BASE_URL", "OPENAI_BASE_URL", "OPENAI_API_BASE") or DEFAULT_BASE_URL, help="API base URL or relay URL.")
    parser.add_argument("--endpoint", help="Override request endpoint, for providers that do not use /v1/images/generations.")
    parser.add_argument("--size", default="1024x1024", help="Requested image size.")
    parser.add_argument("--n", type=int, default=1, help="Number of images requested; script saves the first one.")
    parser.add_argument("--output", type=Path, help="Output image path. Defaults to outputs/<timestamp>-<prompt>.png.")
    parser.add_argument("--timeout", type=int, default=180, help="HTTP timeout in seconds.")
    parser.add_argument("--response-format", choices=["url", "b64_json"], help="Optional OpenAI-style response_format field.")
    parser.add_argument("--extra-json", help="Provider-specific JSON object merged into the request payload.")
    parser.add_argument("--dry-run", action="store_true", help="Print sanitized request configuration without calling the API.")
    parser.add_argument("--list-models", action="store_true", help="List models exposed by the configured /v1/models endpoint.")
    return parser


def main() -> int:
    _load_dotenv()
    args = build_parser().parse_args()
    if not args.api_key:
        raise SystemExit("Missing API key. Set IMAGEGEN_API_KEY or OPENAI_API_KEY, or pass --api-key.")
    if args.list_models:
        models_url = _models_endpoint(args.base_url)
        if args.dry_run:
            print(json.dumps({
                "url": models_url,
                "api_key": _redact(args.api_key),
            }, ensure_ascii=False, indent=2))
            return 0
        _print_models(_get_json(models_url, args.api_key, args.timeout))
        return 0
    if not args.prompt:
        raise SystemExit("Missing prompt. Pass --prompt, or use --list-models to inspect provider models.")
    if not args.model:
        raise SystemExit("Missing model. Set IMAGEGEN_MODEL or pass --model.")

    payload: dict[str, Any] = {
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
        "n": args.n,
    }
    if args.response_format:
        payload["response_format"] = args.response_format
    payload.update(_parse_extra_json(args.extra_json))

    url = _endpoint(args.base_url, args.endpoint)
    output = args.output or _default_output(args.prompt)

    if args.dry_run:
        print(json.dumps({
            "url": url,
            "api_key": _redact(args.api_key),
            "payload": payload,
            "output": str(output),
        }, ensure_ascii=False, indent=2))
        return 0

    result = _request_json(url, args.api_key, payload, args.timeout)
    image = _first_image(result)
    data, content_type = _bytes_from_response(image, args.timeout)
    output = _with_suffix(output, content_type)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)

    print(json.dumps({
        "output": str(output.resolve()),
        "bytes": len(data),
        "content_type": content_type or "unknown",
        "model": args.model,
        "base_url": args.base_url,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())


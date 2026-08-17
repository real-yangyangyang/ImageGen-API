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
SKILL_NAME = "iga"
SCRIPT_DIR = Path(__file__).resolve().parent.parent
PROFILE_PREFIX = "IMAGEGEN_PROFILE_"
PROFILE_FIELDS = {
    "API_KEY": "api_key",
    "MODEL": "model",
    "BASE_URL": "base_url",
    "ENDPOINT": "endpoint",
}


def _codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex"


def _candidate_skill_dirs() -> list[Path]:
    candidates: list[Path] = []
    configured = os.environ.get("IGA_SKILL_DIR")
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.append(_codex_home() / "skills" / SKILL_NAME)
    candidates.append(SCRIPT_DIR)
    return list(dict.fromkeys(candidates))


def _resolve_skill_dir() -> Path:
    for directory in _candidate_skill_dirs():
        if (directory / "SKILL.md").exists():
            return directory
    return SCRIPT_DIR


SKILL_DIR = _resolve_skill_dir()


def _load_dotenv() -> None:
    paths = [
        Path.cwd() / ".env",
        SKILL_DIR / ".env",
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


def _profile_env_name(profile: str, field: str) -> str:
    safe_profile = re.sub(r"[^A-Za-z0-9]+", "_", profile).strip("_").upper()
    return f"{PROFILE_PREFIX}{safe_profile}_{field}"


def _profile_from_env(profile: str | None) -> dict[str, str]:
    if not profile:
        return {}

    config: dict[str, str] = {}
    for env_field, key in PROFILE_FIELDS.items():
        value = os.environ.get(_profile_env_name(profile, env_field))
        if value:
            config[key] = value
    return config


def _profile_names_from_env() -> list[str]:
    names: set[str] = set()
    suffixes = tuple(f"_{field}" for field in PROFILE_FIELDS)
    for key in os.environ:
        if not key.startswith(PROFILE_PREFIX):
            continue
        remainder = key[len(PROFILE_PREFIX):]
        for suffix in suffixes:
            if remainder.endswith(suffix):
                names.add(remainder[:-len(suffix)].lower())
                break
    return sorted(names)


def _resolve_setting(cli_value: str | None, profile_config: dict[str, str], profile_key: str, *env_names: str, default: str | None = None) -> str | None:
    if cli_value:
        return cli_value
    profile_value = profile_config.get(profile_key)
    if profile_value:
        return profile_value
    return _env_first(*env_names) or default


def _selected_profile(cli_profile: str | None) -> str | None:
    return cli_profile or _env_first("IMAGEGEN_PROFILE", "IMAGEGEN_DEFAULT_PROFILE")


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
    return Path.cwd() / "outputs" / f"{timestamp}-{_safe_slug(prompt)}.png"


def _show_paths() -> None:
    print(json.dumps({
        "skill_dir": str(SKILL_DIR.resolve()),
        "script_dir": str(SCRIPT_DIR.resolve()),
        "cwd": str(Path.cwd().resolve()),
        "skill_dir_candidates": [str(path.resolve()) for path in _candidate_skill_dirs()],
        "dotenv_candidates": [
            str((Path.cwd() / ".env").resolve()),
            str((SKILL_DIR / ".env").resolve()),
        ],
        "configured_profiles": _profile_names_from_env(),
    }, ensure_ascii=False, indent=2))


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
    parser.add_argument("--profile", help="Named IMAGEGEN_PROFILE_<NAME>_* configuration to use.")
    parser.add_argument("--model", help="Image model name.")
    parser.add_argument("--api-key", help="API key.")
    parser.add_argument("--base-url", help="API base URL or relay URL.")
    parser.add_argument("--endpoint", help="Override request endpoint, for providers that do not use /v1/images/generations.")
    parser.add_argument("--size", default="1024x1024", help="Requested image size.")
    parser.add_argument("--n", type=int, default=1, help="Number of images requested; script saves the first one.")
    parser.add_argument("--output", type=Path, help="Output image path. Defaults to ./outputs/<timestamp>-<prompt>.png in the current working directory.")
    parser.add_argument("--timeout", type=int, default=180, help="HTTP timeout in seconds.")
    parser.add_argument("--response-format", choices=["url", "b64_json"], help="Optional OpenAI-style response_format field.")
    parser.add_argument("--extra-json", help="Provider-specific JSON object merged into the request payload.")
    parser.add_argument("--dry-run", action="store_true", help="Print sanitized request configuration without calling the API.")
    parser.add_argument("--list-models", action="store_true", help="List models exposed by the configured /v1/models endpoint.")
    parser.add_argument("--list-profiles", action="store_true", help="List configured IMAGEGEN_PROFILE_<NAME>_* profile names.")
    parser.add_argument("--show-paths", action="store_true", help="Show the resolved skill, cwd, and .env paths.")
    return parser


def main() -> int:
    _load_dotenv()
    args = build_parser().parse_args()
    if args.show_paths:
        _show_paths()
        return 0
    if args.list_profiles:
        print(json.dumps({"profiles": _profile_names_from_env()}, ensure_ascii=False, indent=2))
        return 0

    profile = _selected_profile(args.profile)
    profile_config = _profile_from_env(profile)
    api_key = _resolve_setting(args.api_key, profile_config, "api_key", "IMAGEGEN_API_KEY", "OPENAI_API_KEY")
    model = _resolve_setting(args.model, profile_config, "model", "IMAGEGEN_MODEL")
    base_url = _resolve_setting(args.base_url, profile_config, "base_url", "IMAGEGEN_BASE_URL", "OPENAI_BASE_URL", "OPENAI_API_BASE", default=DEFAULT_BASE_URL)
    endpoint = _resolve_setting(args.endpoint, profile_config, "endpoint")

    if profile and not profile_config:
        known = ", ".join(_profile_names_from_env()) or "<none>"
        raise SystemExit(f"Profile '{profile}' is not configured. Known profiles: {known}")
    if not api_key:
        raise SystemExit("Missing API key. Set IMAGEGEN_API_KEY or OPENAI_API_KEY, or pass --api-key.")
    if args.list_models:
        models_url = _models_endpoint(base_url)
        if args.dry_run:
            print(json.dumps({
                "profile": profile,
                "url": models_url,
                "api_key": _redact(api_key),
            }, ensure_ascii=False, indent=2))
            return 0
        _print_models(_get_json(models_url, api_key, args.timeout))
        return 0
    if not args.prompt:
        raise SystemExit("Missing prompt. Pass --prompt, or use --list-models to inspect provider models.")
    if not model:
        raise SystemExit("Missing model. Set IMAGEGEN_MODEL or pass --model.")

    payload: dict[str, Any] = {
        "model": model,
        "prompt": args.prompt,
        "size": args.size,
        "n": args.n,
    }
    if args.response_format:
        payload["response_format"] = args.response_format
    payload.update(_parse_extra_json(args.extra_json))

    url = _endpoint(base_url, endpoint)
    output = args.output or _default_output(args.prompt)

    if args.dry_run:
        print(json.dumps({
            "profile": profile,
            "url": url,
            "api_key": _redact(api_key),
            "payload": payload,
            "output": str(output),
        }, ensure_ascii=False, indent=2))
        return 0

    result = _request_json(url, api_key, payload, args.timeout)
    image = _first_image(result)
    data, content_type = _bytes_from_response(image, args.timeout)
    output = _with_suffix(output, content_type)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)

    print(json.dumps({
        "output": str(output.resolve()),
        "bytes": len(data),
        "content_type": content_type or "unknown",
        "model": model,
        "base_url": base_url,
        "profile": profile,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

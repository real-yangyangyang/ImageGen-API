---
name: iga
description: Generate images from Codex through a user-configured image-generation API. Use when the user wants Codex to call a text-to-image or image-generation model with a manually supplied API key, model name, and optional relay/base URL. This skill includes an OpenAI-compatible adapter for /v1/images/generations-style providers and can be extended with provider-specific adapters for other native image APIs.
---

# ImageGen API

Use this skill to generate images through a user-configured image API. The bundled script currently provides an OpenAI-compatible adapter; add narrow provider-specific adapters when a service uses a different endpoint, authentication scheme, request body, job polling flow, or response schema.

## Workflow

1. Collect required runtime settings:
   - Prompt: the exact image prompt to send.
   - API key: from `.env`, `IMAGEGEN_API_KEY`, `OPENAI_API_KEY`, or an explicit `--api-key`.
   - Model: from `.env`, `IMAGEGEN_MODEL`, or an explicit `--model`.
   - Base URL: optional `.env`, `IMAGEGEN_BASE_URL`, `OPENAI_BASE_URL`, or `--base-url`.
2. Never write API keys into files, logs, examples, or final messages. Prefer temporary environment variables or command arguments only when the user explicitly supplies them in the session.
3. Run `scripts/generate_image.py` for the actual API call.
4. Return the generated file path and, when the host supports images, render the image with Markdown. Do not list, read, or summarize existing files in `outputs/` during normal generation.

## Quick Start

Use the bundled script:

```bash
python scripts/generate_image.py \
  --prompt "A cinematic product photo of a translucent mechanical keyboard on a glass desk" \
  --model "$IMAGEGEN_MODEL" \
  --output outputs/keyboard.png
```

For relay services, pass the base URL:

```bash
python scripts/generate_image.py \
  --prompt "A clean isometric illustration of an image API" \
  --model "$IMAGEGEN_MODEL" \
  --base-url "$IMAGEGEN_BASE_URL" \
  --output outputs/image-api.png
```

## Configuration

Required:
- `IMAGEGEN_API_KEY` or `OPENAI_API_KEY`, unless `--api-key` is provided.
- `IMAGEGEN_MODEL`, unless `--model` is provided.

For easiest setup, copy `.env.example` to `.env`, fill in the values, and keep `.env` out of git.

Optional:
- `IMAGEGEN_BASE_URL` or `OPENAI_BASE_URL`; defaults to `https://api.openai.com`.
- `--size`, default `1024x1024`.
- `--output`, default auto-generates a PNG under the skill-local `outputs/` directory.
- `--extra-json`, for provider-specific payload fields.

Read `references/configuration.md` only when troubleshooting a provider, relay URL, response format, model availability, or environment-variable setup.


## Outputs

Generated images are saved to the `outputs/` directory of the skill copy that is actually executed, so users can recover prior images. Treat this folder as isolated local history:
- Do not read or list `outputs/` during normal image generation.
- Access `outputs/` only when the user explicitly asks to find, list, recover, or clean generated images.
- Use `python scripts/generate_image.py --list-outputs` to list saved images.
- Use `python scripts/generate_image.py --clean-outputs` to delete saved images.
- Use `python scripts/generate_image.py --show-paths` to show the active skill directory and `outputs/` location.
## Built-In Adapter

The bundled script targets OpenAI-compatible image-generation APIs:
- Request path defaults to `/v1/images/generations`.
- Authorization uses `Bearer <api_key>`.
- Responses may contain either `data[0].b64_json` or `data[0].url`.

## Extending Providers

If a provider uses a different native API, extend the script with a small provider adapter instead of hardcoding secrets or model-specific behavior in `SKILL.md`. Keep each adapter responsible for only the provider-specific request and response mapping, and preserve the same user-facing workflow: prompt in, image file path out.






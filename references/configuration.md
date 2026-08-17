# Configuration Reference

The bundled script currently implements an OpenAI-compatible adapter. For native APIs that use different authentication, endpoints, request bodies, polling flows, or response schemas, add a narrow provider adapter while preserving the same user-facing workflow.

## Environment Variables

For easiest setup, copy `.env.example` to `.env` and fill in your own values:

```dotenv
IMAGEGEN_API_KEY=your-api-key
IMAGEGEN_MODEL=your-image-model
IMAGEGEN_BASE_URL=
```

The script automatically reads `.env` from the current working directory or the skill directory. Environment variables still work and take priority over `.env` values.

Use shell environment variables when preferred:

```bash
export IMAGEGEN_API_KEY="..."
export IMAGEGEN_MODEL="..."
export IMAGEGEN_BASE_URL="https://relay.example.com"
```

PowerShell:

```powershell
$env:IMAGEGEN_API_KEY = "..."
$env:IMAGEGEN_MODEL = "..."
$env:IMAGEGEN_BASE_URL = "https://relay.example.com"
```

Fallback variable names are supported for OpenAI-compatible setups:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_API_BASE`

## URL Handling

Pass `--base-url` as a provider root, a `/v1` base URL, or the full image-generation endpoint.

If `--base-url` already ends with `/images/generations`, the script uses it unchanged:

```text
<base-url>
```

If `--base-url` ends with `/v1`, the script calls:

```text
<base-url>/images/generations
```

Otherwise it calls:

```text
<base-url>/v1/images/generations
```

Use `--endpoint` only when a provider requires a different path. Do not pass a full `/v1/images/generations` URL through both `--base-url` and `--endpoint`.

## Provider-Specific Fields

Pass extra request fields as JSON:

```bash
python scripts/generate_image.py \
  --prompt "A watercolor mountain village" \
  --model "$IMAGEGEN_MODEL" \
  --extra-json '{"quality":"high","background":"transparent"}'
```

Only include fields documented by the provider.

## Expected Responses

The script can save images from:

- `data[0].b64_json`
- `data[0].url`
- `images[0].base64`
- data URLs such as `data:image/png;base64,...`

If a provider returns a different schema, patch `scripts/generate_image.py` narrowly and keep secret values out of the repository.

## Model Availability

A `model_not_found` error means the configured service did not accept the exact model id in the request. A provider may advertise a model but expose it under another alias, limit it by account entitlement, require a dedicated endpoint, or not route it through the image-generation API.

Check what the configured service exposes:

```bash
python scripts/generate_image.py \
  --list-models \
  --api-key "$IMAGEGEN_API_KEY" \
  --base-url "$IMAGEGEN_BASE_URL"
```

Use the model id exactly as returned by the service. If the advertised model is unavailable for generation, ask the provider for the exact model id, required endpoint, account entitlement, and supported request payload.




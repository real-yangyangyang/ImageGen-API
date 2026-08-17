# ImageGen API

[中文](#中文) | [English](#english)

---

## 中文

ImageGen API（调用名：`$iga`）是一个轻量级 Codex 生图 skill，用于通过用户自己的图片生成 API 在 Codex 中生成图片。当前内置 OpenAI-compatible adapter；其他厂商的原生 API 可以通过 provider adapter 扩展支持。

用户自行配置 API key、模型名称和可选中转站 URL。本仓库不保存密钥，生成图片默认保存到本地 `outputs/` 目录。

### 功能

- 内置 OpenAI-compatible adapter，支持 `/v1/images/generations` 风格的图片生成接口。
- 支持 OpenAI-compatible 中转站、自定义 API base URL，以及后续扩展的 provider adapter。
- 支持通过 `.env`、环境变量或命令参数提供 API key、模型名和 URL。
- 支持保存 `b64_json`、图片 URL、data URL 等常见响应格式。
- 提供模型列表查询，便于确认中转站实际可用的模型 id。

### 安装

克隆到 Codex skills 目录：

```bash
git clone <your-repo-url> ~/.codex/skills/iga
```

Windows PowerShell：

```powershell
git clone <your-repo-url> "$env:USERPROFILE\.codex\skills\iga"
```

安装后重启 Codex，让 skill 被重新发现。

### 配置

最简单的方式是在 skill 目录中复制示例配置文件：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`：

```dotenv
IMAGEGEN_API_KEY=your-api-key
IMAGEGEN_MODEL=your-image-model
IMAGEGEN_BASE_URL=
```

`IMAGEGEN_BASE_URL` 可选；不设置或留空时默认使用 `https://api.openai.com`。脚本会自动读取 skill 目录或当前工作目录下的 `.env`。

URL 可以填写以下任一形式：

```text
https://relay.example.com
https://relay.example.com/v1
https://relay.example.com/v1/images/generations
```

脚本会自动识别完整 endpoint，避免重复拼接 `/v1/images/generations`。

### 在 Codex 中使用

```text
Use $iga to generate an image: a clean isometric illustration of an image API, white background, high detail.
```

Codex 会根据 skill 指令调用内置脚本，并返回生成图片的本地路径。

### 直接运行脚本

```bash
python scripts/generate_image.py \
  --prompt "A cinematic product photo of a translucent keyboard on a glass desk" \
  --model "$IMAGEGEN_MODEL" \
  --output outputs/keyboard.png
```

使用自定义中转站：

```bash
python scripts/generate_image.py \
  --prompt "A watercolor mountain village at sunrise" \
  --model "$IMAGEGEN_MODEL" \
  --base-url "$IMAGEGEN_BASE_URL" \
  --output outputs/village.png
```

### 常用参数

- `--prompt`：图片提示词。
- `--model`：图片模型名称；未提供时读取 `IMAGEGEN_MODEL`。
- `--api-key`：API key；优先建议使用 `.env` 或环境变量。
- `--base-url`：API base URL 或完整图片生成 endpoint。
- `--size`：图片尺寸，默认 `1024x1024`。
- `--output`：输出图片路径。
- `--extra-json`：传入服务商专属 JSON 字段。
- `--list-models`：查询当前服务实际暴露的模型 id。

### Provider 扩展

当前脚本开箱支持 OpenAI-compatible 接口。如果服务商只是额外增加少量字段，可以通过 JSON 传入：

```bash
python scripts/generate_image.py \
  --prompt "A transparent-background app icon" \
  --model "$IMAGEGEN_MODEL" \
  --extra-json '{"quality":"high","background":"transparent"}'
```

只传入服务商明确支持的字段。若厂商使用不同鉴权、任务轮询、endpoint 或响应结构，应在脚本中新增 provider adapter，而不是把模型专属逻辑写进 README 或 `SKILL.md`。

### 查询可用模型

如果不确定中转站支持哪些模型，可以查询模型列表：

```bash
python scripts/generate_image.py \
  --list-models \
  --api-key "$IMAGEGEN_API_KEY" \
  --base-url "$IMAGEGEN_BASE_URL"
```

使用返回结果中的精确模型 id。

### 隐私与安全

- 不要提交 API key，也不要提交真实 `.env`。
- 不要把密钥写入 `SKILL.md`、`README.md` 或示例文件。
- 推荐使用 `.env` 或环境变量管理密钥；`.env.example` 只放占位值。
- Prompt、模型名和请求参数会发送给你配置的 API 服务商或中转站。
- 生成图片保存在本地；`outputs/` 默认已被 `.gitignore` 排除。
- 本仓库不包含遥测、统计或额外回传逻辑。

---

## English

ImageGen API (invoked as `$iga`) is a lightweight Codex image-generation skill for generating images through a user-provided image-generation API. It includes a built-in OpenAI-compatible adapter; native APIs from other providers can be supported by adding provider adapters.

Users configure their own API key, model name, and optional relay/base URL. This repository does not store secrets, and generated images are saved locally under `outputs/` by default.

### Features

- Includes a built-in OpenAI-compatible adapter for `/v1/images/generations` style image APIs.
- Supports OpenAI-compatible relays, custom API base URLs, and future provider adapters.
- Reads API key, model, and URL from `.env`, environment variables, or command-line arguments.
- Saves common response formats including `b64_json`, image URLs, and data URLs.
- Can query the configured service for exposed model ids.

### Install

Clone this repository into your Codex skills directory:

```bash
git clone <your-repo-url> ~/.codex/skills/iga
```

Windows PowerShell:

```powershell
git clone <your-repo-url> "$env:USERPROFILE\.codex\skills\iga"
```

Restart Codex after installing so the skill can be discovered.

### Configure

The easiest setup is to copy the example environment file inside the skill directory:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then edit `.env`:

```dotenv
IMAGEGEN_API_KEY=your-api-key
IMAGEGEN_MODEL=your-image-model
IMAGEGEN_BASE_URL=
```

`IMAGEGEN_BASE_URL` is optional; if omitted or left empty, the script defaults to `https://api.openai.com`. The script automatically reads `.env` from the skill directory or the current working directory.

The URL may use any of these forms:

```text
https://relay.example.com
https://relay.example.com/v1
https://relay.example.com/v1/images/generations
```

The script detects a full endpoint URL and avoids appending `/v1/images/generations` twice.

### Use In Codex

```text
Use $iga to generate an image: a clean isometric illustration of an image API, white background, high detail.
```

Codex will follow the skill instructions, call the bundled script, and return the generated local image path.

### Direct Script Usage

```bash
python scripts/generate_image.py \
  --prompt "A cinematic product photo of a translucent keyboard on a glass desk" \
  --model "$IMAGEGEN_MODEL" \
  --output outputs/keyboard.png
```

With a custom relay URL:

```bash
python scripts/generate_image.py \
  --prompt "A watercolor mountain village at sunrise" \
  --model "$IMAGEGEN_MODEL" \
  --base-url "$IMAGEGEN_BASE_URL" \
  --output outputs/village.png
```

### Common Options

- `--prompt`: Image prompt.
- `--model`: Image model name; defaults to `IMAGEGEN_MODEL`.
- `--api-key`: API key; `.env` or environment variables are recommended.
- `--base-url`: API base URL or full image-generation endpoint.
- `--size`: Image size, default `1024x1024`.
- `--output`: Output image path.
- `--extra-json`: Provider-specific JSON fields.
- `--list-models`: Query model ids exposed by the configured service.

### Provider Extensions

The bundled script works out of the box with OpenAI-compatible APIs. If your provider only needs a few extra fields, pass them as JSON:

```bash
python scripts/generate_image.py \
  --prompt "A transparent-background app icon" \
  --model "$IMAGEGEN_MODEL" \
  --extra-json '{"quality":"high","background":"transparent"}'
```

Only include fields documented by your provider. If a provider uses different authentication, job polling, endpoints, or response schemas, add a provider adapter in the script instead of placing model-specific logic in README or `SKILL.md`.

### Query Available Models

If you are unsure which models the relay supports, query its model list:

```bash
python scripts/generate_image.py \
  --list-models \
  --api-key "$IMAGEGEN_API_KEY" \
  --base-url "$IMAGEGEN_BASE_URL"
```

Use the exact model id returned by the service.

### Privacy And Security

- Do not commit API keys or a real `.env` file.
- Do not put secrets in `SKILL.md`, `README.md`, or examples.
- Prefer `.env` or environment variables for credentials; `.env.example` should contain placeholders only.
- Prompts, model names, and request parameters are sent to the configured API provider or relay.
- Generated images are saved locally; `outputs/` is ignored by default.
- This repository does not include telemetry, analytics, or additional callbacks.





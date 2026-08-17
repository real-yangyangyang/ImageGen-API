# ImageGen API

<p align="center">
  <strong>A lightweight Codex skill for image generation through user-configured APIs.</strong>
</p>

<p align="center">
  <a href="#中文">中文</a> · <a href="#english">English</a>
</p>

---

## 中文

ImageGen API 是一个轻量级 Codex 生图技能。它内置 OpenAI-compatible adapter，适用于 `/v1/images/generations` 风格的图片生成接口，也可以扩展其他厂商的 provider adapter。

### 特性

- 支持 OpenAI-compatible 图片生成接口和中转站。
- 支持 `.env`、环境变量和命令参数配置。
- 支持 `b64_json`、图片 URL、data URL 等常见响应格式。
- 默认保存图片到本地 `outputs/`，方便之后找回。
- 提供模型列表、输出目录查看和清理命令。

### 安装

克隆到 Codex skills 目录：

```bash
git clone https://github.com/real-yangyangyang/ImageGen-API.git ~/.codex/skills/iga
```

Windows PowerShell：

```powershell
git clone https://github.com/real-yangyangyang/ImageGen-API.git "$env:USERPROFILE\.codex\skills\iga"
```

安装后重启 Codex。

### 配置

进入 skill 目录，复制示例配置：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`：

```dotenv
IMAGEGEN_API_KEY=your-api-key
IMAGEGEN_MODEL=your-image-model
IMAGEGEN_BASE_URL=
```

`IMAGEGEN_BASE_URL` 可留空，默认使用 `https://api.openai.com`。也可以填写中转站根地址、`/v1` 地址，或完整 `/v1/images/generations` endpoint。

### 在 Codex 中使用

```text
Use $iga to generate an image: a clean isometric illustration of an image API, white background, high detail.
```

### 直接运行脚本

```bash
python scripts/generate_image.py \
  --prompt "A cinematic product photo of a translucent keyboard" \
  --output outputs/keyboard.png
```

### 图片保存与清理

默认生成图片会保存到已安装的 skill 目录：`~/.codex/skills/iga/outputs/`。Codex 可能会在任务目录中执行一份临时副本，但脚本会优先定位已安装目录，避免图片落到临时任务文件夹。仓库保留 `outputs/.gitkeep`，真实图片会被 `.gitignore` 忽略。若需要自定义保存位置，可在 `.env` 中设置 `IGA_OUTPUT_DIR`。

```bash
python scripts/generate_image.py --show-paths
python scripts/generate_image.py --list-outputs
python scripts/generate_image.py --clean-outputs
```

`--clean-outputs` 会不可恢复地删除 `outputs/` 中的图片，请谨慎使用。

### 常用参数

| 参数 | 说明 |
| --- | --- |
| `--prompt` | 图片提示词 |
| `--model` | 模型名；默认读取 `IMAGEGEN_MODEL` |
| `--api-key` | API key；推荐使用 `.env` |
| `--base-url` | API base URL 或完整图片生成 endpoint |
| `--size` | 图片尺寸，默认 `1024x1024` |
| `--output` | 输出路径；未指定时保存到 skill 本地 `outputs/` |
| `--extra-json` | 服务商支持的额外 JSON 字段 |
| `--list-models` | 查询当前服务暴露的模型 id |

### 安全

- 不要提交真实 `.env` 或 API key。
- `.env.example` 只放占位值，可以提交。
- Prompt、模型名和请求参数会发送给你配置的 API 服务商或中转站。
- 本项目不包含遥测、统计或额外回传逻辑。

---

## English

ImageGen API is a lightweight Codex skill for image generation through user-configured APIs. It includes a built-in OpenAI-compatible adapter for `/v1/images/generations` style APIs, and can be extended with provider adapters for other native image APIs.

### Features

- Supports OpenAI-compatible image-generation APIs and relays.
- Supports `.env`, environment variables, and command-line configuration.
- Handles common response formats including `b64_json`, image URLs, and data URLs.
- Saves generated images locally under `outputs/` for recovery.
- Includes commands for model listing, output-path inspection, and cleanup.

### Install

Clone this repository into your Codex skills directory:

```bash
git clone https://github.com/real-yangyangyang/ImageGen-API.git ~/.codex/skills/iga
```

Windows PowerShell:

```powershell
git clone https://github.com/real-yangyangyang/ImageGen-API.git "$env:USERPROFILE\.codex\skills\iga"
```

Restart Codex after installation.

### Configure

Inside the skill directory, copy the example environment file:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```dotenv
IMAGEGEN_API_KEY=your-api-key
IMAGEGEN_MODEL=your-image-model
IMAGEGEN_BASE_URL=
```

`IMAGEGEN_BASE_URL` may be empty to use `https://api.openai.com`. It may also be a relay root URL, a `/v1` URL, or a full `/v1/images/generations` endpoint.

### Use In Codex

```text
Use $iga to generate an image: a clean isometric illustration of an image API, white background, high detail.
```

### Direct Script Usage

```bash
python scripts/generate_image.py \
  --prompt "A cinematic product photo of a translucent keyboard" \
  --output outputs/keyboard.png
```

### Image Storage And Cleanup

Generated images are saved by default under the installed skill directory: `~/.codex/skills/iga/outputs/`. Codex may execute a temporary copy inside a task workspace, but the script prefers the installed skill directory so images do not land in temporary task folders. The repository keeps `outputs/.gitkeep`; real image files are ignored by `.gitignore`. To override the save location, set `IGA_OUTPUT_DIR` in `.env`.

```bash
python scripts/generate_image.py --show-paths
python scripts/generate_image.py --list-outputs
python scripts/generate_image.py --clean-outputs
```

`--clean-outputs` permanently deletes images in `outputs/`; use it carefully.

### Common Options

| Option | Description |
| --- | --- |
| `--prompt` | Image prompt |
| `--model` | Model name; defaults to `IMAGEGEN_MODEL` |
| `--api-key` | API key; `.env` is recommended |
| `--base-url` | API base URL or full image-generation endpoint |
| `--size` | Image size, default `1024x1024` |
| `--output` | Output path; defaults to the skill-local `outputs/` |
| `--extra-json` | Extra JSON fields supported by your provider |
| `--list-models` | Query model ids exposed by the configured service |

### Security

- Do not commit a real `.env` or API keys.
- `.env.example` should contain placeholders only and is safe to commit.
- Prompts, model names, and request parameters are sent to the configured API provider or relay.
- This project does not include telemetry, analytics, or additional callbacks.



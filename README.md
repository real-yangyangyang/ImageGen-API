<h1 align="center">ImageGen API</h1>

<p align="center">
  <strong>Codex image generation skill powered by your own API profiles.</strong><br>
  <strong>一个通过自定义 API 调用图片模型的 Codex 生图技能。</strong>
</p>

<p align="center">
  <a href="#中文">中文</a> · <a href="#english">English</a>
</p>

---

## 中文

<p align="right"><a href="#english">Switch to English</a></p>

### 这是什么

ImageGen API 是一个轻量级 Codex skill，用来把你的图片生成请求转发到自己配置的图片 API。

它内置 OpenAI-compatible 适配器，适合支持 `/v1/images/generations` 风格接口的服务，也支持中转站、多个 API profile，以及常见的 `b64_json`、图片 URL、data URL 响应格式。

### 适合谁

- 已经有图片模型 API key，想直接在 Codex 里生图。
- 使用 OpenAI-compatible 中转站，需要自定义 `base_url` 和模型名。
- 同时维护多个图片服务，希望通过 profile 快速切换。
- 想保留一个简单、可审计、无遥测的本地生图工具。

### 快速开始

#### 1. 安装到 Codex skills 目录

macOS / Linux:

```bash
git clone https://github.com/real-yangyangyang/ImageGen-API.git ~/.codex/skills/iga
```

Windows PowerShell:

```powershell
git clone https://github.com/real-yangyangyang/ImageGen-API.git "$env:USERPROFILE\.codex\skills\iga"
```

安装完成后，重启 Codex。

#### 2. 创建本地配置

进入 skill 目录，复制环境变量模板：

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

编辑 `.env`，填入你的 API key 和模型名：

```dotenv
IMAGEGEN_API_KEY=your-api-key
IMAGEGEN_MODEL=your-image-model
IMAGEGEN_BASE_URL=
```

`IMAGEGEN_BASE_URL` 留空时默认使用 `https://api.openai.com`。你也可以填写中转站根地址、`/v1` 地址，或完整的 `/v1/images/generations` endpoint。

#### 3. 在 Codex 里调用

```text
Use $iga to generate an image: a cinematic product photo of a translucent keyboard on a glass desk.
```

生成成功后，Codex 会返回图片文件路径，并在支持图片预览的环境中展示结果。

### 配置方式

#### 单一服务

最简单的配置只需要三个变量：

```dotenv
IMAGEGEN_API_KEY=your-api-key
IMAGEGEN_MODEL=your-image-model
IMAGEGEN_BASE_URL=https://relay.example.com
```

#### 多服务 Profile

如果你有多个服务或多个中转站，可以使用命名 profile：

```dotenv
IMAGEGEN_PROFILE=openai

IMAGEGEN_PROFILE_OPENAI_API_KEY=your-openai-api-key
IMAGEGEN_PROFILE_OPENAI_MODEL=your-openai-image-model
IMAGEGEN_PROFILE_OPENAI_BASE_URL=https://api.openai.com

IMAGEGEN_PROFILE_RELAY_API_KEY=your-relay-api-key
IMAGEGEN_PROFILE_RELAY_MODEL=your-relay-image-model
IMAGEGEN_PROFILE_RELAY_BASE_URL=https://relay.example.com
```

调用时指定 profile：

```text
Use $iga with profile relay to generate an image: a clean isometric illustration of an image API.
```

也可以在命令行中使用：

```bash
python scripts/generate_image.py \
  --profile relay \
  --prompt "A clean isometric illustration of an image API"
```

#### 配置优先级

1. 命令行参数：`--api-key`、`--model`、`--base-url`、`--endpoint`
2. 当前 profile：`IMAGEGEN_PROFILE_<NAME>_*`
3. 全局变量：`IMAGEGEN_API_KEY`、`IMAGEGEN_MODEL`、`IMAGEGEN_BASE_URL`
4. 默认 base URL：`https://api.openai.com`

更多 provider、URL、模型列表和响应格式说明见 [references/configuration.md](references/configuration.md)。

### 在 Codex 中使用

常规调用：

```text
Use $iga to generate an image: a minimal black-and-white icon set for an AI image API.
```

指定 profile：

```text
Use $iga with profile relay to generate an image: a soft watercolor mountain village at sunrise.
```

指定更明确的输出需求：

```text
Use $iga to generate an image: a square app icon, glassmorphism style, transparent background, high detail.
```

### 命令行使用

直接运行脚本：

```bash
python scripts/generate_image.py \
  --prompt "A cinematic product photo of a translucent keyboard" \
  --output outputs/keyboard.png
```

常用参数：

| 参数 | 作用 |
| --- | --- |
| `--prompt` | 图片提示词 |
| `--profile` | 选择 `.env` 中的命名 profile |
| `--model` | 覆盖 `IMAGEGEN_MODEL` |
| `--api-key` | 覆盖环境变量中的 API key |
| `--base-url` | API 根地址、`/v1` 地址或完整 endpoint |
| `--endpoint` | 为非标准 provider 覆盖请求路径 |
| `--size` | 图片尺寸，默认 `1024x1024` |
| `--output` | 输出文件路径 |
| `--extra-json` | 合并额外 provider 参数 |
| `--list-profiles` | 查看已配置 profile，不输出密钥 |
| `--list-models` | 查询当前服务暴露的模型 id |
| `--show-paths` | 查看 skill、脚本、`.env` 和当前目录解析结果 |

查看配置路径：

```bash
python scripts/generate_image.py --show-paths
```

查看可用 profile：

```bash
python scripts/generate_image.py --list-profiles
```

查看服务暴露的模型：

```bash
python scripts/generate_image.py --profile relay --list-models
```

### 图片输出

- 未指定 `--output` 时，图片会保存到当前运行目录的 `outputs/`。
- 指定 `--output` 时，脚本会按给定路径保存；相对路径按当前运行目录解析。
- 项目不再维护 skill 内部图片历史目录，也不跟踪生成图片。

### 项目结构

```text
.
├── SKILL.md                    # Codex skill 说明与执行规则
├── README.md                   # 用户使用文档
├── .env.example                # 本地配置模板，不包含真实密钥
├── agents/
│   └── openai.yaml             # Codex 展示信息
├── references/
│   └── configuration.md        # 进阶配置与排错说明
└── scripts/
    └── generate_image.py       # OpenAI-compatible 图片 API 调用脚本
```

### 安全说明

- 不要提交真实 `.env` 或 API key。
- `.env.example` 只应包含占位值，可以提交。
- Prompt、模型名和请求参数会发送给你配置的 API 服务商或中转站。
- 本项目不包含遥测、统计或额外回传逻辑。

### 排错

`Missing API key`

确认 `.env` 中存在 `IMAGEGEN_API_KEY`，或当前 profile 配置了 `IMAGEGEN_PROFILE_<NAME>_API_KEY`。

`Missing model`

确认 `.env` 中存在 `IMAGEGEN_MODEL`，或当前 profile 配置了 `IMAGEGEN_PROFILE_<NAME>_MODEL`。

`model_not_found`

运行 `--list-models` 查看服务实际暴露的模型 id，并使用返回结果中的精确模型名。

`Profile '<name>' is not configured`

运行 `--list-profiles` 检查 profile 名称；环境变量中的 profile 名会被转为大写并把非字母数字字符转为下划线。

---

## English

<p align="right"><a href="#中文">切换到中文</a></p>

### What It Is

ImageGen API is a lightweight Codex skill that sends your image-generation requests to an API provider you configure.

It includes an OpenAI-compatible adapter for `/v1/images/generations` style APIs, works with relay services, supports multiple API profiles, and handles common response formats such as `b64_json`, image URLs, and data URLs.

### Who It Is For

- You already have an image-model API key and want to generate images directly from Codex.
- You use an OpenAI-compatible relay and need custom `base_url` and model settings.
- You manage multiple image services and want to switch between them with profiles.
- You want a simple, auditable local image-generation tool with no telemetry.

### Quick Start

#### 1. Install Into The Codex Skills Directory

macOS / Linux:

```bash
git clone https://github.com/real-yangyangyang/ImageGen-API.git ~/.codex/skills/iga
```

Windows PowerShell:

```powershell
git clone https://github.com/real-yangyangyang/ImageGen-API.git "$env:USERPROFILE\.codex\skills\iga"
```

Restart Codex after installation.

#### 2. Create Local Configuration

Inside the skill directory, copy the environment template:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your API key and model id:

```dotenv
IMAGEGEN_API_KEY=your-api-key
IMAGEGEN_MODEL=your-image-model
IMAGEGEN_BASE_URL=
```

Leave `IMAGEGEN_BASE_URL` empty to use `https://api.openai.com`. You may also set it to a relay root URL, a `/v1` URL, or a full `/v1/images/generations` endpoint.

#### 3. Use It In Codex

```text
Use $iga to generate an image: a cinematic product photo of a translucent keyboard on a glass desk.
```

After generation succeeds, Codex returns the image file path and displays the image when the host supports previews.

### Configuration

#### Single Provider

The simplest setup needs only three variables:

```dotenv
IMAGEGEN_API_KEY=your-api-key
IMAGEGEN_MODEL=your-image-model
IMAGEGEN_BASE_URL=https://relay.example.com
```

#### Multiple Provider Profiles

If you use multiple providers or relay URLs, configure named profiles:

```dotenv
IMAGEGEN_PROFILE=openai

IMAGEGEN_PROFILE_OPENAI_API_KEY=your-openai-api-key
IMAGEGEN_PROFILE_OPENAI_MODEL=your-openai-image-model
IMAGEGEN_PROFILE_OPENAI_BASE_URL=https://api.openai.com

IMAGEGEN_PROFILE_RELAY_API_KEY=your-relay-api-key
IMAGEGEN_PROFILE_RELAY_MODEL=your-relay-image-model
IMAGEGEN_PROFILE_RELAY_BASE_URL=https://relay.example.com
```

Select a profile from Codex:

```text
Use $iga with profile relay to generate an image: a clean isometric illustration of an image API.
```

Or from the command line:

```bash
python scripts/generate_image.py \
  --profile relay \
  --prompt "A clean isometric illustration of an image API"
```

#### Configuration Priority

1. Command-line values: `--api-key`, `--model`, `--base-url`, `--endpoint`
2. Selected profile values: `IMAGEGEN_PROFILE_<NAME>_*`
3. Global values: `IMAGEGEN_API_KEY`, `IMAGEGEN_MODEL`, `IMAGEGEN_BASE_URL`
4. Default base URL: `https://api.openai.com`

For provider details, URL handling, model listing, and response formats, see [references/configuration.md](references/configuration.md).

### Use In Codex

Standard usage:

```text
Use $iga to generate an image: a minimal black-and-white icon set for an AI image API.
```

With a named profile:

```text
Use $iga with profile relay to generate an image: a soft watercolor mountain village at sunrise.
```

With more specific output requirements:

```text
Use $iga to generate an image: a square app icon, glassmorphism style, transparent background, high detail.
```

### Command-Line Usage

Run the script directly:

```bash
python scripts/generate_image.py \
  --prompt "A cinematic product photo of a translucent keyboard" \
  --output outputs/keyboard.png
```

Common options:

| Option | Purpose |
| --- | --- |
| `--prompt` | Image prompt |
| `--profile` | Select a named profile from `.env` |
| `--model` | Override `IMAGEGEN_MODEL` |
| `--api-key` | Override the API key from environment variables |
| `--base-url` | API root URL, `/v1` URL, or full endpoint |
| `--endpoint` | Override the request path for non-standard providers |
| `--size` | Image size, default `1024x1024` |
| `--output` | Output file path |
| `--extra-json` | Merge extra provider-specific request fields |
| `--list-profiles` | List configured profiles without printing secrets |
| `--list-models` | Query model ids exposed by the configured service |
| `--show-paths` | Inspect resolved skill, script, `.env`, and working-directory paths |

Show resolved paths:

```bash
python scripts/generate_image.py --show-paths
```

List configured profiles:

```bash
python scripts/generate_image.py --list-profiles
```

List provider models:

```bash
python scripts/generate_image.py --profile relay --list-models
```

### Image Output

- Without `--output`, images are saved under `outputs/` in the current working directory.
- With `--output`, the script writes to the path you provide; relative paths resolve from the current working directory.
- The project no longer maintains a skill-local image history and does not track generated images.

### Project Structure

```text
.
├── SKILL.md                    # Codex skill instructions and execution rules
├── README.md                   # User-facing documentation
├── .env.example                # Local configuration template without real secrets
├── agents/
│   └── openai.yaml             # Codex display metadata
├── references/
│   └── configuration.md        # Advanced configuration and troubleshooting
└── scripts/
    └── generate_image.py       # OpenAI-compatible image API script
```

### Security

- Do not commit a real `.env` file or API keys.
- `.env.example` should contain placeholders only and is safe to commit.
- Prompts, model names, and request parameters are sent to your configured API provider or relay.
- This project includes no telemetry, analytics, or additional callbacks.

### Troubleshooting

`Missing API key`

Make sure `.env` contains `IMAGEGEN_API_KEY`, or that the selected profile defines `IMAGEGEN_PROFILE_<NAME>_API_KEY`.

`Missing model`

Make sure `.env` contains `IMAGEGEN_MODEL`, or that the selected profile defines `IMAGEGEN_PROFILE_<NAME>_MODEL`.

`model_not_found`

Run `--list-models` to inspect the model ids actually exposed by the service, then use the exact id returned by the provider.

`Profile '<name>' is not configured`

Run `--list-profiles` to check the configured profile names. Profile names in environment variables are uppercased and non-alphanumeric characters are converted to underscores.

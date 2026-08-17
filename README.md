# ImageGen API (`$iga`)

[中文](#中文) | [English](#english)

---

## 中文

`$iga` 是一个轻量级 Codex 生图 skill。它内置 OpenAI-compatible adapter，适用于 `/v1/images/generations` 风格的图片生成接口，也可以后续扩展其他厂商的 provider adapter。

### 安装

克隆到 Codex skills 目录：

```bash
git clone <your-repo-url> ~/.codex/skills/iga
```

Windows PowerShell：

```powershell
git clone <your-repo-url> "$env:USERPROFILE\.codex\skills\iga"
```

安装后重启 Codex。

### 配置

在 skill 目录复制示例配置：

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

### 使用

在 Codex 中直接调用：

```text
Use $iga to generate an image: a clean isometric illustration of an image API, white background, high detail.
```

也可以直接运行脚本：

```bash
python scripts/generate_image.py \
  --prompt "A cinematic product photo of a translucent keyboard" \
  --output outputs/keyboard.png
```

### 图片保存

默认生成图片会保存到“当前实际执行的那份 skill”的 `outputs/` 目录，方便找回。仓库保留 `outputs/.gitkeep`，真实图片会被 `.gitignore` 忽略。

查看实际路径：

```bash
python scripts/generate_image.py --show-paths
```

列出已保存图片：

```bash
python scripts/generate_image.py --list-outputs
```

清理已保存图片：

```bash
python scripts/generate_image.py --clean-outputs
```

提醒：`--clean-outputs` 会不可恢复地删除 `outputs/` 中的图片。

### 常用参数

- `--prompt`：图片提示词。
- `--model`：模型名；默认读取 `IMAGEGEN_MODEL`。
- `--api-key`：API key；建议使用 `.env`。
- `--base-url`：API base URL 或完整图片生成 endpoint。
- `--size`：图片尺寸，默认 `1024x1024`。
- `--output`：输出路径；未指定时保存到 skill 本地 `outputs/`。
- `--extra-json`：传入服务商支持的额外 JSON 字段。
- `--list-models`：查询当前服务暴露的模型 id。

### 安全说明

- 不要提交真实 `.env` 或 API key。
- `.env.example` 只放占位值，可以提交。
- Prompt、模型名和请求参数会发送给你配置的 API 服务商或中转站。
- 本项目不包含遥测、统计或额外回传逻辑。

---

## English

`$iga` is a lightweight Codex image-generation skill. It includes a built-in OpenAI-compatible adapter for `/v1/images/generations` style APIs, and can be extended with provider adapters for other native image APIs.

### Install

Clone this repository into your Codex skills directory:

```bash
git clone <your-repo-url> ~/.codex/skills/iga
```

Windows PowerShell:

```powershell
git clone <your-repo-url> "$env:USERPROFILE\.codex\skills\iga"
```

Restart Codex after installation.

### Configure

Copy the example environment file inside the skill directory:

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

`IMAGEGEN_BASE_URL` may be left empty to use `https://api.openai.com`. It may also be a relay root URL, a `/v1` URL, or a full `/v1/images/generations` endpoint.

### Usage

Call the skill from Codex:

```text
Use $iga to generate an image: a clean isometric illustration of an image API, white background, high detail.
```

You can also run the script directly:

```bash
python scripts/generate_image.py \
  --prompt "A cinematic product photo of a translucent keyboard" \
  --output outputs/keyboard.png
```

### Image Storage

Generated images are saved by default in the `outputs/` directory of the skill copy that is actually executed. The repository keeps `outputs/.gitkeep`; real image files are ignored by `.gitignore`.

Show the active paths:

```bash
python scripts/generate_image.py --show-paths
```

List saved images:

```bash
python scripts/generate_image.py --list-outputs
```

Clean saved images:

```bash
python scripts/generate_image.py --clean-outputs
```

Reminder: `--clean-outputs` permanently deletes images in `outputs/`.

### Common Options

- `--prompt`: Image prompt.
- `--model`: Model name; defaults to `IMAGEGEN_MODEL`.
- `--api-key`: API key; `.env` is recommended.
- `--base-url`: API base URL or full image-generation endpoint.
- `--size`: Image size, default `1024x1024`.
- `--output`: Output path; defaults to the skill-local `outputs/` directory.
- `--extra-json`: Extra JSON fields supported by your provider.
- `--list-models`: Query model ids exposed by the configured service.

### Security

- Do not commit a real `.env` or API keys.
- `.env.example` should contain placeholders only and is safe to commit.
- Prompts, model names, and request parameters are sent to the configured API provider or relay.
- This project does not include telemetry, analytics, or additional callbacks.

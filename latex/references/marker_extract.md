# marker_extract.py 使用说明

> 目标：用脚本**稳定、可控**地从 PDF 提取：正文（Markdown/HTML/JSON）、图片、公式（LaTeX）、参考文献（txt + 自动生成 bib）。支持 **本地深度学习管线** 与 **LLM 辅助增强**（OpenAI-compatible：openai / deepseek / chatanywhere / ollama / openrouter）。

## 目录

- 0. 关键心智模型（路径、输出结构、LLM 的“真的用上了吗”）
- 1. 环境要求
- 2. 输出与目录结构规则
- 3. 最常用命令（建议复制）
- 4. 参数速查与解释
- 5. 自动识别与默认策略
- 6. 日志阅读与排错

------

## 0. 关键心智模型（路径、输出结构、LLM 的“真的用上了吗”）

### 0.1 脚本位置 vs 处理对象位置

- `marker_extract.py` 是一个**可直接运行的 Python 脚本**，你可以在任何工作目录调用它。
- **仅支持单个 PDF 文件**输入；目录输入会直接报错。

**建议：**在 Codex 工作流里，优先使用绝对路径，降低 CWD 变化造成的路径误判（与 compile.md 同理）。

### 0.2 输出目录是“根”，每个 PDF 一个子目录

脚本会把每个 PDF 的产物放到：

- `<output_root>/<pdf_stem>/...`（pdf_stem 为不含扩展名的文件名）

### 0.3 “确保使用的是 LLM，而不是纯本地”

- 只有你显式加 `--use_llm`，并且 provider 配置成功注入到 Marker 的 OpenAIService 后，脚本才会启用 LLM 相关处理链。
- 没加 `--use_llm`：默认走本地深度学习/传统管线（速度与质量取决于设备与 OCR/表格等组件）。

------

## 1. 环境要求

### 1.1 Python

- 建议：Python 3.10+（与你实际运行脚本的环境一致即可）

### 1.2 关键依赖

- 必需：`marker-pdf`（建议通过 `pip install -U marker-pdf` 安装到你实际运行脚本的环境里）
- 其他：脚本内部会用到 `Pillow`（保存图像）、`requests`（探测 Ollama tags）等能力。

### 1.3 macOS / Apple Silicon 注意点（M1 Pro）

- 你看到的日志 `TableRecEncoderDecoderModel is not compatible with mps backend. Defaulting to cpu instead` 属于上游模型/算子在 mps 上不兼容导致的降级；这意味着“整体可跑”，但某些子模块会退回 CPU（速度变慢是正常现象）。

------

## 2. 输出与目录结构规则

对每个 PDF，会生成（至少）：

- `document.md` / `document.html` / `document.json` / `document.chunks.json`（取决于 `--output_format`）
- `metadata.json`：Marker 渲染对象的 json-safe dump（已做不可序列化对象处理，避免 PIL.Image 等导致崩溃）
- `images/`：抽取到的图片文件（并会尝试把 `document.md` 里的图片引用改写为 `images/<file>`）
- `equations.tex`：提取到的 block 公式（`$$...$$`），按顺序编号，尽可能标注页码（若拿不到页码，会自动不显示 `p.?`）
- `references.txt`：参考文献段落（启发式抽取 + 连续作者补全）
- `references.bib`：由 `references.txt` 自动粗解析生成的 BibTeX（质量取决于原始 references 规范性）
- `manifest.json`：本次抽取的文件清单、计数与 notes（包含是否启用 `no_tables`、LLM provider/url/model 等）

------

## 3. 最常用命令（建议复制）

> 下面示例均为绝对路径写法（与 compile.md 风格一致）。

### 3.1 本地默认（推荐起手式）

```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py "/abs/path/to/your.pdf" -o "/abs/path/to/marker_out" --torch_device mps
```

- `--torch_device mps` 仅影响 torch 设备选择；部分子模块仍可能因不兼容退回 CPU（属正常现象）。
- 无 LLM 时默认使用 `--torch_device mps`，一般不加 `--no_tables`（如需使用必须先征询用户）。
- **在权限受限环境（例如工具/沙盒执行）出现 `PermissionError` 时**，才禁用多进程：
```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py "/abs/path/to/your.pdf" -o "/abs/path/to/marker_out" --disable_multiprocessing --torch_device mps
```
- 抽取速度可能较慢（尤其是禁用多进程）。在自动化工具中运行时，**建议将超时放宽到约 40 分钟**。

### 3.2 启用 LLM（OpenAI）

```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py "/abs/path/to/your.pdf" -o "/abs/path/to/marker_out" --use_llm --provider openai
```

### 3.3 启用 LLM（ChatAnywhere / 中转）

```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py "/abs/path/to/your.pdf" -o "/abs/path/to/marker_out" --use_llm --provider chatanywhere
```

脚本还支持在交互式终端下选择 ChatAnywhere 的模型（不在 TTY 时用默认）。

### 3.4 启用 LLM（DeepSeek）

```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py "/abs/path/to/your.pdf" -o "/abs/path/to/marker_out" --use_llm --provider deepseek
```

### 3.5 启用 LLM（Ollama 本地）

```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py "/abs/path/to/your.pdf" -o "/abs/path/to/marker_out" --use_llm --provider ollama
```

- 脚本会**主动修复代理劫持 localhost**：在进程内设置 `NO_PROXY` 并清理 `http(s)_proxy`，避免 `127.0.0.1:11434` 超时/502。
- 未指定 `--model` 时，会自动从已安装模型里挑一个“更像本地的”（尽量排除 `*cloud*`）。

### 3.6 启用 LLM（OpenRouter）

```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py "/abs/path/to/your.pdf" -o "/abs/path/to/marker_out" --use_llm --provider openrouter
```

### 3.7 只列出 ChatAnywhere 可用模型（脚本内置列表）

```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py --list_chatanywhere_models
```

------

## 4. 参数速查与解释

### 4.0 速查表

| 参数                         | 类型/取值                                        | 默认       | 说明                                                         |
| ---------------------------- | ------------------------------------------------ | ---------- | ------------------------------------------------------------ |
| `input`                      | PDF 文件（单文件）                               | 必填       | **不支持目录**                                                |
| `-o/--output_dir`            | 路径                                             | `marker_v14_out` | 输出根目录。                                              |
| `--output_format`            | `markdown/json/html/chunks`                      | `markdown` | 主文档输出格式。                                             |
| `--page_range`               | 字符串                                           | `None`     | 0-based 页范围，如 `"0,5-10,20"`。                          |
| `--force_ocr`                | flag                                             | False      | 强制 OCR。                                                   |
| `--strip_existing_ocr`       | flag                                             | False      | 去掉已有 OCR 再做。                                          |
| `--paginate_output`          | flag                                             | False      | 输出按页分页（依赖 Marker 端实现）。                         |
| `--disable_image_extraction` | flag                                             | False      | 禁用图片抽取。                                               |
| `--redo_inline_math`         | flag                                             | False      | 尝试修正 inline math。                                       |
| `--block_correction_prompt`  | str                                              | `None`     | 传入 block 修正提示词。                                      |
| `--config_json`              | 路径                                             | `None`     | 额外 Marker config（JSON object），先加载再用 CLI 覆盖。     |
| `--no_tables`                | flag                                             | False      | 过滤掉 table 处理器（减少表格链路）。                        |
| `--torch_device`             | `mps/cpu/...`                                    | `None`     | 通过 `TORCH_DEVICE` 传递设备。                               |
| `--disable_multiprocessing`  | flag                                             | False      | 禁用 pdftext 多进程（等价于 `pdftext_workers=1`）。          |
| `--refs_mode`                | `strict/balanced/loose`                          | `balanced` | 参考文献抽取松紧度。                                         |
| `--eq_source`                | `auto/markdown/rendered`                         | `auto`     | 公式来源：优先 rendered_dump（可拿页码），否则 markdown。    |
| `--use_llm`                  | flag                                             | False      | 启用 LLM 增强处理（表格/手写/标题等处理器可能调用 LLM）。    |
| `--provider`                 | `openai/deepseek/ollama/chatanywhere/openrouter` | `openai`   | LLM 后端。                                                   |
| `--url/--key/--model`        | str                                              | `None`     | 覆盖 provider 默认值。                                       |
| `--ollama_allow_cloud`       | flag                                             | False      | provider=ollama 时允许自动选择 `*:cloud` 远程模型。          |
| `--no_proxy_fix`             | flag                                             | False      | **禁用** NO_PROXY 修复（默认启用）。                          |
| `--list_chatanywhere_models` | flag                                             | False      | 打印 ChatAnywhere 模型列表后退出。                           |

------

## 5. 自动识别与默认策略

### 5.1 PDF 扫描

- **仅支持单文件**：目录输入会直接报错。

### 5.2 Ollama 自动策略

- 优先从 `http://127.0.0.1:11434/api/tags` 拉取模型列表；失败再 fallback 到 `ollama list`。
- 未指定 `--model` 时：尽量选“本地模型”（排除 `cloud`），并倾向小参数规模（8b/14b 优先）。

### 5.3 参考文献抽取策略（refs_mode）

- `strict`：依赖明确的 References 标题与格式特征
- `balanced`：默认；会在文档尾部窗口扫描寻找“像参考文献”的区域
- `loose`：更宽松；更可能“多抓”，也更可能引入正文尾部噪声
  （脚本内部通过 heading 匹配 + tail window scoring + continuation 合并实现）

------

## 6. 日志阅读与排错

### 6.1 `ModuleNotFoundError: No module named 'marker'`

含义：你运行脚本的 Python 环境里没有安装 marker。脚本会打印 `sys.executable` 用于自检。

处理：

```bash
pip install -U marker-pdf
```

### 6.2 metadata.json 写入失败 / “Object of type Image is not JSON serializable”

脚本已通过 `json_safe()` 做了 PIL.Image/bytes/Path 等对象的递归降级，正常情况下不应再因序列化崩溃。
若仍遇到：多半是上游结构变化/新类型对象；可把 `metadata.json` 附近的 ERROR 发我，我会按类型扩展 `json_safe()`。

### 6.3 Ollama 502 / 000 / 超时（最常见：代理劫持 localhost）

症状：

- `curl http://127.0.0.1:11434/...` 返回 502 / 超时
- 或 Marker 日志 `OpenAI inference failed: Error code: 502`

处理原则：

- 确保 `NO_PROXY` / `no_proxy` 包含 `localhost,127.0.0.1`
- 确保对 `ollama` 请求不要走 http(s)_proxy
  脚本已提供进程内修复 `_ensure_localhost_no_proxy()`，并会在 provider=ollama 时应用。

### 6.4 LLM 返回格式不符合预期（TableSchema/SectionHeaderSchema JSON 校验失败）

含义：Marker 的某些 LLM Processor 期待“严格 JSON”，但你的 LLM 端返回了 HTML、解释性文本或 Markdown code fence。常见于：

- 使用了不遵循 schema 的模型
- 或模型提示词被截断/风格不稳定

处理建议：

- 换更“指令遵循强”的模型（或显式换到 OpenAI/DeepSeek 更稳定的模型）
- 对表格：如果你不需要 LLM 表格增强，直接 `--no_tables` 可显著减少这类报错。

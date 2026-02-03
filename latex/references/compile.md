# compile.py 使用说明（v5）

> 目标：用脚本**稳定、可控**地编译单个或批量 LaTeX 工程。默认 **isolated（隔离构建）**，编译成功后只回写 PDF，避免污染工程目录。

## 目录
- 0. 关键心智模型（路径与工作目录）
- 1. 环境要求
- 2. 输出与临时目录规则
- 3. 最常用命令（建议复制）
- 4. 参数速查与解释
- 5. 自动识别规则
- 6. 日志阅读与排错
- 7. 习惯化封装（可选）

---

## 0. 关键心智模型（路径与工作目录）

### 0.1 脚本位置 vs 编译对象位置
- 脚本位置：`/Users/lingguiwang/.codex/skills/latex/scripts/compile.py`
- 编译对象（扫描根目录）由两种方式决定：
  1) 显式指定：`--path /abs/path/to/file_or_dir`
  2) 未指定 `--path`：**以当前工作目录（CWD）为扫描根**（可配合 `--recursive`）

**结论：**
- 不想依赖 CWD 时，务必使用 `--path`。
- 在 Codex 工作流中，建议**统一使用绝对路径**。

### 0.2 相对路径会发生什么？
- `--path`、`--output`、`--tmpdir` 会被脚本**绝对化**：相对路径按 CWD 拼接并 `resolve()`。
- 相对路径可用，但更容易因 CWD 变化而编错目录。**建议始终用绝对路径。**

---

## 1. 环境要求
- Python 3.10+
- TeX 发行版（TeX Live / MacTeX / TinyTeX）
- 可执行工具（脚本会自动探测）：
  - 引擎：`xelatex` / `lualatex` / `pdflatex`
  - 参考文献：`biber` / `bibtex`
- 可选但常见（视模板/宏包而定）：
  - `ghostscript (gs)`：当使用 `pstricks`、EPS/PS 转换等链路时可能被调用

---

## 2. 输出与临时目录规则

### 2.1 输出根目录 `<output_root>`
- 若指定 `--output /abs/out`：
  - PDF：`/abs/out/build_pdf/`
  - 日志：`/abs/out/build_logs/`
- 若不指定 `--output`：
  - `<output_root>` = **当前工作目录（CWD）**
  - PDF：`./build_pdf/`
  - 日志：`./build_logs/`

**建议：**在 Codex 中至少传 `--output "$PWD"`，保证输出位置可控。

### 2.2 输出文件命名
- PDF：`<jobname>__<hash>.pdf`
- log：`<jobname>__<hash>.log`

`<hash>` 用于区分不同目录下同名主文件，避免覆盖。

### 2.3 临时目录（v5）
- 若指定 `--tmpdir /abs/tmp`：
  - 临时目录在其下生成：`/abs/tmp/.tmp_latex/job_<hash>/...`
- 若不指定 `--tmpdir`：
  - 默认使用：`<output_root>/.tmp_latex/job_<hash>/...`

**用途：**
1) isolated 构建目录
2) 通过 `TMPDIR/TMP/TEMP` 传给子进程（xelatex/xdvipdfmx/gs 等），保证可写

**默认清理（v5）：**编译完成后**自动删除**临时目录（包含 `.tmp_latex`）。
- 需要保留现场：加 `--keep-tmpdir`。

**v5 要点：**
- `--tmpdir` 解决 macOS 上 Ghostscript 写 `/var/folders/...` 失败的问题。
- isolated 复制工程时会**忽略临时目录**（`.tmp_latex/.tmp` 及临时根目录），避免递归自复制。

---

## 3. 最常用命令（建议复制）

> 下面示例假设 CWD = 工程根目录。

### 3.1 批量编译当前目录
```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/compile.py \
  --output "$PWD"
```

### 3.2 只编译某个主文件（最稳妥）
```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/compile.py \
  --path "/abs/path/to/main.tex" \
  --output "/abs/path/to/project"
```

### 3.3 编译某个工程目录（自动挑选主文件）
```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/compile.py \
  --path "/abs/path/to/project_dir" \
  --output "/abs/path/to/project_dir"
```

### 3.4 macOS 推荐：显式指定 tmpdir（避免 Ghostscript 权限问题）
```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/compile.py \
  --path "/abs/path/to/project_dir_or_main.tex" \
  --output "/abs/path/to/project_dir" \
  --tmpdir "/abs/path/to/project_dir/.tmp"
```
> 默认编译后会删除临时目录；如需保留调试，加 `--keep-tmpdir`。

---

## 4. 参数速查与解释（v5）

### 4.0 速查表

| 参数 | 取值/类型 | 默认值 | 说明 |
|---|---|---|---|
| `--path` | 路径：`.tex` 或目录 | 必填 | 编译入口；目录会扫描入口 `.tex`（受 `--recursive` 影响）。 |
| `--output` | 路径：目录 | 必填 | 输出根目录；产物在 `<output>/build_pdf`、日志在 `<output>/build_logs`。 |
| `--tmpdir` | 路径：目录 | `None` | 可写临时目录根；macOS 上可规避 Ghostscript 写 `/var/folders/...` 失败。 |
| `--keep-tmpdir` | flag | `False` | 保留临时目录用于调试；默认编译结束清理。 |
| `--engine` | `auto` / `pdflatex` / `xelatex` / `lualatex` | `auto` | LaTeX 引擎选择；`auto` 会判断并回退。 |
| `--bib` | `auto` / `bibtex` / `biber` / `none` | `auto` | 参考文献链路选择；`auto` 会基于工程内容判断。 |
| `--build-mode` | `isolated` / `inplace` | `isolated` | 隔离构建 vs 原地构建。 |
| `--keep-intermediates` | bool | `False` | 是否保留中间文件（`.aux/.log/.toc/...`）。 |
| `--clean-on-fail` | bool | `False` | 失败时是否清理中间产物（更干净但不利排错）。 |
| `--max-runs` | int | `3` | LaTeX 最多重复运行次数（交叉引用稳定）。 |
| `--recursive` | bool | `True` | 当 `--path` 为目录时，是否递归查找入口 `.tex`。 |

**bool 参数写法**：`true/false`、`1/0`、`yes/no`、`y/n`（大小写不敏感）。

### 4.1 路径相关
- `--path <file_or_dir>`：建议当目录下有多个 `.tex` 时指向主 `.tex`，避免误编译。
- `--output <out_root>`：建议绝对路径，或在工程目录传 `--output "$PWD"`。
- `--tmpdir <tmp_root>`：
  - 规避 macOS Ghostscript 写系统临时目录失败
  - 将临时构建目录放到工程目录或高速磁盘

### 4.2 引擎与参考文献
- `--engine auto|pdflatex|xelatex|lualatex`
  - `auto` 会根据内容判断并回退尝试
  - 强制指定适用于模板对引擎有硬性要求

- `--bib auto|bibtex|biber|none`
  - `auto` 会根据 `biblatex` backend、`\bibliography` 等模式判断
  - `none` 适合排查与引用链路无关的问题

### 4.3 构建模式
- `--build-mode isolated|inplace`（默认 `isolated`）

**isolated（推荐）：**
- 复制工程到临时目录编译
- 成功后仅回写 PDF
- 更干净、可重复、避免污染工程目录
- v5 复制时忽略临时目录，避免递归自复制

**inplace：**
- 原地编译
- 适合依赖跨目录相对路径（如 `../fig/xxx.png`）的工程

### 4.4 其他控制
- `--keep-intermediates true|false`：保留中间文件
- `--keep-tmpdir`：保留隔离构建目录（调试用）
- `--clean-on-fail true|false`：失败时是否清理临时产物
- `--max-runs N`：重复运行次数上限
- `--recursive true|false`：目录扫描范围控制

---

## 5. 自动识别规则

### 5.1 目录扫描与目标选择（批量模式）
- 把 `.tex` 文件与“包含 `.tex` 的子目录”作为潜在目标
- 自动排除 `build_pdf/`、`build_logs/` 避免误编译产物目录

**建议：**只编译一个目标时，直接 `--path /abs/to/main.tex`。

### 5.2 主 `.tex` 选择（当 `--path` 为目录）
启发式规则（由高到低）：
- 含 `\documentclass` 且含 `\begin{document}`
- 文件名是 `main/master/paper/manuscript.tex`（不区分大小写）
- `\input/\include` 次数最多

若仍无法唯一确定，会报错并列出候选。此时请改为显式指定主文件。

---

## 6. 日志阅读与排错

### 6.1 排错流程（推荐）
1) 看终端汇总：成功/失败数量、每个目标的 `engine/bib/pdf/logs`
2) 打开日志：`<output_root>/build_logs/<jobname>__<hash>.log`
3) 常见问题定位：
   - 缺 `biber/bibtex`：先安装工具，再重试
   - `.sty` 找不到：TeX 包缺失或发行版过旧
   - 图片/表格找不到：检查 `\includegraphics{...}` 路径；isolated 下注意 `../` 跨目录依赖
   - 中文字体/ctex 警告：优先 xelatex/lualatex，并检查字体可用性

### 6.2 macOS 常见：Ghostscript 无法写系统临时目录
典型报错：
- `GPL Ghostscript ... Could not open temporary file /var/folders/...`
- `xdvipdfmx:fatal: ...`，最终 `No output PDF file written.`

处理建议：
1) 指定可写临时目录（默认会清理，调试加 `--keep-tmpdir`）
```bash
python /Users/lingguiwang/.codex/skills/latex/scripts/compile.py \
  --path "/abs/path/to/main.tex" \
  --output "/abs/path/to/project" \
  --tmpdir "/abs/path/to/project/.tmp"
```
2) 确认 `--tmpdir` 目录可写（必要时 `mkdir -p`）
3) 若工程依赖 `pstricks/EPS/PS`，确认已安装 `gs`

---

## 7. 习惯化封装（可选）

```bash
latexbuild () {
  python /Users/lingguiwang/.codex/skills/latex/scripts/compile.py \
    --path "$1" \
    --output "${2:-$1}"
}
# 用法：latexbuild /abs/path/to/project
#       latexbuild /abs/path/to/main.tex /abs/path/to/outroot
```

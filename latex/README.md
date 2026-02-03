# 12LaTex

面向「凌贵旺 / Guiwang Ling」的本地 LaTeX 工作流工具集（脚本位于 `scripts/`），用于：
- PDF → 结构化抽取（Marker）
- LaTeX 一键编译（自动选择引擎与参考文献工具）

本仓库默认使用**绝对路径**示例，便于直接复制运行。

## 目录结构

- `scripts/compile.py`：LaTeX 一键编译（支持目录扫描/自动选择引擎/日志输出）
- `scripts/marker_extract.py`：PDF 抽取（Marker Extract v14，支持可选 LLM 辅助）
- `plan/`：规划与过程日志（`task_plan.md`、`findings.md`、`progress.md`）
- `assets/`、`references/`：项目素材与参考资料（按需要使用）

## 环境与约定

### 1) help 彩色高亮（pycli-color）

`scripts/compile.py` 与 `scripts/marker_extract.py` 的 `-h/--help` 输出支持统一彩色高亮：
- 以 `-` 开头的选项 token（如 `-h`、`--engine`）→ **青色 + 加粗**
- metavar/占位符 token（全大写或包含 `_`，如 `PATH`、`OUTPUT_DIR`）→ **黄色 + 加粗**

颜色启用策略：
- 默认 auto：仅当 `sys.stdout.isatty()==True` 且 `TERM != dumb` 才启用颜色
- 若存在环境变量 `NO_COLOR`：强制禁用颜色
- 若 `FORCE_COLOR=1`：强制启用颜色（即便非 TTY）

注意：你的环境里常见默认存在 `NO_COLOR=1`，因此要“强制彩色”时通常需要同时**清空 NO_COLOR**：

```bash
NO_COLOR= FORCE_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/compile.py -h
NO_COLOR= FORCE_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/marker_extract.py -h
```

## 使用方法（最小示例）

### 1) LaTeX 一键编译：`scripts/compile.py`

查看帮助（无色 / 强制彩色）：

```bash
NO_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/compile.py -h
NO_COLOR= FORCE_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/compile.py -h
```

编译某个 `.tex`：

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/compile.py --path "/ABS/PATH/TO/main.tex"
```

编译某个目录（脚本会自动扫描并排除输出目录）：

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/compile.py --path "/ABS/PATH/TO/latex_project_dir"
```

### 2) PDF 抽取：`scripts/marker_extract.py`

查看帮助（无色 / 强制彩色）：

```bash
NO_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/marker_extract.py -h
NO_COLOR= FORCE_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/marker_extract.py -h
```

最小抽取（不使用 LLM）：

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/marker_extract.py \
  "/ABS/PATH/TO/paper.pdf" \
  -o "/ABS/PATH/TO/marker_out"
```

仅列出 ChatAnywhere 可用模型（无需传 PDF）：

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/marker_extract.py --list_chatanywhere_models
```

## 常见问题

### 1) 为什么 `FORCE_COLOR=1` 还是没颜色？

如果你的 shell/环境默认设置了 `NO_COLOR=1`，则会强制禁用颜色。请使用：

```bash
NO_COLOR= FORCE_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/compile.py -h
```


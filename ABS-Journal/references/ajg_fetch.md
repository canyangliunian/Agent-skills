# `scripts/ajg_fetch.py`（AJG/ABS 数据抓取与更新）

本文档用于指导在 **用户明确要求“更新/重新抓取/刷新 AJG/ABS 数据库”** 时，如何运行抓取脚本 `scripts/ajg_fetch.py`。  
**默认推荐流程不应调用此脚本**（推荐默认使用本地 `assets/data/` 数据）。

## 何时使用（严格触发条件）

- ✅ 用户明确提出：更新/重新抓取/刷新/更新数据库/更新ABS(AJG)数据/同步最新AJG列表
- ❌ 用户仅说：推荐投稿期刊/帮我选期刊/根据我的论文推荐目标期刊（此时走推荐脚本，不抓取）

## 前置条件：环境变量（必需）

抓取脚本只通过环境变量读取登录凭据：

- `AJG_EMAIL`
- `AJG_PASSWORD`

示例（请在你的 shell 中执行，避免把密码写进任何文件）：

```bash
export AJG_EMAIL="lingguiwang@yeah.net"
export AJG_PASSWORD="你的密码"
```

## 用法（以绝对路径为默认）

先确认帮助信息（与脚本参数保持一致）：

```bash
python3 /Users/lingguiwang/.agents/skills/abs-journal/scripts/ajg_fetch.py -h
```

### 推荐命令（写入 `assets/data/`）

```bash
python3 /Users/lingguiwang/.agents/skills/abs-journal/scripts/ajg_fetch.py \
  --outdir /Users/lingguiwang/.agents/skills/abs-journal/assets/data
```

## 参数说明（与 `-h` 输出一致）

- `--outdir OUTDIR`：**必填**，绝对路径输出目录
- `--mode {core}`：运行模式（当前仅 `core`）
- `--overwrite`：允许覆盖既有输出文件（默认不覆盖）
- `--debug-http`：输出更多 HTTP 调试信息（排查问题时使用）

## 输出文件（概要）

脚本会在 `--outdir` 下生成 AJG 数据文件（例如 JSON/CSV/JSONL 等）。  
具体文件名与字段契约请以 `references/ajg_data_contract.md` 为准。

## 建议：抓取后做离线校验（可选但推荐）

若你希望在不联网的情况下确认抓取结果完整且结构正确，可运行离线校验脚本：

```bash
python3 /Users/lingguiwang/.agents/skills/abs-journal/scripts/ajg_verify_outputs.py \
  --outdir /Users/lingguiwang/.agents/skills/abs-journal/assets/data
```

## 常见错误与排查

### 1) 缺少环境变量

现象：

- 报错提示缺少 `AJG_EMAIL / AJG_PASSWORD`

处理：

- 按“前置条件：环境变量”设置后重试。

### 2) 登录/验证码/访问受限

这类问题通常与网站风控、验证码、网络环境等有关。  
优先参考：`references/troubleshooting.md`。

# 09ABS（AJG 抓取 + 投稿期刊推荐）

本项目面向单一长期用户：凌贵旺（Guiwang Ling），用于：
1) 抓取 Chartered ABS Academic Journal Guide（AJG）最新年份期刊目录并落地到本地文件；
2) 基于本地 AJG 目录对论文进行投稿期刊推荐（skill：`ABS-Journal`）。

本仓库默认采用 **OpenSpec** 管理能力边界与规格（见 `openspec/specs/`），并通过 `openspec/changes/` 跟踪变更。

## 目录结构（约定）

- `scripts/`：抓取与通用脚本
- `assets/data/`：抓取落地的数据文件（示例：`ajg_2024_*.jsonl/.json/.csv`）
- `openspec/`：规格与变更工件

## 1. 抓取 AJG（`ajg-fetch`）

### 环境变量（不要把真实密码写进 git）

在终端设置：

```bash
export AJG_EMAIL="lingguiwang@yeah.net"
export AJG_PASSWORD="你的密码"
```

也可以参考示例文件：`scripts/ajg_config.example.env`。

### 运行（相对路径；基准为项目根目录）

```bash
python3 scripts/ajg_fetch.py \
  --outdir "$(pwd)/assets/data"
```

默认不覆盖既有输出文件；如需覆盖：

```bash
python3 scripts/ajg_fetch.py \
  --outdir "$(pwd)/assets/data" \
  --overwrite
```

### 主要输出

在 `--outdir` 指定目录下生成（年份会随最新 AJG 自动变化）：
- `ajg_<year>_journals_raw.jsonl`
- `ajg_<year>_meta.json`
- `ajg_<year>_journals_core_custom.csv`

### 常见失败与排查

- **缺少环境变量**：脚本默认从环境变量读取登录凭据。请检查 `AJG_EMAIL` / `AJG_PASSWORD` 是否已在当前终端导出，例如：
  - `export AJG_EMAIL="lingguiwang@yeah.net"`
  - `export AJG_PASSWORD="你的密码"`
  - 也可参考示例文件：`scripts/ajg_config.example.env`（不要把真实密码写进 git）
- **登录后仍被 gate 拦截**：可能需要验证码/权限不足，脚本会报错退出并写入 `progress.md` 便于诊断。
- **无法发现最新年份链接**：说明入口页结构变更，需要更新解析逻辑（见 `discover_latest_year_and_url()`）。
- **无法自动定位数据接口**：脚本会提示“需要进一步人工抓包或增加解析逻辑”，此时需要根据网页实际变化更新探测规则。

### 离线校验（不联网）

```bash
python3 scripts/ajg_verify_outputs.py \
  --outdir "$(pwd)/assets/data"
```

## 2. 投稿期刊推荐（skill：`ABS-Journal`）

该推荐 **仅依赖本地 AJG CSV**（默认：`assets/data/ajg_2024_journals_core_custom.csv`），不访问外网。

默认候选期刊来自固定 Field 白名单（AJG CSV 的 `Field` 列；共 5 个 Field，其中 `REGIONAL STUDIES, PLANNING AND ENVIRONMENT` 是一个整体 Field 名称）：
`ECON, FINANCE, PUB SEC, REGIONAL STUDIES, PLANNING AND ENVIRONMENT, SOC SCI`。
如需只看某个领域（例如只 ECON），请显式传 `--field_scope ECON`。
注意：`--field` 仅用于“论文领域标签/关键词配置”，不控制候选范围。

示例输出见：运行后生成的 `reports/ai_report.md`。

推荐脚本（混合模式示例；不联网）：

```bash
python3 scripts/abs_journal.py \
  recommend \
  --field_scope "ECON,FINANCE,PUB SEC,REGIONAL STUDIES, PLANNING AND ENVIRONMENT,SOC SCI" \
  --title "你的论文标题" \
  --abstract "你的论文摘要（可选）" \
  --mode medium \
  --topk 10 \
  --rating_filter "1,2,3" \
  --hybrid \
  --export_candidate_pool_json "candidate_pool.json" \
  --auto_ai

# 运行产出（固定输出目录：reports/）
# - reports/candidate_pool_easy.json, reports/candidate_pool_medium.json, reports/candidate_pool_hard.json
# - reports/ai_output.json
# - reports/ai_report.md
```

## OpenSpec

- 主规格基线：`openspec/specs/`
- 变更工作区：`openspec/changes/`

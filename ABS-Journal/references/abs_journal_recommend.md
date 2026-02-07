# 投稿期刊推荐（基于本地 AJG 数据）

本文档用于指导默认的“**不更新数据库**”投稿期刊推荐流程：  
推荐脚本会读取本地 AJG 核心 CSV（默认在 `assets/data/`），并输出推荐结果。

## 何时使用（默认路径）

- ✅ 用户说：帮我推荐投稿期刊/目标期刊/根据论文选期刊/给出 easy/medium/hard 的推荐
- ✅ 用户没有明确要求更新数据库（此时必须只用本地数据）

## 不做什么（强约束）

- ❌ 不自动联网更新 AJG/ABS 数据库  
  只有用户明确要求更新时，才运行 `scripts/ajg_fetch.py` 写入 `assets/data/`。

## 用法（以绝对路径为默认）

优先使用统一 CLI：`scripts/abs_journal.py`。

先确认帮助信息（与脚本参数保持一致）：

```bash
python3 scripts/abs_journal.py recommend -h
```

## 工作流程

当你希望 **easy/medium/hard 三个难度都先过“主题贴合候选集”**，再让 AI 在候选池内精挑 Top10，并输出固定列：

`序号 | 期刊名 | ABS星级 | 期刊主题`

### 用户偏好（可直接写进 AI 提示）

- 方向优先：贸易 / 农经 / 区经 / 金融 / 政策 / 政治经济
- 尽量少：纯计量 / 纯统计 / 纯方法类期刊（除非确实最贴题且候选池内无更好替代）

### Step 1：生成候选池 JSON（不联网）

分别为三类难度生成候选池（便于套用用户的星级约束，例如 easy=1/2、medium=1/2/3、hard=3/4/4*）：

```bash
python3 scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode easy \
  --topk 10 \
  --hybrid \
  --export_candidate_pool_json "reports/candidate_pool_easy.json"
  
python3 scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode medium \
  --topk 10 \
  --hybrid \
  --export_candidate_pool_json "reports/candidate_pool_medium.json"

python3 scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode hard \
  --topk 10 \
  --hybrid \
  --export_candidate_pool_json "reports/candidate_pool_hard.json"
```

### Step 2：把候选池交给 AI 二次筛选（模板）

提示模板在：

- `scripts/ai_second_pass_template.md`

**硬约束**：AI 只能输出候选池中 `journal` 字段出现过的期刊名。

### Step 3：保存 AI 输出 JSON，并做子集校验 + 生成固定列报告

AI 输出 JSON 约定（必须包含三组且各 ≥ TopK=10）：

```json
{
  "easy": [{"journal": "...", "topic": "..."}],
  "medium": [{"journal": "...", "topic": "..."}],
  "hard": [{"journal": "...", "topic": "..."}]
}
```

运行校验与报告生成（单次即可生成三模式固定列表格，仍然不联网）。相对路径基准：项目根（即包含 `SKILL.md` 的目录）；推荐产出统一写入 `reports/`。

```bash
python3 scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode medium \
  --topk 10 \
  --hybrid \
  --export_candidate_pool_json "candidate_pool.json" \
  --ai_output_json "ai_output.json" \
  --ai_report_md "ai_report.md"
```

注意：
- 若 AI 输出包含候选池之外的期刊名，校验会失败并提示具体条目，必须让 AI 重试（禁止悄悄替换）。
- 若缺少 easy/medium/hard 任一键，或任一组少于 TopK=10 条，或 topic 为空，将直接报错退出。
- `期刊主题` 为 AI 解释性摘要，用于解释与论文主题的匹配关系；不是期刊官方 Aims&Scope。
- 星级过滤（重要）：`--rating_filter` 留空时，脚本会按 mode 自动分层（easy=1,2；medium=2,3；hard=4,4*）。**显式传入** `--rating_filter` 会覆盖默认分层，可能导致三段星级过滤一致（不符合 easy/medium/hard 分层预期）。

重要说明（避免你这次发现的“又重新跑了一次 medium”的误解）：
- `--hybrid` 模式下，脚本会**一次性生成 easy/medium/hard 三个候选池**，文件名为：
  - `reports/candidate_pool_easy.json`
  - `reports/candidate_pool_medium.json`
  - `reports/candidate_pool_hard.json`
- Step 2/Step 3 的 AI 二次筛选与校验，应当分别在这三个候选池的范围内进行（即 easy 只能从 easy 池选，依此类推）。
- 如果你只把其中一个候选池（例如 easy 或 medium）交给 AI，那么 AI 输出的另外两组（medium/hard）会在子集校验时失败。

建议输出路径（固定输出目录：`reports/`，便于留存与复现）：
- 候选池：`reports/candidate_pool_easy.json` / `reports/candidate_pool_medium.json` / `reports/candidate_pool_hard.json`
- AI 输出：`reports/ai_output.json`
- 报告：`reports/ai_report.md`

## 参数说明（与 `-h` 输出一致）

根据 `-h` 输出，本脚本参数如下：

- `--title TITLE`：**必填**，论文标题
- `--abstract ABSTRACT`：可选，论文摘要
- `--mode {easy,medium,hard}`：投稿难度
  - `easy`：最容易（更稳妥/门槛更低的启发式）
  - `medium`：中等难度（折中）
  - `hard`：最困难（更偏高门槛/更“冲刺”）
- `--topk TOPK`：输出期刊数
- `--field FIELD`：论文领域标签/关键词配置（默认 `ECON`；不控制候选范围）
- `--field_scope SCOPE`：候选期刊 Field 白名单（AJG CSV 的 Field 列，逗号分隔；精确匹配）。为空则使用默认白名单：`ECON, FINANCE, PUB SEC, REGIONAL STUDIES, PLANNING AND ENVIRONMENT, SOC SCI`。
- `--rating_filter "1,2,3"`：AJG/ABS 星级过滤（逗号分隔，支持 `4*`）。注意：在混合推荐里，若留空则按 mode 自动分层；显式传入会覆盖默认分层。
- `--hybrid`：启用混合流程（只导出候选池/做校验/生成报告；不调用外部 API）
- `--export_candidate_pool_json PATH`：导出候选池 JSON（相对路径将写入 `reports/`）
- `--ai_output_json PATH`：AI 输出 JSON（相对路径将从 `reports/` 解析）
- `--ai_report_md PATH`：混合流程最终报告 Markdown 输出路径（相对路径将写入 `reports/`）

## 数据依赖（默认从本地读取）

默认推荐依赖本地数据文件（建议放在 `assets/data/`，例如 `assets/data/ajg_2024_journals_core_custom.csv`）。

如果你想用其它年份/自定义 CSV，用 `--ajg_csv` 指定其绝对路径即可。

## 常见错误与排查

### 1) 找不到 AJG CSV 或路径错误

处理：

- 优先把数据放到 `assets/data/`，或
- 使用 `--ajg_csv` 指定 CSV 的绝对路径。

### 2) 输出为空/推荐不合理

可能原因：

- `--field` 不匹配（例如你是管理学/金融方向但仍用 ECON）
- 摘要为空导致主题信息不足（可补充 `--abstract`）

更具体的排查建议见：`references/troubleshooting.md`。

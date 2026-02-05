# 投稿期刊推荐（基于本地 AJG 数据）

本文档用于指导默认的“**不更新数据库**”投稿期刊推荐流程：  
推荐脚本会读取本地 AJG 核心 CSV（默认在 `assets/data/`），并输出推荐结果。

## 何时使用（默认路径）

- ✅ 用户说：帮我推荐投稿期刊/目标期刊/根据论文选期刊/给出 easy/fit/value 的推荐
- ✅ 用户没有明确要求更新数据库（此时必须只用本地数据）

## 不做什么（强约束）

- ❌ 不自动联网更新 AJG/ABS 数据库  
  只有用户明确要求更新时，才运行 `scripts/ajg_fetch.py` 写入 `assets/data/`。

## 用法（以绝对路径为默认）

优先使用统一 CLI：`scripts/abs_journal.py`。

先确认帮助信息（与脚本参数保持一致）：

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/scripts/abs_journal.py recommend -h
```

### 最常用：按主题匹配（fit）

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode fit \
  --topk 20
```

### 星级过滤（可选）

按用户偏好限制 ABS/AJG 星级范围（逗号分隔，支持 `4*`）：

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode fit \
  --topk 20 \
  --rating_filter "1,2,3"
```

## 混合流程（脚本候选池 → AI 二次筛选 → 子集校验 → 固定列报告）

当你希望 **fit/easy/value 三类都先过“主题贴合候选集”**，再让 AI 在候选池内精挑 Top10，并输出固定列：

`序号 | 期刊名 | ABS星级 | 期刊主题`

### 用户偏好（可直接写进 AI 提示）

- 方向优先：贸易 / 农经 / 区经 / 金融 / 政策 / 政治经济
- 尽量少：纯计量 / 纯统计 / 纯方法类期刊（除非确实最贴题且候选池内无更好替代）

### Step 1：生成候选池 JSON（不联网）

下面示例生成候选池，并把候选池写到一个 JSON 文件（绝对路径）：

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode fit \
  --topk 10 \
  --rating_filter "1,2,3" \
  --hybrid \
  --export_candidate_pool_json "/tmp/candidate_pool_fit.json"
```

你也可以分别为三类生成候选池（便于套用用户的星级约束，例如 fit=1/2/3、easy=1/2、value=3/4/4*）：

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode easy \
  --topk 10 \
  --rating_filter "1,2" \
  --hybrid \
  --export_candidate_pool_json "/tmp/candidate_pool_easy.json"

python3 /Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode value \
  --topk 10 \
  --rating_filter "3,4,4*" \
  --hybrid \
  --export_candidate_pool_json "/tmp/candidate_pool_value.json"
```

### Step 2：把候选池交给 AI 二次筛选（模板）

提示模板在：

- `/Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/scripts/ai_second_pass_template.md`

**硬约束**：AI 只能输出候选池中 `journal` 字段出现过的期刊名。

### Step 3：保存 AI 输出 JSON，并做子集校验 + 生成固定列报告

AI 输出 JSON 约定（必须包含三组且各 ≥ TopK=10）：

```json
{
  "fit": [{"journal": "...", "topic": "..."}],
  "easy": [{"journal": "...", "topic": "..."}],
  "value": [{"journal": "...", "topic": "..."}]
}
```

运行校验与报告生成（单次即可生成三模式固定列表格，仍然不联网）。相对路径基准：项目根 `/Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal`。

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode fit \
  --topk 10 \
  --rating_filter "1,2,3" \
  --hybrid \
  --export_candidate_pool_json "assets/candidate_pool_fit.json" \
  --ai_output_json "assets/ai_output.json" \
  --hybrid_report_md "assets/hybrid_report.md"
```

注意：
- 若 AI 输出包含候选池之外的期刊名，校验会失败并提示具体条目，必须让 AI 重试（禁止悄悄替换）。
- 若缺少 fit/easy/value 任一键，或任一组少于 TopK=10 条，或 topic 为空，将直接报错退出。
- `期刊主题` 为 AI 解释性摘要，用于解释与论文主题的匹配关系；不是期刊官方 Aims&Scope。

建议输出路径（相对项目根，便于留存与复现）：
- 候选池：`assets/candidate_pool_fit.json`
- AI 输出：`assets/ai_output.json`
- 报告：`assets/hybrid_report.md`

## 参数说明（与 `-h` 输出一致）

根据 `-h` 输出，本脚本参数如下：

- `--title TITLE`：**必填**，论文标题
- `--abstract ABSTRACT`：可选，论文摘要
- `--mode {easy,fit,value}`：推荐模式
  - `easy`：偏“易发表”（更稳妥/门槛更低的启发式）
  - `fit`：偏“主题匹配”
  - `value`：偏“性价比”
- `--topk TOPK`：输出期刊数
- `--field FIELD`：论文领域（默认 `ECON`）
- `--rating_filter "1,2,3"`：AJG/ABS 星级过滤（逗号分隔，支持 `4*`）
- `--hybrid`：启用混合流程（只导出候选池/做校验/生成报告；不调用外部 API）
- `--export_candidate_pool_json PATH`：导出候选池 JSON（绝对路径）
- `--ai_output_json PATH`：AI 输出 JSON（绝对路径）
- `--hybrid_report_md PATH`：混合流程最终报告 Markdown 输出路径（绝对路径）

## 数据依赖（默认从本地读取）

默认推荐依赖本地数据文件（建议放在）：

- `/Users/lingguiwang/.agents/skills/abs-journal/assets/data/ajg_2024_journals_core_custom.csv`

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

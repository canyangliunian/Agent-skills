# `scripts/abs_journal_recommend.py`（基于本地 AJG 数据的投稿期刊推荐）

本文档用于指导默认的“**不更新数据库**”投稿期刊推荐流程：  
`scripts/abs_journal_recommend.py` 会读取本地 AJG 核心 CSV（默认在 `assets/data/`），并输出推荐结果。

## 何时使用（默认路径）

- ✅ 用户说：帮我推荐投稿期刊/目标期刊/根据论文选期刊/给出 easy/fit/value 的推荐
- ✅ 用户没有明确要求更新数据库（此时必须只用本地数据）

## 不做什么（强约束）

- ❌ 不自动联网更新 AJG/ABS 数据库  
  只有用户明确要求更新时，才运行 `scripts/ajg_fetch.py` 写入 `assets/data/`。

## 用法（以绝对路径为默认）

先确认帮助信息（与脚本参数保持一致）：

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/09ABS/scripts/abs_journal_recommend.py -h
```

### 最常用：按主题匹配（fit）

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/09ABS/scripts/abs_journal_recommend.py \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode fit \
  --topk 20
```

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
- `--ajg_csv AJG_CSV`：AJG 核心 CSV 绝对路径（可覆盖默认本地路径）

## 数据依赖（默认从本地读取）

默认推荐依赖本地数据文件（建议放在）：

- `/Users/lingguiwang/Documents/Coding/LLM/09ABS/assets/data/ajg_2024_journals_core_custom.csv`

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


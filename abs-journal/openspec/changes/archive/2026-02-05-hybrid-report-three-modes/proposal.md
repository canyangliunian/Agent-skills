## Why

Current混合推荐流程未按要求输出固定列 Markdown（“序号 | 期刊名 | ABS星级 | 期刊主题”），且未同时汇报 fit/easy/value 三种模式各 10 篇，导致用户需要手工拼装，降低可复用性与合规性。

## What Changes

- 增强混合推荐报告，生成单一 Markdown 文件，包含 fit、easy、value 三组各 10 篇的固定列表格。
- 固定列格式：`序号 | 期刊名 | ABS星级 | 期刊主题`，并确保候选池子集校验仍生效。
- 为 AI 二次输出增加模式标识与模板校验，避免缺列或越界期刊。
- 补充本地脚本与模板的使用说明，明确输出路径与示例命令。

## Capabilities

### New Capabilities
- `hybrid-report-multi-modes`: 生成包含 fit/easy/value 三组 Top10 的固定列 Markdown 报告，列格式统一。
- `ai-output-template-guard`: 定义并校验 AI 二次筛选 JSON 结构，确保含模式字段、Topic 文本且均在候选池内。

### Modified Capabilities
- `journal-recommendation`: 扩展现有推荐流程以同时产出三模式报告，修正未按固定列输出的问题。

## Impact

- 代码：`scripts/abs_journal.py`, `scripts/abs_ai_review.py`, 相关模板/提示文件（如 `scripts/ai_second_pass_template.md`）。
- 数据：继续使用本地 AJG CSV，不改变数据源。
- 文档：参考 `references/abs_journal_recommend.md` 增补示例与说明。***

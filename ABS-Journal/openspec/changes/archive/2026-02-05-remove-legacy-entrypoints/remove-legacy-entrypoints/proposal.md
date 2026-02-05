## Why

当前仓库的推荐能力已切换为**混合模式**（脚本先生成“主题贴合候选池/粗筛”，再由 AI 仅在候选池内挑选 fit/easy/value 三类 Top10，并通过子集校验与固定列报告输出）。但仓库内仍残留旧入口与文档引用（例如 `abs_journal_recommend.py`），会误导后续维护者/使用者走回“纯脚本直出”路径，破坏一致性与可复现性。

## What Changes

- **BREAKING**：删除旧流程入口脚本 `scripts/abs_journal_recommend.py`（仅保留混合模式入口 `scripts/abs_journal.py recommend --hybrid ...`）。
- 将仓库内所有对 `abs_journal_recommend.py` 的引用替换为混合模式入口与步骤（候选池 JSON → AI 输出 JSON → 子集校验 → 固定列三段 Top10 报告）。
- 同步清理 OpenSpec 规格/归档变更工件中对旧入口的引用（保持一致性，避免“历史文档误导当前使用方式”）。
- 保持“默认不联网更新 AJG 数据库；只有用户明确要求才更新”的既有强约束不变。

## Capabilities

### New Capabilities
- `remove-legacy-entrypoints`: 从仓库层面移除旧入口与引用，确保“仅混合模式”工作流成为唯一推荐路径（含文档与 OpenSpec 规格一致性）。

### Modified Capabilities
- `abs-skill-package`: 更新现有规格描述，去除旧入口脚本引用，改为混合模式流程与相关脚本（候选池导出/子集校验/固定列报告）。

## Impact

- 受影响代码：
  - 删除：`scripts/abs_journal_recommend.py`
  - 文档引用修订：`README.md`、`assets/recommendation_example.md`、`references/abs_journal_recommend.md`、以及 `openspec/specs/**` 与 `openspec/changes/archive/**` 中残留引用。
- 对外行为：
  - 用户将只看到混合模式用法；推荐输出的最终形态为三段固定列表格（fit/easy/value）。
  - 旧入口命令将不再可用（BREAKING），但新的入口已覆盖同一需求且更符合当前工作流。


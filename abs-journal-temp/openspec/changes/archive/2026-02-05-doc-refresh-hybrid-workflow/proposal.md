## Why

文档与示例仍含旧流程残留或表述不够统一，需要全面更新为“混合模式唯一入口”（脚本导出候选池 → AI 仅在候选池内筛选 → 子集校验 → 固定列报告），并按 writing-skills 的要求保持精简、可搜索、绝对路径示例。

## What Changes

- **更新** `SKILL.md`：触发条件与快速上手改为混合模式唯一入口，引用 references 而不内嵌细节。
- **更新** `references/abs_journal_recommend.md`：只描述混合模式步骤与命令链（候选池 JSON → AI 输出 JSON → 校验 → 报告），使用绝对路径。
- **更新** `README.md`：对外介绍只保留混合模式推荐用法（不再出现旧入口/纯脚本模式）。
- **清理残留**：确保仓库内不再出现旧流程表述或链接。

## Capabilities

### New Capabilities
- `docs-hybrid-refresh`: 文档与示例切换为混合模式唯一流程，并对齐 writing-skills（精简主文档，细节下沉 references）。

### Modified Capabilities
- `abs-skill-package`: 更新包内文档的一致性和触发条件表述，使之与当前实现和禁用旧入口的决策保持一致。

## Impact

- 文件：`SKILL.md`、`references/abs_journal_recommend.md`、`README.md`（仅本仓库）。
- 不改代码逻辑；仅文档与示例。保持“默认本地 AJG、不自动联网；显式更新才抓取”硬约束不变。

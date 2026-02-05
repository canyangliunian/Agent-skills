## ADDED Requirements

### Requirement: Remove legacy recommendation entrypoint
系统 MUST 删除旧推荐入口脚本 `scripts/abs_journal_recommend.py`，并确保仓库内不再将其作为可用入口进行引用或推荐。

#### Scenario: Legacy entrypoint is removed
- **WHEN** 用户或维护者在仓库中寻找推荐入口
- **THEN** 仓库 MUST 不再包含 `scripts/abs_journal_recommend.py` 文件

### Requirement: Replace all repository references to the legacy entrypoint
系统 MUST 在本仓库范围内替换对 `abs_journal_recommend.py` 的引用为混合模式工作流入口与步骤，覆盖普通文档与 OpenSpec 规格/归档工件。

#### Scenario: No textual references remain
- **WHEN** 在仓库根目录执行全文搜索 `abs_journal_recommend.py`
- **THEN** 搜索结果 MUST 为空（允许保留备份文件名或 git 历史，不计入工作区）

### Requirement: Keep hybrid workflow as the only recommendation path
系统 MUST 将推荐工作流收敛为混合模式：脚本导出候选池 JSON → AI 仅在候选池内输出 → 子集校验 → 三段固定列报告；文档与示例 MUST 不再暗示存在“纯脚本推荐模式”。

#### Scenario: Documentation points only to hybrid workflow
- **WHEN** 用户查看 README、示例与 references 文档
- **THEN** 推荐路径 MUST 使用 `scripts/abs_journal.py recommend --hybrid ...` 作为唯一入口，并包含候选池导出、AI 输出、子集校验与固定列报告生成步骤


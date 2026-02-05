## MODIFIED Requirements

### Requirement: Package provides stable local-first entrypoints
系统 SHALL 提供稳定入口脚本用于：
1) 显式更新 AJG 数据库（仅在用户明确要求时）；
2) 以**混合模式**推荐投稿期刊：脚本生成候选池 → AI 仅在候选池内二次筛选 → 子集校验 → 固定列三段 TopK 报告。

#### Scenario: Recommend journals via hybrid workflow
- **WHEN** 用户请求推荐投稿期刊（未要求更新数据库）
- **THEN** 系统 MUST 只使用本地 AJG CSV
- **AND THEN** 系统 MUST 先由脚本导出候选池 JSON（主题贴合候选集 + 星级过滤等约束）
- **AND THEN** AI MUST 仅在候选池内输出 `fit/easy/value` 三类 TopK，并包含 `期刊主题`
- **AND THEN** 系统 MUST 校验 AI 输出为候选池子集（禁止候选池外期刊）
- **AND THEN** 系统 MUST 生成固定列三段报告：`序号 | 期刊名 | ABS星级 | 期刊主题`

#### Scenario: Update database only when explicitly requested
- **WHEN** 用户明确提出更新/重新抓取/刷新数据库
- **THEN** 系统 MUST 使用 `AJG_EMAIL/AJG_PASSWORD` 从环境变量读取凭据
- **AND THEN** 系统 MUST 运行抓取脚本写入 `assets/data/`


## Why

当前项目已经有可用的核心脚本（如 `scripts/ajg_fetch.py`）与数据落地（如 `data/ajg_2024_meta.json`），但缺少一套“可复用、可验证、可演进”的规范来约束：功能边界是什么、输入/输出契约是什么、目录结构与命令接口如何稳定、数据格式如何保证兼容。随着后续要将“基于 AJG 目录推荐投稿期刊”的能力封装为 skill（并可能持续迭代），需要尽快引入 OpenSpec 规范，将需求、能力、设计与任务拆分为可追踪工件，降低维护成本与变更风险。

## What Changes

- 建立并落地一套 OpenSpec 驱动的项目规范化流程：以 capability/spec 为中心组织需求与验收标准，并将实现任务显式化。
- 定义并固化“AJG 抓取与数据落地”的输入/输出契约（环境变量、参数、输出文件命名、字段含义、失败模式与重试策略）。
- 定义并固化“期刊推荐（基于 AJG 目录）”的输入/输出契约（论文信息输入、推荐维度、排序逻辑、输出格式与可解释性要求），以支持未来封装为 `ABS-article` skill。
- 规范化项目目录与运行方式（脚本入口、数据目录、产出目录、日志/元数据），并补齐最小化的可验证检查（例如输出文件存在性与字段完整性）。
- 允许在必要时进行接口与目录结构调整（**BREAKING**）：若现有脚本参数、输出文件名或目录结构不利于长期演进，将在 specs/设计阶段明确并执行迁移方案。

## Capabilities

### New Capabilities

- `ajg-fetch`: 抓取 Chartered ABS Academic Journal Guide（AJG）最新年份目录，完成登录（如需要）、发现最新年份入口、全量抓取与本地落地，并输出可用于后续分析/推荐的数据文件与元数据。
- `journal-recommendation`: 基于已落地的 AJG 目录数据，结合用户提供的论文题目信息/摘要/引言/全文片段，按“主题匹配”“易发表”“性价比（ABS 等级 vs 分区）”等维度生成可解释的投稿期刊推荐结果，并支持封装为 skill 的稳定接口。
- `project-structure-openspec`: 将当前项目按 OpenSpec 的能力与规格进行组织：目录结构、命令入口、数据/产出约定、最小验证与变更记录（changes）流程。

### Modified Capabilities

<!-- 无现有 openspec/specs 能力需要修改（当前 openspec/specs 为空）。 -->

## Impact

- 代码影响：
  - `scripts/ajg_fetch.py` 将被纳入 `ajg-fetch` capability 的规范约束，可能需要补齐参数/输出一致性、错误处理与可验证性。
  - 后续的期刊推荐逻辑（目前尚未形成独立实现）将按 `journal-recommendation` capability 进行实现与接口约束。
- 数据与文件影响：
  - `data/` 下的输出文件命名（如 `ajg_<year>_*.jsonl/.json/.csv`）将被写入 specs，未来如需变更将视为 **BREAKING** 并提供迁移说明。
- 依赖影响：
  - `ajg_fetch.py` 当前设计为“stdlib only”，该约束将被显式写入 specs（除非在设计阶段明确引入第三方依赖并给出理由）。
- 外部系统影响：
  - 访问 `charteredabs.org` 可能涉及 gated 登录/验证码/页面结构变动；specs 将明确可接受的失败模式与降级策略（如无法登录时的错误提示与退出码）。


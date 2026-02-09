## 1. OpenSpec Baseline & Repo Hygiene

- [x] 1.1 盘点现有项目入口与目录（scripts/data/ABS-article/等），确认哪些属于本次 change 的实现范围
- [x] 1.2 在 `openspec/specs/` 下为已新增的 capabilities 建立“主 specs”（从 change specs 同步），形成长期规格基线
- [x] 1.3 增补最小化项目运行说明（README 或等价文档）：绝对路径示例、环境变量、常见失败与排查

## 2. `ajg-fetch` Capability Implementation Alignment

- [x] 2.1 为 `scripts/ajg_fetch.py` 补齐/确认 CLI 契约：必选参数、默认值、help 文案与退出码（与 spec 对齐）
- [x] 2.2 输出目录处理：确保无法创建/不可写时给出明确错误，并以非零退出码退出（与 spec 对齐）
- [x] 2.3 输出文件契约校验：抓取成功后验证三类文件（jsonl/json/csv）均被写出，否则失败退出并提示
- [x] 2.4 meta.json 字段校验：确保包含抓取时间（UTC）、AJG 年份、来源 URL（或等价字段），并在缺失时失败或补齐
- [x] 2.5 失败模式梳理：对 gated/登录失败/年份发现失败/HTTP 重试耗尽等场景输出可诊断错误信息

## 3. Minimal Verification for `ajg-fetch`

- [x] 3.1 增加“离线/无网络”可运行的最小校验脚本（例如读取已生成文件并检查字段/表头），避免依赖真实抓取
- [x] 3.2 为校验脚本提供可重复运行方式与绝对路径示例（与项目默认绝对路径约束一致）

## 4. `journal-recommendation` Capability Scaffold (v1)

- [x] 4.1 定义推荐输入的结构化 schema（title/abstract/intro/fulltext 片段等）与参数接口（模式选择：主题/易发表/性价比）
- [x] 4.2 实现 v1 推荐骨架：读取 AJG 数据文件→构建候选集→按模式输出结构化推荐结果（含解释字段）
- [x] 4.3 缺失数据处理：当 AJG 数据文件缺失/不可读时返回明确错误与修复建议（与 spec 对齐）

## 5. `project-structure-openspec` Adoption

- [x] 5.1 统一目录约定：明确 scripts/data/outputs（如需要）与 changes/specs 的职责边界，并更新文档
- [x] 5.2 非破坏性策略：当输出文件已存在时，明确并实现一种安全策略（失败/改名/显式 overwrite 参数其一），并写入说明

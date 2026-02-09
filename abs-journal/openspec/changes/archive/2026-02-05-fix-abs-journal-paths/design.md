## Context

- 交付形态：`ABS-Journal` 已作为一个独立 skill 包被复制到 `~/.agents/skills/abs-journal`。
- 当前问题：skill 内多处文档/示例命令与部分脚本存在旧工程目录（例如 `/Users/lingguiwang/Documents/Coding/LLM/09ABS`）的硬编码绝对路径。
- 约束：
  - 仍需保持“默认只用本地 AJG CSV 推荐，不自动联网更新；只有显式更新意图才抓取”。
  - 示例命令默认使用绝对路径（符合使用习惯与现有规范）。
  - 脚本代码应可迁移：复制或移动 skill 目录后仍可运行（不要求固定在某个工程根目录）。

## Goals / Non-Goals

**Goals:**

- 消除脚本内对固定工程根目录的依赖：通过 `__file__` 推断 `SKILL_ROOT`（即 `scripts/..`）。
- 将文档示例命令中的旧绝对路径统一迁移为 `~/.agents/skills/abs-journal` 对应的绝对路径。
- 调整抓取脚本的进度/发现日志落盘位置，不再写到旧工程目录，而是写入 skill 自身目录（`plan/`），并确保目录不存在时自动创建。
- 最小验证：保证核心入口脚本 `-h` 可运行；本地推荐流程在默认数据存在时可输出结果。

**Non-Goals:**

- 不改变 AJG 抓取逻辑、字段契约、输出文件命名与内容结构。
- 不改变推荐算法/排序逻辑与输出 schema。
- 不引入新的外部依赖或配置系统（如 dotenv/配置文件层）。
- 不做“全局通用路径模板化”（例如同时适配多台机器/多用户路径）；本次仅保证“目录迁移后仍可用”。

## Decisions

1) **脚本内目录定位：使用 `__file__` 推断 skill 根目录**

- 选择：在需要定位 skill 资源（脚本/数据）的位置，引入：
  - `SKILL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))`
- 理由：
  - 与复制/移动目录的操作解耦；不依赖用户当前工作目录（CWD）。
  - 不需要额外依赖，且对 CLI 运行方式（直接 `python3 scripts/x.py` 或从任意目录调用）都稳健。
- 备选方案：
  - 环境变量指定根目录（如 `ABS_JOURNAL_ROOT`）：更灵活但增加用户心智负担，不符合“开箱即用”。
  - 相对路径依赖 CWD：易碎，不符合默认绝对路径与可迁移目标。

2) **文档示例：保持“绝对路径为默认”，但更新为新交付目录**

- 选择：将 `SKILL.md`、`references/*.md`、`assets/*.md` 中出现的旧目录前缀替换为 `/Users/lingguiwang/.agents/skills/abs-journal`。
- 理由：
  - 对目标长期用户（凌贵旺）而言，绝对路径可直接复制执行；同时与现有规范一致。
- 备选方案：
  - 文档改为相对路径 + base dir 说明：更通用，但与“默认绝对路径”规则冲突，且容易被用户在错误目录下执行。

3) **抓取日志落盘：写入 skill 自身 `plan/`**

- 选择：`scripts/ajg_fetch.py` 中 `append_progress/append_findings` 将日志写到 `SKILL_ROOT/plan/progress.md` 与 `SKILL_ROOT/plan/findings.md`，并 `os.makedirs(plan_dir, exist_ok=True)`。
- 理由：
  - 避免把日志写入旧工程目录（迁移后失效）。
  - 与“文件式规划/记录”习惯兼容，且不污染 `assets/`。
- 备选方案：
  - 写到 `--outdir`：更贴近抓取输出，但会混入数据目录；且不利于长期记录“运行过程”。

## Risks / Trade-offs

- [仍有遗漏的旧路径引用] → 使用全库搜索旧前缀进行校验（例如 `rg "/Users/lingguiwang/Documents/Coding/LLM/09ABS"`），并在最小验证中覆盖关键入口。
- [`plan/` 自动创建在某些环境下不可写] → 该目录位于用户主目录下 skill 目录，通常可写；若不可写则在错误信息中提示权限/位置问题。
- [文档绝对路径过于用户绑定] → 该 skill 明确以单一长期用户为目标用户，接受此权衡；同时脚本通过 `__file__` 推断提升迁移鲁棒性。

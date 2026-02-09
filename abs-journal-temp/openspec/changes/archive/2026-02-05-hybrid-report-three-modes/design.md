## Context

- 现状：`scripts/abs_journal.py --hybrid` 可生成候选池并校验 AI 输出，但当前示例流水只产出单模式表格，且未强制固定列格式（序号 | 期刊名 | ABS星级 | 期刊主题）。`abs_ai_review.py` 仅校验候选池子集，未检查模式完备性或列齐备。
- 目标用户：本地使用者（凌贵旺），数据源固定为本地 AJG CSV，需避免联网更新。
- 约束：保持现有 CLI 兼容性；仍默认使用绝对路径；不改数据抓取逻辑；不触碰 ~/.agents 目录，先改本地仓库。

## Goals / Non-Goals

**Goals:**
- 在单次运行中产出含 fit/easy/value 三组各 10 篇的固定列 Markdown 报告。
- 表格列固定为“序号 | 期刊名 | ABS星级 | 期刊主题”，序号从 1 递增。
- 校验 AI 输出：必须为三模式 key，且每模式 ≥ topk（默认10）条，期刊名均在候选池内，topic 非空。
- 提供示例命令与输出路径说明，便于复现。

**Non-Goals:**
- 不调整 AJG 数据源或联网抓取流程。
- 不改推荐打分算法/候选池生成逻辑。
- 不改现有 CLI 参数命名（仅补充可选参数与输出）。

## Decisions

1) **报告生成位置与格式**  
   - 在 `abs_journal.py recommend --hybrid` 内，当提供 `--hybrid_report_md` 时，生成单文件报告，包含三段表格（fit/easy/value）。若缺失任一模式数据则报错终止。  
   - 表格使用 Markdown pipe 表头：`| 序号 | 期刊名 | ABS星级 | 期刊主题 |`；主题来自 AI 输出 `topic` 字段。

2) **AI 输出契约与校验强化**  
   - 扩展 `abs_ai_review.py`：校验 JSON 必含键 `fit`, `easy`, `value`；每组长度 >= `topk`；每条含 `journal`、`topic`；`journal` 必在候选池 `journal` 集内。  
   - 若校验失败，列出缺失模式/越界期刊/空 topic 具体行并退出非零。

3) **复用现有 CLI**  
   - 继续使用 `--export_candidate_pool_json` + `--ai_output_json` + `--hybrid_report_md` 三组合；为三模式运行仅需一轮（模式参数仍以 `--mode fit` 触发候选池生成，AI 输出携带三模式）。  
   - 在 `references/abs_journal_recommend.md` 增补示例命令，说明三模式报告生成方式。

4) **代码结构**  
   - 在 `abs_journal.py` 增加生成报告的函数，循环模式列表，渲染表格。  
   - 轻量依赖：仅使用标准库（json, pathlib, textwrap），不新增第三方。

## Risks / Trade-offs

- **风险：AI 输出不足 10 条或缺 topic** → 通过严格校验提前失败，提示用户补全。  
- **风险：用户仍按单模式 AI 输出** → 报错提示三模式缺失；在文档中强调模板。  
- **风险：兼容性** → 保持参数不变；若老流程不传三模式，会失败，需要在文档标注要求。  
- **Trade-off：一次运行生成三模式** → 牺牲对单模式宽容性换取一致性与合规输出。

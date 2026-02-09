## Context

仓库的期刊推荐已确定为“混合模式”工作流：

1) 脚本离线读取本地 AJG CSV；
2) 先构造“主题贴合候选池”（candidate pool），并支持按用户给定星级过滤（例如 fit=1/2/3、easy=1/2、value=3/4/4*）；
3) AI 仅允许在候选池内输出三类 TopK，并为每条补充解释性的 `期刊主题`；
4) 脚本校验 AI 输出必须是候选池子集（禁止候选池外期刊），并生成三段固定列 Markdown 报告：`序号 | 期刊名 | ABS星级 | 期刊主题`。

当前问题是：仓库内仍存在旧入口脚本 `scripts/abs_journal_recommend.py` 以及大量文档/规格引用，导致维护与使用时容易误走回旧流程。用户要求：仅针对本仓库清理，并且连 `openspec/specs/**` 与 `openspec/changes/archive/**` 的引用也要同步清理，保持一致。

## Goals / Non-Goals

**Goals:**
- 删除旧入口 `scripts/abs_journal_recommend.py`，确保推荐入口仅保留 `scripts/abs_journal.py recommend --hybrid ...`。
- 全仓库替换对旧入口的引用：README、assets 示例、references 文档、OpenSpec specs 与 archive 工件。
- 保持离线优先与“仅显式更新才抓取 AJG”不变。
- 清理后仍可一键运行混合流程（导出候选池 JSON、校验 AI 输出、生成固定列报告）。

**Non-Goals:**
- 不改变推荐打分/候选池算法（除非为兼容清理带来的引用变更所必需）。
- 不删除 AJG 抓取脚本与更新流程（仍按“用户显式要求才更新”保留）。
- 不对 `openspec/changes/archive/**` 进行历史语义重写；仅做字符串级引用修正以避免误导。

## Decisions

1) **删除旧入口而非保留兼容别名**
   - 选择：删除 `scripts/abs_journal_recommend.py`。
   - 原因：该入口的存在本身就是误导源；当前工作流已稳定为混合模式，且 `scripts/abs_journal.py` 已提供统一入口。
   - 备选：保留旧入口但改为转发到新入口（alias）。未选原因：仍会让用户误以为有“纯脚本模式”，不符合“仅混合模式”的目标。

2) **用混合模式链路作为文档唯一推荐路径**
   - 文档与示例统一使用：
     - `scripts/abs_journal.py recommend --hybrid --export_candidate_pool_json ...`
     - `--ai_output_json ... --hybrid_report_md ...`
   - 原因：减少分叉与歧义；与当前 `SKILL.md` 一致。

3) **OpenSpec 规格与归档材料做“引用一致性修订”**
   - 对 `openspec/specs/**` 与 `openspec/changes/archive/**` 中提及旧入口的文本，替换为新入口。
   - 原因：用户要求“保持一致”；避免未来查看规格/历史变更时被误导。

## Risks / Trade-offs

- [风险] 删除入口属于 BREAKING（旧命令不可用） → [缓解] 文档与 `SKILL.md` 提供完整替代命令；并在同一次变更中完成全局引用替换。
- [风险] archive 工件清理可能影响追溯原始上下文 → [缓解] 仅替换入口引用，不改动结论与主要内容；必要时保留 .bak（由 git 历史承担）。
- [风险] 漏改某处引用导致用户仍看到旧命令 → [缓解] `rg "abs_journal_recommend.py"` 全仓库扫描为验收条件，并加入回归脚本/命令验证。


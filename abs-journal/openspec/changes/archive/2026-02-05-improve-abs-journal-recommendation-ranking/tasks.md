## 1. 现状梳理与接口约束

- [x] 1.1 梳理 `scripts/abs_article_impl.py` 现有评分函数与输出字段（`keyword_score/easiness_score/prestige_penalty/total_score/render_report`）
- [x] 1.2 明确需要保持兼容的 CLI 入口与参数（`scripts/abs_journal.py recommend` 与 `scripts/abs_article_impl.py` 的 `--mode/--topk/--field/--title/--abstract`）
- [x] 1.3 记录当前推荐结果“只推 1★/只推 4★”的可复现实例（固定 title/abstract，保存输出片段到 `plan/` 或临时文件，便于回归对比）

## 2. Topic Fit Gating（候选集）实现

- [x] 2.1 抽取 `fit_score` 计算函数（基于现有 `keyword_score` 扩展/重命名为 `fit_score`，保证可解释与完全离线）
- [x] 2.2 设计并实现候选集构造策略（阈值/TopN/相对阈值二选一，或组合），并实现“候选过少回退”逻辑
- [x] 2.3 在代码中实现“所有模式统一先过候选集”的流程改造（Stage A: gating → Stage B: ranking）
- [x] 2.4 为 gating 增加可输出的元信息（阈值/TopN、候选规模、是否触发回退、回退方式）

## 3. 三种模式的排序重构（候选集内排序）

- [x] 3.1 重构 `fit` 模式排序：候选集内按 `fit_score` 为主排序键（必要时用次级键稳定排序）
- [x] 3.2 重构 `easy` 模式排序：候选集内以 `easy_score` 为主、`fit_score` 为次；评估是否保留/调整 prestige 惩罚以避免误判
- [x] 3.3 重构 `value` 模式排序：候选集内以 AJG 等级/星级价值指标为主、`fit_score` 为次，并保持必要的 prestige 惩罚
- [x] 3.4 处理“星级展示分桶”与“排序逻辑”的一致性（bucket 内排序与全局排序一致；说明文字明确“分桶是展示不是过滤”）

## 4. 输出可解释性增强（Markdown 报告）

- [x] 4.1 在表格中新增/展示 `fit_score` 列，并按模式展示 `easy_score` 或 `value_score`（或等价指标）
- [x] 4.2 在“说明”区域新增候选集说明（阈值/TopN、回退是否发生），并对“缺少摘要”场景增加提示
- [x] 4.3 确保输出字段与用词一致、可复核（例如列名 `FitScore/EasyScore/ValueScore` 或中文列名统一）

## 5. 可配置性与可维护性（可选但推荐）

- [x] 5.1 将关键词字典从代码中抽离为可配置文件（例如 `assets/keywords/*.json`）或新增 CLI 参数指定（仍需默认可用）
- [x] 5.2 为不同 field（例如 ECON）提供可扩展的关键词集合入口，不把主题绑定在硬编码词表上

## 6. 回归验证与基本测试

- [x] 6.1 增加最小回归测试脚本/用例：无摘要、短摘要、长摘要三种输入下均能产出 topk 且 gating 生效
- [x] 6.2 增加断言：`easy/value` 输出中所有期刊均来自候选集（低于阈值的不出现）
- [x] 6.3 对比改造前后输出，确认不再出现“明显不贴题但排前”的结果，并记录示例以便后续迭代

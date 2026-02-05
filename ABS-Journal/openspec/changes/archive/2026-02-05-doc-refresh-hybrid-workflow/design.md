## Context

- 当前实现与流程：仅保留混合模式推荐（脚本候选池 → AI 仅在候选池内筛选 → 子集校验 → 固定列报告），入口是 `scripts/abs_journal.py recommend --hybrid ...`。
- 存在的问题：
  - 文档（SKILL.md/README/references）仍有零散旧表述或不够聚焦混合模式；
  - 需要按 writing-skills 精简主文档，细节下沉 references，并保持绝对路径示例；
  - 需保证所有示例/引用与当前代码一致（不出现旧入口）。
- 约束：
  - 不修改代码逻辑，仅改文档与示例；
  - 保持“默认本地 AJG，不自动联网；显式要求才抓取”硬约束不变；
  - 绝对路径示例基于本仓库路径。

## Goals / Non-Goals

**Goals:**
- 文档统一为混合模式唯一入口，示例可直接复制运行。
- 主文档精简，细节挪到 references，符合 writing-skills（CSO 描述不含流程细节）。
- 清理残留旧表述，避免新旧混杂。

**Non-Goals:**
- 不改推荐算法/脚本参数。
- 不调整 AJG 抓取流程。

## Decisions

- 用绝对路径示例指向本仓库脚本（不指向家目录镜像）。
- SKILL.md 只保留触发条件与最小命令，其他细节链接到 references。
- references/abs_journal_recommend.md 成为混合流程的唯一细节文档（含三类模式、星级过滤、AI 提示、校验和报告步骤）。
- README.md 只展示混合模式用法，不再出现旧入口/纯脚本模式。

## Risks / Trade-offs

- 文档过长或重复 → writing-skills 要求压缩主文档、把细节下沉 references。
- 示例路径错误 → 全部使用本仓库绝对路径，完成后人工检查。
- 遗漏旧表述 → 全局 `rg "abs_journal_recommend.py"` 与“纯脚本”相关表述，更新后再跑一次检查。

## 1. 更新主文档（SKILL.md）

- [x] 1.1 精简 description：仅写触发条件（Use when...），不含流程细节
- [x] 1.2 Quick Start 仅保留混合模式命令链（候选池 → AI 输出 → 校验 → 报告），使用本仓库绝对路径
- [x] 1.3 References 区链接到详细文档，不在 SKILL.md 内内嵌参数细节

## 2. 更新 references 文档

- [x] 2.1 `references/abs_journal_recommend.md`：全面改为混合模式唯一流程，含三类星级过滤、AI 提示模板位置、校验与报告命令链（绝对路径）
- [x] 2.2 确保文档无 `abs_journal_recommend.py` 或“纯脚本模式”表述

## 3. 更新 README.md

- [x] 3.1 对外示例只展示混合模式命令链，删除/替换旧入口与纯脚本表述

## 4. 验证

- [x] 4.1 `rg "abs_journal_recommend.py"` 在仓库根返回 0
- [x] 4.2 主文档描述符合 writing-skills（描述不含流程细节，示例可直接运行）

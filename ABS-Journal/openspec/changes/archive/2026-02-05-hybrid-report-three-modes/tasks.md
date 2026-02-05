## 1. 校验与模板完善

- [x] 1.1 更新 `scripts/ai_second_pass_template.md`，明确需输出 fit/easy/value 三键、各含 journal/topic，不得缺列。
- [x] 1.2 在 `abs_ai_review.py` 增加三模式键存在性、TopK 长度、topic 非空、候选池子集校验。

## 2. 报告生成实现

- [x] 2.1 在 `abs_journal.py` 添加生成三模式单文件报告函数，固定表头并按序号输出。
- [x] 2.2 处理缺失模式或条目不足时的错误提示，退出非零。

## 3. 文档与示例

- [x] 3.1 更新 `references/abs_journal_recommend.md`，补充三模式单次运行示例命令与输出说明。
- [x] 3.2 提供生成报告的示例路径与文件名建议（/tmp/hybrid_report.md）。

## 4. 验证

- [x] 4.1 运行推荐脚本生成候选池与 AI 输出示例，确认三模式报告成功写出并表头正确。
- [x] 4.2 验证缺失模式/条目不足时报错路径和信息。

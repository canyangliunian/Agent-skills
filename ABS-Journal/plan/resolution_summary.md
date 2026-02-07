# CLI 输出格式统一问题 - 解决方案总结

## 问题描述
用户反馈期刊推荐的 CLI 输出格式不一致:
- A类和B类前5本: 使用文字分隔线格式 (────────)
- C类4星期刊: 使用表格格式 (┌──┬──┐)

## 根本原因分析

### 代码调查结果
经过完整代码探查,确认:

**✅ 源代码格式统一** (`hybrid_report.py`)
- 第 98-122 行: `render_table()` 函数
- 第 211-213 行: Easy/Medium/Hard 都调用相同函数
- 输出格式: 统一的 Markdown 表格

```python
def render_table(bucket_title: str, items: List[Dict[str, Any]],
                 idx: Dict[str, Dict[str, Any]], topk: int) -> str:
    lines.append("| 序号 | 期刊名 | ABS星级 | Field | 期刊主题 |")
    lines.append("|---:|---|---:|---|---|")
    # ... 所有行使用相同格式
```

**调用位置**:
```python
lines.append(render_table("Easy Top10", ai_norm["easy"], idx_multi.get("easy") or {}, topk))
lines.append(render_table("Medium Top10", ai_norm["medium"], idx_multi.get("medium") or {}, topk))
lines.append(render_table("Hard Top10", ai_norm["hard"], idx_multi.get("hard") or {}, topk))
```

### 问题真相
- ❌ **不是代码 bug** - 生成的 `ai_report.md` 格式完全统一
- ✅ **是呈现选择** - Claude 在向用户汇报时,主动使用了两种不同的格式化方式

## 解决方案

### 方案 A: 规范呈现方式 (已采用) ✅

**原则**:
- 代码无需修改
- `ai_report.md` 保持统一的 Markdown 表格格式
- 在向用户汇报时,严格按照源文件格式呈现

**实施要点**:
1. 所有三个难度级别使用相同的表格格式呈现
2. 不再混合使用文字分隔线和表格
3. 保持与 `ai_report.md` 源文件一致

**优势**:
- ✅ 无需修改任何代码
- ✅ 保持 `ai_report.md` 可被其他工具解析
- ✅ 呈现格式与源文件一致,易于对比

### 方案 B: 修改代码生成 ASCII 表格 (未采用)

**变更点**:
- 修改 `hybrid_report.py:render_table()` 函数
- 使用 `tabulate` 或 `rich` 生成 ASCII 边框表格
- 改变 `ai_report.md` 的格式

**缺点**:
- ❌ 改变源文件格式,可能影响其他工具
- ❌ 增加第三方依赖
- ❌ ASCII 表格在 Markdown 中不规范

## 验证清单

- [x] 确认 `hybrid_report.py` 所有难度级别使用统一函数
- [x] 确认 `ai_report.md` 源文件格式统一
- [x] 用户选择方案 A (规范呈现方式)
- [x] 更新规划文档记录决策

## 关键代码位置

**生成 Markdown 表格**:
- 文件: `/Users/lingguiwang/.claude/skills/abs-journal/scripts/hybrid_report.py`
- 函数: `render_table()` (第 98-122 行)
- 调用: `render_report()` (第 211-213 行)

**输出到终端**:
- 文件: `/Users/lingguiwang/.claude/skills/abs-journal/scripts/abs_journal.py`
- 位置: 第 239 行 - `print(render_report(pool, ai, topk=int(args.topk)))`

## 结论

**无需修改任何代码**。问题已通过明确呈现规范解决。

---

**解决时间**: 2026-02-08 03:57
**决策人**: 用户
**执行状态**: 已完成

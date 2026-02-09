## 1. Restructure Root As Single Skill (`ABS-Journal`)

- [x] 1.1 创建根目录的 `references/` 与 `assets/` 目录（保留现有 `scripts/` 与 `data/`）
- [x] 1.2 梳理并迁移现有 `ABS-article/` 内容：仅保留必要实现，其他示例/报告按需放入 `assets/` 或 `references/`
- [x] 1.3 清理或标记历史遗留目录与文件（如旧 skill 目录），避免重复入口；必要时提供兼容转发/提示（**BREAKING**）

## 2. Unify Script Entrypoints Under `scripts/`

- [x] 2.1 统一抓取入口：确认 `scripts/ajg_fetch.py` 作为“更新数据库”命令，并在帮助/README/SKILL.md 中明确仅在显式更新时运行
- [x] 2.2 统一推荐入口：将现有推荐脚本稳定为根目录 `scripts/` 下的入口（可复用现有实现，必要时薄封装），并默认读取本地 AJG CSV
- [x] 2.3 增加一个“控制流入口”脚本（可选）：根据用户意图选择“仅推荐”或“先更新再推荐”（保持默认不更新）

## 3. Write `SKILL.md` (Skill-creator / Writing-skills Driven)

- [x] 3.1 使用 `$skill-creator`/`$writing-skills` 生成根目录 `SKILL.md`（前言仅 name/description；正文强调默认本地推荐、显式更新才抓取）
- [x] 3.2 在 `SKILL.md` 中引用必要的 `references/` 文档与 `scripts/` 命令（渐进式加载）

## 4. References / Assets Curation

- [x] 4.1 在 `references/` 添加：AJG 数据文件契约、字段说明、常见失败排查（含 envvars 与 gate/验证码）
- [x] 4.2 在 `assets/` 添加：推荐输出示例（Markdown）、必要模板（如有）

## 5. Verification

- [x] 5.1 离线校验：运行 `python3 scripts/ajg_verify_outputs.py --outdir /Users/lingguiwang/Documents/Coding/LLM/09ABS/data`
- [x] 5.2 推荐冒烟：使用现有 `data/` 运行推荐脚本，确认不触发更新也能输出结果
- [x] 5.3 更新流程冒烟（可选）：仅在明确指定时运行抓取（不在默认推荐路径中执行）

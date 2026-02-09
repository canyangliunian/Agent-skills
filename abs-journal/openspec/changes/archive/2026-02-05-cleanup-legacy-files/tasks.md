## 1. Data Migration (`data/` → `assets/data/`)

- [x] 1.1 创建 `assets/data/` 目录并迁移 `data/` 下全部文件到 `assets/data/`
- [x] 1.2 更新默认路径引用：将仓库内硬编码的 `/Users/lingguiwang/Documents/Coding/LLM/09ABS/data` 替换为 `/Users/lingguiwang/Documents/Coding/LLM/09ABS/assets/data`
- [x] 1.3 更新脚本默认参数：抓取与推荐的默认数据目录指向 `assets/data/`

## 2. Script Pruning (With Confirmation)

- [x] 2.1 生成 `scripts/` 候选删除清单：不被 `SKILL.md` / `README.md` / `scripts/abs_journal.py` 引用且不属于抓取/推荐/校验核心
- [x] 2.2 让用户确认候选删除清单后再执行删除（破坏性操作必须二次确认）
- [x] 2.3 删除确认后的脚本，并再次运行推荐与离线校验冒烟

## 3. Legacy / Trash Cleanup

- [x] 3.1 清理 `.DS_Store`、`__pycache__/`、`*.pyc`（全仓库）
- [x] 3.2 清理除保留清单外的其他旧文件/目录（如存在），并在删除前输出清单确认

## 4. Verification

- [x] 4.1 离线校验：运行 `python3 scripts/ajg_verify_outputs.py --outdir /Users/lingguiwang/Documents/Coding/LLM/09ABS/assets/data`
- [x] 4.2 推荐冒烟：使用 `assets/data/` 运行推荐入口，确认默认不更新也能输出结果
- [x] 4.3 更新流程冒烟（可选）：显式 `--update` 时抓取输出到 `assets/data/`（缺失 envvars 时应提示并非零退出）

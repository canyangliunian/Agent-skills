## 1. Error Message UX (Missing Env Vars)

- [x] 1.1 在 `scripts/ajg_fetch.py` 中优化缺少 `AJG_EMAIL`/`AJG_PASSWORD` 的错误信息：包含缺失变量名、可复制的 export 示例、以及 `scripts/ajg_config.example.env` 提示
- [x] 1.2 增补 README “常见失败与排查”：明确默认读取环境变量，并给出 export 示例与 env 示例文件说明

## 2. Verification

- [x] 2.1 添加一个本地可运行的冒烟验证命令（不需要真实登录），用于确认缺失 envvars 时错误信息包含上述要点
- [x] 2.2 运行 `python scripts/ajg_fetch.py --outdir /Users/lingguiwang/Documents/Coding/LLM/09ABS/data`（在未设置 env 的情况下）并确认输出符合 spec

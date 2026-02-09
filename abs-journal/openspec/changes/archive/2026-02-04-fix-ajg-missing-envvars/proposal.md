## Why

当前 `scripts/ajg_fetch.py` 在缺少 `AJG_EMAIL` / `AJG_PASSWORD` 环境变量时会直接抛出异常退出。该行为本身符合“必须通过环境变量读取凭据”的安全约束，但对用户来说缺少更清晰的指导与更稳定的默认行为描述：脚本应默认从环境变量加载凭据，并在未设置时给出可操作的提示（如何设置、如何用示例 env 文件），以减少误用与排错成本。

## What Changes

- 明确并强化默认行为：脚本 **默认从环境变量** 读取 `AJG_EMAIL` / `AJG_PASSWORD` 作为登录凭据来源，不提供在命令行参数中直接传递密码的方式。
- 当环境变量缺失时，输出更明确的错误提示（包含需要设置的变量名、示例导出方式、以及可参考的 `scripts/ajg_config.example.env`），并保持非零退出码。
- 更新项目文档：在 README 中明确“默认读取环境变量”与常见错误排查步骤。

## Capabilities

### New Capabilities

<!-- 无新增 capability。本次为既有抓取能力的行为修复与文档完善。 -->

### Modified Capabilities

- `ajg-fetch`: 明确“默认从环境变量加载凭据”的要求，并增强缺失凭据时的错误提示与可操作性说明（不改变安全约束，不引入明文持久化）。

## Impact

- 影响代码：`scripts/ajg_fetch.py`（错误提示/默认凭据加载行为说明）
- 影响文档：`README.md`（运行说明与排错）
- 不影响外部依赖：保持 stdlib-only，不新增第三方依赖


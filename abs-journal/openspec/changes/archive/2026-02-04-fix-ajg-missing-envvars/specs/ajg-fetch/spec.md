## MODIFIED Requirements

### Requirement: CLI entrypoint and credentials handling
系统 SHALL 提供可通过命令行直接运行的抓取入口，并通过环境变量读取登录凭据，且不得在仓库内以明文方式持久化存储凭据。

#### Scenario: Credentials provided via environment variables
- **WHEN** 用户以命令行运行抓取程序并在环境中设置 `AJG_EMAIL` 与 `AJG_PASSWORD`
- **THEN** 系统 MUST 使用这两个环境变量尝试登录（如站点需要 gated 登录）并继续抓取流程

#### Scenario: Missing credentials
- **WHEN** 用户未设置 `AJG_EMAIL` 或 `AJG_PASSWORD` 且目标页面被 gated 需要登录
- **THEN** 系统 MUST 以非零退出码退出，并给出明确的错误信息指示需要设置相关环境变量

#### Scenario: Missing credentials provides actionable guidance
- **WHEN** 系统检测到 `AJG_EMAIL` 或 `AJG_PASSWORD` 缺失
- **THEN** 系统 MUST 在错误信息中包含（1）缺失的变量名，（2）可复制的 `export` 示例命令，以及（3）提示参考 `scripts/ajg_config.example.env`

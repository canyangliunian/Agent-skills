## MODIFIED Requirements

### Requirement: CLI entrypoint and credentials handling
系统 SHALL 提供可通过命令行直接运行的抓取入口，并通过环境变量读取登录凭据，且不得在仓库内以明文方式持久化存储凭据。

#### Scenario: Credentials provided via environment variables
- **WHEN** 用户以命令行运行抓取程序并在环境中设置 `AJG_EMAIL` 与 `AJG_PASSWORD`
- **THEN** 系统 MUST 使用这两个环境变量尝试登录（如站点需要 gated 登录）并继续抓取流程

#### Scenario: Missing credentials provides actionable guidance
- **WHEN** 系统检测到 `AJG_EMAIL` 或 `AJG_PASSWORD` 缺失
- **THEN** 系统 MUST 在错误信息中包含（1）缺失的变量名，（2）可复制的 `export` 示例命令，以及（3）提示参考 `scripts/ajg_config.example.env`

### Requirement: Output artifacts and naming contract
系统 SHALL 将抓取结果写入本地文件，并满足固定的文件命名契约，以便下游（推荐能力）稳定消费。

#### Scenario: Successful fetch writes expected files
- **WHEN** 抓取流程成功完成
- **THEN** 系统 MUST 在用户指定输出目录写入至少以下文件：
  - `ajg_<year>_journals_raw.jsonl`
  - `ajg_<year>_meta.json`
  - `ajg_<year>_journals_core_custom.csv`

#### Scenario: Overwrite requires explicit flag
- **WHEN** 输出目录中已存在同名输出文件且用户未提供 `--overwrite`
- **THEN** 系统 MUST 失败退出并提示需要 `--overwrite`（非破坏性默认）


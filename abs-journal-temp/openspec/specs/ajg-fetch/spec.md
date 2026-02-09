## Purpose

定义抓取 Chartered ABS Academic Journal Guide（AJG）并落地本地数据文件的能力边界与可验证契约：凭据来源、年份发现、失败模式、输出文件命名与元数据要求。
## Requirements
### Requirement: CLI entrypoint and credentials handling
系统 SHALL 提供可通过命令行直接运行的抓取入口，并通过环境变量读取登录凭据，且不得在仓库内以明文方式持久化存储凭据。

#### Scenario: Credentials provided via environment variables
- **WHEN** 用户以命令行运行抓取程序并在环境中设置 `AJG_EMAIL` 与 `AJG_PASSWORD`
- **THEN** 系统 MUST 使用这两个环境变量尝试登录（如站点需要 gated 登录）并继续抓取流程

#### Scenario: Missing credentials provides actionable guidance
- **WHEN** 系统检测到 `AJG_EMAIL` 或 `AJG_PASSWORD` 缺失
- **THEN** 系统 MUST 在错误信息中包含（1）缺失的变量名，（2）可复制的 `export` 示例命令，以及（3）提示参考 `scripts/ajg_config.example.env`

### Requirement: Discover latest AJG year entry
系统 SHALL 从 AJG 入口页自动发现可用年份链接，并选择最新年份作为抓取目标，避免硬编码年份或固定子链接。

#### Scenario: Latest year can be discovered from entry page
- **WHEN** 系统成功获取 AJG 入口页 HTML 且页面包含多个年份链接
- **THEN** 系统 MUST 选择最大年份对应的链接作为抓取目标年份与目标页面 URL

#### Scenario: Discovery fails due to page changes
- **WHEN** 入口页 HTML 不再包含可解析的年份链接（结构变更等原因）
- **THEN** 系统 MUST 失败退出，并在错误信息中说明“无法发现 AJG 年份链接”，以便用户诊断与更新

### Requirement: Robust HTTP behavior
系统 SHALL 对网络请求提供基础鲁棒性能力（超时、重试、指数退避），并在失败时提供可诊断信息。

#### Scenario: Transient network error
- **WHEN** 网络请求出现临时错误（连接失败、超时等）
- **THEN** 系统 MUST 进行有限次数重试，并采用指数退避策略后再重试

#### Scenario: Persistent HTTP failure
- **WHEN** 在重试次数耗尽后网络请求仍失败
- **THEN** 系统 MUST 失败退出，并在错误信息中包含请求方法与目标 URL（或等价的可诊断信息）

### Requirement: Output artifacts and naming contract
系统 SHALL 将抓取结果写入本地文件，并满足固定的文件命名契约，以便下游（推荐能力）稳定消费。

#### Scenario: Default output directory points to assets/data
- **WHEN** 用户未显式指定数据目录的约定位置（以本 skill 默认配置为准）
- **THEN** 系统 MUST 将抓取输出写入 `assets/data/`（或允许脚本参数覆盖，但默认文档与工作流以 `assets/data/` 为准）

### Requirement: Metadata content for traceability
系统 SHALL 在 meta 文件中记录抓取的关键元信息（时间、年份、来源 URL 等），用于复现与审计。

#### Scenario: Meta file contains required fields
- **WHEN** 系统写出 `ajg_<year>_meta.json`
- **THEN** 该文件 MUST 至少包含抓取时间（UTC）、AJG 年份、来源 URL（或等价字段）以支持追踪


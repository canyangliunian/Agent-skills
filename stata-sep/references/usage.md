# stata-sep 使用速查（客户端配置 + 环境变量）

## MCP 客户端最小配置示例（JSON）
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": ["stata-mcp"],
      "env": {
        "stata_cli": "/ABS/PATH/TO/StataMP",          
        "documents_path": "/ABS/PATH/TO/stata-mcp-folder", 
        "STATA_MCP_CWD": "/ABS/PATH/TO/WORKDIR"      
      }
    }
  }
}
```
- `stata_cli`：必需，当 `uvx stata-mcp --usable` 提示 FAILED；macOS 示例 `/Applications/Stata/StataMP.app/Contents/MacOS/stata-mp`，Windows 示例 `C:\\Program Files\\Stata18\\StataSE.exe`。
- `documents_path`：可选，若不设默认 `~/Documents`，内部会生成 `stata-mcp-folder`。
- `STATA_MCP_CWD`：可选，指定“项目工作根”，结果/日志/临时文件均在该根下的 `stata-mcp-folder` 内。

## 核心命令
- 环境自检：`uvx stata-mcp --usable`
- 版本：`uvx stata-mcp --version`
- 默认启动（stdio）：`uvx stata-mcp`
- HTTP/SSE 传输：`uvx stata-mcp -t http` 或 `-t sse`
- Agent 模式：`uvx stata-mcp --agent`

## 目录约定（默认在 `STATA_MCP_CWD` 或 `~/Documents` 下自动创建）
- `stata-mcp-log/`：运行日志（.log）
- `stata-mcp-dofile/`：生成的 do 文件
- `stata-mcp-result/`：表格/图形等结果输出
- `stata-mcp-tmp/`：临时文件（含 `get_data_info` 输出的 JSON）

## 最小工作流（命令顺序）
1) `get_data_info`（可选）→ 确认变量与缺失。
2) `results_doc_path`（若需表格/图形输出）。
3) `write_dofile` 写主 do（或 `append_dofile` 迭代）。
4) `stata_do` 执行，返回 `log_file_path` + `log_content`。
5) 用 `read_file` 查看 log/表格，必要时修订并重跑。

## 常用环境变量
- `STATA_MCP_CLIENT`: 某些客户端传入特殊标记（如 cc），影响 CWD 取值。
- `STATA_MCP_LOGGING_ON`: 默认 true；设为 false 关闭日志。
- `STATA_MCP_LOG_FILE`: 自定义日志文件（默认 `~/.statamcp.log`）。
- `STATA_MCP_LOGGING_CONSOLE_HANDLER`: 设 true 额外在控制台打印日志。
- `STATA_MCP_LOGGING_FILE_HANDLER`: 控制文件日志开关，默认 true。
- `STATA_MCP_PROMPT`: 控制是否暴露 prompt 资源，默认 true。

## Windows 额外提示
- 路径请使用绝对路径并双反斜杠，如 `C:\\Program Files\\Stata18\\StataSE.exe`。
- 若需创建目录，优先用 `mk_dir`，避免无权限位置。


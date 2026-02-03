# stata-sep 工具与常见坑

## 工具总览（对应 Stata-MCP 实现）
- `help(cmd)` (Unix)：返回 Stata help 文本。失败多因命令不存在。
- `write_dofile(content, encoding="utf-8", strict_mode=False)`：写新 do，返回绝对路径。
- `append_dofile(original_dofile_path, content, encoding="utf-8")`：基于原 do 生成新 do；原文件缺失则仅写新增内容。
- `stata_do(dofile_path, log_file_name=None, is_read_log=True)`：运行 do；返回 `log_file_path` 与可选 `log_content`。
- `read_file(file_path, encoding="utf-8")`：读取文本文件。
- `get_data_info(data_path, vars_list=None, encoding="utf-8")`：描述 .dta/.csv，输出 JSON 路径于 `stata-mcp-tmp/`。
- `ado_package_install(package, source="ssc"|"github"|"net", is_replace=True, package_source_from=None)` (Unix)：安装 ado；需确认。
- `load_figure(figure_path)`：回显 png/jpg。
- `mk_dir(path)`：安全创建目录（sanitize 路径）。
- Prompts：`stata_assistant_role(lang?)`、`stata_analysis_strategy(lang?)`、`results_doc_path()`。

## 典型用法片段
- 生成结果路径并写 do：
  ```
  local output_path "`=results_doc_path()'"
  use "/ABS/data.dta", clear
  regress price mpg
  esttab using "`output_path'/reg1.rtf", replace
  ```
- 运行 do：
  ```json
  {"tool":"stata_do","params":{"dofile_path":"/ABS/path/20251210120000.do","is_read_log":true}}
  ```
- 追加 do：
  ```json
  {"tool":"append_dofile","params":{"original_dofile_path":"/ABS/path/base.do","content":"reg price mpg"}}
  ```

## 常见问题与排查
- 路径不存在/相对路径：所有输入必须绝对路径；Windows 需双反斜杠。
- `stata_cli` 未找到：先跑 `uvx stata-mcp --usable`，按提示设置 `stata_cli` 环境变量。
- 日志为空：检查 do 中是否有 `log using` 并被关闭；`stata_do` 会自动生成日志路径。
- 包安装失败：确认源 `ssc`/`github`/`net`；防火墙或代理问题需手动下载。
- `get_data_info` 报扩展不支持：目前仅支持 .dta/.csv。
- 绘图/交互命令：避免需要 GUI 的命令，或确保图形输出到文件后用 `load_figure`。

## 最佳实践
- do 开头即 `use <abs path>, clear`；设置 `version 17`（或实际版本）。
- 输出统一写入 `results_doc_path()` 返回目录；表格文件带时间戳避免覆盖。
- 复杂流水线拆成多个 do，逐步 `append_dofile`，每步跑 `stata_do` 验证。
- 安装包前先检查是否必需，减少时间开销。


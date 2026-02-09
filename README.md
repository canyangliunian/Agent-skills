# Agent Skills Collection

![Skills](https://img.shields.io/badge/skills-6-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

面向「凌贵旺 / Guiwang Ling」的 Claude Code Agent Skills 集合，涵盖学术研究、LaTeX 排版、终端动画、CLI 工具开发等场景。

## 目录

- [项目概述](#项目概述)
- [Skills 列表](#skills-列表)
  - [1. ABS-Journal](#1-abs-journal)
  - [2. latex](#2-latex)
  - [3. stata-sep](#3-stata-sep)
  - [4. pycli-color](#4-pycli-color)
  - [5. script2animation](#5-script2animation)
  - [6. oh-my-opencode-update](#6-oh-my-opencode-update)
- [通用约定](#通用约定)
- [安装与使用](#安装与使用)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [联系方式](#联系方式)

## 项目概述

本仓库包含多个独立的 Agent Skills，每个 skill 都遵循标准的 SKILL.md 规范，可直接集成到 Claude Code 或其他支持 MCP 的 AI 客户端中使用。

**目标用户**：凌贵旺（Guiwang Ling）
**单位**：南京农业大学经济管理学院
**邮箱**：lingguiwang@yeah.net

## Skills 列表

### 1. ABS-Journal

**路径**：`./ABS-Journal/`
**描述**：学术期刊推荐与 AJG/ABS 数据库管理工具

**核心功能**：
- 抓取 Chartered ABS Academic Journal Guide (AJG) 最新期刊目录
- 基于本地 AJG 数据库进行投稿期刊推荐（混合 AI + 规则筛选）
- 支持多领域候选池（ECON, FINANCE, PUB SEC, REGIONAL STUDIES, PLANNING AND ENVIRONMENT, SOC SCI）
- 生成三段式推荐报告（easy/medium/hard）

**使用场景**：
- 需要更新 AJG/ABS 期刊数据库
- 根据论文标题和摘要推荐投稿期刊
- 查看特定领域的期刊列表

**快速开始**：
```bash
# 推荐期刊（使用本地数据）
python3 ABS-Journal/scripts/abs_journal.py recommend \
  --title "你的论文标题" \
  --abstract "你的摘要" \
  --mode medium \
  --hybrid \
  --auto_ai

# 更新 AJG 数据库（需要账号密码）
export AJG_EMAIL="your_email"
export AJG_PASSWORD="your_password"
python3 ABS-Journal/scripts/ajg_fetch.py --outdir "$(pwd)/ABS-Journal/assets/data"
```

---

### 2. latex

**路径**：`./latex/`
**描述**：PDF 转 LaTeX 与一键编译工具集

**核心功能**：
- PDF → 结构化内容抽取（基于 Marker Extract，支持 LLM 辅助）
- 支持 AEA、经济研究、NAU、SCU 等学术模板
- LaTeX 一键编译（自动选择引擎与参考文献工具）
- 公式、图表、参考文献自动提取与整理

**使用场景**：
- 将 PDF 论文转换为可编辑的 LaTeX 格式
- 使用学术模板快速生成论文或 Beamer 演示文稿
- 批量编译 LaTeX 项目

**快速开始**：
```bash
# PDF 抽取（优先使用 LLM）
python3 latex/scripts/marker_extract.py \
  "/path/to/paper.pdf" \
  -o "/path/to/output" \
  --use_llm --provider chatanywhere

# LaTeX 编译
python3 latex/scripts/compile.py \
  --path "/path/to/main.tex" \
  --output "/path/to/output"
```

---

### 3. stata-sep

**路径**：`./stata-sep/`
**描述**：基于 Stata-MCP 的 Stata 分析工作流

**核心功能**：
- 通过 MCP 协议与 Stata 交互
- 自动生成和执行 do 文件
- 数据描述性统计与可视化
- ado 包管理与安装
- 支持 agent 模式与评估流程

**使用场景**：
- 在 Claude Code 中直接运行 Stata 分析
- 自动化数据清洗与回归分析
- 生成可复现的 Stata 工作流

**快速开始**：
```bash
# 检查 Stata 环境
uvx stata-mcp --usable

# 配置 MCP server（参考 references/usage.md）
# 然后在 Claude Code 中直接使用 Stata-MCP 工具
```

---

### 4. pycli-color

**路径**：`./pycli-color/`
**描述**：Python argparse CLI 彩色帮助输出规范

**核心功能**：
- 为 Python CLI 脚本提供统一的彩色 `--help` 输出
- 选项（`-h`, `--title`）显示为青色加粗
- metavar（`TITLE`, `FILE_PATH`）显示为黄色加粗
- 支持 `NO_COLOR` / `FORCE_COLOR` 环境变量控制

**使用场景**：
- 开发新的 Python CLI 工具
- 改进现有脚本的用户体验
- 统一项目中所有 CLI 工具的视觉风格

**快速开始**：
```bash
# 查看示例（强制彩色输出）
NO_COLOR= FORCE_COLOR=1 python3 pycli-color/scripts/demo_pycli_color.py -h

# 在新脚本中复用（复制 ColorHelpFormatter 类）
```

---

### 5. script2animation

**路径**：`./script2animation/`
**描述**：将脚本转换为终端动画教程

**核心功能**：
- 生成离线 HTML 终端动画（macOS Terminal 风格）
- 支持打字机效果、场景切换、暂停/重播
- 自动从脚本提取真实参数和输出
- 墨绿色系深色主题，支持配色微调

**使用场景**：
- 为脚本创建可视化教程
- 生成演示文档或培训材料
- 展示 CLI 工具的使用方法

**快速开始**：
```bash
# 在 Claude Code 中使用 skill
# 提供脚本路径，自动生成动画 HTML
```

---

### 6. oh-my-opencode-update

**路径**：`./oh-my-opencode-update/`
**描述**：oh-my-opencode 插件升级与故障排查工具

**核心功能**：
- 升级 oh-my-opencode 到最新版本或指定版本
- 自动备份、清理缓存、验证安装
- 支持自定义配置路径（环境变量）
- 处理权限错误和缓存冲突

**使用场景**：
- 升级 oh-my-opencode 插件
- 解决插件缓存或权限问题
- 验证插件安装状态

**快速开始**：
```bash
# Dry-run（推荐先测试）
bash oh-my-opencode-update/scripts/oh_my_opencode_update.sh --dry-run --latest

# 实际升级到最新版
bash oh-my-opencode-update/scripts/oh_my_opencode_update.sh --apply --latest

# 升级到指定版本
bash oh-my-opencode-update/scripts/oh_my_opencode_update.sh --apply --target-version 3.2.2
```

---

## 通用约定

### 路径规范
- **绝对路径优先**：所有脚本示例默认使用绝对路径，确保可移植性
- **相对路径说明**：当使用相对路径时，必须明确基准目录（通常为项目根目录）

### 代码规范
- **可运行性**：所有代码必须包含必要的库导入、路径设置和错误处理
- **可复现性**：优先编写可复用的脚本、函数和模板，而非一次性命令

### 安全原则
- **确认机制**：潜在破坏性操作（删除文件、覆盖代码、批量编辑）必须先警告并请求确认
- **环境变量**：敏感信息（密码、API Key）通过环境变量传递，不写入代码

### 文档规范
- **SKILL.md**：每个 skill 必须包含标准的 SKILL.md 文件，定义触发条件、核心功能和使用流程
- **README.md**：每个 skill 可选包含 README.md，提供快速上手指南
- **references/**：详细文档和参考资料放在 references/ 目录

## 安装与使用

### 前置要求
- Python 3.8+
- 根据具体 skill 需求安装依赖（参见各 skill 的 README.md）

### 集成到 Claude Code

1. 将本仓库克隆到本地：
```bash
# 使用 SSH（推荐）
git clone git@github.com:canyangliunian/Agent-skills.git ~/Documents/GitHub/claude-skills

# 或使用 HTTPS
git clone https://github.com/canyangliunian/Agent-skills.git ~/Documents/GitHub/claude-skills
```

2. 在 Claude Code 配置中添加 skills 路径（通常在 `~/.claude/` 或项目 `.claude/` 目录）

3. 使用 `/skill-name` 命令调用对应的 skill

### 开发新 Skill

参考现有 skill 的结构：
```
skill-name/
├── SKILL.md          # 必需：skill 定义和规范
├── README.md         # 可选：快速上手指南
├── scripts/          # 可执行脚本
├── references/       # 详细文档
├── assets/           # 资源文件（模板、数据等）
└── plan/             # 可选：规划与进度跟踪
```

## 贡献指南

本仓库面向单一用户（凌贵旺），但欢迎提出改进建议：
- 提交 Issue 报告问题或建议新功能
- 提交 Pull Request 改进现有 skill
- 遵循现有的代码规范和文档格式

## 许可证

MIT License

本项目采用 MIT 许可证，允许自由使用、修改和分发。详见 LICENSE 文件。

## 联系方式

- **姓名**：凌贵旺 (Guiwang Ling)
- **单位**：南京农业大学经济管理学院
- **邮箱**：lingguiwang@yeah.net

---

**最后更新**：2025-02-09

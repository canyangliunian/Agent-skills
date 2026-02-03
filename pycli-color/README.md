# pycli-color

为 Python `argparse` CLI 提供统一的彩色 `-h/--help` 输出规范：

- 选项 token（以 `-` 开头，如 `-h`, `--title`）：青色 + 加粗
- metavar/占位符（全大写或包含 `_`，如 `TITLE`, `AJG_CSV`）：黄色 + 加粗
- 支持 `NO_COLOR` / `FORCE_COLOR=1` 的可控启停策略

核心规则见：`/Users/lingguiwang/.agents/skills/pycli-color/SKILL.md`

## 快速验证

你的环境里常见 `NO_COLOR=1` 全局存在，因此即便实现了彩色 `--help`，默认也可能显示无色。

强制输出彩色（推荐验证命令）：

```bash
NO_COLOR= FORCE_COLOR=1 python3 /Users/lingguiwang/.agents/skills/pycli-color/scripts/demo_pycli_color.py -h
```

强制无色：

```bash
NO_COLOR=1 python3 /Users/lingguiwang/.agents/skills/pycli-color/scripts/demo_pycli_color.py -h
```

## 在新脚本中复用

最简单方式：

- 直接复制 `demo_pycli_color.py` 中的以下符号到你的脚本（保持命名一致更便于复用）：
  - `supports_color`
  - `colorize`
  - `ColorHelpFormatter`
  - `ANSI_RESET`, `ANSI_CYAN_BOLD`, `ANSI_YELLOW_BOLD`
- 在 `argparse.ArgumentParser` 中设置：`formatter_class=ColorHelpFormatter`


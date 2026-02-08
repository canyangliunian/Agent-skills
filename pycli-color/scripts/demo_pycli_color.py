#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
demo_pycli_color.py

用于验证 `pycli-color` 技能的彩色 `--help` 输出效果（argparse + 自定义 HelpFormatter）。

颜色规则：
- option token（以 '-' 开头）：青色 + 加粗
- metavar token（全大写或包含 '_'）：黄色 + 加粗

颜色启用策略：
- 默认 auto：仅当 sys.stdout.isatty() 为 True 且 TERM != 'dumb' 时启用
- 若存在 NO_COLOR：强制禁用
- 若 FORCE_COLOR=1：强制启用（即便非 TTY）

测试（请保留这些注释，便于未来快速验证）：
# NO_COLOR=1 python3 scripts/demo_pycli_color.py -h
# FORCE_COLOR=1 python3 scripts/demo_pycli_color.py -h
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List


ANSI_RESET = "\x1b[0m"
ANSI_CYAN_BOLD = "\x1b[36;1m"
ANSI_YELLOW_BOLD = "\x1b[33;1m"


def supports_color() -> bool:
    """
    Color policy:
    - Default auto: enable only when stdout is a TTY and TERM is not 'dumb'
    - If NO_COLOR exists: force disable
    - If FORCE_COLOR=1: force enable (even if non-TTY)
    """
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("FORCE_COLOR") == "1":
        return True
    term = os.environ.get("TERM", "")
    if term.lower() == "dumb":
        return False
    return sys.stdout.isatty()


def colorize(text: str, ansi_code: str) -> str:
    if not supports_color():
        return text
    return f"{ansi_code}{text}{ANSI_RESET}"


class ColorHelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action: argparse.Action) -> str:
        text = super()._format_action_invocation(action)
        if not supports_color():
            return text

        parts = text.split()
        out: List[str] = []
        for p in parts:
            if p.startswith("-"):
                out.append(colorize(p, ANSI_CYAN_BOLD))
            elif p.isupper() or "_" in p:
                out.append(colorize(p, ANSI_YELLOW_BOLD))
            else:
                out.append(p)
        return " ".join(out)


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        formatter_class=ColorHelpFormatter,
        description="pycli-color demo：演示彩色 --help 输出",
    )

    # 最小CLI面（用于校验）
    ap.add_argument("--title", required=True, help="必填：标题（required=True）")
    ap.add_argument("--mode", choices=["easy", "fit"], default="easy", help="choices 示例参数")
    ap.add_argument("--topk", type=int, default=10, help="可选参数示例（整数）")
    return ap


def main() -> int:
    ap = build_arg_parser()
    args = ap.parse_args()
    print(f"title={args.title}")
    print(f"mode={args.mode}")
    print(f"topk={args.topk}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


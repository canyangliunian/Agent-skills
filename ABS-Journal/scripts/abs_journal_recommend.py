#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ABS-Journal: journal recommendation (local-first).

This is a stable root-level entrypoint for journal recommendation.
It defaults to local AJG CSV and does NOT update/fetch AJG data.

Usage (absolute paths recommended):
  python3 /Users/lingguiwang/.agents/skills/abs-journal/scripts/abs_journal_recommend.py \
    --title "..." --abstract "..." --mode fit
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    skill_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    impl = os.path.join(skill_root, "scripts", "abs_article_impl.py")
    if not os.path.isfile(impl):
        raise RuntimeError(f"推荐实现脚本不存在: {impl}")
    os.execv(sys.executable, [sys.executable, impl, *sys.argv[1:]])
    raise RuntimeError("execv failed")


if __name__ == "__main__":
    raise SystemExit(main())

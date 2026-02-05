#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Minimal regression checks for topic-fit gating.

This is a lightweight, offline sanity check script (not a full test framework).
It verifies:
- The report includes gating metadata
- Output still works with empty abstract
"""

from __future__ import annotations

import os
import re
import subprocess
import sys


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AJG_CSV = os.path.join(REPO_ROOT, "assets", "data", "ajg_2024_journals_core_custom.csv")
IMPL = os.path.join(REPO_ROOT, "scripts", "abs_article_impl.py")


def run(mode: str, abstract: str) -> str:
    cmd = [
        sys.executable,
        IMPL,
        "--ajg_csv",
        AJG_CSV,
        "--field",
        "ECON",
        "--title",
        "Trade war and public opinion",
        "--abstract",
        abstract,
        "--mode",
        mode,
        "--topk",
        "10",
    ]
    p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.stdout


def main() -> int:
    for mode in ["fit", "easy", "value"]:
        out = run(mode, abstract="We study tariff shocks and public attitudes toward trade using surveys.")
        assert "## 候选集（主题贴合）" in out, f"missing gating section for mode={mode}"
        assert "已对所有模式启用“主题贴合候选集”前置筛选" in out, f"missing gating note for mode={mode}"

    out2 = run("easy", abstract="")
    assert "你未提供摘要" in out2, "missing empty-abstract warning"

    # Very lightweight gating assertion: in this repo's current gating strategy, the
    # report should not include journals that are far outside the likely top-fit candidates.
    # We use a conservative check: a known journal title that appears around the fit-score
    # boundary for this particular query should not show up when topk is small.
    out3 = run("easy", abstract="We study tariff shocks and public attitudes toward trade using surveys.")
    assert "Journal of Time Series Analysis" not in out3, "unexpected far-off journal present; gating may be broken"

    # Basic table header sanity.
    assert re.search(r"\\|\\s*FitScore\\s*\\|\\s*EasyScore\\s*\\|\\s*ValueScore\\s*\\|", out3), "missing score columns"
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

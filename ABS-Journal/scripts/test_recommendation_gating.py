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
    for mode in ["easy", "medium", "hard"]:
        out = run(mode, abstract="We study tariff shocks and public attitudes toward trade using surveys.")
        assert "## 候选集（主题贴合）" in out, f"missing gating section for mode={mode}"
        assert "已对所有模式启用“主题贴合候选集”前置筛选" in out, f"missing gating note for mode={mode}"
        assert "候选 Field：" in out, f"missing field scope line for mode={mode}"
        # Rating hierarchy markers should exist after splitting 1/2/3 buckets.
        if mode == "easy":
            assert ("A 主投更易（1）" in out) or ("A 主投更易（2）" in out), "missing rating bucket markers for easy"
        if mode == "medium":
            assert ("A 主投更易（2）" in out) or ("B 备投折中（3）" in out), "missing rating bucket markers for medium"

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

    # Fallback sanity: rating_filter + limited bucket should still output something, and never crash.
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
        "trade war tariffs agriculture public opinion beliefs RCT",
        "--mode",
        "hard",
        "--topk",
        "10",
        "--rating_filter",
        "4,4*",
    ]
    p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert "## C 冲刺更高（4）" in p.stdout or "## C 冲刺更高（4*）" in p.stdout, "missing hard buckets under rating_filter"

    # field_scope invalid should fail with a readable error listing known fields.
    bad = subprocess.run(
        [
            sys.executable,
            IMPL,
            "--ajg_csv",
            AJG_CSV,
            "--field",
            "ECON",
            "--field_scope",
            "NOT_A_FIELD",
            "--title",
            "t",
            "--abstract",
            "trade",
            "--mode",
            "easy",
            "--topk",
            "10",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert bad.returncode != 0, "expected invalid field_scope to fail"
    assert "可选 Field（来自 CSV）" in bad.stdout, "expected list of known fields in error"
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Regression test: --hybrid should not require explicit --export_candidate_pool_json.

This is a lightweight smoke test that runs the CLI end-to-end with --hybrid and
verifies that candidate pools are generated under the repo's reports/ directory.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = REPO_ROOT / "reports"


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "abs_journal.py"), *argv],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    # Clean up expected outputs (best-effort).
    for p in [
        REPORTS_DIR / "candidate_pool_easy.json",
        REPORTS_DIR / "candidate_pool_medium.json",
        REPORTS_DIR / "candidate_pool_hard.json",
    ]:
        try:
            p.unlink()
        except FileNotFoundError:
            pass

    proc = _run(
        [
            "recommend",
            "--title",
            "test",
            "--mode",
            "medium",
            "--hybrid",
            "--auto_ai",
            "--topk",
            "2",
        ]
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return int(proc.returncode or 1)

    for p in [
        REPORTS_DIR / "candidate_pool_easy.json",
        REPORTS_DIR / "candidate_pool_medium.json",
        REPORTS_DIR / "candidate_pool_hard.json",
    ]:
        if not p.exists():
            sys.stderr.write(f"missing output: {p}\\n")
            return 2
        obj = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(obj, dict) or "candidates" not in obj:
            sys.stderr.write(f"bad json structure: {p}\\n")
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


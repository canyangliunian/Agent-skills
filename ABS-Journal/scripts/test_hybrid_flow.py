#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Offline minimal regression for hybrid flow:
- generate candidate pool JSON
- create a mock AI output JSON strictly within pool
- validate subset enforcement (abs_ai_review.py)
- render final report (hybrid_report.py)

Run:
  python3 /ABS_JOURNAL_HOME/scripts/test_hybrid_flow.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, List


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run(argv: List[str]) -> None:
    proc = subprocess.run(argv, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "command failed:\n"
            + " ".join(argv)
            + "\n--- stdout ---\n"
            + proc.stdout
            + "\n--- stderr ---\n"
            + proc.stderr
        )


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_first(pool_path: str) -> str:
    pool = load_json(pool_path)
    cands = pool.get("candidates") or []
    if not cands:
        raise RuntimeError("candidate pool empty")
    j = (cands[0].get("journal") or "").strip()
    if not j:
        raise RuntimeError("candidate journal missing")
    return j


def main() -> int:
    ajg_csv = os.path.join(ROOT, "assets", "data", "ajg_2024_journals_core_custom.csv")
    abs_article_impl = os.path.join(ROOT, "scripts", "abs_article_impl.py")
    abs_ai_review = os.path.join(ROOT, "scripts", "abs_ai_review.py")
    hybrid_report = os.path.join(ROOT, "scripts", "hybrid_report.py")

    with tempfile.TemporaryDirectory() as td:
        pool_path = os.path.join(td, "pool.json")
        ai_path = os.path.join(td, "ai.json")
        report_path = os.path.join(td, "report.md")

        title = "Retaliatory tariffs on US agricultural products: RCT evidence in China"
        abstract = "trade war tariffs agriculture public opinion beliefs RCT"

        run(
            [
                sys.executable,
                abs_article_impl,
                "--ajg_csv",
                ajg_csv,
                "--field",
                "ECON",
                "--mode",
                "fit",
                "--topk",
                "10",
                "--title",
                title,
                "--abstract",
                abstract,
                "--rating_filter",
                "1,2,3",
                "--export_candidate_pool_json",
                pool_path,
            ]
        )

        j = pick_first(pool_path)
        topk = 10
        items = [{"journal": j, "topic": f"mock topic {i}"} for i in range(1, topk + 1)]
        ai_obj = {"fit": items, "easy": items, "value": items}
        with open(ai_path, "w", encoding="utf-8") as f:
            json.dump(ai_obj, f, ensure_ascii=False, indent=2)

        run([sys.executable, abs_ai_review, "--candidate_pool_json", pool_path, "--ai_output_json", ai_path, "--topk", str(topk)])

        proc = subprocess.run(
            [sys.executable, hybrid_report, "--candidate_pool_json", pool_path, "--ai_output_json", ai_path, "--topk", str(topk)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(proc.stdout)

        text = proc.stdout
        for key in ["Fit Top10", "Easy Top10", "Value Top10", "序号", "期刊名", "ABS星级", "期刊主题"]:
            if key not in text:
                raise RuntimeError(f"missing in report: {key}")

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
                "--field_scope",
                "",
                "--mode",
                "medium",
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
        items_easy = [{"journal": j, "topic": f"mock topic easy {i}"} for i in range(1, topk + 1)]
        items_medium = [{"journal": j, "topic": f"mock topic medium {i}"} for i in range(1, topk + 1)]
        items_hard = [{"journal": j, "topic": f"mock topic hard {i}"} for i in range(1, topk + 1)]
        # Make sure baseline test uses non-overlapping journals across buckets
        if topk >= 2:
            items_medium[0]["journal"] = j + " (alt-medium)"
            items_hard[0]["journal"] = j + " (alt-hard)"
        ai_obj = {"easy": items_easy, "medium": items_medium, "hard": items_hard}
        with open(ai_path, "w", encoding="utf-8") as f:
            json.dump(ai_obj, f, ensure_ascii=False, indent=2)

        # The above "alt-*" journals won't be in candidate pool; instead, pick distinct journals from pool when possible.
        pool = load_json(pool_path)
        js = [((c or {}).get("journal") or "").strip() for c in (pool.get("candidates") or []) if isinstance(c, dict)]
        js = [x for x in js if x]
        if len(js) >= 3:
            items_easy = [{"journal": js[0], "topic": f"mock topic easy {i}"} for i in range(1, topk + 1)]
            items_medium = [{"journal": js[1], "topic": f"mock topic medium {i}"} for i in range(1, topk + 1)]
            items_hard = [{"journal": js[2], "topic": f"mock topic hard {i}"} for i in range(1, topk + 1)]
            ai_obj = {"easy": items_easy, "medium": items_medium, "hard": items_hard}
            with open(ai_path, "w", encoding="utf-8") as f:
                json.dump(ai_obj, f, ensure_ascii=False, indent=2)

        run([sys.executable, abs_ai_review, "--candidate_pool_json", pool_path, "--ai_output_json", ai_path, "--topk", str(topk)])

        # Overlap should be rejected by validator (default expectation: no overlap across buckets)
        overlap_ai_path = os.path.join(td, "ai_overlap.json")
        overlap_obj = {"easy": items_easy, "medium": items_easy, "hard": items_hard}
        with open(overlap_ai_path, "w", encoding="utf-8") as f:
            json.dump(overlap_obj, f, ensure_ascii=False, indent=2)
        p = subprocess.run(
            [sys.executable, abs_ai_review, "--candidate_pool_json", pool_path, "--ai_output_json", overlap_ai_path, "--topk", str(topk)],
            capture_output=True,
            text=True,
        )
        if p.returncode == 0:
            raise RuntimeError("expected overlap validation to fail, but it passed")

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
        for key in ["Easy Top10", "Medium Top10", "Hard Top10", "序号", "期刊名", "ABS星级", "Field"]:
            if key not in text:
                raise RuntimeError(f"missing in report: {key}")

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

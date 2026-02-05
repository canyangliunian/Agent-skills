#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Hybrid journal recommendation: script candidate pool -> AI second pass (manual) -> validation.

This script does NOT call external APIs. It validates that an AI-produced selection
is strictly a subset of the candidate pool exported by abs_article_impl.py.

Usage (example):
  python3 /ABS_JOURNAL_HOME/scripts/abs_article_impl.py \\
    --ajg_csv /ABS_JOURNAL_HOME/assets/data/ajg_2024_journals_core_custom.csv \\
    --field ECON --profile general --mode fit --topk 200 \\
    --title \"...\" --abstract \"...\" \\
    --export_candidate_pool_json /tmp/candidate_pool.json

  # (You paste / generate AI output as JSON into /tmp/ai_output.json)
  python3 /ABS_JOURNAL_HOME/scripts/abs_ai_review.py \\
    --candidate_pool_json /tmp/candidate_pool.json \\
    --ai_output_json /tmp/ai_output.json
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isabs(path):
        raise RuntimeError(f"路径必须是绝对路径: {path}")
    if not os.path.exists(path):
        raise RuntimeError(f"JSON 不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_subset(candidate_pool: Dict[str, Any], ai_output: Dict[str, Any], topk: int) -> List[str]:
    """Validate AI output against candidate pool with tri-mode requirements."""
    modes = ["fit", "easy", "value"]

    # Build allowed journals per mode (supports single-pool or per-mode pools)
    if any(k in candidate_pool for k in modes):
        allowed_by_bucket: Dict[str, set] = {}
        for bucket in modes:
            pool = candidate_pool.get(bucket) or {}
            cands = (pool.get("candidates") if isinstance(pool, dict) else []) or []
            s = {c.get("journal") for c in cands if isinstance(c, dict)}
            s.discard(None)
            allowed_by_bucket[bucket] = s
    else:
        cands = candidate_pool.get("candidates") or []
        s = {c.get("journal") for c in cands if isinstance(c, dict)}
        s.discard(None)
        allowed_by_bucket = {b: s for b in modes}

    errors: List[str] = []

    # Mode presence
    for bucket in modes:
        if bucket not in ai_output:
            errors.append(f"{bucket}: 缺少该模式输出")

    # Per-mode validation
    for bucket in modes:
        items = ai_output.get(bucket) or []
        if not isinstance(items, list):
            errors.append(f"{bucket}: 输出必须是 list")
            continue
        if len(items) < topk:
            errors.append(f"{bucket}: 数量不足 TopK={topk}，仅 {len(items)} 条")
        allowed = allowed_by_bucket.get(bucket) or set()
        for idx, it in enumerate(items, 1):
            if not isinstance(it, dict):
                errors.append(f"{bucket}[{idx}]: 每条必须是 dict")
                continue
            j = it.get("journal")
            if j not in allowed:
                errors.append(f"{bucket}[{idx}]: 期刊不在候选池: {j!r}")
            topic = it.get("topic")
            if not isinstance(topic, str) or not topic.strip():
                errors.append(f"{bucket}[{idx}]: 缺少非空 topic")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate_pool_json", required=True, help="候选池 JSON（绝对路径；可为单池或 fit/easy/value 多池）")
    ap.add_argument("--ai_output_json", required=True, help="AI 输出 JSON（绝对路径）")
    ap.add_argument("--topk", type=int, default=10, help="每个模式至少需要的条目数（默认 10）")
    args = ap.parse_args()

    pool = load_json(os.path.abspath(args.candidate_pool_json))
    out = load_json(os.path.abspath(args.ai_output_json))
    errors = validate_subset(pool, out, topk=args.topk)
    if errors:
        print("INVALID")
        for e in errors:
            print("-", e)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

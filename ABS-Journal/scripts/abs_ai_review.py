#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Hybrid journal recommendation: script candidate pool -> AI second pass (manual) -> validation.

This script does NOT call external APIs. It validates that an AI-produced selection
is strictly a subset of the candidate pool exported by abs_article_impl.py.

Usage (example):
  python3 /Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/scripts/abs_article_impl.py \\
    --ajg_csv /Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/assets/data/ajg_2024_journals_core_custom.csv \\
    --field ECON --profile general --mode fit --topk 200 \\
    --title \"...\" --abstract \"...\" \\
    --export_candidate_pool_json /tmp/candidate_pool.json

  # (You paste / generate AI output as JSON into /tmp/ai_output.json)
  python3 /Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal/scripts/abs_ai_review.py \\
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


def validate_subset(candidate_pool: Dict[str, Any], ai_output: Dict[str, Any]) -> List[str]:
    # Support two shapes:
    # A) Single pool: {"meta": ..., "candidates": [...]}
    # B) Multi pools (recommended): {"fit": {...}, "easy": {...}, "value": {...}}
    if any(k in candidate_pool for k in ["fit", "easy", "value"]):
        allowed_by_bucket: Dict[str, set] = {}
        for bucket in ["fit", "easy", "value"]:
            pool = candidate_pool.get(bucket) or {}
            cands = (pool.get("candidates") if isinstance(pool, dict) else []) or []
            s = {c.get("journal") for c in cands if isinstance(c, dict)}
            s.discard(None)
            allowed_by_bucket[bucket] = s
    else:
        cands = candidate_pool.get("candidates") or []
        s = {c.get("journal") for c in cands if isinstance(c, dict)}
        s.discard(None)
        allowed_by_bucket = {b: s for b in ["fit", "easy", "value"]}

    errors: List[str] = []
    for bucket in ["fit", "easy", "value"]:
        items = ai_output.get(bucket) or []
        if not isinstance(items, list):
            errors.append(f"{bucket}: 输出必须是 list")
            continue
        allowed = allowed_by_bucket.get(bucket) or set()
        for idx, it in enumerate(items, 1):
            if not isinstance(it, dict):
                errors.append(f"{bucket}[{idx}]: 每条必须是 dict")
                continue
            j = it.get("journal")
            if j not in allowed:
                errors.append(f"{bucket}[{idx}]: 期刊不在候选池: {j!r}")
            if not it.get("topic"):
                errors.append(f"{bucket}[{idx}]: 缺少 topic 字段")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate_pool_json", required=True, help="候选池 JSON（绝对路径；可为单池或 fit/easy/value 多池）")
    ap.add_argument("--ai_output_json", required=True, help="AI 输出 JSON（绝对路径）")
    args = ap.parse_args()

    pool = load_json(os.path.abspath(args.candidate_pool_json))
    out = load_json(os.path.abspath(args.ai_output_json))
    errors = validate_subset(pool, out)
    if errors:
        print("INVALID")
        for e in errors:
            print("-", e)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

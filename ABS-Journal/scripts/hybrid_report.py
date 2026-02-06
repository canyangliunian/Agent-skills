#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Render hybrid recommendation report from:
- candidate pool JSON exported by abs_article_impl.py
- AI output JSON (validated subset)

This script does NOT call external APIs. It only formats a report.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List, Tuple


def load_json_abs(path: str) -> Dict[str, Any]:
    if not os.path.isabs(path):
        raise RuntimeError(f"路径必须是绝对路径: {path}")
    if not os.path.exists(path):
        raise RuntimeError(f"JSON 不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def md_escape(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def build_index(pool: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for c in pool.get("candidates") or []:
        if not isinstance(c, dict):
            continue
        j = (c.get("journal") or "").strip()
        if j:
            out[j] = c
    return out


def build_index_multi(pool_multi: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    out: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for bucket in ["easy", "medium", "hard"]:
        pool = pool_multi.get(bucket) or {}
        if not isinstance(pool, dict):
            continue
        out[bucket] = build_index(pool)
    return out


def normalize_ai(ai: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for bucket in ["easy", "medium", "hard"]:
        items = ai.get(bucket) or []
        if not isinstance(items, list):
            raise RuntimeError(f"{bucket}: AI 输出必须是 list")
        norm: List[Dict[str, Any]] = []
        for it in items:
            if not isinstance(it, dict):
                raise RuntimeError(f"{bucket}: 每条必须是 dict")
            j = (it.get("journal") or "").strip()
            topic = (it.get("topic") or "").strip()
            if not j:
                raise RuntimeError(f"{bucket}: 缺少 journal")
            if not topic:
                raise RuntimeError(f"{bucket}: {j}: 缺少 topic")
            norm.append({"journal": j, "topic": topic})
        out[bucket] = norm
    return out


def star_label(v: str) -> str:
    return (v or "").strip()


def render_table(
    bucket_title: str,
    items: List[Dict[str, Any]],
    idx: Dict[str, Dict[str, Any]],
    topk: int,
) -> str:
    lines: List[str] = []
    lines.append(f"### {bucket_title}")
    lines.append("")
    lines.append("| 序号 | 期刊名 | ABS星级 | 期刊主题 |")
    lines.append("|---:|---|---:|---|")

    count = 0
    for i, it in enumerate(items, 1):
        if count >= topk:
            break
        j = it["journal"]
        cand = idx.get(j) or {}
        rating = star_label(str(cand.get("ajg_2024") or ""))
        topic = it["topic"]
        lines.append(f"| {i} | {md_escape(j)} | {md_escape(rating)} | {md_escape(topic)} |")
        count += 1
    lines.append("")
    return "\n".join(lines)


def extract_meta(pool: Dict[str, Any]) -> Dict[str, Any]:
    meta = pool.get("meta") or {}
    if not isinstance(meta, dict):
        return {}
    return meta


def is_multi_pool(obj: Dict[str, Any]) -> bool:
    return any(k in obj for k in ["easy", "medium", "hard"])


def render_report(
    pool: Dict[str, Any],
    ai: Dict[str, Any],
    *,
    topk: int,
) -> str:
    if is_multi_pool(pool):
        meta_easy = extract_meta(pool.get("easy") or {})
        meta_medium = extract_meta(pool.get("medium") or {})
        meta_hard = extract_meta(pool.get("hard") or {})
        idx_multi = build_index_multi(pool)
        meta = meta_medium or meta_easy or meta_hard
    else:
        meta = extract_meta(pool)
        idx_multi = {"easy": build_index(pool), "medium": build_index(pool), "hard": build_index(pool)}
    ai_norm = normalize_ai(ai)

    lines: List[str] = []
    lines.append("# 投稿期刊推荐（混合流程：脚本候选池 → AI 二次筛选）")
    lines.append("")
    lines.append("## 可追溯信息")
    lines.append("")
    if is_multi_pool(pool):
        lines.append("- 候选池形态：easy/medium/hard 多池（每段各自星级过滤与排序）")
        for label, m in [("Easy", meta_easy), ("Medium", meta_medium), ("Hard", meta_hard)]:
            if not m:
                continue
            lines.append(f"- {label}：AJG CSV={m.get('ajg_csv')}；星级过滤={m.get('rating_filter')}；规模={m.get('count')}")
    else:
        if meta.get("generated_at"):
            lines.append(f"- 候选池生成时间：{meta.get('generated_at')}")
        if meta.get("ajg_csv"):
            lines.append(f"- AJG CSV：{meta.get('ajg_csv')}")
        if meta.get("mode"):
            lines.append(f"- 候选池难度：{meta.get('mode')}")
        if meta.get("rating_filter"):
            lines.append(f"- 星级过滤：{meta.get('rating_filter')}")
        gating = meta.get("gating")
        if isinstance(gating, dict):
            lines.append(f"- 主题贴合候选集：{gating.get('total_after')}（筛选前：{gating.get('total_before')}）")
            lines.append(f"- gating 策略：{gating.get('strategy')}，TopN={gating.get('candidate_topn')}，回退={gating.get('fallback_used')}")
        lines.append(f"- 候选池规模：{meta.get('count')}")
    lines.append("")
    lines.append("## 论文信息")
    lines.append("")
    paper = meta.get("paper") if isinstance(meta.get("paper"), dict) else {}
    if paper.get("title"):
        lines.append(f"- 标题：{paper.get('title')}")
    if paper.get("abstract"):
        lines.append(f"- 摘要：{paper.get('abstract')}")
    lines.append("")
    lines.append("## 推荐清单（固定列）")
    lines.append("")
    lines.append(render_table("Easy Top10", ai_norm["easy"], idx_multi.get("easy") or {}, topk))
    lines.append(render_table("Medium Top10", ai_norm["medium"], idx_multi.get("medium") or {}, topk))
    lines.append(render_table("Hard Top10", ai_norm["hard"], idx_multi.get("hard") or {}, topk))
    lines.append("## 说明")
    lines.append("")
    lines.append("- `期刊主题` 为 AI 解释性摘要，用于解释与论文主题的匹配关系；不是期刊官方 Aims&Scope。")
    lines.append("- 本流程不自动联网查询审稿周期/版面费/投稿偏好等信息。")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate_pool_json", required=True, help="候选池 JSON（绝对路径）")
    ap.add_argument("--ai_output_json", required=True, help="AI 输出 JSON（绝对路径，需已通过子集校验）")
    ap.add_argument("--topk", type=int, default=10, help="每段输出 TopK（默认10）")
    args = ap.parse_args()

    pool = load_json_abs(os.path.abspath(args.candidate_pool_json))
    ai = load_json_abs(os.path.abspath(args.ai_output_json))
    print(render_report(pool, ai, topk=int(args.topk)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

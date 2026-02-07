#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ABS-Journal unified CLI (local-first).

Default behavior:
- Recommend journals using local AJG CSV (no network).

Only update when explicitly requested:
- Pass --update to fetch the latest AJG dataset into --data_dir.

Examples (portable; absolute paths can be derived at runtime):
  # Recommend (default)
  python3 scripts/abs_journal.py \\
    recommend --title "..." --abstract "..." --mode medium

  # Update then recommend
  export AJG_EMAIL="lingguiwang@yeah.net"
  export AJG_PASSWORD="..."
  python3 scripts/abs_journal.py \\
    recommend --update --data_dir "$(pwd)/assets/data" \\
    --title "..." --abstract "..."
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

from abs_paths import data_dir as default_data_dir
from abs_paths import reports_dir as default_reports_dir
from abs_paths import skill_root as resolve_skill_root


SKILL_ROOT = str(resolve_skill_root())

DEFAULT_EXPORT_DIR = os.path.join(SKILL_ROOT, "assets")  # legacy; reports go to DEFAULT_REPORTS_DIR
DEFAULT_REPORTS_DIR = str(default_reports_dir())

DEFAULT_AI_OUTPUT_JSON = "ai_output.json"
DEFAULT_AI_REPORT_MD = "ai_report.md"

# Default rating buckets for a more intuitive difficulty layering.
# Users can override via --rating_filter explicitly.
DEFAULT_RATING_FILTER_BY_MODE = {
    "easy": "1,2",
    "medium": "2,3",
    "hard": "4,4*",
}


def resolve_inside_skill(path: str, *, base_dir: str) -> str:
    """Resolve a user path so that relative paths land inside this skill.

    - If `path` is absolute: keep as-is (user explicitly chose an external location).
    - If `path` is relative: resolve under `base_dir` (which should be inside SKILL_ROOT).
    """
    if not path:
        return ""
    if os.path.isabs(path):
        return os.path.abspath(path)
    # Avoid accidental duplication like "assets/assets/foo.json" when callers pass "assets/foo.json"
    path = strip_leading_dirs(path, "assets", "assets/assets", "reports", "reports/reports")
    return os.path.abspath(os.path.join(base_dir, path))


def strip_leading_dirs(path: str, *dirs: str) -> str:
    p = path.replace("\\", "/")
    for d in dirs:
        d2 = d.strip("/").replace("\\", "/")
        if not d2:
            continue
        if p.startswith(d2 + "/"):
            return p[len(d2) + 1 :]
    return path


def run_py(script_rel: str, argv: List[str]) -> int:
    script = os.path.join(SKILL_ROOT, script_rel)
    if not os.path.isfile(script):
        raise RuntimeError(f"脚本不存在: {script}")
    import subprocess

    proc = subprocess.run([sys.executable, script, *argv])
    return int(proc.returncode)


def _load_candidate_pools(export_json_list: List[str]) -> List[dict]:
    import json

    pools: List[dict] = []
    for p in export_json_list:
        if not p:
            continue
        with open(p, "r", encoding="utf-8") as f:
            pools.append(json.load(f))
    return pools


def _select_topk_from_pools(export_json_list: List[str], *, topk: int) -> dict:
    """Auto-pick top journals from candidate pools (offline; no external API)."""
    pools = _load_candidate_pools(export_json_list)
    if not pools:
        raise RuntimeError("未找到候选池 JSON（请先生成候选池）")

    modes = ["easy", "medium", "hard"]

    by_mode = {}
    for pool in pools:
        meta = (pool or {}).get("meta") or {}
        mode = (meta.get("mode") or "").strip() or "unknown"
        by_mode[mode] = pool

    def pick_from(pool: dict) -> List[dict]:
        candidates = (pool or {}).get("candidates") or []

        def key(c: dict):
            s = (c or {}).get("signals") or {}
            return (float(s.get("total_score") or 0.0), float(s.get("fit_score") or 0.0))

        ranked = sorted(candidates, key=key, reverse=True)
        picked = []
        for c in ranked[:topk]:
            picked.append(
                {
                    "journal": c.get("journal", ""),
                    "ajg_2024": c.get("ajg_2024", ""),
                    "topic": "根据候选池打分（主题贴合/可投稿性/价值权重等）自动筛选",
                }
            )
        return picked

    # Ensure non-overlap across easy/medium/hard.
    #
    # Note: candidate pools can be intentionally rebalanced to be near 1:1 by rating,
    # which might shrink pool sizes (e.g., medium could be ~10). In that case, strict
    # cross-bucket uniqueness can make --auto_ai fail unnecessarily. We therefore apply
    # uniqueness as best-effort: avoid overlap when possible, but allow overlap as a
    # fallback to guarantee TopK.
    picked_names = set()

    def pick_unique(mode: str) -> List[dict]:
        pool = by_mode.get(mode) or pools[0]
        candidates = (pool or {}).get("candidates") or []

        def key(c: dict):
            s = (c or {}).get("signals") or {}
            return (float(s.get("total_score") or 0.0), float(s.get("fit_score") or 0.0))

        ranked = sorted(candidates, key=key, reverse=True)
        out: List[dict] = []
        for c in ranked:
            name = (c.get("journal") or "").strip()
            if not name or name in picked_names:
                continue
            out.append(
                {
                    "journal": name,
                    "ajg_2024": c.get("ajg_2024", ""),
                    "topic": "根据候选池打分（主题贴合/可投稿性/价值权重等）自动筛选",
                }
            )
            picked_names.add(name)
            if len(out) >= topk:
                break
        if len(out) < topk:
            # Fallback: allow overlap if needed to complete TopK.
            for c in ranked:
                name = (c.get("journal") or "").strip()
                if not name:
                    continue
                out.append(
                    {
                        "journal": name,
                        "ajg_2024": c.get("ajg_2024", ""),
                        "topic": "根据候选池打分（主题贴合/可投稿性/价值权重等）自动筛选",
                    }
                )
                if len(out) >= topk:
                    break
        if len(out) < topk:
            raise RuntimeError(f"--auto_ai 生成失败：{mode} 仅选到 {len(out)}/{topk}（候选池不足）")
        return out

    ai_obj = {m: pick_unique(m) for m in modes}

    # If we were given multiple pools (easy/medium/hard), embed them so that
    # subset validation can correctly validate per-bucket membership.
    multi_pool = len(pools) > 1 or any(k in by_mode for k in modes)
    if multi_pool:
        ai_obj["candidate_pool_by_mode"] = {m: (by_mode.get(m) or {}) for m in modes}
        # In multi-pool mode, allow overlap across buckets by default for --auto_ai,
        # since validation will be performed per-bucket membership. Cross-bucket
        # non-overlap is a nice-to-have but can fail when pools are intentionally
        # rebalanced or small.
        ai_obj.setdefault("meta", {})
        if isinstance(ai_obj["meta"], dict):
            ai_obj["meta"]["allow_overlap"] = True

    # Merge meta (may already exist).
    meta = ai_obj.get("meta")
    if not isinstance(meta, dict):
        meta = {}
    meta["generated_by"] = "abs_journal.py --auto_ai"
    ai_obj["meta"] = meta
    return ai_obj


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_rec = sub.add_parser("recommend", help="基于本地AJG数据推荐投稿期刊（默认不更新）")
    ap_rec.add_argument("--update", action="store_true", help="显式更新AJG数据库后再推荐（默认不更新）")
    ap_rec.add_argument(
        "--data_dir",
        default=str(default_data_dir()),
        help="AJG数据目录（绝对路径推荐）",
    )
    ap_rec.add_argument("--title", required=True, help="论文标题")
    ap_rec.add_argument("--abstract", default="", help="论文摘要")
    ap_rec.add_argument("--field", default="ECON", help="论文领域标签/关键词配置（默认ECON；不控制候选范围）")
    ap_rec.add_argument(
        "--field_scope",
        default="",
        help=(
            "候选期刊 Field 白名单（AJG CSV 的 Field 列，逗号分隔；精确匹配）。"
            "默认（留空）即使用内置 5 个 Field 白名单：ECON, FINANCE, PUB SEC, REGIONAL STUDIES, PLANNING AND ENVIRONMENT, SOC SCI。"
            "如需只看某一个领域，请显式传入（例如：--field_scope ECON）。"
        ),
    )
    ap_rec.add_argument("--mode", default="easy", choices=["easy", "medium", "hard"], help="投稿难度：easy(最容易)/medium(中等)/hard(最困难)")
    ap_rec.add_argument("--topk", type=int, default=10, help="每个难度输出期刊数（默认10）")
    ap_rec.add_argument(
        "--export_candidate_pool_json",
        default="",
        help="导出候选池 JSON（用于 AI 二次筛选）。为空则不导出。相对路径将写入本 skill 的 reports/ 下。",
    )
    ap_rec.add_argument(
        "--hybrid",
        action="store_true",
        help="启用混合流程：脚本导出候选池 JSON，然后由 AI（人工/外部）在候选池内二次筛选；本脚本不调用外部 API。",
    )
    ap_rec.add_argument(
        "--ai_output_json",
        default=DEFAULT_AI_OUTPUT_JSON,
        help="AI 二次筛选输出 JSON（仅在 --hybrid 时使用）。相对路径将从本 skill 的 reports/ 下解析。",
    )
    ap_rec.add_argument(
        "--auto_ai",
        action="store_true",
        help="自动生成 AI 输出 JSON（离线；不调用外部 API），并继续执行子集校验与报告生成（需同时提供 --ai_output_json 与 --ai_report_md）",
    )
    ap_rec.add_argument(
        "--ai_report_md",
        default=DEFAULT_AI_REPORT_MD,
        help="混合流程最终报告 Markdown 输出路径。相对路径将写入本 skill 的 reports/ 下；需同时提供 --ai_output_json。",
    )
    ap_rec.add_argument(
        "--rating_filter",
        default="",
        help="AJG/ABS 星级过滤（逗号分隔，如: 1,2,3 或 3,4,4*）。默认将按 mode 自动分层：easy=1,2；medium=2,3；hard=4,4*。显式传入则覆盖默认。",
    )

    ap_up = sub.add_parser("update", help="更新AJG数据库（需要 env: AJG_EMAIL/AJG_PASSWORD）")
    ap_up.add_argument(
        "--data_dir",
        default=str(default_data_dir()),
        help="输出数据目录（绝对路径推荐）",
    )
    ap_up.add_argument("--overwrite", action="store_true", help="允许覆盖既有输出文件（默认不覆盖）")
    ap_up.add_argument("--debug-http", action="store_true")

    args, unknown = ap.parse_known_args()

    if args.cmd == "update":
        fetch_args = [
            "--outdir",
            os.path.abspath(args.data_dir),
        ]
        if args.overwrite:
            fetch_args.append("--overwrite")
        if args.debug_http:
            fetch_args.append("--debug-http")
        return run_py("scripts/ajg_fetch.py", fetch_args)

    if args.cmd == "recommend":
        data_dir = os.path.abspath(args.data_dir)
        os.makedirs(DEFAULT_REPORTS_DIR, exist_ok=True)
        if args.update:
            fetch_args = ["--outdir", data_dir]
            returncode = run_py("scripts/ajg_fetch.py", fetch_args)
            if returncode != 0:
                return returncode

        # Default local file in this repo. If you updated to a newer year,
        # pass --ajg_csv explicitly via direct call to abs_article_impl.py,
        # or update this mapping later.
        raw_export = (args.export_candidate_pool_json or "").strip()
        raw_export = strip_leading_dirs(raw_export, "reports", "reports/reports", "assets", "assets/assets")
        export_json = resolve_inside_skill(raw_export, base_dir=DEFAULT_REPORTS_DIR) if raw_export else ""
        if args.hybrid and not export_json:
            export_json = resolve_inside_skill("candidate_pool.json", base_dir=DEFAULT_REPORTS_DIR)

        modes = ["easy", "medium", "hard"]
        if args.mode and args.mode not in modes:
            raise RuntimeError(f"非法 --mode: {args.mode}（允许：easy/medium/hard）")

        # Default: always generate a theme-fit candidate pool first (mode-agnostic gating),
        # then rank within that pool for each difficulty bucket.
        selected_modes = modes if args.hybrid else [args.mode]
        if not selected_modes or any(m not in modes for m in selected_modes):
            raise RuntimeError("内部错误：selected_modes 为空或包含非法值")

        multi_pool = bool(args.hybrid)
        export_json_list = []
        if multi_pool:
            base, ext = os.path.splitext(export_json)
            export_json_list = [f"{base}_{m}{ext or '.json'}" for m in selected_modes]
        else:
            export_json_list = [export_json] if export_json else [""]

        for m, out_json in zip(selected_modes, export_json_list):
            rating_filter = (args.rating_filter or "").strip()
            if not rating_filter:
                rating_filter = DEFAULT_RATING_FILTER_BY_MODE.get(m, "")
            rec_args = [
                "--ajg_csv",
                os.path.join(data_dir, "ajg_2024_journals_core_custom.csv"),
                "--title",
                args.title,
                "--abstract",
                args.abstract,
                "--field",
                args.field,
                "--field_scope",
                args.field_scope,
                "--mode",
                m,
                "--topk",
                str(args.topk),
                "--export_candidate_pool_json",
                out_json,
                "--rating_filter",
                rating_filter,
            ]
            returncode = run_py("scripts/abs_article_impl.py", rec_args)
            if returncode != 0:
                return returncode

        if not args.hybrid:
            return 0

        if export_json_list:
            print("")
            print("已生成候选池 JSON：")
            for p in export_json_list:
                if p:
                    print("-", p)

        # Validate AI output (manual step) if provided.
        if args.ai_output_json:
            if not export_json_list or any((not p) for p in export_json_list):
                raise RuntimeError("混合流程需要候选池 JSON 输出（请提供 --export_candidate_pool_json）")
            pool_arg = export_json_list if multi_pool else export_json_list[0]
            ai_output_path = resolve_inside_skill(args.ai_output_json, base_dir=DEFAULT_REPORTS_DIR)

            if args.auto_ai:
                if not args.ai_report_md:
                    raise RuntimeError("--auto_ai 需要同时提供 --ai_report_md（用于输出最终报告）")
                os.makedirs(os.path.dirname(ai_output_path) or ".", exist_ok=True)
                import json

                auto = _select_topk_from_pools(export_json_list, topk=args.topk)
                with open(ai_output_path, "w", encoding="utf-8") as f:
                    json.dump(auto, f, ensure_ascii=False, indent=2)
                print(f"已自动生成 AI 输出 JSON：{ai_output_path}")

            returncode = run_py(
                "scripts/abs_ai_review.py",
                [
                    "--candidate_pool_json",
                    # For --auto_ai, we embed candidate pools into ai_output.json, so pass that file.
                    ai_output_path if args.auto_ai else (pool_arg if isinstance(pool_arg, str) else pool_arg[0]),
                    "--ai_output_json",
                    ai_output_path,
                    "--topk",
                    str(args.topk),
                ],
            )
            if returncode != 0:
                return returncode

            if args.ai_report_md:
                out_md = resolve_inside_skill(args.ai_report_md, base_dir=DEFAULT_REPORTS_DIR)
                os.makedirs(os.path.dirname(out_md) or ".", exist_ok=True)
                import subprocess

                pool_for_report = pool_arg if isinstance(pool_arg, str) else pool_arg[0]
                proc = subprocess.run(
                    [
                        sys.executable,
                        os.path.join(SKILL_ROOT, "scripts", "hybrid_report.py"),
                        "--candidate_pool_json",
                        pool_for_report,
                        "--ai_output_json",
                        ai_output_path,
                        "--topk",
                        str(args.topk),
                    ],
                    capture_output=True,
                    text=True,
                )
                if proc.returncode != 0:
                    print(proc.stdout, end="")
                    print(proc.stderr, end="", file=sys.stderr)
                    return int(proc.returncode)
                with open(out_md, "w", encoding="utf-8") as f:
                    f.write(proc.stdout)
                print(f"已写入混合流程报告：{out_md}")
            return 0

        print("")
        print("已生成候选池 JSON。下一步：将候选池提供给 AI 二次筛选，并保存 AI 输出为 JSON，然后用 --ai_output_json 校验。")
        print(f"- 候选池：{export_json}")
        return 0

    raise RuntimeError(f"unknown cmd: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())

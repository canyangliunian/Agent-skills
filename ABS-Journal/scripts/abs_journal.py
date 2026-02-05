#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ABS-Journal unified CLI (local-first).

Default behavior:
- Recommend journals using local AJG CSV (no network).

Only update when explicitly requested:
- Pass --update to fetch the latest AJG dataset into --data_dir.

Examples (absolute paths recommended):
  # Recommend (default)
  python3 /Users/lingguiwang/.agents/skills/abs-journal/scripts/abs_journal.py \\
    recommend --title "..." --abstract "..." --mode fit

  # Update then recommend
  export AJG_EMAIL="lingguiwang@yeah.net"
  export AJG_PASSWORD="..."
  python3 /Users/lingguiwang/.agents/skills/abs-journal/scripts/abs_journal.py \\
    recommend --update --data_dir /Users/lingguiwang/.agents/skills/abs-journal/assets/data \\
    --title "..." --abstract "..."
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List


SKILL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run_py(script_rel: str, argv: List[str]) -> int:
    script = os.path.join(SKILL_ROOT, script_rel)
    if not os.path.isfile(script):
        raise RuntimeError(f"脚本不存在: {script}")
    import subprocess

    proc = subprocess.run([sys.executable, script, *argv])
    return int(proc.returncode)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_rec = sub.add_parser("recommend", help="基于本地AJG数据推荐投稿期刊（默认不更新）")
    ap_rec.add_argument("--update", action="store_true", help="显式更新AJG数据库后再推荐（默认不更新）")
    ap_rec.add_argument(
        "--data_dir",
        default=os.path.join(SKILL_ROOT, "assets", "data"),
        help="AJG数据目录（绝对路径推荐）",
    )
    ap_rec.add_argument("--title", required=True, help="论文标题")
    ap_rec.add_argument("--abstract", default="", help="论文摘要")
    ap_rec.add_argument("--field", default="ECON", help="论文领域（默认ECON）")
    ap_rec.add_argument("--mode", default="easy", choices=["easy", "fit", "value"], help="推荐模式")
    ap_rec.add_argument("--topk", type=int, default=20, help="输出期刊数")

    ap_up = sub.add_parser("update", help="更新AJG数据库（需要 env: AJG_EMAIL/AJG_PASSWORD）")
    ap_up.add_argument(
        "--data_dir",
        default=os.path.join(SKILL_ROOT, "assets", "data"),
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
        if args.update:
            fetch_args = ["--outdir", data_dir]
            returncode = run_py("scripts/ajg_fetch.py", fetch_args)
            if returncode != 0:
                return returncode

        # Default local file in this repo. If you updated to a newer year,
        # pass --ajg_csv explicitly via direct call to abs_article_impl.py,
        # or update this mapping later.
        rec_args = [
            "--ajg_csv",
            os.path.join(data_dir, "ajg_2024_journals_core_custom.csv"),
            "--title",
            args.title,
            "--abstract",
            args.abstract,
            "--field",
            args.field,
            "--mode",
            args.mode,
            "--topk",
            str(args.topk),
        ]
        return run_py("scripts/abs_article_impl.py", rec_args)

    raise RuntimeError(f"unknown cmd: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())

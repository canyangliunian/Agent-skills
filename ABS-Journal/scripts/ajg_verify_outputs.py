#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Offline verification for AJG outputs.

Design goals:
- Works without network access (only reads local outputs).
- No third-party dependencies (stdlib only).
- Fast, explicit failure messages for CI-like checks.

Usage (absolute paths recommended):
  python3 /Users/lingguiwang/.agents/skills/abs-journal/scripts/ajg_verify_outputs.py \
    --outdir /Users/lingguiwang/.agents/skills/abs-journal/assets/data

It checks:
- Required files exist for the latest discovered year in the directory (by filename).
- meta.json contains required keys.
- CSV has a header row and includes minimal columns (AJG 2024 / Journal Title / Field when present).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from typing import List, Optional, Tuple


YEAR_RE = re.compile(r"^ajg_(\d{4})_journals_core_custom\.csv$")


def find_latest_year(outdir: str) -> Tuple[int, str]:
    candidates: List[Tuple[int, str]] = []
    for name in os.listdir(outdir):
        m = YEAR_RE.match(name)
        if not m:
            continue
        year = int(m.group(1))
        candidates.append((year, name))
    if not candidates:
        raise RuntimeError("在输出目录中未发现形如 ajg_<year>_journals_core_custom.csv 的文件")
    year, csv_name = sorted(candidates, key=lambda x: x[0])[-1]
    return year, csv_name


def require_file(path: str) -> None:
    if not os.path.isfile(path):
        raise RuntimeError(f"缺少文件或不是普通文件: {path}")


def load_meta(meta_path: str) -> dict:
    with open(meta_path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise RuntimeError(f"meta.json 不是 JSON object: {meta_path}")
    return obj


def verify_meta(meta: dict, meta_path: str) -> None:
    required = ["retrieved_at_utc", "ajg_year", "entrypoint_url"]
    missing = [k for k in required if k not in meta]
    if missing:
        raise RuntimeError(f"meta.json 缺少必要字段 {missing}: {meta_path}")


def verify_csv_header(csv_path: str) -> None:
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
    if not header:
        raise RuntimeError(f"CSV 缺少表头行: {csv_path}")
    header_norm = [h.strip() for h in header if h is not None]
    # Minimal expectations for the custom display order in this repo.
    expected_any = {"Journal Title", "Journal", "title"}
    if not any(h in expected_any for h in header_norm):
        raise RuntimeError(f"CSV 表头缺少期刊名称列（Journal Title/Journal/title 其一）: {csv_path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True, help="AJG 输出目录（绝对路径推荐）")
    ap.add_argument("--year", type=int, default=None, help="指定年份（默认自动选择目录中最新年份）")
    args = ap.parse_args()

    outdir = os.path.abspath(args.outdir)
    if not os.path.isabs(outdir):
        raise RuntimeError("--outdir 必须是绝对路径")
    if not os.path.isdir(outdir):
        raise RuntimeError(f"输出目录不存在或不是目录: {outdir}")

    if args.year is None:
        year, _ = find_latest_year(outdir)
    else:
        year = int(args.year)

    raw_path = os.path.join(outdir, f"ajg_{year}_journals_raw.jsonl")
    meta_path = os.path.join(outdir, f"ajg_{year}_meta.json")
    csv_path = os.path.join(outdir, f"ajg_{year}_journals_core_custom.csv")

    require_file(raw_path)
    require_file(meta_path)
    require_file(csv_path)

    meta = load_meta(meta_path)
    verify_meta(meta, meta_path)
    verify_csv_header(csv_path)

    sys.stdout.write(f"OK: year={year} outdir={outdir}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        raise

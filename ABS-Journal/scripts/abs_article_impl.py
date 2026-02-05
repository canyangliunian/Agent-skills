#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ABS-Journal: Recommend target journals using AJG core catalog.

This is the implementation script (moved from the legacy ABS-article skill).
It does NOT use external web resources; it relies only on the local AJG CSV.

Inputs:
- title (required)
- abstract (optional)
- mode (default: easy; options: easy/fit/value)

Outputs:
- a Markdown report to stdout

Default AJG CSV (absolute path):
  /Users/lingguiwang/Documents/Coding/LLM/09ABS/assets/data/ajg_2024_journals_core_custom.csv
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


DEFAULT_AJG_CSV = "/Users/lingguiwang/Documents/Coding/LLM/09ABS/assets/data/ajg_2024_journals_core_custom.csv"


ANSI_RESET = "\x1b[0m"
ANSI_BOLD = "\x1b[1m"
ANSI_CYAN = "\x1b[36m"
ANSI_GREEN = "\x1b[32m"
ANSI_YELLOW = "\x1b[33m"


def supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    term = os.environ.get("TERM", "")
    return term != "" and term.lower() != "dumb"


def c(s: str, color: str) -> str:
    if not supports_color():
        return s
    return f"{color}{s}{ANSI_RESET}"


class ColorHelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action: argparse.Action) -> str:
        text = super()._format_action_invocation(action)
        if not supports_color():
            return text

        parts = text.split()
        if not parts:
            return text

        out = []
        for p in parts:
            if p.startswith("-"):
                out.append(c(p, ANSI_CYAN + ANSI_BOLD))
            elif p.isupper() or "_" in p:
                out.append(c(p, ANSI_YELLOW + ANSI_BOLD))
            else:
                out.append(p)
        return " ".join(out)


@dataclass(frozen=True)
class PaperProfile:
    field: str
    title: str
    abstract: str
    mode: str


@dataclass
class JournalRow:
    field: str
    title: str
    ajg_2024: str
    ajg_2021: str
    citescore_rank: str
    snip_rank: str
    sjr_rank: str
    jif_rank: str
    sdg_pct: str
    intl_pct: str
    collab_pct: str
    policy_value: str


def now_local_str() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def normalize_text(s: str) -> str:
    t = (s or "").lower()
    t = re.sub(r"[^a-z0-9\s-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def parse_ajg_rating(r: str) -> Tuple[int, bool]:
    s = (r or "").strip()
    if s == "4*":
        return 4, True
    if s in {"1", "2", "3", "4"}:
        return int(s), False
    return 4, True


def easiness_score(ajg_2024: str) -> float:
    level, star = parse_ajg_rating(ajg_2024)
    base = {1: 4.0, 2: 3.0, 3: 2.0, 4: 1.0}.get(level, 1.0)
    if level == 4 and star:
        base -= 0.4
    return base


def keyword_score(paper: PaperProfile, journal: JournalRow) -> float:
    text = normalize_text(paper.title + " " + paper.abstract)

    keywords = {
        "tariff": 1.5,
        "trade": 1.0,
        "trade war": 2.0,
        "retaliatory": 2.0,
        "protection": 1.2,
        "policy": 0.8,
        "public opinion": 1.8,
        "attitudes": 1.2,
        "beliefs": 1.0,
        "collectiv": 1.0,
        "trust": 1.0,
        "human capital": 1.0,
        "random": 0.8,
        "experiment": 1.2,
        "randomised": 1.2,
        "randomized": 1.2,
        "trial": 1.0,
        "survey": 0.8,
        "agricultur": 1.5,
        "food": 1.0,
        "china": 1.0,
        "us china": 1.2,
    }

    score = 0.0
    for k, w in keywords.items():
        if k in text:
            score += w

    if journal.field in {"ECON", "IB&AREA", "PUB SEC"}:
        score += 0.5

    return score


def parse_rank_int(s: str) -> int:
    try:
        return int(float((s or "").strip()))
    except Exception:
        return 10**9


def prestige_penalty(journal: JournalRow) -> float:
    penalties = []
    for r in [journal.citescore_rank, journal.snip_rank, journal.sjr_rank, journal.jif_rank]:
        v = parse_rank_int(r)
        if v <= 10:
            penalties.append(1.2)
        elif v <= 30:
            penalties.append(0.6)
        else:
            penalties.append(0.0)
    return sum(penalties)


def total_score(paper: PaperProfile, journal: JournalRow) -> Dict[str, float]:
    k = keyword_score(paper, journal)
    e = easiness_score(journal.ajg_2024)
    p = prestige_penalty(journal)

    if paper.mode == "fit":
        total = (2.2 * k) + (0.6 * e) - (0.4 * p)
    elif paper.mode == "value":
        ajg_level, ajg_star = parse_ajg_rating(journal.ajg_2024)
        quality = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}.get(ajg_level, 1.0)
        if ajg_level == 4 and ajg_star:
            quality += 0.2
        total = (1.4 * quality) + (1.2 * k) + (0.2 * e) - (0.8 * p)
    else:
        total = (2.0 * e) + (1.2 * k) - (1.0 * p)

    return {"total": total, "easy": e, "kw": k, "prestige_pen": p}


def load_ajg_csv(path: str) -> List[JournalRow]:
    if not os.path.isabs(path):
        raise RuntimeError("--ajg_csv 必须是绝对路径")
    if not os.path.exists(path):
        raise RuntimeError(f"AJG CSV 不存在: {path}")

    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        rows = []
        for row in r:
            rows.append(
                JournalRow(
                    field=(row.get("Field") or "").strip(),
                    title=(row.get("Journal Title") or "").strip(),
                    ajg_2024=(row.get("AJG 2024") or "").strip(),
                    ajg_2021=(row.get("AJG 2021") or "").strip(),
                    citescore_rank=(row.get("Citescore rank") or "").strip(),
                    snip_rank=(row.get("SNIP rank") or "").strip(),
                    sjr_rank=(row.get("SJR rank") or "").strip(),
                    jif_rank=(row.get("JIF rank") or "").strip(),
                    sdg_pct=(row.get("SDG content indicator (2017-21)") or "").strip(),
                    intl_pct=(row.get("International co-authorship (2017-21)") or "").strip(),
                    collab_pct=(row.get("Academic-non-academic collaboration (2017-21)") or "").strip(),
                    policy_value=(row.get("Citations in policy documents (2017-21)") or "").strip(),
                )
            )
        return rows


def pick_candidates(rows: List[JournalRow], paper_field: str) -> List[JournalRow]:
    allowed = {paper_field}
    if paper_field == "ECON":
        allowed |= {"IB&AREA", "PUB SEC", "REGIONAL STUDIES, PLANNING AND ENVIRONMENT"}
    return [r for r in rows if r.field in allowed]


def group_bucket(ajg_2024: str) -> str:
    level, star = parse_ajg_rating(ajg_2024)
    if level in {1, 2}:
        return "A 主投更易"
    if level == 3:
        return "B 备投折中"
    if level == 4 and star:
        return "C 冲刺更高（4*）"
    return "C 冲刺更高（4）"


def md_escape(s: str) -> str:
    return (s or "").replace("|", "\\|")


def render_report(paper: PaperProfile, ranked: List[Tuple[JournalRow, Dict[str, float]]], topk: int) -> str:
    lines: List[str] = []
    lines.append("# 投稿期刊推荐（基于AJG目录）")
    lines.append("")
    lines.append(f"- 生成时间：{now_local_str()}")
    lines.append(f"- 论文领域：{paper.field}")
    lines.append(f"- 模式：{paper.mode}")
    lines.append("")
    lines.append("## 论文信息")
    lines.append("")
    lines.append(f"- 标题：{paper.title}")
    if paper.abstract:
        lines.append(f"- 摘要：{paper.abstract}")
    lines.append("")

    buckets: Dict[str, List[Tuple[JournalRow, Dict[str, float]]]] = {}
    for j, s in ranked[:topk]:
        b = group_bucket(j.ajg_2024)
        buckets.setdefault(b, []).append((j, s))

    for bucket in ["A 主投更易", "B 备投折中", "C 冲刺更高（4）", "C 冲刺更高（4*）"]:
        if bucket not in buckets:
            continue
        lines.append(f"## {bucket}")
        lines.append("")
        lines.append(
            "| Field | Journal | AJG 2024 | AJG 2021 | Citescore | SNIP | SJR | JIF | SDG | Intl | Collab | Policy | 理由(简) |"
        )
        lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
        for j, s in buckets[bucket]:
            reason = []
            if s["kw"] >= 2.0:
                reason.append("主题匹配")
            if s["easy"] >= 3.0:
                reason.append("相对易")
            try:
                if j.policy_value and float(j.policy_value or 0) > 1:
                    reason.append("政策相关度高")
            except Exception:
                pass
            if not reason:
                reason.append("备选")

            lines.append(
                "| "
                + " | ".join(
                    [
                        md_escape(j.field),
                        md_escape(j.title),
                        md_escape(j.ajg_2024),
                        md_escape(j.ajg_2021),
                        md_escape(j.citescore_rank),
                        md_escape(j.snip_rank),
                        md_escape(j.sjr_rank),
                        md_escape(j.jif_rank),
                        md_escape(j.sdg_pct),
                        md_escape(j.intl_pct),
                        md_escape(j.collab_pct),
                        md_escape(j.policy_value),
                        md_escape("/".join(reason)),
                    ]
                )
                + " |"
            )
        lines.append("")

    lines.append("## 说明")
    lines.append("")
    lines.append("- 本推荐仅基于本地AJG核心目录字段与摘要关键词匹配，不包含外网审稿周期/版面费/投稿偏好等信息。")
    lines.append("- 如果你希望更精准（例如更聚焦农业经济/贸易政策/政治经济学子领域），建议补充引言或JEL分类。")

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(formatter_class=ColorHelpFormatter)
    ap.add_argument("--ajg_csv", default=DEFAULT_AJG_CSV, help="AJG核心CSV绝对路径")
    ap.add_argument("--field", default="ECON", help="论文领域（默认ECON）")
    ap.add_argument("--title", required=True, help="论文标题")
    ap.add_argument("--abstract", default="", help="论文摘要")
    ap.add_argument("--mode", default="easy", choices=["easy", "fit", "value"], help="推荐模式：easy(易发表)/fit(主题匹配)/value(性价比)")
    ap.add_argument("--topk", type=int, default=20, help="输出期刊数")
    args = ap.parse_args()

    paper = PaperProfile(field=args.field, title=args.title, abstract=args.abstract, mode=args.mode)
    rows = load_ajg_csv(args.ajg_csv)
    cand = pick_candidates(rows, paper_field=paper.field)

    scored: List[Tuple[JournalRow, Dict[str, float]]] = []
    for j in cand:
        scored.append((j, total_score(paper, j)))

    scored.sort(key=lambda x: x[1]["total"], reverse=True)
    report = render_report(paper, scored, topk=args.topk)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

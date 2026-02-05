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

Default AJG CSV (portable absolute path at runtime):
  <ABS_JOURNAL_DATA_DIR or ABS_JOURNAL_HOME>/assets/data/ajg_2024_journals_core_custom.csv
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from abs_paths import ajg_csv_default

DEFAULT_AJG_CSV = str(ajg_csv_default("2024"))

# Keep a skill root for resolving additional bundled assets (e.g., keyword lists).
from abs_paths import skill_root as resolve_skill_root

SKILL_ROOT = str(resolve_skill_root())


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


def domain_preference_bonus(paper: PaperProfile, journal: JournalRow) -> float:
    """偏好加分：贸易/农经/区经/金融/政策/政治经济 等应用方向。

    这是在“主题贴合候选集”前置筛选之后的轻量排序偏好，用于把更应用的期刊
    往前推一点，避免方法刊在 value/fit 下过于靠前。
    """

    _ = paper
    jt = normalize_text(journal.title)
    bonus = 0.0

    # Trade / policy / political economy
    if any(k in jt for k in ["trade", "tariff", "policy", "political economy", "public policy", "public"]):
        bonus += 0.4

    # Agriculture / food
    if any(k in jt for k in ["agric", "farm", "food"]):
        bonus += 0.4

    # Regional / development / urban / spatial
    if any(k in jt for k in ["regional", "development", "urban", "spatial"]):
        bonus += 0.3

    # Finance / banking / credit (keep small to avoid dominating non-finance papers)
    if any(k in jt for k in ["finance", "bank", "credit", "microfinance", "money"]):
        bonus += 0.2

    return bonus


def keyword_score(paper: PaperProfile, journal: JournalRow) -> float:
    text = normalize_text(paper.title + " " + paper.abstract)

    keywords = get_keywords(paper.field, profile=os.environ.get("ABS_PROFILE", "general"))

    score = 0.0
    for k, w in keywords.items():
        if k in text:
            score += w

    if journal.field in {"ECON", "IB&AREA", "PUB SEC"}:
        score += 0.5

    return score


def get_keywords(field: str, *, profile: str = "general") -> Dict[str, float]:
    # Default local keyword file (offline).
    # - general: more generic econ keywords
    # - ling: personalized (trade/agri/RCT/etc.) tuned for the repo owner
    base = os.path.join(SKILL_ROOT, "assets", "keywords")
    if profile == "ling":
        path = os.path.join(base, "econ_ling_trade_rct.json")
    else:
        path = os.path.join(base, "econ_general.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if not isinstance(obj, dict):
            raise ValueError("keywords json must be an object")
        out: Dict[str, float] = {}
        for k, v in obj.items():
            if not isinstance(k, str):
                continue
            try:
                out[k] = float(v)
            except Exception:
                continue
        if out:
            return out
    except Exception:
        pass

    # Fallback minimal keywords if file missing/broken.
    return {"trade": 1.0, "tariff": 1.5, "policy": 0.8, "survey": 0.8}


def fit_score(paper: PaperProfile, journal: JournalRow) -> float:
    """主题贴合分（离线、可解释）。

    当前版本直接复用 keyword_score 的逻辑作为 V1 实现，后续可在不破坏
    gating/排序框架的前提下迭代（例如外置词表、引入短语优先等）。
    """

    base = keyword_score(paper, journal)
    # Align with prior behavior: ECON/IB&AREA/PUB SEC 等领域在 keyword_score 中会有 +0.5 先验。
    # topic-fit gating 的初版实现需要把这部分包含进 fit_score，否则会出现“表格 fit 分与 gating 打分不一致”的混乱。
    field_bonus = 0.5 if journal.field in {"ECON", "IB&AREA", "PUB SEC"} else 0.0
    # Journal-side proxies SHOULD NOT dominate: only apply when the paper itself
    # clearly indicates a related topic (to avoid pushing agri/trade journals for microcredit/min-wage, etc.).
    paper_text = normalize_text(paper.title + " " + paper.abstract)
    apply_agri = any(k in paper_text for k in ["agricultur", "agriculture", "food", "farm"])
    apply_trade = any(k in paper_text for k in ["trade", "tariff"])
    apply_policy_public = any(k in paper_text for k in ["policy", "public opinion", "attitudes", "beliefs"])
    apply_dev = any(k in paper_text for k in ["development", "tfp", "productivity", "cluster", "spatial"])
    apply_labor = any(k in paper_text for k in ["wage", "minimum wage", "inequality", "gini", "labor", "employment"])
    apply_finance = any(k in paper_text for k in ["microcredit", "credit", "loan", "bank", "interest rate", "apr"])

    journal_bonus = 0.0
    jt = normalize_text(journal.title)
    if apply_agri and ("agric" in jt or "farm" in jt or "food" in jt):
        journal_bonus += 0.8
    if apply_trade and ("trade" in jt or "tariff" in jt):
        journal_bonus += 0.7
    if apply_policy_public and ("policy" in jt or "public" in jt or "opinion" in jt):
        journal_bonus += 0.5
    if apply_dev and "development" in jt:
        journal_bonus += 0.3
    if apply_labor and ("labor" in jt or "employment" in jt or "inequality" in jt or "wage" in jt):
        journal_bonus += 0.4
    if apply_finance and ("finance" in jt or "credit" in jt or "bank" in jt):
        journal_bonus += 0.4

    return base + field_bonus + journal_bonus


def method_heaviness_penalty(paper: PaperProfile, journal: JournalRow) -> float:
    """惩罚“纯方法/计量/统计”倾向（轻量启发式，避免压过主题贴合）。

    目标：在主题贴合候选池内，降低“Econometrics / Statistics / Methods”类期刊的排序优势，
    更偏向贸易/农经/区经/金融/政策/政治经济等应用方向期刊。
    """

    _ = paper
    jt = normalize_text(journal.title)
    hard = ["econometric", "econometrics", "statistic", "statistics", "method", "methods"]
    soft = ["theory", "mathematical", "probability", "stochastic"]
    if any(k in jt for k in hard):
        return 0.8
    if any(k in jt for k in soft):
        return 0.4
    return 0.0


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


def value_score(ajg_2024: str) -> float:
    level, star = parse_ajg_rating(ajg_2024)
    score = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}.get(level, 1.0)
    if level == 4 and star:
        score += 0.2
    return score


def total_score(paper: PaperProfile, journal: JournalRow) -> Dict[str, float]:
    # Note: topic-fit gating happens before calling this function.
    f = fit_score(paper, journal)
    e = easiness_score(journal.ajg_2024)
    v = value_score(journal.ajg_2024)
    p = prestige_penalty(journal)
    m = method_heaviness_penalty(paper, journal)
    d = domain_preference_bonus(paper, journal)

    if paper.mode == "fit":
        total = (10.0 * f) + (0.1 * e) - (0.2 * p) - (1.0 * m) + (2.0 * d)
    elif paper.mode == "easy":
        total = (10.0 * e) + (0.1 * f) - (0.6 * p) - (0.6 * m) + (1.0 * d)
    else:  # value
        total = (10.0 * v) + (0.2 * f) - (0.8 * p) - (0.8 * m) + (2.0 * d)

    return {"total": total, "easy": e, "value": v, "fit": f, "prestige_pen": p, "method_pen": m}


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


def narrow_candidates_by_journal_title(
    paper: PaperProfile, candidates: List[JournalRow]
) -> Tuple[List[JournalRow], str]:
    """No-op candidate narrowing.

    We keep the pipeline simple and more general by default: do not pre-filter journals
    based on journal-title heuristics.
    """

    _ = paper
    return candidates, ""


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


def render_report(
    paper: PaperProfile,
    ranked: List[Tuple[JournalRow, Dict[str, float]]],
    topk: int,
    *,
    gating_meta: Optional[GatingMeta] = None,
) -> str:
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

    if gating_meta is not None:
        lines.append("## 候选集（主题贴合）")
        lines.append("")
        lines.append(f"- 策略：{gating_meta.strategy}")
        lines.append(f"- 候选集大小：{gating_meta.total_candidates_after}（筛选前：{gating_meta.total_candidates_before}）")
        lines.append(f"- 目标候选 TopN：{gating_meta.candidate_topn}")
        lines.append(f"- 最小候选数：{gating_meta.min_candidates}")
        lines.append(f"- 是否触发回退：{'是' if gating_meta.fallback_used else '否'}")
        lines.append("")

    # Keep only topk for output, but preserve global ordering inside each AJG bucket.
    top_rows = ranked[:topk]
    buckets: Dict[str, List[Tuple[JournalRow, Dict[str, float]]]] = {}
    for j, s in top_rows:
        b = group_bucket(j.ajg_2024)
        buckets.setdefault(b, []).append((j, s))

    ordered_buckets = ["A 主投更易", "B 备投折中", "C 冲刺更高（4）", "C 冲刺更高（4*）"]
    if paper.mode == "value":
        ordered_buckets = ["C 冲刺更高（4*）", "C 冲刺更高（4）", "B 备投折中", "A 主投更易"]

    for bucket in ordered_buckets:
        if bucket not in buckets:
            continue
        lines.append(f"## {bucket}")
        lines.append("")
        lines.append(
            "| Field | Journal | AJG 2024 | AJG 2021 | FitScore | EasyScore | ValueScore | PrestigePen | Citescore | SNIP | SJR | JIF | SDG | Intl | Collab | Policy | 理由(简) |"
        )
        lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
        for j, s in buckets[bucket]:
            reason = []
            if s["fit"] >= 2.0:
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
                        md_escape(f"{s.get('fit', 0.0):.2f}"),
                        md_escape(f"{s.get('easy', 0.0):.2f}"),
                        md_escape(f"{s.get('value', 0.0):.2f}"),
                        md_escape(f"{s.get('prestige_pen', 0.0):.2f}"),
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
    if gating_meta is not None:
        lines.append(
            f"- 已对所有模式启用“主题贴合候选集”前置筛选（策略：{gating_meta.strategy}；候选：{gating_meta.total_candidates_after}/{gating_meta.total_candidates_before}；回退：{'是' if gating_meta.fallback_used else '否'}）。"
        )
    if not paper.abstract:
        lines.append("- 你未提供摘要：主题贴合判断可信度会降低；建议补充摘要/引言或更具体的关键词以获得更稳健的候选集。")
    lines.append("- 如果你希望更精准（例如更聚焦农业经济/贸易政策/政治经济学子领域），建议补充引言或JEL分类。")

    return "\n".join(lines)


def stable_journal_id(j: JournalRow) -> str:
    title = normalize_text(j.title).replace(" ", "-")
    rating = (j.ajg_2024 or "").strip().replace("*", "star")
    field = (j.field or "").strip().lower().replace(" ", "-")
    return f"{field}:{rating}:{title}"


def candidate_pool_to_dict(
    paper: PaperProfile,
    ajg_csv_path: str,
    candidates: List[Tuple[JournalRow, Dict[str, float]]],
    *,
    mode: str,
    gating_meta: Optional[GatingMeta],
    rating_filter: str = "",
) -> Dict[str, object]:
    pool = []
    for j, s in candidates:
        pool.append(
            {
                "id": stable_journal_id(j),
                "field": j.field,
                "journal": j.title,
                "ajg_2024": j.ajg_2024,
                "ajg_2021": j.ajg_2021,
                "signals": {
                    "fit_score": float(s.get("fit", 0.0)),
                    "easy_score": float(s.get("easy", 0.0)),
                    "value_score": float(s.get("value", 0.0)),
                    "prestige_penalty": float(s.get("prestige_pen", 0.0)),
                    "method_penalty": float(s.get("method_pen", 0.0)),
                    "total_score": float(s.get("total", 0.0)),
                },
            }
        )

    meta: Dict[str, object] = {
        "generated_at": now_local_str(),
        "paper": {
            "field": paper.field,
            "title": paper.title,
            "abstract": paper.abstract,
        },
        "mode": mode,
        "ajg_csv": os.path.abspath(ajg_csv_path),
        "rating_filter": rating_filter,
        "gating": None,
        "count": len(pool),
    }
    if gating_meta is not None:
        meta["gating"] = {
            "strategy": gating_meta.strategy,
            "candidate_topn": gating_meta.candidate_topn,
            "min_candidates": gating_meta.min_candidates,
            "total_before": gating_meta.total_candidates_before,
            "total_after": gating_meta.total_candidates_after,
            "fallback_used": gating_meta.fallback_used,
        }

    return {"meta": meta, "candidates": pool}


def write_json(path: str, obj: Dict[str, object]) -> None:
    out_dir = os.path.dirname(os.path.abspath(path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


@dataclass(frozen=True)
class GatingMeta:
    strategy: str
    candidate_topn: int
    min_candidates: int
    total_candidates_before: int
    total_candidates_after: int
    fallback_used: bool


def gate_by_topic_fit(
    paper: PaperProfile,
    candidates: List[JournalRow],
    *,
    topk: int,
    candidate_topn: Optional[int] = None,
    min_candidates: Optional[int] = None,
) -> Tuple[List[JournalRow], Dict[str, float], GatingMeta]:
    """构造主题贴合候选集（TopN + 回退）。

    V1 策略：先按 fit_score 降序取 TopN 作为候选集；若候选过少则扩大 TopN 直至满足 min_candidates。
    """

    total_before = len(candidates)
    if total_before == 0:
        meta = GatingMeta(
            strategy="topn",
            candidate_topn=0,
            min_candidates=0,
            total_candidates_before=0,
            total_candidates_after=0,
            fallback_used=False,
        )
        return [], {}, meta

    default_topn = max(topk * 8, 80)
    default_min_candidates = max(topk, 20)
    candidate_topn = int(candidate_topn or default_topn)
    min_candidates = int(min_candidates or default_min_candidates)

    scored = [(j, fit_score(paper, j)) for j in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)

    chosen_topn = min(candidate_topn, len(scored))
    fallback_used = False
    if chosen_topn < min_candidates:
        chosen_topn = min(min_candidates, len(scored))
        fallback_used = True

    gated = [j for j, _ in scored[:chosen_topn]]
    fit_map = {j.title: s for j, s in scored[:chosen_topn]}

    meta = GatingMeta(
        strategy="topn",
        candidate_topn=chosen_topn,
        min_candidates=min_candidates,
        total_candidates_before=total_before,
        total_candidates_after=len(gated),
        fallback_used=fallback_used,
    )
    return gated, fit_map, meta


def main() -> int:
    ap = argparse.ArgumentParser(formatter_class=ColorHelpFormatter)
    ap.add_argument("--ajg_csv", default=DEFAULT_AJG_CSV, help="AJG核心CSV绝对路径")
    ap.add_argument("--field", default="ECON", help="论文领域（默认ECON）")
    ap.add_argument("--title", required=True, help="论文标题")
    ap.add_argument("--abstract", default="", help="论文摘要")
    ap.add_argument("--mode", default="easy", choices=["easy", "fit", "value"], help="推荐模式：easy(易发表)/fit(主题匹配)/value(性价比)")
    ap.add_argument("--topk", type=int, default=20, help="输出期刊数")
    ap.add_argument(
        "--profile",
        default=os.environ.get("ABS_PROFILE", "general"),
        choices=["general", "ling"],
        help="主题贴合关键词配置：general(更通用)/ling(更偏个人研究方向)。也可用环境变量 ABS_PROFILE 覆盖。",
    )
    ap.add_argument(
        "--export_candidate_pool_json",
        default="",
        help="导出候选池到 JSON（供 AI 二次筛选）。为空则不导出。建议绝对路径。",
    )
    ap.add_argument(
        "--rating_filter",
        default="",
        help="AJG/ABS 星级过滤（逗号分隔，如: 1,2,3 或 3,4,4*）。为空则不过滤。",
    )
    args = ap.parse_args()

    # Make profile available to scoring functions without threading through all signatures.
    os.environ["ABS_PROFILE"] = args.profile

    paper = PaperProfile(field=args.field, title=args.title, abstract=args.abstract, mode=args.mode)
    rows = load_ajg_csv(args.ajg_csv)
    cand = pick_candidates(rows, paper_field=paper.field)

    gated, fit_map, gmeta = gate_by_topic_fit(paper, cand, topk=args.topk)

    scored: List[Tuple[JournalRow, Dict[str, float]]] = []
    for j in gated:
        # Important: scoring MUST be mode-aware for ranking inside the gated candidate set.
        # Since total_score uses paper.mode, we need to compute inside loop after gating.
        s = total_score(paper, j)
        # Ensure gated fit is consistent with ordering, and present even if total_score changes.
        s["fit"] = float(fit_map.get(j.title, s.get("fit", 0.0)))
        scored.append((j, s))

    scored.sort(key=lambda x: x[1]["total"], reverse=True)

    if args.rating_filter:
        allowed = {x.strip() for x in args.rating_filter.split(",") if x.strip()}
        scored = [x for x in scored if (x[0].ajg_2024 or "").strip() in allowed]

    report = render_report(paper, scored, topk=args.topk, gating_meta=gmeta)
    print(report)

    if args.export_candidate_pool_json:
        pool_obj = candidate_pool_to_dict(
            paper,
            args.ajg_csv,
            scored,
            mode=args.mode,
            gating_meta=gmeta,
            rating_filter=args.rating_filter,
        )
        write_json(args.export_candidate_pool_json, pool_obj)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

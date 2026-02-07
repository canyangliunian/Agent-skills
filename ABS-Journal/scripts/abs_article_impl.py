#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ABS-Journal: Recommend target journals using AJG core catalog.

This is the implementation script (moved from the legacy ABS-article skill).
It does NOT use external web resources; it relies only on the local AJG CSV.

Inputs:
- title (required)
- abstract (optional)
- mode (default: easy; options: easy/medium/hard)

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

# Default candidate field whitelist (AJG CSV: Field column).
# Note: this controls which journals enter the candidate pool. It is NOT the paper's field label.
DEFAULT_FIELD_SCOPE = [
    "ECON",
    "FINANCE",
    "PUB SEC",
    "REGIONAL STUDIES, PLANNING AND ENVIRONMENT",
    "SOC SCI",
]

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
    return 0, False


def easiness_score(ajg_2024: str) -> float:
    level, star = parse_ajg_rating(ajg_2024)
    base = {1: 4.0, 2: 3.0, 3: 2.0, 4: 1.0}.get(level, 1.0)
    if level == 4 and star:
        base -= 0.4
    return base


def domain_preference_bonus(paper: PaperProfile, journal: JournalRow) -> float:
    """偏好加分：贸易/农经/区经/金融/政策/政治经济 等应用方向。

    这是在“主题贴合候选集”前置筛选之后的轻量排序偏好，用于把更应用的期刊
    往前推一点，避免方法刊在高难度/中难度下过于靠前。
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
    """Compute per-journal scores inside the topic-fit gated candidate pool.

    New semantics:
    - easy: 投稿难度最低（更稳妥/门槛更低）
    - medium: 中等难度（折中）
    - hard: 投稿难度最高（更偏高门槛/更“冲刺”）
    """

    # Note: topic-fit gating happens before calling this function.
    f = fit_score(paper, journal)
    e = easiness_score(journal.ajg_2024)
    v = value_score(journal.ajg_2024)
    p = prestige_penalty(journal)
    m = method_heaviness_penalty(paper, journal)
    d = domain_preference_bonus(paper, journal)

    if paper.mode == "easy":
        total = (10.0 * e) + (0.1 * f) - (0.6 * p) - (0.6 * m) + (1.0 * d)
    elif paper.mode == "medium":
        total = (6.0 * f) + (6.0 * e) + (2.0 * v) - (0.6 * p) - (0.8 * m) + (2.0 * d)
    else:  # hard
        total = (10.0 * v) + (0.2 * f) - (0.8 * p) - (0.8 * m) + (2.0 * d)

    return {"total": total, "easy": e, "value": v, "fit": f, "prestige_pen": p, "method_pen": m}


def load_ajg_csv(path: str) -> List[JournalRow]:
    # Accept both absolute and relative paths.
    # Relative paths are resolved against this repo/skill root for portability.
    if not os.path.isabs(path):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", path))
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


def parse_field_scope(raw: str) -> List[str]:
    # NOTE:
    # AJG CSV 的 Field 列里存在带逗号的单个 Field 值，例如：
    # "REGIONAL STUDIES, PLANNING AND ENVIRONMENT"
    # 但 CLI 约定又使用逗号分隔多个 Field。为兼容默认值与用户输入，
    # 这里对该特殊 Field 做一次合并修复：
    #   "REGIONAL STUDIES, PLANNING AND ENVIRONMENT" -> 单个 token
    parts = [x.strip() for x in (raw or "").split(",") if x.strip()]
    if not parts:
        return []

    merged: List[str] = []
    i = 0
    while i < len(parts):
        cur = parts[i]
        if (
            cur.upper() == "REGIONAL STUDIES"
            and i + 1 < len(parts)
            and parts[i + 1].upper() == "PLANNING AND ENVIRONMENT"
        ):
            merged.append("REGIONAL STUDIES, PLANNING AND ENVIRONMENT")
            i += 2
            continue
        merged.append(cur)
        i += 1
    return merged


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
    if level == 0:
        return "未评级"
    if level == 1:
        return "A 主投更易（1）"
    if level == 2:
        return "A 主投更易（2）"
    if level == 3:
        return "B 备投折中（3）"
    if level == 4 and star:
        return "C 冲刺更高（4*）"
    return "C 冲刺更高（4）"


def md_escape(s: str) -> str:
    return (s or "").replace("|", "\\|")


def apply_rating_mix(
    paper: PaperProfile,
    ranked: List[Tuple[JournalRow, Dict[str, float]]],
    *,
    topk: int,
) -> List[Tuple[JournalRow, Dict[str, float]]]:
    """Re-balance the topk rows to improve rating hierarchy inside each mode.

    This is applied AFTER normal scoring + rating_filter. It only affects which rows
    appear in the final TopK (ordering among selected rows is preserved).

    Default quotas (best-effort; only affects the TopK slice, and only if enough candidates exist):
    - easy bucket (ratings 1/2): try to include at least 2 journals rated "2" in TopK.
    - medium bucket (ratings 2/3): try to include at least 2 journals rated "3" in TopK.
    - hard bucket: no mixing here (ratings 4/4*).
    """

    if topk <= 0:
        return []

    mode = (paper.mode or "").strip()
    if mode not in {"easy", "medium"}:
        return ranked

    if topk < 6:
        # Too small to enforce meaningful mix; keep simple.
        return ranked

    want_rating = "2" if mode == "easy" else "3"
    min_want = 2

    take = ranked[:topk]
    have = sum(1 for j, _ in take if (j.ajg_2024 or "").strip() == want_rating)
    if have >= min_want:
        return ranked

    # Find candidates within ranked[topk:] that match want_rating.
    needed = min_want - have
    replacements = []
    for idx in range(topk, len(ranked)):
        j, s = ranked[idx]
        if (j.ajg_2024 or "").strip() == want_rating:
            replacements.append((idx, (j, s)))
            if len(replacements) >= needed:
                break
    if not replacements:
        return ranked

    # Replace from the end of TopK those that are NOT want_rating.
    out = list(ranked)
    replace_positions = [i for i in range(topk - 1, -1, -1) if (out[i][0].ajg_2024 or "").strip() != want_rating]
    if not replace_positions:
        return ranked

    for pos, (src_idx, item) in zip(replace_positions, replacements):
        # swap item at pos with src_idx
        out[pos], out[src_idx] = out[src_idx], out[pos]

    return out


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
    lines.append(f"- 难度：{paper.mode}")
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
        if isinstance(getattr(gating_meta, "field_scope_effective", None), list):
            lines.append(f"- 候选 Field：{', '.join(getattr(gating_meta, 'field_scope_effective'))}")
        lines.append(f"- 策略：{gating_meta.strategy}")
        lines.append(f"- 候选集大小：{gating_meta.total_candidates_after}（筛选前：{gating_meta.total_candidates_before}）")
        lines.append(f"- 目标候选 TopN：{gating_meta.candidate_topn}")
        lines.append(f"- 最小候选数：{gating_meta.min_candidates}")
        lines.append(f"- 是否触发回退：{'是' if gating_meta.fallback_used else '否'}")
        lines.append("")

    # Keep only topk for output, but preserve global ordering inside each AJG bucket.
    # Also apply a small rating-mix rule so easy/medium feel more layered.
    ranked2 = apply_rating_mix(paper, ranked, topk=topk)
    top_rows = ranked2[:topk]
    buckets: Dict[str, List[Tuple[JournalRow, Dict[str, float]]]] = {}
    for j, s in top_rows:
        b = group_bucket(j.ajg_2024)
        buckets.setdefault(b, []).append((j, s))

    ordered_buckets = ["A 主投更易（1）", "A 主投更易（2）", "B 备投折中（3）", "C 冲刺更高（4）", "C 冲刺更高（4*）", "未评级"]
    if paper.mode == "hard":
        ordered_buckets = ["C 冲刺更高（4*）", "C 冲刺更高（4）", "B 备投折中（3）", "A 主投更易（2）", "A 主投更易（1）", "未评级"]

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
    if paper.mode in {"easy", "medium"}:
        lines.append("- 为增强层次感：在同一难度的星级桶内，系统会“尽量”混入更高一档星级（easy 尝试包含少量 2；medium 尝试包含少量 3）。若主题贴合候选不足，则可能无法满足。")
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


def _normalize_allowed_ratings(raw: str, *, mode: str) -> List[str]:
    """Normalize rating filter to an ordered list for rebalancing.

    Ordering is important for deterministic quota remainder allocation and for the
    "adjacent within-bucket" fill policy:
    - easy: ["1", "2"]
    - medium: ["2", "3"]
    - hard: ["4", "4*"]
    """

    tokens = [x.strip() for x in (raw or "").split(",") if x.strip()]
    default_order = {
        "easy": ["1", "2"],
        "medium": ["2", "3"],
        "hard": ["4", "4*"],
    }.get((mode or "").strip(), [])

    if tokens:
        token_set = set(tokens)
        known = [t for t in default_order if t in token_set]
        extra = sorted([t for t in tokens if t not in set(default_order)])
        out = known + extra
        return out

    return list(default_order)


def compute_exact_rating_quota(
    target_total: int,
    allowed_ratings: List[str],
) -> Tuple[Dict[str, int], str]:
    """计算精确的星级配额，实现1:1分配。

    Args:
        target_total: 目标总数（如10本）
        allowed_ratings: 允许的星级列表（如["1","2"]）

    Returns:
        (配额字典, 描述字符串)
    """
    num_ratings = len(allowed_ratings)
    if num_ratings == 0:
        return {}, "无有效星级"

    base_quota = target_total // num_ratings
    remainder = target_total % num_ratings

    quota = {}
    for idx, rating in enumerate(allowed_ratings):
        quota[rating] = base_quota
        if idx < remainder:
            quota[rating] += 1

    desc = f"精确1:1配额（基础{base_quota}本，余数{remainder}分配给前{remainder}个星级）"
    return quota, desc


def _estimate_balanced_pool_size(
    available_by_rating: Dict[str, int],
    *,
    allowed_ratings: List[str],
    min_pool_size: int,
    max_pool_size: int,
    exact_balance: bool = False,
    target_topk: int = 10,
) -> int:
    """Pick an export pool size that prefers 1:1, but never below min_pool_size.

    Strategy:
    - If all ratings have plenty, use max_pool_size.
    - If one rating is scarce, use k * min(available) (perfect 1:1), but not below min_pool_size.
    - If even min_pool_size cannot be achieved without breaking 1:1, we still return min_pool_size
      and allow fill from adjacent ratings during selection.
    - When exact_balance=True: use a more conservative pool size to ensure precise 1:1 quotas.
    """

    allowed_ratings = [r for r in (allowed_ratings or []) if r]
    if not allowed_ratings:
        return int(min_pool_size)

    num_ratings = len(allowed_ratings)

    if exact_balance:
        # Exact balance mode: ensure each rating has enough journals
        # Strategy: each rating needs at least (target_topk // num_ratings) + 2 for fallback
        per_rating_needed = max(target_topk // num_ratings + 2, min_pool_size // num_ratings)
        balanced_cap = int(num_ratings * per_rating_needed)
        target = min(balanced_cap, int(max_pool_size))
        return max(int(min_pool_size), int(target))

    # Original logic: best-effort 1:1
    mins = [int(available_by_rating.get(r, 0)) for r in allowed_ratings]
    min_avail = min(mins) if mins else 0
    balanced_cap = int(num_ratings * min_avail) if min_avail > 0 else 0
    target = balanced_cap if balanced_cap > 0 else int(max_pool_size)
    return max(int(min_pool_size), min(int(max_pool_size), int(target)))


def rebalance_by_rating_quota(
    ranked: List[Tuple[JournalRow, Dict[str, float]]],
    *,
    allowed_ratings: List[str],
    target_n: int,
    mode: str,
    exact_balance: bool = False,
) -> Tuple[List[Tuple[JournalRow, Dict[str, float]]], Dict[str, object]]:
    """Rebalance exported candidate pools to be as 1:1 as possible across allowed ratings.

    Policy:
    - Best-effort 1:1 across `allowed_ratings` inside the same mode bucket.
    - If a rating lacks enough candidates, fill from the adjacent rating within the same bucket
      (easy: 1<->2; medium: 2<->3; hard: 4<->4*).
    - Keep stable ordering by consuming from the ranked lists; never invent new journals.
    - When exact_balance=True: use exact quota distribution for precise 1:1 balance.
    """

    mode = (mode or "").strip()
    allowed_ratings = [r for r in (allowed_ratings or []) if r]
    if target_n <= 0 or not ranked or not allowed_ratings:
        meta: Dict[str, object] = {
            "enabled": True,
            "allowed_ratings": list(allowed_ratings),
            "target_pool_size": int(max(target_n, 0)),
            "available_by_rating": {},
            "selected_by_rating": {},
            "filled": False,
            "insufficient_total_candidates": True,
        }
        return ranked[: max(target_n, 0)], meta

    by_rating: Dict[str, List[Tuple[JournalRow, Dict[str, float]]]] = {r: [] for r in allowed_ratings}
    for it in ranked:
        j, _ = it
        r = (j.ajg_2024 or "").strip()
        if r in by_rating:
            by_rating[r].append(it)

    available_by_rating = {r: len(by_rating.get(r) or []) for r in allowed_ratings}
    available_total = sum(int(available_by_rating.get(r, 0)) for r in allowed_ratings)

    k = len(allowed_ratings)
    min_avail = min(int(available_by_rating.get(r, 0)) for r in allowed_ratings) if allowed_ratings else 0
    ideal_balanced_size = int(k * min_avail) if min_avail > 0 else 0

    # Prefer the balanced size (1:1) when possible; caller provides `target_n` as a
    # "try to export this many" size. If perfect 1:1 is impossible due to scarcity
    # in one rating, we should still export up to `target_n` by filling from the
    # adjacent rating within the same bucket (policy below).
    target_n_eff = min(int(target_n), int(available_total))

    # Quotas: best-effort 1:1 across allowed ratings, but never exceed availability.
    # Start from an equal share and then distribute remainder to ratings that still have spare capacity.
    if exact_balance:
        # Use exact quota allocation for precise 1:1 balance
        quota, quota_desc = compute_exact_rating_quota(
            target_n_eff, allowed_ratings
        )
    else:
        # Original logic: best-effort 1:1
        base = target_n_eff // k
        rem = target_n_eff % k
        quota: Dict[str, int] = {r: min(base, int(available_by_rating.get(r, 0))) for r in allowed_ratings}

        # Distribute remainder deterministically by allowed_ratings order, but only to ratings with capacity.
        remain = target_n_eff - sum(quota.values())
        idx = 0
        while remain > 0 and k > 0:
            r = allowed_ratings[idx % k]
            cap = int(available_by_rating.get(r, 0))
            if quota.get(r, 0) < cap:
                quota[r] = int(quota.get(r, 0)) + 1
                remain -= 1
            idx += 1
            # Safety: if we loop too much with no progress, break.
            if idx > (k * (target_n_eff + 2)):
                break
        quota_desc = f"最佳1:1（目标{target_n_eff}本，实际{sum(quota.values())}本）"

    selected: List[Tuple[JournalRow, Dict[str, float]]] = []
    used_ids: set = set()
    selected_by_rating: Dict[str, int] = {r: 0 for r in allowed_ratings}

    def take_from(rating: str, n: int) -> int:
        taken = 0
        lst = by_rating.get(rating) or []
        while taken < n and lst:
            item = lst.pop(0)
            jid = stable_journal_id(item[0])
            if jid in used_ids:
                continue
            used_ids.add(jid)
            selected.append(item)
            taken += 1
        return taken

    for r in allowed_ratings:
        got = take_from(r, quota.get(r, 0))
        selected_by_rating[r] += got

    # Adjacent-within-bucket fill policy.
    fill_order: List[str]
    if mode == "easy":
        fill_order = ["1", "2"]
    elif mode == "medium":
        fill_order = ["2", "3"]
    else:
        fill_order = ["4", "4*"]
    fill_order = [r for r in fill_order if r in set(allowed_ratings)] or list(allowed_ratings)

    def adjacent_sources(rating: str) -> List[str]:
        if len(fill_order) != 2:
            return [x for x in fill_order if x != rating]
        a, b = fill_order
        return [b] if rating == a else [a]

    filled = False
    while len(selected) < target_n_eff:
        progress = False
        for r in allowed_ratings:
            if len(selected) >= target_n_eff:
                break
            if selected_by_rating.get(r, 0) >= quota.get(r, 0):
                continue
            need = quota[r] - selected_by_rating.get(r, 0)
            got = take_from(r, need)
            if got:
                progress = True
                selected_by_rating[r] += got
                continue
            for src in adjacent_sources(r):
                got2 = take_from(src, need)
                if got2:
                    filled = True
                    progress = True
                    selected_by_rating[src] = selected_by_rating.get(src, 0) + got2
                    break
        if not progress:
            break

    # If still short but candidates remain in any allowed bucket, keep filling round-robin.
    if len(selected) < target_n_eff:
        for r in allowed_ratings:
            while len(selected) < target_n_eff:
                got = take_from(r, 1)
                if got:
                    filled = True
                else:
                    break
            if len(selected) >= target_n_eff:
                break

    insufficient_total = len(selected) < target_n_eff
    meta2: Dict[str, object] = {
        "enabled": True,
        "allowed_ratings": list(allowed_ratings),
        "target_pool_size": int(target_n_eff),
        "ideal_balanced_pool_size": int(ideal_balanced_size),
        "available_by_rating": dict(available_by_rating),
        "selected_by_rating": dict({k: int(v) for k, v in selected_by_rating.items()}),
        "filled": bool(filled),
        "insufficient_total_candidates": bool(insufficient_total),
        "quota_description": quota_desc,
        "exact_balance": exact_balance,
    }
    return selected, meta2


def candidate_pool_to_dict(
    paper: PaperProfile,
    ajg_csv_path: str,
    candidates: List[Tuple[JournalRow, Dict[str, float]]],
    *,
    mode: str,
    gating_meta: Optional[GatingMeta],
    rating_filter: str = "",
    rating_filter_effective: str = "",
    field_scope_requested: str = "",
    field_scope_effective: Optional[List[str]] = None,
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
        "rating_filter_effective": rating_filter_effective or rating_filter,
        "field_scope_requested": field_scope_requested,
        "field_scope_effective": field_scope_effective or [],
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
    field_scope_effective: List[str]


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
            field_scope_effective=[],
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
        field_scope_effective=[],
    )
    return gated, fit_map, meta


def main() -> int:
    ap = argparse.ArgumentParser(formatter_class=ColorHelpFormatter)
    ap.add_argument("--ajg_csv", default=DEFAULT_AJG_CSV, help="AJG核心CSV路径（绝对/相对均可；相对路径基于项目根）")
    ap.add_argument("--field", default="ECON", help="论文领域标签/关键词配置（默认ECON；不控制候选范围）")
    ap.add_argument(
        "--field_scope",
        default="",
        help=(
            "候选期刊 Field 白名单（AJG CSV 的 Field 列，逗号分隔；精确匹配）。"
            "为空则使用默认白名单：ECON,FINANCE,PUB SEC,REGIONAL STUDIES, PLANNING AND ENVIRONMENT,SOC SCI。"
        ),
    )
    ap.add_argument("--title", required=True, help="论文标题")
    ap.add_argument("--abstract", default="", help="论文摘要")
    ap.add_argument("--mode", default="easy", choices=["easy", "medium", "hard"], help="投稿难度：easy(最容易)/medium(中等)/hard(最困难)")
    ap.add_argument("--topk", type=int, default=10, help="输出期刊数（默认10）")
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
    ap.add_argument(
        "--exact_rating_balance",
        action="store_true",
        help="启用精确星级平衡（每个模式内部按固定配额分配：easy:5x2星+5x1星；medium:5x3星+5x2星；hard:5x4*+5x4星）"
    )
    args = ap.parse_args()

    # Make profile available to scoring functions without threading through all signatures.
    os.environ["ABS_PROFILE"] = args.profile

    paper = PaperProfile(field=args.field, title=args.title, abstract=args.abstract, mode=args.mode)
    rows = load_ajg_csv(args.ajg_csv)
    requested_scope_raw = (args.field_scope or "").strip()
    field_scope_effective = parse_field_scope(requested_scope_raw) if requested_scope_raw else list(DEFAULT_FIELD_SCOPE)
    if not field_scope_effective:
        raise RuntimeError("--field_scope 解析后为空；请提供至少一个 Field")

    known_fields = {r.field for r in rows if (r.field or "").strip()}
    unknown = [x for x in field_scope_effective if x not in known_fields]
    if unknown:
        known_sorted = sorted(known_fields)
        raise RuntimeError(
            "以下 Field 不存在于 AJG CSV 的 Field 列："
            + ", ".join(repr(x) for x in unknown)
            + "\n可选 Field（来自 CSV）:\n- "
            + "\n- ".join(known_sorted)
        )

    cand = [r for r in rows if r.field in set(field_scope_effective)]

    def build_ranked(*, candidate_topn: Optional[int]) -> Tuple[List[Tuple[JournalRow, Dict[str, float]]], GatingMeta]:
        gated, fit_map, gmeta = gate_by_topic_fit(paper, cand, topk=args.topk, candidate_topn=candidate_topn)
        gmeta = GatingMeta(
            strategy=gmeta.strategy,
            candidate_topn=gmeta.candidate_topn,
            min_candidates=gmeta.min_candidates,
            total_candidates_before=gmeta.total_candidates_before,
            total_candidates_after=gmeta.total_candidates_after,
            fallback_used=gmeta.fallback_used,
            field_scope_effective=list(field_scope_effective),
        )
        scored_local: List[Tuple[JournalRow, Dict[str, float]]] = []
        for j in gated:
            s = total_score(paper, j)
            s["fit"] = float(fit_map.get(j.title, s.get("fit", 0.0)))
            scored_local.append((j, s))
        scored_local.sort(key=lambda x: x[1]["total"], reverse=True)
        return scored_local, gmeta

    # Phase 1: normal gating.
    scored, gmeta = build_ranked(candidate_topn=None)

    # Apply rating filter (if any) and check TopK sufficiency.
    rating_filter = (args.rating_filter or "").strip()
    allowed = {x.strip() for x in rating_filter.split(",") if x.strip()} if rating_filter else set()
    filtered = scored
    if allowed:
        filtered = [x for x in scored if (x[0].ajg_2024 or "").strip() in allowed]

    # Phase 2 fallback: if filtered is too small, expand the gating candidate_topn.
    # This keeps the same rating_filter, but looks at a wider topic-fit candidate pool.
    if allowed and len(filtered) < int(args.topk):
        expanded_topn = max(gmeta.candidate_topn * 2, gmeta.candidate_topn + 80, int(args.topk) * 20)
        scored2, gmeta2 = build_ranked(candidate_topn=expanded_topn)
        filtered2 = [x for x in scored2 if (x[0].ajg_2024 or "").strip() in allowed]
        if len(filtered2) >= len(filtered):
            scored = scored2
            gmeta = gmeta2
            filtered = filtered2

    # Phase 3 fallback (soft): if still too small, do NOT expand the rating filter silently.
    # Expanding ratings here breaks the user's mental model for mode buckets and also makes
    # exported candidate pools confusing (e.g., easy unexpectedly contains 3-star journals).
    # We instead keep the requested rating filter and let downstream selection/reporting
    # reflect the true availability.

    scored = filtered

    # For exact balance mode, we need to generate a balanced pool first,
    # then select TopK from the balanced pool for the report.
    if getattr(args, "exact_rating_balance", False) or args.export_candidate_pool_json:
        effective = ",".join(sorted(allowed)) if allowed else ""
        allowed_ordered = _normalize_allowed_ratings(effective or rating_filter, mode=args.mode)
        # For exported candidate pools, prefer 1:1 as much as possible (ideal size = k * min(available)),
        # but ensure pool is large enough for downstream TopK selection.
        # We use a two-pass: first compute availability by rating, then choose a target size.
        avail_tmp: Dict[str, int] = {}
        for j, _s in scored:
            r = (j.ajg_2024 or "").strip()
            if r in set(allowed_ordered):
                avail_tmp[r] = int(avail_tmp.get(r, 0)) + 1
        pool_min = int(args.topk) * 10
        pool_max = min(len(scored), max(int(args.topk) * 30, 150))
        pool_size = _estimate_balanced_pool_size(
            avail_tmp,
            allowed_ratings=allowed_ordered,
            min_pool_size=min(pool_min, pool_max),
            max_pool_size=pool_max,
            exact_balance=getattr(args, "exact_rating_balance", False),
            target_topk=args.topk,
        )
        scored_for_pool, rebalance_meta = rebalance_by_rating_quota(
            scored,
            allowed_ratings=allowed_ordered,
            target_n=pool_size,
            mode=args.mode,
            exact_balance=getattr(args, "exact_rating_balance", False),
        )


        # For exact balance mode, use the balanced pool for the report
        report_scored = scored_for_pool if getattr(args, "exact_rating_balance", False) else scored
    else:
        report_scored = scored
        scored_for_pool = []
        rebalance_meta = {}

    # For exact balance mode, apply exact 1:1 balance to TopK as well
    if getattr(args, "exact_rating_balance", False):
        # Get allowed ratings for current mode
        effective = ",".join(sorted(allowed)) if allowed else ""
        allowed_ordered = _normalize_allowed_ratings(effective or rating_filter, mode=args.mode)
        # Apply exact balance to report_scored for TopK output
        report_scored, topk_rebalance_meta = rebalance_by_rating_quota(
            report_scored,
            allowed_ratings=allowed_ordered,
            target_n=args.topk,
            mode=args.mode,
            exact_balance=True,
        )

    report = render_report(paper, report_scored, topk=args.topk, gating_meta=gmeta)
    print(report)

    if args.export_candidate_pool_json:
        pool_obj = candidate_pool_to_dict(
            paper,
            args.ajg_csv,
            scored_for_pool,
            mode=args.mode,
            gating_meta=gmeta,
            rating_filter=args.rating_filter,
            rating_filter_effective=effective if 'effective' in locals() else '',
            field_scope_requested=requested_scope_raw,
            field_scope_effective=field_scope_effective,
        )
        meta = pool_obj.get('meta')
        if isinstance(meta, dict):
            meta['rating_rebalance'] = rebalance_meta
        write_json(args.export_candidate_pool_json, pool_obj)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

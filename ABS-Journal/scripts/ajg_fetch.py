#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Fetch Chartered ABS Academic Journal Guide (AJG) data.

Design goals:
- No third-party dependencies (stdlib only).
- Do not store plaintext credentials in files.
- Be robust to URL changes by discovering latest AJG year from the entry page.

Usage:
  export AJG_EMAIL='...'
  export AJG_PASSWORD='...'
  python3 /Users/lingguiwang/.agents/skills/abs-journal/scripts/ajg_fetch.py \
    --outdir /Users/lingguiwang/.agents/skills/abs-journal/assets/data

Outputs:
- ajg_<year>_journals_raw.jsonl
- ajg_<year>_meta.json
- ajg_<year>_journals_core_custom.csv
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import html
from html.parser import HTMLParser
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import http.cookiejar
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple


BASE = "https://charteredabs.org"
ENTRY_URL = "https://charteredabs.org/academic-journal-guide"
LOGIN_URL = "https://charteredabs.org/login?gated=true"
AUTH_POST_URL = "https://charteredabs.org/!/auth/login"

DEFAULT_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"

ANSI_RESET = "\x1b[0m"
ANSI_BOLD = "\x1b[1m"
ANSI_CYAN_BOLD = "\x1b[36;1m"
ANSI_YELLOW_BOLD = "\x1b[33;1m"


def supports_color() -> bool:
    """
    Color policy:
    - Default auto: enable only when stdout is a TTY and TERM is not 'dumb'
    - If NO_COLOR exists: force disable
    - If FORCE_COLOR=1: force enable (even if non-TTY)
    """
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("FORCE_COLOR") == "1":
        return True
    term = os.environ.get("TERM", "")
    if term.lower() == "dumb":
        return False
    return sys.stdout.isatty()


def colorize(text: str, ansi_code: str) -> str:
    if not supports_color():
        return text
    return f"{ansi_code}{text}{ANSI_RESET}"


class ColorHelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action: argparse.Action) -> str:
        text = super()._format_action_invocation(action)
        if not supports_color():
            return text

        # Keep punctuation/commas from argparse (e.g., "-h, --help") while coloring tokens.
        # We color:
        # - option tokens starting with "-" as cyan+bold
        # - metavar/placeholder tokens (ALL CAPS or containing "_") as yellow+bold
        tokens = re.split(r"(\s+)", text)
        out: List[str] = []
        for tok in tokens:
            if not tok or tok.isspace():
                out.append(tok)
                continue

            core = tok.rstrip(",")
            suffix = tok[len(core) :]
            if core.startswith("-"):
                out.append(colorize(core, ANSI_CYAN_BOLD) + suffix)
            elif core.isupper() or "_" in core:
                out.append(colorize(core, ANSI_YELLOW_BOLD) + suffix)
            else:
                out.append(tok)
        return "".join(out)


class TokenParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.token: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "input":
            return
        attrs_dict = {k: (v if v is not None else "") for k, v in attrs}
        if attrs_dict.get("name") == "_token" and attrs_dict.get("value"):
            self.token = attrs_dict["value"]


def utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).replace(microsecond=0).isoformat()


def http_open(
    opener: urllib.request.OpenerDirector,
    req: urllib.request.Request,
    timeout: int = 30,
    retries: int = 5,
    backoff: float = 1.0,
    debug_http: bool = False,
) -> Tuple[int, str, bytes]:
    last_err: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            with opener.open(req, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                final_url = resp.geturl()
                body = resp.read()
                if debug_http:
                    sys.stderr.write(f"[HTTP] {req.method} {req.full_url} -> {status} {final_url} bytes={len(body)}\n")
                return status, final_url, body
        except Exception as e:
            last_err = e
            if attempt >= retries:
                break
            sleep_s = backoff * (2 ** (attempt - 1))
            time.sleep(sleep_s)
    raise RuntimeError(f"HTTP request failed after {retries} attempts: {req.method} {req.full_url}: {last_err}")


def build_opener() -> urllib.request.OpenerDirector:
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPRedirectHandler(),
    )
    opener.addheaders = [
        ("User-Agent", DEFAULT_UA),
        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
        ("Accept-Language", "en-US,en;q=0.9"),
        ("Connection", "keep-alive"),
    ]
    return opener


def decode_body(body: bytes, fallback: str = "utf-8") -> str:
    try:
        return body.decode("utf-8")
    except UnicodeDecodeError:
        return body.decode(fallback, errors="replace")


def discover_latest_year_and_url(opener: urllib.request.OpenerDirector, debug_http: bool = False) -> Tuple[int, str]:
    req = urllib.request.Request(ENTRY_URL, method="GET")
    status, final_url, body = http_open(opener, req, debug_http=debug_http)
    if status >= 400:
        raise RuntimeError(f"Failed to fetch entry page: {status} {final_url}")
    html_text = decode_body(body)

    # Find links like /academic-journal-guide/academic-journal-guide-2024
    years: List[int] = []
    candidates: Dict[int, str] = {}
    for m in re.finditer(r"/academic-journal-guide/academic-journal-guide-(\d{4})", html_text):
        y = int(m.group(1))
        years.append(y)
        candidates[y] = urllib.parse.urljoin(BASE, m.group(0))

    if not years:
        # Fallback: maybe single link without year; keep entry URL
        raise RuntimeError("Could not discover AJG year link from entry page")

    latest_year = max(years)
    return latest_year, candidates[latest_year]


def fetch_csrf_token(opener: urllib.request.OpenerDirector, debug_http: bool = False) -> str:
    req = urllib.request.Request(LOGIN_URL, method="GET")
    status, final_url, body = http_open(opener, req, debug_http=debug_http)
    if status >= 400:
        raise RuntimeError(f"Failed to fetch login page: {status} {final_url}")
    html_text = decode_body(body)
    parser = TokenParser()
    parser.feed(html_text)
    if not parser.token:
        raise RuntimeError("Could not find CSRF _token in login page")
    return parser.token


def do_login(
    opener: urllib.request.OpenerDirector,
    email: str,
    password: str,
    debug_http: bool = False,
) -> None:
    token = fetch_csrf_token(opener, debug_http=debug_http)

    form = {
        "_token": token,
        "email": email,
        "password": password,
    }
    data = urllib.parse.urlencode(form).encode("utf-8")

    req = urllib.request.Request(
        AUTH_POST_URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": LOGIN_URL,
            "Origin": BASE,
        },
    )
    status, final_url, body = http_open(opener, req, debug_http=debug_http)

    # Some sites redirect on success; body might still be HTML.
    # We verify gating by fetching the AJG page afterwards.
    if status >= 400:
        raise RuntimeError(f"Login POST failed: {status} {final_url}")

    html_text = decode_body(body)
    # The site loads reCAPTCHA script on many pages; do not treat that alone as a hard failure.
    # If the login actually failed due to CAPTCHA, the AJG page fetch below will still be gated.


def is_gated_page(html_text: str) -> bool:
    t = html_text.lower()
    if "log in or register to view" in t:
        return True
    if "/login?gated=true" in t or "user log in" in t and "!/auth/login" in t:
        return True
    return False


def extract_first_module_script_src(html_text: str) -> Optional[str]:
    # Find <script type="...-module" src="https://charteredabs.org/build/assets/site-xxxx.js"></script>
    m = re.search(r"<script[^>]+type=\"[^\"]+-module\"[^>]+src=\"([^\"]+)\"", html_text)
    if m:
        return html.unescape(m.group(1))
    return None


def parse_algolia_vars_from_html(html_text: str) -> Optional[Tuple[str, str, bool]]:
    # Example:
    # window.ALGOLIA_APP_ID = 'PQZAS87G1F';
    # window.ALGOLIA_PUBLIC = '...';
    # window.ALGOLIA_USE_DEV_INDEXES = false;
    app_m = re.search(r"window\.ALGOLIA_APP_ID\s*=\s*'([^']+)'", html_text)
    key_m = re.search(r"window\.ALGOLIA_PUBLIC\s*=\s*'([^']+)'", html_text)
    dev_m = re.search(r"window\.ALGOLIA_USE_DEV_INDEXES\s*=\s*(true|false)", html_text)
    if not (app_m and key_m and dev_m):
        return None
    app_id = app_m.group(1).strip()
    api_key = key_m.group(1).strip()
    use_dev = dev_m.group(1).strip().lower() == "true"
    return app_id, api_key, use_dev


def parse_algolia_vars_from_html_or_entry(
    opener: urllib.request.OpenerDirector,
    entry_url: str,
    debug_http: bool = False,
) -> Optional[Tuple[str, str, bool]]:
    # Try parse from AJG HTML first; if missing, try the main entry page (some globals are set there).
    req = urllib.request.Request(entry_url, method="GET")
    st, fu, bd = http_open(opener, req, debug_http=debug_http)
    if st >= 400:
        return None
    html_text = decode_body(bd)
    alg = parse_algolia_vars_from_html(html_text)
    if alg:
        return alg
    req2 = urllib.request.Request(ENTRY_URL, method="GET")
    st2, fu2, bd2 = http_open(opener, req2, debug_http=debug_http)
    if st2 >= 400:
        return None
    return parse_algolia_vars_from_html(decode_body(bd2))


def parse_search_index_from_html(html_text: str) -> Optional[str]:
    m = re.search(r'search-index="([^"]+)"', html_text)
    if not m:
        return None
    return html.unescape(m.group(1)).strip()


def algolia_headers(app_id: str, api_key: str) -> Dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-algolia-application-id": app_id,
        "x-algolia-api-key": api_key,
    }


def algolia_query(
    opener: urllib.request.OpenerDirector,
    app_id: str,
    api_key: str,
    index_name: str,
    query: str,
    hits_per_page: int,
    page: int,
    debug_http: bool = False,
) -> Dict[str, Any]:
    url = f"https://{app_id}-dsn.algolia.net/1/indexes/{urllib.parse.quote(index_name)}/query"
    payload = {"query": query, "hitsPerPage": hits_per_page, "page": page}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=algolia_headers(app_id, api_key),
    )
    status, final_url, body = http_open(opener, req, debug_http=debug_http)
    if status >= 400:
        raise RuntimeError(f"Algolia query failed: {status} {final_url}")
    return json.loads(decode_body(body))


def algolia_list_indexes(
    opener: urllib.request.OpenerDirector,
    app_id: str,
    api_key: str,
    debug_http: bool = False,
) -> List[Dict[str, Any]]:
    url = f"https://{app_id}-dsn.algolia.net/1/indexes"
    req = urllib.request.Request(url, method="GET", headers=algolia_headers(app_id, api_key))
    status, final_url, body = http_open(opener, req, debug_http=debug_http)
    if status >= 400:
        raise RuntimeError(f"Algolia list indexes failed: {status} {final_url}")
    obj = json.loads(decode_body(body))
    items = obj.get("items")
    if not isinstance(items, list):
        raise RuntimeError("Algolia list indexes returned unexpected JSON shape")
    return items


def resolve_algolia_index_name(
    opener: urllib.request.OpenerDirector,
    app_id: str,
    api_key: str,
    search_index_hint: str,
    debug_http: bool = False,
) -> str:
    # The page may advertise e.g. CABS_AJG, but the actual Algolia index might be prefixed
    # (e.g., dev_CABS_AJG). We resolve by listing indexes and matching.
    items = algolia_list_indexes(opener, app_id, api_key, debug_http=debug_http)
    candidates: List[str] = []
    for it in items:
        name = it.get("name")
        if isinstance(name, str) and (name == search_index_hint or name.endswith(search_index_hint) or search_index_hint in name):
            candidates.append(name)
    if not candidates:
        raise RuntimeError(f"Could not resolve Algolia index name from hint: {search_index_hint}")
    # Prefer exact match, then dev_ prefix, then shortest.
    if search_index_hint in candidates:
        return search_index_hint
    dev = f"dev_{search_index_hint}"
    if dev in candidates:
        return dev
    return sorted(candidates, key=lambda s: (len(s), s))[0]


def find_api_endpoints_in_js(js_text: str) -> List[str]:
    # Heuristic: look for strings that seem like API routes.
    endpoints: set[str] = set()

    for pat in [
        r"/!/[^\"'\s]+",
        r"/api/[^\"'\s]+",
        r"/academic-journal-guide[^\"'\s]+",
    ]:
        for m in re.finditer(pat, js_text):
            s = m.group(0)
            if len(s) > 3:
                endpoints.add(s)

    return sorted(endpoints)


def maybe_json_from_html(html_text: str) -> Optional[Any]:
    # Look for embedded JSON in a script tag: window.__INITIAL_STATE__ = {...}
    # This is heuristic and may fail.
    patterns = [
        r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\});",
        r"window\.__NUXT__\s*=\s*(\{.*?\});",
    ]
    for pat in patterns:
        m = re.search(pat, html_text, flags=re.DOTALL)
        if not m:
            continue
        raw = m.group(1)
        try:
            return json.loads(raw)
        except Exception:
            return None
    return None


def write_jsonl(path: str, records: Iterable[Dict[str, Any]]) -> int:
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    return n


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def flatten_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    # Flatten one level of nested dicts to keep CSV friendly.
    flat: Dict[str, Any] = {}
    for k, v in rec.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                flat[f"{k}__{k2}"] = v2
        else:
            flat[k] = v
    return flat


def normalize_value(v: Any) -> Any:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (list, tuple)):
        # JSON-encode lists
        return json.dumps(v, ensure_ascii=False)
    s = str(v).strip()
    return s


def write_csv(path: str, rows: List[Dict[str, Any]], columns: List[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: normalize_value(r.get(c, "")) for c in columns})


def choose_column_order(columns: List[str]) -> List[str]:
    # Priority groups
    priority = [
        "journal_title",
        "title",
        "journal",
        "issn",
        "issn_print",
        "issn_online",
        "ajg_rating",
        "rating",
        "rank",
        "subject_area",
        "field",
        "category",
        "publisher",
        "ajg_year",
        "source_url",
        "retrieved_at_utc",
    ]

    cols = list(dict.fromkeys(columns))
    pri = [c for c in priority if c in cols]
    rest = sorted([c for c in cols if c not in pri])
    return pri + rest


CORE_COLUMNS_PRESET_A = [
    "title",
    "field",
    "publisher",
    "print_issn",
    "e_issn",
    "ajg_2024",
    "ajg_2021",
    "ajg_2018",
    "ajg_2015",
    "abs_2010",
    "scopus_profile_url",
    "web_of_science_profile",
    "ajg_year",
]

CORE_COLUMNS_CUSTOM_DISPLAY_ORDER = [
    # Display name -> internal CSV column key mapping will be applied when writing.
    "Field",
    "Journal Title",
    "AJG 2024",
    "AJG 2021",
    "Citescore rank",
    "SNIP rank",
    "SJR rank",
    "JIF rank",
    "SDG content indicator (2017-21)",
    "International co-authorship (2017-21)",
    "Academic-non-academic collaboration (2017-21)",
    "Citations in policy documents (2017-21)",
]


def core_display_to_internal_key(display_name: str) -> str:
    mapping = {
        "Field": "field",
        "Journal Title": "title",
        "AJG 2024": "ajg_2024",
        "AJG 2021": "ajg_2021",
        "Citescore rank": "citescore_rank",
        "SNIP rank": "snip_rank",
        "SJR rank": "sjr_rank",
        "JIF rank": "jcr_rank",
        "SDG content indicator (2017-21)": "sdg_any_as_percent_of_scholarly_output_2017_2021",
        "International co-authorship (2017-21)": "intl_percent_of_co_authored_outputs_2017_2021",
        "Academic-non-academic collaboration (2017-21)": "scholarly_percent_of_scholarly_output_2017_2021",
        "Citations in policy documents (2017-21)": "policy_percent_of_scholarly_output_2017_2021__value",
    }
    if display_name not in mapping:
        raise RuntimeError(f"Unknown core display field: {display_name}")
    return mapping[display_name]


def transform_ajg_rating(value: Any) -> str:
    s = str(value).strip()
    if s == "5":
        return "4*"
    if s in {"1", "2", "3", "4", "4*"}:
        return s
    return s


def format_percent_value(internal_key: str, value: Any) -> str:
    s = str(value).strip()
    if s == "":
        return ""
    try:
        x = float(s)
    except Exception:
        return s

    # For the three “percent_of...” style fields, values are already 0-100.
    if internal_key in {
        "sdg_any_as_percent_of_scholarly_output_2017_2021",
        "intl_percent_of_co_authored_outputs_2017_2021",
        "scholarly_percent_of_scholarly_output_2017_2021",
    }:
        if x.is_integer():
            return f"{int(x)}%"
        return f"{x}%"

    # For policy_percent..., values appear to be already in 0-100 scale (median ~0.2, max ~52.7).
    # User requested: keep original value (no % symbol).
    if internal_key == "policy_percent_of_scholarly_output_2017_2021__value":
        return s

    return s


def write_csv_with_header_alias(
    path: str,
    rows: List[Dict[str, Any]],
    display_columns: List[str],
) -> None:
    internal_cols = [core_display_to_internal_key(c) for c in display_columns]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(display_columns)
        for r in rows:
            out_row: List[str] = []
            for k in internal_cols:
                v = r.get(k, "")
                if k in {"ajg_2024", "ajg_2021"}:
                    out_row.append(transform_ajg_rating(v))
                elif k in {
                    "sdg_any_as_percent_of_scholarly_output_2017_2021",
                    "intl_percent_of_co_authored_outputs_2017_2021",
                    "scholarly_percent_of_scholarly_output_2017_2021",
                    "policy_percent_of_scholarly_output_2017_2021__value",
                }:
                    out_row.append(format_percent_value(k, v))
                else:
                    out_row.append(normalize_value(v))
            w.writerow(out_row)


def normalize_title(s: str) -> str:
    if not s:
        return ""
    t = str(s).strip().lower()
    t = re.sub(r"[’'`]", "", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    t = re.sub(r"\\s+", " ", t).strip()
    return t


def detect_records_in_json(obj: Any) -> Optional[List[Dict[str, Any]]]:
    # Try common shapes: {data:[...]} or {items:[...]} or directly a list.
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        return obj
    if isinstance(obj, dict):
        for key in ["data", "items", "results", "journals", "records"]:
            v = obj.get(key)
            if isinstance(v, list) and (not v or isinstance(v[0], dict)):
                return v  # type: ignore[return-value]
    return None


def attempt_fetch_data_via_api_probe(
    opener: urllib.request.OpenerDirector,
    entry_url: str,
    debug_http: bool = False,
) -> Tuple[Optional[str], Optional[Any]]:
    # Preferred: AJG uses Algolia (InstantSearch). Try using Algolia credentials embedded in HTML.
    req = urllib.request.Request(entry_url, method="GET")
    status, final_url, body = http_open(opener, req, debug_http=debug_http)
    if status >= 400:
        raise RuntimeError(f"Failed to fetch AJG entry page (post-login): {status} {final_url}")

    html_text = decode_body(body)
    if is_gated_page(html_text):
        raise RuntimeError("AJG page still gated after login")

    alg = parse_algolia_vars_from_html(html_text)
    if not alg:
        alg = parse_algolia_vars_from_html_or_entry(opener, entry_url, debug_http=debug_http)
    idx_hint = parse_search_index_from_html(html_text)
    if alg and idx_hint:
        app_id, api_key, _use_dev = alg
        resolved = resolve_algolia_index_name(opener, app_id, api_key, idx_hint, debug_http=debug_http)
        # Fetch all pages
        first = algolia_query(opener, app_id, api_key, resolved, query="", hits_per_page=1000, page=0, debug_http=debug_http)
        hits0 = first.get("hits")
        if not (isinstance(hits0, list) and (not hits0 or isinstance(hits0[0], dict))):
            return None, None
        nb_pages = int(first.get("nbPages") or 1)
        all_hits: List[Dict[str, Any]] = list(hits0)  # type: ignore[arg-type]
        for p in range(1, nb_pages):
            page_obj = algolia_query(opener, app_id, api_key, resolved, query="", hits_per_page=1000, page=p, debug_http=debug_http)
            page_hits = page_obj.get("hits")
            if not (isinstance(page_hits, list) and (not page_hits or isinstance(page_hits[0], dict))):
                raise RuntimeError(f"Algolia page {p} returned unexpected hits shape")
            all_hits.extend(page_hits)  # type: ignore[arg-type]
        return f"algolia:{resolved}", all_hits

    # Fallback: download module JS and scan for endpoints.
    module_src = extract_first_module_script_src(html_text)
    if not module_src:
        return None, None

    # Fetch module JS
    req2 = urllib.request.Request(module_src, method="GET")
    status2, final_url2, body2 = http_open(opener, req2, debug_http=debug_http)
    if status2 >= 400:
        return None, None

    js_text = decode_body(body2)
    endpoints = find_api_endpoints_in_js(js_text)

    # Prefer endpoints that look like data endpoints
    preferred = [e for e in endpoints if "ajg" in e.lower() or "journal" in e.lower()]
    candidates = preferred + [e for e in endpoints if e not in preferred]

    # Try GET each candidate endpoint if it looks like a JSON endpoint.
    # We only try a small number to avoid hammering the site.
    for ep in candidates[:25]:
        url = urllib.parse.urljoin(BASE, ep)
        # Skip obvious auth endpoints
        if ep.startswith("/!/auth/"):
            continue
        req3 = urllib.request.Request(url, method="GET", headers={"Accept": "application/json,*/*"})
        try:
            st, fu, bd = http_open(opener, req3, debug_http=debug_http)
        except Exception:
            continue
        if st >= 400:
            continue
        text = decode_body(bd)
        # quick json check
        if not text.strip().startswith(("{", "[")):
            continue
        try:
            obj = json.loads(text)
        except Exception:
            continue
        recs = detect_records_in_json(obj)
        if recs is not None and len(recs) > 10:
            return url, obj

    # Also try embedded JSON
    embedded = maybe_json_from_html(html_text)
    if embedded is not None:
        recs = detect_records_in_json(embedded)
        if recs is not None and len(recs) > 10:
            return "embedded", embedded

    return None, None


def build_rows_from_records(
    records: List[Dict[str, Any]],
    ajg_year: int,
    source_url: str,
    retrieved_at_utc: str,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for rec in records:
        flat = flatten_record(rec)
        flat["ajg_year"] = ajg_year
        flat["source_url"] = source_url
        flat["retrieved_at_utc"] = retrieved_at_utc
        rows.append(flat)
    return rows


def dedupe_rows(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    seen: set[str] = set()
    out: List[Dict[str, Any]] = []
    dup = 0
    for r in rows:
        title = str(r.get("journal_title") or r.get("title") or r.get("journal") or "").strip().lower()
        issn = str(r.get("issn") or "").strip().lower()
        key = f"{title}||{issn}"
        if key in seen and key != "||":
            dup += 1
            continue
        seen.add(key)
        out.append(r)
    return out, dup


def append_progress(msg: str) -> None:
    skill_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    plan_dir = os.environ.get("ABS_JOURNAL_PLAN_DIR", "").strip() or os.path.join(skill_root, "plan")
    try:
        os.makedirs(plan_dir, exist_ok=True)
        path = os.path.join(plan_dir, "progress.md")
        ts = _dt.datetime.now().strftime("%H:%M")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"- {ts} {msg}\n")
        return
    except Exception:
        fallback = os.path.join("/tmp", "abs-journal-plan")
        os.makedirs(fallback, exist_ok=True)
        path = os.path.join(fallback, "progress.md")
        ts = _dt.datetime.now().strftime("%H:%M")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"- {ts} {msg}\n")


def append_findings(msg: str) -> None:
    skill_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    plan_dir = os.environ.get("ABS_JOURNAL_PLAN_DIR", "").strip() or os.path.join(skill_root, "plan")
    try:
        os.makedirs(plan_dir, exist_ok=True)
        path = os.path.join(plan_dir, "findings.md")
        with open(path, "a", encoding="utf-8") as f:
            f.write(msg.rstrip() + "\n")
        return
    except Exception:
        fallback = os.path.join("/tmp", "abs-journal-plan")
        os.makedirs(fallback, exist_ok=True)
        path = os.path.join(fallback, "findings.md")
        with open(path, "a", encoding="utf-8") as f:
            f.write(msg.rstrip() + "\n")


def mask_secret(s: str) -> str:
    if not s:
        return ""
    if len(s) <= 4:
        return "*" * len(s)
    return s[:2] + "*" * (len(s) - 4) + s[-2:]


def main() -> int:
    # Help color tests:
    #   NO_COLOR=1 python scripts/ajg_fetch.py -h
    #   FORCE_COLOR=1 python scripts/ajg_fetch.py -h
    ap = argparse.ArgumentParser(formatter_class=ColorHelpFormatter)
    ap.add_argument("--outdir", required=True, help="绝对路径输出目录")
    # For UX validation: include at least one choices argument.
    ap.add_argument("--mode", default="core", choices=["core"], help="运行模式（当前仅core）")
    ap.add_argument("--overwrite", action="store_true", help="允许覆盖既有输出文件（默认不覆盖）")
    ap.add_argument("--debug-http", action="store_true")
    args = ap.parse_args()

    outdir = os.path.abspath(args.outdir)
    if not os.path.isabs(outdir):
        raise RuntimeError("--outdir 必须是绝对路径")
    try:
        os.makedirs(outdir, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"无法创建输出目录: {outdir}: {e}")

    if not os.path.isdir(outdir):
        raise RuntimeError(f"输出目录不是一个目录: {outdir}")

    if not os.access(outdir, os.W_OK):
        raise RuntimeError(f"输出目录不可写: {outdir}")

    email = os.environ.get("AJG_EMAIL", "").strip()
    password = os.environ.get("AJG_PASSWORD", "").strip()
    if not email or not password:
        missing = []
        if not email:
            missing.append("AJG_EMAIL")
        if not password:
            missing.append("AJG_PASSWORD")
        missing_s = ", ".join(missing) if missing else "AJG_EMAIL/AJG_PASSWORD"
        raise RuntimeError(
            "缺少环境变量（默认从环境变量读取登录凭据）："
            f"{missing_s}\n"
            "请在当前终端会话中设置：\n"
            "  export AJG_EMAIL=\"lingguiwang@yeah.net\"\n"
            "  export AJG_PASSWORD=\"你的密码\"\n"
            "也可参考示例文件（不要提交真实密码）：scripts/ajg_config.example.env"
        )

    opener = build_opener()

    append_progress("开始：探测最新AJG入口")
    latest_year, latest_url = discover_latest_year_and_url(opener, debug_http=args.debug_http)
    ajg_year = latest_year
    entry_url = latest_url

    append_progress(f"最新AJG入口：{ajg_year} {entry_url}")

    append_progress("开始：自动化登录")
    append_progress(f"使用账号：{email} 密码：{mask_secret(password)}（仅用于本地会话，不写入文件）")
    do_login(opener, email=email, password=password, debug_http=args.debug_http)

    # Verify access
    req = urllib.request.Request(entry_url, method="GET")
    st, fu, bd = http_open(opener, req, debug_http=args.debug_http)
    if st >= 400:
        raise RuntimeError(f"Failed to fetch AJG page after login: {st} {fu}")
    ht = decode_body(bd)
    if is_gated_page(ht):
        raise RuntimeError("登录后仍被 gate 拦截（可能需要验证码/权限不足）")

    append_progress("登录验证通过：可访问AJG页面")

    append_progress("开始：探测数据API/嵌入数据")
    api_url, obj = attempt_fetch_data_via_api_probe(opener, entry_url, debug_http=args.debug_http)
    if api_url is None or obj is None:
        raise RuntimeError("未能自动定位AJG数据接口/嵌入数据（需要进一步人工抓包或增加解析逻辑）")

    append_findings(f"\n## 数据入口探测结果（{utc_now_iso()}）\n")
    append_findings(f"- 发现可用数据源：{api_url}\n")

    records = detect_records_in_json(obj)
    if records is None:
        raise RuntimeError("数据源返回JSON但未识别到records列表结构")

    retrieved_at = utc_now_iso()

    raw_path = os.path.join(outdir, f"ajg_{ajg_year}_journals_raw.jsonl")
    core_csv_custom_path = os.path.join(outdir, f"ajg_{ajg_year}_journals_core_custom.csv")
    meta_path = os.path.join(outdir, f"ajg_{ajg_year}_meta.json")

    out_paths = [raw_path, core_csv_custom_path, meta_path]
    if not args.overwrite:
        existing = [p for p in out_paths if os.path.exists(p)]
        if existing:
            raise RuntimeError(
                "输出文件已存在（默认不覆盖）。如需覆盖请加 --overwrite。已存在: "
                + ", ".join(existing)
            )

    append_progress(f"写入原始数据：{raw_path}")
    raw_count = write_jsonl(raw_path, records)

    rows = build_rows_from_records(records, ajg_year=ajg_year, source_url=entry_url, retrieved_at_utc=retrieved_at)
    rows, dup = dedupe_rows(rows)

    # Collect columns
    col_set: set[str] = set()
    for r in rows:
        col_set.update(r.keys())
    columns = choose_column_order(sorted(col_set))

    # Default output mode: ONLY core custom CSV + json/jsonl.
    append_progress(f"写入核心列CSV（自定义表头）：{core_csv_custom_path}")
    write_csv_with_header_alias(core_csv_custom_path, rows, CORE_COLUMNS_CUSTOM_DISPLAY_ORDER)

    meta = {
        "ajg_year": ajg_year,
        "entrypoint_url": entry_url,
        "data_source": api_url,
        "retrieved_at_utc": retrieved_at,
        "raw_count": raw_count,
        "row_count": len(rows),
        "duplicate_count": dup,
        "columns": columns,
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    append_progress(f"写入元数据：{meta_path}")
    # Output contract verification (fail fast for downstream consumers)
    missing = [p for p in out_paths if not os.path.isfile(p)]
    if missing:
        raise RuntimeError("输出契约校验失败：以下文件未成功写出: " + ", ".join(missing))

    required_meta_keys = ["retrieved_at_utc", "ajg_year", "entrypoint_url"]
    for k in required_meta_keys:
        if k not in meta:
            raise RuntimeError(f"元数据缺少必要字段: {k}")

    append_progress("完成")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        append_progress(f"失败：{e}")
        sys.stderr.write(f"ERROR: {e}\n")
        raise

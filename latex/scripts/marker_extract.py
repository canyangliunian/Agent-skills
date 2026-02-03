#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""marker_extract.py
====================
简要说明
- 从 PDF 提取正文、图片、公式与参考文献
- 自动生成 references.txt 与 references.bib
- 支持 OpenAI/DeepSeek/ChatAnywhere/Ollama 等 OpenAI-compatible 接口

常用示例
1) 本地默认：
   python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py \
     "/abs/path/to/your.pdf" \
     -o "/abs/path/to/marker_out"
2) LLM（ChatAnywhere）：
   python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py \
     "/abs/path/to/your.pdf" \
     -o "/abs/path/to/marker_out" \
     --use_llm --provider chatanywhere
3) 仅列出 ChatAnywhere 可用模型：
   python /Users/lingguiwang/.codex/skills/latex/scripts/marker_extract.py --list_chatanywhere_models
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# 测试（请保留这些注释，便于未来快速验证）：
# NO_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/marker_extract.py -h
# NO_COLOR= FORCE_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/marker_extract.py -h

ANSI_RESET = "\x1b[0m"
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

        parts = text.split()
        out: List[str] = []
        for p in parts:
            if p.startswith("-"):
                out.append(colorize(p, ANSI_CYAN_BOLD))
            elif p.isupper() or "_" in p:
                out.append(colorize(p, ANSI_YELLOW_BOLD))
            else:
                out.append(p)
        return " ".join(out)


# ============================================================
# Provider defaults
# ============================================================

PROVIDERS: Dict[str, Dict[str, str]] = {
    "openai": {
        "url": "https://api.openai.com/v1",
        "key_env": "OPENAI_API_KEY",
        "model": "gpt-5.2",
    },
    "deepseek": {
        "url": "https://api.deepseek.com",
        "key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-chat",
    },
    "ollama": {
        "url": "http://localhost:11434/v1",
        "key_env": "OLLAMA_API_KEY",  # 可选；缺失时用 "ollama"
        "model": "qwen3:8b",
    },
    "chatanywhere": {
        "url": "https://api.chatanywhere.tech/v1",
        "key_env": "CHATANYWHERE_API_KEY",
        "model": "gpt-5.2",
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1",            # 假设这是openrouter的API地址
        "key_env": "OPENROUTER_API_KEY",  # 假设这是openrouter的API Key环境变量
        "model": "openai/gpt-5.2",                          # 请根据实际情况填写模型名称
    },
}

# ============================================================
# ChatAnywhere model list (for CLI selection)
# ============================================================

CHATANYWHERE_MODEL_GROUPS = [
    ("免费版（每天总共5次）", [
        "gpt-5.2",
        "gpt-5.1",
        "gpt-5",
        "gpt-4o",
        "gpt-4.1",
    ]),
    ("支持（每天 总共30 次）", [
        "deepseek-r1",
        "deepseek-v3",
        "deepseek-v3-2-exp",
    ]),
    ("支持（每天 总共200 次）", [
        "gpt-4o-mini",
        "gpt-3.5-turbo",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "gpt-5-mini",
        "gpt-5-nano",
    ]),
]

# ============================================================
# Ollama helpers (model discovery + proxy hygiene)
# ============================================================

def _ensure_localhost_no_proxy() -> None:
    """
    避免 http(s)_proxy 劫持 localhost/127.0.0.1 访问，导致 000/502/超时。
    在进程内强制 NO_PROXY，并清理 proxy env（仅影响当前进程）。
    """
    required = ["localhost", "127.0.0.1"]
    cur = os.environ.get("NO_PROXY") or os.environ.get("no_proxy") or ""
    parts = [p.strip() for p in cur.split(",") if p.strip()]
    for r in required:
        if r not in parts:
            parts.append(r)
    val = ",".join(parts) if parts else ",".join(required)
    os.environ["NO_PROXY"] = val
    os.environ["no_proxy"] = val

    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        os.environ.pop(k, None)


def _ollama_models_via_http() -> List[str]:
    try:
        import requests  # local import
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        if r.status_code != 200:
            return []
        data = r.json()
        out: List[str] = []
        for it in (data.get("models") or []):
            name = it.get("name")
            if isinstance(name, str) and name.strip():
                out.append(name.strip())
        return out
    except Exception:
        return []


def _ollama_models_via_cli() -> List[str]:
    try:
        import subprocess
        out = subprocess.check_output(["ollama", "list"], stderr=subprocess.STDOUT, text=True, timeout=3)
        models: List[str] = []
        for line in out.splitlines()[1:]:
            parts = line.split()
            if parts:
                models.append(parts[0].strip())
        return models
    except Exception:
        return []


def _ollama_list_models() -> List[str]:
    models = _ollama_models_via_http()
    if models:
        return models
    return _ollama_models_via_cli()


def _choose_ollama_model(requested: Optional[str], allow_cloud: bool = False) -> Optional[str]:
    """
    requested 非空则直接返回；
    否则从本机已安装模型里挑选：本地模型优先（尽量排除 *cloud*）。
    """
    if requested and requested.strip():
        return requested.strip()

    models = _ollama_list_models()
    if not models:
        return None

    if allow_cloud:
        return models[0]

    local = [m for m in models if "cloud" not in m.lower()]
    if local:
        # 简单优先级：小模型优先（8b/14b > 30b > 120b ...）
        def score(name: str) -> int:
            m = re.search(r"(\d+)\s*b", name.lower().replace("-", ""))
            if m:
                return int(m.group(1))
            m2 = re.search(r"(\d+)b", name.lower())
            if m2:
                return int(m2.group(1))
            return 10_000
        return sorted(local, key=score)[0]

    return models[0]


def _warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def choose_chatanywhere_model(default_model: str) -> str:
    """
    在 TTY 下提供交互式模型选择。
    """
    if not sys.stdin.isatty():
        return default_model

    print("\n[ChatAnywhere] 可用模型列表：")
    options: List[str] = []
    idx = 1
    for group, models in CHATANYWHERE_MODEL_GROUPS:
        print(f"  {group}:")
        for m in models:
            print(f"    {idx}. {m}")
            options.append(m)
            idx += 1

    print(f"\n请输入模型编号（回车使用默认：{default_model}；输入 q 退出）：", end="")
    try:
        choice = input().strip()
    except EOFError:
        return default_model

    if choice.lower() == "q":
        print("[INFO] 用户取消选择，使用默认模型。")
        return default_model
    if not choice:
        return default_model
    if choice.isdigit():
        i = int(choice)
        if 1 <= i <= len(options):
            return options[i - 1]
    print("[WARN] 输入无效，使用默认模型。")
    return default_model

# ============================================================
# Helper Functions
# ============================================================

def references_to_bibtex(references: str) -> str:
    """
    将提取的参考文献文本转换为BibTeX格式。
    假设输入的参考文献是简化的条目，如：`[1] Author, Title, Journal, Year.`
    """

    def _clean_ref_line(ref: str) -> str:
        s = ref.strip()
        # 去掉 markdown 加粗标记
        s = s.replace("**", "")
        s = s.replace("–", "-")
        s = re.sub(r"^\[\d+\]\s*", "", s)
        s = re.sub(r"^\(?\d{1,3}\)?[.\)]\s*", "", s)
        s = re.sub(r"^(\*|-|\u2022)\s+", "", s)
        return s.strip()

    def _make_key(author: str, year: str, title: str) -> str:
        base = (author.split()[0] if author else "ref").lower()
        yr = re.sub(r"\D", "", year)[:4] if year else "noyear"
        h = hashlib.md5(title.encode("utf-8")).hexdigest()[:6] if title else "000000"
        key = f"{base}{yr}{h}"
        return re.sub(r"[^a-z0-9]+", "", key)

    def parse_reference(ref: str) -> str:
        s = _clean_ref_line(ref)
        if not s:
            return ""

        # 提取年份
        year = ""
        m = re.search(r"\b(19|20)\d{2}\b", s)
        if m:
            year = m.group(0)

        author = ""
        title = ""
        journal = ""

        # 标题：优先取引号内内容（兼容英文引号）
        m_title = re.search(r"[\"“”](.+?)[\"“”]", s)
        if m_title:
            title = m_title.group(1).strip()
            before = s[:m_title.start()].strip()
            after = s[m_title.end():].strip(" .")
            author = before.strip(" ,")
            journal = after
        else:
            # 无引号：用首个句号划分作者与标题
            if "." in s:
                first, rest = s.split(".", 1)
                author = first.strip(" ,")
                rest = rest.strip()
                # 标题到下一个句号为止
                if "." in rest:
                    title, rest2 = rest.split(".", 1)
                    title = title.strip(" ,")
                    journal = rest2.strip()
                else:
                    title = rest.strip(" ,")
            else:
                author = s.strip()

        # 清理 journal 尾部年份等信息
        if journal:
            journal = re.sub(r"\s*\(?\b(19|20)\d{2}\b.*$", "", journal).strip(" ,;")
        if title:
            title = title.strip(" .")

        entry_type = "article" if journal else "misc"
        key = _make_key(author, year, title)

        fields = [
            f"  author = {{{author}}}" if author else None,
            f"  title = {{{title}}}" if title else None,
            f"  journal = {{{journal}}}" if journal else None,
            f"  year = {{{year}}}" if year else None,
        ]
        fields = [f for f in fields if f]
        if not fields:
            # 尽量保留原始信息，避免条目丢失
            return f"@misc{{{key},\n  note = {{{s}}}\n}}"

        bibtex_entry = f"@{entry_type}{{{key},\n" + ",\n".join(fields) + "\n}}"
        return bibtex_entry


    bib_entries = []
    for line in references.splitlines():
        bib_entry = parse_reference(line)
        if bib_entry:
            bib_entries.append(bib_entry)

    return "\n\n".join(bib_entries)

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def is_pdf(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() == ".pdf"


def iter_pdfs(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        if is_pdf(input_path):
            yield input_path
        return
    # 仅支持单 PDF；目录输入在 main 中会被拦截
    return


def save_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def pydantic_dump(obj: Any) -> Any:
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, (dict, list, str, int, float, bool)):
        return obj
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


def json_safe(obj: Any, *, _depth: int = 0, _max_depth: int = 32) -> Any:
    """
    递归把对象转换为可 json.dump 的结构，避免 metadata.json 写入崩溃。
    - PIL.Image.Image -> {"__type__":"PIL.Image","mode":...,"size":[w,h]}
    - bytes -> {"__type__":"bytes","len":N}
    - Path -> str
    - set/tuple -> list
    - 其它不可序列化 -> str(obj)
    """
    if _depth > _max_depth:
        return "<max_depth_reached>"

    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, Path):
        return str(obj)

    # bytes-like
    if isinstance(obj, (bytes, bytearray, memoryview)):
        return {"__type__": "bytes", "len": int(len(obj))}

    # PIL Image (lazy import)
    try:
        from PIL import Image  # type: ignore
        if isinstance(obj, Image.Image):
            return {
                "__type__": "PIL.Image",
                "mode": getattr(obj, "mode", None),
                "size": list(getattr(obj, "size", (None, None))),
            }
    except Exception:
        pass

    # dict
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            # key 强制 string
            ks = str(k)
            out[ks] = json_safe(v, _depth=_depth + 1, _max_depth=_max_depth)
        return out

    # list/tuple/set
    if isinstance(obj, (list, tuple, set)):
        return [json_safe(x, _depth=_depth + 1, _max_depth=_max_depth) for x in obj]

    # numpy / torch tensors (best-effort)
    if hasattr(obj, "tolist"):
        try:
            return obj.tolist()
        except Exception:
            pass

    # pydantic model / dataclass
    if hasattr(obj, "model_dump"):
        try:
            return json_safe(obj.model_dump(), _depth=_depth + 1, _max_depth=_max_depth)
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        try:
            return json_safe(obj.__dict__, _depth=_depth + 1, _max_depth=_max_depth)
        except Exception:
            pass

    return str(obj)


# ============================================================
# Images saving
# ============================================================

def save_images(images: Any, out_dir: Path) -> Tuple[int, List[str]]:
    written: List[str] = []
    if images is None:
        return 0, written

    def sanitize_name(name: str) -> str:
        name = name.replace("\\", "_").replace("/", "_").strip()
        name = re.sub(r"[^A-Za-z0-9_.\-]+", "_", name)
        return name[:180] if name else ""

    def save_one(name: str, img_obj: Any) -> None:
        base = sanitize_name(name) or f"image_{len(written)+1:03d}"
        out_path = out_dir / (base if base.lower().endswith((".png", ".jpg", ".jpeg", ".webp")) else f"{base}.png")
        try:
            if hasattr(img_obj, "save"):
                img_obj.save(out_path)
            elif isinstance(img_obj, (bytes, bytearray)):
                out_path.write_bytes(img_obj)
            else:
                out_path.write_text(str(img_obj), encoding="utf-8")
            written.append(out_path.name)
        except Exception as e:
            (out_dir / f"{out_path.stem}__ERROR.txt").write_text(
                f"Failed saving image {out_path.name}: {repr(e)}",
                encoding="utf-8",
            )

    if isinstance(images, dict):
        for k, v in images.items():
            save_one(str(k), v)
    elif isinstance(images, (list, tuple)):
        for it in images:
            if isinstance(it, (list, tuple)) and len(it) == 2:
                save_one(str(it[0]), it[1])
            else:
                save_one(f"image_{len(written)+1:03d}", it)
    else:
        save_one("images_dump", images)

    return len(written), written


# ============================================================
# Markdown image link rewrite (document.md -> images/<file>)
# ============================================================

MD_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

def rewrite_markdown_image_paths(md: str, saved_image_files: List[str], images_dir_name: str = "images") -> str:
    """
    Marker 生成的 Markdown 往往写成: ![](_page_0_Picture_0.jpeg)
    但我们把图片存到 images/ 目录下，因此需要把链接改成:
      ![](images/_page_0_Picture_0.jpeg)

    只改“本地文件名”且确实存在于 saved_image_files 的条目；不会改 URL 或绝对路径。
    """
    if not md or not saved_image_files:
        return md

    saved = set(saved_image_files)

    def is_url(p: str) -> bool:
        return "://" in p or p.startswith("data:")

    def normalize_rel(p: str) -> str:
        p = p.strip()
        if p.startswith("./"):
            p = p[2:]
        return p

    def repl(m: re.Match) -> str:
        alt = m.group(1)
        inside = m.group(2).strip()

        # handle <...> form
        path_part = inside
        tail = ""
        if inside.startswith("<") and ">" in inside:
            j = inside.find(">")
            path_part = inside[1:j].strip()
            tail = inside[j+1:]  # keep any title/space
            wrapped = True
        else:
            # split first token as path; keep remainder (title)
            sp = inside.find(" ")
            if sp == -1:
                path_part = inside
                tail = ""
            else:
                path_part = inside[:sp]
                tail = inside[sp:]
            wrapped = False

        path_part = normalize_rel(path_part)

        # skip if already points to images/
        if path_part.startswith(images_dir_name + "/") or path_part.startswith(images_dir_name + "\\"):
            return m.group(0)

        # skip url / absolute
        if is_url(path_part) or path_part.startswith("/") or path_part.startswith("~"):
            return m.group(0)

        fname = Path(path_part).name
        if fname in saved:
            new_path = f"{images_dir_name}/{fname}"
            if wrapped:
                new_inside = f"<{new_path}>{tail}"
            else:
                new_inside = f"{new_path}{tail}"
            return f"![{alt}]({new_inside})"

        return m.group(0)

    return MD_IMAGE_RE.sub(repl, md)


# ============================================================
# Equations extraction
# ============================================================

EQ_BLOCK_RE = re.compile(r"\$\$(.+?)\$\$", flags=re.DOTALL)

def extract_equations_from_markdown(md: str) -> List[str]:
    eqs = [m.group(1).strip() for m in EQ_BLOCK_RE.finditer(md or "")]
    uniq: List[str] = []
    seen = set()
    for e in eqs:
        if e and e not in seen:
            seen.add(e)
            uniq.append(e)
    return uniq


def walk_json(obj: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk_json(v)
    elif isinstance(obj, list):
        for it in obj:
            yield from walk_json(it)


def _get_page_from_node(node: Dict[str, Any]) -> Optional[int]:
    """
    Marker 的 JSON 结构在不同版本可能使用不同字段表示页码。
    这里做尽可能宽松的兼容：
      page / page_number / page_num / page_idx / page_index
    统一返回 1-based 页码（更符合人类阅读）；若无法确定返回 None。
    """
    for k in ("page_number", "page_num", "page", "page_idx", "page_index"):
        v = node.get(k)
        if isinstance(v, int):
            if k in ("page_idx", "page_index"):
                return v + 1
            return v + 1 if v == 0 else v
        if isinstance(v, str) and v.strip().isdigit():
            iv = int(v.strip())
            if k in ("page_idx", "page_index"):
                return iv + 1
            return iv + 1 if iv == 0 else iv
    return None


def extract_equations_from_rendered_dump(rendered_dump: Any) -> List[str]:
    """
    兼容旧逻辑：只返回 latex/tex 字符串列表（不含页码）。
    """
    items = extract_equations_with_locations(rendered_dump)
    uniq: List[str] = []
    seen = set()
    for it in items:
        e = it.get("latex")
        if not e or not isinstance(e, str):
            continue
        if e not in seen:
            seen.add(e)
            uniq.append(e)
    return uniq


def extract_equations_with_locations(rendered_dump: Any) -> List[Dict[str, Any]]:
    """
    从 rendered_dump 里尽量提取：
      - latex/tex
      - page（1-based）
      - block_type
    返回按文档遍历顺序的列表（通常与正文顺序一致）。
    """
    out: List[Dict[str, Any]] = []
    if rendered_dump is None:
        return out

    for node in walk_json(rendered_dump):
        bt = str(node.get("block_type", "")).strip()
        if bt not in ("Equation", "TextInlineMath"):
            continue

        latex: Optional[str] = None
        for key in ("latex", "tex", "text", "content"):
            val = node.get(key)
            if isinstance(val, str) and val.strip():
                latex = val.strip()
                break
        if not latex:
            continue

        if len(latex) > 8000:
            continue

        page = _get_page_from_node(node)

        out.append({
            "latex": latex,
            "page": page,
            "block_type": bt,
        })

    # 去重：保持首次出现的顺序
    dedup: List[Dict[str, Any]] = []
    seen = set()
    for it in out:
        e = it["latex"]
        if e in seen:
            continue
        seen.add(e)
        dedup.append(it)
    return dedup


# ============================================================
# References extraction
# ============================================================

def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def reference_heading_match(line: str) -> Optional[Tuple[int, str]]:
    m = re.match(
        r"^\s{0,3}(#{1,6})\s*(?:\d+\s*[\.\)]\s*)?"
        r"(?:\*\*|__)?\s*"
        r"(references|bibliography|works cited|literature cited|参考文献|引用文献|文献|参考资料)"
        r"\s*(?:\*\*|__)?\s*$",
        line,
        flags=re.IGNORECASE,
    )
    if not m:
        return None
    return len(m.group(1)), normalize_ws(m.group(2).lower())


def looks_like_reference_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if re.match(r"^(\*|-|\u2022)\s+\S+", s):
        return True
    if re.match(r"^\[\d+\]\s+\S+", s):
        return True
    if re.match(r"^\(?\d{1,3}\)?[.\)]\s+\S+", s):
        return True
    if re.search(r"\b(19|20)\d{2}\b", s) and re.search(
        r"\b(pp\.|vol\.|no\.|journal|review|working paper|press|university|proceedings)\b",
        s,
        re.IGNORECASE,
    ):
        return True
    if re.search(r"\b(19|20)\d{2}\b", s) and re.match(r"^[A-Z][A-Za-z'`\-]+,\s*[A-Z]", s):
        return True
    return False


def extract_references(md: str, mode: str = "balanced") -> str:
    lines = (md or "").splitlines()
    n = len(lines)
    if n == 0:
        return ""

    heading_idx = None
    heading_level = None

    for i in range(n - 1, -1, -1):
        m = reference_heading_match(lines[i])
        if m:
            heading_level, _kw = m
            heading_idx = i
            break

    def collect_from(start_idx: int) -> List[str]:
        if start_idx >= n:
            return []
        # 跳过标题行本身，从下一行开始收集
        start = start_idx + 1
        out = lines[start:]
        if heading_level is not None:
            stop = None
            for j in range(start + 1, n):
                m2 = re.match(r"^\s{0,3}(#{1,6})\s+\S+", lines[j])
                if m2 and len(m2.group(1)) <= heading_level:
                    stop = j
                    break
            if stop is not None:
                out = lines[start:stop]
        return out

    raw: List[str] = collect_from(heading_idx) if heading_idx is not None else []

    if not raw and mode in ("balanced", "loose"):
        tail_start = int(n * (0.70 if mode == "balanced" else 0.60))
        tail = lines[tail_start:]
        best_score = 0
        best_slice: Optional[Tuple[int, int]] = None
        window = 140
        step = 25
        for s in range(0, max(1, len(tail) - 10), step):
            e = min(len(tail), s + window)
            chunk = tail[s:e]
            score = sum(1 for ln in chunk if looks_like_reference_line(ln))
            if score >= 8 and score > best_score:
                best_score = score
                best_slice = (s, e)
        if best_slice:
            s, e = best_slice
            raw = tail[s:e]

    if not raw:
        return ""

    out: List[str] = []
    started = False
    for ln in raw:
        if looks_like_reference_line(ln):
            out.append(ln.rstrip())
            started = True
            continue
        if started and (ln.startswith("  ") or ln.startswith("\t")) and ln.strip():
            out.append(ln.rstrip())
            continue

    if mode != "strict" and len(out) < 10:
        out = [x.rstrip() for x in raw if x.strip()]

    return "\n".join(out).strip()


def count_reference_entries(refs: str) -> int:
    if not refs:
        return 0
    lines = [ln.strip() for ln in refs.splitlines() if ln.strip()]
    if not lines:
        return 0
    start_lines = 0
    for ln in lines:
        if re.match(r"^(\*|-|\u2022)\s+\S+", ln):
            start_lines += 1
            continue
        if re.match(r"^\[\d+\]\s+\S+", ln):
            start_lines += 1
            continue
        if re.match(r"^\(?\d{1,3}\)?[.\)]\s+\S+", ln):
            start_lines += 1
            continue
    return start_lines if start_lines > 0 else len(lines)


def fix_reference_continuations(refs: str) -> str:
    """
    修复参考文献中“同一作者用 —— 或省略作者”的行：
    例如：", AND GRILICHES, Z." / "AND SCOTCHMER, S." / "——" 等，
    用上一条参考文献的作者前缀补齐。
    """
    if not refs:
        return refs

    lines = refs.splitlines()
    out: List[str] = []
    last_author_prefix = ""

    def extract_author_prefix(core: str) -> str:
        if not core:
            return ""
        for q in ('"', "“", "”"):
            if q in core:
                return core.split(q, 1)[0].strip()
        m = re.search(r"\.\s+[A-Z]", core)
        if m:
            return core[:m.start()].strip()
        return ""

    def is_continuation(core: str) -> bool:
        s = core.lstrip()
        return s.startswith((", ", ",", "AND ", "and ", "& ", "—", "——", "- "))

    for line in lines:
        if not line.strip():
            out.append(line)
            continue

        m = re.match(r"^(\s*-\s+)", line)
        prefix = m.group(1) if m else ""
        rest = line[len(prefix):] if prefix else line

        bold = rest.startswith("**") and rest.endswith("**") and len(rest) >= 4
        core = rest[2:-2] if bold else rest

        if is_continuation(core) and last_author_prefix:
            s = core.lstrip()
            s = s.lstrip(" ,—-")
            core = f"{last_author_prefix} {s}".strip()

        # 更新作者前缀（仅对非延续行）
        if not is_continuation(core):
            cand = extract_author_prefix(core)
            if cand:
                last_author_prefix = cand

        new_rest = f"**{core}**" if bold else core
        out.append(prefix + new_rest)

    return "\n".join(out)


# ============================================================
# Provider config to Marker OpenAIService parameters
# ============================================================

@dataclass
class ProviderConfig:
    provider: str
    url: str
    api_key: str
    model: str


def get_provider_config(provider: str, url: Optional[str], key: Optional[str], model: Optional[str], *, ollama_allow_cloud: bool = False, apply_proxy_fix: bool = True) -> ProviderConfig:
    if provider not in PROVIDERS:
        raise ValueError(f"Unsupported provider={provider}. Supported: {', '.join(PROVIDERS.keys())}")

    base = PROVIDERS[provider]
    final_url = (url or base["url"]).rstrip("/")
    final_model = model or base["model"]

    # provider=chatanywhere：若未显式指定 model，提供交互式选择
    if provider == "chatanywhere" and not model:
        final_model = choose_chatanywhere_model(final_model)

    # provider=ollama：修复 proxy 劫持 localhost，并在未指定 model 时自动挑选已安装模型
    if provider == "ollama":
        if apply_proxy_fix:
            _ensure_localhost_no_proxy()
        chosen = _choose_ollama_model(model, allow_cloud=ollama_allow_cloud)
        if chosen:
            final_model = chosen
        else:
            _warn("provider=ollama but no local models found from /api/tags or `ollama list`. LLM steps may fail.")

    env_name = base.get("key_env", "")
    env_key = os.getenv(env_name) if env_name else None
    final_key = key or env_key

    # Ollama 通常不需要 key；Marker OpenAIService 仍要求一个字符串，这里给默认值
    if not final_key:
        if provider == "ollama":
            final_key = "ollama"
        else:
            raise ValueError(f"Missing API key for provider={provider}. Please set env {env_name} or pass --key.")

    return ProviderConfig(provider=provider, url=final_url, api_key=final_key, model=final_model)


# ============================================================
# Processing pipeline per PDF
# ============================================================

@dataclass
class ExtractManifest:
    input_pdf: str
    output_dir: str
    output_format: str
    created_at: str
    files: Dict[str, str]
    counts: Dict[str, int]
    notes: List[str]


def convert_with_marker(
    pdf_path: Path,
    output_format: str,
    page_range: Optional[str],
    force_ocr: bool,
    strip_existing_ocr: bool,
    paginate_output: bool,
    disable_image_extraction: bool,
    use_llm: bool,
    redo_inline_math: bool,
    block_correction_prompt: Optional[str],
    config_json: Optional[Path],
    no_tables: bool,
    disable_multiprocessing: bool,
    provider_cfg: Optional[ProviderConfig],
) -> Tuple[str, Any, Any, List[str]]:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    from marker.config.parser import ConfigParser

    config: Dict[str, Any] = {}

    # 先加载 config_json（若有），再用 CLI 显式参数覆盖，避免 CLI 被意外覆盖
    if config_json is not None:
        extra = json.loads(config_json.read_text(encoding="utf-8"))
        if not isinstance(extra, dict):
            raise ValueError("config_json must be a JSON object (dict).")
        config.update(extra)

    config["output_format"] = output_format
    if page_range:
        config["page_range"] = page_range
    if force_ocr:
        config["force_ocr"] = True
    if strip_existing_ocr:
        config["strip_existing_ocr"] = True
    if paginate_output:
        config["paginate_output"] = True
    if disable_image_extraction:
        config["disable_image_extraction"] = True
    if use_llm:
        config["use_llm"] = True
    if redo_inline_math:
        config["redo_inline_math"] = True
    if block_correction_prompt:
        config["block_correction_prompt"] = block_correction_prompt
    if disable_multiprocessing:
        config["pdftext_workers"] = 1

    # ✅ 用 Marker 原生 OpenAIService 注入任何 OpenAI-compatible 后端
    if use_llm and provider_cfg is not None:
        config["llm_service"] = "marker.services.openai.OpenAIService"
        config["openai_base_url"] = provider_cfg.url
        config["openai_api_key"] = provider_cfg.api_key
        config["openai_model"] = provider_cfg.model

    notes: List[str] = []

    cp = ConfigParser(config)

    processors = cp.get_processors()
    if processors is not None and no_tables:
        filtered = []
        for proc in processors:
            name = f"{proc.__class__.__module__}.{proc.__class__.__name__}"
            if "table" in name.lower():
                continue
            filtered.append(proc)
        processors = filtered
        notes.append("no_tables_enabled")

    converter = PdfConverter(
        config=cp.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=processors,
        renderer=cp.get_renderer(),
        llm_service=cp.get_llm_service(),
    )

    rendered = converter(str(pdf_path))
    text, _, images = text_from_rendered(rendered)
    rendered_dump = pydantic_dump(rendered)
    # ✅ 关键：metadata 写入前必须 json-safe
    rendered_dump = json_safe(rendered_dump)

    return text, rendered_dump, images, notes


def process_one_pdf(args: argparse.Namespace, pdf_path: Path) -> None:
    out_dir = args.output_dir / pdf_path.stem
    safe_mkdir(out_dir)
    img_dir = out_dir / "images"
    safe_mkdir(img_dir)

    provider_cfg: Optional[ProviderConfig] = None
    llm_notes: List[str] = []
    if args.use_llm:
        provider_cfg = get_provider_config(
            args.provider,
            args.url,
            args.key,
            args.model,
            ollama_allow_cloud=bool(args.ollama_allow_cloud),
            apply_proxy_fix=(args.provider == "ollama" and not args.no_proxy_fix),
        )
        llm_notes.extend([
            f"llm_provider={provider_cfg.provider}",
            f"llm_url={provider_cfg.url}",
            f"llm_model={provider_cfg.model}",
        ])

    text, rendered_dump, images, conv_notes = convert_with_marker(
        pdf_path=pdf_path,
        output_format=args.output_format,
        page_range=args.page_range,
        force_ocr=args.force_ocr,
        strip_existing_ocr=args.strip_existing_ocr,
        paginate_output=args.paginate_output,
        disable_image_extraction=args.disable_image_extraction,
        use_llm=args.use_llm,
        redo_inline_math=args.redo_inline_math,
        block_correction_prompt=args.block_correction_prompt,
        config_json=args.config_json,
        no_tables=args.no_tables,
        disable_multiprocessing=args.disable_multiprocessing,
        provider_cfg=provider_cfg,
    )

    # 保存文档
    if args.output_format == "markdown":
        doc_path = out_dir / "document.md"
        doc_path.write_text(text, encoding="utf-8")
    elif args.output_format == "html":
        doc_path = out_dir / "document.html"
        doc_path.write_text(text, encoding="utf-8")
    elif args.output_format == "json":
        doc_path = out_dir / "document.json"
        try:
            save_json(doc_path, json.loads(text))
        except Exception:
            doc_path.write_text(text, encoding="utf-8")
    elif args.output_format == "chunks":
        doc_path = out_dir / "document.chunks.json"
        try:
            save_json(doc_path, json.loads(text))
        except Exception:
            doc_path.write_text(text, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported output_format={args.output_format}")

    # metadata
    meta_path = out_dir / "metadata.json"
    save_json(meta_path, rendered_dump)

    # images
    img_count, img_files = save_images(images, img_dir)

    # 修复 document.md 的图片相对路径：![](xxx.jpeg) -> ![](images/xxx.jpeg)
    if args.output_format == "markdown" and img_files:
        try:
            fixed = rewrite_markdown_image_paths(text, img_files, images_dir_name="images")
            if fixed != text:
                text = fixed
                doc_path.write_text(text, encoding="utf-8")
        except Exception as _e:
            # 不要因为重写失败导致整体失败；记录到 notes
            conv_notes.append(f"md_image_rewrite_failed:{type(_e).__name__}")

    # equations
    # 目标：在 equations.tex 中给每个公式加注释：编号 + 页码
    eq_items: List[Dict[str, Any]] = []

    # 优先从 rendered_dump 抽取（可拿到 page 信息）
    if args.eq_source in ("auto", "rendered"):
        eq_items = extract_equations_with_locations(rendered_dump)

    # fallback：从 markdown 抽取（通常拿不到 page）
    if not eq_items and args.eq_source in ("auto", "markdown") and args.output_format == "markdown":
        eqs_md = extract_equations_from_markdown(text)
        eq_items = [{"latex": e, "page": None, "block_type": "Equation"} for e in eqs_md]

    eq_path = out_dir / "equations.tex"
    if eq_items:
        # 若所有公式都无法提取页码，则不输出页码提示，避免满屏 p.?
        has_page_hint = any(isinstance(it.get("page"), int) for it in eq_items)

        parts: List[str] = ["% Extracted equations (with numbering)"]
        for i, it in enumerate(eq_items, start=1):
            if has_page_hint:
                page = it.get("page")
                page_str = f"p.{page}" if isinstance(page, int) else "p.?"
                parts.append(f"\n% Eq {i} | {page_str}")
            else:
                parts.append(f"\n% Eq {i}")
            parts.append("$$\n" + str(it.get("latex", "")).strip() + "\n$$")
        eq_path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
        eq_count = len(eq_items)
    else:
        eq_path.write_text("% No equations found by current heuristics.\n", encoding="utf-8")
        eq_count = 0

    # references
    ref_path = out_dir / "references.txt"
    refs = extract_references(text, mode=args.refs_mode) if args.output_format == "markdown" else ""
    refs = fix_reference_continuations(refs) if refs else refs
    if refs:
        ref_path.write_text(refs + "\n", encoding="utf-8")
        ref_count = count_reference_entries(refs)
    else:
        ref_path.write_text("No references section found by heuristic.\n", encoding="utf-8")
        ref_count = 0

    # references -> .bib
    bib_path = out_dir / "references.bib"
    if refs:
        bib = references_to_bibtex(refs)
        if bib:
            bib_path.write_text(bib + "\n", encoding="utf-8")
        else:
            bib_path.write_text("% No bib entries generated from references.\n", encoding="utf-8")
    else:
        bib_path.write_text("% No references section found by heuristic.\n", encoding="utf-8")

    manifest = ExtractManifest(
        input_pdf=str(pdf_path),
        output_dir=str(out_dir),
        output_format=args.output_format,
        created_at=now_iso(),
        files={
            "document": str(doc_path),
            "metadata": str(meta_path),
            "images_dir": str(img_dir),
            "equations_tex": str(eq_path),
            "references_txt": str(ref_path),
            "references_bib": str(bib_path),
        },
        counts={
            "images": img_count,
            "equations": eq_count,
            "references_lines": ref_count,
        },
        notes=(conv_notes + llm_notes),
    )
    save_json(out_dir / "manifest.json", asdict(manifest))

    print(f"[OK] {pdf_path.name} -> {out_dir} | images={img_count}, eqs={eq_count}, refs_lines={ref_count}")


# ============================================================
# CLI
# ============================================================

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="marker_extract_v14",
        description="Marker Extract v14: Add references to bib conversion.",
        formatter_class=ColorHelpFormatter,
    )
    p.add_argument("input", type=str, metavar="PDF_PATH", help="PDF file path (single PDF only).")
    p.add_argument("-o", "--output_dir", type=str, metavar="OUTPUT_DIR", default="marker_v14_out", help="Output root directory.")

    p.add_argument("--output_format", type=str, metavar="FORMAT", default="markdown", choices=["markdown", "json", "html", "chunks"])
    p.add_argument("--page_range", type=str, metavar="PAGE_RANGE", default=None, help='e.g. "0,5-10,20" (0-based).')
    p.add_argument("--force_ocr", action="store_true")
    p.add_argument("--strip_existing_ocr", action="store_true")
    p.add_argument("--paginate_output", action="store_true")
    p.add_argument("--disable_image_extraction", action="store_true")
    p.add_argument("--redo_inline_math", action="store_true")
    p.add_argument("--block_correction_prompt", type=str, metavar="PROMPT", default=None)
    p.add_argument("--config_json", type=str, metavar="CONFIG_JSON", default=None)
    p.add_argument("--no_tables", action="store_true")
    p.add_argument("--torch_device", type=str, metavar="TORCH_DEVICE", default=None)
    p.add_argument("--disable_multiprocessing", action="store_true", help="Disable multiprocessing in pdftext (set pdftext_workers=1).")

    p.add_argument("--refs_mode", type=str, metavar="REFS_MODE", default="balanced", choices=["strict", "balanced", "loose"])
    p.add_argument("--eq_source", type=str, metavar="EQ_SOURCE", default="auto", choices=["auto", "markdown", "rendered"])

    p.add_argument("--use_llm", action="store_true")
    p.add_argument("--provider", type=str, metavar="PROVIDER", default="openai", choices=list(PROVIDERS.keys()))
    p.add_argument("--url", type=str, metavar="URL", default=None)
    p.add_argument("--key", type=str, metavar="API_KEY", default=None)
    p.add_argument("--model", type=str, metavar="MODEL", default=None)
    p.add_argument("--ollama_allow_cloud", action="store_true", help="For provider=ollama: if model is not specified, allow selecting *:cloud remote models")
    p.add_argument("--no_proxy_fix", action="store_true", help="For provider=ollama: disable NO_PROXY fix (default: enabled)")
    p.add_argument("--list_chatanywhere_models", action="store_true", help="List ChatAnywhere models and exit.")

    return p

def main() -> int:
    args = build_argparser().parse_args()

    # 环境自检：避免“以为在 base311，实际还在 base”
    print(f"[ENV] python={sys.executable}")

    if args.list_chatanywhere_models:
        print("[ChatAnywhere] 可用模型列表：")
        for group, models in CHATANYWHERE_MODEL_GROUPS:
            print(f"  {group}:")
            for m in models:
                print(f"    - {m}")
        return 0

    if args.torch_device:
        os.environ["TORCH_DEVICE"] = args.torch_device

    # marker import check
    try:
        import marker  # noqa: F401
    except Exception as e:
        print(f"[ERROR] import marker failed: {repr(e)}", file=sys.stderr)
        print("        Fix: ensure you are running in the env where marker-pdf is installed, e.g.:", file=sys.stderr)
        print("        conda activate base311", file=sys.stderr)
        print("        pip install -U marker-pdf", file=sys.stderr)
        return 2

    args.output_dir = Path(args.output_dir).expanduser().resolve()
    safe_mkdir(args.output_dir)

    args.config_json = Path(args.config_json).expanduser().resolve() if args.config_json else None
    if args.config_json and not args.config_json.exists():
        print(f"[ERROR] config_json not found: {args.config_json}", file=sys.stderr)
        return 2

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"[ERROR] input not found: {input_path}", file=sys.stderr)
        return 2
    if input_path.is_dir():
        print(f"[ERROR] directory input is not supported. Please pass a single PDF file: {input_path}", file=sys.stderr)
        return 2

    pdfs = list(iter_pdfs(input_path))
    if not pdfs:
        print(f"[ERROR] no PDFs found under: {input_path}", file=sys.stderr)
        return 2

    print(f"[INFO] PDFs found: {len(pdfs)} | output_root={args.output_dir} | use_llm={args.use_llm}")

    for pdf in pdfs:
        try:
            process_one_pdf(args, pdf)
        except KeyboardInterrupt:
            print("\n[INTERRUPT] stopped by user", file=sys.stderr)
            return 130
        except Exception as e:
            err_dir = args.output_dir / pdf.stem
            safe_mkdir(err_dir)
            (err_dir / "ERROR.txt").write_text(repr(e), encoding="utf-8")
            print(f"[FAIL] {pdf.name}: {repr(e)} (see {err_dir / 'ERROR.txt'})", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
import sys
from pathlib import Path
from typing import Optional
import re
import shutil
import os
import subprocess
import tempfile
import textwrap
import time

# 测试（请保留这些注释，便于未来快速验证）：
# NO_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/compile.py -h
# NO_COLOR= FORCE_COLOR=1 python3 /Users/lingguiwang/Documents/Coding/LLM/12LaTex/scripts/compile.py -h

DEFAULT_ASSETS_DIR = Path.cwd()
DEFAULT_OUTPUT_DIR = Path.cwd() / "build_pdf"
DEFAULT_LOGS_DIR = Path.cwd() / "build_logs"

ENGINE_CANDIDATES = ["xelatex", "lualatex", "pdflatex"]
BIB_CANDIDATES = ["biber", "bibtex"]

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
        out: list[str] = []
        for p in parts:
            if p.startswith("-"):
                out.append(colorize(p, ANSI_CYAN_BOLD))
            elif p.isupper() or "_" in p:
                out.append(colorize(p, ANSI_YELLOW_BOLD))
            else:
                out.append(p)
        return " ".join(out)

MAIN_NAME_PATTERNS = re.compile(r"^(main|master|paper|manuscript)\.tex$", re.IGNORECASE)
XE_FEATURE_PATTERNS = re.compile(
    r"\\usepackage\s*(\[[^\]]*\])?\s*\{(fontspec|xeCJK|ctex)\}|\\(fontspec|xeCJK|ctex)",
    re.IGNORECASE,
)
def _has_fontspec_commands(tex_text: str) -> bool:
    lowered = tex_text.lower()
    return (
        "\\setmainfont" in lowered
        or "\\setsansfont" in lowered
        or "\\setmonofont" in lowered
    )

def requires_unicode_engine(tex_text: str) -> bool:
    return bool(
        XE_FEATURE_PATTERNS.search(tex_text)
        or CTEX_CLASS_PATTERNS.search(tex_text)
        or CTEX_PKG_PATTERNS.search(tex_text)
        or _has_fontspec_commands(tex_text)
    )
BIBLATEX_PATTERNS = re.compile(
    r"\\usepackage\s*(\[[^\]]*\])?\s*\{biblatex\}|\\addbibresource",
    re.IGNORECASE,
)
BIBER_BACKEND_PATTERNS = re.compile(r"backend\s*=\s*biber", re.IGNORECASE)
BIBTEX_PATTERNS = re.compile(
    r"\\bibliography\s*\{|\\usepackage\s*(\[[^\]]*\])?\s*\{natbib\}",
    re.IGNORECASE,
)
CITE_PATTERNS = re.compile(r"\\cite\w*\s*\{", re.IGNORECASE)
CTEX_CLASS_PATTERNS = re.compile(
    r"\\documentclass\s*(\[[^\]]*\])?\s*\{[^}]*ctex[^}]*\}",
    re.IGNORECASE,
)
CTEX_PKG_PATTERNS = re.compile(
    r"\\usepackage\s*(\[[^\]]*\])?\s*\{(ctex|CJK|CJKutf8)\}",
    re.IGNORECASE,
)
RERUN_PATTERNS = re.compile(
    r"Rerun to get (cross-references|citations|outlines) right|"
    r"rerunfilecheck|"
    r"Please \(re\)run (LaTeX|Biber)",
    re.IGNORECASE,
)
FATAL_LATEX_PATTERNS = re.compile(
    r"Fatal error occurred|Emergency stop|Undefined control sequence|TeX capacity exceeded|! LaTeX Error",
    re.IGNORECASE,
)
FONT_CJK_WARN_PATTERNS = re.compile(
    r'Font "([^"]+)" does not contain requested Script\s*"CJK"',
    re.IGNORECASE,
)
NULLFONT_MISSING_PATTERNS = re.compile(
    r"Missing character: There is no .* in font nullfont!",
    re.IGNORECASE,
)
UNDEFINED_REF_PATTERNS = re.compile(
    r"LaTeX Warning: Citation `[^']+' on page .* undefined on input line .*|"
    r"LaTeX Warning: There were undefined references",
    re.IGNORECASE,
)
NO_BBL_PATTERNS = re.compile(r"No file .*\.bbl\.", re.IGNORECASE)

CLEAN_EXTENSIONS = [
    ".aux", ".log", ".out", ".toc", ".bbl", ".blg", ".bcf", ".run.xml",
    ".fdb_latexmk", ".fls", ".synctex.gz", ".nav", ".snm", ".lof", ".lot",
    ".idx", ".ilg", ".ind", ".dvi",
]


@dataclass
class Config:
    assets_dir: Path
    output_dir: Path
    logs_dir: Path
    engine: str
    bib: str
    build_mode: str
    keep_intermediates: bool
    keep_tmpdir: bool
    clean_on_fail: bool
    max_runs: int
    recursive: bool
    tmpdir: Optional[Path] = None
@dataclass
class Target:
    id: str
    kind: str  # "file" or "dir"
    path: Path


@dataclass
class MainTexResult:
    ok: bool
    path: Optional[Path] = None
    candidates: Optional[list[Path]] = None
    reason: Optional[str] = None

@dataclass
class EnginePlan:
    engine: Optional[str]
    attempts: list[str]
    reason: Optional[str] = None


@dataclass
class BibPlan:
    tool: Optional[str]
    attempts: list[str]
    reason: Optional[str] = None


@dataclass
class CmdResult:
    ok: bool
    returncode: int
    output: str


@dataclass
class Result:
    target: Target
    ok: bool
    main_tex: Optional[Path]
    engine: Optional[str]
    bib_tool: Optional[str]
    pdf_path: Optional[Path]
    log_dir: Path
    elapsed_sec: float
    error: Optional[str] = None
    warning: Optional[str] = None

def parse_bool(value: str) -> bool:
    v = value.strip().lower()
    if v in {"true", "1", "yes", "y"}:
        return True
    if v in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def require_absolute_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def build_config(args: argparse.Namespace) -> Config:
    if args.output:
        output_root = args.output
        output_dir = output_root / "build_pdf"
        logs_dir = output_root / "build_logs"
    else:
        output_dir = DEFAULT_OUTPUT_DIR
        logs_dir = DEFAULT_LOGS_DIR
    return Config(
        assets_dir=DEFAULT_ASSETS_DIR,
        output_dir=output_dir,
        logs_dir=logs_dir,
        tmpdir=args.tmpdir,
        engine=args.engine,
        bib=args.bib,
        build_mode=args.build_mode,
        keep_intermediates=args.keep_intermediates,
        clean_on_fail=args.clean_on_fail,
        max_runs=args.max_runs,
        recursive=args.recursive,
        keep_tmpdir=args.keep_tmpdir,
    )

def which_or_none(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def detect_tools() -> dict:
    tools = {}
    for cmd in ENGINE_CANDIDATES + BIB_CANDIDATES:
        tools[cmd] = which_or_none(cmd)
    return tools


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gbk", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def target_id(path: Path, base: Path, kind: str) -> str:
    rel = path.relative_to(base).as_posix()
    safe = rel.replace("/", "__")
    return f"{kind}__{safe}"


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def scan_targets(assets_dir: Path, recursive: bool, exclude_dirs: Optional[list[Path]] = None) -> list[Target]:
    targets: list[Target] = []
    if not assets_dir.exists():
        return targets
    exclude_dirs = exclude_dirs or []

    for tex_file in assets_dir.glob("*.tex"):
        if not tex_file.is_file():
            continue
        tid = target_id(tex_file, assets_dir, "file")
        targets.append(Target(id=tid, kind="file", path=tex_file))

    if recursive:
        dir_iter = (p for p in assets_dir.rglob("*") if p.is_dir() and p != assets_dir)
    else:
        dir_iter = (p for p in assets_dir.iterdir() if p.is_dir())

    for dir_path in dir_iter:
        if any(_is_under(dir_path, ex) for ex in exclude_dirs):
            continue
        if any(dir_path.glob("*.tex")):
            candidates = list_main_tex_candidates(dir_path)
            if len(candidates) > 1 and all(includes == 0 for _, includes in candidates):
                for tex_path, _ in candidates:
                    tid = target_id(tex_path, assets_dir, "file")
                    targets.append(Target(id=tid, kind="file", path=tex_path))
                continue
            tid = target_id(dir_path, assets_dir, "dir")
            targets.append(Target(id=tid, kind="dir", path=dir_path))

    return targets


def list_main_tex_candidates(project_dir: Path) -> list[tuple[Path, int]]:
    tex_files = list(project_dir.glob("*.tex"))
    candidates: list[tuple[Path, int]] = []
    for tex_path in tex_files:
        if not tex_path.is_file():
            continue
        content = read_text(tex_path)
        has_doc = ("\\documentclass" in content) and ("\\begin{document}" in content)
        if not has_doc:
            continue
        includes = len(re.findall(r"\\(input|include)\s*\{", content))
        candidates.append((tex_path, includes))
    return candidates


def find_main_tex(project_dir: Path) -> MainTexResult:
    tex_files = list(project_dir.glob("*.tex"))
    if not tex_files:
        return MainTexResult(ok=False, reason="No .tex files found in directory")

    scored = []
    for tex_path in tex_files:
        content = read_text(tex_path)
        has_doc = ("\\documentclass" in content) and ("\\begin{document}" in content)
        name_match = bool(MAIN_NAME_PATTERNS.match(tex_path.name))
        includes = len(re.findall(r"\\(input|include)\s*\{", content))
        scored.append((tex_path, has_doc, name_match, includes))

    candidates = [s for s in scored if s[1]] or scored

    if len(candidates) > 1:
        name_filtered = [s for s in candidates if s[2]]
        if name_filtered:
            candidates = name_filtered

    if len(candidates) > 1:
        max_includes = max(s[3] for s in candidates)
        candidates = [s for s in candidates if s[3] == max_includes]

    if len(candidates) == 1:
        return MainTexResult(ok=True, path=candidates[0][0])

    return MainTexResult(
        ok=False,
        candidates=[s[0] for s in candidates],
        reason="Ambiguous main .tex file",
    )


def detect_engine(tex_text: str, tools: dict, preferred: str) -> EnginePlan:
    if preferred != "auto":
        if tools.get(preferred):
            return EnginePlan(engine=preferred, attempts=[preferred])
        return EnginePlan(engine=None, attempts=[preferred], reason=f"{preferred} not available")

    has_xe = requires_unicode_engine(tex_text)
    if has_xe:
        order = ["xelatex", "lualatex", "pdflatex"]
    else:
        order = ["pdflatex", "xelatex", "lualatex"]

    attempts = list(order)
    for engine in order:
        if tools.get(engine):
            return EnginePlan(engine=engine, attempts=attempts)

    return EnginePlan(engine=None, attempts=attempts, reason="No LaTeX engine available")


def detect_bib(tex_text: str, tools: dict, preferred: str, project_dir: Path) -> BibPlan:
    if preferred == "none":
        return BibPlan(tool=None, attempts=[])

    if preferred != "auto":
        if tools.get(preferred):
            return BibPlan(tool=preferred, attempts=[preferred])
        return BibPlan(tool=None, attempts=[preferred], reason=f"{preferred} not available")

    has_biblatex = bool(BIBLATEX_PATTERNS.search(tex_text) or BIBER_BACKEND_PATTERNS.search(tex_text))
    has_bibtex = bool(BIBTEX_PATTERNS.search(tex_text))
    has_cite = bool(CITE_PATTERNS.search(tex_text))
    has_bib_files = has_referenced_bib_files(tex_text, project_dir)

    needs_bib = has_biblatex or (has_bibtex and has_bib_files) or (has_bib_files and has_cite)
    if not needs_bib:
        return BibPlan(tool=None, attempts=[])

    if has_biblatex:
        order = ["biber", "bibtex"]
    else:
        order = ["bibtex", "biber"]

    attempts = []
    for tool in order:
        attempts.append(tool)
        if tools.get(tool):
            return BibPlan(tool=tool, attempts=attempts)

    return BibPlan(tool=None, attempts=attempts, reason="No bibliography tool available")


def has_cross_dir_refs(tex_text: str) -> bool:
    return "../" in tex_text or "..\\" in tex_text


def _extract_bib_entries(tex_text: str, pattern: str) -> list[str]:
    entries: list[str] = []
    for raw in re.findall(pattern, tex_text, flags=re.IGNORECASE):
        value = raw[-1] if isinstance(raw, tuple) else raw
        for part in value.split(","):
            name = part.strip().strip("\"'{}")
            if name:
                entries.append(name)
    return entries


def _normalize_bib_name(name: str) -> str:
    if name.lower().endswith(".bib"):
        return name
    return f"{name}.bib"


def has_referenced_bib_files(tex_text: str, project_dir: Path) -> bool:
    bib_entries = _extract_bib_entries(tex_text, r"\\bibliography\s*\{([^}]*)\}")
    bib_entries += _extract_bib_entries(tex_text, r"\\addbibresource\s*(\[[^\]]*\])?\s*\{([^}]*)\}")
    if not bib_entries:
        return False
    for entry in bib_entries:
        name = _normalize_bib_name(entry)
        entry_path = Path(name)
        if not entry_path.is_absolute():
            entry_path = (project_dir / entry_path).resolve()
        if entry_path.exists():
            return True
    return False


def collect_project_texts(main_tex: Path, project_dir: Path) -> str:
    parts = [read_text(main_tex)]
    for cls_path in project_dir.glob("*.cls"):
        parts.append(read_text(cls_path))
    for sty_path in project_dir.glob("*.sty"):
        parts.append(read_text(sty_path))
    return "\n".join(parts)



def _is_writable_dir(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True)
        test = p / ".write_test"
        test.write_text("ok", encoding="utf-8")
        test.unlink(missing_ok=True)
        return True
    except Exception:
        return False


def _pick_tmp_base(cfg: "Config", src_dir: Path, target_hash: str) -> Path:
    """Pick a writable temp base directory for this build.

    Priority:
    1) --tmpdir (cfg.tmpdir) if provided
    2) <output_root>/.tmp_latex (output_root is cfg.logs_dir.parent)
    3) <src_dir>/.tmp_latex (fallback)
    """
    candidates: list[Path] = []
    if getattr(cfg, "tmpdir", None):
        candidates.append(Path(cfg.tmpdir))  # type: ignore[arg-type]
    candidates.append((cfg.logs_dir.parent / ".tmp_latex").resolve())
    candidates.append((src_dir / ".tmp_latex").resolve())

    for base in candidates:
        if _is_writable_dir(base):
            # per-target subdir to avoid collisions
            per = (base / f"job_{target_hash}").resolve()
            per.mkdir(parents=True, exist_ok=True)
            return per

    # As a last resort, try the current working directory
    per = (Path.cwd() / ".tmp_latex" / f"job_{target_hash}").resolve()
    per.mkdir(parents=True, exist_ok=True)
    return per



def _maybe_delete_tmpdir(cfg: "Config") -> None:
    """Delete temp directory after build (default behavior).

    Use --keep-tmpdir to preserve temp files for debugging.
    """
    if getattr(cfg, "keep_tmpdir", False):
        return

    # Prefer user-specified --tmpdir; otherwise delete the auto temp base under output root.
    base = Path(cfg.tmpdir).resolve() if getattr(cfg, "tmpdir", None) else (cfg.logs_dir.parent / ".tmp_latex").resolve()
    try:
        base_str = str(base)
        if base_str in ("/", str(Path.home().resolve())):
            return
        if not base.exists() or not base.is_dir():
            return
        if not (base.name.startswith(".tmp") or base.name.startswith("latex_build_")):
            return
        shutil.rmtree(base, ignore_errors=True)
    except Exception:
        # Do not fail the build result because of temp cleanup
        return

def _ensure_tmp_env(env: dict[str, str], tmp_base: Path) -> dict[str, str]:
    """Force subprocesses (xelatex/gs/etc.) to use a writable temp directory."""
    # Many tools read TMPDIR on macOS; some read TMP/TEMP.
    env = dict(env)
    env["TMPDIR"] = str(tmp_base)
    env["TMP"] = str(tmp_base)
    env["TEMP"] = str(tmp_base)
    return env


def _should_delete_tmpdir(p: Path) -> bool:
    """
    Safety guard: only delete tmp directories that look like LaTeX temp dirs.
    This avoids accidental deletion if a wrong path is passed.
    """
    try:
        p = p.resolve()
    except Exception:
        return False
    name = p.name
    if name.startswith(".tmp") or name.startswith("latex_build_"):
        return True
    return False

def _delete_tmpdir(p: Path) -> None:
    if not p:
        return
    try:
        p = p.resolve()
    except Exception:
        return
    # Never delete root or home
    if str(p) in ("/", str(Path.home())):
        return
    if not p.exists() or not p.is_dir():
        return
    if not _should_delete_tmpdir(p):
        return
    _delete_tmpdir(p)

def run_cmd(cmd: list[str], cwd: Path, log_path: Path, append: bool = True, env: Optional[dict[str, str]] = None) -> CmdResult:
    header = f"\n$ {' '.join(cmd)}\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with log_path.open(mode, encoding="utf-8") as f:
        f.write(header)

    if env is None:
        env = os.environ.copy()

    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(proc.stdout)

    return CmdResult(ok=proc.returncode == 0, returncode=proc.returncode, output=proc.stdout)


def needs_rerun(output: str) -> bool:
    return bool(RERUN_PATTERNS.search(output))


def is_soft_latex_failure(output: str) -> bool:
    if "Output written on" not in output:
        return False
    return not FATAL_LATEX_PATTERNS.search(output)


def tail_log(path: Path, lines: int = 30) -> str:
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(content[-lines:])


def error_hints(text: str) -> list[str]:
    hints = []
    lower = text.lower()
    if "biber" in lower and "not found" in lower:
        hints.append("缺少 biber，可安装后重试")
    if "bibtex" in lower and "not found" in lower:
        hints.append("缺少 bibtex，可安装后重试")
    if "file" in lower and "not found" in lower and ".sty" in lower:
        hints.append("缺少 LaTeX 宏包（.sty），请检查 TeX 发行版")
    if "! i can't find file" in lower:
        hints.append("缺少引用文件或图片，请检查相对路径")
    if "missing $ inserted" in lower:
        hints.append("可能存在数学模式错误（缺少 $）")
    if "fontspec error" in lower and "cannot be found" in lower:
        hints.append("缺少系统字体，请安装字体或在 ctex 中指定可用字体集")
    if FONT_CJK_WARN_PATTERNS.search(text):
        hints.append("检测到字体不支持 CJK 字形，建议改用支持中文的字体或设置 ctex 字体集")
    if NULLFONT_MISSING_PATTERNS.search(text):
        hints.append("出现 nullfont 缺字，常见于中文字体未正确加载，请检查字体配置")
    return hints


def extract_warnings(text: str) -> list[str]:
    warnings: list[str] = []
    fonts = sorted({m.group(1) for m in FONT_CJK_WARN_PATTERNS.finditer(text)})
    if fonts:
        warnings.append(f"字体缺少 CJK 字形: {', '.join(fonts)}")
    if NULLFONT_MISSING_PATTERNS.search(text):
        warnings.append("出现 nullfont 缺字，可能是中文字体未正确加载")
    if UNDEFINED_REF_PATTERNS.search(text):
        warnings.append("存在未解析引用，请检查 .bib 或引用键")
    if NO_BBL_PATTERNS.search(text):
        warnings.append("未生成 .bbl，可能未正确运行 biber/bibtex")
    return warnings


def merge_warning(existing: Optional[str], extras: list[str]) -> Optional[str]:
    if not extras:
        return existing
    uniq = []
    if existing:
        uniq.append(existing)
    for item in extras:
        if item and item not in uniq:
            uniq.append(item)
    return "；".join(uniq)


def copy_project(src_dir: Path, temp_root: Path) -> Path:
    """Copy a LaTeX project directory into a temporary build root.

    Important: when temp_root lives *inside* src_dir (e.g. tmpdir under the project),
    we must ignore the temp directory itself to avoid recursive self-copying which
    can explode path lengths (File name too long).
    """
    dest = temp_root / src_dir.name
    if dest.exists():
        shutil.rmtree(dest)

    # Compute the top-level directory name that contains temp_root, if temp_root is inside src_dir.
    temp_top = None
    try:
        rel = temp_root.relative_to(src_dir)
        if rel.parts:
            temp_top = rel.parts[0]
    except ValueError:
        temp_top = None

    def _ignore(_src: str, names: list[str]) -> set[str]:
        ignore = {".git", "__pycache__", ".DS_Store"}
        # Always ignore our own temp directories
        ignore.update({".tmp_latex", ".tmp"})
        if temp_top:
            ignore.add(temp_top)
        return ignore.intersection(names)

    shutil.copytree(src_dir, dest, ignore=_ignore)
    return dest


def cleanup_inplace(jobname: str, work_dir: Path) -> None:
    for ext in CLEAN_EXTENSIONS:
        target = work_dir / f"{jobname}{ext}"
        if target.exists():
            try:
                target.unlink()
            except OSError:
                pass


def compile_chain(
    engine: str,
    bib_tool: Optional[str],
    main_tex: Path,
    work_dir: Path,
    log_path: Path,
    max_runs: int,
    env: Optional[dict[str, str]] = None,
) -> tuple[bool, str, list[str], str]:
    jobname = main_tex.stem
    output = ""

    def run_engine(append: bool = True) -> CmdResult:
        return run_cmd(
            [
                engine,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                main_tex.name,
            ],
            cwd=work_dir,
            log_path=log_path,
            append=append,
            env=env,
        )

    last_cmd = [engine, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", main_tex.name]
    last_output = ""
    last_cmd[0] = engine

    if not bib_tool:
        runs = 0
        while runs < max_runs:
            runs += 1
            result = run_engine(append=(runs != 1))
            last_cmd[0] = engine
            output += result.output
            last_output = result.output
            if not result.ok and not is_soft_latex_failure(result.output):
                return False, output, last_cmd, last_output
            if not needs_rerun(result.output):
                break
        return True, output, last_cmd, last_output

    result = run_engine(append=False)
    last_cmd[0] = engine
    output += result.output
    last_output = result.output
    if not result.ok and not is_soft_latex_failure(result.output):
        return False, output, last_cmd, last_output

    bib_result = run_cmd([bib_tool, jobname], cwd=work_dir, log_path=log_path, append=True, env=env)
    output += bib_result.output
    last_cmd = [bib_tool, jobname]
    if not bib_result.ok:
        return False, output, last_cmd, last_output

    post_runs = 0
    post_limit = max(2, max_runs)
    while post_runs < post_limit:
        post_runs += 1
        result = run_engine(append=True)
        last_cmd = [engine, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", main_tex.name]
        output += result.output
        last_output = result.output
        if not result.ok:
            return False, output, last_cmd, last_output
        if post_runs >= 2 and not needs_rerun(result.output):
            break

    return True, output, last_cmd, last_output


def compile_target(target: Target, cfg: Config, tools: dict) -> Result:
    start = time.time()
    target_hash = hashlib.sha1(target.id.encode("utf-8")).hexdigest()[:10]
    log_dir = cfg.logs_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = None
    ok_flag: Optional[bool] = None

    if target.kind == "file":
        main_tex = target.path
        src_dir = target.path.parent
    else:
        src_dir = target.path
        main_result = find_main_tex(src_dir)
        if not main_result.ok:
            reason = main_result.reason or "Failed to detect main TeX"
            candidates = main_result.candidates or []
            if candidates:
                reason += " | candidates: " + ", ".join(str(p) for p in candidates)
            return Result(
                target=target,
                ok=False,
                main_tex=None,
                engine=None,
                bib_tool=None,
                pdf_path=None,
                log_dir=log_dir,
                elapsed_sec=time.time() - start,
                error=reason,
            )
        main_tex = main_result.path

    log_path = log_dir / f"{main_tex.stem}__{target_hash}.log"

    tex_text = collect_project_texts(main_tex, src_dir)
    engine_plan = detect_engine(tex_text, tools, cfg.engine)
    if not engine_plan.engine:
        return Result(
            target=target,
            ok=False,
            main_tex=main_tex,
            engine=None,
            bib_tool=None,
            pdf_path=None,
            log_dir=log_dir,
            elapsed_sec=time.time() - start,
            error=engine_plan.reason or "No engine selected",
        )

    warning = None
    has_bibtex = bool(BIBTEX_PATTERNS.search(tex_text))
    has_bib_files = has_referenced_bib_files(tex_text, src_dir)
    if cfg.bib == "auto" and has_bibtex and not has_bib_files:
        warning = "检测到 \\bibliography 但未找到引用的 .bib，已跳过 bibtex"
        bib_plan = BibPlan(tool=None, attempts=[])
    else:
        bib_plan = detect_bib(tex_text, tools, cfg.bib, src_dir)
        if cfg.bib != "none" and bib_plan.tool is None and bib_plan.reason:
            return Result(
                target=target,
                ok=False,
                main_tex=main_tex,
                engine=engine_plan.engine,
                bib_tool=None,
                pdf_path=None,
                log_dir=log_dir,
                elapsed_sec=time.time() - start,
                error=bib_plan.reason,
            )

    temp_root = None
    tmp_base = _pick_tmp_base(cfg, src_dir, target_hash)
    base_env = _ensure_tmp_env(os.environ.copy(), tmp_base)

    work_dir = src_dir
    temp_project_dir = None
    try:
        if cfg.build_mode == "isolated":
            temp_root = Path(tempfile.mkdtemp(prefix="latex_build_", dir=str(tmp_base)))
            temp_project_dir = copy_project(src_dir, temp_root)
            work_dir = temp_project_dir
            main_tex = temp_project_dir / main_tex.relative_to(src_dir)

        ok = False
        output = ""
        used_engine = None
        attempts = list(engine_plan.attempts)
        if cfg.engine == "auto" and requires_unicode_engine(tex_text):
            attempts = [e for e in attempts if e in ("xelatex", "lualatex")]
        if engine_plan.engine and engine_plan.engine in attempts:
            attempts = [engine_plan.engine] + [e for e in attempts if e != engine_plan.engine]
        for engine in attempts:
            if not tools.get(engine):
                continue
            ok, output, last_cmd, last_output = compile_chain(
                engine,
                bib_plan.tool,
                main_tex,
                work_dir,
                log_path,
                cfg.max_runs,
                env=base_env,
            )
            used_engine = engine
            if ok or cfg.engine != "auto":
                break
        if ok and last_cmd and last_cmd[0] != used_engine:
            used_engine = last_cmd[0]
        ok_flag = ok
        pdf_src_name = main_tex.stem + ".pdf"
        pdf_src = work_dir / pdf_src_name
        pdf_dest = cfg.output_dir / f"{main_tex.stem}__{target_hash}.pdf"

        if ok and bib_plan.tool:
            bbl_path = work_dir / f"{main_tex.stem}.bbl"
            if not bbl_path.exists():
                extra = "未检测到生成的 .bbl（最终仍缺失）"
                warning = f"{warning}；{extra}" if warning else extra

        if ok and pdf_src.exists():
            pdf_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf_src, pdf_dest)
        elif ok:
            ok = False
            output += "\nPDF not found after compilation."

        if ok and cfg.build_mode == "inplace" and not cfg.keep_intermediates:
            cleanup_inplace(main_tex.stem, work_dir)

        if cfg.build_mode == "isolated":
            if ok and not cfg.keep_intermediates:
                _delete_tmpdir(temp_root)
            elif not ok and cfg.clean_on_fail:
                _delete_tmpdir(temp_root)

        elapsed = time.time() - start
        warnings_from_log = extract_warnings(output)
        warning = merge_warning(warning, warnings_from_log)
        error_tail = tail_log(log_path)
        if ok and last_output:
            error_tail = last_output
        if not ok and has_cross_dir_refs(tex_text) and cfg.build_mode == "isolated":
            extra = "可能存在跨目录相对路径(../)，隔离构建下请确保依赖在工程目录内"
            if error_tail:
                error_tail = error_tail + "\n" + extra
            else:
                error_tail = extra
        return Result(
            target=target,
            ok=ok,
            main_tex=main_tex,
            engine=used_engine,
            bib_tool=bib_plan.tool,
            pdf_path=pdf_dest if ok else None,
            log_dir=log_dir,
            elapsed_sec=elapsed,
            error=None if ok else error_tail,
            warning=warning,
        )
    finally:
        if cfg.build_mode == "isolated" and temp_root and (ok_flag is None or ok_flag is False):
            if cfg.clean_on_fail:
                _delete_tmpdir(temp_root)


def summarize_results(results: list[Result]) -> int:
    successes = [r for r in results if r.ok]
    failures = [r for r in results if not r.ok]

    print("\n=== 编译汇总 ===")
    print(f"成功: {len(successes)} | 失败: {len(failures)}")

    for r in successes:
        print(
            f"[OK] {r.target.id} | engine={r.engine} | bib={r.bib_tool or 'none'} | "
            f"pdf={r.pdf_path} | {r.elapsed_sec:.1f}s"
        )
        if r.warning:
            print(f"    提示: {r.warning}")

    for r in failures:
        print(
            f"[FAIL] {r.target.id} | engine={r.engine} | bib={r.bib_tool or 'none'} | "
            f"logs={r.log_dir} | {r.elapsed_sec:.1f}s"
        )
        if r.error:
            tail = r.error.strip()
            if tail:
                print("--- log tail ---")
                print(textwrap.indent(tail, "    "))
                print("---------------")
                for hint in error_hints(tail):
                    print(f"    提示: {hint}")
    return 1 if failures else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LaTeX 一键编译脚本",
        formatter_class=ColorHelpFormatter,
    )
    parser.add_argument("--path", type=require_absolute_path, metavar="PATH", help="编译指定 .tex 或目录（绝对路径）")
    parser.add_argument("--output", type=require_absolute_path, metavar="OUTPUT_DIR", help="输出根目录（绝对路径）")
    parser.add_argument("--tmpdir", type=require_absolute_path, metavar="TMPDIR", default=None, help="临时目录（绝对路径，可写；用于 Ghostscript 等外部工具）")
    parser.add_argument(
        "--keep-tmpdir",
        action="store_true",
        help="保留临时目录（调试用）。默认：编译结束后自动删除临时目录。",
    )
    parser.add_argument("--engine", default="auto", metavar="ENGINE", choices=["auto", "pdflatex", "xelatex", "lualatex"])
    parser.add_argument("--bib", default="auto", metavar="BIB", choices=["auto", "bibtex", "biber", "none"])
    parser.add_argument("--build-mode", default="isolated", metavar="BUILD_MODE", choices=["isolated", "inplace"])
    parser.add_argument("--keep-intermediates", type=parse_bool, metavar="KEEP_INTERMEDIATES", default=False)
    parser.add_argument("--clean-on-fail", type=parse_bool, metavar="CLEAN_ON_FAIL", default=False)
    parser.add_argument("--max-runs", type=int, metavar="MAX_RUNS", default=3)
    parser.add_argument("--recursive", type=parse_bool, metavar="RECURSIVE", default=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = build_config(args)
    if args.path and not args.path.exists():
        print(f"路径不存在: {args.path}")
        return 2

    tools = detect_tools()

    if args.path:
        path = args.path
        if path.is_file():
            tid = target_id(path, path.parent, "file")
            targets = [Target(id=tid, kind="file", path=path)]
        else:
            candidates = list_main_tex_candidates(path)
            if len(candidates) == 1:
                tid = target_id(path, path.parent, "dir")
                targets = [Target(id=tid, kind="dir", path=path)]
            else:
                exclude_dirs = [cfg.output_dir, cfg.logs_dir]
                targets = scan_targets(path, cfg.recursive, exclude_dirs=exclude_dirs)
    else:
        exclude_dirs = [cfg.output_dir, cfg.logs_dir]
        targets = scan_targets(cfg.assets_dir, cfg.recursive, exclude_dirs=exclude_dirs)

    if not targets:
        print("未发现可编译目标")
        return 0

    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    cfg.logs_dir.mkdir(parents=True, exist_ok=True)

    results: list[Result] = []
    for target in targets:
        result = compile_target(target, cfg, tools)
        results.append(result)

    code = summarize_results(results)
    _maybe_delete_tmpdir(cfg)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

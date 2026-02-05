#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ABS-Journal path utilities (portable across machines).

Goals:
- Avoid hard-coded absolute paths in code/docs.
- Support both "dev repo" and "~/.agents/skills/abs-journal" installation.
- Prefer absolute paths at runtime (for robustness), but derive them dynamically.

Environment variables (optional):
- ABS_JOURNAL_HOME: override skill root (directory that contains SKILL.md, assets/, scripts/)
- ABS_JOURNAL_DATA_DIR: override data directory (default: <root>/assets/data)
- ABS_JOURNAL_CACHE_DIR: override cache directory (default: <root>/.cache)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def _env_path(name: str) -> Optional[Path]:
    v = os.environ.get(name, "").strip()
    if not v:
        return None
    return Path(os.path.expanduser(v)).resolve()


def skill_root() -> Path:
    """Return the ABS-Journal root directory.

    Resolution order:
    1) ABS_JOURNAL_HOME env var
    2) Walk up from this file until a directory containing "SKILL.md" is found
    """
    override = _env_path("ABS_JOURNAL_HOME")
    if override is not None:
        return override

    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "SKILL.md").is_file():
            return p

    # Fallback: scripts/.. (keeps behavior similar to prior code)
    return here.parent.parent.resolve()


def data_dir() -> Path:
    override = _env_path("ABS_JOURNAL_DATA_DIR")
    if override is not None:
        return override
    return (skill_root() / "assets" / "data").resolve()


def cache_dir() -> Path:
    override = _env_path("ABS_JOURNAL_CACHE_DIR")
    if override is not None:
        return override
    return (skill_root() / ".cache").resolve()


def ajg_csv_default(year: str = "2024") -> Path:
    return (data_dir() / f"ajg_{year}_journals_core_custom.csv").resolve()


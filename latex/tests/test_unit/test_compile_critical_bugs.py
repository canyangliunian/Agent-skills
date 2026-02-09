#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Test cases for compile.py - Critical Bug Detection (TDD RED Stage)

This module contains tests designed to FAIL and expose Critical bugs in compile.py:
- Bug 1: NameError in requires_unicode_engine() (compile.py:89-90)
- Bug 2: RecursionError in _delete_tmpdir() (compile.py:559)

These tests follow TDD principles:
- RED: Tests should fail, demonstrating the bugs exist
- GREEN: After bug fixes, tests should pass
- REFACTOR: Improve code quality while keeping tests green
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import pytest


class TestRequiresUnicodeEngine:
    """Tests for requires_unicode_engine() function - Critical Bug #1"""

    def test_detects_ctex_class(self):
        """Test detection of ctex document class.

        This test should FAIL with NameError because CTEX_CLASS_PATTERNS
        is used before it's defined in compile.py:89-90.

        Expected failure: NameError: name 'CTEX_CLASS_PATTERNS' is not defined
        """
        from compile import requires_unicode_engine

        tex_content = r"\documentclass{ctexart}"

        # This should raise NameError due to variable definition order bug
        result = requires_unicode_engine(tex_content)

        # If we reach here after fix, the function should return True
        assert result is True, "ctexart document class should require unicode engine"

    def test_detects_ctex_package(self):
        """Test detection of ctex package.

        This test should FAIL with NameError because CTEX_PKG_PATTERNS
        is used before it's defined in compile.py:89-90.

        Expected failure: NameError: name 'CTEX_PKG_PATTERNS' is not defined
        """
        from compile import requires_unicode_engine

        tex_content = r"""
\documentclass{article}
\usepackage{ctex}
\begin{document}
内容
\end{document}
"""

        # This should raise NameError due to variable definition order bug
        result = requires_unicode_engine(tex_content)

        # If we reach here after fix, the function should return True
        assert result is True, "ctex package should require unicode engine"

    def test_detects_xecjk_package(self):
        """Test detection of xeCJK package.

        This should work because XE_FEATURE_PATTERNS is defined before use.
        """
        from compile import requires_unicode_engine

        tex_content = r"""
\documentclass{article}
\usepackage{xeCJK}
\begin{document}
内容
\end{document}
"""

        result = requires_unicode_engine(tex_content)
        assert result is True, "xeCJK package should require unicode engine"

    def test_rejects_plain_latex(self):
        """Test that plain LaTeX without unicode features returns False."""
        from compile import requires_unicode_engine

        tex_content = r"""
\documentclass{article}
\begin{document}
Hello World
\end{document}
"""

        result = requires_unicode_engine(tex_content)
        assert result is False, "plain LaTeX should not require unicode engine"


class TestDeleteTmpdir:
    """Tests for _delete_tmpdir() function - Critical Bug #2"""

    def test_no_infinite_recursion(self):
        """Test that _delete_tmpdir doesn't cause infinite recursion.

        This test should FAIL with RecursionError because _delete_tmpdir()
        recursively calls itself at compile.py:559 instead of calling
        shutil.rmtree().

        Expected failure: RecursionError: maximum recursion depth exceeded
        """
        import shutil
        import tempfile
        from compile import _delete_tmpdir

        # Create a temporary directory that matches the deletion pattern
        with tempfile.TemporaryDirectory(prefix=".tmp_test_latex_") as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Add a test file inside
            test_file = tmpdir_path / "test.txt"
            test_file.write_text("test content")

            # Verify directory exists
            assert tmpdir_path.exists(), "Test directory should exist before deletion"

            # This should raise RecursionError due to infinite self-call
            _delete_tmpdir(tmpdir_path)

            # If we reach here after fix, directory should be deleted
            assert not tmpdir_path.exists(), "Directory should be deleted"

    def test_skips_non_tmp_directories(self):
        """Test that _delete_tmpdir skips non-tmp directories."""
        import tempfile
        from compile import _delete_tmpdir, _should_delete_tmpdir

        with tempfile.TemporaryDirectory(prefix="regular_dir_") as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Verify it's not a tmp-style directory
            assert not _should_delete_tmpdir(tmpdir_path), \
                "Regular directory should not match tmp pattern"

            # Try to delete (should be skipped)
            _delete_tmpdir(tmpdir_path)

            # Directory should still exist
            assert tmpdir_path.exists(), "Non-tmp directory should not be deleted"

    def test_handles_nonexistent_directory(self):
        """Test that _delete_tmpdir handles nonexistent directory gracefully."""
        from compile import _delete_tmpdir

        fake_path = Path("/tmp/nonexistent_dir_12345")

        # Should not raise any exception
        _delete_tmpdir(fake_path)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])

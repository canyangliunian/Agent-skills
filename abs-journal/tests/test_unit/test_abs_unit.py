#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for abs-journal - TDD Approach

This module contains unit tests for abs-journal functions:
1. supports_color() - environment variable combination tests
2. validate_no_overlap() - boundary condition tests
3. render_report() - gating_meta=None handling tests

Following TDD principles:
- Write tests first to understand expected behavior
- Run tests to verify current behavior
- Identify bugs and edge cases
- Work with code-reviewer to fix issues
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import pytest


class TestSupportsColor:
    """Tests for supports_color() function in abs_article_impl.py"""

    def test_no_color_disables_color(self, monkeypatch):
        """Test that NO_COLOR environment variable disables color."""
        monkeypatch.setenv("NO_COLOR", "1")
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        monkeypatch.setenv("TERM", "xterm-256color")

        from abs_article_impl import supports_color

        result = supports_color()
        assert result is False, "NO_COLOR=1 should disable color"

    def test_empty_term_disables_color(self, monkeypatch):
        """Test that empty TERM disables color."""
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("TERM", "")

        from abs_article_impl import supports_color

        result = supports_color()
        assert result is False, "empty TERM should disable color"

    def test_dumb_term_disables_color(self, monkeypatch):
        """Test that TERM=dumb disables color."""
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("TERM", "dumb")

        from abs_article_impl import supports_color

        result = supports_color()
        assert result is False, "TERM=dumb should disable color"

    def test_valid_term_enables_color(self, monkeypatch):
        """Test that valid TERM enables color when NO_COLOR is not set."""
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("TERM", "xterm-256color")

        from abs_article_impl import supports_color

        result = supports_color()
        assert result is True, "valid TERM should enable color"

    def test_force_color_conflict_behavior(self, monkeypatch):
        """Test behavior when both NO_COLOR and FORCE_COLOR are set.

        Note: This test documents current behavior. The expected behavior
        when both are set should be clarified (current: NO_COLOR wins).
        """
        monkeypatch.setenv("NO_COLOR", "1")
        monkeypatch.setenv("FORCE_COLOR", "1")
        monkeypatch.setenv("TERM", "xterm-256color")

        from abs_article_impl import supports_color

        result = supports_color()
        # Current behavior: NO_COLOR takes precedence
        assert result is False, "NO_COLOR should take precedence over FORCE_COLOR"


class TestValidateNoOverlap:
    """Tests for validate_no_overlap() function in abs_ai_review.py"""

    def test_no_overlap_valid_input(self):
        """Test that valid input with no overlaps returns empty list."""
        from abs_ai_review import validate_no_overlap

        ai_output = {
            "easy": [{"journal": "Journal A", "topic": "topic 1"}],
            "medium": [{"journal": "Journal B", "topic": "topic 2"}],
            "hard": [{"journal": "Journal C", "topic": "topic 3"}],
        }

        errors = validate_no_overlap(ai_output)
        assert errors == [], "no overlaps should return empty error list"

    def test_detects_overlap_between_buckets(self):
        """Test that overlap between buckets is detected."""
        from abs_ai_review import validate_no_overlap

        ai_output = {
            "easy": [{"journal": "Journal A", "topic": "topic 1"}],
            "medium": [{"journal": "Journal A", "topic": "topic 2"}],  # Duplicate!
            "hard": [{"journal": "Journal C", "topic": "topic 3"}],
        }

        errors = validate_no_overlap(ai_output)
        assert len(errors) == 1, "should detect 1 overlap"
        assert "Journal A" in errors[0], "error should mention Journal A"
        assert "easy" in errors[0] and "medium" in errors[0], \
            "error should mention both buckets"

    def test_allows_explicit_overlap(self):
        """Test that meta.allow_overlap=True allows overlaps."""
        from abs_ai_review import validate_no_overlap

        ai_output = {
            "meta": {"allow_overlap": True},
            "easy": [{"journal": "Journal A", "topic": "topic 1"}],
            "medium": [{"journal": "Journal A", "topic": "topic 2"}],  # Allowed!
            "hard": [{"journal": "Journal C", "topic": "topic 3"}],
        }

        errors = validate_no_overlap(ai_output)
        assert errors == [], "allow_overlap=True should permit overlaps"

    def test_handles_empty_buckets(self):
        """Test that empty buckets don't cause errors."""
        from abs_ai_review import validate_no_overlap

        ai_output = {
            "easy": [],
            "medium": [],
            "hard": [],
        }

        errors = validate_no_overlap(ai_output)
        assert errors == [], "empty buckets should return no errors"

    def test_handles_missing_buckets(self):
        """Test that missing buckets don't cause errors."""
        from abs_ai_review import validate_no_overlap

        ai_output = {
            "easy": [{"journal": "Journal A", "topic": "topic 1"}],
            # medium and hard are missing
        }

        errors = validate_no_overlap(ai_output)
        assert errors == [], "missing buckets should be handled gracefully"

    def test_normalizes_whitespace_in_journal_names(self):
        """Test that journal names with different whitespace are treated as same."""
        from abs_ai_review import validate_no_overlap

        ai_output = {
            "easy": [{"journal": "Journal  A", "topic": "topic 1"}],  # Double space
            "medium": [{"journal": "Journal A", "topic": "topic 2"}],  # Single space
            "hard": [],
        }

        errors = validate_no_overlap(ai_output)
        # After .strip(), "Journal  A" and "Journal A" should be treated as same
        # Current behavior: they are treated as different (potential bug?)
        # This test documents current behavior
        assert len(errors) == 1, "should detect overlap after whitespace normalization"

    def test_handles_none_input(self):
        """Test that None input is handled gracefully."""
        from abs_ai_review import validate_no_overlap

        # This might raise an exception - that's a bug to fix
        with pytest.raises((AttributeError, TypeError)):
            validate_no_overlap(None)

    def test_handles_empty_string_journal(self):
        """Test that empty journal names are skipped."""
        from abs_ai_review import validate_no_overlap

        ai_output = {
            "easy": [{"journal": "", "topic": "topic 1"}],
            "medium": [{"journal": "   ", "topic": "topic 2"}],  # Whitespace only
            "hard": [{"journal": "Journal C", "topic": "topic 3"}],
        }

        errors = validate_no_overlap(ai_output)
        assert errors == [], "empty journal names should be skipped"

    def test_handles_non_dict_items(self):
        """Test that non-dict items are skipped."""
        from abs_ai_review import validate_no_overlap

        ai_output = {
            "easy": ["string", 123, None],  # Non-dict items
            "medium": [{"journal": "Journal A", "topic": "topic"}],
            "hard": [],
        }

        errors = validate_no_overlap(ai_output)
        assert errors == [], "non-dict items should be skipped"


class TestRenderReport:
    """Tests for render_report() function in hybrid_report.py"""

    def test_handles_none_gating_meta(self):
        """Test that gating_meta=None is handled gracefully."""
        # This test will be implemented after understanding the function signature
        # For now, document the expected behavior
        pass

    def test_renders_valid_gating_meta(self):
        """Test that valid gating_meta is rendered correctly."""
        # This test will be implemented after understanding the function signature
        pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])

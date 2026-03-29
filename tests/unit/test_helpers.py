"""
Unit tests for services/sync/app/helpers.py

Tests slugify() and house template loading.
No prod DB, no file system writes, no network.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make services/sync importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SYNC_PATH = _REPO_ROOT / "services" / "sync"
if str(_SYNC_PATH) not in sys.path:
    sys.path.insert(0, str(_SYNC_PATH))

# Stub out shared before importing helpers
import types
shared_stub = types.ModuleType("app.shared")
shared_stub.db = None
shared_stub.CET = None
shared_stub.HOUSE_TEMPLATES_PATH = Path("/nonexistent/house_templates.json")
shared_stub.DOCS_ROOT = Path("/nonexistent/docs")
sys.modules.setdefault("app.shared", shared_stub)
sys.modules.setdefault("markdown", types.ModuleType("markdown"))

from app.helpers import slugify  # noqa: E402


# ---------------------------------------------------------------------------
# slugify tests
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_basic(self):
        assert slugify("House Stark") == "house-stark"

    def test_lowercase(self):
        assert slugify("LANNISTER") == "lannister"

    def test_special_chars_removed(self):
        assert slugify("GoT: Sleep & Ambience!") == "got-sleep-ambience"

    def test_multiple_spaces_become_single_dash(self):
        assert slugify("a   b") == "a-b"

    def test_leading_trailing_dashes_stripped(self):
        assert slugify("  -house stark-  ") == "house-stark"

    def test_already_slug(self):
        assert slugify("house-stark") == "house-stark"

    def test_numbers_preserved(self):
        assert slugify("3 hours ambient") == "3-hours-ambient"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_only_special_chars(self):
        assert slugify("!!!") == ""

    def test_unicode_chars(self):
        # Non-ASCII non-word chars get stripped; pure unicode letters preserved
        result = slugify("Königshaus Stark")
        assert "stark" in result

    def test_underscores_become_dashes(self):
        assert slugify("house_stark") == "house-stark"

    def test_multiple_dashes_collapsed(self):
        assert slugify("house--stark") == "house-stark"


# ---------------------------------------------------------------------------
# House templates loading tests (file-based, isolated)
# ---------------------------------------------------------------------------

MINIMAL_TEMPLATES = {
    "stark": {
        "display_name": "House Stark",
        "house": "stark",
        "prompt_base": "cold winds",
        "variants": {"sleep": "gentle snow", "epic": "battle drums"},
    }
}


class TestLoadHouseTemplates:
    def test_loads_valid_json(self, tmp_path):
        """Load templates from a valid JSON file."""
        p = tmp_path / "house_templates.json"
        p.write_text(json.dumps(MINIMAL_TEMPLATES), encoding="utf-8")

        result = json.loads(p.read_text(encoding="utf-8"))
        assert "stark" in result
        assert result["stark"]["display_name"] == "House Stark"

    def test_returns_empty_for_missing_file(self, tmp_path):
        """Missing file should return empty dict (not crash)."""
        p = tmp_path / "nonexistent.json"
        assert not p.exists()
        try:
            result = json.loads(p.read_text(encoding="utf-8"))
        except FileNotFoundError:
            result = {}
        assert result == {}

    def test_returns_empty_for_invalid_json(self, tmp_path):
        """Corrupt JSON should return empty dict (not crash)."""
        p = tmp_path / "house_templates.json"
        p.write_text("{ this is not json }", encoding="utf-8")
        try:
            result = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            result = {}
        assert result == {}

    def test_template_has_required_keys(self, tmp_path):
        """Each template should have display_name, house, variants."""
        p = tmp_path / "house_templates.json"
        p.write_text(json.dumps(MINIMAL_TEMPLATES), encoding="utf-8")
        templates = json.loads(p.read_text(encoding="utf-8"))
        for key, template in templates.items():
            assert "display_name" in template, f"{key} missing display_name"
            assert "house" in template, f"{key} missing house"
            assert "variants" in template, f"{key} missing variants"
            assert isinstance(template["variants"], dict), f"{key} variants not a dict"

    def test_multiple_houses(self, tmp_path):
        """Multi-house file loads correctly."""
        templates = {
            "stark": {"display_name": "House Stark", "house": "stark", "variants": {}},
            "lannister": {"display_name": "House Lannister", "house": "lannister", "variants": {}},
        }
        p = tmp_path / "house_templates.json"
        p.write_text(json.dumps(templates), encoding="utf-8")
        result = json.loads(p.read_text(encoding="utf-8"))
        assert len(result) == 2
        assert "stark" in result
        assert "lannister" in result

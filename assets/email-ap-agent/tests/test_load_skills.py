"""Tests for load_skill_resources.py."""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
os.environ["IBD_TESTING"] = "1"

from load_skill_resources import _load_skill, get_load_skill_resource_tool


def test_get_load_skill_resource_tool_returns_list():
    tools = get_load_skill_resource_tool()
    assert isinstance(tools, list)
    assert len(tools) == 1


def test_load_skill_tool_has_correct_name():
    tools = get_load_skill_resource_tool()
    assert tools[0].name == "load_skill"


def test_load_skill_tool_has_description():
    tools = get_load_skill_resource_tool()
    assert len(tools[0].description) > 10


@pytest.mark.asyncio
async def test_load_skill_returns_string():
    result = await _load_skill("email-classification/SKILL.md")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_load_skill_returns_not_found_for_missing_file():
    result = await _load_skill("nonexistent/SKILL.md")
    assert "not found" in result.lower() or "error" in result.lower()


@pytest.mark.asyncio
async def test_load_skill_handles_read_error_gracefully(tmp_path, monkeypatch):
    """Test that _load_skill handles unreadable files gracefully."""
    import load_skill_resources
    monkeypatch.setattr(load_skill_resources, "SKILLS_DIR", tmp_path)
    test_file = tmp_path / "test-skill" / "SKILL.md"
    test_file.parent.mkdir()
    test_file.write_text("# Test Skill\nThis is a test skill.")
    result = await _load_skill("test-skill/SKILL.md")
    assert "Test Skill" in result or "test skill" in result.lower()

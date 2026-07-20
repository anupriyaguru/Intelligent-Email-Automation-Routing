"""Tests for util.py helper functions."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
os.environ["IBD_TESTING"] = "1"

from util import enhance_tool_description, enhance_tool_name


def _mock_tool(name="test_tool", server_name="test-server", description="Test desc"):
    m = MagicMock()
    m.name = name
    m.server_name = server_name
    m.description = description
    return m


def test_enhance_tool_name_with_server():
    tool = _mock_tool(name="get_data", server_name="my-server")
    result = enhance_tool_name(tool)
    assert "get_data" in result
    assert "my_server" in result or result == "my_server__get_data"


def test_enhance_tool_name_without_server():
    tool = _mock_tool(name="get_data", server_name="")
    result = enhance_tool_name(tool)
    assert result == "get_data"


def test_enhance_tool_name_replaces_hyphens_with_underscores():
    tool = _mock_tool(name="list_items", server_name="sap-s4-cloud")
    result = enhance_tool_name(tool)
    assert "-" not in result
    assert "sap_s4_cloud" in result


def test_enhance_tool_description_with_server():
    tool = _mock_tool(description="Returns data", server_name="sap-s4")
    result = enhance_tool_description(tool)
    assert "Returns data" in result
    assert "sap-s4" in result


def test_enhance_tool_description_without_server():
    tool = _mock_tool(description="Returns data", server_name="")
    result = enhance_tool_description(tool)
    assert result == "Returns data"


def test_enhance_tool_description_none_desc():
    m = MagicMock()
    m.name = "test"
    m.server_name = ""
    m.description = None
    result = enhance_tool_description(m)
    assert isinstance(result, str)


def test_enhance_tool_description_wraps_server_in_brackets():
    tool = _mock_tool(description="Get invoice status", server_name="sap-ap-mcp")
    result = enhance_tool_description(tool)
    assert "[sap-ap-mcp]" in result


def test_enhance_tool_name_dots_become_underscores():
    tool = _mock_tool(name="get_status", server_name="sap.s4.cloud")
    result = enhance_tool_name(tool)
    assert "." not in result
    assert "sap_s4_cloud" in result

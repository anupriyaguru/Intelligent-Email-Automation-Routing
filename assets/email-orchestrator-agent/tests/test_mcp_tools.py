"""Unit tests for mcp_tools.py — mock mode."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
os.environ["IBD_TESTING"] = "1"


def _write_mock_file(tmp_path):
    mock_data = {
        "servers": {
            "test-server": {
                "tools": {
                    "get_test_data": {
                        "description": "Get test data from SAP",
                        "mock_response": {"result": "test_value", "status": "ok"},
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "record_id": {"type": "string", "description": "Record ID"},
                                "count": {"type": "integer", "description": "Count"},
                            },
                            "required": ["record_id"]
                        }
                    },
                    "create_entry": {
                        "description": "Create a new entry",
                        "mock_response": {"created": True, "id": "NEW-001"},
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Entry name"},
                                "active": {"type": "boolean", "description": "Is active"},
                            },
                            "required": ["name"]
                        }
                    }
                }
            }
        }
    }
    return mock_data


def test_get_mcp_tools_returns_list_in_test_mode(tmp_path, monkeypatch):
    import mcp_tools
    mock_path = tmp_path / "mcp-mock.json"
    mock_data = _write_mock_file(tmp_path)
    mock_path.write_text(json.dumps(mock_data))
    monkeypatch.setattr(mcp_tools, "_MOCK_FILE", mock_path)
    tools = mcp_tools._build_mock_tools()
    assert isinstance(tools, list)
    assert len(tools) == 2


def test_mock_tools_have_names(tmp_path, monkeypatch):
    import mcp_tools
    mock_path = tmp_path / "mcp-mock.json"
    mock_data = _write_mock_file(tmp_path)
    mock_path.write_text(json.dumps(mock_data))
    monkeypatch.setattr(mcp_tools, "_MOCK_FILE", mock_path)
    tools = mcp_tools._build_mock_tools()
    names = [t.name for t in tools]
    assert "get_test_data" in names
    assert "create_entry" in names


@pytest.mark.asyncio
async def test_mock_tool_returns_mock_response(tmp_path, monkeypatch):
    import mcp_tools
    mock_path = tmp_path / "mcp-mock.json"
    mock_data = _write_mock_file(tmp_path)
    mock_path.write_text(json.dumps(mock_data))
    monkeypatch.setattr(mcp_tools, "_MOCK_FILE", mock_path)
    tools = mcp_tools._build_mock_tools()
    get_tool = next(t for t in tools if t.name == "get_test_data")
    result = await get_tool.coroutine(record_id="R-001")
    data = json.loads(result)
    assert data["result"] == "test_value"
    assert data["status"] == "ok"


def test_build_mock_tools_returns_empty_when_no_file(monkeypatch):
    import mcp_tools
    from pathlib import Path
    monkeypatch.setattr(mcp_tools, "_MOCK_FILE", Path("/nonexistent/mcp-mock.json"))
    tools = mcp_tools._build_mock_tools()
    assert tools == []


def test_set_user_token_and_get_user_token():
    from mcp_tools import get_user_token, set_user_token
    token_before = get_user_token()
    set_user_token("test-jwt-token-abc123")
    assert get_user_token() == "test-jwt-token-abc123"
    set_user_token(token_before)


@pytest.mark.asyncio
async def test_get_mcp_tools_in_test_mode(tmp_path, monkeypatch):
    import mcp_tools
    mock_path = tmp_path / "mcp-mock.json"
    mock_data = _write_mock_file(tmp_path)
    mock_path.write_text(json.dumps(mock_data))
    monkeypatch.setattr(mcp_tools, "_MOCK_FILE", mock_path)
    tools = await mcp_tools.get_mcp_tools()
    assert isinstance(tools, list)
    assert len(tools) == 2

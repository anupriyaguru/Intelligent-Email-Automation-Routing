"""Unit tests for email-collections-agent tools.py."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
os.environ["IBD_TESTING"] = "1"

from tools import get_collections_tools


def test_financial_action_threshold():
    from tools import FINANCIAL_ACTION_THRESHOLD
    assert FINANCIAL_ACTION_THRESHOLD == 5000.00


def test_get_collections_tools_returns_list():
    tools = get_collections_tools()
    assert isinstance(tools, list)
    assert len(tools) >= 1


def test_all_tools_have_name_and_description():
    tools = get_collections_tools()
    for tool in tools:
        assert tool.name, f"Tool missing name"
        assert tool.description, f"Tool {tool.name} missing description"


def test_tool_names_are_unique():
    tools = get_collections_tools()
    names = [t.name for t in tools]
    assert len(names) == len(set(names))


@pytest.mark.asyncio
async def test_first_tool_returns_json():
    tools = get_collections_tools()
    first_tool = tools[0]
    schema = first_tool.args_schema
    if schema:
        fields = schema.model_fields
        sample_kwargs = {}
        for fname, finfo in fields.items():
            ann = finfo.annotation
            default = finfo.default
            if default is None or str(default) == "PydanticUndefined":
                if ann == int or ann == float:
                    sample_kwargs[fname] = 1 if ann == int else 1.0
                else:
                    sample_kwargs[fname] = "TEST-001"
        result = await first_tool.coroutine(**sample_kwargs)
    else:
        result = await first_tool.coroutine()
    assert result is not None
    data = json.loads(result)
    assert isinstance(data, dict)

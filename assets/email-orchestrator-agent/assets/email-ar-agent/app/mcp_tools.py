"""MCP tool loader.

Owned indirection layer between agent code and the Agent Gateway.
All agent code imports get_mcp_tools from here.
"""

import json
import logging
import os
import time
from contextvars import ContextVar, Token
from pathlib import Path
from typing import Any, Optional

from sap_cloud_sdk.agentgateway import create_client
from pydantic import create_model
from langchain_core.tools import StructuredTool

from util import enhance_tool_description, enhance_tool_name, call_mcp_tool_with_retry

logger = logging.getLogger(__name__)

_user_token_context: ContextVar[str | None] = ContextVar('user_token', default=None)
_agw_client: Optional[Any] = None
_MOCK_FILE = Path(__file__).parent.parent / "mcp-mock.json"


def _build_mock_tools() -> list:
    if not _MOCK_FILE.exists():
        return []
    try:
        mock_data = json.loads(_MOCK_FILE.read_text())
    except Exception:
        return []
    tools = []
    from langchain_core.tools import StructuredTool
    from pydantic import Field, create_model
    for _server_slug, server in mock_data.get("servers", {}).items():
        for tool_name, tool_def in server.get("tools", {}).items():
            description = tool_def.get("description", "")
            mock_response = tool_def.get("mock_response", {})
            input_schema = tool_def.get("input_schema", {})
            props = input_schema.get("properties", {})
            required_fields = set(input_schema.get("required", []))
            field_definitions: dict = {}
            for field_name, field_info in props.items():
                json_type = field_info.get("type", "string")
                python_type = int if json_type == "integer" else (float if json_type == "number" else (bool if json_type == "boolean" else str))
                if field_name in required_fields:
                    field_definitions[field_name] = (python_type, Field(description=field_info.get("description", "")))
                else:
                    field_definitions[field_name] = (python_type, Field(default=None, description=field_info.get("description", "")))
            args_schema = create_model(f"{tool_name}_args", **field_definitions) if field_definitions else create_model(f"{tool_name}_args")
            _response = json.dumps(mock_response)
            async def _coroutine(_resp=_response, **kwargs) -> str:
                return _resp
            tools.append(StructuredTool(name=tool_name, description=description, args_schema=args_schema, coroutine=_coroutine, handle_tool_error=True))
    return tools


async def get_mcp_tools(user_token: str | None = None) -> list:
    global _agw_client
    if os.environ.get("IBD_TESTING") == "1":
        return _build_mock_tools()
    if not user_token:
        raise ValueError("user_token is required")
    try:
        if _agw_client is None:
            _agw_client = create_client()
        mcp_tools = await _agw_client.list_mcp_tools(user_token=user_token)
        if not mcp_tools:
            return []
        langchain_tools = []
        for mcp_tool in mcp_tools:
            try:
                properties = mcp_tool.input_schema.get("properties", {})
                required = set(mcp_tool.input_schema.get("required", []))
                fields = {}
                for name, prop in properties.items():
                    ptype = str
                    if prop.get("type") == "integer": ptype = int
                    elif prop.get("type") == "number": ptype = float
                    elif prop.get("type") == "boolean": ptype = bool
                    fields[name] = (ptype, ...) if name in required else (ptype | None, None)
                args_schema = create_model(f"{mcp_tool.name}_args", **fields) if fields else None
                agw_client = _agw_client
                async def run(**kwargs) -> str:
                    return await call_mcp_tool_with_retry(agw_client, mcp_tool, user_token=_user_token_context.get(), **kwargs)
                langchain_tools.append(StructuredTool.from_function(coroutine=run, name=mcp_tool.name, description=getattr(mcp_tool, 'description', ''), args_schema=args_schema, handle_tool_error=True))
            except Exception as e:
                logger.warning(f"Failed to convert tool {mcp_tool.name}: {e}")
        return langchain_tools
    except Exception:
        _agw_client = None
        return []


def set_user_token(user_token: str | None) -> Token:
    return _user_token_context.set(user_token)


def get_user_token() -> str | None:
    return _user_token_context.get()

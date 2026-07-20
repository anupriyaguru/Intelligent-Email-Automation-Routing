"""Utility helpers for MCP tool integration."""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def enhance_tool_name(mcp_tool: Any) -> str:
    """Return namespaced tool name to avoid conflicts across MCP servers."""
    server_name = getattr(mcp_tool, 'server_name', '').replace('-', '_').replace('.', '_')
    tool_name = getattr(mcp_tool, 'name', 'unknown')
    if server_name:
        return f"{server_name}__{tool_name}"
    return tool_name


def enhance_tool_description(mcp_tool: Any) -> str:
    """Return enhanced description including server context."""
    desc = getattr(mcp_tool, 'description', '') or ''
    server_name = getattr(mcp_tool, 'server_name', '')
    if server_name:
        return f"[{server_name}] {desc}"
    return desc


async def call_mcp_tool_with_retry(agw_client: Any, mcp_tool: Any, user_token: str | None = None, retries: int = 3, **kwargs) -> str:
    """Call an MCP tool with retry logic."""
    import asyncio
    last_error = None
    for attempt in range(retries):
        try:
            result = await agw_client.call_mcp_tool(mcp_tool, user_token=[REDACTED], **kwargs)
            return str(result)
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
            logger.warning(f"MCP tool call attempt {attempt + 1} failed: {e}")
    raise last_error

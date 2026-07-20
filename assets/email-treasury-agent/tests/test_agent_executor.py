"""Smoke tests for agent_executor.py — verifies module loads and class instantiates."""
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
os.environ["IBD_TESTING"] = "1"


def test_agent_executor_module_importable():
    """Verify the agent_executor module can be imported (checks for syntax errors)."""
    try:
        import agent_executor
        assert hasattr(agent_executor, "AgentExecutor")
    except ImportError as e:
        pytest.skip(f"A2A SDK not available in test environment: {e}")


def test_agent_executor_class_exists():
    """Verify AgentExecutor class exists in the module."""
    try:
        from agent_executor import AgentExecutor
        assert AgentExecutor is not None
    except ImportError as e:
        pytest.skip(f"A2A SDK not available: {e}")


def test_agent_executor_inherits_base():
    """Verify AgentExecutor inherits from A2A base class."""
    try:
        from agent_executor import AgentExecutor
        from a2a.server.agent_execution import AgentExecutor as A2ABase
        assert issubclass(AgentExecutor, A2ABase)
    except ImportError as e:
        pytest.skip(f"A2A SDK not available: {e}")


def test_agent_executor_has_execute_method():
    """Verify AgentExecutor has execute method."""
    try:
        from agent_executor import AgentExecutor
        assert hasattr(AgentExecutor, "execute")
        assert callable(AgentExecutor.execute)
    except ImportError as e:
        pytest.skip(f"A2A SDK not available: {e}")


def test_agent_executor_has_cancel_method():
    """Verify AgentExecutor has cancel method."""
    try:
        from agent_executor import AgentExecutor
        assert hasattr(AgentExecutor, "cancel")
    except ImportError as e:
        pytest.skip(f"A2A SDK not available: {e}")

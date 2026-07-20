"""Unit tests for email-orchestrator-agent agent.py."""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
os.environ["IBD_TESTING"] = "1"

from agent import SampleAgent, get_confidence_threshold, get_model_name, get_system_prompt, get_temperature


def test_get_model_name_returns_string():
    name = get_model_name()
    assert isinstance(name, str)
    assert len(name) > 0


def test_get_temperature_returns_float():
    temp = get_temperature()
    assert isinstance(temp, float)
    assert 0.0 <= temp <= 1.0


def test_get_system_prompt_contains_orchestrator():
    prompt = get_system_prompt()
    assert "orchestrat" in prompt.lower()


def test_get_system_prompt_mentions_milestones():
    prompt = get_system_prompt()
    assert "M1" in prompt and "M2" in prompt


def test_get_system_prompt_mentions_financial_threshold():
    prompt = get_system_prompt()
    assert "threshold" in prompt.lower() or "financial" in prompt.lower()


def test_get_confidence_threshold_value():
    threshold = get_confidence_threshold()
    assert threshold == 0.75


def test_sample_agent_initialization():
    agent = SampleAgent()
    assert agent is not None
    assert hasattr(agent, "llm")
    assert hasattr(agent, "stream")
    assert hasattr(agent, "invoke")


def test_sample_agent_supported_content_types():
    agent = SampleAgent()
    assert "text" in agent.SUPPORTED_CONTENT_TYPES


@pytest.mark.asyncio
async def test_stream_yields_dict():
    """Test that stream yields dicts with required keys (mock tools)."""
    agent = SampleAgent()
    results = []
    async for chunk in agent.stream("Hello", "test-context-id", tools=[]):
        results.append(chunk)
        if len(results) > 5:
            break

    assert len(results) >= 1
    last = results[-1]
    assert "is_task_complete" in last
    assert "require_user_input" in last
    assert "content" in last

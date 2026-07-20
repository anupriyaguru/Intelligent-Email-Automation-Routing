"""Unit tests for email-ap-agent agent.py."""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
os.environ["IBD_TESTING"] = "1"

from agent import SampleAgent, get_model_name, get_system_prompt, get_temperature


def test_get_model_name_returns_string():
    name = get_model_name()
    assert isinstance(name, str)
    assert len(name) > 0


def test_get_temperature_returns_float():
    temp = get_temperature()
    assert isinstance(temp, float)
    assert 0.0 <= temp <= 1.0


def test_get_system_prompt_mentions_ap():
    prompt = get_system_prompt()
    assert "ap" in prompt.lower()


def test_get_system_prompt_mentions_requires_human_review():
    prompt = get_system_prompt()
    assert "requires_human_review" in prompt


def test_get_system_prompt_not_empty():
    prompt = get_system_prompt()
    assert len(prompt) > 100


def test_sample_agent_initialization():
    agent = SampleAgent()
    assert agent is not None
    assert hasattr(agent, "llm")
    assert hasattr(agent, "stream")


def test_sample_agent_supported_content_types():
    assert "text" in SampleAgent.SUPPORTED_CONTENT_TYPES


@pytest.mark.asyncio
async def test_stream_yields_dict():
    agent = SampleAgent()
    results = []
    async for chunk in agent.stream("Hello", "ctx-001", tools=[]):
        results.append(chunk)
        if len(results) > 5:
            break
    assert len(results) >= 1
    last = results[-1]
    assert "is_task_complete" in last
    assert "content" in last

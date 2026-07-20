"""Unit tests for Orchestrator Agent tools."""
import json
import os
import sys
from pathlib import Path

import pytest

# Ensure app/ on path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
os.environ["IBD_TESTING"] = "1"

from tools import (
    CONFIDENCE_THRESHOLD,
    FINANCIAL_ACTION_THRESHOLD,
    _check_completeness,
    _classify_email_intent,
    _detect_language,
    _flag_review,
    _identify_bp,
    _query_knowledge_base,
    _send_email,
    _write_kb,
    get_orchestrator_tools,
)


@pytest.mark.asyncio
async def test_classify_email_intent_returns_instruction():
    result = await _classify_email_intent(
        subject="Account statement request",
        body="Please send me my account statement for Q4 2024.",
        case_id="TEST-001"
    )
    data = json.loads(result)
    assert data["case_id"] == "TEST-001"
    assert "instruction" in data
    assert "classification" in data["instruction"].lower() or "classify" in data["instruction"].lower()


@pytest.mark.asyncio
async def test_classify_email_intent_generates_case_id_when_missing():
    result = await _classify_email_intent(
        subject="Subject",
        body="Body text",
    )
    data = json.loads(result)
    assert "case_id" in data
    assert len(data["case_id"]) > 0


@pytest.mark.asyncio
async def test_identify_bp_returns_instruction():
    result = await _identify_bp(
        sender_email="test@example.com",
        case_id="TEST-002"
    )
    data = json.loads(result)
    assert "instruction" in data
    assert data["sender_email"] == "test@example.com"
    assert data["case_id"] == "TEST-002"


@pytest.mark.asyncio
async def test_check_completeness_dispute_requires_invoice():
    result = await _check_completeness(
        intent_category="dispute",
        email_body="We dispute the charge.",
        case_id="TEST-003"
    )
    data = json.loads(result)
    assert "invoice_number" in data["required_fields"]


@pytest.mark.asyncio
async def test_check_completeness_statement_requires_nothing():
    result = await _check_completeness(
        intent_category="statement_request",
        email_body="Please send my statement.",
        case_id="TEST-004"
    )
    data = json.loads(result)
    assert data["required_fields"] == []


@pytest.mark.asyncio
async def test_send_email_rejects_missing_case_id():
    result = await _send_email(
        recipient_email="test@example.com",
        subject="Test",
        body="Test body",
        case_id="",
        channel="outlook"
    )
    data = json.loads(result)
    assert "error" in data
    assert "case_id" in data["error"].lower()


@pytest.mark.asyncio
async def test_send_email_with_case_id_returns_instruction():
    result = await _send_email(
        recipient_email="test@example.com",
        subject="Re: Test",
        body="Dear Test, ...",
        case_id="CASE-001",
        channel="outlook"
    )
    data = json.loads(result)
    assert "instruction" in data
    assert data["case_id"] == "CASE-001"
    assert data["milestone"] == "M5"


@pytest.mark.asyncio
async def test_flag_review_includes_required_fields():
    result = await _flag_review(
        case_id="CASE-002",
        bp_id="BP-999",
        sender_email="user@test.com",
        subject="Unknown inquiry",
        body="I have a question...",
        intent_category="general_inquiry",
        confidence_score=0.45,
        flagged_reason="low_confidence",
    )
    data = json.loads(result)
    review = data["review_case"]
    assert review["case_id"] == "CASE-002"
    assert review["confidence_score"] == 0.45
    assert review["flagged_reason"] == "low_confidence"


@pytest.mark.asyncio
async def test_query_knowledge_base_returns_milestone():
    result = await _query_knowledge_base(
        bp_id="BP-123",
        intent_category="statement_request",
        case_id="CASE-003"
    )
    data = json.loads(result)
    assert data["milestone"] == "M2"
    assert data["bp_id"] == "BP-123"


@pytest.mark.asyncio
async def test_write_kb_logs_m6():
    result = await _write_kb(
        case_id="CASE-004",
        bp_id="BP-123",
        intent_category="statement_request",
        routing_path="email-ar-agent",
        response_summary="Statement sent for Q4 2024.",
        resolution_type="automated"
    )
    data = json.loads(result)
    assert data["milestone"] == "M6"
    assert data["case_record"]["case_id"] == "CASE-004"
    assert data["case_record"]["resolution_type"] == "automated"


@pytest.mark.asyncio
async def test_detect_language_returns_instruction():
    result = await _detect_language("Hello, please send my account statement.")
    data = json.loads(result)
    assert "instruction" in data


def test_financial_action_threshold_value():
    assert FINANCIAL_ACTION_THRESHOLD == 5000.00


def test_confidence_threshold_value():
    assert CONFIDENCE_THRESHOLD == 0.75


def test_get_orchestrator_tools_returns_list():
    tools = get_orchestrator_tools()
    assert isinstance(tools, list)
    assert len(tools) >= 10


def test_all_tools_have_name_and_description():
    tools = get_orchestrator_tools()
    for tool in tools:
        assert tool.name, f"Tool missing name"
        assert tool.description, f"Tool {tool.name} missing description"


def test_tool_names_are_unique():
    tools = get_orchestrator_tools()
    names = [t.name for t in tools]
    assert len(names) == len(set(names)), "Duplicate tool names detected"


def test_classify_email_tool_in_registry():
    tools = get_orchestrator_tools()
    names = [t.name for t in tools]
    assert "classify_email_intent" in names


def test_send_email_tool_in_registry():
    tools = get_orchestrator_tools()
    names = [t.name for t in tools]
    assert "send_email_reply" in names


def test_flag_review_tool_in_registry():
    tools = get_orchestrator_tools()
    names = [t.name for t in tools]
    assert "flag_for_human_review" in names

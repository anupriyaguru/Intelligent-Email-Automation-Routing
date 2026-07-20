"""Collections Agent tools — overdue accounts and dunning via MCP tools."""
import json
import logging

from langchain_core.tools import StructuredTool
from opentelemetry import trace
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

FINANCIAL_ACTION_THRESHOLD = 5000.00


class GetOverdueItemsInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")
    top: int = Field(default=50, le=100, description="Max records (max 100)")


class GetDunningHistoryInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")
    top: int = Field(default=10, le=100, description="Max records (max 100)")


class CheckPaymentArrangementInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")


class CreatePaymentArrangementInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")
    total_amount: float = Field(description="Total overdue amount to arrange")
    installments: int = Field(description="Number of installments")
    case_id: str = Field(description="Email case ID")


@tracer.start_as_current_span("get_overdue_items")
async def _get_overdue_items(bp_id: str, top: int = 50) -> str:
    top = min(top, 100)
    logger.info("[COL-M1].achieved: retrieving overdue items | bp_id=%s", bp_id)
    return json.dumps({
        "instruction": "Use the SAP S/4HANA Collections Management MCP tool to retrieve overdue receivables.",
        "bp_id": bp_id,
        "top": top
    })


@tracer.start_as_current_span("get_dunning_history")
async def _get_dunning_history(bp_id: str, top: int = 10) -> str:
    top = min(top, 100)
    logger.info("[COL-M1].achieved: retrieving dunning history | bp_id=%s", bp_id)
    return json.dumps({
        "instruction": "Use the SAP S/4HANA Collections Management MCP tool to retrieve dunning history and current dunning level.",
        "bp_id": bp_id,
        "top": top
    })


@tracer.start_as_current_span("check_existing_payment_arrangement")
async def _check_arrangement(bp_id: str) -> str:
    return json.dumps({
        "instruction": "Use the SAP S/4HANA Collections Management MCP tool to check for existing payment arrangements.",
        "bp_id": bp_id
    })


@tracer.start_as_current_span("create_payment_arrangement")
async def _create_arrangement(bp_id: str, total_amount: float, installments: int, case_id: str) -> str:
    if total_amount > FINANCIAL_ACTION_THRESHOLD:
        logger.info("[COL-M1].missed: payment arrangement requires human approval | amount=%.2f", total_amount)
        return json.dumps({
            "requires_human_review": True,
            "requires_human_review_reason": "high_value_payment_arrangement",
            "message": f"Payment arrangement of ${total_amount:.2f} exceeds threshold ${FINANCIAL_ACTION_THRESHOLD:.2f}.",
            "arrangement_draft": {"bp_id": bp_id, "total_amount": total_amount, "installments": installments, "case_id": case_id}
        })
    logger.info("[COL-M1].achieved: creating payment arrangement | amount=%.2f | installments=%d", total_amount, installments)
    return json.dumps({
        "instruction": "Use the SAP S/4HANA Collections Management MCP tool to create a payment arrangement.",
        "bp_id": bp_id,
        "total_amount": total_amount,
        "installments": installments,
        "case_id": case_id
    })


def get_collections_tools() -> list:
    return [
        StructuredTool(
            name="get_overdue_items",
            description="Retrieve overdue receivable items for a business partner including days past due and aging buckets.",
            args_schema=GetOverdueItemsInput,
            coroutine=_get_overdue_items,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="get_dunning_history",
            description="Retrieve dunning correspondence history and current dunning level for a business partner.",
            args_schema=GetDunningHistoryInput,
            coroutine=_get_dunning_history,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="check_existing_payment_arrangement",
            description="Check if there is an existing payment arrangement for a business partner.",
            args_schema=CheckPaymentArrangementInput,
            coroutine=_check_arrangement,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="create_payment_arrangement",
            description="Create a payment arrangement for overdue balance. Automatically flags for human review if amount exceeds $5,000.",
            args_schema=CreatePaymentArrangementInput,
            coroutine=_create_arrangement,
            handle_tool_error=True,
        ),
    ]

"""AR Agent tools — Accounts Receivable operations via MCP tools."""
import json
import logging
from typing import Optional

from langchain_core.tools import StructuredTool
from opentelemetry import trace
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

FINANCIAL_ACTION_THRESHOLD = 5000.00


class GetAccountStatementInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")
    fiscal_year: Optional[str] = Field(default=None, description="Fiscal year, e.g. '2024'")
    top: int = Field(default=50, le=100, description="Max records to return (max 100)")


class GetOpenItemsInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")
    top: int = Field(default=50, le=100, description="Max records to return (max 100)")


class CreateDisputeCaseInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")
    invoice_number: str = Field(description="Invoice number being disputed")
    dispute_amount: float = Field(description="Amount being disputed")
    dispute_reason: str = Field(description="Reason for the dispute")
    case_id: str = Field(description="Email case ID for reference")


class GetDisputeStatusInput(BaseModel):
    dispute_case_id: str = Field(description="SAP dispute case ID")


class CreateCreditMemoInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")
    original_invoice: str = Field(description="Original invoice number")
    credit_amount: float = Field(description="Credit amount to apply")
    reason: str = Field(description="Reason for the credit memo")
    case_id: str = Field(description="Email case ID for reference")


@tracer.start_as_current_span("get_account_statement")
async def _get_account_statement(bp_id: str, fiscal_year: Optional[str] = None, top: int = 50) -> str:
    top = min(top, 100)
    logger.info("[AR-M1].achieved: retrieving account statement | bp_id=%s | year=%s", bp_id, fiscal_year)
    return json.dumps({
        "instruction": "Use the SAP S/4HANA AR OData MCP tool to retrieve the account statement for this business partner.",
        "bp_id": bp_id,
        "fiscal_year": fiscal_year or "current",
        "top": top
    })


@tracer.start_as_current_span("get_open_items")
async def _get_open_items(bp_id: str, top: int = 50) -> str:
    top = min(top, 100)
    logger.info("[AR-M1].achieved: retrieving open items | bp_id=%s", bp_id)
    return json.dumps({
        "instruction": "Use the SAP S/4HANA AR OData MCP tool to retrieve open items for this business partner.",
        "bp_id": bp_id,
        "top": top
    })


@tracer.start_as_current_span("create_dispute_case")
async def _create_dispute_case(bp_id: str, invoice_number: str, dispute_amount: float, dispute_reason: str, case_id: str) -> str:
    requires_human_review = dispute_amount > FINANCIAL_ACTION_THRESHOLD
    if requires_human_review:
        logger.info("[AR-M1].missed: dispute creation requires human approval | amount=%.2f | threshold=%.2f", dispute_amount, FINANCIAL_ACTION_THRESHOLD)
        return json.dumps({
            "requires_human_review": True,
            "requires_human_review_reason": "high_value_dispute",
            "message": f"Dispute amount ${dispute_amount:.2f} exceeds threshold ${FINANCIAL_ACTION_THRESHOLD:.2f}. Flagging for human approval.",
            "case_id": case_id
        })
    logger.info("[AR-M1].achieved: creating dispute case | invoice=%s | amount=%.2f", invoice_number, dispute_amount)
    return json.dumps({
        "instruction": "Use the SAP Dispute Management API MCP tool to create a new dispute case.",
        "bp_id": bp_id,
        "invoice_number": invoice_number,
        "dispute_amount": dispute_amount,
        "dispute_reason": dispute_reason,
        "case_id": case_id
    })


@tracer.start_as_current_span("get_dispute_status")
async def _get_dispute_status(dispute_case_id: str) -> str:
    return json.dumps({
        "instruction": "Use the SAP Dispute Management API MCP tool to retrieve the dispute case status.",
        "dispute_case_id": dispute_case_id
    })


@tracer.start_as_current_span("create_credit_memo")
async def _create_credit_memo(bp_id: str, original_invoice: str, credit_amount: float, reason: str, case_id: str) -> str:
    # Credit memos ALWAYS require human review
    logger.info("[AR-M1].missed: credit memo always requires human approval | amount=%.2f", credit_amount)
    return json.dumps({
        "requires_human_review": True,
        "requires_human_review_reason": "credit_memo_always_requires_approval",
        "message": "Credit memo requests always require human approval per company policy.",
        "credit_memo_draft": {
            "bp_id": bp_id,
            "original_invoice": original_invoice,
            "credit_amount": credit_amount,
            "reason": reason,
            "case_id": case_id
        }
    })


def get_ar_tools() -> list:
    """Return all AR Agent tools."""
    return [
        StructuredTool(
            name="get_account_statement",
            description="Retrieve the account statement for a business partner from SAP S/4HANA AR. Returns open items, balances, and transaction history.",
            args_schema=GetAccountStatementInput,
            coroutine=_get_account_statement,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="get_open_items",
            description="Retrieve open (unpaid) items for a business partner from SAP S/4HANA AR.",
            args_schema=GetOpenItemsInput,
            coroutine=_get_open_items,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="create_dispute_case",
            description="Create a dispute case in SAP Dispute Management. Automatically flags for human review if dispute amount exceeds $5,000.",
            args_schema=CreateDisputeCaseInput,
            coroutine=_create_dispute_case,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="get_dispute_status",
            description="Check the status of an existing SAP dispute case by its dispute case ID.",
            args_schema=GetDisputeStatusInput,
            coroutine=_get_dispute_status,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="create_credit_memo",
            description="Request a credit memo creation in SAP. Always flags for human review per company policy — never creates automatically.",
            args_schema=CreateCreditMemoInput,
            coroutine=_create_credit_memo,
            handle_tool_error=True,
        ),
    ]

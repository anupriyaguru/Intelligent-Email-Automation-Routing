"""Treasury Agent tools — payment terms and financing via MCP tools."""
import json
import logging

from langchain_core.tools import StructuredTool
from opentelemetry import trace
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class GetPaymentTermsInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")


class GetCreditLineInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID (customer)")


@tracer.start_as_current_span("get_payment_terms")
async def _get_payment_terms(bp_id: str) -> str:
    logger.info("[TR-M1].achieved: retrieving payment terms | bp_id=%s", bp_id)
    return json.dumps({
        "instruction": "Use the SAP S/4HANA Finance MCP tool to retrieve payment terms for this business partner.",
        "bp_id": bp_id
    })


@tracer.start_as_current_span("get_credit_line_status")
async def _get_credit_line(bp_id: str) -> str:
    logger.info("[TR-M1].achieved: retrieving credit line | bp_id=%s", bp_id)
    return json.dumps({
        "instruction": "Use the SAP S/4HANA Credit Management MCP tool to retrieve credit line availability for this business partner.",
        "bp_id": bp_id
    })


def get_treasury_tools() -> list:
    return [
        StructuredTool(
            name="get_payment_terms",
            description="Retrieve payment terms (net days, discount terms, baseline date) for a business partner from SAP S/4HANA.",
            args_schema=GetPaymentTermsInput,
            coroutine=_get_payment_terms,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="get_credit_line_status",
            description="Retrieve credit line availability and credit exposure for a customer business partner.",
            args_schema=GetCreditLineInput,
            coroutine=_get_credit_line,
            handle_tool_error=True,
        ),
    ]

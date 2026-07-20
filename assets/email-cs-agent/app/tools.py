"""Customer Service Agent tools — general inquiries and FAQ via MCP tools."""
import json
import logging

from langchain_core.tools import StructuredTool
from opentelemetry import trace
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class GetBPProfileInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")


class SearchFAQInput(BaseModel):
    query: str = Field(description="Customer or vendor question to search FAQs for")
    top: int = Field(default=5, le=20, description="Max FAQ results to return")


class GetPriorCasesInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")
    top: int = Field(default=10, le=100, description="Max prior cases to retrieve")


class LogComplaintInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")
    subject: str = Field(description="Complaint subject")
    body: str = Field(description="Complaint body text")
    case_id: str = Field(description="Email case ID")


@tracer.start_as_current_span("get_bp_profile")
async def _get_bp_profile(bp_id: str) -> str:
    logger.info("[CS-M1].achieved: retrieving BP profile | bp_id=%s", bp_id)
    return json.dumps({
        "instruction": "Use the SAP Business Partner MCP tool to retrieve the full profile for this business partner.",
        "bp_id": bp_id
    })


@tracer.start_as_current_span("search_faq_knowledge_base")
async def _search_faq(query: str, top: int = 5) -> str:
    logger.info("[CS-M1].achieved: searching FAQ knowledge base | query=%s", query[:80])
    return json.dumps({
        "instruction": "Use the HANA Cloud knowledge base MCP tool to search FAQ entries matching this query.",
        "query": query,
        "top": min(top, 20)
    })


@tracer.start_as_current_span("get_prior_cases")
async def _get_prior_cases(bp_id: str, top: int = 10) -> str:
    logger.info("[CS-M1].achieved: retrieving prior cases | bp_id=%s", bp_id)
    return json.dumps({
        "instruction": "Use the HANA Cloud knowledge base MCP tool to retrieve prior case history for this business partner.",
        "bp_id": bp_id,
        "top": min(top, 100)
    })


@tracer.start_as_current_span("log_complaint")
async def _log_complaint(bp_id: str, subject: str, body: str, case_id: str) -> str:
    logger.info("[CS-M1].achieved: logging complaint | bp_id=%s | case_id=%s", bp_id, case_id)
    return json.dumps({
        "instruction": "Use the HANA Cloud knowledge base MCP tool to record this complaint as a new case entry.",
        "complaint": {"bp_id": bp_id, "subject": subject, "body": body[:200], "case_id": case_id}
    })


def get_cs_tools() -> list:
    return [
        StructuredTool(
            name="get_business_partner_profile",
            description="Retrieve the full SAP Business Partner profile including contact info, account tier, and relationship details.",
            args_schema=GetBPProfileInput,
            coroutine=_get_bp_profile,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="search_faq_knowledge_base",
            description="Search the HANA Cloud FAQ knowledge base for answers to customer or vendor questions.",
            args_schema=SearchFAQInput,
            coroutine=_search_faq,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="get_prior_case_history",
            description="Retrieve prior case history for a business partner from the HANA Cloud knowledge base.",
            args_schema=GetPriorCasesInput,
            coroutine=_get_prior_cases,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="log_complaint",
            description="Log a customer or vendor complaint as a case record in the HANA Cloud knowledge base.",
            args_schema=LogComplaintInput,
            coroutine=_log_complaint,
            handle_tool_error=True,
        ),
    ]

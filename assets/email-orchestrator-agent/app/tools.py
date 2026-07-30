"""Orchestrator Agent tools — email processing pipeline."""
import json
import logging
import uuid
from typing import Optional

from langchain_core.tools import StructuredTool
from opentelemetry import trace
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

# Financial threshold — write actions above this amount require human approval
FINANCIAL_ACTION_THRESHOLD = 5000.00
# Confidence threshold below which cases go to human review
CONFIDENCE_THRESHOLD = 0.75


# ─── Input schemas ────────────────────────────────────────────────────────────

class ClassifyEmailInput(BaseModel):
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body text")
    case_id: Optional[str] = Field(default=None, description="Case ID if already assigned")


class IdentifyBPInput(BaseModel):
    sender_email: str = Field(description="Sender email address")
    case_id: str = Field(description="Case ID for logging")


class CheckCompletenessInput(BaseModel):
    intent_category: str = Field(description="Classified intent category")
    email_body: str = Field(description="Email body text")
    case_id: str = Field(description="Case ID for logging")


class QueryKBInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID")
    intent_category: str = Field(description="Classified intent category")
    case_id: str = Field(description="Case ID for logging")


class WriteKBInput(BaseModel):
    case_id: str = Field(description="Case ID")
    bp_id: str = Field(description="SAP Business Partner ID")
    intent_category: str = Field(description="Classified intent category")
    routing_path: str = Field(description="Which sub-agent handled the case")
    response_summary: str = Field(description="Summary of the response sent")
    resolution_type: str = Field(description="automated | human_approved | human_overridden | escalated")


class SendEmailInput(BaseModel):
    recipient_email: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body text")
    case_id: str = Field(description="Case ID — required, never send without one")
    channel: str = Field(description="outlook | gmail")


class FlagReviewInput(BaseModel):
    case_id: str = Field(description="Case ID")
    bp_id: str = Field(description="Business Partner ID")
    sender_email: str = Field(description="Sender email")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    intent_category: str = Field(description="Classified intent")
    confidence_score: float = Field(description="AI confidence score")
    draft_response: Optional[str] = Field(default=None, description="Sub-agent draft response if available")
    flagged_reason: str = Field(description="Reason for flagging: low_confidence | high_value | legal_hold | new_partner | sub_agent_failure")
    ai_classification_rationale: Optional[str] = Field(default=None, description="AI classification reasoning")
    knowledge_base_context: Optional[str] = Field(default=None, description="JSON string of KB context used")


class DelegateSubAgentInput(BaseModel):
    sub_agent_name: str = Field(description="ar_agent | ap_agent | treasury_agent | collections_agent | cs_agent")
    case_context: str = Field(description="JSON string of the full case context to pass to the sub-agent")


class DetectLanguageInput(BaseModel):
    text: str = Field(description="Text to detect language for")


class ClarificationInput(BaseModel):
    case_id: str = Field(description="Case ID")
    recipient_email: str = Field(description="Sender email to send clarification to")
    clarification_question: str = Field(description="The question to ask the sender")
    channel: str = Field(description="outlook | gmail")


# ─── Tool implementations ─────────────────────────────────────────────────────

@tracer.start_as_current_span("classify_email_intent")
async def _classify_email_intent(subject: str, body: str, case_id: Optional[str] = None) -> str:
    """Classify email intent using the email-classification runtime skill."""
    if not case_id:
        case_id = str(uuid.uuid4())[:8]

    # This function is called by the LLM which uses the email-classification skill
    # The LLM reads the skill via load_skill tool and applies classification logic
    result = {
        "case_id": case_id,
        "status": "pending_classification",
        "instruction": "Load the email-classification skill (load_skill path='email-classification/SKILL.md') and classify this email. Return: intent_category, confidence_score (0.0-1.0), requires_human_review (bool), summary (2 sentences).",
        "subject": subject,
        "body_preview": body[:500]
    }
    logger.info("M1 classification triggered | case_id=%s | subject=%s", case_id, subject[:80])
    return json.dumps(result)


@tracer.start_as_current_span("identify_business_partner")
async def _identify_bp(sender_email: str, case_id: str) -> str:
    """Identify the SAP business partner from sender email."""
    logger.info("M3 BP identification triggered | case_id=%s | sender=%s", case_id, sender_email)
    return json.dumps({
        "instruction": "Use the SAP Business Partner API MCP tool to look up the business partner by email address. Return: bp_id, bp_name, bp_type (customer|vendor), bp_tier (preferred|standard|at_risk), found (bool), legal_hold_flag, at_risk_flag",
        "sender_email": sender_email,
        "case_id": case_id
    })


@tracer.start_as_current_span("check_information_completeness")
async def _check_completeness(intent_category: str, email_body: str, case_id: str) -> str:
    """Check if email contains all required fields for the given intent."""
    required_fields = {
        "statement_request": [],
        "credit_memo": ["invoice_number_or_amount"],
        "billing_adjustment": ["invoice_number", "disputed_amount"],
        "dispute": ["invoice_number"],
        "follow_up": [],
        "vendor_invoice_status": ["invoice_number_or_po_number"],
        "payment_confirmation": ["invoice_number_or_amount"],
        "payment_terms": [],
        "overdue_followup": [],
        "general_inquiry": []
    }
    fields = required_fields.get(intent_category, [])
    return json.dumps({
        "instruction": f"Check if the email body contains these required fields: {fields}. Return: is_complete (bool), missing_fields (list), clarification_question (pre-drafted question if incomplete)",
        "intent_category": intent_category,
        "required_fields": fields,
        "email_body": email_body[:300],
        "case_id": case_id
    })


@tracer.start_as_current_span("query_knowledge_base")
async def _query_knowledge_base(bp_id: str, intent_category: str, case_id: str) -> str:
    """Query HANA Cloud vector store for BP context and policies."""
    logger.info("M2 KB query triggered | case_id=%s | bp_id=%s | intent=%s", case_id, bp_id, intent_category)
    return json.dumps({
        "instruction": "Use the HANA Cloud knowledge base MCP tool to query prior interaction history and policies. Return: prior_cases_summary (last 5), policy_rules (matching policies), preferred_partner_flag, at_risk_flag, legal_hold_flag",
        "bp_id": bp_id,
        "intent_category": intent_category,
        "case_id": case_id,
        "milestone": "M2"
    })


@tracer.start_as_current_span("write_case_to_knowledge_base")
async def _write_kb(case_id: str, bp_id: str, intent_category: str, routing_path: str, response_summary: str, resolution_type: str) -> str:
    """Write resolved case to HANA Cloud knowledge base."""
    logger.info("M6.achieved: case stored in knowledge base | case_id=%s | partner_id=%s | intent=%s | resolution_type=%s",
                case_id, bp_id, intent_category, resolution_type)
    return json.dumps({
        "instruction": "Use the HANA Cloud knowledge base MCP tool to write this resolved case record.",
        "case_record": {
            "case_id": case_id,
            "bp_id": bp_id,
            "intent_category": intent_category,
            "routing_path": routing_path,
            "response_summary": response_summary,
            "resolution_type": resolution_type
        },
        "milestone": "M6"
    })


@tracer.start_as_current_span("send_email_reply")
async def _send_email(recipient_email: str, subject: str, body: str, case_id: str, channel: str) -> str:
    """Send outbound email reply via Outlook or Gmail."""
    if not case_id:
        return json.dumps({"error": "case_id is required before sending any email"})
    logger.info("M5.achieved: response sent to business partner | case_id=%s | channel=%s", case_id, channel)
    return json.dumps({
        "instruction": f"Use the {channel} MCP tool to send this email reply. Log the send event before dispatching.",
        "recipient_email": recipient_email,
        "subject": subject,
        "body": body,
        "case_id": case_id,
        "channel": channel,
        "milestone": "M5"
    })


@tracer.start_as_current_span("flag_for_human_review")
async def _flag_review(case_id: str, bp_id: str, sender_email: str, subject: str, body: str,
                       intent_category: str, confidence_score: float, flagged_reason: str,
                       draft_response: Optional[str] = None, ai_classification_rationale: Optional[str] = None,
                       knowledge_base_context: Optional[str] = None) -> str:
    """Flag case for human review via the CAP review dashboard."""
    logger.info("Case flagged for review | case_id=%s | reason=%s | confidence=%.2f", case_id, flagged_reason, confidence_score)

    # If in testing mode, actually POST to CAP dashboard
    import os
    if os.getenv('IBD_TESTING') == '1':
        try:
            import httpx
            review_case = {
                "case_id": case_id,
                "bp_id": bp_id,
                "sender_email": sender_email,
                "email_subject": subject,
                "email_body": body,
                "intent_category": intent_category,
                "confidence_score": confidence_score,
                "flagged_reason": flagged_reason,
                "draft_response": draft_response or "",
                "ai_classification_rationale": ai_classification_rationale or "",
                "knowledge_base_context": knowledge_base_context or "{}",
                "status": "pending_review",
                "created_at": "2026-07-22T10:00:00Z"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:4004/api/review/ReviewCases",
                    json=review_case,
                    timeout=10.0
                )

                if response.status_code in [200, 201]:
                    logger.info("Successfully created review case in CAP dashboard | case_id=%s", case_id)
                    return json.dumps({
                        "status": "success",
                        "message": f"Review case created in dashboard | case_id={case_id}",
                        "review_ticket_id": case_id
                    })
                else:
                    logger.warning("Failed to create review case | status=%d | response=%s", response.status_code, response.text[:200])
        except Exception as e:
            logger.error("Error posting to CAP dashboard: %s", str(e))

    return json.dumps({
        "instruction": "Use the review dashboard OData MCP tool to POST a new ReviewCase record with status=pending_review.",
        "review_case": {
            "case_id": case_id,
            "bp_id": bp_id,
            "sender_email": sender_email,
            "email_subject": subject,
            "email_body": body,
            "intent_category": intent_category,
            "confidence_score": confidence_score,
            "flagged_reason": flagged_reason,
            "draft_response": draft_response or "",
            "ai_classification_rationale": ai_classification_rationale or "",
            "knowledge_base_context": knowledge_base_context or "{}"
        }
    })


async def _delegate_sub_agent(sub_agent_name: str, case_context: str) -> str:
    """Delegate case to the correct specialist sub-agent via A2A protocol."""
    logger.info("M4 delegation triggered | sub_agent=%s", sub_agent_name)
    context = json.loads(case_context) if isinstance(case_context, str) else case_context
    return json.dumps({
        "instruction": f"Invoke the {sub_agent_name} via A2A protocol with the case context. The sub-agent will retrieve SAP data and draft a response. Expect back: draft_response, confidence, sap_actions_taken, requires_human_review.",
        "sub_agent": sub_agent_name,
        "case_context": context,
        "milestone": "M4"
    })


async def _detect_language(text: str) -> str:
    """Detect language of incoming email."""
    return json.dumps({
        "instruction": "Detect the language of this text and return an ISO 639-1 language code (e.g. 'en', 'es', 'de', 'fr').",
        "text_preview": text[:200]
    })


@tracer.start_as_current_span("send_clarification_request")
async def _send_clarification(case_id: str, recipient_email: str, clarification_question: str, channel: str) -> str:
    """Send clarification request to business partner when information is missing."""
    logger.info("M3.missed: information gap detected — clarification requested | case_id=%s", case_id)
    return json.dumps({
        "instruction": f"Use the {channel} MCP tool to send this clarification question to the sender. Set case status to pending_clarification.",
        "case_id": case_id,
        "recipient_email": recipient_email,
        "clarification_question": clarification_question,
        "channel": channel
    })


# ─── Tool registry ─────────────────────────────────────────────────────────────

def get_orchestrator_tools() -> list:
    """Return all Orchestrator Agent tools."""
    return [
        StructuredTool(
            name="classify_email_intent",
            description="Classify the intent of an incoming email using the email-classification skill. Returns intent_category, confidence_score, requires_human_review, and summary.",
            args_schema=ClassifyEmailInput,
            coroutine=_classify_email_intent,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="identify_business_partner",
            description="Identify the SAP Business Partner associated with the sender email address. Returns bp_id, bp_name, bp_type, bp_tier, found, legal_hold_flag, at_risk_flag.",
            args_schema=IdentifyBPInput,
            coroutine=_identify_bp,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="check_information_completeness",
            description="Check if the email contains all required information for the given intent category. Returns is_complete, missing_fields, clarification_question.",
            args_schema=CheckCompletenessInput,
            coroutine=_check_completeness,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="query_knowledge_base",
            description="Query the HANA Cloud knowledge base for prior interaction history, policies, and partner flags for a given business partner and intent.",
            args_schema=QueryKBInput,
            coroutine=_query_knowledge_base,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="write_case_to_knowledge_base",
            description="Write a resolved case record to the HANA Cloud knowledge base. Always call this as the final step after every resolved case.",
            args_schema=WriteKBInput,
            coroutine=_write_kb,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="send_email_reply",
            description="Send an outbound email reply to a business partner via Outlook or Gmail. Requires a valid case_id. Never send without a case_id.",
            args_schema=SendEmailInput,
            coroutine=_send_email,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="flag_for_human_review",
            description="Flag a case for human review via the review dashboard. Use when confidence is low, financial threshold is exceeded, legal hold is active, or sub-agent fails.",
            args_schema=FlagReviewInput,
            coroutine=_flag_review,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="delegate_to_sub_agent",
            description="Delegate an email case to the correct specialist sub-agent (ar_agent, ap_agent, treasury_agent, collections_agent, cs_agent) via A2A protocol.",
            args_schema=DelegateSubAgentInput,
            coroutine=_delegate_sub_agent,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="detect_language",
            description="Detect the language of the incoming email body. Returns ISO 639-1 language code.",
            args_schema=DetectLanguageInput,
            coroutine=_detect_language,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="send_clarification_request",
            description="Send a clarification request to the business partner when required information is missing from their email.",
            args_schema=ClarificationInput,
            coroutine=_send_clarification,
            handle_tool_error=True,
        ),
    ]

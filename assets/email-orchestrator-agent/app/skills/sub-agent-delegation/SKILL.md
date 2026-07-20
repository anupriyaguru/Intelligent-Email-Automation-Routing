---
name: sub-agent-delegation
description: A2A protocol contract for communicating with specialist sub-agents
---

# Sub-Agent Delegation Protocol

## Input Schema (Orchestrator → Sub-Agent)

When delegating to a sub-agent, pass the following context object:

```json
{
  "case_id": "string — unique case identifier",
  "intent": "string — one of the 10 intent categories",
  "bp_id": "string — SAP business partner number",
  "bp_name": "string — business partner display name",
  "bp_type": "string — customer | vendor",
  "email_subject": "string — original email subject",
  "email_body": "string — original email body text",
  "knowledge_base_context": {
    "prior_cases_summary": ["list of prior case summaries"],
    "policy_rules": ["list of applicable policy strings"],
    "preferred_partner_flag": "boolean",
    "at_risk_flag": "boolean",
    "legal_hold_flag": "boolean"
  },
  "sap_data_needed": ["list of SAP data types needed, e.g. open_items, dispute_status, invoice_status"]
}
```

## Output Schema (Sub-Agent → Orchestrator)

Sub-agents MUST return a response matching this schema:

```json
{
  "draft_response": "string — the full draft email response text to send to the business partner",
  "confidence": "float 0.0–1.0 — sub-agent's confidence in the response accuracy",
  "sap_actions_taken": ["list of SAP API actions taken, e.g. dispute_case_created, statement_retrieved"],
  "requires_human_review": "boolean — true if human approval is needed before sending",
  "requires_human_review_reason": "string — reason code if requires_human_review is true",
  "sap_data_retrieved": "object — the raw SAP data that was fetched"
}
```

## Confidence Thresholds

- **confidence >= 0.85**: Sub-agent is confident. Orchestrator may send automatically if no other review triggers apply.
- **confidence 0.65–0.84**: Orchestrator should consider flagging for human review unless the intent is routine (statement_request, payment_confirmation).
- **confidence < 0.65**: Sub-agent is uncertain. Always set `requires_human_review: true`.

## Error Handling

If a sub-agent fails to respond or returns an error:
1. Log `M4.missed: sub-agent failed | case_id=[ID] | sub_agent=[name] | reason=[error]`
2. Set `requires_human_review: true` with reason `sub_agent_failure`
3. Route to Human Review Queue with the original email and error details

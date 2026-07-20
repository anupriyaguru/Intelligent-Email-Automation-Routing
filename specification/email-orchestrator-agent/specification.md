# Specification: email-orchestrator-agent

> **Guidelines**: Read [guidelines.md](../guidelines.md) and [guidelines-agent.md](../guidelines-agent.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` for full context on the multi-agent architecture, milestones, routing rules, and SAP API integrations
- [ ] Bootstrap agent code in `assets/email-orchestrator-agent/` using skill `sap-agent-bootstrap` (invoke from inside `assets/email-orchestrator-agent/`, use copy commands — do NOT create files manually)
- [ ] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

- [ ] Create runtime skill `app/skills/email-classification/SKILL.md` with instructions for the Orchestrator to classify email intent (categories: statement_request, credit_memo, billing_adjustment, dispute, follow_up, general_inquiry, vendor_invoice_status, payment_confirmation, payment_terms, overdue_followup). Include confidence scoring guidance and the rule that any confidence below threshold must set `requires_human_review: true`.
- [ ] Create runtime skill `app/skills/knowledge-base-lookup/SKILL.md` with instructions for querying the HANA Cloud vector store: how to form a semantic search query from the business partner ID + intent category, how to interpret prior interaction summaries, how to apply preferred-partner flags, and how to match department policies.
- [ ] Create runtime skill `app/skills/routing-rules/SKILL.md` that defines the full routing decision matrix:
  - `statement_request` → AR Sub-Agent
  - `credit_memo` → AR Sub-Agent
  - `billing_adjustment` → AR Sub-Agent
  - `dispute` → AR Sub-Agent
  - `follow_up` → route based on last case sub-agent, default to Customer Service Sub-Agent
  - `vendor_invoice_status` → AP Sub-Agent
  - `payment_confirmation` → AP Sub-Agent
  - `payment_terms` → Treasury Sub-Agent
  - `overdue_followup` → Collections Sub-Agent
  - `general_inquiry` → Customer Service Sub-Agent
  - Unknown / low confidence → Human Review Queue
- [ ] Create runtime skill `app/skills/response-policy/SKILL.md` with tone and content guidelines for outbound emails: professional tone, always include case reference number, never disclose internal system names, escalation language for high-risk responses, required disclaimer for financial adjustments
- [ ] Create runtime skill `app/skills/sub-agent-delegation/SKILL.md` with the A2A protocol contract for communicating with sub-agents: input schema (case_id, intent, bp_id, email_subject, email_body, knowledge_base_context, sap_data_needed), expected output schema (draft_response, confidence, sap_actions_taken, requires_human_review)

---

## Orchestrator Agent Core Logic

### Email Ingestion Tool
- [ ] Implement tool `poll_outlook_inbox` that connects to Microsoft Outlook/Exchange via Microsoft Graph API (using MCP server) and returns a list of unread emails with: message_id, sender_email, subject, body_text, received_timestamp
- [ ] Implement tool `poll_gmail_inbox` that connects to Gmail via Gmail API (using MCP server) and returns a list of unread emails with: message_id, sender_email, subject, body_text, received_timestamp
- [ ] Implement tool `mark_email_processed` that marks an email as read/processed in the source inbox (Outlook or Gmail) given message_id and source channel
- [ ] Implement tool `send_email_reply` that sends an outbound email reply via the appropriate channel (Outlook or Gmail) given: recipient_email, subject, body, case_id. Logs the send event before dispatching. Never sends without a valid case_id.

### Intent Classification
- [ ] Implement tool `classify_email_intent` that accepts email subject and body text and returns: intent_category (one of the 10 categories defined in the classification runtime skill), confidence_score (0.0–1.0), requires_human_review (bool, true if confidence < threshold), summary (2-sentence plain-language summary of what the sender wants)
- [ ] Define `CONFIDENCE_THRESHOLD` as a plain Python constant (default 0.75) — do NOT use `@agent_config` for this
- [ ] Implement tool `detect_language` that detects the language of the email body and returns an ISO 639-1 language code (e.g. `en`, `es`, `de`)

### Business Partner Identification
- [ ] Implement tool `identify_business_partner` that accepts sender_email and returns: bp_id (SAP business partner number), bp_name, bp_type (customer or vendor), bp_tier (preferred / standard / at_risk), found (bool). Uses the SAP S/4HANA Business Partner API via MCP tool.
- [ ] Implement tool `check_information_completeness` that accepts intent_category and email_body and returns: is_complete (bool), missing_fields (list of field names that are required but absent, e.g. ["invoice_number", "amount"]), clarification_question (pre-drafted question to send back if incomplete)
- [ ] Implement tool `send_clarification_request` that sends a clarification email to the business partner when required information is missing. Stores a "pending_clarification" record in the case log. The case is paused until a reply is received.

### Knowledge Base Integration
- [ ] Implement tool `query_knowledge_base` that accepts bp_id and intent_category and returns: prior_cases_summary (list of last 5 relevant case summaries), policy_rules (list of matching policy strings), preferred_partner_flag (bool), at_risk_flag (bool), legal_hold_flag (bool). Queries HANA Cloud vector store via MCP tool.
- [ ] Implement tool `write_case_to_knowledge_base` that accepts a resolved case record and writes it to the HANA Cloud vector store. Case record includes: case_id, bp_id, intent_category, routing_path, response_summary, resolution_type (automated / human_approved / human_overridden), timestamp, sub_agent_used. This is always the final step of every resolved case.

### Sub-Agent Delegation
- [ ] Implement tool `delegate_to_sub_agent` that accepts: sub_agent_name (ar_agent / ap_agent / treasury_agent / collections_agent / cs_agent), case_context (dict with all case fields). Uses the A2A protocol to invoke the sub-agent. Returns the sub-agent's response including draft_response, confidence, sap_actions_taken, requires_human_review.
- [ ] Implement sub-agent connector classes for each of the five sub-agents: `ARSubAgentConnector`, `APSubAgentConnector`, `TreasurySubAgentConnector`, `CollectionsSubAgentConnector`, `CSSubAgentConnector`. Each implements the same A2A interface contract from the runtime skill.
- [ ] Implement routing logic that maps intent_category → correct sub-agent connector using the routing rules runtime skill. Returns the connector instance.

### Human Review Queue
- [ ] Implement tool `flag_for_human_review` that accepts case_context (including the sub-agent's draft_response if available) and writes a "pending_review" record to the CAP review dashboard's OData service. Returns a review_ticket_id.
- [ ] Implement tool `poll_human_review_decision` that checks the CAP review dashboard for a decision on a given review_ticket_id. Returns: decision (approved / overridden / escalated), reviewer_id, final_response (approved or overridden text), timestamp. Used in async polling loop.

### Orchestrator Main Flow
- [ ] Implement the main Orchestrator flow in `app/agent.py` as `_run_agent(email)` (plain async helper, not a generator) executing the following sequence:
  1. Classify email intent → assign case_id
  2. Query knowledge base with bp_id + intent
  3. Identify business partner from SAP
  4. Check information completeness
  5. If incomplete → send clarification request → pause case → return
  6. If legal_hold_flag or at_risk_flag → immediately flag for human review
  7. Route to correct sub-agent
  8. Receive sub-agent draft response
  9. If requires_human_review (from classification or sub-agent) OR confidence < threshold → flag for human review → poll for decision → use decision response
  10. Apply response policy rules (tone, disclaimer, case reference)
  11. Send email reply to business partner
  12. Write resolved case to knowledge base
- [ ] Implement continuous polling loop in `stream()` that calls `_run_agent()` for each new email from both inboxes, yields progress events, and handles errors gracefully (failed cases go to human review, not silent drop)

---

## Business Step Instrumentation (Milestones)

- [ ] Instrument **M1 — Email Ingested and Intent Classified**: emit `M1.achieved` log after intent classification succeeds with intent category, confidence score, and sender. Emit `M1.missed` on classification failure or timeout. Add OpenTelemetry span `email-ingestion-classification` using decorator on `classify_email_intent`.
- [ ] Instrument **M2 — Knowledge Base Consulted**: emit `M2.achieved` after knowledge base query returns with prior case count and policy match count. Emit `M2.missed` if query fails or returns empty context. Add span `knowledge-base-consultation` using decorator on `query_knowledge_base`.
- [ ] Instrument **M3 — Business Partner Identified and Info Gap Assessed**: emit `M3.achieved` when BP found in S/4HANA and completeness check passes. Emit `M3.missed` with gap details if BP not found or fields missing. Add span `bp-identification-gap-check`.
- [ ] Instrument **M4 — Routed to Sub-Agent and Response Drafted**: emit `M4.achieved` when sub-agent returns draft response with confidence score. Emit `M4.missed` on sub-agent routing failure or timeout. Add span `sub-agent-delegation` using decorator on `delegate_to_sub_agent`.
- [ ] Instrument **M5 — Response Sent to Business Partner**: emit `M5.achieved` after send_email_reply confirms dispatch, including resolution_type (automated / human_approved) and channel (outlook / gmail). Emit `M5.missed` if send fails. Add span `response-dispatch`.
- [ ] Instrument **M6 — Case Stored in Knowledge Base**: emit `M6.achieved` after write_case_to_knowledge_base confirms persistence. Emit `M6.missed` if write fails. Add span `knowledge-base-write` using decorator on `write_case_to_knowledge_base`.
- [ ] Verify `auto_instrument()` is called at top of `main.py` before any AI framework imports

---

## Sub-Agent Implementations

> Each sub-agent is a lightweight Python AI Agent that receives a structured case context from the Orchestrator, retrieves SAP data, and returns a draft response. Each sub-agent is a separate asset that follows the same agent bootstrap pattern.

### AR Sub-Agent (`email-ar-agent`)
- [ ] Bootstrap `assets/email-ar-agent/` using `sap-agent-bootstrap`
- [ ] Implement tool `get_ar_open_items` — retrieves open receivable line items for a given bp_id from SAP S/4HANA AR API via MCP tool. Returns: list of open items with document number, amount, currency, due date, status.
- [ ] Implement tool `get_account_statement` — retrieves a formatted account statement for bp_id covering a specified date range. Returns statement as structured data (line items with dates, amounts, running balance).
- [ ] Implement tool `get_dispute_case_status` — retrieves status of an existing dispute case by dispute_case_id from SAP Dispute Management API (`CE_API_DISPUTE_MANAGE_0001:v1`) via MCP tool.
- [ ] Implement tool `create_dispute_case` — creates a new dispute case in SAP S/4HANA for a given bp_id, amount, and reason code. Returns dispute_case_id. **Requires human approval above financial threshold — tool must check threshold before executing and return `requires_human_review: true` if exceeded.**
- [ ] Implement tool `get_credit_memo_status` — retrieves the status of a credit memo request by credit_memo_id from SAP Credit Memo API (`API_CREDIT_MEMO_REQUEST_SRV:v1`) via MCP tool.
- [ ] Implement tool `create_credit_memo_request` — creates a credit memo request in SAP S/4HANA. **Always requires human approval — tool must always return `requires_human_review: true`.**
- [ ] Implement AR agent `_run_agent()` that: (1) reads case context, (2) fetches relevant SAP data based on intent, (3) drafts a response using the fetched data, (4) returns draft_response, confidence, sap_actions_taken, requires_human_review
- [ ] Instrument AR sub-agent with its own milestone logs: `AR-M1.achieved: ar_data_retrieved`, `AR-M1.missed: ar_data_retrieval_failed`

### AP Sub-Agent (`email-ap-agent`)
- [ ] Bootstrap `assets/email-ap-agent/` using `sap-agent-bootstrap`
- [ ] Implement tool `get_vendor_invoice_status` — retrieves the processing status of a vendor invoice by invoice_id or bp_id from SAP S/4HANA AP API via MCP tool. Returns: invoice_id, amount, currency, posting_date, payment_status, payment_date (if paid).
- [ ] Implement tool `get_purchase_order_status` — retrieves PO status by po_number for a given vendor bp_id. Returns PO details and goods receipt status.
- [ ] Implement tool `get_ap_payment_confirmation` — retrieves proof of payment for a specific invoice. Returns payment document number, bank transfer reference, and amount.
- [ ] Implement AP agent `_run_agent()` that fetches vendor data and drafts response with full invoice/payment details

### Treasury Sub-Agent (`email-treasury-agent`)
- [ ] Bootstrap `assets/email-treasury-agent/` using `sap-agent-bootstrap`
- [ ] Implement tool `get_payment_terms` — retrieves current payment terms for a given bp_id from SAP S/4HANA. Returns: payment_term_code, description, net_days, discount_days, discount_percentage.
- [ ] Implement tool `get_working_capital_info` — retrieves financing and working capital arrangement details for a bp_id. Returns available credit line, outstanding balance, financing terms.
- [ ] Implement Treasury agent `_run_agent()` that looks up payment/financing terms and drafts a clear explanation response

### Collections Sub-Agent (`email-collections-agent`)
- [ ] Bootstrap `assets/email-collections-agent/` using `sap-agent-bootstrap`
- [ ] Implement tool `get_overdue_items` — retrieves all overdue receivable items for bp_id with days overdue, amount, and dunning level from SAP Collections Management API via MCP tool.
- [ ] Implement tool `get_dunning_history` — retrieves the dunning letter history for a given bp_id. Returns list of dunning notices with dates, levels, and amounts.
- [ ] Implement tool `get_payment_arrangement` — retrieves any existing payment plan/arrangement for bp_id. Returns installment schedule if one exists.
- [ ] Implement Collections agent `_run_agent()` that assesses overdue status, references any existing arrangement, and drafts a follow-up or payment plan confirmation response. **Never threatens legal action autonomously — always flags legal escalation for human review.**

### Customer Service Sub-Agent (`email-cs-agent`)
- [ ] Bootstrap `assets/email-cs-agent/` using `sap-agent-bootstrap`
- [ ] Implement tool `get_bp_profile` — retrieves full business partner profile from SAP S/4HANA including contact details, account manager, preferred communication preferences, account status.
- [ ] Implement tool `search_knowledge_base_faq` — searches the knowledge base for FAQ entries and policy documents matching the email topic. Returns top 3 matching policy/FAQ entries.
- [ ] Implement tool `get_prior_case_history` — retrieves the last 10 resolved cases for bp_id from the knowledge base. Returns summaries to provide context continuity.
- [ ] Implement CS agent `_run_agent()` that searches FAQs and prior cases, then drafts a helpful, context-aware response. For unrecognized inquiry types, drafts a "we will review and respond within 1 business day" acknowledgment and flags for human review.

---

## SAP API Integration

- [ ] Confirm that MCP server entries for the following SAP S/4HANA APIs are registered in each sub-agent's `asset.yaml` under `requires`:
  - Dispute Management: `sap.s4:apiResource:CE_API_DISPUTE_MANAGE_0001:v1`
  - Credit Memo Request: `sap.s4:apiResource:API_CREDIT_MEMO_REQUEST_SRV:v1`
  - Business Partner master data API
  - AR/AP open items API
  - Collections Management API
- [ ] Define `FINANCIAL_ACTION_THRESHOLD` as a plain Python constant in each sub-agent that performs write operations (AR, Collections). Default: 5000.00 (USD). Any SAP write action above this amount sets `requires_human_review: true`.
- [ ] Invoke `mcp-translation-file` skill for each API spec in `specification/email-orchestrator-agent/api-specs/` (if available). If skill is unavailable, log `[MCP-SKILL] mcp-translation-file unavailable — skipping` and proceed using MCP tool stubs.
- [ ] After MCP translation files are generated, invoke `setup-solution` to register new MCP server assets
- [ ] Generate `mcp-mock.json` for each agent using `mcp-mock-config` skill (required before tests run)
- [ ] Wire MCP tool loading in each agent's `agent.py` using `get_mcp_tools()` from `mcp_tools.py` — NEVER direct HTTP clients

---

## System Prompt

- [ ] Write the Orchestrator system prompt in `app/agent.py` under `@prompt_section` covering:
  - Role: "You are the Email Orchestration Agent. You coordinate all email processing for customer and vendor communications."
  - You must classify every email, consult the knowledge base, identify the business partner, check information completeness, route to the correct specialist agent, review the specialist's response, apply response policies, and send the reply.
  - You NEVER respond to a business partner without a valid case_id.
  - You NEVER execute financial write operations (credit memos, dispute creation) above the financial threshold without human approval.
  - You NEVER contact a business partner not found in SAP master data without human approval.
  - You always set `top` (or equivalent page-size) to a maximum of 100 on every tool call that accepts it.
  - If you are uncertain about the correct action, flag the case for human review rather than guessing.
  - Do not hallucinate SAP data. Use only data returned by tools.
- [ ] Write a system prompt for each sub-agent scoped to its domain, with the same "no hallucination" and "max top=100" rules, plus domain-specific SAP data instructions

---

## Delete Template Skill

- [ ] Delete the template runtime skill from each agent: `rm -rf assets/email-orchestrator-agent/app/skills/template-skill/ assets/email-ar-agent/app/skills/template-skill/ assets/email-ap-agent/app/skills/template-skill/ assets/email-treasury-agent/app/skills/template-skill/ assets/email-collections-agent/app/skills/template-skill/ assets/email-cs-agent/app/skills/template-skill/`

---

## Testing

- [ ] Install test dependencies: `pip install -r requirements-test.txt` in each agent asset root
- [ ] Write unit test for `classify_email_intent` — mock LLM, test with sample emails for each of the 10 intent categories, verify correct category and confidence score returned
- [ ] Write unit test for `identify_business_partner` — mock MCP S/4HANA tool, test found and not-found cases
- [ ] Write unit test for `check_information_completeness` — test each intent category with complete and incomplete email bodies
- [ ] Write unit test for `query_knowledge_base` — mock HANA Cloud MCP tool, verify prior case summaries and policy rules returned correctly
- [ ] Write unit test for `delegate_to_sub_agent` — mock sub-agent A2A connector, verify correct sub-agent selected for each intent category
- [ ] Write unit test for `send_email_reply` — mock Outlook/Gmail MCP tools, verify email is sent and case_id is always included
- [ ] Write unit test for `write_case_to_knowledge_base` — mock HANA Cloud write MCP tool, verify all required fields are persisted
- [ ] Write unit test for `flag_for_human_review` — mock CAP review dashboard OData call, verify pending_review record written
- [ ] Write unit tests for each sub-agent tool (one per tool): mock SAP MCP calls, verify correct data shape returned
- [ ] Write one integration test per agent: end-to-end flow with real LLM mocked, mock all MCP tools, simulate an email through the full pipeline and verify correct milestone logs emitted, correct sub-agent called, and response sent
- [ ] Run `pytest` from each agent asset root (no args) — fix failures before proceeding
- [ ] Ensure coverage ≥ 70% across all agent assets; add targeted tests if below threshold
- [ ] Run final `pytest` (no args) from each agent asset root to produce `test_report.json`
- [ ] Verify `test_report.json` exists in each agent asset root

---

## Validation

- [ ] Run `grep -r "M[0-9]\.achieved" assets/email-orchestrator-agent/app/` — must return results for all 6 milestones
- [ ] Run `grep -r "sap_cloud_sdk.agent_decorators" assets/email-orchestrator-agent/app/` — must return results
- [ ] Run `grep -c "^@agent_model\|^@agent_config\|^@prompt_section" assets/email-orchestrator-agent/app/agent.py` — must return exactly 3
- [ ] Run the same decorator check on each sub-agent's `agent.py`
- [ ] Verify `test_report.json` exists in all 6 agent asset roots

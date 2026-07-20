# Product Requirements Document (PRD)

**Title:** Intelligent Email Automation & Routing — Multi-Agent Orchestration Platform  
**Date:** 2026-07-06  
**Owner:** Finance / Customer Service Operations  
**Solution Category:** AI Agent, BTP Extension

---

## Product Purpose & Value Proposition

**Elevator Pitch:**  
Every month, 10,000 emails from customers and vendors pile up in shared inboxes. Staff spend their days manually reading, sorting, and forwarding them — while business partners wait for answers. This platform puts an Orchestrator Agent in charge: it reads every email, understands what is being asked, consults a living knowledge base, dispatches it to the right specialist agent (AR, AP, Treasury, Collections, Customer Service), and sends a professional response back — all automatically, and continuously getting smarter with every case it resolves.

**Business Need:**  
There is no scalable, intelligent mechanism to handle high-volume inbound business partner email. Manual triage is slow, inconsistent, and costly. Emails get misrouted, responses are delayed, and institutional knowledge about preferred partners and department policies lives only in people's heads. A system that reads, learns, routes, responds, and remembers is required.

**Expected Value:**

- Eliminate manual email triage for routine requests (target: 80%+ fully automated)
- Reduce average email response time from hours/days to minutes
- Improve routing accuracy and response consistency across all departments
- Build a reusable knowledge base that captures every business partner interaction, policy, and resolution for future use

**Product Objectives (Prioritized):**

1. Automate at least 80% of incoming emails end-to-end without human involvement
2. Achieve 90%+ intent classification accuracy across all email categories
3. Route each email to the correct department sub-agent within seconds of receipt
4. Respond to the business partner with an acknowledgment in under 2 minutes
5. Store every resolved case in the knowledge base so the system continuously improves

---

## User Profiles & Personas

### Primary Persona: Maria — AR/Collections Specialist

Maria is a 34-year-old Accounts Receivable specialist who manages overdue accounts and handles a large share of the incoming email volume. She spends 3–4 hours per day reading emails, copying data from SAP, drafting replies, and forwarding threads to the right people. She knows her customers well and is frustrated that her time is consumed by routine requests (statement copies, payment confirmation, credit memo status) that she feels a computer could handle. She wants to spend her time on the genuinely complex cases that need her judgment — not on repetitive inbox triage. She needs the system to handle the routine, surface the complex, and not embarrass her in front of long-standing customers.

### Secondary Persona: James — Finance Operations Manager

James is a 44-year-old Finance Operations Manager responsible for AR, AP, and Treasury. He does not work in the inbox directly, but he owns the SLA commitments to business partners and the operational cost of the team. He is frustrated by inconsistent response quality, missed SLAs, and the inability to report on email volume trends. He needs visibility into how many emails are coming in, how they are being handled, who is being escalated to, and how quickly cases are resolved. He is the primary sponsor of this project and will measure success by headcount reallocation and partner satisfaction scores.

### Secondary Persona: Rosa — Customer Service Representative

Rosa is a 28-year-old Customer Service rep who handles general vendor and customer inquiries that do not fit neatly into Finance buckets. She often receives emails forwarded to her by other teams, sometimes with no context. She is comfortable with technology and open to AI tools, but she needs to trust that the AI has done its homework — she does not want to send a response that contradicts what a colleague already said. Her key need is context: when an email lands in her queue, she wants to see everything the system already knows about that business partner.

### Other User Types

- **AP Specialist** — handles vendor payment status, invoice disputes, purchase order inquiries
- **Treasury Analyst** — handles payment terms, financing inquiries, working capital questions
- **IT Administrator** — manages system configuration, email connector credentials, and agent model updates

---

## User Goals & Tasks

### For Maria (AR/Collections Specialist):

**Goals:**
- Spend time on complex disputes and collections strategies, not routine email triage
- Trust that routine emails (statement requests, payment confirmations) are handled accurately and promptly
- Review and approve flagged complex emails quickly, with full context available

**Key Tasks:**
- Review the human review queue for flagged emails each morning
- Approve, override, or escalate AI-drafted responses for complex cases
- Access the full interaction history of any business partner from the review dashboard

### For James (Finance Operations Manager):

**Goals:**
- Have real-time visibility into email volume, routing accuracy, and resolution speed
- Report on SLA compliance and automation rate to leadership
- Trust that the system respects department policies and preferred partner protocols

**Key Tasks:**
- Monitor the operations dashboard for email volume, automation rate, and escalation trends
- Review and update routing rules, department policies, and preferred partner lists
- Approve threshold settings for what qualifies as "complex" (requiring human review)

---

## Product Principles

1. **Orchestrator as single source of truth**: All email handling flows through the Orchestrator Agent. No sub-agent communicates directly with a business partner — all outbound responses are reviewed and sent by the Orchestrator.
2. **Human-in-the-loop for high-risk actions**: The system escalates rather than guesses. Credit adjustments above a defined threshold, disputed amounts, and unfamiliar sender profiles always require human approval before action.
3. **Knowledge compounds over time**: Every resolved case makes the system smarter. Routing decisions, response templates, partner preferences, and policy exceptions are written back to the knowledge base after every interaction.
4. **Transparency for the reviewer**: When a human reviews a flagged email, they see everything the AI saw — the email, the classification rationale, the knowledge base context, the sub-agent's proposed response — so they can make a fast, informed decision.
5. **Data stays within SAP BTP**: All AI processing, knowledge storage, and case logging runs on SAP BTP using SAP AI Core and HANA Cloud. No business partner data leaves the SAP ecosystem.

---

## Business Context

**Current State:**  
Incoming emails from customers and vendors are received in shared Outlook and Gmail inboxes. Staff manually read each email, determine the topic, look up relevant data in SAP S/4HANA, draft a response, and forward the thread to the appropriate team. This process is entirely manual, takes hours per email in some cases, and results in inconsistent response quality and frequent misrouting.

**Strategic Alignment:**  
This platform directly supports the company's Lead to Cash process efficiency goals, specifically reducing operational cost in AR/AP, improving business partner experience, and enabling the finance team to operate at higher volume without proportional headcount growth.

**Success Criteria:**

- 80% of incoming emails fully resolved without human intervention within 90 days of go-live
- Average response time to business partner reduced to under 2 minutes for automated cases
- Routing accuracy of 90% or above (measured by human reviewer override rate)
- Knowledge base populated with all prior interaction history and active policies before go-live

---

## Goals and Non-Goals

### Goals (In Scope)

- Ingest emails from Microsoft Outlook/Exchange and Gmail/Google Workspace
- Classify email intent from subject line and body using AI (SAP AI Core)
- Consult a knowledge base of prior interactions, business partner profiles, and department policies before routing
- Identify the business partner (customer or vendor) and assess whether all required information is present
- Route each email to the correct specialist sub-agent (AR, AP, Treasury, Collections, Customer Service)
- Have the sub-agent retrieve live data from SAP S/4HANA and compose a response
- Send a final, policy-compliant response to the business partner via email
- Flag low-confidence or high-risk cases to a human review queue before responding
- Store resolved case details back into the knowledge base after every interaction
- Provide a human review dashboard (BTP Extension) for flagged cases

### Non-Goals (Out of Scope)

- Processing inbound phone calls or chat messages (email only in this release)
- Replacing SAP S/4HANA as the financial system of record — the agents read and write via APIs only
- Autonomous approval of credit adjustments above the defined financial threshold without human sign-off
- Training or fine-tuning the underlying LLM models — the system uses SAP AI Core foundation models as-is
- Integration with external CRM systems (scoped for a future release)

---

## Requirements

### Must-Have Requirements

**REQ-01**: Email Ingestion from Outlook and Gmail

- **Problem to Solve**: Emails arrive in two separate inboxes (Outlook and Gmail) and must be captured in one system for processing.
- **User Story**: As the Orchestrator Agent, I need to continuously poll both Outlook/Exchange and Gmail inboxes so that no incoming email is missed regardless of which platform the business partner uses.
- **Acceptance Criteria**:
  - Given a new email arrives in either inbox, when the polling cycle runs, then the email (subject, body, sender, timestamp) is captured and passed to the Orchestrator Agent within 2 minutes.
- **Maps to Objective**: Objective 1 — Automate 80%+ of emails end-to-end
- **Priority Rank**: 1

**REQ-02**: Intent Classification

- **Problem to Solve**: The system must understand what each email is asking for before it can act.
- **User Story**: As the Orchestrator Agent, I need to read the email subject and body and classify the intent (statement request, credit memo, adjustment, dispute, follow-up, general inquiry) so that I can route it correctly.
- **Acceptance Criteria**:
  - Given an incoming email, when the Orchestrator Agent processes it, then an intent category and confidence score are assigned.
  - Given a confidence score below the defined threshold, when the email is classified, then it is immediately flagged for human review rather than auto-routed.
- **Maps to Objective**: Objective 2 — 90%+ classification accuracy
- **Priority Rank**: 2

**REQ-03**: Knowledge Base Consultation

- **Problem to Solve**: Without context about prior interactions, preferred partner status, and active policies, the system cannot make informed routing or response decisions.
- **User Story**: As the Orchestrator Agent, I need to query the knowledge base for this business partner's history, preferred status flags, and applicable department policies before routing so that my decisions are contextually informed.
- **Acceptance Criteria**:
  - Given a classified email with an identified business partner, when the Orchestrator queries the knowledge base, then it receives prior interaction summaries, partner tier/preference flags, and matching policy rules.
  - Given a business partner with no prior history, when the knowledge base is queried, then the Orchestrator proceeds with default policies and flags the case as a new partner.
- **Maps to Objective**: Objective 2 and Objective 5
- **Priority Rank**: 3

**REQ-04**: Business Partner Identification and Information Gap Detection

- **Problem to Solve**: Some emails arrive without enough information to act on (missing invoice number, account ID, etc.). Acting on incomplete information produces incorrect responses.
- **User Story**: As the Orchestrator Agent, I need to identify the business partner from SAP S/4HANA master data and assess whether the email contains enough information to proceed so that I only route complete requests.
- **Acceptance Criteria**:
  - Given an email with sufficient information, when the business partner is identified, then the case proceeds to sub-agent routing.
  - Given an email with missing required information, when the gap is detected, then the Orchestrator sends an automated clarification request to the sender and pauses the case pending their reply.
- **Maps to Objective**: Objective 1 and Objective 4
- **Priority Rank**: 4

**REQ-05**: Sub-Agent Routing and SAP Data Retrieval

- **Problem to Solve**: Each email type requires domain expertise and access to specific SAP S/4HANA data. A single agent cannot specialize in all domains simultaneously.
- **User Story**: As the Orchestrator Agent, I need to delegate each classified email to the appropriate specialist sub-agent (AR, AP, Treasury, Collections, Customer Service) so that the response is accurate, domain-specific, and backed by live SAP data.
- **Acceptance Criteria**:
  - Given a classified and complete email, when the Orchestrator routes it, then the correct sub-agent receives the case.
  - Given a routed case, when the sub-agent processes it, then it retrieves the relevant SAP S/4HANA data (open items, dispute status, credit memo records) via standard APIs and composes a draft response.
  - Given a sub-agent draft response, when it is returned to the Orchestrator, then the Orchestrator reviews it for policy compliance before sending.
- **Maps to Objective**: Objective 3 — Route to correct sub-agent within seconds
- **Priority Rank**: 5

**REQ-06**: Automated Response to Business Partner

- **Problem to Solve**: Business partners currently wait hours or days for a reply. They need immediate acknowledgment and, where possible, a complete answer.
- **User Story**: As a customer or vendor, I need to receive a prompt, professional, and accurate response to my email so that I can trust my inquiry is being handled.
- **Acceptance Criteria**:
  - Given an automated case, when the Orchestrator approves the sub-agent response, then a reply is sent to the business partner within 2 minutes of the email being received.
  - Given a human-review case, when the reviewer approves the response, then the reply is sent immediately upon approval.
- **Maps to Objective**: Objective 4 — Respond within 2 minutes
- **Priority Rank**: 6

**REQ-07**: Human Review Queue and Dashboard

- **Problem to Solve**: The system cannot autonomously handle all emails. Low-confidence, high-risk, or policy-sensitive emails need a human decision before a response is sent.
- **User Story**: As Maria (AR Specialist), I need a review queue where I can see flagged emails with full AI context so that I can approve, override, or escalate quickly and confidently.
- **Acceptance Criteria**:
  - Given a flagged email, when a reviewer opens it in the dashboard, then they see the original email, the AI's classification rationale, the knowledge base context used, and the sub-agent's proposed response.
  - Given a reviewer action (approve / override / escalate), when it is submitted, then the response is sent (or escalated) and the case is logged.
- **Maps to Objective**: Objective 1 — Human safety net for the 20% that cannot be automated
- **Priority Rank**: 7

**REQ-08**: Case Storage and Knowledge Base Update

- **Problem to Solve**: Without writing resolved cases back to the knowledge base, the system cannot learn from experience and will repeat the same mistakes.
- **User Story**: As the Orchestrator Agent, I need to write every resolved case (intent, routing decision, response, reviewer action, outcome) back to the knowledge base so that future emails from the same business partner are handled with better context.
- **Acceptance Criteria**:
  - Given a resolved case, when the response is sent, then the case record is written to the knowledge base including: sender ID, intent category, routing path, response summary, resolution type (automated / human-approved), and timestamp.
  - Given a human override, when the reviewer submits a correction, then the correct routing and response are stored as a learning signal.
- **Maps to Objective**: Objective 5 — Continuously improve
- **Priority Rank**: 8

### High-Want Requirements

**REQ-09**: Preferred Business Partner Handling

- **Problem to Solve**: High-value customers and preferred vendors should receive prioritized, elevated-tone responses.
- **User Story**: As James (Finance Manager), I need preferred partner flags to influence response priority and tone so that our most important relationships receive appropriate attention.
- **Priority Rank**: 1

**REQ-10**: Operations Dashboard for Management

- **Problem to Solve**: James cannot currently report on email volume, automation rate, or SLA compliance.
- **User Story**: As James, I need a management dashboard showing daily email volume, automation rate, average response time, routing accuracy, and escalation count so that I can report on operational performance.
- **Priority Rank**: 2

### Nice-to-Have Requirements

**REQ-11**: Multi-language Email Support

- **Problem to Solve**: Some business partners communicate in languages other than English.
- **User Story**: As the Orchestrator Agent, I need to detect the language of the incoming email and respond in the same language so that non-English business partners receive appropriate service.
- **Priority Rank**: 1

---

## Non-Functional Requirements

### Performance

- **Latency**: Automated response sent to business partner within 2 minutes of email receipt (95th percentile)
- **Throughput**: System must handle up to 500 emails per day (approximately 10,000/month) without degradation

### Reliability

- **Availability**: 99.5% uptime during business hours; graceful degradation (queue and retry) outside business hours
- **Fallback**: If AI classification fails, email is automatically routed to the human review queue rather than dropped

### Cost

- **Budget Controls**: SAP AI Core token usage monitored per sub-agent; alerts triggered if daily usage exceeds defined threshold
- **Optimization**: Knowledge base query results cached per business partner session to reduce redundant lookups

### Explainability

- **Traceability**: Every routing decision is logged with the classification rationale and knowledge base context used
- **Decision Logging**: All Orchestrator decisions (route, clarify, escalate, respond) are stored in the case log with timestamps
- **Uncertainty Communication**: Confidence score is displayed to human reviewers for every flagged case

---

## Solution Architecture

**Architecture Overview:**  
A multi-agent platform deployed on SAP BTP. The Orchestrator Agent is the central Python-based AI agent that manages the full email lifecycle. It delegates to five specialized sub-agents, each backed by SAP S/4HANA Cloud (Private Edition) APIs. A HANA Cloud vector store serves as the shared knowledge base. A React + CAP web application serves as the human review dashboard. Email I/O is handled via Outlook and Gmail API connectors.

**Key Components:**

- **Orchestrator Agent** (Python, SAP AI Core): Central coordinator — ingests emails, classifies intent, queries knowledge base, routes to sub-agents, sends responses, writes cases back to knowledge base
- **AR Sub-Agent** (Python, SAP AI Core): Handles account statements, open item lookups, dispute case creation and status, credit memo requests
- **AP Sub-Agent** (Python, SAP AI Core): Handles vendor invoice status, payment confirmations, purchase order inquiries
- **Treasury Sub-Agent** (Python, SAP AI Core): Handles payment terms inquiries, financing questions, working capital communications
- **Collections Sub-Agent** (Python, SAP AI Core): Handles overdue account follow-ups, payment arrangement communications, dunning responses
- **Customer Service Sub-Agent** (Python, SAP AI Core): Handles general inquiries, complaints, policy questions, and anything that does not fit a finance-specific bucket
- **Knowledge Base** (SAP HANA Cloud — vector store): Stores prior interaction history, business partner profiles, preferred partner flags, department policies, and resolved case learnings
- **Human Review Dashboard** (SAP BTP — CAP backend + React frontend): Web application for reviewing flagged cases, approving/overriding AI responses, and monitoring operations
- **Email Connectors**: Outlook/Exchange API and Gmail API for reading inbound and sending outbound emails

**Integration Points:**

- **SAP S/4HANA Cloud (Private Edition)**: Each sub-agent connects via standard APIs — Dispute Management (`CE_API_DISPUTE_MANAGE_0001:v1`), Credit Memo Request (`API_CREDIT_MEMO_REQUEST_SRV:v1`), AR/AP open item queries, Collections Management — read and write, real-time
- **Microsoft Outlook/Exchange**: Inbound email polling and outbound reply sending — via Microsoft Graph API
- **Gmail/Google Workspace**: Inbound email polling and outbound reply sending — via Gmail REST API
- **SAP AI Core**: LLM inference for intent classification, response drafting, and reasoning across all agents

**Deployment Environments:**

- **Dev**: Full environment with synthetic business partner data; used for agent development and unit testing
- **QA**: Connected to S/4HANA sandbox; used for integration and routing accuracy testing with anonymized real emails
- **Prod**: Live S/4HANA Private Edition; email connectors active; human review queue live before full automation is enabled

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
- The Orchestrator Agent is designed with an open sub-agent registry — new specialist agents (e.g., Legal Agent, HR Agent, Procurement Agent) can be added without modifying the Orchestrator's core routing logic
- Each sub-agent exposes a standardized interface (input: case context; output: proposed response + confidence score) so new agents can be plugged in by implementing this contract
- Department routing rules and preferred partner policies are stored in the knowledge base (not hardcoded) and can be updated by authorized users without a code deployment
- The human review dashboard allows business users to add new intent categories and routing rules through configuration, reducing dependency on engineering for policy changes

**Business Step Instrumentation:**
- All six key milestones (see Milestones section) emit structured log statements upon achievement and upon miss/skip
- The Orchestrator Agent emits a log entry at every routing decision, knowledge base query, and sub-agent delegation
- Each sub-agent emits logs on: data retrieval from S/4HANA (success/failure), response draft completion, and confidence score
- All logs include: case ID, business partner ID, timestamp, milestone ID, and event type (achieved / missed / error)
- Log pattern: `[MILESTONE_ID].[achieved|missed]: [description] | case_id=[ID] | partner_id=[ID]`

### Automation & Agent Behaviour

**Automation Level:** Autonomous multi-agent / Hybrid (human-in-the-loop for high-risk cases)

**Actions the system performs without human approval:**
- Classify email intent and assign confidence score
- Query knowledge base and identify business partner
- Send clarification request to business partner when information is missing
- Route case to the appropriate sub-agent
- Retrieve live data from SAP S/4HANA via APIs
- Send automated response to business partner (for high-confidence, routine cases)
- Write resolved case to knowledge base

**Actions that require human review or approval:**
- Any response where the AI confidence score falls below the defined threshold
- Any case involving a credit adjustment, financial write-off, or dispute above the defined monetary threshold
- Any email from a new/unrecognized business partner not found in SAP master data
- Any response that modifies SAP financial records (credit memos, dispute case creation) above the threshold
- Any case flagged as sensitive by the knowledge base (e.g., partner marked as "at-risk" or "legal hold")

**Model or engine used:** SAP Generative AI Hub (GPT-4o or equivalent) via SAP AI Core, deployed on SAP BTP

**Knowledge & data sources accessed:**

- SAP HANA Cloud (vector store): Prior interaction history, partner profiles, policies — read and write
- SAP S/4HANA Cloud (Private Edition): AR open items, AP invoices, dispute cases, credit memos, collections — read and write via APIs
- Inbound email content (Outlook + Gmail): Read only at ingestion; Orchestrator sends outbound replies

**Tools or connectors invoked:**

- Outlook/Exchange API: Read inbound emails, send outbound replies (write)
- Gmail API: Read inbound emails, send outbound replies (write)
- SAP AI Core (LLM inference): Intent classification, response drafting (stateless read)
- SAP HANA Cloud (vector store): Knowledge base queries and case write-back (read/write)
- SAP S/4HANA Dispute API (`CE_API_DISPUTE_MANAGE_0001:v1`): Create/read dispute cases (read/write — **high-risk above threshold**)
- SAP S/4HANA Credit Memo API (`API_CREDIT_MEMO_REQUEST_SRV:v1`): Create credit memo requests (write — **high-risk, requires human approval**)
- SAP S/4HANA AR/AP/Collections APIs: Read open items, payment status, collections data (read-only)

**Guardrails & fail-safes:**

- The Orchestrator never sends a financial-modification response (credit memo, write-off, dispute creation) without sub-agent confidence above the defined threshold AND a human reviewer approval
- If the AI classification confidence is below threshold, the case is routed to the human review queue — never auto-responded
- If an SAP API call fails, the case is paused and the reviewer is notified rather than silently dropped
- The system never responds to an unrecognized sender (not in SAP BP master data) without human approval
- All outbound emails are logged before being sent; no email is sent without a case record being created first
- Monetary thresholds for automated action are configurable by the Finance Manager from the dashboard

### Configuration & Data

**Configuration Scope:**  
Email connector credentials (Outlook and Gmail), SAP AI Core model endpoints, SAP S/4HANA API credentials, monetary thresholds for automated action, confidence score thresholds, sub-agent routing rules, and department policy documents must all be configured before go-live.

**Organisational & Master Data:**

- Business partner master data from SAP S/4HANA (customers and vendors) must be accessible to the Orchestrator for BP identification
- Preferred partner lists and partner tier flags must be loaded into the knowledge base as part of the initial seeding exercise
- Department routing rules and email response policy templates must be authored and loaded into the knowledge base before go-live

**Data Migration & Cutover:**

- Historical email interaction data (past 12–24 months) should be summarized and loaded into the knowledge base as the initial training corpus; data cleansing and summarization is owned by the AR/AP team leads
- Cutover plan: run in shadow mode (classify and route but do not send) for 2 weeks in QA; enable automated sending for low-risk categories first; expand to full automation over 4 weeks

---

## Governance, Risk & Compliance

**Data Handling:**

- All email content and business partner data is processed and stored within SAP BTP (HANA Cloud); no data is sent to external AI services outside the SAP AI Core boundary
- Business partner PII (names, email addresses, account numbers) is stored in the knowledge base only in encrypted form
- Emails older than the defined retention period are purged from the knowledge base per company data retention policy

**Approval Flows:**

- Credit memo creation and dispute case creation above the financial threshold require a Finance Specialist approval via the review dashboard before the SAP API write is executed
- New routing rules and policy updates require Finance Manager approval before they are activated in the knowledge base

---

## Milestones

### M1: Email Ingested and Intent Classified

- **Description**: The Orchestrator Agent has received the email and successfully determined its intent and assigned a confidence score.
- **Achieved when**: An intent category and confidence score have been assigned to the incoming email.
- **Log on achievement**: `M1.achieved: email ingested and intent classified | case_id=[ID] | intent=[category] | confidence=[score] | partner=[sender]`
- **Log on miss**: `M1.missed: intent classification failed or timed out | case_id=[ID] | partner=[sender] | reason=[error]`

### M2: Knowledge Base Consulted and Context Loaded

- **Description**: The Orchestrator has queried the knowledge base and loaded prior interaction history, partner profile, and applicable policies into the case context.
- **Achieved when**: Knowledge base query returns results (or confirms new partner status) and context is attached to the case.
- **Log on achievement**: `M2.achieved: knowledge base consulted | case_id=[ID] | partner_id=[ID] | prior_cases=[count] | policy_matches=[count]`
- **Log on miss**: `M2.missed: knowledge base query failed or returned no context | case_id=[ID] | partner_id=[ID] | reason=[error]`

### M3: Business Partner Identified and Information Gap Assessed

- **Description**: The Orchestrator has matched the sender to a SAP business partner record and determined whether all required information is present to proceed.
- **Achieved when**: BP match confirmed in S/4HANA master data and information completeness check passes.
- **Log on achievement**: `M3.achieved: BP identified and case is complete | case_id=[ID] | bp_id=[ID] | gap_detected=false`
- **Log on miss**: `M3.missed: BP not found or information gap detected | case_id=[ID] | partner=[sender] | gap=[missing_fields]`

### M4: Routed to Sub-Agent and Response Drafted

- **Description**: The Orchestrator has delegated the case to the correct specialist sub-agent, the sub-agent has retrieved live SAP data, and a draft response has been returned to the Orchestrator.
- **Achieved when**: Sub-agent returns a draft response with confidence score to the Orchestrator.
- **Log on achievement**: `M4.achieved: sub-agent response received | case_id=[ID] | sub_agent=[name] | confidence=[score]`
- **Log on miss**: `M4.missed: sub-agent routing failed or response not received | case_id=[ID] | sub_agent=[name] | reason=[error]`

### M5: Response Sent to Business Partner

- **Description**: The final response has been sent to the business partner — either automatically (high confidence) or after human approval.
- **Achieved when**: Outbound email is confirmed sent via Outlook or Gmail API.
- **Log on achievement**: `M5.achieved: response sent to business partner | case_id=[ID] | partner_id=[ID] | resolution_type=[automated|human_approved] | channel=[outlook|gmail]`
- **Log on miss**: `M5.missed: response send failed | case_id=[ID] | partner_id=[ID] | reason=[error]`

### M6: Case Stored in Knowledge Base

- **Description**: The full resolved case record has been written back to the knowledge base for future learning.
- **Achieved when**: Case record (intent, routing, response, resolution type, timestamp) is confirmed written to HANA Cloud vector store.
- **Log on achievement**: `M6.achieved: case stored in knowledge base | case_id=[ID] | partner_id=[ID] | intent=[category] | resolution_type=[automated|human_approved]`
- **Log on miss**: `M6.missed: case storage failed | case_id=[ID] | partner_id=[ID] | reason=[error]`

---

## Risks, Assumptions, and Dependencies

### Risks

- **Knowledge base cold start**: The system's effectiveness depends on having quality seed data (prior emails, policies, partner lists). Without this, early routing accuracy will be lower. Mitigation: dedicate 2–3 weeks before go-live to data preparation.
- **S/4HANA data quality**: If business partner master data is incomplete or inconsistent, the BP identification step will fail more often, increasing human review load. Mitigation: run a BP data quality check as a pre-condition for go-live.
- **AI model accuracy on edge cases**: LLM classification may perform poorly on unusual email types not well represented in the knowledge base. Mitigation: shadow mode testing period before full automation is enabled.
- **Email connector authentication**: OAuth credentials for Outlook and Gmail require IT approval and periodic renewal. Mitigation: credential rotation automation must be built into the deployment.

### Assumptions (Validate These)

- SAP S/4HANA Cloud (Private Edition) APIs for AR, AP, Dispute, Credit Memo, and Collections are accessible from SAP BTP via standard connectivity
- The company has an active SAP AI Core subscription on SAP BTP
- SAP HANA Cloud (with vector engine enabled) is available or can be provisioned on the company's BTP subaccount
- The Finance Manager has authority to define and approve the monetary thresholds for automated action
- Historical email data is available and can be processed for knowledge base seeding

### Dependencies

- SAP BTP subaccount with AI Core, HANA Cloud, and Cloud Foundry runtime provisioned
- SAP S/4HANA Cloud (Private Edition) API credentials and connectivity (SAP BTP connectivity service or SAP Integration Suite)
- Microsoft Graph API access (Outlook connector) — requires IT/Azure AD approval
- Gmail API access — requires IT/Google Workspace admin approval
- Initial knowledge base seeding — depends on AR/AP team leads to prepare historical interaction summaries and policy documents

---

## Open Questions

- What is the company's defined monetary threshold above which automated financial actions (credit memos, dispute creation) require human approval?
- What is the acceptable confidence score threshold below which the system should escalate to human review?
- Should the system handle emails in languages other than English in the initial release, or is that deferred?
- What is the data retention policy for email content and case records in the knowledge base?
- Which team owns the knowledge base content (policies, routing rules, preferred partner lists) on an ongoing basis?

---

## Appendix

### Glossary

- **Orchestrator Agent**: The central AI agent that coordinates all email processing from ingestion to resolution
- **Sub-Agent**: A specialized AI agent with domain expertise in one area (AR, AP, Treasury, Collections, Customer Service)
- **Knowledge Base**: A vector-indexed database (HANA Cloud) storing prior interactions, business partner profiles, and department policies
- **Business Partner (BP)**: A customer or vendor who communicates via email
- **Human Review Queue**: The dashboard interface where human agents review and approve AI-flagged cases
- **Intent Classification**: The AI process of determining what a business partner is asking for from the email subject and body
- **Confidence Score**: A numerical value (0–1) representing how certain the AI is about its classification or response quality

### References

- SAP AI Core documentation: https://help.sap.com/docs/sap-ai-core
- SAP HANA Cloud Vector Engine: https://help.sap.com/docs/hana-cloud
- SAP S/4HANA Dispute Management API: `sap.s4:apiResource:CE_API_DISPUTE_MANAGE_0001:v1`
- SAP S/4HANA Credit Memo Request API: `sap.s4:apiResource:API_CREDIT_MEMO_REQUEST_SRV:v1`
- SAP BTP Cloud Foundry Runtime: https://help.sap.com/docs/btp

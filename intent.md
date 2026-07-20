# Intelligent Email Automation & Routing — Multi-Agent Orchestration

AI-powered multi-agent system with a central Orchestrator Agent that coordinates specialized sub-agents (AR, AP, Treasury, Collections, Customer Service) to process 10,000+ monthly customer and vendor emails end-to-end, with a shared knowledge base that learns from every interaction.

## Business challenge

The company receives approximately 10,000 emails per month from customers and vendors covering a wide variety of topics — account statements, follow-ups on prior emails, credit memos, billing adjustments, disputes, and general inquiries. These emails arrive across both Microsoft Outlook/Exchange and Gmail/Google Workspace. Currently, staff must manually read, categorize, and forward each email to the right department. This is time-consuming, error-prone, and creates delays in response time.

The business needs a multi-agent system led by a central Orchestrator Agent that:
1. Scans each incoming email and understands its intent (subject + full body)
2. Consults a living knowledge base — prior interactions, preferred customer/vendor lists, department policies
3. Categorizes the request by business partner and determines whether additional information is needed before acting
4. Routes the email to the correct specialized sub-agent (AR, AP, Treasury, Collections, Customer Service), gathers the sub-agent's response, and sends a final reply to the business partner
5. Stores all case details back into the knowledge base so the system continuously learns and improves

All information flows back to the Orchestrator Agent, which maintains full visibility and control over every case from first email to resolution.

## Key Milestones

1. **Email Ingested & Intent Understood** — Orchestrator Agent reads incoming email (subject + body), understands intent, and assigns a preliminary request type (statement, credit memo, adjustment, dispute, follow-up, general inquiry).
2. **Knowledge Base Consulted** — Orchestrator queries the knowledge base for prior interactions with this business partner, applicable customer/vendor policies, and preferred-partner flags to enrich its context.
3. **Business Partner Categorized & Info Gap Assessed** — Orchestrator identifies the business partner (customer or vendor), assesses whether all required information is present, and — if not — sends a clarification request back to the sender before proceeding.
4. **Sub-Agent Routed & Response Gathered** — Orchestrator delegates the case to the appropriate sub-agent (AR Agent, AP Agent, Treasury Agent, Collections Agent, or Customer Service Agent), which pulls live data from SAP S/4HANA and composes a response.
5. **Response Sent to Business Partner** — Orchestrator reviews the sub-agent's response, applies tone/policy rules, and sends the final reply to the customer or vendor.
6. **Case Stored in Knowledge Base** — Full case details (intent, routing decision, response, resolution outcome, business partner profile update) are written back to the knowledge base for future learning.

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash (generic)

### Process Hierarchy

```
Lead to Cash (generic)
└── Invoice to Cash
    └── Process Accounts Receivables and Collect Payment (BPS-366)
        └── Process disputes
        └── Manage collections
        └── Credit memo and adjustment handling
└── Plan to Optimize Marketing and Sales
    └── Develop Customer Service Strategy and Plans (BPS-367)
        └── Develop customer care and customer service strategy
        └── Business partner routing and intelligent triage
        └── Knowledge base learning and continuous improvement
```

### Summary

The business challenge maps to the Lead to Cash end-to-end process, spanning Invoice to Cash (AR collections, dispute management, credit memo processing) and the customer service strategy layer (routing, triage, acknowledgment, and knowledge capture). Vendor-side emails align with Source to Pay for indirect supplier collaboration.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Gap? | Notes / assumptions |
| ---------------------- | ----------------------- | ---------- | ----------------- | ------------------ | ---- | ------------------- |
| Orchestrator Agent — coordinates all sub-agents, full case lifecycle | SAP AI Core (LLM runtime) | — | — | — | Yes | Must be custom-built as a Python AI Agent on SAP BTP using SAP AI Core as the LLM backbone |
| Email intent understanding (subject + body) | SAP AI Core, Service Ticket Intelligence (Text Classification) | — | — | — | Yes | SAP AI Core provides the LLM; custom prompt engineering handles intent extraction |
| Knowledge base — prior interactions, policies, preferred partner lists | SAP BTP (vector store / HANA Cloud vector engine) | — | — | — | Yes | HANA Cloud with vector capabilities on BTP is the recommended store; no standard SAP product covers this out of the box |
| Business partner classification & info gap detection | Orchestrator Agent (custom reasoning) | — | — | — | Yes | Requires dynamic reasoning — handled by the Orchestrator Agent with SAP S/4HANA BP data |
| AR Sub-Agent — statements, open items, dispute handling | SAP S/4HANA Dispute & Collections APIs | `sap.s4:apiResource:CE_API_DISPUTE_MANAGE_0001:v1` | — | — | Partial | Dispute and AR APIs available; sub-agent wraps these with natural language reasoning |
| AP Sub-Agent — vendor invoice status, payment confirmations | SAP S/4HANA (AP open items) | — | — | — | Partial | Standard AP APIs exist; sub-agent layer is custom |
| Treasury Sub-Agent — payment terms, financing inquiries | SAP S/4HANA Finance APIs | — | — | — | Partial | Treasury-related APIs available in S/4HANA Private Edition |
| Collections Sub-Agent — overdue follow-ups, payment plans | SAP S/4HANA Collections Management | `sap.s4:apiResource:CE_API_DISPUTE_MANAGE_0001:v1` | — | — | No | Standard collections APIs available |
| Credit memo request processing | Credit Memo Request (A2X) | `sap.s4:apiResource:API_CREDIT_MEMO_REQUEST_SRV:v1` | — | — | No | Standard S/4HANA API available |
| Send reply to business partner (Outlook + Gmail) | Outlook Email API, Gmail API | — | — | — | No | Both connectors available; Orchestrator Agent sends final reply |
| Human review queue for low-confidence / high-risk cases | BTP Extension (CAP + React review dashboard) | — | — | — | Yes | No standard SAP product; lightweight review UI needed |
| Case storage and knowledge base update after resolution | HANA Cloud vector store + SAP BTP persistence | — | — | — | Yes | Custom write-back logic required after each resolved case |

### Key findings

- The Orchestrator Agent pattern is the right architectural fit — it provides a single control plane across all specialized sub-agents and maintains full case context from ingestion to resolution.
- SAP AI Core on BTP is the LLM runtime for all agents; HANA Cloud (vector engine) is the recommended knowledge base store, keeping everything within the SAP ecosystem.
- Sub-agents for AR, AP, Treasury, Collections, and Customer Service are Python-based AI Agents, each with access to the relevant SAP S/4HANA APIs for their domain.
- The knowledge base is a living asset — it learns preferred business partner behavior, policy exceptions, and routing patterns over time, improving accuracy with every resolved case.
- A BTP Extension (CAP + React) review dashboard remains necessary for low-confidence or high-risk cases that require a human decision before the Orchestrator sends the final reply.
- All email I/O (read + respond) is handled by the Orchestrator Agent via Outlook and Gmail connectors, removing the need for n8n as the primary orchestration layer.

## Recommendations

### Multi-Agent Orchestration Platform for Intelligent Email Handling

#### Executive Summary

Orchestrator Agent on SAP BTP coordinates domain sub-agents to process all emails end-to-end.

#### Recommended Solution

Build a multi-agent platform on SAP BTP with the following architecture:

**Orchestrator Agent (Python, SAP AI Core)**
The central brain. Receives every incoming email, understands intent, consults the knowledge base, determines the business partner context, assesses information completeness, delegates to the correct sub-agent, reviews the sub-agent's response, sends the final reply to the business partner, and writes the resolved case back to the knowledge base. All information flows back through the Orchestrator.

**Specialized Sub-Agents (Python, SAP AI Core)**
Each sub-agent has expertise in one domain and direct access to the relevant SAP S/4HANA APIs:
- **AR Agent** — account statements, open items, dispute case creation and tracking
- **AP Agent** — vendor invoice status, payment confirmations, purchase order inquiries
- **Treasury Agent** — payment terms, financing inquiries, working capital questions
- **Collections Agent** — overdue account follow-ups, payment arrangements, dunning responses
- **Customer Service Agent** — general inquiries, complaints, escalations, policy questions

**Knowledge Base (SAP HANA Cloud — vector store)**
A persistent, searchable store containing: prior interaction history per business partner, preferred customer/vendor flags, department policies and response templates, routing rules, and learned patterns from resolved cases. Every resolved case is written back here to continuously improve accuracy.

**Human Review Dashboard (BTP Extension — CAP + React)**
A lightweight web application where human agents review cases the Orchestrator flagged as low-confidence or high-risk. Reviewers can approve, override, or escalate. Their decisions are also fed back into the knowledge base as training signal.

**Email Connectors**
The Orchestrator Agent reads from and writes to both Microsoft Outlook/Exchange and Gmail/Google Workspace inboxes directly.

#### Affected User Roles

- AR/AP/Collections/Treasury Specialists — receive pre-classified, context-rich cases; no manual email triage
- Customer Service Representatives — handle only escalated or complex cases via the review dashboard
- Finance Managers — gain visibility into case volumes, response times, and routing accuracy via the dashboard
- Customers and Vendors (Business Partners) — receive faster, more accurate, and consistent responses

#### Important factors

##### Continuous learning from every resolved case
The knowledge base grows smarter with every email processed. Preferred partner behavior, policy exceptions, and routing patterns are captured automatically, reducing the need for human intervention over time.

##### Single source of truth for all business partner communications
Every inbound email and outbound response is stored in the knowledge base, giving any sub-agent or human reviewer full context on the history of any business partner relationship.

##### Human-in-the-loop for high-stakes decisions
The system is designed to escalate — not guess — when confidence is low. Credit adjustments above a threshold, disputed amounts, or unusual vendor requests are always reviewed by a human before action is taken.

#### Potential risks

##### Knowledge base quality depends on initial data seeding
The system needs an initial dataset of past interactions and policies to be effective from day one. A data preparation phase is required before go-live.

##### Sub-agent accuracy relies on SAP S/4HANA data quality
If S/4HANA data (open items, BP master data) is incomplete or inconsistent, sub-agents may produce incorrect responses. Data cleansing should be part of the rollout plan.

#### Recommended solution category

AI Agent, BTP Extension

#### Intent fit
96%

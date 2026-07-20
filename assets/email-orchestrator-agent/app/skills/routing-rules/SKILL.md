---
name: routing-rules
description: Routing decision matrix mapping email intent categories to specialist sub-agents
---

# Routing Rules

## Intent → Sub-Agent Mapping

| Intent Category | Target Sub-Agent | Notes |
|---|---|---|
| `statement_request` | `email-ar-agent` | AR retrieves open items and account statement |
| `credit_memo` | `email-ar-agent` | AR handles credit memo creation and status |
| `billing_adjustment` | `email-ar-agent` | AR handles billing adjustments |
| `dispute` | `email-ar-agent` | AR creates and tracks dispute cases |
| `follow_up` | Check prior case sub-agent → fallback to `email-cs-agent` | Look up the last case for this BP and route to that sub-agent. If no prior case found, route to CS. |
| `vendor_invoice_status` | `email-ap-agent` | AP checks vendor invoice processing status |
| `payment_confirmation` | `email-ap-agent` | AP retrieves payment confirmation and bank reference |
| `payment_terms` | `email-treasury-agent` | Treasury looks up payment terms and financing details |
| `overdue_followup` | `email-collections-agent` | Collections checks overdue items and dunning status |
| `general_inquiry` | `email-cs-agent` | CS handles FAQs, complaints, and unclassified requests |
| Unknown / confidence < 0.75 | Human Review Queue | Do not route; flag immediately |

## Override Rules

- **legal_hold_flag = true**: Route to Human Review Queue regardless of intent category.
- **at_risk_flag = true**: Route to Human Review Queue for any write operations; read-only queries can proceed to sub-agent.
- **new_partner (not found in SAP)**: Route to Human Review Queue regardless of intent category.
- **Financial action above FINANCIAL_ACTION_THRESHOLD**: Sub-agent sets `requires_human_review: true`; Orchestrator routes to Human Review Queue after receiving sub-agent response.

---
name: email-classification
description: Instructions for classifying incoming email intent and assigning a confidence score
---

# Email Classification Skill

## Intent Categories

Classify every incoming email into exactly ONE of the following categories:

| Category | Description | Keywords / Signals |
|---|---|---|
| `statement_request` | Customer/vendor requesting an account statement or balance summary | "statement", "balance", "account summary", "outstanding balance" |
| `credit_memo` | Request to issue or check status of a credit memo | "credit memo", "credit note", "credit adjustment" |
| `billing_adjustment` | Request to adjust a billing amount or correct an invoice | "adjustment", "billing error", "incorrect charge", "overcharged" |
| `dispute` | Formal dispute of an invoice, charge, or transaction | "dispute", "disagree", "incorrect invoice", "not received" |
| `follow_up` | Following up on a previous email, case, or inquiry | "following up", "checking in", "still waiting", "previously sent" |
| `vendor_invoice_status` | Vendor asking about the processing status of their submitted invoice | "invoice status", "invoice processing", "when will you pay", "payment expected" |
| `payment_confirmation` | Vendor or customer requesting confirmation that a payment was sent/received | "payment confirmation", "proof of payment", "wire transfer confirmation" |
| `payment_terms` | Question about payment terms, discount periods, or financing | "payment terms", "net 30", "discount", "financing", "credit line" |
| `overdue_followup` | Collections-related: overdue balance, dunning, payment plan | "overdue", "past due", "collections", "dunning", "payment plan" |
| `general_inquiry` | Any question that does not fit the above categories | catch-all |

## Confidence Scoring Guidelines

- **0.90–1.00**: Email clearly and unambiguously matches one category. Multiple clear signals in subject AND body.
- **0.75–0.89**: Email mostly matches one category but has some ambiguity.
- **0.50–0.74**: Email could fit 2 categories. Choose the more likely one.
- **0.00–0.49**: Very ambiguous. Flag for human review regardless of chosen category.

## Rules

1. Always read BOTH the subject line AND the full email body before classifying.
2. If the body contradicts the subject, the body takes precedence.
3. If the email is a reply chain (contains "Re:" or "Fw:"), focus on the most recent message.
4. If confidence < 0.75, set `requires_human_review: true`.
5. Always provide a 2-sentence `summary` in plain language describing what the sender wants.

---
name: knowledge-base-lookup
description: Instructions for querying the HANA Cloud vector store knowledge base for business partner context
---

# Knowledge Base Lookup Skill

## What the Knowledge Base Contains

- **Prior interaction history**: Summaries of past resolved cases per business partner (BP ID)
- **Preferred partner flags**: Whether a BP is on the preferred customer/vendor list
- **At-risk flags**: Whether a BP is flagged as at-risk or on legal hold
- **Department policies**: Routing rules, response templates, financial thresholds
- **FAQ entries**: Answers to frequently asked questions by topic

## How to Form a Query

1. Combine the `bp_id` with the `intent_category` as the primary search keys.
2. Retrieve the last 5 most relevant prior cases for this BP and intent.
3. Retrieve all active policy rules matching the intent category.
4. Check for preferred_partner_flag, at_risk_flag, and legal_hold_flag for this BP.

## Interpreting Results

- **prior_cases_summary**: Use these to understand the BP's relationship history. If a prior case resolved a similar issue, reference the resolution approach.
- **policy_rules**: These are mandatory — apply all matching policy rules when drafting the response.
- **preferred_partner_flag = true**: Prioritize this case (queue position bump) and use elevated professional tone.
- **at_risk_flag = true**: Flag for human review on any write operations. Do not offer payment arrangements autonomously.
- **legal_hold_flag = true**: Immediately route to Human Review Queue. Do not respond to the BP autonomously under any circumstances.

## New Partners

If the knowledge base returns no prior cases and the BP is not found in SAP master data:
- Log `M2.achieved: new partner — no prior history` 
- Set `is_new_partner: true` in the case context
- Proceed with default policies
- Flag for human review

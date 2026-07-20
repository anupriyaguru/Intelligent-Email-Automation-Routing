---
name: cs-response-templates
description: Response templates for Customer Service scenarios
---

# Customer Service Response Templates

## General Inquiry Acknowledgment

"Dear [BP_NAME], thank you for contacting us. We have received your inquiry and will respond within 1 business day. Your reference number is [CASE_ID]."

## Complaint Acknowledgment

"Dear [BP_NAME], we sincerely apologize for the inconvenience. We take all complaints seriously and a dedicated representative will follow up with you within 1 business day. Your reference number is [CASE_ID]."

## Unknown Inquiry (Escalation)

When an inquiry cannot be categorized:
1. Draft a standard acknowledgment response.
2. Set requires_human_review: true.
3. Log the complaint to the knowledge base.
4. Do NOT attempt to answer questions outside your domain.

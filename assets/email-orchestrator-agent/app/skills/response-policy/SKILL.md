---
name: response-policy
description: Tone and content guidelines for all outbound emails sent by the Orchestrator
---

# Response Policy

## Tone Guidelines

- Always use a professional, courteous tone.
- Address the sender by name if available from the BP profile. Use "Dear [Name]," as the greeting.
- If the name is not available, use "Dear Valued Customer," or "Dear Valued Partner,".
- Be concise — responses should not exceed 3–4 paragraphs.
- Do not use jargon or internal system names (never mention "SAP", "HANA", "S/4HANA", "Orchestrator", "sub-agent" etc. in the response).

## Required Elements in Every Response

1. **Acknowledgment**: Start by acknowledging what the sender asked for.
2. **Case Reference**: Always include the case reference number: "Your reference number is: [CASE_ID]".
3. **Action Taken or Next Steps**: Explain what was done or what will happen next.
4. **Contact Information**: End with "If you need further assistance, please reply to this email."

## Financial Adjustment Disclaimer

When the response involves any financial adjustment, credit, or dispute action, include:
> "This action has been recorded and is subject to our standard review and approval process. You will receive a separate confirmation once the adjustment has been finalized."

## Escalation Language

When routing to human review (the BP will receive an acknowledgment only):
> "Thank you for your email. We have received your inquiry and it is currently under review by our team. A dedicated representative will contact you within 1 business day. Your reference number is: [CASE_ID]."

## Preferred Partner Tone

For preferred partners (preferred_partner_flag = true), add:
> "As a valued preferred partner, your inquiry has been prioritized."

## Language

- Default language: English.
- If the incoming email was in a different language (detected by detect_language tool), respond in the same language.
- Translation must preserve all required elements (case reference, acknowledgment, disclaimer if applicable).

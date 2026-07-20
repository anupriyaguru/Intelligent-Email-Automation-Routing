# Specification: email-review-dashboard-cap

> **Guidelines**: Read [guidelines.md](../guidelines.md) and [guidelines-cap.md](../guidelines-cap.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` for full context on the review dashboard requirements, user personas (Maria — AR Specialist, James — Finance Manager), and integration with the Orchestrator Agent
- [ ] Invoke the `cap-development` skill from `assets/email-review-dashboard-cap/` to set up the CAP project structure
- [ ] Install dependencies (`npm install`), validate the project starts (`cds watch`) and responds at `http://localhost:4004`

---

## Data Model (CDS)

- [ ] Define entity `ReviewCase` in `db/schema.cds` with fields:
  - `case_id` (String, key) — unique case identifier from the Orchestrator
  - `status` (String enum: `pending_review`, `approved`, `overridden`, `escalated`, `resolved`)
  - `bp_id` (String) — SAP business partner ID
  - `bp_name` (String) — business partner display name
  - `bp_type` (String enum: `customer`, `vendor`)
  - `bp_tier` (String enum: `preferred`, `standard`, `at_risk`)
  - `sender_email` (String)
  - `email_subject` (String)
  - `email_body` (LargeString)
  - `received_at` (DateTime)
  - `intent_category` (String)
  - `confidence_score` (Decimal)
  - `ai_classification_rationale` (LargeString) — the AI's reasoning for the classification
  - `knowledge_base_context` (LargeString) — JSON summary of KB lookup results used
  - `sub_agent_used` (String) — which sub-agent drafted the response
  - `draft_response` (LargeString) — the AI/sub-agent's proposed reply
  - `final_response` (LargeString) — the approved or overridden reply that was sent
  - `reviewer_id` (String)
  - `review_action` (String enum: `approved`, `overridden`, `escalated`)
  - `review_notes` (LargeString)
  - `reviewed_at` (DateTime)
  - `resolution_type` (String enum: `automated`, `human_approved`, `human_overridden`, `escalated`)
  - `resolved_at` (DateTime)
  - `flagged_reason` (String) — reason the case was flagged (low_confidence, high_value, legal_hold, new_partner, etc.)

- [ ] Define entity `CaseMetrics` as a view in `db/schema.cds` aggregating daily/weekly email volume, automation rate (automated / total), average confidence score, escalation count, and average resolution time by intent category. This powers the management dashboard.

- [ ] Define entity `PolicyRule` in `db/schema.cds` with fields:
  - `rule_id` (String, key)
  - `intent_category` (String)
  - `description` (LargeString)
  - `routing_target` (String)
  - `financial_threshold` (Decimal)
  - `requires_human_review` (Boolean)
  - `active` (Boolean)
  - `updated_by` (String)
  - `updated_at` (DateTime)

- [ ] Define entity `BusinessPartnerConfig` in `db/schema.cds` with fields:
  - `bp_id` (String, key)
  - `preferred_flag` (Boolean)
  - `at_risk_flag` (Boolean)
  - `legal_hold_flag` (Boolean)
  - `notes` (LargeString)
  - `updated_by` (String)
  - `updated_at` (DateTime)

- [ ] Add sample data CSV files in `db/data/` for `ReviewCase`, `PolicyRule`, and `BusinessPartnerConfig` with 10–15 realistic test records each (use fictional BP IDs and case references)

---

## OData Service (CDS)

- [ ] Define service `ReviewDashboardService` in `srv/review-dashboard-service.cds` exposing:
  - `ReviewCases` — full CRUD (agents write pending cases; reviewers read and update)
  - `CaseMetrics` — read-only view for management dashboard
  - `PolicyRules` — CRUD for Finance Manager to manage routing rules
  - `BusinessPartnerConfigs` — CRUD for managing preferred/at-risk/legal-hold flags
- [ ] Annotate `ReviewCases` with `@readonly` on fields that must not be edited by reviewers: `case_id`, `bp_id`, `sender_email`, `email_subject`, `email_body`, `received_at`, `intent_category`, `confidence_score`, `ai_classification_rationale`, `knowledge_base_context`, `sub_agent_used`, `draft_response`
- [ ] Annotate `ReviewCases` with `@mandatory` on reviewer-editable fields when submitting a decision: `review_action`, `final_response` (required if overridden), `reviewed_at`
- [ ] Run `cds compile srv/` to validate all CDS models compile without errors

---

## Custom Service Handler

- [ ] Implement custom handler `srv/review-dashboard-service.js` with the following business logic:
  - **`BEFORE UPDATE ReviewCases`**: Validate that `review_action` is one of `approved`, `overridden`, `escalated`. If `review_action = overridden`, validate that `final_response` is not empty. If `review_action = escalated`, validate that `review_notes` is provided. Reject invalid updates with a descriptive error message.
  - **`ON UPDATE ReviewCases`** (review decision submitted): Set `reviewed_at` = current timestamp. Set `status` = the value of `review_action`. If approved, set `final_response` = `draft_response` (keep as-is). If overridden, keep the reviewer's `final_response`. Set `resolution_type` accordingly.
  - **`AFTER UPDATE ReviewCases`** (post-decision): Emit a structured event `review.decision.submitted` with case_id, review_action, reviewer_id, and final_response. The Orchestrator Agent listens to this event to proceed with sending the email reply.
  - **`BEFORE CREATE ReviewCases`**: Validate that all required fields are present (case_id, bp_id, sender_email, email_subject, draft_response, flagged_reason). Auto-set `status = pending_review` and `received_at` = current timestamp if not provided.

- [ ] Implement read handler for `CaseMetrics` that computes: total_cases_today, automated_today, human_reviewed_today, automation_rate_pct, avg_confidence, avg_resolution_minutes, cases_by_intent (array), escalations_today

---

## React Frontend

- [ ] Invoke the `cap-development` skill to scaffold the React frontend in `assets/email-review-dashboard-cap/ui/`
- [ ] Implement **Review Queue Page** (`/review`) — the primary view for AR/AP/Collections specialists (Maria's view):
  - Table of all `pending_review` cases sorted by received_at ascending (oldest first)
  - Columns: Received, Business Partner, Type (customer/vendor), Intent Category, Confidence Score (color-coded: green ≥ 0.75, amber 0.5–0.74, red < 0.5), Flagged Reason
  - Click row to open **Case Detail Panel** (side panel or modal)
- [ ] Implement **Case Detail Panel** — shown when a reviewer clicks a case:
  - Section 1 — Original Email: sender, subject, full body, received timestamp, source channel (Outlook / Gmail)
  - Section 2 — AI Analysis: intent category, confidence score, classification rationale (from `ai_classification_rationale`), knowledge base context summary (from `knowledge_base_context`), sub-agent used
  - Section 3 — Business Partner: bp_name, bp_id, bp_type, bp_tier badge (preferred / standard / at-risk), any active flags (legal hold, at-risk)
  - Section 4 — Proposed Response: editable text area pre-filled with `draft_response`
  - Action buttons: **Approve** (sends draft_response as-is), **Override** (sends edited response), **Escalate** (requires notes)
  - Confirmation dialog before any action is submitted
- [ ] Implement **Operations Dashboard Page** (`/dashboard`) — for Finance Managers (James's view):
  - KPI cards: Total Emails Today, Automation Rate (%), Avg Response Time (min), Escalations Today
  - Bar chart: Emails by Intent Category (last 7 days)
  - Line chart: Daily Automation Rate trend (last 30 days)
  - Table: Cases in Review Queue by Department (AR / AP / Treasury / Collections / CS) with count and oldest pending age
- [ ] Implement **Policy Rules Page** (`/policies`) — for Finance Manager to manage routing and threshold configuration:
  - Table of all active `PolicyRule` records
  - Inline edit for `financial_threshold`, `requires_human_review`, `routing_target`, `active` fields
  - Save button per row; changes immediately active on save
- [ ] Implement **Business Partner Config Page** (`/partners`) — for managing preferred/at-risk/legal-hold flags:
  - Search by bp_id or bp_name
  - Toggle preferred_flag, at_risk_flag, legal_hold_flag with confirmation dialog
  - Notes field for adding context
- [ ] Implement **Case History Page** (`/history`) — read-only list of all resolved cases (status = approved / overridden / escalated / resolved):
  - Filterable by date range, intent category, resolution type, sub-agent used
  - Click row to view read-only Case Detail Panel for audit trail
- [ ] Apply SAP UI5 Web Components throughout for consistent visual language
- [ ] Ensure all pages are responsive and usable on tablet screen sizes

---

## Testing

- [ ] Write unit test for the `BEFORE UPDATE ReviewCases` handler — test all validation rules: invalid action type rejected, override without final_response rejected, escalation without notes rejected
- [ ] Write unit test for the `ON UPDATE ReviewCases` handler — test approved path (final_response = draft_response), overridden path (final_response = reviewer text), escalated path (status = escalated)
- [ ] Write unit test for the `BEFORE CREATE ReviewCases` handler — test required field validation and auto-set of status and received_at
- [ ] Write unit test for the `CaseMetrics` read handler — test that KPI aggregations return correct values given seeded test data
- [ ] Run `cds compile srv/` to confirm no CDS compile errors
- [ ] Run `cds watch` and use curl/httpie to confirm all OData endpoints respond:
  - `GET /odata/v4/ReviewDashboardService/ReviewCases` — returns seeded data
  - `GET /odata/v4/ReviewDashboardService/CaseMetrics` — returns aggregated metrics
  - `POST /odata/v4/ReviewDashboardService/ReviewCases` — creates a new pending case
  - `PATCH /odata/v4/ReviewDashboardService/ReviewCases(case_id='TEST-001')` — submits a review decision
- [ ] Run all tests and confirm they pass before proceeding

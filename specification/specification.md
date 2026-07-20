# Specification

> **Guidelines**: Read [guidelines.md](./guidelines.md) before executing ANY tasks below.

Check off items as completed.

---

## Solution Overview

This solution implements an intelligent, multi-agent email automation platform for processing 10,000+ monthly customer and vendor emails. A central Orchestrator Agent coordinates five specialized sub-agents (AR, AP, Treasury, Collections, Customer Service). A shared HANA Cloud knowledge base provides memory and learning. A CAP + React review dashboard enables human oversight for complex cases.

**Assets:**
| Asset Name | Type | Purpose |
|---|---|---|
| `email-orchestrator-agent` | AI Agent (Python) | Central Orchestrator — owns the full email lifecycle |
| `email-ar-agent` | AI Agent (Python) | AR specialist — statements, disputes, credit memos |
| `email-ap-agent` | AI Agent (Python) | AP specialist — vendor invoices, payment confirmations |
| `email-treasury-agent` | AI Agent (Python) | Treasury specialist — payment terms, financing |
| `email-collections-agent` | AI Agent (Python) | Collections specialist — overdue follow-ups, payment plans |
| `email-cs-agent` | AI Agent (Python) | Customer Service specialist — general inquiries, complaints |
| `email-review-dashboard-cap` | BTP Extension (CAP + React) | Human review queue + operations dashboard |

---

## Solution Setup

- [ ] Create all asset directories:
  ```bash
  mkdir -p assets/email-orchestrator-agent \
            assets/email-ar-agent \
            assets/email-ap-agent \
            assets/email-treasury-agent \
            assets/email-collections-agent \
            assets/email-cs-agent \
            assets/email-review-dashboard-cap
  ```
- [ ] Invoke `setup-solution` skill to create `solution.yaml` and all `asset.yaml` files for every asset listed above
- [ ] Validate all `asset.yaml` and `solution.yaml` files exist and are well-formed before proceeding

---

## Asset Implementation

Execute each asset specification in the order listed. The sub-agents (AR, AP, Treasury, Collections, CS) may be implemented in parallel after the Orchestrator spec is complete, since the Orchestrator defines the A2A interface contract they all follow.

- [ ] Execute `specification/email-orchestrator-agent/specification.md` — **complete all items** (this defines the A2A interface contract for sub-agents; complete before starting sub-agents)
- [ ] Execute `specification/email-ar-agent/specification.md` — complete all items in the AR Sub-Agent section of the Orchestrator spec
- [ ] Execute `specification/email-ap-agent/specification.md` — complete all items in the AP Sub-Agent section
- [ ] Execute `specification/email-treasury-agent/specification.md` — complete all items in the Treasury Sub-Agent section
- [ ] Execute `specification/email-collections-agent/specification.md` — complete all items in the Collections Sub-Agent section
- [ ] Execute `specification/email-cs-agent/specification.md` — complete all items in the CS Sub-Agent section
- [ ] Execute `specification/email-review-dashboard-cap/specification.md` — complete all items

---

## Cross-Asset Compatibility Check

Run after ALL asset implementations are complete.

- [ ] **A2A Interface Contract**: Verify all sub-agents (AR, AP, Treasury, Collections, CS) accept the standard input schema defined in the Orchestrator's `sub-agent-delegation` runtime skill (case_id, intent, bp_id, email_subject, email_body, knowledge_base_context, sap_data_needed) and return the standard output schema (draft_response, confidence, sap_actions_taken, requires_human_review)
- [ ] **Review Dashboard ↔ Orchestrator Event Contract**: Verify the CAP service emits `review.decision.submitted` events with the exact fields the Orchestrator's `poll_human_review_decision` tool expects (decision, reviewer_id, final_response, timestamp). Fix any field name mismatches.
- [ ] **Knowledge Base Read/Write Contract**: Verify all agents that write to the knowledge base (`write_case_to_knowledge_base`) produce records with the exact schema that `query_knowledge_base` expects to read. Align field names if they differ.
- [ ] **Financial Threshold Consistency**: Verify `FINANCIAL_ACTION_THRESHOLD` constants are consistently defined across all sub-agents that perform SAP write operations (AR Agent, Collections Agent). All should default to the same value (5000.00).
- [ ] **MCP Tool Names**: Verify no agent hard-codes MCP tool names anywhere. All tool resolution must use `get_mcp_tools()` dynamic loading.
- [ ] **Milestone Log Format**: Verify all 6 Orchestrator milestones (M1–M6) and all sub-agent milestones follow the exact log pattern: `[MILESTONE_ID].[achieved|missed]: [description] | case_id=[ID] | partner_id=[ID]`
- [ ] **Test Coverage**: Run `pytest` from each agent asset root and confirm all `test_report.json` files exist. Confirm coverage ≥ 70% across all assets.
- [ ] **CAP Service Health**: Run `cds watch` from `assets/email-review-dashboard-cap/` and confirm all OData endpoints respond correctly.

---

## Final Validation

- [ ] Verify all 7 `asset.yaml` files exist under their respective `assets/<asset-name>/` directories
- [ ] Verify `solution.yaml` exists at the project root and references all 7 assets
- [ ] Verify `test_report.json` exists in each of the 6 agent asset roots
- [ ] Run the decorator check on each agent: `grep -c "^@agent_model\|^@agent_config\|^@prompt_section" assets/<agent>/app/agent.py` — must return exactly 3 for each
- [ ] Run the instrumentation check on each agent: `grep -r "M[0-9]\.achieved" assets/<agent>/app/` — must return results
- [ ] Confirm the review dashboard React UI renders all 5 pages: /review, /dashboard, /policies, /partners, /history

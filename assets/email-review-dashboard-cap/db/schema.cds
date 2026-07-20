namespace email.review.dashboard;

using { cuid, managed } from '@sap/cds/common';

// ─── Code lists ────────────────────────────────────────────────────────────────

type ReviewStatus : String(30) enum {
    pending_review = 'pending_review';
    approved       = 'approved';
    rejected       = 'rejected';
    escalated      = 'escalated';
    overridden     = 'overridden';
}

type FlaggedReason : String(50) enum {
    low_confidence               = 'low_confidence';
    high_value                   = 'high_value';
    legal_hold                   = 'legal_hold';
    new_partner                  = 'new_partner';
    sub_agent_failure            = 'sub_agent_failure';
    credit_memo                  = 'credit_memo';
    high_value_payment_arrangement = 'high_value_payment_arrangement';
    at_risk_partner              = 'at_risk_partner';
}

type IntentCategory : String(40) enum {
    statement_request  = 'statement_request';
    credit_memo        = 'credit_memo';
    billing_adjustment = 'billing_adjustment';
    dispute            = 'dispute';
    follow_up          = 'follow_up';
    vendor_invoice_status = 'vendor_invoice_status';
    payment_confirmation = 'payment_confirmation';
    payment_terms      = 'payment_terms';
    overdue_followup   = 'overdue_followup';
    general_inquiry    = 'general_inquiry';
}

type ResolutionType : String(30) enum {
    automated       = 'automated';
    human_approved  = 'human_approved';
    human_overridden = 'human_overridden';
    escalated       = 'escalated';
}

// ─── Review Cases (human review queue) ────────────────────────────────────────

entity ReviewCases : cuid, managed {
    caseId                     : String(50) not null;
    bpId                       : String(20);
    bpName                     : String(200);
    bpType                     : String(10);
    senderEmail                : String(255) not null;
    emailSubject               : String(500) not null;
    emailBody                  : LargeString;
    intentCategory             : IntentCategory;
    confidenceScore            : Decimal(5, 4);
    flaggedReason              : FlaggedReason;
    draftResponse              : LargeString;
    aiClassificationRationale  : LargeString;
    knowledgeBaseContext       : LargeString;    // JSON blob
    status                     : ReviewStatus default 'pending_review';
    reviewedBy                 : String(255);
    reviewedAt                 : Timestamp;
    reviewerComment            : LargeString;
    finalResponse              : LargeString;
    resolutionType             : ResolutionType;
    subAgent                   : String(60);
    sapActionsProposed         : LargeString;   // JSON blob
}

// ─── Resolved Cases (knowledge base history) ───────────────────────────────────

entity ResolvedCases : cuid, managed {
    caseId           : String(50) not null;
    bpId             : String(20);
    bpName           : String(200);
    intentCategory   : IntentCategory;
    routingPath      : String(100);
    responseSummary  : LargeString;
    resolutionType   : ResolutionType;
    resolvedAt       : Timestamp;
    subAgent         : String(60);
}

// ─── Business Partner Policies ────────────────────────────────────────────────

entity BPolicies : cuid, managed {
    policyKey        : String(100) not null;
    policyName       : String(200) not null;
    intentCategory   : IntentCategory;
    policyText       : LargeString not null;
    isActive         : Boolean default true;
    effectiveFrom    : Date;
    effectiveTo      : Date;
}

// ─── Preferred / At-Risk Partners ─────────────────────────────────────────────

entity PartnerFlags : cuid, managed {
    bpId             : String(20) not null;
    bpName           : String(200);
    isPreferred      : Boolean default false;
    isAtRisk         : Boolean default false;
    hasLegalHold     : Boolean default false;
    notes            : LargeString;
    flaggedBy        : String(255);
    flaggedAt        : Timestamp;
}

// ─── Dashboard Metrics (aggregated) ───────────────────────────────────────────

entity DashboardStats : cuid {
    statDate         : Date;
    totalEmails      : Integer;
    automatedCount   : Integer;
    humanReviewCount : Integer;
    escalatedCount   : Integer;
    avgConfidence    : Decimal(5, 4);
    byIntent         : LargeString;   // JSON blob: {intent: count}
    byAgent          : LargeString;   // JSON blob: {agent: count}
}

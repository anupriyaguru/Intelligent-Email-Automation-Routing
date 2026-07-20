using { email.review.dashboard as db } from '../db/schema';

service ReviewService @(path: '/api/review') {

    // ─── Human Review Queue ────────────────────────────────────────────────
    entity ReviewCases as projection on db.ReviewCases
        excluding { aiClassificationRationale, knowledgeBaseContext }
        actions {
            action approveCase(finalResponse: LargeString, reviewerComment: String) returns ReviewCases;
            action rejectCase(reviewerComment: String)                              returns ReviewCases;
            action overrideAndSend(finalResponse: LargeString, reviewerComment: String) returns ReviewCases;
            action escalateCase(reviewerComment: String)                            returns ReviewCases;
        };

    // ─── Case History ──────────────────────────────────────────────────────
    @readonly
    entity ResolvedCases as projection on db.ResolvedCases;

    // ─── Policies ─────────────────────────────────────────────────────────
    entity BPolicies as projection on db.BPolicies;

    // ─── Partner Flags ─────────────────────────────────────────────────────
    entity PartnerFlags as projection on db.PartnerFlags;

    // ─── Dashboard Stats ───────────────────────────────────────────────────
    @readonly
    entity DashboardStats as projection on db.DashboardStats;

    // ─── Functions ────────────────────────────────────────────────────────
    function getPendingReviewCount() returns Integer;
    function getDashboardSummary()   returns LargeString;
}

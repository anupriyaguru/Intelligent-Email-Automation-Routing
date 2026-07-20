'use strict';

const { beforeAll, afterAll, describe, it, expect } = require('@jest/globals');
const cds = require('@sap/cds');

let srv, db;
let ReviewCases, ResolvedCases, BPolicies, PartnerFlags, DashboardStats;

beforeAll(async () => {
    cds.root = __dirname + '/..';
    const model = await cds.load('*');
    db = await cds.deploy(model).to('sqlite::memory:');
    srv = await cds.serve('ReviewService').from(model).to(db);
    ({ ReviewCases, ResolvedCases, BPolicies, PartnerFlags, DashboardStats } = srv.entities);
});

// ─── helper ───────────────────────────────────────────────────────────────────
async function insertCase(overrides = {}) {
    const ID = cds.utils.uuid();
    await db.run(INSERT.into(ReviewCases).entries({
        ID,
        caseId: `TEST-${ID.slice(0, 8)}`,
        senderEmail: 'test@example.com',
        emailSubject: 'Test Subject',
        status: 'pending_review',
        ...overrides,
    }));
    return ID;
}

// ─── approveCase ──────────────────────────────────────────────────────────────
describe('approveCase action', () => {

    it('should approve a pending case and set status to approved', async () => {
        const ID = await insertCase();

        // Typed stub: srv.approveCase(EntityReflection, entityKey, ...positional_params)
        await srv.approveCase(ReviewCases, { ID }, 'Dear Customer, approved.', 'Verified.');

        const result = await db.run(SELECT.one.from(ReviewCases).where({ ID }));
        expect(result.status).toBe('approved');
        expect(result.resolutionType).toBe('human_approved');
        expect(result.finalResponse).toBe('Dear Customer, approved.');
    });

    it('should reject approving an already-approved case', async () => {
        const ID = await insertCase({ status: 'approved' });

        await expect(
            srv.approveCase(ReviewCases, { ID }, 'Duplicate.', '')
        ).rejects.toThrow();
    });
});

// ─── rejectCase ───────────────────────────────────────────────────────────────
describe('rejectCase action', () => {

    it('should reject a pending case', async () => {
        const ID = await insertCase();

        await srv.rejectCase(ReviewCases, { ID }, 'Invalid request.');

        const result = await db.run(SELECT.one.from(ReviewCases).where({ ID }));
        expect(result.status).toBe('rejected');
    });
});

// ─── overrideAndSend ──────────────────────────────────────────────────────────
describe('overrideAndSend action', () => {

    it('should override a pending case', async () => {
        const ID = await insertCase();

        await srv.overrideAndSend(ReviewCases, { ID }, 'Override response.', 'Changed draft.');

        const result = await db.run(SELECT.one.from(ReviewCases).where({ ID }));
        expect(result.status).toBe('overridden');
        expect(result.resolutionType).toBe('human_overridden');
    });

    it('should fail when finalResponse is empty', async () => {
        const ID = await insertCase();

        await expect(
            srv.overrideAndSend(ReviewCases, { ID }, '', '')
        ).rejects.toThrow(/finalResponse is required/i);
    });
});

// ─── escalateCase ─────────────────────────────────────────────────────────────
describe('escalateCase action', () => {

    it('should escalate a pending case', async () => {
        const ID = await insertCase();

        await srv.escalateCase(ReviewCases, { ID }, 'Legal review needed.');

        const result = await db.run(SELECT.one.from(ReviewCases).where({ ID }));
        expect(result.status).toBe('escalated');
        expect(result.resolutionType).toBe('escalated');
    });
});

// ─── getDashboardSummary ──────────────────────────────────────────────────────
describe('getDashboardSummary function', () => {

    it('should return JSON with required keys', async () => {
        const response = await srv.getDashboardSummary();
        const summary = JSON.parse(response);
        expect(summary).toHaveProperty('pending');
        expect(summary).toHaveProperty('approved');
        expect(summary).toHaveProperty('total');
        expect(summary).toHaveProperty('autoResolutionRate');
        expect(typeof summary.total).toBe('number');
    });
});

// ─── getPendingReviewCount ────────────────────────────────────────────────────
describe('getPendingReviewCount function', () => {

    it('should return a non-negative number', async () => {
        const count = await srv.getPendingReviewCount();
        expect(typeof count).toBe('number');
        expect(count).toBeGreaterThanOrEqual(0);
    });
});

// ─── BPolicies ────────────────────────────────────────────────────────────────
describe('BPolicies entity', () => {

    it('should create and retrieve a policy', async () => {
        const ID = cds.utils.uuid();
        await db.run(INSERT.into(BPolicies).entries({
            ID,
            policyKey: `POL-${ID.slice(0, 8)}`,
            policyName: 'Test Policy',
            policyText: 'Policy text here.',
            isActive: true,
        }));

        const result = await db.run(SELECT.one.from(BPolicies).where({ ID }));
        expect(result.policyName).toBe('Test Policy');
        expect(result.isActive).toBe(true);
    });
});

// ─── PartnerFlags ─────────────────────────────────────────────────────────────
describe('PartnerFlags entity', () => {

    it('should create a partner flag', async () => {
        const ID = cds.utils.uuid();
        await db.run(INSERT.into(PartnerFlags).entries({
            ID,
            bpId: `BP-TEST-${ID.slice(0, 4)}`,
            bpName: 'Test Partner Corp',
            isPreferred: true,
            isAtRisk: false,
            hasLegalHold: false,
        }));

        const result = await db.run(SELECT.one.from(PartnerFlags).where({ ID }));
        expect(result.isPreferred).toBe(true);
        expect(result.hasLegalHold).toBe(false);
    });
});

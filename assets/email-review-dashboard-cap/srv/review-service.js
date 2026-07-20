'use strict';

const cds = require('@sap/cds');

module.exports = class ReviewService extends cds.ApplicationService {

    async init() {
        const { ReviewCases, ResolvedCases, DashboardStats } = this.entities;

        // ─── approveCase action ────────────────────────────────────────────
        this.on('approveCase', ReviewCases, async (req) => {
            // Support both HTTP (req.params[0]) and in-process (req.data) call patterns
            const ID = (req.params && req.params[0] && req.params[0].ID) || req.data?.ID;
            const { finalResponse, reviewerComment } = req.data || {};
            const now = new Date().toISOString();

            if (!ID) return req.reject(400, 'ID is required');

            const n = await UPDATE(ReviewCases, ID)
                .where({ status: { '!=': 'approved' } })
                .with({
                    status: 'approved',
                    finalResponse: finalResponse || '',
                    reviewerComment: reviewerComment || '',
                    reviewedBy: req.user?.id || 'system',
                    reviewedAt: now,
                    resolutionType: 'human_approved',
                });

            if (!n) return req.reject(409, 'Case not found or already processed');

            return await SELECT.one.from(ReviewCases, ID);
        });

        // ─── rejectCase action ─────────────────────────────────────────────
        this.on('rejectCase', ReviewCases, async (req) => {
            const ID = (req.params && req.params[0] && req.params[0].ID) || req.data?.ID;
            const { reviewerComment } = req.data || {};
            const now = new Date().toISOString();

            if (!ID) return req.reject(400, 'ID is required');

            const n = await UPDATE(ReviewCases, ID)
                .where({ status: 'pending_review' })
                .with({
                    status: 'rejected',
                    reviewerComment: reviewerComment || '',
                    reviewedBy: req.user?.id || 'system',
                    reviewedAt: now,
                    resolutionType: 'rejected',
                });

            if (!n) return req.reject(409, 'Case not found or already processed');

            return await SELECT.one.from(ReviewCases, ID);
        });

        // ─── overrideAndSend action ────────────────────────────────────────
        this.on('overrideAndSend', ReviewCases, async (req) => {
            const ID = (req.params && req.params[0] && req.params[0].ID) || req.data?.ID;
            const { finalResponse, reviewerComment } = req.data || {};
            const now = new Date().toISOString();

            if (!ID) return req.reject(400, 'ID is required');
            if (!finalResponse) return req.reject(400, 'finalResponse is required for override');

            const n = await UPDATE(ReviewCases, ID)
                .where({ status: 'pending_review' })
                .with({
                    status: 'overridden',
                    finalResponse,
                    reviewerComment: reviewerComment || '',
                    reviewedBy: req.user?.id || 'system',
                    reviewedAt: now,
                    resolutionType: 'human_overridden',
                });

            if (!n) return req.reject(409, 'Case not found or not in pending_review state');

            return await SELECT.one.from(ReviewCases, ID);
        });

        // ─── escalateCase action ───────────────────────────────────────────
        this.on('escalateCase', ReviewCases, async (req) => {
            const ID = (req.params && req.params[0] && req.params[0].ID) || req.data?.ID;
            const { reviewerComment } = req.data || {};
            const now = new Date().toISOString();

            if (!ID) return req.reject(400, 'ID is required');

            const n = await UPDATE(ReviewCases, ID)
                .where({ status: 'pending_review' })
                .with({
                    status: 'escalated',
                    reviewerComment: reviewerComment || '',
                    reviewedBy: req.user?.id || 'system',
                    reviewedAt: now,
                    resolutionType: 'escalated',
                });

            if (!n) return req.reject(409, 'Case not found or already processed');

            return await SELECT.one.from(ReviewCases, ID);
        });

        // ─── getPendingReviewCount function ───────────────────────────────
        this.on('getPendingReviewCount', async () => {
            const result = await SELECT.one
                .from(ReviewCases)
                .columns('count(*) as count')
                .where({ status: 'pending_review' });
            return Number(result?.count ?? 0);
        });

        // ─── getDashboardSummary function ─────────────────────────────────
        this.on('getDashboardSummary', async () => {
            const [pending, approved, escalated, total] = await Promise.all([
                SELECT.one.from(ReviewCases).columns('count(*) as count').where({ status: 'pending_review' }),
                SELECT.one.from(ReviewCases).columns('count(*) as count').where({ status: 'approved' }),
                SELECT.one.from(ReviewCases).columns('count(*) as count').where({ status: 'escalated' }),
                SELECT.one.from(ReviewCases).columns('count(*) as count'),
            ]);

            const summary = {
                pending: Number(pending?.count ?? 0),
                approved: Number(approved?.count ?? 0),
                escalated: Number(escalated?.count ?? 0),
                total: Number(total?.count ?? 0),
                autoResolutionRate: Number(total?.count) > 0
                    ? parseFloat(((Number(approved?.count ?? 0)) / Number(total.count) * 100).toFixed(1))
                    : 0.0,
            };

            return JSON.stringify(summary);
        });

        return super.init();
    }
};

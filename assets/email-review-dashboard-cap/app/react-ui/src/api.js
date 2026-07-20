/**
 * API client for the ReviewService OData endpoints.
 */

const BASE = '/api/review';

async function fetchJson(url, options) {
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        ...options,
    });
    if (!res.ok) {
        const body = await res.text();
        throw new Error(`HTTP ${res.status}: ${body}`);
    }
    const text = await res.text();
    return text ? JSON.parse(text) : null;
}

// ─── Review Cases ─────────────────────────────────────────────────────────────

export async function getReviewCases(filter = '') {
    const query = filter ? `?$filter=${encodeURIComponent(filter)}&$orderby=createdAt desc` : '?$orderby=createdAt desc';
    const data = await fetchJson(`${BASE}/ReviewCases${query}`);
    return data?.value ?? [];
}

export async function getReviewCase(id) {
    return fetchJson(`${BASE}/ReviewCases(${id})`);
}

export async function approveCase(id, finalResponse, reviewerComment) {
    return fetchJson(`${BASE}/ReviewCases(${id})/ReviewService.approveCase`, {
        method: 'POST',
        body: JSON.stringify({ finalResponse, reviewerComment }),
    });
}

export async function rejectCase(id, reviewerComment) {
    return fetchJson(`${BASE}/ReviewCases(${id})/ReviewService.rejectCase`, {
        method: 'POST',
        body: JSON.stringify({ reviewerComment }),
    });
}

export async function overrideAndSend(id, finalResponse, reviewerComment) {
    return fetchJson(`${BASE}/ReviewCases(${id})/ReviewService.overrideAndSend`, {
        method: 'POST',
        body: JSON.stringify({ finalResponse, reviewerComment }),
    });
}

export async function escalateCase(id, reviewerComment) {
    return fetchJson(`${BASE}/ReviewCases(${id})/ReviewService.escalateCase`, {
        method: 'POST',
        body: JSON.stringify({ reviewerComment }),
    });
}

// ─── Policies ─────────────────────────────────────────────────────────────────

export async function getPolicies() {
    const data = await fetchJson(`${BASE}/BPolicies?$orderby=intentCategory`);
    return data?.value ?? [];
}

export async function createPolicy(policy) {
    return fetchJson(`${BASE}/BPolicies`, {
        method: 'POST',
        body: JSON.stringify(policy),
    });
}

export async function updatePolicy(id, patch) {
    return fetchJson(`${BASE}/BPolicies(${id})`, {
        method: 'PATCH',
        body: JSON.stringify(patch),
    });
}

export async function deletePolicy(id) {
    return fetchJson(`${BASE}/BPolicies(${id})`, { method: 'DELETE' });
}

// ─── Partner Flags ────────────────────────────────────────────────────────────

export async function getPartnerFlags() {
    const data = await fetchJson(`${BASE}/PartnerFlags?$orderby=bpId`);
    return data?.value ?? [];
}

export async function createPartnerFlag(flag) {
    return fetchJson(`${BASE}/PartnerFlags`, {
        method: 'POST',
        body: JSON.stringify(flag),
    });
}

export async function updatePartnerFlag(id, patch) {
    return fetchJson(`${BASE}/PartnerFlags(${id})`, {
        method: 'PATCH',
        body: JSON.stringify(patch),
    });
}

// ─── Case History ─────────────────────────────────────────────────────────────

export async function getResolvedCases(top = 50) {
    const data = await fetchJson(`${BASE}/ResolvedCases?$orderby=createdAt desc&$top=${top}`);
    return data?.value ?? [];
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export async function getDashboardSummary() {
    const data = await fetchJson(`${BASE}/getDashboardSummary()`);
    return data?.value ? JSON.parse(data.value) : {};
}

export async function getDashboardStats() {
    const data = await fetchJson(`${BASE}/DashboardStats?$orderby=statDate desc&$top=30`);
    return data?.value ?? [];
}

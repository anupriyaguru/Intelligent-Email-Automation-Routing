// Simple Express server without CAP/CDS dependencies
const express = require('express');
const path = require('path');

const app = express();
const PORT = 4004;

// In-memory storage
const reviewCases = [];
let caseIdCounter = 1;

// Middleware
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    if (req.method === 'OPTIONS') {
        return res.sendStatus(200);
    }
    next();
});

app.use(express.json());

// API Routes
app.get('/api/review/ReviewCases', (req, res) => {
    res.json({ value: reviewCases });
});

app.post('/api/review/ReviewCases', (req, res) => {
    const newCase = {
        ID: `case-${caseIdCounter++}`,
        ...req.body,
        createdAt: new Date().toISOString(),
        modifiedAt: new Date().toISOString(),
        status: req.body.status || 'pending_review'
    };
    reviewCases.push(newCase);
    console.log(`[Review Dashboard] New case: ${newCase.caseId} - ${newCase.flaggedReason}`);
    res.status(201).json(newCase);
});

app.get('/api/review/ReviewCases/:id', (req, res) => {
    const reviewCase = reviewCases.find(c => c.ID === req.params.id);
    if (reviewCase) {
        res.json(reviewCase);
    } else {
        res.status(404).json({ error: 'Case not found' });
    }
});

app.patch('/api/review/ReviewCases/:id', (req, res) => {
    const index = reviewCases.findIndex(c => c.ID === req.params.id);
    if (index >= 0) {
        reviewCases[index] = {
            ...reviewCases[index],
            ...req.body,
            modifiedAt: new Date().toISOString()
        };
        res.json(reviewCases[index]);
    } else {
        res.status(404).json({ error: 'Case not found' });
    }
});

// Action endpoints
app.post('/api/review/ReviewCases/:id/approveCase', (req, res) => {
    const index = reviewCases.findIndex(c => c.ID === req.params.id);
    if (index >= 0) {
        reviewCases[index] = {
            ...reviewCases[index],
            status: 'approved',
            finalResponse: req.body.finalResponse || reviewCases[index].draftResponse,
            reviewerComment: req.body.reviewerComment || '',
            reviewedAt: new Date().toISOString(),
            resolutionType: 'human_approved'
        };
        console.log(`[Review Dashboard] Case approved: ${reviewCases[index].caseId}`);
        res.json(reviewCases[index]);
    } else {
        res.status(404).json({ error: 'Case not found' });
    }
});

app.post('/api/review/ReviewCases/:id/rejectCase', (req, res) => {
    const index = reviewCases.findIndex(c => c.ID === req.params.id);
    if (index >= 0) {
        reviewCases[index] = {
            ...reviewCases[index],
            status: 'rejected',
            reviewerComment: req.body.reviewerComment || '',
            reviewedAt: new Date().toISOString()
        };
        console.log(`[Review Dashboard] Case rejected: ${reviewCases[index].caseId}`);
        res.json(reviewCases[index]);
    } else {
        res.status(404).json({ error: 'Case not found' });
    }
});

// Serve React UI
const uiPath = path.join(__dirname, 'app', 'react-ui', 'dist');
app.use(express.static(uiPath));

// Fallback for SPA routing - must be last
app.use((req, res) => {
    res.sendFile(path.join(uiPath, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`\n========================================`);
    console.log(`  Email Review Dashboard - Running`);
    console.log(`========================================`);
    console.log(`  Server:  http://localhost:${PORT}`);
    console.log(`  API:     http://localhost:${PORT}/api/review/`);
    console.log(`========================================\n`);
});

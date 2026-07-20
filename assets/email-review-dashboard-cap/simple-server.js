// Minimal CAP server without database
const cds = require('@sap/cds');
const express = require('express');

async function startServer() {
    try {
        // Don't use database at all
        cds.env.requires.db = null;

        const app = express();
        app.use(express.json());

        // Mock data store
        const store = {
            ReviewCases: [],
            ResolvedCases: [],
            BPolicies: [],
            PartnerFlags: []
        };

        // Basic REST endpoints
        app.get('/api/review/ReviewCases', (req, res) => {
            res.json({ value: store.ReviewCases });
        });

        app.post('/api/review/ReviewCases', (req, res) => {
            const item = {
                ID: require('crypto').randomUUID(),
                ...req.body,
                createdAt: new Date().toISOString(),
                status: 'pending_review'
            };
            store.ReviewCases.push(item);
            res.status(201).json(item);
        });

        app.get('/api/review/ResolvedCases', (req, res) => {
            res.json({ value: store.ResolvedCases });
        });

        app.get('/api/review/BPolicies', (req, res) => {
            res.json({ value: store.BPolicies });
        });

        app.get('/api/review/PartnerFlags', (req, res) => {
            res.json({ value: store.PartnerFlags });
        });

        app.get('/', (req, res) => {
            res.json({
                name: 'Email Review Dashboard',
                endpoints: [
                    '/api/review/ReviewCases',
                    '/api/review/ResolvedCases',
                    '/api/review/BPolicies',
                    '/api/review/PartnerFlags'
                ]
            });
        });

        const port = 4004;
        app.listen(port, () => {
            console.log(`\n✅ CAP Dashboard (mock mode) running on http://localhost:${port}`);
            console.log(`   Endpoints: http://localhost:${port}/api/review/`);
        });
    } catch (err) {
        console.error('Error starting server:', err);
    }
}

startServer();

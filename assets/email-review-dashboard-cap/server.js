// Simple CAP server without SQLite dependency
const cds = require('@sap/cds');

// Override database service to use in-memory storage
class InMemoryService extends cds.Service {
    constructor() {
        super();
        this.data = {
            ReviewCases: [],
            ResolvedCases: [],
            BPolicies: [],
            PartnerFlags: [],
            DashboardStats: []
        };
    }

    async init() {
        this.on('READ', '*', async (req) => {
            const entity = req.target.name.split('.').pop();
            return this.data[entity] || [];
        });

        this.on('CREATE', '*', async (req) => {
            const entity = req.target.name.split('.').pop();
            const data = req.data;
            data.ID = data.ID || require('crypto').randomUUID();
            data.createdAt = new Date().toISOString();
            this.data[entity] = this.data[entity] || [];
            this.data[entity].push(data);
            return data;
        });

        this.on('UPDATE', '*', async (req) => {
            const entity = req.target.name.split('.').pop();
            const items = this.data[entity] || [];
            const id = req.data.ID;
            const index = items.findIndex(item => item.ID === id);
            if (index >= 0) {
                items[index] = { ...items[index], ...req.data, modifiedAt: new Date().toISOString() };
                return items[index];
            }
            return null;
        });

        this.on('DELETE', '*', async (req) => {
            const entity = req.target.name.split('.').pop();
            const items = this.data[entity] || [];
            const id = req.data.ID;
            const index = items.findIndex(item => item.ID === id);
            if (index >= 0) {
                items.splice(index, 1);
                return { deleted: 1 };
            }
            return { deleted: 0 };
        });

        return super.init();
    }
}

module.exports = async function() {
    // Register in-memory database service
    cds.env.requires.db = { impl: InMemoryService };

    // Start CAP server
    await cds.serve('all').from('srv');

    console.log('\n[CAP] Server started with in-memory database');
    console.log('[CAP] Service endpoints:');
    console.log('  - http://localhost:4004/api/review/');
    console.log('  - http://localhost:4004/');
};

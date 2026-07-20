import { useEffect, useState } from 'react';
import { getDashboardSummary, getDashboardStats } from '../api';

export default function DashboardPage() {
    const [summary, setSummary] = useState({});
    const [stats, setStats]     = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError]     = useState('');

    useEffect(() => {
        (async () => {
            setLoading(true); setError('');
            try {
                const [s, d] = await Promise.all([getDashboardSummary(), getDashboardStats()]);
                setSummary(s);
                setStats(d);
            } catch (e) { setError(e.message); }
            finally { setLoading(false); }
        })();
    }, []);

    if (loading) return <div className="loading">Loading dashboard…</div>;
    if (error)   return <div className="error-msg">{error}</div>;

    const autoRate = summary.autoResolutionRate ?? 'N/A';

    return (
        <div>
            <h1 className="page-title">📊 Operations Dashboard</h1>

            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-number">{summary.pending ?? 0}</div>
                    <div className="stat-label">Pending Review</div>
                </div>
                <div className="stat-card">
                    <div className="stat-number">{summary.approved ?? 0}</div>
                    <div className="stat-label">Approved Today</div>
                </div>
                <div className="stat-card">
                    <div className="stat-number">{summary.escalated ?? 0}</div>
                    <div className="stat-label">Escalated</div>
                </div>
                <div className="stat-card">
                    <div className="stat-number">{summary.total ?? 0}</div>
                    <div className="stat-label">Total Cases</div>
                </div>
                <div className="stat-card">
                    <div className="stat-number">{autoRate}%</div>
                    <div className="stat-label">Auto-Resolution Rate</div>
                </div>
            </div>

            <div className="card">
                <h2 style={{fontSize:15, fontWeight:700, marginBottom:14}}>Daily Email Volume</h2>
                {stats.length === 0 ? (
                    <p className="text-muted">No historical stats available yet.</p>
                ) : (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Total</th>
                                <th>Automated</th>
                                <th>Human Review</th>
                                <th>Escalated</th>
                                <th>Avg Confidence</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stats.map(s => (
                                <tr key={s.ID}>
                                    <td>{s.statDate}</td>
                                    <td><strong>{s.totalEmails}</strong></td>
                                    <td style={{color:'#107e3e'}}>{s.automatedCount}</td>
                                    <td style={{color:'#e9730c'}}>{s.humanReviewCount}</td>
                                    <td style={{color:'#bb0000'}}>{s.escalatedCount}</td>
                                    <td>{s.avgConfidence ? (s.avgConfidence * 100).toFixed(1) + '%' : 'N/A'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            <div className="card">
                <h2 style={{fontSize:15, fontWeight:700, marginBottom:14}}>Agent Performance Overview</h2>
                <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:12}}>
                    {[
                        { name: 'AR Agent',          icon: '📑', domain: 'Accounts Receivable' },
                        { name: 'AP Agent',          icon: '🏭', domain: 'Accounts Payable' },
                        { name: 'Treasury Agent',    icon: '💰', domain: 'Treasury & Finance' },
                        { name: 'Collections Agent', icon: '📞', domain: 'Collections' },
                        { name: 'CS Agent',          icon: '💬', domain: 'Customer Service' },
                        { name: 'Orchestrator',      icon: '🎯', domain: 'Central Coordinator' },
                    ].map(a => (
                        <div key={a.name} style={{
                            background:'#f7f9ff', border:'1px solid #e0e8ff',
                            borderRadius:8, padding:16, display:'flex', alignItems:'center', gap:14
                        }}>
                            <span style={{fontSize:28}}>{a.icon}</span>
                            <div>
                                <div style={{fontWeight:700, fontSize:13}}>{a.name}</div>
                                <div className="text-muted">{a.domain}</div>
                                <div style={{marginTop:4}}>
                                    <span className="badge badge-approved" style={{fontSize:11}}>● Active</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

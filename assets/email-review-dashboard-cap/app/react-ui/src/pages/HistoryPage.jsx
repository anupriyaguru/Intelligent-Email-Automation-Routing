import { useEffect, useState } from 'react';
import { getResolvedCases } from '../api';

export default function HistoryPage() {
    const [cases, setCases]   = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError]   = useState('');
    const [search, setSearch] = useState('');

    useEffect(() => {
        (async () => {
            setLoading(true); setError('');
            try { setCases(await getResolvedCases(100)); }
            catch (e) { setError(e.message); }
            finally { setLoading(false); }
        })();
    }, []);

    const filtered = search
        ? cases.filter(c =>
            c.caseId?.includes(search) ||
            c.bpId?.includes(search) ||
            c.bpName?.toLowerCase().includes(search.toLowerCase()) ||
            c.intentCategory?.includes(search)
        )
        : cases;

    const RESOLUTION_BADGE = {
        automated:       'badge-approved',
        human_approved:  'badge-approved',
        human_overridden:'badge-escalated',
        escalated:       'badge-pending',
    };

    return (
        <div>
            <h1 className="page-title">🗂 Case History</h1>
            {error && <div className="error-msg">{error}</div>}

            <div className="filters">
                <input
                    className="form-control"
                    style={{maxWidth:320}}
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder="Search by case ID, BP ID, name, or intent…"
                />
                <span className="text-muted">{filtered.length} cases</span>
            </div>

            {loading ? <div className="loading">Loading history…</div> : (
                <div className="card" style={{padding:0}}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Case ID</th>
                                <th>Business Partner</th>
                                <th>Intent</th>
                                <th>Sub-Agent</th>
                                <th>Resolution</th>
                                <th>Response Summary</th>
                                <th>Resolved</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.length === 0 && (
                                <tr><td colSpan={7} style={{textAlign:'center',color:'#888',padding:24}}>No cases found</td></tr>
                            )}
                            {filtered.map(c => (
                                <tr key={c.ID}>
                                    <td className="text-small">{c.caseId}</td>
                                    <td>
                                        <div>{c.bpName || c.bpId}</div>
                                        <div className="text-muted">{c.bpId}</div>
                                    </td>
                                    <td className="text-small">{c.intentCategory?.replace(/_/g,' ')}</td>
                                    <td className="text-small">{c.subAgent}</td>
                                    <td>
                                        <span className={`badge ${RESOLUTION_BADGE[c.resolutionType] || 'badge-pending'}`}>
                                            {c.resolutionType?.replace(/_/g,' ')}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="truncate text-small">{c.responseSummary}</div>
                                    </td>
                                    <td className="text-muted">
                                        {c.resolvedAt ? new Date(c.resolvedAt).toLocaleDateString() : ''}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

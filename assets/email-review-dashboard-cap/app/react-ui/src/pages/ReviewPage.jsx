import { useEffect, useState } from 'react';
import { getReviewCases, approveCase, rejectCase, overrideAndSend, escalateCase } from '../api';

const STATUS_FILTER_OPTIONS = ['all', 'pending_review', 'approved', 'rejected', 'escalated', 'overridden'];
const BADGE_CLASS = {
    pending_review: 'badge-pending',
    approved:       'badge-approved',
    rejected:       'badge-rejected',
    escalated:      'badge-escalated',
    overridden:     'badge-overridden',
};

function confidenceClass(score) {
    if (score >= 0.75) return 'confidence-high';
    if (score >= 0.5)  return 'confidence-medium';
    return 'confidence-low';
}

export default function ReviewPage() {
    const [cases, setCases]         = useState([]);
    const [loading, setLoading]     = useState(true);
    const [error, setError]         = useState('');
    const [statusFilter, setStatus] = useState('pending_review');
    const [selected, setSelected]   = useState(null);
    const [comment, setComment]     = useState('');
    const [finalResp, setFinalResp] = useState('');
    const [processing, setProcessing] = useState(false);

    const load = async () => {
        setLoading(true); setError('');
        try {
            const filter = statusFilter !== 'all' ? `status eq '${statusFilter}'` : '';
            setCases(await getReviewCases(filter));
        } catch (e) { setError(e.message); }
        finally { setLoading(false); }
    };

    useEffect(() => { load(); }, [statusFilter]);

    const openCase = (c) => { setSelected(c); setComment(''); setFinalResp(c.draftResponse || ''); };
    const closeModal = () => { setSelected(null); setComment(''); setFinalResp(''); };

    const act = async (action) => {
        setProcessing(true);
        try {
            const id = selected.ID;
            if (action === 'approve')   await approveCase(id, finalResp, comment);
            if (action === 'reject')    await rejectCase(id, comment);
            if (action === 'override')  await overrideAndSend(id, finalResp, comment);
            if (action === 'escalate')  await escalateCase(id, comment);
            closeModal();
            load();
        } catch (e) { alert(e.message); }
        finally { setProcessing(false); }
    };

    return (
        <div>
            <h1 className="page-title">📬 Human Review Queue</h1>
            {error && <div className="error-msg">{error}</div>}

            <div className="filters">
                <label className="form-label" style={{margin:0}}>Filter by Status:</label>
                {STATUS_FILTER_OPTIONS.map(s => (
                    <button
                        key={s}
                        className={`btn btn-sm ${statusFilter === s ? 'btn-primary' : 'btn-ghost'}`}
                        onClick={() => setStatus(s)}
                    >{s === 'all' ? 'All' : s.replace(/_/g, ' ')}</button>
                ))}
                <button className="btn btn-ghost btn-sm" onClick={load} style={{marginLeft:'auto'}}>↻ Refresh</button>
            </div>

            {loading ? <div className="loading">Loading cases…</div> : (
                <div className="card" style={{padding:0}}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Case ID</th>
                                <th>Business Partner</th>
                                <th>Subject</th>
                                <th>Intent</th>
                                <th>Confidence</th>
                                <th>Reason</th>
                                <th>Status</th>
                                <th>Received</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {cases.length === 0 && (
                                <tr><td colSpan={9} style={{textAlign:'center', color:'#888', padding:24}}>No cases found</td></tr>
                            )}
                            {cases.map(c => (
                                <tr key={c.ID}>
                                    <td className="text-small">{c.caseId}</td>
                                    <td>
                                        <div>{c.bpName || c.bpId}</div>
                                        <div className="text-muted">{c.senderEmail}</div>
                                    </td>
                                    <td className="truncate">{c.emailSubject}</td>
                                    <td className="text-small">{c.intentCategory?.replace(/_/g,' ')}</td>
                                    <td>
                                        <span className={confidenceClass(c.confidenceScore)}>
                                            {(c.confidenceScore * 100).toFixed(0)}%
                                        </span>
                                    </td>
                                    <td className="text-small">{c.flaggedReason?.replace(/_/g,' ')}</td>
                                    <td><span className={`badge ${BADGE_CLASS[c.status] || ''}`}>{c.status?.replace(/_/g,' ')}</span></td>
                                    <td className="text-muted">{c.createdAt ? new Date(c.createdAt).toLocaleDateString() : ''}</td>
                                    <td>
                                        <button className="btn btn-ghost btn-sm" onClick={() => openCase(c)}>Review</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {selected && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <span className="modal-title">Review Case: {selected.caseId}</span>
                            <button className="modal-close" onClick={closeModal}>×</button>
                        </div>

                        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12, marginBottom:16}}>
                            <div><span className="form-label">Business Partner</span>{selected.bpName || selected.bpId}</div>
                            <div><span className="form-label">Sender</span>{selected.senderEmail}</div>
                            <div><span className="form-label">Intent</span>{selected.intentCategory?.replace(/_/g,' ')}</div>
                            <div><span className="form-label">Confidence</span>
                                <span className={confidenceClass(selected.confidenceScore)}>
                                    {(selected.confidenceScore * 100).toFixed(0)}%
                                </span>
                            </div>
                            <div><span className="form-label">Flagged Reason</span>{selected.flaggedReason?.replace(/_/g,' ')}</div>
                            <div><span className="form-label">Sub-Agent</span>{selected.subAgent}</div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Email Subject</label>
                            <div className="form-control" style={{background:'#f7f7f7'}}>{selected.emailSubject}</div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Email Body</label>
                            <textarea className="form-control" readOnly value={selected.emailBody || ''} style={{background:'#f7f7f7', minHeight:80}} />
                        </div>

                        <div className="form-group">
                            <label className="form-label">AI Draft Response</label>
                            <textarea
                                className="form-control"
                                value={finalResp}
                                onChange={e => setFinalResp(e.target.value)}
                                placeholder="Edit the draft response to send…"
                                style={{minHeight:120}}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Reviewer Comment</label>
                            <textarea
                                className="form-control"
                                value={comment}
                                onChange={e => setComment(e.target.value)}
                                placeholder="Add your review comment (optional)…"
                                style={{minHeight:60}}
                            />
                        </div>

                        <div className="modal-footer">
                            <button className="btn btn-ghost"    onClick={closeModal} disabled={processing}>Cancel</button>
                            <button className="btn btn-warning"  onClick={() => act('escalate')} disabled={processing}>🔺 Escalate</button>
                            <button className="btn btn-danger"   onClick={() => act('reject')}   disabled={processing}>✗ Reject</button>
                            <button className="btn btn-primary"  onClick={() => act('override')} disabled={processing}>✏ Override & Send</button>
                            <button className="btn btn-success"  onClick={() => act('approve')}  disabled={processing}>✓ Approve & Send</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

import { useEffect, useState } from 'react';
import { getPartnerFlags, createPartnerFlag, updatePartnerFlag } from '../api';

const EMPTY_FLAG = { bpId: '', bpName: '', isPreferred: false, isAtRisk: false, hasLegalHold: false, notes: '' };

export default function PartnersPage() {
    const [partners, setPartners] = useState([]);
    const [loading, setLoading]   = useState(true);
    const [error, setError]       = useState('');
    const [editing, setEditing]   = useState(null);
    const [form, setForm]         = useState(EMPTY_FLAG);
    const [saving, setSaving]     = useState(false);

    const load = async () => {
        setLoading(true); setError('');
        try { setPartners(await getPartnerFlags()); }
        catch (e) { setError(e.message); }
        finally { setLoading(false); }
    };

    useEffect(() => { load(); }, []);

    const openNew = () => { setEditing('new'); setForm(EMPTY_FLAG); };
    const openEdit = (p) => { setEditing(p.ID); setForm({ ...p }); };
    const closeModal = () => { setEditing(null); };

    const handleSave = async () => {
        if (!form.bpId) { alert('Business Partner ID is required.'); return; }
        setSaving(true);
        try {
            if (editing === 'new') await createPartnerFlag(form);
            else await updatePartnerFlag(editing, {
                isPreferred: form.isPreferred,
                isAtRisk: form.isAtRisk,
                hasLegalHold: form.hasLegalHold,
                notes: form.notes,
                bpName: form.bpName,
            });
            closeModal(); load();
        } catch (e) { alert(e.message); }
        finally { setSaving(false); }
    };

    return (
        <div>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20 }}>
                <h1 className="page-title" style={{margin:0}}>🏢 Partner Flags</h1>
                <button className="btn btn-primary" onClick={openNew}>+ Add Partner Flag</button>
            </div>

            {error && <div className="error-msg">{error}</div>}

            {loading ? <div className="loading">Loading partner flags…</div> : (
                <div className="card" style={{padding:0}}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>BP ID</th>
                                <th>Name</th>
                                <th>Preferred</th>
                                <th>At Risk</th>
                                <th>Legal Hold</th>
                                <th>Notes</th>
                                <th>Flagged</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {partners.length === 0 && (
                                <tr><td colSpan={8} style={{textAlign:'center',color:'#888',padding:24}}>No partner flags found</td></tr>
                            )}
                            {partners.map(p => (
                                <tr key={p.ID}>
                                    <td><strong>{p.bpId}</strong></td>
                                    <td>{p.bpName}</td>
                                    <td>{p.isPreferred ? <span className="badge badge-approved">⭐ Preferred</span> : <span className="text-muted">—</span>}</td>
                                    <td>{p.isAtRisk ? <span className="badge badge-pending">⚠ At Risk</span> : <span className="text-muted">—</span>}</td>
                                    <td>{p.hasLegalHold ? <span className="badge badge-rejected">🔒 Hold</span> : <span className="text-muted">—</span>}</td>
                                    <td className="truncate text-small">{p.notes}</td>
                                    <td className="text-muted">{p.flaggedAt ? new Date(p.flaggedAt).toLocaleDateString() : ''}</td>
                                    <td>
                                        <button className="btn btn-ghost btn-sm" onClick={() => openEdit(p)}>Edit</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {editing && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <span className="modal-title">{editing === 'new' ? 'Add Partner Flag' : 'Edit Partner Flag'}</span>
                            <button className="modal-close" onClick={closeModal}>×</button>
                        </div>

                        <div className="form-group">
                            <label className="form-label">BP ID *</label>
                            <input className="form-control" value={form.bpId} disabled={editing !== 'new'}
                                onChange={e => setForm({...form, bpId: e.target.value})} placeholder="e.g. BP-10001" />
                        </div>
                        <div className="form-group">
                            <label className="form-label">BP Name</label>
                            <input className="form-control" value={form.bpName || ''}
                                onChange={e => setForm({...form, bpName: e.target.value})} placeholder="Company name" />
                        </div>

                        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:12, marginBottom:14}}>
                            {[
                                ['isPreferred', '⭐ Preferred Partner'],
                                ['isAtRisk',    '⚠ At Risk'],
                                ['hasLegalHold','🔒 Legal Hold'],
                            ].map(([key, label]) => (
                                <div key={key} style={{display:'flex', alignItems:'center', gap:8, background:'#f7f7f7', padding:'10px 14px', borderRadius:6, cursor:'pointer'}}
                                    onClick={() => setForm({...form, [key]: !form[key]})}>
                                    <input type="checkbox" checked={!!form[key]} onChange={() => {}} />
                                    <span className="text-small">{label}</span>
                                </div>
                            ))}
                        </div>

                        <div className="form-group">
                            <label className="form-label">Notes</label>
                            <textarea className="form-control" value={form.notes || ''}
                                onChange={e => setForm({...form, notes: e.target.value})}
                                placeholder="Reason for flag, context, escalation contacts…"
                                style={{minHeight:80}} />
                        </div>

                        <div className="modal-footer">
                            <button className="btn btn-ghost" onClick={closeModal}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                                {saving ? 'Saving…' : 'Save Flag'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

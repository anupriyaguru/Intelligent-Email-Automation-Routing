import { useEffect, useState } from 'react';
import { getPolicies, createPolicy, updatePolicy, deletePolicy } from '../api';

const INTENT_OPTIONS = [
    '', 'statement_request', 'credit_memo', 'billing_adjustment', 'dispute',
    'follow_up', 'vendor_invoice_status', 'payment_confirmation',
    'payment_terms', 'overdue_followup', 'general_inquiry'
];

const EMPTY_POLICY = { policyKey: '', policyName: '', intentCategory: '', policyText: '', isActive: true };

export default function PoliciesPage() {
    const [policies, setPolicies] = useState([]);
    const [loading, setLoading]   = useState(true);
    const [error, setError]       = useState('');
    const [editing, setEditing]   = useState(null);
    const [form, setForm]         = useState(EMPTY_POLICY);
    const [saving, setSaving]     = useState(false);

    const load = async () => {
        setLoading(true); setError('');
        try { setPolicies(await getPolicies()); }
        catch (e) { setError(e.message); }
        finally { setLoading(false); }
    };

    useEffect(() => { load(); }, []);

    const openNew = () => { setEditing('new'); setForm(EMPTY_POLICY); };
    const openEdit = (p) => { setEditing(p.ID); setForm({ ...p }); };
    const closeModal = () => { setEditing(null); };

    const handleSave = async () => {
        if (!form.policyKey || !form.policyName || !form.policyText) {
            alert('Key, Name, and Text are required.'); return;
        }
        setSaving(true);
        try {
            if (editing === 'new') await createPolicy(form);
            else await updatePolicy(editing, { policyText: form.policyText, policyName: form.policyName, isActive: form.isActive });
            closeModal(); load();
        } catch (e) { alert(e.message); }
        finally { setSaving(false); }
    };

    const handleDelete = async (id) => {
        if (!confirm('Delete this policy?')) return;
        try { await deletePolicy(id); load(); }
        catch (e) { alert(e.message); }
    };

    return (
        <div>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20 }}>
                <h1 className="page-title" style={{margin:0}}>📋 Business Policies</h1>
                <button className="btn btn-primary" onClick={openNew}>+ New Policy</button>
            </div>

            {error && <div className="error-msg">{error}</div>}

            {loading ? <div className="loading">Loading policies…</div> : (
                <div className="card" style={{padding:0}}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Key</th>
                                <th>Name</th>
                                <th>Intent Category</th>
                                <th>Status</th>
                                <th>Text Preview</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {policies.length === 0 && (
                                <tr><td colSpan={6} style={{textAlign:'center',color:'#888',padding:24}}>No policies found</td></tr>
                            )}
                            {policies.map(p => (
                                <tr key={p.ID}>
                                    <td className="text-small">{p.policyKey}</td>
                                    <td><strong>{p.policyName}</strong></td>
                                    <td className="text-small">{p.intentCategory?.replace(/_/g,' ') || 'All'}</td>
                                    <td>
                                        <span className={`badge ${p.isActive ? 'badge-approved' : 'badge-rejected'}`}>
                                            {p.isActive ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="truncate text-small" style={{maxWidth:300, color:'#555'}}>
                                            {p.policyText}
                                        </div>
                                    </td>
                                    <td>
                                        <button className="btn btn-ghost btn-sm" onClick={() => openEdit(p)} style={{marginRight:4}}>Edit</button>
                                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(p.ID)}>Delete</button>
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
                            <span className="modal-title">{editing === 'new' ? 'New Policy' : 'Edit Policy'}</span>
                            <button className="modal-close" onClick={closeModal}>×</button>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Policy Key *</label>
                            <input className="form-control" value={form.policyKey} disabled={editing !== 'new'}
                                onChange={e => setForm({...form, policyKey: e.target.value})} placeholder="e.g. AR-DISPUTE-001" />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Policy Name *</label>
                            <input className="form-control" value={form.policyName}
                                onChange={e => setForm({...form, policyName: e.target.value})} placeholder="Human-readable name" />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Intent Category</label>
                            <select className="form-control" value={form.intentCategory || ''}
                                onChange={e => setForm({...form, intentCategory: e.target.value})}>
                                {INTENT_OPTIONS.map(o => <option key={o} value={o}>{o || '— All categories —'}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Policy Text *</label>
                            <textarea className="form-control" value={form.policyText} style={{minHeight:120}}
                                onChange={e => setForm({...form, policyText: e.target.value})} placeholder="Full policy text…" />
                        </div>
                        <div className="form-group" style={{display:'flex', alignItems:'center', gap:8}}>
                            <input type="checkbox" id="isActive" checked={form.isActive}
                                onChange={e => setForm({...form, isActive: e.target.checked})} />
                            <label htmlFor="isActive">Active</label>
                        </div>

                        <div className="modal-footer">
                            <button className="btn btn-ghost" onClick={closeModal}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                                {saving ? 'Saving…' : 'Save Policy'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

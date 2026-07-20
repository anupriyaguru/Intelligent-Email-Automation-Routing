import { useState } from 'react';
import ReviewPage from './pages/ReviewPage';
import DashboardPage from './pages/DashboardPage';
import PoliciesPage from './pages/PoliciesPage';
import PartnersPage from './pages/PartnersPage';
import HistoryPage from './pages/HistoryPage';
import './App.css';

const NAV_ITEMS = [
    { id: 'review',    label: '📬 Review Queue' },
    { id: 'dashboard', label: '📊 Dashboard' },
    { id: 'policies',  label: '📋 Policies' },
    { id: 'partners',  label: '🏢 Partners' },
    { id: 'history',   label: '🗂 History' },
];

export default function App() {
    const [activePage, setActivePage] = useState('review');

    const renderPage = () => {
        switch (activePage) {
            case 'review':    return <ReviewPage />;
            case 'dashboard': return <DashboardPage />;
            case 'policies':  return <PoliciesPage />;
            case 'partners':  return <PartnersPage />;
            case 'history':   return <HistoryPage />;
            default:          return <ReviewPage />;
        }
    };

    return (
        <div className="app-shell">
            <header className="app-header">
                <div className="header-logo">⚡ Email Automation Hub</div>
                <nav className="app-nav">
                    {NAV_ITEMS.map(item => (
                        <button
                            key={item.id}
                            className={`nav-btn ${activePage === item.id ? 'active' : ''}`}
                            onClick={() => setActivePage(item.id)}
                        >
                            {item.label}
                        </button>
                    ))}
                </nav>
            </header>
            <main className="app-main">
                {renderPage()}
            </main>
        </div>
    );
}

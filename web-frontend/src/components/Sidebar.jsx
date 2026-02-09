import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ConfirmModal from './ConfirmModal';
import logo from '../assets/logo.png';
import logoLight from '../assets/logo_light.png';
import { useTheme } from '../App';

function Sidebar({ username, datasets, onDeleteDataset, onLogout }) {
    const navigate = useNavigate();
    const { isDark } = useTheme();
    const [deleteModal, setDeleteModal] = useState({ show: false, id: null, filename: '' });

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const handleDeleteClick = (e, id, filename) => {
        e.stopPropagation();
        setDeleteModal({ show: true, id, filename });
    };

    const confirmDelete = () => {
        if (deleteModal.id) {
            // Mock event object since original handler expects it
            const mockEvent = { stopPropagation: () => { } };
            onDeleteDataset(mockEvent, deleteModal.id, deleteModal.filename);
            setDeleteModal({ show: false, id: null, filename: '' });
        }
    };

    return (
        <>
            <aside className="sidebar">
                <div className="login-logo" style={{ marginBottom: '2rem', cursor: 'pointer', textAlign: 'center' }} onClick={() => navigate('/dashboard')}>
                    <img src={isDark ? logo : logoLight} alt="CHEMVIZ" style={{ maxWidth: '160px', height: 'auto' }} />
                </div>

                <div
                    onClick={() => navigate('/profile')}
                    className="user-profile-card animate-slide-up stagger-1"
                >
                    <div className="user-avatar">
                        {username ? username.charAt(0).toUpperCase() : 'U'}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.7rem', marginBottom: '0.1rem', textTransform: 'uppercase', letterSpacing: '0.05em', margin: 0 }}>
                            Signed in as
                        </p>
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                            <p style={{ fontWeight: '600', fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', margin: 0 }}>{username}</p>
                        </div>
                    </div>
                </div>

                <h3 className="animate-slide-up stagger-2" style={{ fontSize: '0.9rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '1rem', marginTop: '1rem', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
                    Recent Datasets
                </h3>

                <ul className="history-list">
                    {datasets.length === 0 ? (
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                            No datasets uploaded yet
                        </p>
                    ) : (
                        datasets.map((dataset, index) => (
                            <li
                                key={dataset.id}
                                className={`history-item animate-slide-up stagger-${(index % 4) + 3}`}
                                onClick={() => navigate(`/dataset/${dataset.id}`)}
                            >
                                <span className="history-item-name">📄 {dataset.filename}</span>
                                <span className="history-item-meta">
                                    {formatDate(dataset.uploaded_at)} • {dataset.total_count} records
                                </span>
                                <button
                                    className="history-item-delete"
                                    onClick={(e) => handleDeleteClick(e, dataset.id, dataset.filename)}
                                    title="Delete dataset"
                                >
                                    🗑️
                                </button>
                            </li>
                        ))
                    )}
                </ul>

                <div style={{ marginTop: 'auto', paddingTop: '1.5rem' }}>
                    <button className="btn btn-outline" style={{ width: '100%' }} onClick={onLogout}>
                        Sign Out
                    </button>
                </div>
            </aside>

            <ConfirmModal
                isOpen={deleteModal.show}
                onClose={() => setDeleteModal({ ...deleteModal, show: false })}
                onConfirm={confirmDelete}
                title="Delete Dataset"
                message={`Are you sure you want to delete "${deleteModal.filename}"? This action cannot be undone.`}
            />
        </>
    );
}

export default Sidebar;

import React from 'react';

function ConfirmModal({ isOpen, onClose, onConfirm, title, message, confirmText = 'Delete', confirmColor = '#f5576c' }) {
    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: 'var(--bg-overlay)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000,
            backdropFilter: 'blur(5px)'
        }} onClick={onClose}>
            <div
                className="glass-card"
                style={{
                    width: '100%',
                    maxWidth: '400px',
                    padding: '2rem',
                    textAlign: 'center',
                    border: '1px solid var(--border-color)',
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
                }}
                onClick={e => e.stopPropagation()}
            >
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
                <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>{title}</h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>{message}</p>

                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <button
                        className="btn btn-outline"
                        onClick={onClose}
                        style={{ minWidth: '100px' }}
                    >
                        Cancel
                    </button>
                    <button
                        className="btn"
                        onClick={onConfirm}
                        style={{
                            minWidth: '100px',
                            background: confirmColor,
                            color: 'white',
                            boxShadow: `0 4px 15px ${confirmColor}40`
                        }}
                    >
                        {confirmText}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ConfirmModal;

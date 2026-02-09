import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import Sidebar from '../components/Sidebar';
import { getUserProfile, updateUserProfile } from '../services/api';

function ProfilePage() {
    const { username, logout, updateUser } = useAuth();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirm_password: ''
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            const data = await getUserProfile();
            setFormData(prev => ({
                ...prev,
                username: data.username,
                email: data.email || ''
            }));
            setLoading(false);
        } catch (err) {
            setError('Failed to load profile');
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError('');
        setSuccess('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setError('');
        setSuccess('');

        if (formData.password && formData.password !== formData.confirm_password) {
            setError('Passwords do not match');
            setSaving(false);
            return;
        }

        try {
            const updateData = {
                username: formData.username,
                email: formData.email
            };
            if (formData.password) {
                updateData.password = formData.password;
                updateData.confirm_password = formData.confirm_password;
            }

            await updateUserProfile(updateData);
            updateUser(formData.username); // Update global state
            setSuccess('Profile updated successfully');

            // Clear password fields
            setFormData(prev => ({
                ...prev,
                password: '',
                confirm_password: ''
            }));
        } catch (err) {
            const errorData = err.response?.data;
            if (typeof errorData === 'object') {
                const messages = Object.values(errorData).flat().join('. ');
                setError(messages || 'Failed to update profile');
            } else {
                setError('Failed to update profile');
            }
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-overlay">
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div className="app-layout">
            <Sidebar username={username} datasets={[]} onDeleteDataset={() => { }} onLogout={logout} />
            <main className="main-content">
                <header className="header">
                    <h1>Profile Settings</h1>
                </header>

                <div className="glass-card" style={{ maxWidth: '600px' }}>
                    <form onSubmit={handleSubmit}>
                        {error && <div className="alert alert-error">{error}</div>}
                        {success && <div className="alert alert-success">{success}</div>}

                        <div className="input-group">
                            <label>Username</label>
                            <input
                                name="username"
                                type="text"
                                className="input"
                                value={formData.username}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="input-group">
                            <label>Email</label>
                            <input
                                name="email"
                                type="email"
                                className="input"
                                value={formData.email}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <hr style={{ borderColor: 'var(--border-color)', margin: '2rem 0' }} />
                        <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Change Password</h3>

                        <div className="input-group">
                            <label>New Password (leave blank to keep current)</label>
                            <input
                                name="password"
                                type="password"
                                className="input"
                                value={formData.password}
                                onChange={handleChange}
                                minLength={6}
                                placeholder="Min 6 characters"
                            />
                        </div>

                        <div className="input-group">
                            <label>Confirm New Password</label>
                            <input
                                name="confirm_password"
                                type="password"
                                className="input"
                                value={formData.confirm_password}
                                onChange={handleChange}
                            />
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '2rem' }}>
                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={() => navigate('/dashboard')}
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="btn btn-primary"
                                disabled={saving}
                            >
                                {saving ? 'Saving...' : 'Save Changes'}
                            </button>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    );
}

export default ProfilePage;

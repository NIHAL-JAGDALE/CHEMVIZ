import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { getDatasets, deleteDataset } from '../services/api';
import FileUploader from '../components/FileUploader';
import Sidebar from '../components/Sidebar';

function DashboardPage() {
    const { username, logout } = useAuth();
    const navigate = useNavigate();
    const [datasets, setDatasets] = useState([]);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        loadDatasets();
    }, []);

    const loadDatasets = async () => {
        try {
            const data = await getDatasets();
            setDatasets(data);
        } catch (err) {
            setError('Failed to load datasets');
        }
    };

    const handleUploadSuccess = (data) => {
        setSuccess(`Successfully uploaded ${data.filename}`);
        // Navigate to the new dataset page
        setTimeout(() => {
            navigate(`/dataset/${data.dataset_id}`);
        }, 1000);
    };

    const handleQuickDelete = async (e, datasetId, filename) => {
        e.stopPropagation(); // Prevent navigation when clicking delete

        try {
            await deleteDataset(datasetId);
            setSuccess(`Successfully deleted ${filename}`);
            // Refresh the datasets list
            loadDatasets();
            // Clear success message after 3 seconds
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError('Failed to delete dataset');
            setTimeout(() => setError(''), 3000);
        }
    };

    return (
        <div className="app-layout">
            {/* Sidebar */}
            <Sidebar
                username={username}
                datasets={datasets}
                onDeleteDataset={handleQuickDelete}
                onLogout={logout}
            />

            {/* Main Content */}
            <main className="main-content animate-fade-in">
                <header className="header animate-slide-up">
                    <h1>Equipment Analytics Dashboard</h1>
                </header>

                {error && <div className="alert alert-error">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}

                {/* Upload Section */}
                <section className="animate-slide-up stagger-1" style={{ marginBottom: '2rem', marginTop: '2rem' }}>
                    <h2 style={{ marginBottom: '1rem' }}>Upload New Dataset</h2>
                    <FileUploader onSuccess={handleUploadSuccess} onError={setError} />
                </section>

                <div className="animate-slide-up stagger-2" style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-muted)' }}>
                    <div className="floating" style={{ fontSize: '4rem', marginBottom: '1rem', opacity: 0.5 }}>📊</div>
                    <h2 style={{ marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Welcome to Visualizer</h2>
                    <p>Select a dataset from the sidebar or upload a new CSV to get started.</p>
                </div>
            </main>
        </div>
    );
}

export default DashboardPage;

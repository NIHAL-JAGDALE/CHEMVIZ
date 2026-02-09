import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import Sidebar from '../components/Sidebar';
import { getDatasets, getDatasetSummary, getDatasetData, downloadReport, deleteDataset } from '../services/api';
import DataTable from '../components/DataTable';
import TypeDistributionChart from '../components/TypeDistributionChart';
import AveragesChart from '../components/AveragesChart';

import ConfirmModal from '../components/ConfirmModal';

function DatasetPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [dataset, setDataset] = useState(null);
    const [datasetSummary, setDatasetSummary] = useState(null);
    const [datasetData, setDatasetData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { username, logout } = useAuth();
    const [datasets, setDatasets] = useState([]);
    const [deleteModal, setDeleteModal] = useState({ show: false, id: null, filename: '' });

    useEffect(() => {
        loadDatasets();
    }, []);

    const loadDatasets = async () => {
        try {
            const data = await getDatasets();
            setDatasets(data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleSidebarDelete = async (e, datasetId, filename) => {
        e.stopPropagation();
        setDeleteModal({ show: true, id: datasetId, filename, isSidebar: true });
    };

    const confirmDelete = async () => {
        if (!deleteModal.id) return;

        try {
            await deleteDataset(deleteModal.id);

            if (deleteModal.isSidebar) {
                if (deleteModal.id == id) {
                    navigate('/dashboard');
                } else {
                    loadDatasets();
                }
            } else {
                navigate('/dashboard');
            }
        } catch (err) {
            console.error("Failed to delete dataset", err);
            setError('Failed to delete dataset');
        } finally {
            setDeleteModal({ show: false, id: null, filename: '' });
        }
    };

    useEffect(() => {
        loadDatasetDetails();
    }, [id]);

    const loadDatasetDetails = async () => {
        setLoading(true);
        setError('');
        try {
            const summaryData = await getDatasetSummary(id);
            setDataset({
                id: summaryData.id,
                filename: summaryData.filename,
                uploaded_at: summaryData.uploaded_at
            });
            setDatasetSummary(summaryData.summary);

            const dataResponse = await getDatasetData(id);
            setDatasetData(dataResponse);

        } catch (err) {
            console.error(err);
            setError('Failed to load dataset details. ' + (err.response?.data?.error || err.message));
        } finally {
            setLoading(false);
        }
    };


    const handleDownloadReport = async () => {
        try {
            const blob = await downloadReport(id);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${dataset.filename.replace('.csv', '')}_report.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            setError('Failed to download report');
        }
    };

    const handleDelete = async () => {
        setDeleteModal({ show: true, id: id, filename: dataset?.filename, isSidebar: false });
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <div className="loading-overlay">
                <div className="spinner" style={{ width: '48px', height: '48px' }}></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="app-layout">
                <Sidebar username={username} datasets={datasets} onDeleteDataset={handleSidebarDelete} onLogout={logout} />
                <main className="main-content">
                    <div className="alert alert-error">{error}</div>
                    <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>Back to Dashboard</button>

                    <ConfirmModal
                        isOpen={deleteModal.show}
                        onClose={() => setDeleteModal({ ...deleteModal, show: false })}
                        onConfirm={confirmDelete}
                        title="Delete Dataset"
                        message={`Are you sure you want to delete "${deleteModal.filename}"? This action cannot be undone.`}
                    />
                </main>
            </div>
        );
    }

    return (
        <div className="app-layout">
            <Sidebar username={username} datasets={datasets} onDeleteDataset={handleSidebarDelete} onLogout={logout} />
            <main className="main-content animate-fade-in">
                <header className="header animate-slide-up" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <button className="btn btn-outline" onClick={() => navigate('/dashboard')} style={{ marginBottom: '1rem' }}>
                            ← Back to Dashboard
                        </button>
                        <h1>{dataset?.filename || 'Dataset Details'}</h1>
                        {dataset && <p style={{ color: 'var(--text-muted)' }}>Uploaded on {formatDate(dataset.uploaded_at)}</p>}
                    </div>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <button className="btn btn-danger" onClick={handleDelete}>
                            🗑️ Delete Dataset
                        </button>
                        <button className="btn btn-primary" onClick={handleDownloadReport}>
                            📥 Download PDF Report
                        </button>
                    </div>
                </header>

                {datasetSummary && (
                    <>
                        {/* Summary Cards */}
                        <section className="summary-grid">
                            <div className="summary-card tilt-card animate-slide-up stagger-1">
                                <div className="summary-card-value">{datasetSummary.total_count}</div>
                                <div className="summary-card-label">Total Records</div>
                            </div>
                            {Object.entries(datasetSummary.averages || {}).map(([key, value], index) => (
                                <div className={`summary-card tilt-card animate-slide-up stagger-${(index % 4) + 1}`} key={key}>
                                    <div className="summary-card-value">{value.toFixed(2)}</div>
                                    <div className="summary-card-label">Avg {key.replace(/_/g, ' ')}</div>
                                </div>
                            ))}
                        </section>

                        {/* Charts */}
                        <section className="charts-grid">
                            <div className="chart-card tilt-card animate-slide-up stagger-3" style={{ paddingTop: '3.5rem' }}>
                                <h3>Equipment Type Distribution</h3>
                                <div style={{ flexGrow: 1, minHeight: 0, position: 'relative' }}>
                                    <TypeDistributionChart data={datasetSummary.type_distribution} title="equipment_type_distribution" />
                                </div>
                            </div>
                            <div className="chart-card tilt-card animate-slide-up stagger-4" style={{ paddingTop: '3.5rem' }}>
                                <h3>Average Parameter Values</h3>
                                <div style={{ flexGrow: 1, minHeight: 0, position: 'relative' }}>
                                    <AveragesChart data={datasetSummary.averages} title="average_parameters" />
                                </div>
                            </div>
                        </section>

                        {/* Data Table */}
                        {datasetData && (
                            <section>
                                <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Raw Data</h2>
                                <DataTable columns={datasetData.columns} data={datasetData.data} />
                            </section>
                        )}
                    </>
                )}

                <ConfirmModal
                    isOpen={deleteModal.show}
                    onClose={() => setDeleteModal({ ...deleteModal, show: false })}
                    onConfirm={confirmDelete}
                    title="Delete Dataset"
                    message={`Are you sure you want to delete "${deleteModal.filename}"? This action cannot be undone.`}
                />
            </main>
        </div>
    );
}

export default DatasetPage;

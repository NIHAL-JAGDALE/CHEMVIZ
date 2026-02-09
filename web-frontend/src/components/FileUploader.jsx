import React, { useState, useRef } from 'react';
import { uploadDataset } from '../services/api';

function FileUploader({ onSuccess, onError }) {
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [dragOver, setDragOver] = useState(false);
    const fileInputRef = useRef(null);

    const handleFile = async (file) => {
        if (!file) return;

        if (!file.name.endsWith('.csv')) {
            onError('Please upload a CSV file');
            return;
        }

        setUploading(true);
        setProgress(0);
        onError('');

        try {
            const data = await uploadDataset(file, setProgress);
            onSuccess(data);
        } catch (err) {
            onError(err.response?.data?.error || 'Upload failed. Please try again.');
        } finally {
            setUploading(false);
            setProgress(0);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files[0];
        handleFile(file);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragOver(true);
    };

    const handleDragLeave = () => {
        setDragOver(false);
    };

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    const handleChange = (e) => {
        const file = e.target.files[0];
        handleFile(file);
    };

    return (
        <div
            className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
            onClick={handleClick}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
        >
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleChange}
                accept=".csv"
                style={{ display: 'none' }}
            />

            {uploading ? (
                <>
                    <div className="upload-zone-icon">⏳</div>
                    <p className="upload-zone-text">Uploading... {progress}%</p>
                    <div className="progress-bar">
                        <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
                    </div>
                </>
            ) : (
                <>
                    <div className="upload-zone-icon">📤</div>
                    <p className="upload-zone-text">
                        Drag & drop a CSV file here, or click to browse
                    </p>
                    <p className="upload-zone-hint">
                        Supports any CSV file with headers
                    </p>
                </>
            )}
        </div>
    );
}

export default FileUploader;

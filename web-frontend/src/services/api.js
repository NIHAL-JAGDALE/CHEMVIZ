import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

// Handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Don't redirect if it's a login attempt that failed
        if (error.response?.status === 401 && !error.config.url.includes('/auth/login')) {
            localStorage.removeItem('authToken');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const login = async (username, password) => {
    const response = await api.post('/auth/login/', { username, password });
    return response.data;
};

export const register = async (username, email, password, confirmPassword) => {
    const response = await api.post('/auth/register/', {
        username,
        email,
        password,
        confirm_password: confirmPassword
    });
    return response.data;
};

// Dataset API
export const uploadDataset = async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
            );
            if (onProgress) onProgress(percentCompleted);
        },
    });
    return response.data;
};

export const getDatasets = async () => {
    const response = await api.get('/datasets/');
    return response.data;
};

export const getDatasetSummary = async (datasetId) => {
    const response = await api.get(`/summary/${datasetId}/`);
    return response.data;
};

export const getDatasetData = async (datasetId) => {
    const response = await api.get(`/data/${datasetId}/`);
    return response.data;
};

export const downloadReport = async (datasetId) => {
    const response = await api.get(`/report/${datasetId}/`, {
        responseType: 'blob',
    });
    return response.data;
};


export const getUserProfile = async () => {
    const response = await api.get('/user/profile/');
    return response.data;
};

export const updateUserProfile = async (userData) => {
    const response = await api.put('/user/profile/', userData);
    return response.data;
};

export const deleteDataset = async (datasetId) => {
    const response = await api.delete(`/datasets/${datasetId}/`);
    return response.data;
};

export default api;

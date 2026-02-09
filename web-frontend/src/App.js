import React, { useState, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import DatasetPage from './pages/DatasetPage';
import ProfilePage from './pages/ProfilePage';

// Theme Context
const ThemeContext = createContext(null);
export const useTheme = () => useContext(ThemeContext);

export function ThemeProvider({ children }) {
    const [isDark, setIsDark] = useState(localStorage.getItem('theme') !== 'light');

    React.useEffect(() => {
        if (isDark) {
            document.body.classList.remove('light-theme');
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.add('light-theme');
            document.body.classList.remove('dark-theme');
        }
    }, [isDark]);

    const toggleTheme = () => {
        const newTheme = !isDark;
        setIsDark(newTheme);
        localStorage.setItem('theme', newTheme ? 'dark' : 'light');
    };

    return (
        <ThemeContext.Provider value={{ isDark, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
    const [token, setToken] = useState(localStorage.getItem('authToken'));
    const [username, setUsername] = useState(localStorage.getItem('username'));

    const login = (newToken, newUsername) => {
        localStorage.setItem('authToken', newToken);
        localStorage.setItem('username', newUsername);
        setToken(newToken);
        setUsername(newUsername);
    };

    const logout = () => {
        localStorage.removeItem('authToken');
        localStorage.removeItem('username');
        setToken(null);
        setUsername(null);
    };

    const updateUser = (newUsername) => {
        localStorage.setItem('username', newUsername);
        setUsername(newUsername);
    };

    return (
        <AuthContext.Provider value={{ token, username, login, logout, updateUser, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
}

// Protected Route
function ProtectedRoute({ children }) {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return children;
}

function AppContent() {
    const { isDark, toggleTheme } = useTheme();

    return (
        <BrowserRouter>
            <AuthProvider>
                <button
                    className="theme-toggle"
                    onClick={toggleTheme}
                    title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
                >
                    <span style={{
                        transform: isDark ? 'rotate(0)' : 'rotate(360deg)',
                        transition: 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
                        display: 'inline-block'
                    }}>
                        {isDark ? '☀️' : '🌙'}
                    </span>
                </button>
                <Routes>
                    <Route path="/login" element={<AuthPage />} />
                    <Route
                        path="/dashboard"
                        element={
                            <ProtectedRoute>
                                <DashboardPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/profile"
                        element={
                            <ProtectedRoute>
                                <ProfilePage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/dataset/:id"
                        element={
                            <ProtectedRoute>
                                <DatasetPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/"
                        element={<Navigate to="/dashboard" replace />}
                    />
                    <Route
                        path="/*"
                        element={<Navigate to="/dashboard" replace />}
                    />
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    );
}

function App() {
    return (
        <ThemeProvider>
            <AppContent />
        </ThemeProvider>
    );
}

export default App;

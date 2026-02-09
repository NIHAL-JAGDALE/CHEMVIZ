import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { login as apiLogin, register as apiRegister } from '../services/api';

import logo from '../assets/logo.png';
import logoLight from '../assets/logo_light.png';
import { useTheme } from '../App';

function AuthPage() {
    const { isDark } = useTheme();
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError('');
        setSuccess('');
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const data = await apiLogin(formData.username, formData.password);
            login(data.token, data.username);
            navigate('/');
        } catch (err) {
            if (err.response?.status === 401) {
                setError('Invalid credentials');
                return;
            }
            const errorData = err.response?.data;
            if (typeof errorData === 'object' && errorData.error) {
                setError(errorData.error);
            } else if (typeof errorData === 'object') {
                const firstError = Object.values(errorData)[0];
                setError(Array.isArray(firstError) ? firstError[0] : firstError);
            } else {
                setError('Login failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        // Client-side validation
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters');
            setLoading(false);
            return;
        }

        try {
            const data = await apiRegister(
                formData.username,
                formData.email,
                formData.password,
                formData.confirmPassword
            );
            login(data.token, data.username);
            navigate('/');
        } catch (err) {
            const errorData = err.response?.data;
            if (typeof errorData === 'object') {
                // Handle field-specific errors
                const errorMessages = [];
                for (const [key, value] of Object.entries(errorData)) {
                    if (key === 'error') {
                        errorMessages.push(value);
                    } else {
                        const msg = Array.isArray(value) ? value[0] : value;
                        errorMessages.push(`${key}: ${msg}`);
                    }
                }
                setError(errorMessages.join('. '));
            } else {
                setError('Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    const toggleMode = () => {
        setIsLogin(!isLogin);
        setError('');
        setSuccess('');
        setFormData({
            username: '',
            email: '',
            password: '',
            confirmPassword: ''
        });
    };

    return (
        <div className="auth-container animate-fade-in">
            <div className="auth-card tilt-card animate-slide-up">
                {/* Logo Section */}
                <div className="auth-logo floating">
                    <img src={isDark ? logo : logoLight} alt="CHEMVIZ Logo" style={{ maxWidth: '200px', marginBottom: '1rem' }} />
                </div>

                {/* Tab Toggle */}
                <div className="auth-tabs">
                    <button
                        className={`auth-tab ${isLogin ? 'active' : ''}`}
                        onClick={() => toggleMode()}
                        disabled={loading}
                    >
                        Sign In
                    </button>
                    <button
                        className={`auth-tab ${!isLogin ? 'active' : ''}`}
                        onClick={() => toggleMode()}
                        disabled={loading}
                    >
                        Sign Up
                    </button>
                </div>

                {/* Error/Success Messages */}
                {error && <div className="alert alert-error">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}

                {/* Login Form */}
                {isLogin ? (
                    <form onSubmit={handleLogin} className="auth-form">
                        <div className="input-group">
                            <label htmlFor="username">Username</label>
                            <input
                                id="username"
                                name="username"
                                type="text"
                                className="input"
                                value={formData.username}
                                onChange={handleChange}
                                placeholder="Enter your username"
                                required
                                autoComplete="username"
                            />
                        </div>

                        <div className="input-group">
                            <label htmlFor="password">Password</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                className="input"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Enter your password"
                                required
                                autoComplete="current-password"
                            />
                        </div>

                        <button
                            type="submit"
                            className="btn btn-primary auth-submit-btn"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner" style={{ width: '18px', height: '18px' }}></span>
                                    Signing in...
                                </>
                            ) : (
                                <>
                                    <span>🔐</span>
                                    Sign In
                                </>
                            )}
                        </button>
                    </form>
                ) : (
                    /* Registration Form */
                    <form onSubmit={handleRegister} className="auth-form">
                        <div className="input-group">
                            <label htmlFor="reg-username">Username</label>
                            <input
                                id="reg-username"
                                name="username"
                                type="text"
                                className="input"
                                value={formData.username}
                                onChange={handleChange}
                                placeholder="Choose a username"
                                required
                                minLength={3}
                                autoComplete="username"
                            />
                        </div>

                        <div className="input-group">
                            <label htmlFor="email">Email</label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                className="input"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="Enter your email"
                                required
                                autoComplete="email"
                            />
                        </div>

                        <div className="input-group">
                            <label htmlFor="reg-password">Password</label>
                            <input
                                id="reg-password"
                                name="password"
                                type="password"
                                className="input"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Create a password (min 6 chars)"
                                required
                                minLength={6}
                                autoComplete="new-password"
                            />
                        </div>

                        <div className="input-group">
                            <label htmlFor="confirmPassword">Confirm Password</label>
                            <input
                                id="confirmPassword"
                                name="confirmPassword"
                                type="password"
                                className="input"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="Confirm your password"
                                required
                                autoComplete="new-password"
                            />
                        </div>

                        <button
                            type="submit"
                            className="btn btn-primary auth-submit-btn"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner" style={{ width: '18px', height: '18px' }}></span>
                                    Creating account...
                                </>
                            ) : (
                                <>
                                    <span>🚀</span>
                                    Create Account
                                </>
                            )}
                        </button>
                    </form>
                )}

                {/* Footer */}
                <div className="auth-footer">
                    <p>
                        {isLogin
                            ? "Don't have an account?"
                            : "Already have an account?"
                        }
                        <button
                            type="button"
                            className="auth-link-btn"
                            onClick={toggleMode}
                            disabled={loading}
                        >
                            {isLogin ? 'Create one' : 'Sign in'}
                        </button>
                    </p>
                </div>
            </div>

            {/* Background Decoration */}
            <div className="auth-bg-decoration">
                <div className="auth-bg-circle auth-bg-circle-1"></div>
                <div className="auth-bg-circle auth-bg-circle-2"></div>
                <div className="auth-bg-circle auth-bg-circle-3"></div>
            </div>
        </div>
    );
}

export default AuthPage;

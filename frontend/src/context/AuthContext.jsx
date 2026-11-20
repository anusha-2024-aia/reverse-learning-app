/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useState, useEffect } from 'react';
import api from '../api/axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const getStoredToken = () => sessionStorage.getItem('token') || localStorage.getItem('token');
  const [token, setToken] = useState(getStoredToken());
  const [user, setUser] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(!!token);
  const [loading, setLoading] = useState(true);

  const fetchUser = async () => {
    const activeToken = getStoredToken();
    if (!activeToken) {
      setLoading(false);
      return;
    }
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
      setIsLoggedIn(true);
    } catch (error) {
      console.error("Failed to fetch user:", error);
      if (error.response && error.response.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const login = async (usernameOrEmail, password) => {
    try {
      const response = await api.post('/auth/login', { username_or_email: usernameOrEmail, password });
      const newToken = response.data.access_token;
      sessionStorage.setItem('token', newToken);
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setIsLoggedIn(true);
      return { success: true };
    } catch (error) {
      console.error("Login error:", error);
      let errorMessage = 'An error occurred during login';
      const data = error.response?.data;
      if (data?.message || data?.detail) {
        const raw = data.message || data.detail;
        errorMessage = typeof raw === 'string' ? raw : JSON.stringify(raw);
      }
      return { success: false, error: errorMessage };
    }
  };

  const demoLogin = async () => {
    try {
      const response = await api.post('/auth/demo-login');
      const newToken = response.data.access_token;
      sessionStorage.setItem('token', newToken);
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setIsLoggedIn(true);
      return { success: true, user: response.data.user };
    } catch (error) {
      console.error("Demo login error:", error);
      const data = error.response?.data;
      return { success: false, error: data?.message || data?.detail || 'Demo login failed' };
    }
  };

  const signup = async (name, email, password, confirmPassword, university, focusTrack) => {
    try {
      await api.post('/auth/register', {
        name: name,
        username: email ? email.split('@')[0] : undefined,
        email: email,
        password: password,
        confirm_password: confirmPassword,
        university: university,
        target_role: focusTrack
      });
      // Do not auto login.
      return { success: true };
    } catch (error) {
      console.error("Signup error:", error);
      let errorMessage = 'An error occurred during signup';
      const data = error.response?.data;
      if (data?.message || data?.detail) {
        const raw = data.message || data.detail;
        errorMessage = typeof raw === 'string' ? raw : JSON.stringify(raw);
      }
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    sessionStorage.removeItem('token');
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsLoggedIn(false);
  };

  return (
    <AuthContext.Provider value={{ token, user, isLoggedIn, loading, login, demoLogin, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

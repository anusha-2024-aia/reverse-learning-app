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
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : JSON.stringify(error.response.data.detail);
      }
      return { success: false, error: errorMessage };
    }
  };

  const signup = async (name, email, password, confirmPassword) => {
    try {
      await api.post('/auth/register', { 
        name: name,
        username: email ? email.split('@')[0] : undefined,
        email: email, 
        password: password,
        confirm_password: confirmPassword 
      });
      // Do not auto login.
      return { success: true };
    } catch (error) {
      console.error("Signup error:", error);
      let errorMessage = 'An error occurred during signup';
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : JSON.stringify(error.response.data.detail);
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
    <AuthContext.Provider value={{ token, user, isLoggedIn, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

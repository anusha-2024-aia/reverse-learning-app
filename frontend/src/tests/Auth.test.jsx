import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';
import { AuthContext, AuthProvider } from '../context/AuthContext';
import api from '../api/axios';

vi.mock('../api/axios', () => {
  return {
    default: {
      get: vi.fn(),
      post: vi.fn(),
    },
  };
});

describe('Authentication Flow Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
    localStorage.clear();
  });

  it('TEST A — VALID LOGIN: updates auth state, succeeds, and navigates', async () => {
    // Mock successful login API call
    api.post.mockResolvedValueOnce({
      data: { access_token: 'mock-valid-token-123' },
    });
    // Mock user profile API call
    api.get.mockResolvedValueOnce({
      data: { id: 1, name: 'Test User', email: 'test@example.com' },
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/login']}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<div data-testid="dashboard-page">Dashboard Home</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    // Enter valid credentials
    const usernameInput = screen.getByLabelText(/username or email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    fireEvent.change(usernameInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    fireEvent.click(submitButton);

    // Verify API called with credentials
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/auth/login', {
        username_or_email: 'test@example.com',
        password: 'password123',
      });
    });

    // Verify redirect to dashboard
    await waitFor(() => {
      expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
    });

    // Verify token stored
    expect(localStorage.getItem('token')).toBe('mock-valid-token-123');
  });

  it('TEST B — INVALID LOGIN: displays error message and stays on login page', async () => {
    // Mock failed login response
    api.post.mockRejectedValueOnce({
      response: {
        status: 401,
        data: { detail: 'Invalid username or password' },
      },
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/login']}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<div data-testid="dashboard-page">Dashboard Home</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    const usernameInput = screen.getByLabelText(/username or email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    fireEvent.change(usernameInput, { target: { value: 'invalid@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });

    fireEvent.click(submitButton);

    // Verify error is displayed
    await waitFor(() => {
      expect(screen.getByText('Invalid username or password')).toBeInTheDocument();
    });

    // Verify user remains on login page
    expect(screen.queryByTestId('dashboard-page')).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument();
  });

  it('TEST C — LOADING STATE: disables submit button and shows loading text', async () => {
    let resolveLogin;
    const loginPromise = new Promise((resolve) => {
      resolveLogin = resolve;
    });
    api.post.mockReturnValueOnce(loginPromise);

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/login']}>
          <LoginPage />
        </MemoryRouter>
      </AuthProvider>
    );

    const usernameInput = screen.getByLabelText(/username or email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    fireEvent.change(usernameInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    fireEvent.click(submitButton);

    // Button should show loading state and be disabled
    expect(screen.getByRole('button', { name: /logging in\.\.\./i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /logging in\.\.\./i })).toBeDisabled();

    // Resolve login promise to clean up
    resolveLogin({ data: { access_token: 'token-abc' } });
  });
});

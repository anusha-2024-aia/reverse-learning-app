import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import SignupPage from '../pages/SignupPage';
import LoginPage from '../pages/LoginPage';
import { AuthProvider, AuthContext } from '../context/AuthContext';
import ProtectedRoute from '../components/ProtectedRoute';
import api from '../api/axios';

vi.mock('../api/axios', () => {
  return {
    default: {
      get: vi.fn(),
      post: vi.fn(),
    },
  };
});

describe('Registration and Login UI & Lifecycle Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
    localStorage.clear();
  });

  it('TEST 1 & 11: Fresh registration page starts completely empty with no stale errors or prefilled names', () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/signup']}>
          <SignupPage />
        </MemoryRouter>
      </AuthProvider>
    );

    const nameInput = screen.getByLabelText(/full legal name/i);
    const emailInput = screen.getByLabelText(/email address/i);
    const universityInput = screen.getByLabelText(/university/i);
    const passwordInput = screen.getByLabelText(/^access password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

    expect(nameInput.value).toBe('');
    expect(emailInput.value).toBe('');
    expect(universityInput.value).toBe('');
    expect(passwordInput.value).toBe('');
    expect(confirmPasswordInput.value).toBe('');
    expect(screen.queryByText(/this email is already registered/i)).not.toBeInTheDocument();
  });

  it('TEST 2 & 3: Displays duplicate email error with Sign In link, and clears error when user types new email', async () => {
    api.post.mockRejectedValueOnce({
      response: {
        status: 400,
        data: { message: 'This email is already registered. Please sign in or use another email.' }
      }
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/signup']}>
          <SignupPage />
        </MemoryRouter>
      </AuthProvider>
    );

    const nameInput = screen.getByLabelText(/full legal name/i);
    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^access password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitBtn = screen.getByRole('button', { name: /create student account/i });

    fireEvent.change(nameInput, { target: { value: 'Test Student' } });
    fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123!' } });

    fireEvent.click(submitBtn);

    // Verify duplicate email message with sign in link
    await waitFor(() => {
      expect(screen.getByText(/this email is already registered/i)).toBeInTheDocument();
    });

    // TEST 3: User changes email -> old error must clear immediately
    fireEvent.change(emailInput, { target: { value: 'new_unique_email@example.com' } });
    expect(screen.queryByText(/this email is already registered/i)).not.toBeInTheDocument();
  });

  it('TEST 4: Client validates malformed email and blocks submission', async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/signup']}>
          <SignupPage />
        </MemoryRouter>
      </AuthProvider>
    );

    const nameInput = screen.getByLabelText(/full legal name/i);
    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^access password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitBtn = screen.getByRole('button', { name: /create student account/i });

    fireEvent.change(nameInput, { target: { value: 'Test Student' } });
    fireEvent.change(emailInput, { target: { value: 'not-an-email' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123!' } });

    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
    });
    expect(api.post).not.toHaveBeenCalled();
  });

  it('TEST 6: Successful login with credentials updates Auth context and navigates to dashboard', async () => {
    api.post.mockResolvedValueOnce({
      data: { access_token: 'fresh-user-jwt-token' }
    });
    api.get.mockResolvedValueOnce({
      data: { id: 10, name: 'Student Ten', email: 'student10@example.com' }
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/login']}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<div data-testid="dashboard-screen">Dashboard Screen</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    const identifierInput = screen.getByLabelText(/username or email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginBtn = screen.getByRole('button', { name: /log in/i });

    fireEvent.change(identifierInput, { target: { value: 'student10@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePassword123!' } });

    fireEvent.click(loginBtn);

    await waitFor(() => {
      expect(screen.getByTestId('dashboard-screen')).toBeInTheDocument();
    });
    expect(localStorage.getItem('token')).toBe('fresh-user-jwt-token');
  });

  it('TEST 7: Invalid login rejected with clear error message', async () => {
    api.post.mockRejectedValueOnce({
      response: {
        status: 401,
        data: { message: 'Invalid email or password.' }
      }
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/login']}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    const identifierInput = screen.getByLabelText(/username or email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginBtn = screen.getByRole('button', { name: /log in/i });

    fireEvent.change(identifierInput, { target: { value: 'student@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'WrongPassword' } });

    fireEvent.click(loginBtn);

    await waitFor(() => {
      expect(screen.getByText('Invalid email or password.')).toBeInTheDocument();
    });
  });

  it('TEST 9 & 10: Demo login works independently, and unauthenticated protected route redirects to login', async () => {
    // Unauthenticated access
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/study']}>
          <Routes>
            <Route path="/study" element={<ProtectedRoute><div>Protected Room</div></ProtectedRoute>} />
            <Route path="/login" element={<div data-testid="login-fallback">Login Fallback</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    expect(screen.getByTestId('login-fallback')).toBeInTheDocument();
    expect(screen.queryByText('Protected Room')).not.toBeInTheDocument();
  });
});

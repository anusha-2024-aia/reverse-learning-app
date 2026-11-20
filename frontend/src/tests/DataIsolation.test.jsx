import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import ResumeIntelligence from '../pages/ResumeIntelligence';
import Dashboard from '../pages/Dashboard';
import KnowledgeGaps from '../pages/KnowledgeGaps';
import SmartRevision from '../pages/SmartRevision';
import AnalyticsPage from '../pages/AnalyticsPage';
import api from '../api/axios';

vi.mock('../api/axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import servicesApi from '../services/api';

describe('Data Isolation and Empty State Unit Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderWithAuth = (component, user) => {
    return render(
      <AuthContext.Provider value={{ user, isLoggedIn: true }}>
        <MemoryRouter>{component}</MemoryRouter>
      </AuthContext.Provider>
    );
  };

  it('ResumeIntelligence: renders empty upload hero state for newly registered student with no resume', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/resume/active') {
        return Promise.resolve({ data: { has_resume: false } });
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    renderWithAuth(<ResumeIntelligence />, { email: 'student@example.com', name: 'New Student' });

    await waitFor(() => {
      expect(screen.getByText(/Upload your resume to benchmark against real software engineering hiring bars/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Target Role Alignment/i)).toBeInTheDocument();
    expect(screen.getByText(/Technical Gap Extraction/i)).toBeInTheDocument();
  });

  it('ResumeIntelligence: renders active resume analysis when student has an uploaded resume', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/resume/active') {
        return Promise.resolve({
          data: {
            has_resume: true,
            file_name: 'candidate_resume_2026.pdf',
            analysis_summary: {
              match_score: 85,
              skills: ['Go', 'Kubernetes', 'Python'],
              strengths: [{ title: 'Strong Systems Depth', description: 'Experience in Go' }]
            },
            questions: []
          }
        });
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    renderWithAuth(<ResumeIntelligence />, { email: 'student@example.com', name: 'New Student' });

    await waitFor(() => {
      expect(screen.getByText('candidate_resume_2026.pdf')).toBeInTheDocument();
    });

    expect(screen.getByText('85')).toBeInTheDocument();
    expect(screen.getByText(/Strong Systems Depth/i)).toBeInTheDocument();
  });

  it('Dashboard: displays clean 0% mastery and 0-day streak for new student', async () => {
    servicesApi.get.mockImplementation((url) => {
      if (url === '/dashboard-data') {
        return Promise.resolve({
          data: {
            user: { name: 'Fresh User' },
            summary: { overallScore: 0, streak: 0, streakDays: 0 },
            recentActivity: []
          }
        });
      }
      if (url === '/adaptive-learning/recommendation') {
        return Promise.resolve({ data: null });
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    renderWithAuth(<Dashboard />, { email: 'fresh@example.com', name: 'Fresh User' });

    await waitFor(() => {
      expect(screen.getByText(/Welcome to Reverse Learning/i)).toBeInTheDocument();
    });

    expect(screen.getByText('Cognitive Mastery Index')).toBeInTheDocument();
    expect(screen.getByText('Active Retention Streak')).toBeInTheDocument();
    expect(screen.getByText('Target Knowledge Gaps')).toBeInTheDocument();
    expect(screen.getByText('Days')).toBeInTheDocument();
    expect(screen.getByText('Priority')).toBeInTheDocument();
  });

  it('KnowledgeGaps: displays empty state for student with no recorded gaps', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/knowledge-gaps') {
        return Promise.resolve({ data: { gaps: [] } });
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    renderWithAuth(<KnowledgeGaps />, { email: 'fresh@example.com', name: 'Fresh User' });

    await waitFor(() => {
      expect(screen.getByText(/No Knowledge Gaps Detected Yet/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Start First Diagnostic →/i)).toBeInTheDocument();
  });

  it('SmartRevision: displays empty queue state when student has no due revisions', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/revisions') {
        return Promise.resolve({
          data: {
            due_today: [],
            summary: { due_today_count: 0, overdue_count: 0 }
          }
        });
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    renderWithAuth(<SmartRevision />, { email: 'fresh@example.com', name: 'Fresh User' });

    await waitFor(() => {
      expect(screen.getByText(/Your Active Recall Queue is Clear!/i)).toBeInTheDocument();
    });

    expect(screen.getByText('0')).toBeInTheDocument(); // Topics due: 0
    expect(screen.getByText('0 / 0')).toBeInTheDocument(); // Today's revision: 0 / 0
  });

  it('AnalyticsPage: displays empty telemetry onboarding state when student has no activity', async () => {
    api.get.mockImplementation((url) => {
      if (url.startsWith('/analytics')) {
        return Promise.resolve({
          data: {
            has_enough_data: false,
            summary: { overallScore: 0, learningStreak: 0 }
          }
        });
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    renderWithAuth(<AnalyticsPage />, { email: 'fresh@example.com', name: 'Fresh User' });

    await waitFor(() => {
      expect(screen.getByText(/No Learning Telemetry Recorded Yet/i)).toBeInTheDocument();
    });

    expect(screen.getByText('0.0h')).toBeInTheDocument();
  });
});
